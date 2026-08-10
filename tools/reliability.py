"""Analyze repeated evaluation runs for judge reliability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


def analyze_reliability(runs: list[dict[str, Any]]) -> dict[str, Any]:
    if not runs:
        raise ValueError("At least one run is required.")
    by_case: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        for case in run["cases"]:
            by_case.setdefault(case["case_id"], []).append(case)

    case_reports = []
    for case_id, cases in sorted(by_case.items()):
        verdicts = [case["passed"] for case in cases if case["passed"] is not None]
        scores = [case["score"] for case in cases if case["score"] is not None]
        case_reports.append(
            {
                "case_id": case_id,
                "verdict_agreement": len(set(verdicts)) <= 1,
                "verdicts": verdicts,
                "score_mean": mean(scores) if scores else None,
                "score_stddev": pstdev(scores) if len(scores) > 1 else 0.0 if scores else None,
            }
        )

    return {
        "run_count": len(runs),
        "case_count": len(case_reports),
        "verdict_agreement_rate": (
            sum(case["verdict_agreement"] for case in case_reports)
            / len(case_reports)
            if case_reports
            else 0.0
        ),
        "verdict_flip_count": sum(
            not case["verdict_agreement"] for case in case_reports
        ),
        "cases": case_reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", type=Path)
    args = parser.parse_args()
    report = analyze_reliability(json.loads(args.runs.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
