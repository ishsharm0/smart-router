# Model Router Intelligent

Cost-optimizing model router for OpenClaw with OpenRouter. Dynamically routes prompts to the cheapest appropriate model based on task complexity.

## Quick Install

```bash
# 1. Copy skill to workspace
mkdir -p ~/.openclaw/workspace/skills/model-router-intelligent
cp -r /path/to/skill/* ~/.openclaw/workspace/skills/model-router-intelligent/

# 2. Link extension
mkdir -p ~/.openclaw/extensions/model-router
ln -sf ../workspace/skills/model-router-intelligent/extension/index.js ~/.openclaw/extensions/model-router/index.js

# 3. Enable plugin in openclaw.json
openclaw config patch --json '{"plugins":{"entries":{"model-router":{"enabled":true}}}}'
```

## Configuration

### Adding New Models

Edit `config/models.json`:

```json
{
  "models": {
    "my-model": {
      "id": "provider/model-id",
      "name": "Display Name",
      "provider": "openrouter",
      "cost": { "input": 0.10, "output": 0.10, "unit": "per-1m-tokens" },
      "context": 32000,
      "strengths": ["coding", "reasoning"],
      "aliases": ["alias1", "alias2"],
      "enabled": true
    }
  }
}
```

### Adding New Categories

Edit `config/categories.json`. Categories are matched by priority (highest first):

```json
{
  "categories": {
    "my-category": {
      "model": "my-model",
      "priority": 75,
      "description": "What this category handles",
      "triggers": {
        "keywords": ["keyword1", "keyword2"],
        "patterns": ["^regex_pattern$"],
        "thresholds": { "minTokens": 500 }
      },
      "enableThinking": false
    }
  }
}
```

### Disabling a Model

Set `enabled: false` in `config/models.json`:

```json
{
  "models": {
    "kimi": {
      "enabled": false
    }
  }
}
```

## Manual Override

In any prompt, specify model explicitly:

```
--model minimax   # Force MiniMax
--model kimi     # Force Kimi
--model deepseek  # Any model alias
```

## Debug Mode

```bash
OPENCLAW_MODEL_ROUTER_DEBUG=1 openclaw gateway restart
```

Check logs:

```bash
tail -f ~/.openclaw/logs/model-router.log
```

## Test Routing

```bash
# Test a prompt
node ~/.openclaw/workspace/skills/model-router-intelligent/scripts/router.js "fix this bug"

# Interactive mode
node ~/.openclaw/workspace/skills/model-router-intelligent/scripts/router.js --interactive

# List models
node ~/.openclaw/workspace/skills/model-router-intelligent/scripts/router.js --list
```

## Default Categories

| Category | Model | Triggers |
|----------|-------|----------|
| heartbeat | MiniMax | maintenance checks |
| vision | Kimi | images, PDFs, UI |
| recall | Kimi | context recovery |
| complex | Kimi | architecture, planning |
| coding | MiniMax | code edits, debugging |
| simple | MiniMax | short chat, pings |

## Requirements

- OpenClaw 2026.2+
- OpenRouter API key in environment
- Node.js 18+
