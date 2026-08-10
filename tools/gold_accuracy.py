"""Compute offline accuracy metrics for a gold-labeled verdict dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def join_predictions(
    gold_cases: list[dict[str, Any]],
    evaluation_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Join normalized framework cases to gold verdicts by case_id."""
    predictions = {
        case["case_id"]: case["passed"]
        for result in evaluation_results
        for case in result["cases"]
        if case["passed"] is not None
    }
    missing = [
        case["case_id"] for case in gold_cases if case["case_id"] not in predictions
    ]
    if missing:
        raise ValueError(f"Missing predictions for gold cases: {', '.join(missing)}")
    return [
        {
            "case_id": case["case_id"],
            "expected_pass": case["expected_pass"],
            "predicted_pass": predictions[case["case_id"]],
        }
        for case in gold_cases
    ]


def calculate_metrics(cases: list[dict[str, Any]]) -> dict[str, Any]:
    if not cases:
        raise ValueError("Gold dataset must contain at least one case.")

    true_positive = sum(
        case["expected_pass"] and case["predicted_pass"] for case in cases
    )
    true_negative = sum(
        not case["expected_pass"] and not case["predicted_pass"] for case in cases
    )
    false_positive = sum(
        not case["expected_pass"] and case["predicted_pass"] for case in cases
    )
    false_negative = sum(
        case["expected_pass"] and not case["predicted_pass"] for case in cases
    )
    total = len(cases)

    return {
        "total": total,
        "correct": true_positive + true_negative,
        "accuracy": (true_positive + true_negative) / total,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "predictions",
        type=Path,
        nargs="?",
        help="Legacy path to cases containing expected_pass and predicted_pass.",
    )
    parser.add_argument("--gold", type=Path, help="Gold cases with expected_pass.")
    parser.add_argument("--min-accuracy", type=float, default=None)
    parser.add_argument(
        "--results",
        type=Path,
        help="Normalized result file emitted by tools/run_evals.py.",
    )
    args = parser.parse_args()
    if args.gold and args.results:
        gold_cases = json.loads(args.gold.read_text(encoding="utf-8"))
        results = json.loads(args.results.read_text(encoding="utf-8"))
        cases = join_predictions(gold_cases, results)
    elif args.predictions:
        cases = json.loads(args.predictions.read_text(encoding="utf-8"))
    else:
        parser.error("provide predictions, or both --gold and --results")
    metrics = calculate_metrics(cases)
    print(json.dumps(metrics, indent=2))
    if args.min_accuracy is not None and metrics["accuracy"] < args.min_accuracy:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
