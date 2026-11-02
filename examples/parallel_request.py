"""Print one exact request without an API key, network call, or answer key."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with (root / "data/public-100.jsonl").open(encoding="utf-8") as stream:
    question = json.loads(next(stream))
request = {
    "state": question["state"],
    "questions": {
        "answer": {
            "type": "choice",
            "instructions": question["instructions"],
            "criteria": {choice["value"]: choice["description"] for choice in question["choices"]},
        }
    },
}
print(json.dumps(request, indent=2))
