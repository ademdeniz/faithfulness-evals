"""Offline retrieval relevance and answer correctness metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def retrieval_metrics(case: dict[str, Any]) -> dict[str, float]:
    retrieved = set(case["retrieved_context_ids"])
    relevant = set(case["relevant_context_ids"])
    if not relevant:
        raise ValueError(f"{case['case_id']}: relevant context cannot be empty.")

    true_positive = len(retrieved & relevant)
    precision = true_positive / len(retrieved) if retrieved else 0.0
    recall = true_positive / len(relevant)
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {"precision": precision, "recall": recall, "f1": f1}


def evaluate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    if not cases:
        raise ValueError("Metric dataset must contain at least one case.")

    retrieval = [retrieval_metrics(case) for case in cases]
    correct = sum(bool(case["answer_correct"]) for case in cases)
    return {
        "total": len(cases),
        "retrieval": {
            "precision": sum(item["precision"] for item in retrieval) / len(retrieval),
            "recall": sum(item["recall"] for item in retrieval) / len(retrieval),
            "f1": sum(item["f1"] for item in retrieval) / len(retrieval),
        },
        "answer_correctness": correct / len(cases),
        "answer_correct": correct,
        "answer_incorrect": len(cases) - correct,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()
    cases = json.loads(args.dataset.read_text(encoding="utf-8"))
    print(json.dumps(evaluate_cases(cases), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
