"""Parse provider usage fields and estimate model-call costs."""

from __future__ import annotations

from typing import Any


def extract_usage(response: dict[str, Any]) -> dict[str, int]:
    usage = response.get("usage", response.get("usage_metadata", {}))
    return {
        "input_tokens": int(
            usage.get("input_tokens", usage.get("prompt_tokens", 0))
        ),
        "output_tokens": int(
            usage.get("output_tokens", usage.get("completion_tokens", 0))
        ),
    }


def estimate_cost(
    usage: dict[str, int],
    input_usd_per_million: float,
    output_usd_per_million: float,
) -> float:
    if input_usd_per_million < 0 or output_usd_per_million < 0:
        raise ValueError("Token prices cannot be negative.")
    cost = (
        usage["input_tokens"] * input_usd_per_million
        + usage["output_tokens"] * output_usd_per_million
    ) / 1_000_000
    return round(cost, 8)
