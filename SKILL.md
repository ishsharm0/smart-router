---
name: smart-router
description: Cost-optimizing model router. Routes prompts to optimal models based on task complexity.
---

# Smart Router

Intelligent model routing based on task complexity. Routes to the best model for each task type.

## For Agents

### Import

```python
from skills.smart_router.classifier import route, classify, should_use_cheap_model
```

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `route(prompt)` | dict | Full routing decision with model_id |
| `classify(prompt)` | dict | Category + reason |
| `should_use_cheap_model(prompt)` | bool | True if should use default model |

### Response Format

```python
result = route("fix this bug in auth.py")

{
  "type": "coding",                          # matched category
  "model_key": "minimax",                    # model identifier
  "model_id": "minimax/minimax-m2.5",        # full model ID for API
  "reason": "coding_keyword",                # what triggered match
}
```

### Explicit Override

Users can force a model with `--model=<name>`:
- `--model=kimi` → Uses Kimi
- `--model=minimax` → Uses MiniMax
- `--model=claude` → Uses Claude (if enabled)

## Categories (Priority Order)

| Priority | Category | Model | Keywords |
|----------|----------|-------|----------|
| 100 | heartbeat | default | maintenance, check_reminders |
| 90 | vision | multimodal | image, pdf, screenshot, diagram |
| 85 | recall | large-context | prior context, what were we talking about |
| 70 | coding | code-optimized | code, fix, debug, function, api |
| 60 | complex | advanced | architecture, system design, multi-file |
| 50 | simple | default | hi, ok, ping, status (<8 words) |

## Configuration

Models: `config/models.json`
Categories: `config/categories.json`

Add new models and categories by editing these config files.

## Testing

```bash
# Test a prompt
python3 -m python.classifier "fix this bug"

# List models
python3 -m python.classifier --list
```
