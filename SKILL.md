---
name: smart-router
description: Cost-optimizing model router. Routes prompts to optimal models (MiniMax for simple, Kimi for complex).
---

# Smart Router

Intelligent model routing based on task complexity. Saves costs by using cheap models (MiniMax) for simple tasks, expensive models (Kimi) only when needed.

## For Agents

### Import

```python
from skills.smart_router.classifier import route, classify, should_use_cheap_model
```

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `route(prompt)` | dict | Full routing decision with model_id |
| `classify(prompt)` | dict | Category + reason + thinking setting |
| `should_use_cheap_model(prompt)` | bool | True if should use MiniMax |

### Response Format

```python
result = route("fix this bug in auth.py")

{
  "type": "coding",                          # matched category
  "model_key": "minimax",                    # model identifier
  "model_id": "minimax/minimax-m2.5",        # full model ID for API
  "reason": "coding_keyword",                # what triggered match
  "enable_thinking": false                   # thinking on/off for this category
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
| 100 | heartbeat | MiniMax | heartbeat maintenance, check_reminders_silent |
| 90 | vision | Kimi | image, pdf, screenshot, diagram, ui |
| 85 | recall | Kimi | what were we talking about, prior context |
| 70 | coding | MiniMax | code, fix, debug, function, class, api, git |
| 60 | complex | Kimi | architecture, system design, multi-file, 700+ tokens |
| 50 | simple | MiniMax | hi, ok, ping, status (<8 words) |

## Model Selection Only

This skill routes prompts to the optimal model. Thinking/reasoning is controlled globally by `agents.defaults.thinkingDefault` in openclaw.json (currently: off).

## Configuration

Models: `config/models.json`
Categories: `config/categories.json`

## Testing

```bash
# Test a prompt
python3 -m python.classifier "fix this bug"

# List models
python3 -m python.classifier --list
```
