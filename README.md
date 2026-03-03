# Smart Router

> Intelligent model routing for any LLM setup. Automatically routes prompts to the optimal model based on task type, complexity, and model strengths.

**Works with:** OpenRouter, Alibaba Cloud, Ollama, LM Studio, vLLM, Anthropic Direct, OpenAI Direct, Google AI, and more.

---

## Quick Start

### 1. Choose a Preset

Smart Router includes pre-configured presets for common setups:

| Preset | Models | Best For | Cost |
|--------|--------|----------|------|
| `minimal` | 2 models | Simple setups, local LLMs, budget | $ |
| `alibaba-coding-plan` | 3 models | Alibaba Cloud users (free tier) | Free* |
| `openrouter-all` | 7 models | Full OpenRouter access | $$ |
| `enterprise` | 4 models | Production, highest quality | $$$$ |

\* Alibaba Coding Plan: 1200 requests per 5hr shared pool

### 2. Install

```bash
# Via ClawHub (recommended)
clawhub install smart-router

# Or manual
cp -r smart-router/ ~/.openclaw/workspace/skills/
```

### 3. Load a Preset

```bash
# Copy your chosen preset to active config
cd ~/.openclaw/workspace/skills/smart-router

# Example: Use OpenRouter preset
cp presets/openrouter-all.json config/models.json
cp presets/openrouter-all.json config/categories.json

# Or use the included script
python3 scripts/load-preset.py openrouter-all
```

### 4. Customize (Optional)

Edit `config/models.json` to adjust model IDs for your provider:

```json
{
  "models": {
    "fast": {
      "id": "anthropic/claude-sonnet-4.6",  // Your model ID
      "enabled": true,
      "default": true
    }
  }
}
```

### 5. Test

```bash
python3 -m python.classifier "fix this bug"
# → {"type": "coding", "model_key": "fast", "model_id": "..."}
```

---

## What This Does

Smart Router analyzes each prompt and routes to the best model:

| If your prompt is... | Route to | Why |
|---------------------|----------|-----|
| "hi", "thanks", "ping" | Fast model | Low latency, cheap |
| "fix this bug", "implement feature" | Coding model | Best SWE-Bench score |
| "explain quantum physics" | Reasoning model | Best GPQA score |
| "analyze this screenshot" | Vision model | Best multimodal |
| "write an email" | Writing model | Best prose quality |

**Result:** Better quality responses, lower costs, faster responses for simple tasks.

---

## Available Presets

### `minimal` (2 Models)

Bare minimum setup. Works with any provider.

```json
{
  "fast": "Your fast coding/chat model",
  "smart": "Your smart reasoning/vision model"
}
```

**Example configs:**
- OpenRouter: `claude-sonnet-4.6` + `gemini-3.1-pro`
- Ollama: `llama3.1:8b` + `llama3.1:70b`
- Alibaba: `MiniMax-M2.5` + `qwen3.5-plus`

### `alibaba-coding-plan` (3 Models)

Optimized for Alibaba Cloud's free Coding Plan.

| Model | Use For |
|-------|---------|
| MiniMax M2.5 | Coding, chat, default |
| Qwen3.5-Plus | Science, reasoning, large context |
| Kimi K2.5 | Vision, frontend, agent swarms |

### `openrouter-all` (7 Models)

Full OpenRouter model selection.

| Model | Use For | Cost/1M |
|-------|---------|---------|
| GPT-5.3 Codex | Critical coding | $0.75/$3.00 |
| Claude Opus 4.6 | Complex reasoning | $15/$75 |
| Claude Sonnet 4.6 | Balanced tasks | $3/$15 |
| Gemini 3.1 Pro | Vision, video, large context | $0.50/$2.00 |
| MiniMax M2.5 | Fast coding | $0.30/$1.20 |
| Kimi K2.5 | Frontend, agent swarms | $0.45/$2.20 |
| DeepSeek V3.2 | Budget coding | $0.32/$0.89 |

### `enterprise` (4 Models)

Premium production setup.

| Model | Use For |
|-------|---------|
| GPT-5.3 Codex | Default, coding, agentic |
| Claude Opus 4.6 | Architecture, writing, analysis |
| Gemini 3.1 Pro | Vision, video, multimodal |
| Claude Sonnet 4.6 | Simple tasks (cost savings) |

---

## Create Your Own Preset

### Step 1: Copy a Template

```bash
cp presets/minimal.json presets/my-setup.json
```

### Step 2: Edit Models

```json
{
  "name": "My Custom Setup",
  "description": "Personal config",
  "models": {
    "fast": {
      "id": "your-provider/model-id",
      "name": "Friendly Name",
      "provider": "provider-name",
      "context": 100000,
      "strengths": ["coding", "chat"],
      "benchmarks": { "swe-bench": 75 },
      "cost": { "input": 0.50, "output": 1.50 },
      "aliases": ["fast", "default"],
      "enabled": true,
      "default": true
    }
  }
}
```

### Step 3: Edit Routing

