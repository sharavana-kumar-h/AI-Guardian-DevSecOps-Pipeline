#!/usr/bin/env python3
"""Check whether the repository has enough evidence to be GitHub-demo ready."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return {}


def status(path: Path) -> str:
    return "present" if path.exists() and path.stat().st_size > 0 else "missing"


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day 22 - Release Readiness Report",
        "",
        f"**Decision:** {payload['decision']}",
        f"**Readiness score:** {payload['score']}/100",
        "",
        "## Required repository files",
        "",
        "| File | Status |",
        "|---|---|",
    ]
    for row in payload["required_files"]:
        lines.append(f"| `{row['path']}` | {row['status']} |")
    lines.extend(["", "## Required evidence reports", "", "| Report | Status |", "|---|---|"])
    for row in payload["required_reports"]:
        lines.append(f"| `{row['path']}` | {row['status']} |")
    lines.extend(["", "## Recommended evidence reports", "", "| Report | Status |", "|---|---|"])
    for row in payload["recommended_reports"]:
        lines.append(f"| `{row['path']}` | {row['status']} |")
    lines.extend(["", "## Notes", ""])
    if payload["notes"]:
        for note in payload["notes"]:
            lines.append(f"- {note}")
    else:
        lines.append("- No readiness gaps detected by the offline checker.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/release-readiness-policy.json")
    parser.add_argument("--output", default="reports/release-readiness.md")
    parser.add_argument("--json-output", default="reports/release-readiness.json")
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    required_files = config.get("required_files", [])
    required_reports = config.get("required_reports", [])
    recommended_reports = config.get("recommended_reports", [])

    required_file_rows = [{"path": item, "status": status(Path(item))} for item in required_files]
    required_report_rows = [{"path": item, "status": status(Path(item))} for item in required_reports]
    recommended_report_rows = [{"path": item, "status": status(Path(item))} for item in recommended_reports]

    missing_required_files = [row["path"] for row in required_file_rows if row["status"] != "present"]
    missing_required_reports = [row["path"] for row in required_report_rows if row["status"] != "present"]
    missing_recommended_reports = [row["path"] for row in recommended_report_rows if row["status"] != "present"]

    total_required = max(1, len(required_file_rows) + len(required_report_rows))
    present_required = sum(1 for row in required_file_rows + required_report_rows if row["status"] == "present")
    total_recommended = max(1, len(recommended_report_rows))
    present_recommended = sum(1 for row in recommended_report_rows if row["status"] == "present")

    score = round((present_required / total_required) * 80 + (present_recommended / total_recommended) * 20)
    decision = "PASS" if not missing_required_files and score >= 75 else "WARN" if score >= 60 else "FAIL"

    notes: list[str] = []
    if missing_required_files:
        notes.append("Required repository files missing: " + ", ".join(missing_required_files))
    if missing_required_reports:
        notes.append("Required evidence reports missing or empty: " + ", ".join(missing_required_reports))
    if missing_recommended_reports:
        notes.append("Recommended evidence reports missing or empty: " + ", ".join(missing_recommended_reports))
    if decision != "PASS":
        notes.append("The repository is still usable as a scaffold, but collect missing scanner evidence before calling it production-like.")

    payload = {
        "decision": decision,
        "score": score,
        "required_files": required_file_rows,
        "required_reports": required_report_rows,
        "recommended_reports": recommended_report_rows,
        "notes": notes,
    }
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    Path(args.output).write_text(markdown(payload), encoding="utf-8")
    print(f"Release readiness: {decision} ({score}/100)")
    return 1 if args.fail and decision == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
