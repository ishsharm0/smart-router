---
name: smart-router
description: Intelligent model router. Routes prompts to optimal models based on task type and model strengths.
version: 2.0.1
---

# Smart Router

Intelligent model routing based on task type, complexity, and model benchmarks. Routes to the best model for each task.

## For Agents

### Import

```python
from skills.smart_router.classifier import route, classify, should_use_cheap_model, get_model
```

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `route(prompt)` | dict | Full routing decision with model_id |
| `classify(prompt)` | dict | Category + reason + metrics |
| `should_use_cheap_model(prompt)` | bool | True if MiniMax (fast/cheap) |
| `get_model(model_key)` | dict | Model config by key or alias |

### Response Format

```python
result = route("fix this bug in auth.py")

{
  "type": "coding",                          # matched category
  "model_key": "minimax",                    # model identifier
  "model_id": "MiniMax-M2.5",                # full model ID for API
  "reason": "coding_keyword",                # what triggered match
  "enable_thinking": false                   # whether to enable thinking mode
}
```

### Explicit Override

Users can force a model with `--model=<name>`:
- `--model=kimi` → Uses Kimi K2.5
- `--model=minimax` → Uses MiniMax M2.5
- `--model=qwen` → Uses Qwen3.5-Plus

Override takes priority over automatic routing.

## Categories (Priority Order)

| Priority | Category | Model | Keywords |
|----------|----------|-------|----------|
| 100 | heartbeat | MiniMax | heartbeat_ok, check_reminders, internal heartbeat |
| 95 | vision | Kimi | image, pdf, screenshot, diagram, chart, visual |
| 90 | frontend | Kimi | css, html, react, tailwind, component, ui, layout |
| 85 | complex | Qwen | explain, architecture, science, math, theory, prove, derive |
| 80 | coding | MiniMax | code, fix, debug, bug, error, function, api, refactor |
| 80 | axiom | MiniMax | axiom, trading, playwright, wallet tracker, cdp |
| 50 | simple | MiniMax | hi, hello, ok, thanks, ping, status (<8 words) |
| — | fallback | MiniMax | Everything else |

## Model Strengths

| Model | Best For | Benchmarks |
|-------|----------|------------|
| **MiniMax M2.5** | Coding, chat, speed | SWE-Bench: 80.2% |
| **Qwen3.5-Plus** | Science, reasoning, large context | GPQA: 88.4% |
| **Kimi K2.5** | Vision, frontend, agent swarms | BrowseComp: 78.4% |

## Configuration

Models: `config/models.json`
Categories: `config/categories.json`

Add new models and categories by editing these config files. Config is shared across Python skill and gateway extension.

## Testing

```bash
# Test a prompt
python3 -m python.classifier "fix this bug"

# Test different categories
python3 -m python.classifier "explain quantum physics"  # complex → qwen
python3 -m python.classifier "analyze this image"       # vision → kimi
python3 -m python.classifier "hi"                       # simple → minimax

# List models
python3 -m python.classifier --list
```

## Notes

- Categories evaluated in priority order (highest first)
- First match wins
- Fallback: MiniMax M2.5
- All configs are hot-reloaded on gateway restart
