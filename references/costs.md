# Model Costs Reference (OpenRouter)

## Pricing (per 1M input/output tokens)

| Model | Input ($) | Output ($) | Context |
|-------|-----------|------------|---------|
| **MiniMax-M2.5** | $0.15 | $0.15 | 28K |
| **Kimi K2.5** | $0.30 | $1.50 | 128K |

## Cost Savings Example

| Task Type | Tokens | MiniMax Cost | Kimi Cost | Savings |
|-----------|--------|--------------|------------|---------|
| Simple query | 500 | $0.000075 | $0.000375 | 80% |
| Code edit | 2,000 | $0.0003 | $0.0015 | 80% |
| Complex reasoning | 10,000 | $0.0015 | $0.0075 | 80% |

## Quality Guidelines

- **MiniMax-M2.5**: Excellent for coding, tool-use, simple reasoning, fast responses
- **Kimi K2.5**: Best for complex reasoning, large context windows, multi-file analysis

## Latency

- MiniMax: ~500ms typical
- Kimi: ~800ms typical (longer context)
