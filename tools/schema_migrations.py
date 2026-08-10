"""Migrate legacy normalized evaluation results to the current schema."""

from __future__ import annotations

from typing import Any

from tools.eval_result import SCHEMA_VERSION


def migrate_result(result: dict[str, Any]) -> dict[str, Any]:
    version = result.get("schema_version", 0)
    if version > SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported result schema version {version}; current is {SCHEMA_VERSION}."
        )
    migrated = dict(result)
    migrated.setdefault("schema_version", SCHEMA_VERSION)
    migrated.setdefault("generated_at", None)
    migrated.setdefault("model", None)
    migrated.setdefault("latency_ms", None)
    migrated.setdefault("input_tokens", None)
    migrated.setdefault("output_tokens", None)
    migrated.setdefault("estimated_cost_usd", None)
    for case in migrated.get("cases", []):
        case.setdefault("reason", None)
        case.setdefault("claims", [])
    return migrated
