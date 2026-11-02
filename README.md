# PWS-Decisions Benchmark

**A web-grounded decision API benchmark for agents.**

PWS-Decisions tests whether a decision API can select the correct answer when a workflow depends on specific, dated facts about the public web. It includes 100 public multiple-choice questions, deterministic scoring, and a minimal Parallel Decisions API runner. No LLM judge is required because ground-truth is provided. Question files and reference answers are available through signed-in Hugging Face access; they are not included in this GitHub repository.

## Decision model leaderboard

Mean accuracy ± sample standard deviation across three runs, in percentage points. Sorted by whole-set accuracy. The whole set contains the public 100 plus 200 private questions.

| Decision API | Public Set Accuracy (100) | Whole Set Accuracy (300) |
|---|---:|---:|
| **Parallel Decisions API** | **78.33% ± 0.58** | **76.22% ± 0.19** |
| Perplexity Decisions | 51.00% ± 0.00 | 50.89% ± 0.38 |
| Baseten Mammoth | 37.00% ± 0.00 | 45.00% ± 0.00 |
| OpenAI Decisions API | 42.00% ± 0.00 | 41.67% ± 0.00 |
| TypeSafe Jev 1.14 | 33.33% ± 0.58 | 33.44% ± 0.19 |

Uniform random guessing: **44.67% public / 42.42% whole**. See [methodology](docs/methodology.md).

Parallel has the highest accuracy among these tested decision API configurations: **76.22% accuracy**.

## Web-grounded latency and price comparison

Whole set, three runs; complete-answer latency and estimated cost including native search.

| Configuration | Evaluation date (Pacific) | p50 / p95 latency | USD / 1,000 questions |
|---|---|---:|---:|
| **Parallel Decisions API** | **2026-10-29** | **0.56 / 0.71 s** | **$1.00** |
| OpenAI Luna + native web search | 2026-10-29 | 7.42 / 19.17 s | $16.52 |
| Anthropic Haiku 5.5 + native web search | 2026-10-29 | 6.38 / 10.95 s | $27.43–$28.79 |

See [recorded results](docs/results.md) for exact configurations and corresponding accuracy.

## Quickstart: evaluate Parallel Decisions API

Set `PARALLEL_API_KEY` in your environment, then try the canonical request from the [Parallel launch quickstart](https://parallel.ai/blog/decisions-api#get-started). See the [API quickstart documentation](https://docs.parallel.ai/decisions/decisions-quickstart) for more examples.

```bash
curl https://api.parallel.ai/v1/decisions \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "state": {
      "page": "https://parallel.ai/blog/decisions-api",
      "note": "Thinking fast, but checking first."
    },
    "questions": {
      "is_this_real": {
        "type": "noul",
        "instructions": "Has Parallel announced a Decisions API?"
      },
      "has_anyone_noticed": {
        "type": "noul",
        "instructions": "Has this blog post been submitted to Hacker News?"
      }
    }
  }'
```

The same command is available locally in [examples/parallel_quickstart.sh](examples/parallel_quickstart.sh).

### Run the public benchmark

Python 3.10+; the benchmark runner has no third-party dependencies. First sign in to Hugging Face and accept the dataset access form. Access is granted immediately; Parallel receives your account username and email. Download the questions and reference answers from [PWS-Decisions on Hugging Face](https://huggingface.co/datasets/parallel-web/pws-decisions-benchmark).

After accepting the access form, install the Hugging Face CLI and download the gated files from the actual dataset repository into this directory:

```bash
pip install huggingface_hub
hf auth login
hf download parallel-web/pws-decisions-benchmark --repo-type dataset --include 'data/*' 'results/public-per-question.csv' --local-dir .
```

Then run:

```bash
# Validate the dataset and inspect the request without making API calls.
python -m pws_decisions evaluate --dry-run

# Set PARALLEL_API_KEY securely in your environment, then run the 100 questions.
python -m pws_decisions evaluate --output runs/parallel-run-1.jsonl

# Score an existing prediction file locally.
python -m pws_decisions score --predictions runs/parallel-run-1.jsonl

# Run offline validation tests.
python -m unittest discover -s tests
```

Inspect a benchmark request with [examples/parallel_request.py](examples/parallel_request.py).

## Benchmark other decision APIs

Return one JSONL record per public question using its stable ID:

```json
{"id":"PWS-D-001","prediction":"<choice_value>","status":"success"}
```

Valid statuses are `success`, `refusal`, `error`, and `invalid_response`. A refusal or failure is incorrect; missing predictions remain in the denominator. Duplicate and unknown IDs are rejected. Use exact choice values, not descriptions. Run the same `score` command against your file. Provider-specific adapters may translate the envelope but must preserve state, instructions, and choices.

## How we built the benchmark

Based on Parallel's Decision API topics of interest and search traffic, we generated a representative set of synthetic questions that is aligned with customer demand. Reference answers were researched separately from candidate responses. This makes PWS-Decisions a development challenge set.

Question dates and version constraints are part of the task. A present-day fact must not replace a historical reference answer. Detailed provenance and limitations are in the [dataset card](docs/dataset-card.md).

## Related decision model benchmarks and leaderboards

PWS-Decisions complements Jev benchmarks and other decision model leaderboards with questions that require externally grounded web facts.

- [JevBench by Benchmark Heaven](https://github.com/fstandhartinger/jevbench) evaluates typed decision accuracy, calibration, latency, and cost.
- [JevBench by LeanMCP](https://leanmcp.github.io/jevbench/) provides an open evaluation framework for typed decision models.
- [Artificial Analysis Decision Index](https://artificialanalysis.ai/methodology/decision-index) combines **AA-Omniscience-Decision**, **HLE-MultiChoice (Humanity’s Last Exam)**, **When2Call**, and **WildGuardTest** to evaluate knowledge, reasoning, tool calling, and classification.

Use these alongside PWS-Decisions when comparing decision APIs for agent workflows.

## Reproducibility and future releases

The 100 release questions, answer key, and per-question predictions are distributed through gated Hugging Face access. GitHub contains the runner, aggregate statistics, and configuration. The dataset manifest commits to the current whole-set content without exposing its 200 private questions. See [versioning and contamination](docs/versioning.md) before interpreting changes in public versus whole-set accuracy.

## Files

- `data/public-100.jsonl`: gated download of candidate inputs, without answers.
- `data/public-100-answers.jsonl`: gated download of reference labels for local scoring.
- `results/baseline-summary.json`: full/public counts, variability, latency, dates, and prices.
- `results/public-per-question.csv`: gated download of three-run predictions.
- `AGENTS.md`: concise instructions for agents running this benchmark.

## Citation and licenses

Use `CITATION.cff` when citing a released version. The runner and examples are licensed under [MIT](LICENSE). The questions, reference answers, and per-question baseline predictions use separate [evaluation-only, no-redistribution terms](DATA_LICENSE). You may publish aggregate results and submit question inputs to APIs being evaluated; do not redistribute dataset files or question content. Other users should obtain their own signed-in Hugging Face access.
