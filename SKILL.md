---
name: model-router-intelligent
description: Intelligent cost-optimizing model router for OpenClaw. Routes prompts to optimal models based on task complexity.
---

# Intelligent Model Router

Python-based model routing skill for OpenClaw. Provides intelligent cost-optimized routing between OpenRouter models.

## Quick Use

```python
from skills.model_router_intelligent.classifier import route, should_use_cheap_model

# Classify a prompt
result = route("fix this bug")
# -> {'type': 'coding', 'model_key': 'minimax', 'model_id': '...', 'reason': 'coding_keyword'}

# Quick check
if should_use_cheap_model("hello"):
    print("Use MiniMax")
```

## Default Categories

| Category | Model | Triggers |
|----------|-------|----------|
| heartbeat | MiniMax | maintenance |
| vision | Kimi | images, PDFs |
| recall | Kimi | context recovery |
| complex | Kimi | architecture, planning |
| coding | MiniMax | code edits |
| simple | MiniMax | short chat |

## Configuration

Edit `config/models.json` to add/modify models.
Edit `config/categories.json` to add/modify classification rules.

## Testing

```bash
python -m skills.model_router_intelligent.classifier "your prompt"
python -m skills.model_router_intelligent.classifier --list
```
