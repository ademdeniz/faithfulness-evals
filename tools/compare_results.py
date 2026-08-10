"""Compare normalized results from multiple evaluation frameworks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def compare_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    if len(results) < 2:
        raise ValueError("At least two framework results are required.")

    by_case: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        for case in result["cases"]:
            by_case.setdefault(case["case_id"], []).append(
                {
                    "framework": result["framework"],
                    "score": case["score"],
                    "passed": case["passed"],
                }
            )

    cases = []
    for case_id, evaluations in sorted(by_case.items()):
        verdicts = {item["passed"] for item in evaluations}
        scores = [
            item["score"] for item in evaluations if item["score"] is not None
        ]
        cases.append(
            {
                "case_id": case_id,
                "evaluations": evaluations,
                "agreement": len(verdicts) <= 1,
                "score_spread": max(scores) - min(scores) if scores else None,
            }
        )

    disagreements = sum(not case["agreement"] for case in cases)
    return {
        "frameworks": [result["framework"] for result in results],
        "case_count": len(cases),
        "agreement_count": len(cases) - disagreements,
        "disagreement_count": disagreements,
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    results = json.loads(args.results.read_text(encoding="utf-8"))
    print(json.dumps(compare_results(results), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
