#!/usr/bin/env bash
set -eu
: "${PARALLEL_API_KEY:?Set PARALLEL_API_KEY in your environment}"

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
