"""Parse provider usage fields and estimate model-call costs."""

from __future__ import annotations

from typing import Any


def _value(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def extract_usage(response: dict[str, Any]) -> dict[str, int]:
    usage = _value(response, "usage", None) or _value(
        response, "usage_metadata", {}
    )
    return {
        "input_tokens": int(
            _value(usage, "input_tokens", _value(usage, "prompt_tokens", 0))
        ),
        "output_tokens": int(
            _value(usage, "output_tokens", _value(usage, "completion_tokens", 0))
        ),
    }


def usage_from_objects(*objects: Any) -> dict[str, int] | None:
    """Return the first non-empty usage metadata exposed by an object."""
    for obj in objects:
        usage = extract_usage(obj)
        if usage["input_tokens"] or usage["output_tokens"]:
            return usage
    return None


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
