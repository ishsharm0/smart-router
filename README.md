# Smart Router

> Cost-optimizing model router for OpenClaw. Automatically routes prompts to the optimal model based on task complexity.

## What This Skill Does

The **Smart Router** analyzes each prompt and selects the best model for the task:

| Task Type | Model | Why |
|-----------|-------|-----|
| Background maintenance | Default model | Lightweight checks |
| Simple chat | Default model | Fast, cheap responses |
| Code editing | Strong model | Best for code tasks |
| Vision/Images | Multimodal model | Image understanding |
| Context recall | Large context model | Long conversation memory |
| Complex reasoning | Advanced model | Deep reasoning capability |

**Goal:** Use cheaper/faster models for simple tasks, reserve expensive models only when needed.

---

## For Agents (AI-to-AI)

### How I Route Prompts

```python
from skills.smart_router.classifier import route

# Input: any prompt string
decision = route("fix this bug in auth.py")

# Output:
# {
#   "type": "coding",           # category matched
#   "model_key": "minimax",      # which model to use
#   "model_id": "minimax/minimax-m2.5",
#   "reason": "coding_keyword",  # what triggered this
# }
```

### Key Functions

| Function | Returns | Use Case |
|----------|---------|----------|
| `route(prompt)` | dict | Full routing decision |
| `classify(prompt)` | dict | Category classification |
| `should_use_cheap_model(prompt)` | bool | Quick cheap/expensive check |
| `get_model(model_key)` | dict | Get model config by key |
| `resolve_explicit_override(prompt)` | dict | Check for `--model=...` |

### Explicit Override

Users can force a specific model:
```
--model=kimi
--model=minimax
--model=claude
```

---

## For Humans (Installation)

### Quick Install

```bash
# Via ClawHub (recommended)
clawhub install smart-router

# Or manual
cp -r smart-router/ ~/.openclaw/workspace/skills/
```

### Enable Auto-Routing (Optional)

The router works as a skill by default. For automatic model selection on every prompt:

```bash
# Enable the smart-router plugin
openclaw config patch --json '{"plugins":{"entries":{"smart-router":{"enabled":true}}}}'
openclaw gateway restart
```

### Test Installation

```bash
# Test routing
cd ~/.openclaw/workspace/skills/smart-router
python3 -m python.classifier "fix this bug"
# → {"type": "coding", "model_key": "minimax", ...}

python3 -m python.classifier "analyze this diagram"
# → {"type": "vision", "model_key": "kimi", ...}

# List all models
python3 -m python.classifier --list
```

---

## Configuration

### Default Models (Included)

| Key | Model ID | Strengths |
|----|---------|-----------|
| minimax | minimax/minimax-m2.5 | Coding, fast, cheap |
| kimi | moonshotai/kimi-k2.5 | Vision, reasoning, large context |

### Add a New Model

Edit `config/models.json`:

```json
{
  "models": {
    "claude": {
      "id": "anthropic/claude-3.5-sonnet",
      "name": "Claude 3.5 Sonnet",
      "provider": "openrouter",
      "cost": { "input": 3.00, "output": 15.00, "unit": "per-1m-tokens" },
      "context": 200000,
      "strengths": ["writing", "analysis"],
      "aliases": ["claude", "sonnet"],
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
      "model": "claude",
      "priority": 65,
      "description": "Content writing and editing",
      "triggers": {
        "keywords": ["write", "draft", "edit", "compose"]
      }
    }
  }
}
```

### Category Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Model key to route to |
| `priority` | number | Higher = checked first (100 = highest) |
| `triggers.keywords` | array | Match any keyword (case-insensitive) |
| `triggers.patterns` | array | Regex patterns |
| `triggers.thresholds` | object | minTokens, maxWords, minCodeFences, etc. |

---

## Debugging

```bash
# Enable debug logging
OPENCLAW_SMART_ROUTER_DEBUG=1 openclaw gateway restart

# Check logs
openclaw logs | grep SmartRouter
```

---

## File Structure

```
smart-router/
├── SKILL.md              # Agent instructions
├── README.md              # This file
├── config/
│   ├── models.json        # Model definitions
│   └── categories.json    # Routing rules
├── python/
│   └── classifier.py      # Core Python implementation
├── lib/
│   └── classifier.js      # JavaScript version
├── extension/
│   └── index.js           # Gateway plugin hook
└── scripts/
    └── router.js          # CLI helper
```

---

## Requirements

- OpenClaw 2026.2+
- OpenRouter API key (for model access)
- Python 3.8+ (for Python skill usage)

---

## License

MIT
