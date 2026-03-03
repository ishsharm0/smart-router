# Smart Router

> Intelligent model routing for OpenClaw. Automatically routes prompts to the optimal model based on task type, complexity, and model strengths.

## What This Skill Does

The **Smart Router** analyzes each prompt and selects the best model for the task using config-driven rules. Instead of using one model for everything, it routes to specialized models:

| Task Type | Model | Why |
|-----------|-------|-----|
| Simple chat, pings | MiniMax M2.5 | Fastest inference, low latency |
| Coding, debugging | MiniMax M2.5 | Best SWE-Bench score (80.2%) |
| Science, math, reasoning | Qwen3.5-Plus | Best GPQA-Diamond (88.4%) |
| Vision, images, PDFs | Kimi K2.5 | Best multimodal capabilities |
| Frontend, UI, CSS | Kimi K2.5 | Strongest at visual-to-code |
| Background maintenance | MiniMax M2.5 | Fast, lightweight |

**Goal:** Match each task to the model that excels at it — faster responses, better quality, optimal resource usage.

---

## Model Benchmarks (2026)

| Model | SWE-Bench | GPQA-Diamond | Intelligence Index | Speed | Best For |
|-------|-----------|--------------|-------------------|-------|----------|
| **MiniMax M2.5** | 80.2% | — | ~80 | ⚡⚡⚡ | Coding, chat, tool use |
| **Qwen3.5-Plus** | 76.4% | 88.4% | ~82 | ⚡⚡ | Science, reasoning, large context |
| **Kimi K2.5** | 76.8% | 87.6% | ~85 | ⚡ | Vision, frontend, agent swarms |

*Data from Artificial Analysis, Hugging Face, and community benchmarks (Feb 2026)*

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
#   "model_id": "MiniMax-M2.5",
#   "reason": "coding_keyword",  # what triggered this
# }
```

### Key Functions

| Function | Returns | Use Case |
|----------|---------|----------|
| `route(prompt)` | dict | Full routing decision with model_id |
| `classify(prompt)` | dict | Category + reason for classification |
| `should_use_cheap_model(prompt)` | bool | Quick cheap/expensive check |
| `get_model(model_key)` | dict | Get model config by key or alias |
| `resolve_explicit_override(prompt)` | dict | Check for `--model=...` override |

### Explicit Override

Users can force a specific model with `--model=<name>`:
```
--model=kimi      → Routes to Kimi K2.5
--model=minimax   → Routes to MiniMax M2.5
--model=qwen      → Routes to Qwen3.5-Plus
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

The router works as a skill by default. For automatic model selection on every prompt, enable it as a plugin:

```bash
# Enable the smart-router plugin
openclaw config patch --json '{"plugins":{"entries":{"smart-router":{"enabled":true}}}}'
openclaw gateway restart
```

### Test Installation

```bash
# Test routing decisions
cd ~/.openclaw/workspace/skills/smart-router

python3 -m python.classifier "fix this bug"
# → {"type": "coding", "model_key": "minimax", "model_id": "MiniMax-M2.5", ...}

python3 -m python.classifier "explain quantum entanglement"
# → {"type": "complex", "model_key": "qwen", "model_id": "qwen3.5-plus", ...}

python3 -m python.classifier "analyze this screenshot"
# → {"type": "vision", "model_key": "kimi", "model_id": "kimi-k2.5", ...}

# List all available models
python3 -m python.classifier --list
```

---

## Configuration

### Default Models (Included)

| Key | Model ID | Provider | Strengths |
|-----|----------|----------|-----------|
| `minimax` | MiniMax-M2.5 | Alibaba | Coding, speed, tool use |
| `qwen` | qwen3.5-plus | Alibaba | Reasoning, science, large context |
| `kimi` | kimi-k2.5 | Alibaba | Vision, frontend, agent swarms |

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
      "strengths": ["writing", "analysis", "conversation"],
      "weaknesses": ["expensive", "slower than minimax"],
      "benchmarks": {
        "swe-bench": 77.2,
        "gpqa-diamond": 85.1
      },
      "aliases": ["claude", "sonnet", "anthropic"],
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
      "description": "Content writing, editing, and creative work",
      "triggers": {
        "keywords": ["write", "draft", "edit", "compose", "rewrite", "polish"]
      }
    }
  }
}
```

### Category Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Model key to route to (must exist in models.json) |
| `priority` | number | Higher = checked first (100 = highest priority) |
| `description` | string | Human-readable description of the category |
| `triggers.keywords` | array | Match any keyword (case-insensitive substring) |
| `triggers.patterns` | array | Regex patterns to match (Python regex syntax) |
| `triggers.thresholds` | object | Structural checks: minTokens, maxWords, minCodeFences, minFilePaths, etc. |

### Threshold Options

| Threshold | Type | Description |
|-----------|------|-------------|
| `minTokens` | number | Minimum estimated tokens (chars / 4) |
| `maxTokens` | number | Maximum estimated tokens |
| `minWords` | number | Minimum word count |
| `maxWords` | number | Maximum word count |
| `minCodeFences` | number | Minimum ``` code blocks |
| `minFilePaths` | number | Minimum file paths detected |

---

## Routing Logic

Categories are evaluated in **priority order** (highest first). First match wins.

1. **Priority 100**: Heartbeat (background maintenance)
2. **Priority 95**: Vision (images, PDFs, diagrams)
3. **Priority 90**: Frontend (UI, CSS, React, Tailwind)
4. **Priority 85**: Complex (science, math, reasoning, "explain")
5. **Priority 80**: Coding (debug, fix, implement, refactor)
6. **Priority 80**: Axiom (trading automation)
7. **Priority 50**: Simple (chat, pings, <8 words)
8. **Fallback**: MiniMax M2.5 (default for everything else)

---

## Debugging

```bash
# Enable debug logging
export OPENCLAW_SMART_ROUTER_DEBUG=1
openclaw gateway restart

# Check gateway logs
openclaw logs --follow | grep -i router

# Test a prompt manually
python3 -m python.classifier "your prompt here"
```

---

## File Structure

```
smart-router/
├── SKILL.md               # Agent instructions (internal)
├── README.md              # This file (public docs)
├── config/
│   ├── models.json        # Model definitions and benchmarks
│   └── categories.json    # Routing rules and triggers
├── python/
│   ├── classifier.py      # Core Python implementation
│   └── config/            # Synced config copies
├── extension/
│   ├── index.js           # Gateway plugin hook
│   └── config/            # Synced config copies
├── lib/
│   └── classifier.js      # JavaScript version (legacy)
├── scripts/
│   └── router.js          # CLI helper
└── references/
    └── costs.md           # Model pricing reference
```

---

## Requirements

- **OpenClaw** 2026.2+
- **Python** 3.8+ (for Python skill usage)
- **Model provider** configured (Alibaba, OpenRouter, etc.)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.1 | Mar 2026 | Benchmark-based routing: MiniMax default, Qwen reasoning, Kimi vision |
| 2.0.0 | Feb 2026 | Config-driven routing, multi-provider support |
| 1.0.0 | Jan 2026 | Initial release |

---

## License

MIT

---

## Contributing

1. Add model benchmarks to `models.json`
2. Add routing category to `categories.json`
3. Test with `python3 -m python.classifier "test prompt"`
4. Submit PR with benchmark sources

For model research and benchmark sources, see:
- [Artificial Analysis](https://artificialanalysis.ai)
- [Hugging Face Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
- [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA)