```json
{
  "routing": {
    "fallback": "fast",
    "categories": {
      "coding": {
        "model": "fast",
        "priority": 80,
        "keywords": ["code", "fix", "debug", "bug"]
      }
    }
  }
}
```

### Step 4: Load It

```bash
python3 scripts/load-preset.py my-setup
```

---

## Model Benchmarks Reference

Data from [Artificial Analysis](https://artificialanalysis.ai), [Hugging Face](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard), and community testing (Feb 2026).

### Coding (SWE-Bench Verified)

| Model | Score | Provider |
|-------|-------|----------|
| GPT-5.3 Codex | 82.1% | OpenAI |
| Claude Opus 4.6 | 80.9% | Anthropic |
| MiniMax M2.5 | 80.2% | MiniMax |
| Gemini 3.1 Pro | 78.5% | Google |
| Claude Sonnet 4.6 | 77.2% | Anthropic |
| Kimi K2.5 | 76.8% | Moonshot |
| Qwen3.5-Plus | 76.4% | Alibaba |

### Science & Reasoning (GPQA-Diamond)

| Model | Score | Provider |
|-------|-------|----------|
| GPT-5.3 Codex | 91.2% | OpenAI |
| Claude Opus 4.6 | 89.2% | Anthropic |
| Qwen3.5-Plus | 88.4% | Alibaba |
| Gemini 3.1 Pro | 87.9% | Google |
| Kimi K2.5 | 87.6% | Moonshot |

### Vision (MMMU Pro / OCRBench)

| Model | Score | Provider |
|-------|-------|----------|
| Gemini 3.1 Pro | 78.2% (MMMU) | Google |
| Kimi K2.5 | 92.3% (OCRBench) | Moonshot |
| GPT-5.3 Codex | 76.8% (MMMU) | OpenAI |

### Speed (Tokens/Second)

| Model | Speed | Latency |
|-------|-------|---------|
| Llama 3.1 8B | 2600 tok/s | ~0.1s |
| MiniMax M2.5 | ~80 tok/s | ~0.4s |
| Claude Sonnet 4.6 | ~65 tok/s | ~0.6s |
| Qwen3.5-Plus | ~50 tok/s | ~0.8s |
| Kimi K2.5 | ~35 tok/s | ~1.2s |

---

## Configuration Reference

### Category Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Model key to route to |
| `priority` | number | Higher = checked first (100 = highest) |
| `description` | string | Human-readable description |
| `triggers.keywords` | array | Match any keyword (case-insensitive) |
| `triggers.patterns` | array | Regex patterns |
| `triggers.thresholds` | object | minTokens, maxWords, minCodeFences, etc. |

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

## Provider-Specific Setup

### OpenRouter

1. Get API key: https://openrouter.ai/keys
2. Use `openrouter-all` or `minimal` preset
3. Set `OPENROUTER_API_KEY` env var

### Alibaba Cloud

1. Sign up for Coding Plan (free tier)
2. Use `alibaba-coding-plan` preset
3. Configure API key in gateway config

### Ollama (Local)

1. Install: https://ollama.ai
2. Pull models: `ollama pull llama3.1:8b llama3.1:70b`
3. Use `minimal` preset with Ollama model IDs

### LM Studio (Local)

1. Download: https://lmstudio.ai
2. Load models and start local server
3. Use `minimal` preset with `localhost:1234` endpoints

### vLLM (Self-Hosted)

1. Deploy vLLM with your models
2. Use `minimal` preset with vLLM endpoints
3. Configure base URLs in models.json

---

## Debugging

```bash
# Enable debug logging
export OPENCLAW_SMART_ROUTER_DEBUG=1
openclaw gateway restart

# Test a prompt
python3 -m python.classifier "your prompt here"

# List available models
python3 -m python.classifier --list

# List available presets
ls presets/
```

---

## File Structure

```
smart-router/
├── README.md              # This file
├── SKILL.md               # Agent instructions
├── config/
│   ├── models.json        # Active model config
│   └── categories.json    # Active routing rules
├── presets/
│   ├── minimal.json       # 2-model preset
│   ├── alibaba-coding-plan.json
│   ├── openrouter-all.json
│   └── enterprise.json    # Premium preset
├── python/
│   └── classifier.py      # Core Python implementation
├── scripts/
│   └── load-preset.py     # Preset loader script
└── references/
    └── benchmarks.md      # Model benchmark data
```

---

## Requirements

- **OpenClaw** 2026.2+
- **Python** 3.8+ (for Python skill usage)
- **Model provider** configured (any OpenAI-compatible API)

---

## Contributing

### Add a Preset

1. Create `presets/your-preset.json`
2. Include 2-10 models with benchmarks
3. Define routing categories
4. Submit PR with benchmark sources

### Update Benchmarks

Edit `references/benchmarks.md` with:
- Model name and version
- Benchmark scores (SWE-Bench, GPQA, etc.)
- Source URL
- Date tested

---

## License

MIT

---

## Support

- **Issues:** https://github.com/ishsharm0/smart-router/issues
- **Discussions:** https://github.com/ishsharm0/smart-router/discussions
- **Benchmarks:** https://artificialanalysis.ai, https://llm-stats.com
