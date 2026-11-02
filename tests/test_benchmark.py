import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

from pws_decisions.__main__ import build_request, call_parallel, load_questions, parse_answer, read_jsonl, score

ROOT = Path(__file__).resolve().parents[1]


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = load_questions(ROOT / "data/public-100.jsonl")
        cls.answers = read_jsonl(ROOT / "data/public-100-answers.jsonl")

    def test_exact_public_size_and_manifest(self):
        self.assertEqual(len(self.questions), 100)
        manifest = json.loads((ROOT / "data/manifest.json").read_text())
        for file, key in [("public-100.jsonl", "questions_sha256"), ("public-100-answers.jsonl", "answers_sha256")]:
            self.assertEqual(hashlib.sha256((ROOT / "data" / file).read_bytes()).hexdigest(), manifest[key])

    def test_perfect_and_missing_predictions(self):
        predictions = [{"id": a["id"], "prediction": a["answer"], "status": "success"} for a in self.answers]
        self.assertEqual(score(self.questions, self.answers, predictions)["accuracy_percent"], 100)
        self.assertEqual(score(self.questions, self.answers, predictions[:-1])["accuracy_percent"], 99)
        self.assertAlmostEqual(score(self.questions, self.answers, [])["uniform_random_accuracy_percent"], 44.6666666667)

    def test_failure_cannot_be_correct_even_with_matching_label(self):
        a = self.answers[0]
        for status in ["refusal", "error", "invalid_response"]:
            result = score(self.questions, self.answers, [{"id": a["id"], "prediction": a["answer"], "status": status}])
            self.assertEqual(result["correct"], 0)

    def test_duplicate_unknown_and_partial_gold_rejected(self):
        p = {"id": self.answers[0]["id"], "prediction": self.answers[0]["answer"], "status": "success"}
        with self.assertRaises(ValueError):
            score(self.questions, self.answers, [p, p])
        with self.assertRaises(ValueError):
            score(self.questions, self.answers, [{**p, "id": "unknown"}])
        with self.assertRaises(ValueError):
            score(self.questions, self.answers[:-1], [])

    def test_request_allowlist_excludes_answers(self):
        q = {**self.questions[0], "answer": "DO_NOT_SEND", "gold": "DO_NOT_SEND", "internal_metadata": "DO_NOT_SEND"}
        req = build_request(q)
        self.assertEqual(set(req), {"state", "questions"})
        self.assertNotIn("DO_NOT_SEND", json.dumps(req))
        self.assertEqual(req["questions"]["answer"]["criteria"], {c["value"]: c["description"] for c in q["choices"]})

    def test_refusal_and_invalid_response(self):
        q = self.questions[0]
        self.assertEqual(parse_answer({"answers": {"answer": {"type": "refusal"}}}, q)["status"], "refusal")
        with self.assertRaises(ValueError):
            parse_answer({"answers": {"answer": {"type": "choice", "choice": "not-a-choice"}}}, q)

    def test_transport_contract_and_secret_not_logged(self):
        q = self.questions[0]
        payload = {"answers": {"answer": {"type": "choice", "choice": q["choices"][0]["value"]}}}
        with patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(payload).encode())) as call:
            call.return_value.status = 200
            result = call_parallel(q, "SECRET_FOR_TEST_ONLY")
            request = call.call_args.args[0]
            self.assertEqual(request.full_url, "https://api.parallel.ai/v1/decisions")
            self.assertEqual(request.get_header("X-api-key"), "SECRET_FOR_TEST_ONLY")
            self.assertEqual(json.loads(request.data), build_request(q))
            self.assertEqual(result["status"], "success")
            self.assertNotIn("SECRET_FOR_TEST_ONLY", json.dumps(result))

    def test_http_error_is_retained_without_retry(self):
        error = urllib.error.HTTPError("https://api.parallel.ai/v1/decisions", 504, "timeout", {}, None)
        with patch("urllib.request.urlopen", side_effect=error) as call:
            result = call_parallel(self.questions[0], "SECRET_FOR_TEST_ONLY")
        self.assertEqual(call.call_count, 1)
        self.assertEqual(result["http_status"], 504)
        self.assertEqual(result["status"], "error")
        self.assertIsNone(result["prediction"])

    def test_public_results_reproduce_each_provider_run(self):
        with (ROOT / "results/public-per-question.csv").open(newline="") as f:
            records = list(csv.DictReader(f))
        self.assertEqual(len(records), 1500)
        self.assertTrue(all(r["id"] in {q["id"] for q in self.questions} for r in records))
        summary = json.loads((ROOT / "results/baseline-summary.json").read_text())
        for provider in summary["results"]:
            for run, expected in enumerate(provider["public"]["correct_counts"], 1):
                rows = [r for r in records if r["provider"] == provider["provider"] and int(r["run"]) == run]
                self.assertEqual(len(rows), 100)
                predictions = [{"id": r["id"], "prediction": r["prediction"] or None, "status": r["status"]} for r in rows]
                self.assertEqual(score(self.questions, self.answers, predictions)["correct"], expected)


if __name__ == "__main__":
    unittest.main()
