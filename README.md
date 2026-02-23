# Model Router Intelligent

Cost-optimizing model router for OpenClaw. Dynamically routes prompts to the cheapest appropriate model based on task complexity.

## Quick Install

```bash
# Clone or copy to workspace
cp -r model-router-intelligent/ ~/.openclaw/workspace/skills/

# Link extension (for automatic routing)
mkdir -p ~/.openclaw/extensions/model-router
ln -sf ../workspace/skills/model-router-intelligent/extension/index.js ~/.openclaw/extensions/model-router/index.js

# Copy config to extension
mkdir -p ~/.openclaw/extensions/model-router/{lib,config}
cp ~/.openclaw/workspace/skills/model-router-intelligent/lib/classifier.js ~/.openclaw/extensions/model-router/lib/
cp ~/.openclaw/workspace/skills/model-router-intelligent/config/*.json ~/.openclaw/extensions/model-router/config/

# Enable plugin
openclaw config patch --json '{"plugins":{"entries":{"model-router":{"enabled":true}}}}'
```

## Usage

### As Python Skill (Recommended)

```python
from skills.model_router_intelligent.classifier import route, should_use_cheap_model

# Get routing decision
decision = route("fix this bug")
print(decision)
# {'type': 'coding', 'model_key': 'minimax', 'model_id': 'minimax/minimax-m2.5', ...}

# Quick check
if should_use_cheap_model("hi"):
    print("Use MiniMax")
else:
    print("Use Kimi")
```

### Via CLI

```bash
# Test a prompt
python -m skills.model_router_intelligent.classifier "fix this bug"

# List models
python -m skills.model_router_intelligent.classifier --list

# Check if cheap model
python -m skills.model_router_intelligent.classifier --cheap "hi"
```

## Configuration

### Adding Models

Edit `config/models.json`:

```json
{
  "models": {
    "newmodel": {
      "id": "provider/model-id",
      "name": "Display Name",
      "provider": "openrouter",
      "cost": { "input": 0.10, "output": 0.10, "unit": "per-1m-tokens" },
      "context": 32000,
      "strengths": ["coding"],
      "aliases": ["nm", "newm"],
      "enabled": true
    }
  }
}
```

### Adding Categories

Edit `config/categories.json`:

```json
{
  "categories": {
    "my-category": {
      "model": "minimax",
      "priority": 75,
      "triggers": {
        "keywords": ["keyword1"],
        "patterns": ["^regex$"],
        "thresholds": { "minTokens": 500 }
      },
      "enableThinking": false
    }
  }
}
```

## Manual Override

```
--model minimax   # Force MiniMax
--model kimi     # Force Kimi
```

## Debug

```bash
OPENCLAW_MODEL_ROUTER_DEBUG=1 openclaw gateway restart
```

## Files

```
model-router-intelligent/
├── config/
│   ├── models.json        # Model definitions
│   └── categories.json    # Classification rules
├── python/
│   ├── __init__.py        # Skill entry point
│   ├── classifier.py      # Core routing logic
│   └── config/            # Local config copy
├── lib/
│   └── classifier.js      # JS version (for extension)
├── extension/
│   └── index.js           # Gateway plugin
├── README.md
└── SKILL.md
```

## Requirements

- OpenClaw 2026.2+
- OpenRouter API key
- Python 3.8+
