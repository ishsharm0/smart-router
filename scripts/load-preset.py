#!/usr/bin/env python3
"""
Preset loader for Smart Router.
Copies preset configurations to active config directory.

Usage:
    python3 load-preset.py <preset-name>
    
Examples:
    python3 load-preset.py minimal
    python3 load-preset.py openrouter-all
    python3 load-preset.py alibaba-coding-plan
"""

import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PRESETS_DIR = SCRIPT_DIR.parent / "presets"
CONFIG_DIR = SCRIPT_DIR.parent / "config"


def load_preset(preset_name: str) -> dict:
    """Load a preset configuration."""
    preset_path = PRESETS_DIR / f"{preset_name}.json"
    
    if not preset_path.exists():
        print(f"❌ Preset not found: {preset_name}")
        print(f"\nAvailable presets:")
        for p in PRESETS_DIR.glob("*.json"):
            print(f"  - {p.stem}")
        sys.exit(1)
    
    with open(preset_path, "r") as f:
        return json.load(f)


def extract_models_config(preset: dict) -> dict:
    """Extract models configuration from preset."""
    return {
        "$schema": preset.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "version": preset.get("version", "2.1.0"),
        "description": "Active model configuration. Loaded from preset.",
        "preset": {
            "name": preset.get("name", "unknown"),
            "path": f"../presets/{preset.get('name', 'unknown').replace(' ', '-').lower()}.json",
            "description": preset.get("description", "")
        },
        "models": preset.get("models", {}),
        "defaults": preset.get("defaults", {"fallback": "fast", "explicitOverride": True}),
        "budget": preset.get("budget", {})
    }


def extract_categories_config(preset: dict) -> dict:
    """Extract categories configuration from preset."""
    routing = preset.get("routing", {})
    categories = routing.get("categories", {})
    fallback = routing.get("fallback", "fast")
    
    # Convert keyword-only categories to full format
    formatted_categories = {}
    for cat_name, cat_config in categories.items():
        formatted_categories[cat_name] = {
            "model": cat_config.get("model", fallback),
            "priority": cat_config.get("priority", 50),
            "description": f"{cat_name} category",
            "triggers": {}
        }
        
        if "keywords" in cat_config:
            formatted_categories[cat_name]["triggers"]["keywords"] = cat_config["keywords"]
        if "patterns" in cat_config:
            formatted_categories[cat_name]["triggers"]["patterns"] = cat_config["patterns"]
        if "thresholds" in cat_config:
            formatted_categories[cat_name]["triggers"]["thresholds"] = cat_config["thresholds"]
    
    return {
        "$schema": preset.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "version": preset.get("version", "2.1.0"),
        "description": "Active routing configuration. Loaded from preset.",
        "preset": {
            "name": preset.get("name", "unknown"),
            "path": f"../presets/{preset.get('name', 'unknown').replace(' ', '-').lower()}.json",
            "description": preset.get("description", "")
        },
        "categories": formatted_categories,
        "fallback": {
            "model": fallback,
            "description": f"Default fallback model: {fallback}"
        }
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 load-preset.py <preset-name>")
        print("\nAvailable presets:")
        for p in PRESETS_DIR.glob("*.json"):
            preset_data = json.load(open(p))
            models = len(preset_data.get("models", {}))
            print(f"  - {p.stem}: {models} models")
        sys.exit(1)
    
    preset_name = sys.argv[1]
    print(f"Loading preset: {preset_name}")
    
    # Load preset
    preset = load_preset(preset_name)
    print(f"✓ Found preset: {preset.get('name', preset_name)}")
    
    # Extract and save models config
    models_config = extract_models_config(preset)
    models_path = CONFIG_DIR / "models.json"
    with open(models_path, "w") as f:
        json.dump(models_config, f, indent=2)
    print(f"✓ Wrote {models_path}")
    
    # Extract and save categories config
    categories_config = extract_categories_config(preset)
    categories_path = CONFIG_DIR / "categories.json"
    with open(categories_path, "w") as f:
        json.dump(categories_config, f, indent=2)
    print(f"✓ Wrote {categories_path}")
    
    # Sync to extension and python subdirectories
    for subdir in ["extension/config", "python/config"]:
        subdir_path = SCRIPT_DIR.parent / subdir
        if subdir_path.exists():
            with open(subdir_path / "models.json", "w") as f:
                json.dump(models_config, f, indent=2)
            with open(subdir_path / "categories.json", "w") as f:
                json.dump(categories_config, f, indent=2)
            print(f"✓ Synced to {subdir}/")
    
    print(f"\n✅ Preset '{preset_name}' loaded successfully!")
    print(f"\nNext steps:")
    print(f"  1. Edit config/models.json if needed (adjust model IDs for your provider)")
    print(f"  2. Test: python3 -m python.classifier \"test prompt\"")
    print(f"  3. Restart gateway: openclaw gateway restart")


if __name__ == "__main__":
    main()
