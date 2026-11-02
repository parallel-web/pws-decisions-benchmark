import argparse
import concurrent.futures
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import time
import urllib.error
import urllib.request

ENDPOINT = "https://api.parallel.ai/v1/decisions"
ROOT = Path(__file__).resolve().parent.parent


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load_questions(path):
    rows = read_jsonl(path)
    seen = set()
    for row in rows:
        if set(row) != {"id", "state", "instructions", "choices"}:
            raise ValueError("Question fields must be exactly id, state, instructions, choices")
        if not isinstance(row["id"], str) or not row["id"] or row["id"] in seen:
            raise ValueError("Question IDs must be unique nonempty strings")
        seen.add(row["id"])
        if not isinstance(row["instructions"], str) or not row["instructions"].strip():
            raise ValueError("Instructions must be nonempty")
        choices = row["choices"]
        if not isinstance(choices, list) or not 2 <= len(choices) <= 255:
            raise ValueError("A question must have 2–255 choices")
        if any(set(c) != {"value", "description"} or not all(isinstance(v, str) and v for v in c.values()) for c in choices):
            raise ValueError("Each choice needs nonempty value and description strings")
        if len({c["value"] for c in choices}) != len(choices):
            raise ValueError("Choice values must be unique")
    if not rows:
        raise ValueError("Empty dataset")
    return rows


def build_request(question):
    return {"state": question["state"], "questions": {"answer": {
        "type": "choice", "instructions": question["instructions"],
        "criteria": {c["value"]: c["description"] for c in question["choices"]},
    }}}


def parse_answer(response, question):
    answer = response["answers"]["answer"]
    if answer.get("type") == "refusal":
        return {"prediction": None, "status": "refusal"}
    if answer.get("type") != "choice" or answer.get("choice") not in {c["value"] for c in question["choices"]}:
        raise ValueError("Response did not contain a valid choice")
    return {"prediction": answer["choice"], "status": "success"}


def score(questions, answers, predictions):
    expected = {q["id"]: q for q in questions}
    gold = {}
    for row in answers:
        if row["id"] in gold or row["id"] not in expected:
            raise ValueError("Duplicate or unknown answer ID")
        if row["answer"] not in {c["value"] for c in expected[row["id"]]["choices"]}:
            raise ValueError("Reference answer is not a valid choice")
        gold[row["id"]] = row["answer"]
    if set(gold) != set(expected):
        raise ValueError("Reference answer coverage must match the dataset")
    found = {}
    for row in predictions:
        if row["id"] not in expected or row["id"] in found:
            raise ValueError("Duplicate or unknown prediction ID")
        if row.get("status") not in {"success", "refusal", "error", "invalid_response"}:
            raise ValueError("Prediction needs an explicit valid status")
        found[row["id"]] = row
    correct = sum(found.get(k, {}).get("status") == "success" and found[k].get("prediction") == v for k, v in gold.items())
    return {"n": len(expected), "correct": correct, "accuracy_percent": 100 * correct / len(expected),
            "missing": len(expected) - len(found),
            "non_success": sum(r["status"] != "success" for r in found.values()),
            "uniform_random_accuracy_percent": 100 * statistics.mean(1 / len(q["choices"]) for q in questions)}


def call_parallel(question, api_key):
    started = time.perf_counter()
    result = {"id": question["id"], "prediction": None, "status": "error", "attempts": 1,
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    request = urllib.request.Request(ENDPOINT, data=json.dumps(build_request(question)).encode(),
                                    headers={"x-api-key": api_key, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result["http_status"] = response.status
            payload = json.load(response)
        result.update(parse_answer(payload, question))
    except urllib.error.HTTPError as exc:
        result["http_status"] = exc.code
        result["error_type"] = "http_error"
    except (KeyError, TypeError, ValueError) as exc:
        result["status"] = "invalid_response"
        result["error_type"] = type(exc).__name__
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        result["error_type"] = type(exc).__name__
    result["latency_ms"] = (time.perf_counter() - started) * 1000
    return result


def main():
    parser = argparse.ArgumentParser(description="Run and score PWS-Decisions without an LLM judge.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ["evaluate", "score"]:
        cmd = commands.add_parser(name)
        cmd.add_argument("--dataset", type=Path, default=ROOT / "data/public-100.jsonl")
        cmd.add_argument("--answers", type=Path, default=ROOT / "data/public-100-answers.jsonl")
        if name == "evaluate":
            cmd.add_argument("--output", type=Path, default=ROOT / "runs/parallel.jsonl")
            cmd.add_argument("--workers", type=int, default=4)
            cmd.add_argument("--dry-run", action="store_true")
        else:
            cmd.add_argument("--predictions", type=Path, required=True)
    args = parser.parse_args()
    questions = load_questions(args.dataset)
    if args.command == "score":
        print(json.dumps(score(questions, read_jsonl(args.answers), read_jsonl(args.predictions)), indent=2))
        return
    if args.dry_run:
        print(json.dumps({"questions": len(questions), "endpoint": ENDPOINT, "sample_request": build_request(questions[0])}, indent=2))
        return
    if not 1 <= args.workers <= 12:
        parser.error("--workers must be between 1 and 12")
    key = os.environ.get("PARALLEL_API_KEY")
    if not key:
        parser.error("Set PARALLEL_API_KEY in your environment")
    metadata_path = args.output.with_suffix(".metadata.json")
    if args.output.exists() or metadata_path.exists():
        parser.error("Output already exists; choose a fresh path for each run")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    records = []
    with args.output.open("x", encoding="utf-8") as output:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(call_parallel, q, key) for q in questions]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                records.append(result)
                output.write(json.dumps(result, ensure_ascii=False) + "\n")
                output.flush()
    metadata = {"endpoint": ENDPOINT, "workers": args.workers, "attempts_per_question": 1,
                "dataset_sha256": hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
                "latency_definition": "Complete response time; excludes executor queue; no automatic retries",
                "summary": score(questions, read_jsonl(args.answers), records)}
    with metadata_path.open("x", encoding="utf-8") as output:
        output.write(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata["summary"], indent=2))


if __name__ == "__main__":
    main()
