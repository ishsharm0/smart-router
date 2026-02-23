---
name: model-router-intelligent
description: Intelligent cost-optimizing model router for OpenClaw with OpenRouter. Dynamically routes prompts to the cheapest appropriate model based on task complexity.
---

# Intelligent Model Router

Config-driven model routing for OpenClaw with OpenRouter. Routes prompts to optimal models based on task classification.

## Files

```
model-router-intelligent/
├── config/
│   ├── models.json        # Model definitions (id, cost, aliases)
│   └── categories.json    # Classification rules & priorities
├── lib/
│   └── classifier.js      # Core routing logic (shared)
├── extension/
│   └── index.js           # OpenClaw plugin
├── scripts/
│   └── router.js          # CLI for testing
├── README.md              # Installation guide
└── SKILL.md              # This file
```

## How It Works

1. Prompt arrives at `before_model_resolve` hook
2. Classifier checks explicit override (`--model minimax`)
3. Otherwise, matches against categories (priority order)
4. Returns provider + model override

## Categories (Priority Order)

1. **heartbeat** → MiniMax (maintenance)
2. **vision** → Kimi (images/PDFs)
3. **recall** → Kimi (context recovery)
4. **complex** → Kimi (architecture/planning)
5. **coding** → MiniMax (code/tool work)
6. **simple** → MiniMax (short chat)
7. **fallback** → MiniMax

## Customization

### Add a Model

Edit `config/models.json`:

```json
"newmodel": {
  "id": "provider/newmodel",
  "cost": { "input": 0.10, "output": 0.10 },
  "aliases": ["nm", "newm"]
}
```

### Add a Category

Edit `config/categories.json`. Add entry with:
- `model`: model key from models.json
- `priority`: higher = checked first
- `triggers.keywords`: array of matching strings
- `triggers.patterns`: array of regex strings
- `triggers.thresholds`: min/max tokens/words/code fences

## Usage

- Plugin auto-loads if enabled in openclaw.json
- Manual override: `--model minimax` or `--model kimi`
- Test: `node scripts/router.js "your prompt"`

## Debug

```bash
OPENCLAW_MODEL_ROUTER_DEBUG=1 openclaw gateway restart
tail -f ~/.openclaw/logs/model-router.log
```
