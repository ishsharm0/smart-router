---
name: smart-router
description: Intelligent model router. Routes prompts to optimal models based on task type and model strengths.
version: 2.1.0
presets: [minimal, alibaba-coding-plan, openrouter-all, enterprise]
---

# Smart Router

Intelligent model routing based on task type, complexity, and model benchmarks. Works with any LLM provider.

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
| `should_use_cheap_model(prompt)` | bool | True if using fast/cheap model |
| `get_model(model_key)` | dict | Model config by key or alias |
| `list_presets()` | list | Available preset names |

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
- `--model=opus` → Uses Claude Opus 4.6

Override takes priority over automatic routing.

## Categories (Priority Order)

Default routing (alibaba-coding-plan preset):

| Priority | Category | Model | Keywords |
|----------|----------|-------|----------|
| 100 | heartbeat | minimax | heartbeat_ok, check_reminders, internal heartbeat |
| 95 | vision | kimi | image, pdf, screenshot, diagram, chart, visual |
| 90 | frontend | kimi | css, html, react, tailwind, component, ui, layout |
| 85 | complex | qwen | explain, architecture, science, math, theory, prove, derive |
| 80 | coding | minimax | code, fix, debug, bug, error, function, api, refactor |
| 80 | axiom | minimax | axiom, trading, playwright, wallet tracker, cdp |
| 50 | simple | minimax | hi, hello, ok, thanks, ping, status (<8 words) |
| — | fallback | minimax | Everything else |

**Note:** Categories vary by preset. Check `config/categories.json` for active routing.

## Model Strengths (by Preset)

### alibaba-coding-plan (Active)

| Model | Best For | Benchmarks |
|-------|----------|------------|
| **MiniMax M2.5** | Coding, chat, speed | SWE-Bench: 80.2% |
| **Qwen3.5-Plus** | Science, reasoning, large context | GPQA: 88.4% |
| **Kimi K2.5** | Vision, frontend, agent swarms | BrowseComp: 78.4% |

### openrouter-all

| Model | Best For | Cost/1M |
|-------|----------|---------|
| GPT-5.3 Codex | Critical coding, agentic | $0.75/$3.00 |
| Claude Opus 4.6 | Complex reasoning, writing | $15/$75 |
| Claude Sonnet 4.6 | Balanced tasks | $3/$15 |
| Gemini 3.1 Pro | Vision, video, large context | $0.50/$2.00 |
| MiniMax M2.5 | Fast coding | $0.30/$1.20 |

### enterprise

| Model | Best For |
|-------|----------|
| GPT-5.3 Codex | Default, coding, agentic tasks |
| Claude Opus 4.6 | Architecture, analysis, writing |
| Gemini 3.1 Pro | Vision, multimodal, video |
| Claude Sonnet 4.6 | Simple tasks (cost savings) |

## Configuration

Models: `config/models.json`
Categories: `config/categories.json`
Presets: `presets/*.json`

### Load a Preset

```bash
python3 scripts/load-preset.py <preset-name>

# Examples:
python3 scripts/load-preset.py minimal
python3 scripts/load-preset.py openrouter-all
python3 scripts/load-preset.py enterprise
```

### Add a Model

Edit `config/models.json`:

```json
{
  "models": {
    "my-model": {
      "id": "provider/model-id",
      "name": "Friendly Name",
      "provider": "provider",
      "context": 100000,
      "strengths": ["coding", "chat"],
      "benchmarks": { "swe-bench": 75 },
      "aliases": ["my-model", "custom"],
      "enabled": true
    }
  }
}
```

### Add a Category

Edit `config/categories.json`:

```json
{
  "categories": {
    "writing": {
      "model": "my-model",
      "priority": 65,
      "description": "Content writing and editing",
      "triggers": {
        "keywords": ["write", "draft", "edit", "compose"]
      }
    }
  }
}
```

## Testing

```bash
# Test a prompt
python3 -m python.classifier "fix this bug"

# Test different categories
python3 -m python.classifier "explain quantum physics"  # complex
python3 -m python.classifier "analyze this image"       # vision
python3 -m python.classifier "hi"                       # simple

# List models
python3 -m python.classifier --list

# List presets
ls presets/
```

## Notes

- Categories evaluated in priority order (highest first)
- First match wins
- Fallback: configured per preset (usually fastest/cheapest model)
- All configs are hot-reloaded on gateway restart
- Presets are provider-agnostic — adjust model IDs for your setup

## Available Presets

| Preset | Models | Best For |
|--------|--------|----------|
| `minimal` | 2 | Simple setups, local LLMs |
| `alibaba-coding-plan` | 3 | Alibaba Cloud free tier |
| `openrouter-all` | 7 | Full OpenRouter access |
| `enterprise` | 4 | Production, highest quality |
