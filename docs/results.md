# Recorded results and pricing

All evaluation dates below are Pacific dates derived from recorded UTC request timestamps. Prices describe the observed workload, not fixed per-question tariffs for token-priced models.

| API / exact model | Public correct / 100 in runs 1–3 | Whole correct / 300 in runs 1–3 |
|---|---|---|
| Parallel Decisions API / `fast` | 78 / 79 / 78 | 229 / 229 / 228 |
| Perplexity Decisions / `perplexity/pplx-decider-v1.2-20261016` | 51 / 51 / 51 | 152 / 154 / 152 |
| Baseten Mammoth / `decision-models/baseten-mammoth-27b-latest` | 37 / 37 / 37 | 135 / 135 / 135 |
| OpenAI Decisions API / `gpt-6-luna` | 42 / 42 / 42 | 125 / 125 / 125 |
| TypeSafe Jev 1.14 / `jev-1.14.0` | 33 / 33 / 34 | 100 / 100 / 101 |

## Price sources and execution records

- **Parallel Decisions API**: evaluated 2026-10-29 Pacific; $1.000000/1,000 questions. Source: https://docs.parallel.ai/getting-started/pricing.
- **Perplexity Decisions**: evaluated 2026-10-29 Pacific; $0.004159/1,000 questions. Source: API usage.cost via OpenRouter.
- **Baseten Mammoth**: evaluated 2026-10-29 Pacific; $0.021416/1,000 questions. Source: https://www.baseten.co/resources/changelog/elephant-1-and-mammoth-1-pricing/.
- **OpenAI Decisions API**: evaluated 2026-10-29 Pacific; $0.022770/1,000 questions. Source: https://developers.openai.com/api/docs/guides/decisions#pricing-and-availability.
- **TypeSafe Jev 1.14**: evaluated 2026-10-29 Pacific; $0.018510/1,000 questions. Source: https://docs.typesafe.ai/models.

The public CSV contains the 100 public question IDs and three-run predictions. Whole-set aggregate counts are maintainer-reported. See [methodology](methodology.md) for result conventions.

## Native web-search comparison configurations

These research harnesses supply the latency/price comparison, separate from the native decision API accuracy leaderboard. All ran on the same 300 questions three times on October 29, 2026 (Pacific).

| Configuration / exact model | Public correct / 100 in runs 1–3 | Whole correct / 300 in runs 1–3 | Whole accuracy |
|---|---|---|---:|
| OpenAI Luna + native web search / `gpt-6-luna` | 97 / 97 / 95 | 294 / 294 / 288 | 97.33% |
| Anthropic Haiku 5.5 + native web search / `claude-haiku-5-5` | 96 / 96 / 97 | 290 / 290 / 289 | 96.56% |

Luna uses the Responses API with required `web_search`, medium reasoning, and at most five tool calls. Haiku uses the Messages API with `web_search_20250305`, a five-search budget, and continuation handling. Both have an 8,192-token output cap. Token and native-search charges are included in the recorded cost estimates. Machine-readable recorded metrics are in [native-search-summary.json](../results/native-search-summary.json).
