# Dataset card

- **Name:** PWS-Decisions Benchmark
- **Version:** 0.1.0-rc1
- **Task:** exact multiple-choice decisions requiring externally verifiable public facts
- **Public size:** 100 questions, with a separate answer key
- **Whole size:** 300 questions, including the public 100
- **Language:** English
- **Reference scope:** the date, version, and other constraints written in each question
- **Label source:** model-assisted research, reviewed by the benchmark owner
- **License:** [evaluation-only, no redistribution](../DATA_LICENSE); runner and examples separately MIT

The question JSONL contains only `id`, `state`, `instructions`, and `choices`. The answer-key JSONL contains only `id` and `answer`. IDs are stable within this candidate. Original internal IDs, traffic metadata, private-set questions, raw API responses, and internal research paths are excluded.

State describes caller requirements rather than a reference-evidence packet. Choice values must remain exact; rewriting a question, shuffling its choices, changing a date, or editing a reference label creates a different evaluation contract. Recompute affected results and increment the dataset version when changing contracts.

The dataset is purposive. Reference evidence may become stale, historical pages may change, and model consensus may share systematic errors. See [methodology](methodology.md) for evaluation conventions.

The whole-set uniform-random baseline is 42.4222%, calculated from 206 two-choice, 11 three-choice, 80 four-choice, and 3 five-choice questions. The public baseline is 44.6667%. Random accuracy is the mean of `1 / number_of_choices`, not the majority-label accuracy.
