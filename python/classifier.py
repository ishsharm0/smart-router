"""
Core classifier library for model-router-intelligent.
Config-driven routing logic - shared between skill and extension.
"""

import json
import os
import re
from pathlib import Path
from typing import Optional, Any

# Resolve skill directory
SKILL_DIR = Path(__file__).parent.parent
CONFIG_DIR = SKILL_DIR / "config"

# Load configs
_models_config: dict = {}
_categories_config: dict = {}

def load_configs() -> None:
    """Load model and category configurations."""
    global _models_config, _categories_config
    
    try:
        with open(CONFIG_DIR / "models.json", "r") as f:
            _models_config = json.load(f)
    except FileNotFoundError:
        _models_config = {"models": {}, "defaults": {"fallback": "minimax"}}
    
    try:
        with open(CONFIG_DIR / "categories.json", "r") as f:
            _categories_config = json.load(f)
    except FileNotFoundError:
        _categories_config = {"categories": {}, "fallback": {"model": "minimax"}}

load_configs()


def get_models() -> dict:
    """Get all enabled models from config."""
    models = {}
    for key, model in (_models_config.get("models") or {}).items():
        if model.get("enabled", True):
            models[key] = model
    return models


def get_model(model_key: str) -> Optional[dict]:
    """Get model config by key or resolve from alias."""
    models = get_models()
    
    if model_key in models:
        return {"key": model_key, **models[model_key]}
    
    # Try resolving as alias
    lower = model_key.lower().strip()
    for key, model in models.items():
        aliases = model.get("aliases", [])
        if any(a.lower() == lower for a in aliases):
            return {"key": key, **model}
    
    return None


def resolve_model_from_alias(alias: str) -> Optional[dict]:
    """Resolve model key from alias."""
    return get_model(alias)


def contains_any(text: str, keywords: list) -> bool:
    """Check if text contains any keyword (case-insensitive)."""
    if not keywords:
        return False
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def matches_any_pattern(text: str, patterns: list) -> bool:
    """Check if text matches any regex pattern."""
    if not patterns:
        return False
    for pattern in patterns:
        try:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        except re.error:
            continue
    return False


def analyze_prompt(text: str) -> dict:
    """Calculate prompt metrics."""
    text = str(text or "")
    return {
        "text": text,
        "lower": text.lower(),
        "words": text.split(),
        "estimated_tokens": len(text) // 4,
        "code_fence_count": len(re.findall(r"```[\s\S]*?```", text)),
        "file_path_count": len(re.findall(
            r"\b[a-z0-9_\-/]+\.(ts|tsx|js|jsx|py|go|rs|json|ya?ml|md|sql|sh|html|css)\b",
            text, re.IGNORECASE
        )),
    }


def check_thresholds(metrics: dict, thresholds: dict) -> bool:
    """Check if metrics meet thresholds."""
    if not thresholds:
        return False
    
    checks = [
        ("minCodeFences", lambda t, m: m["code_fence_count"] >= t),
        ("minFilePaths", lambda t, m: m["file_path_count"] >= t),
        ("minTokens", lambda t, m: m["estimated_tokens"] >= t),
        ("minWords", lambda t, m: len(m["words"]) >= t),
        ("maxWords", lambda t, m: len(m["words"]) <= t),
        ("maxTokens", lambda t, m: m["estimated_tokens"] <= t),
    ]
    
    for key, fn in checks:
        if key in thresholds:
            if not fn(thresholds[key], metrics):
                return False
    return True


