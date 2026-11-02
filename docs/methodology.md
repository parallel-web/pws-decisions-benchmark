# Methodology

## Task and scoring

Each question provides JSON state, a question with an explicit date or version scope, and 2–5 mutually exclusive choice values. A correct prediction exactly matches the reference choice value. Every question has equal weight. Refusals, invalid responses, transport failures, and missing predictions count as incorrect. Unknown or duplicate IDs are rejected. No LLM judge is involved in scoring.

The table reports the mean of three run accuracies and their sample standard deviation (percentage points). Approximate 95% t intervals use two degrees of freedom; they measure repeatability on this fixed set, not generalization or reference-label uncertainty. Zero observed variation does not imply zero future uncertainty.

## Construction and selection

The 300 questions describe synthetic operational decisions about public-web facts. Reference answers were researched separately from candidate responses.

Questions were chosen for their difficulty and alignment with customer outcomes. The resulting challenge set contains 100 public and 200 private questions.

## Endpoint configurations

Parallel uses `POST https://api.parallel.ai/v1/decisions`, authenticated with `x-api-key`, in default `fast` mode. The request uses `state` and a named `questions.answer` object with `type: choice`, `instructions`, and `criteria`. The example does not send a model parameter, reference answer, or source-research artifact. A response may be a typed refusal, which scores incorrect.

Other rows use their native decision endpoints with the same state, instructions, and choices, without supplied web context. Perplexity is accessed through OpenRouter. Exact model IDs and endpoints appear in `results/run-config.json`. This is a comparison of end-to-end API configurations.
