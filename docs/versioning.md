# Dataset versions and reproducibility

## Identify the evaluated version

Report the dataset version alongside each benchmark result. The dataset's `data/manifest.json` records the version, question counts, SHA-256 checksums of the public questions and answer key, and a checksum commitment to the full 300-question set.

Use the checksums to verify that evaluations use the same inputs and reference answers. Preserve each question's wording, choices, and date or version constraints: a question about a historical fact should be answered for its stated date.

## Corrections and updates

Changes to questions, answer choices, reference labels, or set membership require a new dataset version and a description of the changes. Recompute affected scores and retain the previous version's results so readers can distinguish dataset corrections from changes in API performance.

Report the API or model configuration, evaluation date, and number of runs with each result. Compare results on the same dataset version and configuration whenever possible.

## Public and whole-set results

The public set contains 100 questions. The whole set contains those same 100 questions plus 200 private questions. With equal weight per question:

```text
whole_accuracy = (public_accuracy + 2 × private_accuracy) / 3
```

Whole-set accuracy therefore overlaps with public-set accuracy. Use the separate private-only score when comparing performance on public and private questions.

## Interpreting changes over time

Published questions and answers may become available through training data or web search. When possible, record whether an evaluation retrieves benchmark pages or answer keys, and distinguish retrieval of published answers from memorization.

A public/private score gap alone does not establish overfitting. Changes in models, prompts, retrieval coverage, question difficulty, and sampling can also affect results. Compare individual predictions under consistent conditions and use fresh, independently selected questions to investigate generalization.

## Future releases

If the remaining 200 questions are released, the complete dataset can be checked against the existing whole-set checksum commitment using the encoding specified in the manifest. That release would make all 300 questions public. Future evaluations of unseen questions should use a separately collected set.
