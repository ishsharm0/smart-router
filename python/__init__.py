"""
OpenClaw skill: model-router-intelligent

Provides intelligent model routing for OpenClaw agents.
Use this skill when you need to decide which model to use for a task.

Usage in your agent code:
    from skills.model_router_intelligent.classifier import route, should_use_cheap_model
    
    decision = route("fix this bug")
    if decision["model_key"] == "minimax":
        # Use MiniMax
    else:
        # Use Kimi

Or call the skill directly for auto-routing.
"""

import json
import sys
from pathlib import Path

# Add skill path for imports
SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

from classifier import (
    route,
    classify,
    get_models,
    get_model,
    should_use_cheap_model,
    get_router_decision,
    load_configs,
)


def execute(prompt: str) -> dict:
    """
    Execute the skill - route a prompt to the optimal model.
    
    Args:
        prompt: The user's prompt/message
        
    Returns:
        dict with routing decision:
        {
            "type": "coding|vision|complex|simple|...",
            "model_key": "minimax|kimi|...",
            "model_id": "provider/model-id",
            "reason": "why this model was chosen",
            "enable_thinking": bool
        }
    """
    return route(prompt)


def execute_for_skill(context: dict) -> dict:
    """
    OpenClaw skill entry point.
    
    Expected context keys:
        - prompt: the message to classify
        - action: optional "route", "classify", "list_models"
    
    Returns routing decision or requested info.
    """
    action = context.get("action", "route")
    prompt = context.get("prompt", "")
    
    if action == "list_models" or action == "list":
        return {
            "models": get_models(),
            "action": "list_models",
        }
    
    if action == "classify":
        return classify(prompt)
    
    # Default: route
    return route(prompt)


# Skill metadata for OpenClaw
SKILL_METADATA = {
    "name": "model-router-intelligent",
    "description": "Intelligent cost-optimizing model router. Routes prompts to optimal models based on task complexity.",
    "version": "2.0.0",
    "models": ["minimax", "kimi"],
    "categories": ["heartbeat", "vision", "recall", "complex", "coding", "simple"],
}


# Quick access functions for common use cases
__all__ = [
    "route",
    "classify", 
    "get_models",
    "get_model",
    "should_use_cheap_model",
    "get_router_decision",
    "load_configs",
    "execute",
    "execute_for_skill",
    "SKILL_METADATA",
]


# Demo/test when run directly
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Model Router Intelligent")
    parser.add_argument("prompt", nargs="*", help="Prompt to classify")
    parser.add_argument("--list", "-l", action="store_true", help="List available models")
    parser.add_argument("--classify", "-c", help="Classify a prompt")
    parser.add_argument("--cheap", "-q", help="Check if prompt should use cheap model")
    
    args = parser.parse_args()
    
    if args.list:
        models = get_models()
        print("Available models:")
        for key, model in models.items():
            print(f"  {key}: {model.get('id')}")
            print(f"    aliases: {', '.join(model.get('aliases', [])) or 'none'}")
            cost = model.get("cost", {})
            print(f"    cost: ${cost.get('input', '?')}/${cost.get('output', '?')}")
            print()
    elif args.classify:
        result = classify(args.classify)
        print(json.dumps(result, indent=2))
    elif args.cheap:
        result = should_use_cheap_model(args.cheap)
        print(f"Use cheap model: {result}")
    elif args.prompt:
        prompt = " ".join(args.prompt)
        result = route(prompt)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()