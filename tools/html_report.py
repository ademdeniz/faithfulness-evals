"""Generate a dependency-free HTML report from normalized results."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.compare_results import compare_results


def render_report(results: list[dict[str, Any]]) -> str:
    comparison = compare_results(results) if len(results) >= 2 else None
    rows = []
    for result in results:
        for case in result["cases"]:
            verdict = (
                "PASS" if case["passed"] is True
                else "FAIL" if case["passed"] is False
                else "UNKNOWN"
            )
            rows.append(
                "<tr>"
                f"<td>{html.escape(result['framework'])}</td>"
                f"<td>{html.escape(case['case_id'])}</td>"
                f"<td>{case['score'] if case['score'] is not None else ''}</td>"
                f"<td>{verdict}</td>"
                f"<td>{html.escape(case.get('reason') or '')}</td>"
                "</tr>"
            )
    agreement = (
        f"<p>Agreement: {comparison['agreement_count']} / "
        f"{comparison['case_count']} cases; "
        f"{comparison['disagreement_count']} disagreements.</p>"
        if comparison
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Faithfulness Evaluation Report</title>
<style>
body {{ font: 16px system-ui, sans-serif; margin: 2rem; color: #222; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: .5rem; text-align: left; }}
th {{ background: #f2f2f2; }}
.PASS {{ color: #176b2c; font-weight: 700; }}
.FAIL {{ color: #a21d1d; font-weight: 700; }}
</style>
</head>
<body>
<h1>Faithfulness Evaluation Report</h1>
{agreement}
<table>
<thead><tr><th>Framework</th><th>Case</th><th>Score</th><th>Verdict</th><th>Reason</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    results = json.loads(args.results.read_text(encoding="utf-8"))
    args.output.write_text(render_report(results), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
