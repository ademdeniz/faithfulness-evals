"""Compare evaluation metrics against a checked-in regression baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def compare_baseline(
    baseline: dict[str, Any],
    current: dict[str, Any],
    *,
    max_accuracy_drop: float = 0.05,
    max_latency_increase_ratio: float = 0.25,
    max_cost_increase_ratio: float = 0.25,
) -> dict[str, Any]:
    checks = []
    accuracy_delta = current["accuracy"] - baseline["accuracy"]
    checks.append(
        {
            "metric": "accuracy",
            "baseline": baseline["accuracy"],
            "current": current["accuracy"],
            "delta": accuracy_delta,
            "passed": accuracy_delta >= -max_accuracy_drop,
        }
    )
    for metric, limit in (
        ("latency_ms", max_latency_increase_ratio),
        ("estimated_cost_usd", max_cost_increase_ratio),
    ):
        old = baseline.get(metric)
        new = current.get(metric)
        passed = True if old in (None, 0) else new <= old * (1 + limit)
        checks.append(
            {
                "metric": metric,
                "baseline": old,
                "current": new,
                "ratio_limit": limit,
                "passed": passed,
            }
        )
    return {"passed": all(check["passed"] for check in checks), "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    args = parser.parse_args()
    report = compare_baseline(
        json.loads(args.baseline.read_text()),
        json.loads(args.current.read_text()),
    )
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
