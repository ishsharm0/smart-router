# Model Costs & Benchmarks Reference

Last updated: 2026-03-03

## Current Setup: Alibaba Cloud (Coding Plan)

**Pricing:** Flat subscription — 1200 requests per 5hr shared pool. No per-token billing.

| Model | Input | Output | Context | Status |
|-------|-------|--------|---------|--------|
| **MiniMax M2.5** | $0 (included) | $0 (included) | 131K | ✅ Primary |
| **Qwen3.5-Plus** | $0 (included) | $0 (included) | 1M | ✅ Fallback |
| **Kimi K2.5** | $0 (included) | $0 (included) | 256K | ✅ Vision |

**Quota:** 1200 requests / 5hr window across all three models. Shared pool.

---

## Model Benchmarks (2026)

Data from [Artificial Analysis](https://artificialanalysis.ai), [Hugging Face](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard), and community testing.

### Coding (SWE-Bench Verified)

| Model | Score | Notes |
|-------|-------|-------|
| **MiniMax M2.5** | 80.2% | Best open model for coding |
| Claude Opus 4.5 | 80.9% | Proprietary leader |
| Kimi K2.5 | 76.8% | Strong, but verbose |
| Qwen3.5-Plus | 76.4% | Solid all-rounder |

### Science & Reasoning (GPQA-Diamond)

| Model | Score | Notes |
|-------|-------|-------|
| **Qwen3.5-Plus** | 88.4% | Best open model for science |
| GPT-5.2 | 92.4% | Proprietary leader |
| Kimi K2.5 | 87.6% | Close second |
| MiniMax M2.5 | — | Weaker on science |

### Vision & Multimodal

| Model | Score | Notes |
|-------|-------|-------|
| **Kimi K2.5** | 92.3% (OCRBench) | Best open vision model |
| Kimi K2.5 | 90.1% (MathVista) | Strong visual reasoning |
| Kimi K2.5 | 78.4% (BrowseComp) | With Agent Swarm |

### Intelligence Index (Artificial Analysis)

| Model | Index | Hallucination Rate |
|-------|-------|-------------------|
| Kimi K2.5 | ~85 | -11 (higher hallucination) |
| Qwen3.5-Plus | ~82 | +5 (balanced) |
| MiniMax M2.5 | ~80 | +8 (low hallucination) |

### Speed (Output Tokens/Second)

| Model | Speed | Latency |
|-------|-------|---------|
| **MiniMax M2.5** | ~80 tok/s | ~0.4s TTFT |
| Qwen3.5-Plus | ~50 tok/s | ~0.8s TTFT |
| Kimi K2.5 | ~35 tok/s | ~1.2s TTFT |

---

## Routing Recommendations

Based on benchmarks and speed:

| Task Type | Route To | Why |
|-----------|----------|-----|
| Chat, pings, quick tasks | MiniMax | Fastest, lowest latency |
| Coding, debugging, refactor | MiniMax | Best SWE-Bench (80.2%) |
| Science, math, "explain" | Qwen3.5+ | Best GPQA (88.4%) |
| Images, PDFs, diagrams | Kimi | Best vision (92.3% OCRBench) |
| Frontend, UI, CSS | Kimi | Strong visual-to-code |
| Large context (>100K tokens) | Qwen3.5+ | 1M context window |
| Agent swarms, parallel tasks | Kimi | Agent Swarm framework |

---

## Historical: OpenRouter Pricing (Reference Only)

⚠️ **Not current** — for reference if switching providers.

| Model | Input/1M | Output/1M | Context |
|-------|----------|-----------|---------|
| MiniMax M2.5 | $0.10-0.30 | $1.20-1.40 | 196K |
| Kimi K2.5 | $0.15-0.45 | $2.20-3.00 | 262K |
| DeepSeek V3 | $0.04-0.37 | $0.16-1.06 | 164K |

⚠️ DeepSeek listed at $0.04/$0.16 is **direct API only**. OpenRouter charges $0.32/$0.89.

---

## Optimization Notes

1. **MiniMax as default** — Fastest inference, best coding, low hallucination
2. **Qwen for reasoning** — Use when accuracy > speed (science, math, complex architecture)
3. **Kimi for vision** — Only use when image/PDF input required (slower, higher hallucination)
4. **Avoid DeepSeek on OpenRouter** — 3-4x markup vs direct API

---

## Sources

- [Artificial Analysis Model Comparisons](https://artificialanalysis.ai/models/comparisons)
- [Kimi K2.5: Still Worth It After Two Weeks?](https://huggingface.co/blog/mlabonne/kimik25)
- [r/LocalLLaMA SWE-Bench Discussion](https://reddit.com/r/LocalLLaMA)
- [Moonshot AI Kimi K2.5 Tech Report](https://arxiv.org/abs/2602.02276)
