#!/usr/bin/env python3
"""Convert raw SonarQube issue evidence into a developer remediation queue."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEVERITY_WEIGHT = {"BLOCKER": 10, "CRITICAL": 8, "MAJOR": 5, "MINOR": 2, "INFO": 1}
TYPE_WEIGHT = {"VULNERABILITY": 4, "SECURITY_HOTSPOT": 3, "BUG": 2, "CODE_SMELL": 1}

REMEDIATION_HINTS = [
    ("null", "Add explicit null validation, defensive checks, or Bean Validation constraints."),
    ("password", "Remove sensitive values from code and use Jenkins credentials, Kubernetes Secrets, or a secret manager."),
    ("sql", "Use parameterized queries, Spring Data repositories, or prepared statements."),
    ("random", "Use SecureRandom for any security-sensitive randomness."),
    ("exception", "Handle exceptions narrowly and avoid swallowing security-relevant errors."),
    ("log", "Avoid logging secrets, tokens, credentials, and personal data."),
    ("csrf", "Enable CSRF protection for browser-authenticated state-changing requests."),
]


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def recommendation(message: str, issue_type: str) -> str:
    low = message.lower()
    for needle, hint in REMEDIATION_HINTS:
        if needle in low:
            return hint
    if issue_type == "VULNERABILITY":
        return "Prioritize this as a security fix. Read the Sonar rule details and add a regression test after remediation."
    if issue_type == "BUG":
        return "Fix the underlying logic defect and add a focused unit test that fails before the fix."
    if issue_type == "SECURITY_HOTSPOT":
        return "Review whether this code path is reachable by untrusted users and document the decision."
    return "Refactor to improve maintainability, then confirm tests and coverage still pass."


def risk_score(issue: dict[str, Any]) -> int:
    sev = SEVERITY_WEIGHT.get(str(issue.get("severity", "INFO")).upper(), 1)
    typ = TYPE_WEIGHT.get(str(issue.get("type", "CODE_SMELL")).upper(), 1)
    line_bonus = 1 if issue.get("line") else 0
    return min(10, sev + typ + line_bonus)


def normalize_issue(issue: dict[str, Any]) -> dict[str, Any]:
    message = str(issue.get("message", ""))
    issue_type = str(issue.get("type", "UNKNOWN")).upper()
    return {
        "key": issue.get("key"),
        "severity": str(issue.get("severity", "INFO")).upper(),
        "type": issue_type,
        "component": issue.get("component"),
        "line": issue.get("line"),
        "message": message,
        "rule": issue.get("rule"),
        "risk_score": risk_score(issue),
        "recommendation": recommendation(message, issue_type),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="reports/sonar-findings.json")
    parser.add_argument("--json-output", default="reports/sonar-issue-triage.json")
    parser.add_argument("--markdown-output", default="reports/sonar-issue-triage.md")
    args = parser.parse_args()

    data = load_json(Path(args.input))
    output = Path(args.json_output)
    md_output = Path(args.markdown_output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if not isinstance(data, dict) or data.get("error"):
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "UNAVAILABLE",
            "reason": data.get("error") if isinstance(data, dict) else "sonar evidence missing",
            "triaged_issues": [],
        }
    else:
        issues = ((data.get("issues") or {}).get("issues") or [])
        triaged = [normalize_issue(issue) for issue in issues]
        triaged.sort(key=lambda x: x["risk_score"], reverse=True)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "READY",
            "issue_count": len(triaged),
            "by_severity": dict(Counter(item["severity"] for item in triaged)),
            "by_type": dict(Counter(item["type"] for item in triaged)),
            "triaged_issues": triaged,
        }

    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    md = ["# SonarQube Issue Triage", "", f"Generated: `{payload['generated_at']}`", "", f"Status: **{payload['status']}**", ""]
    if payload["status"] != "READY":
        md.append(f"Reason: `{payload.get('reason', 'unknown')}`")
    else:
        md.append(f"Triaged issues: **{payload.get('issue_count', 0)}**")
        md.append("")
        md.append("| Risk | Severity | Type | Location | Message | Recommendation |")
        md.append("|---:|---|---|---|---|---|")
        for item in payload["triaged_issues"][:30]:
            loc = f"{item.get('component')}:{item.get('line') or ''}"
            msg = str(item.get("message", "")).replace("|", "\\|")[:120]
            rec = str(item.get("recommendation", "")).replace("|", "\\|")
            md.append(f"| {item['risk_score']} | {item['severity']} | {item['type']} | `{loc}` | {msg} | {rec} |")
    md.append("")
    md_output.write_text("\n".join(md), encoding="utf-8")
    print(f"Sonar issue triage written to {md_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