def classify(prompt: str) -> dict:
    """Classify a prompt against categories (priority order)."""
    metrics = analyze_prompt(prompt)
    categories = _categories_config.get("categories", {})
    fallback = _categories_config.get("fallback", {"model": "minimax"})
    
    # Sort categories by priority (higher first)
    sorted_categories = sorted(
        categories.items(),
        key=lambda x: x[1].get("priority", 0),
        reverse=True
    )
    
    for category_key, category in sorted_categories:
        triggers = category.get("triggers", {})
        
        # Check keywords
        if triggers.get("keywords") and contains_any(metrics["lower"], triggers["keywords"]):
            model = get_model(category.get("model", "minimax"))
            return {
                "category": category_key,
                "model_key": category.get("model", "minimax"),
                "model_id": model.get("id") if model else category.get("model"),
                "reason": f"{category_key}_keyword",
                "enable_thinking": category.get("enableThinking", False),
                "metrics": metrics,
            }
        
        # Check patterns
        if triggers.get("patterns") and matches_any_pattern(metrics["text"], triggers["patterns"]):
            model = get_model(category.get("model", "minimax"))
            return {
                "category": category_key,
                "model_key": category.get("model", "minimax"),
                "model_id": model.get("id") if model else category.get("model"),
                "reason": f"{category_key}_pattern",
                "enable_thinking": category.get("enableThinking", False),
                "metrics": metrics,
            }
        
        # Check thresholds
        if triggers.get("thresholds") and check_thresholds(metrics, triggers["thresholds"]):
            model = get_model(category.get("model", "minimax"))
            return {
                "category": category_key,
                "model_key": category.get("model", "minimax"),
                "model_id": model.get("id") if model else category.get("model"),
                "reason": f"{category_key}_threshold",
                "enable_thinking": category.get("enableThinking", False),
                "metrics": metrics,
            }
    
    # Fallback
    model = get_model(fallback.get("model", "minimax"))
    return {
        "category": "default",
        "model_key": fallback.get("model", "minimax"),
        "model_id": model.get("id") if model else fallback.get("model"),
        "reason": "fallback",
        "enable_thinking": False,
        "metrics": metrics,
    }


def resolve_explicit_override(input_data: Any) -> Optional[dict]:
    """Resolve explicit model override from prompt or event."""
    # Handle both string prompt and dict event
    if isinstance(input_data, str):
        prompt = input_data
        event = {}
    else:
        prompt = str(input_data.get("prompt", "") if isinstance(input_data, dict) else "")
        event = input_data or {}
    
    models = get_models()
    
    # Check for --model flag in prompt
    match = re.search(r"(?:^|\s)(?:--model|model)\s*=?\s*([a-z0-9._\/-]+)", prompt, re.IGNORECASE)
    if match and match.group(1):
        resolved = get_model(match.group(1))
        if resolved:
            return resolved
    
    # Check event.model
    if event.get("model"):
        resolved = get_model(event["model"])
        if resolved:
            return resolved
    
    # Check event.metadata?.model
    metadata = event.get("metadata", {})
    if metadata.get("model"):
        resolved = get_model(metadata["model"])
        if resolved:
            return resolved
    
    return None


def route(input_data: Any) -> dict:
    """Main routing decision."""
    explicit = resolve_explicit_override(input_data)
    
    prompt = input_data.get("prompt") if isinstance(input_data, dict) else str(input_data or "")
    classification = classify(prompt)
    
    if explicit:
        return {
            "type": "explicit",
            "model_key": explicit.get("key"),
            "model_id": explicit.get("id"),
            "reason": "explicit_override",
            "classification": classification,
        }
    
    return {
        "type": classification["category"],
        "model_key": classification["model_key"],
        "model_id": classification["model_id"],
        "reason": classification["reason"],
        "enable_thinking": classification.get("enable_thinking", False),
    }


# Convenience functions for skill integration
def should_use_cheap_model(prompt: str) -> bool:
    """Quick check if prompt should use cheap model (MiniMax)."""
    result = route(prompt)
    return result.get("model_key") == "minimax"


def get_router_decision(prompt: str) -> dict:
    """Get routing decision for a prompt."""
    return route(prompt)


# CLI
if __name__ == "__main__":
    import sys
    
    args = sys.argv[1:]
    
    if "--list" in args or "-l" in args:
        models = get_models()
        print("Available models:")
        for key, model in models.items():
            print(f"  {key}: {model.get('id')}")
            print(f"    aliases: {', '.join(model.get('aliases', [])) or 'none'}")
            cost = model.get("cost", {})
            print(f"    cost: ${cost.get('input', '?')}/${cost.get('output', '?')} ({cost.get('unit', '')})")
            print(f"    context: {model.get('context', '?')}")
            print()
    elif "--help" in args or "-h" in args:
        print("Usage: python -m classifier [options] [prompt]")
        print("Options:")
        print("  -l, --list          List available models")
        print("  -h, --help          Show this help")
    elif args:
        prompt = " ".join(args)
        result = route(prompt)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python -m classifier <prompt>")
        print("Try: python -m classifier --help")
