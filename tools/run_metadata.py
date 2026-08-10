"""Utilities for aggregating evaluation execution metadata."""

from __future__ import annotations

from typing import Any


def summarize_metadata(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        raise ValueError("At least one evaluation result is required.")

    timed = [result["latency_ms"] for result in results if result.get("latency_ms") is not None]
    costs = [
        result["estimated_cost_usd"]
        for result in results
        if result.get("estimated_cost_usd") is not None
    ]
    return {
        "framework_count": len(results),
        "models": sorted({result["model"] for result in results if result.get("model")}),
        "total_latency_ms": sum(timed),
        "average_latency_ms": sum(timed) / len(timed) if timed else None,
        "total_estimated_cost_usd": sum(costs),
        "missing_latency_count": len(results) - len(timed),
        "missing_cost_count": len(results) - len(costs),
    }
