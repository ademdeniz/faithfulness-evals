"""Shared result schema for faithfulness evaluations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


SCHEMA_VERSION = 1


@dataclass
class ClaimResult:
    claim: str
    supported: bool | None
    evidence: list[str] = field(default_factory=list)


@dataclass
class CaseResult:
    case_id: str
    score: float | None
    passed: bool | None
    reason: str | None = None
    claims: list[ClaimResult] = field(default_factory=list)


@dataclass
class EvaluationResult:
    framework: str
    metric: str
    cases: list[CaseResult]
    schema_version: int = SCHEMA_VERSION
    model: str | None = None
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
