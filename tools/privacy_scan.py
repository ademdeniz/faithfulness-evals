"""Scan evaluation text for common sensitive-data patterns."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PATTERNS = {
    "anthropic_api_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?1[-. ]?)?(?:\(?\d{3}\)?[-. ]?)\d{3}[-.]\d{4}\b"),
    "medical_record_number": re.compile(
        r"\b(?:MRN|medical record number)\s*[:#-]?\s*[A-Z0-9-]{4,}\b",
        re.IGNORECASE,
    ),
}


def scan_text(text: str) -> list[dict[str, int | str]]:
    findings = []
    for kind, pattern in PATTERNS.items():
        findings.extend(
            {
                "type": kind,
                "start": match.start(),
                "end": match.end(),
            }
            for match in pattern.finditer(text)
        )
    return sorted(findings, key=lambda finding: finding["start"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    findings = scan_text(args.path.read_text(encoding="utf-8"))
    if findings:
        print(f"Sensitive data detected: {len(findings)} finding(s)")
        for finding in findings:
            print(f"- {finding['type']} at offset {finding['start']}")
        return 1
    print(f"No sensitive data detected in {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
