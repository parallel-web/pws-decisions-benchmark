# Using PWS-Decisions

Read README.md and docs/methodology.md before reporting scores.

- Validate offline: `python -m pws_decisions evaluate --dry-run` and `python -m unittest discover -s tests`.
- Run a billable evaluation only when the user authorizes it. Read PARALLEL_API_KEY from the environment; never print or write it.
- Keep the exact question state, instructions, choice values, and descriptions. Never send the answer key as candidate input.
- Use a fresh output path for each run. Include failures and refusals in the denominator. Do not discard hard questions or replace failed attempts silently.
- To score another provider, produce the documented JSONL prediction format and use the same scorer.
- Report model/endpoint, dataset checksum, evaluation date, run count, retry policy, sample size, accuracy, and latency definition.
- Public and whole-set numbers are distinct. The whole set includes public questions and is maintainer-reported until its private portion is released.
- Never infer training-data memorization from a score gap alone. See docs/versioning.md.
- Do not change labels or datasets to improve a provider's score. Proposed corrections need evidence, review, and a new dataset version.
