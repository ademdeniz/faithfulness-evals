"""Convert Promptfoo JSON output to the shared evaluation result schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def normalize_promptfoo(payload: dict[str, Any]) -> dict[str, Any]:
    raw_results = payload.get("results", payload)
    if isinstance(raw_results, dict):
        raw_results = raw_results.get("results", [])
    if not isinstance(raw_results, list) or not raw_results:
        raise ValueError("Promptfoo output does not contain evaluation results.")

    cases = []
    latencies = []
    input_tokens = output_tokens = 0
    models = set()
    for index, item in enumerate(raw_results, start=1):
        grading = item.get("gradingResult", {})
        test_case = item.get("testCase", {})
        case_id = (
            test_case.get("description")
            or item.get("description")
            or f"case-{index}"
        )
        provider = item.get("provider")
        if provider:
            models.add(provider if isinstance(provider, str) else provider.get("id", ""))
        if item.get("latencyMs") is not None:
            latencies.append(item["latencyMs"])
        usage = item.get("tokenUsage", {})
        input_tokens += usage.get("prompt", usage.get("input", 0)) or 0
        output_tokens += usage.get("completion", usage.get("output", 0)) or 0
        cases.append(
            {
                "case_id": case_id,
                "score": grading.get("score"),
                "passed": grading.get("pass"),
                "reason": grading.get("reason"),
                "claims": [],
            }
        )

    return {
        "framework": "promptfoo",
        "metric": "faithfulness",
        "cases": cases,
        "model": sorted(models)[0] if models else None,
        "latency_ms": sum(latencies) if latencies else None,
        "input_tokens": input_tokens or None,
        "output_tokens": output_tokens or None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    normalized = normalize_promptfoo(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
