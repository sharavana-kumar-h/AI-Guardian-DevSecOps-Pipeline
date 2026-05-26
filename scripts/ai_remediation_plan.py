#!/usr/bin/env python3
"""Generate a developer-facing AI-style remediation plan from pipeline evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def load_text(path: Path, limit: int = 6000) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit]


def add_action(actions: list[dict[str, Any]], source: str, priority: str, title: str, detail: str) -> None:
    actions.append({"source": source, "priority": priority, "title": title, "detail": detail})


def build_actions(reports: Path) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []

    secure = load_json(reports / "secure-code-review.json")
    if isinstance(secure, dict):
        for finding in secure.get("findings", [])[:20]:
            sev = finding.get("severity", "INFO")
            priority = "P0" if sev == "CRITICAL" else "P1" if sev == "HIGH" else "P2"
            add_action(
                actions,
                "Secure Code Review",
                priority,
                f"Fix {finding.get('rule_id')} in {finding.get('file')}:{finding.get('line')}",
                finding.get("recommendation", "Review and remediate."),
            )

    sonar = load_json(reports / "sonar-issue-triage.json")
    if isinstance(sonar, dict) and sonar.get("status") == "READY":
        for issue in sonar.get("triaged_issues", [])[:20]:
            score = int(issue.get("risk_score", 0))
            priority = "P0" if score >= 9 else "P1" if score >= 7 else "P2"
            add_action(
                actions,
                "SonarQube",
                priority,
                f"Resolve {issue.get('severity')} {issue.get('type')} issue",
                f"{issue.get('component')}:{issue.get('line') or ''} — {issue.get('recommendation')}",
            )

    cves = load_json(reports / "ai-cve-priorities.json")
    if isinstance(cves, list):
        for vuln in cves[:10]:
            priority = vuln.get("priority", "P2")
            title = vuln.get("id") or vuln.get("cve") or "Dependency/container CVE"
            detail = vuln.get("recommendation") or vuln.get("reason") or "Upgrade vulnerable dependency/image and rerun scan."
            add_action(actions, "CVE Prioritization", priority, f"Remediate {title}", detail)

    container = load_json(reports / "ai-container-risk.json")
    if isinstance(container, dict):
        score = int(container.get("risk_score", 0) or 0)
        if score >= 50:
            add_action(actions, "Container Risk", "P1", "Reduce Docker image risk score", "Review high/critical image CVEs, base image choice, non-root user, and package footprint.")

    sonar_policy = load_json(reports / "sonar-policy-result.json")
    if isinstance(sonar_policy, dict) and sonar_policy.get("status") == "FAILED":
        for fail in sonar_policy.get("failures", []):
            add_action(actions, "Sonar Local Policy", "P0", "Fix local SAST gate violation", fail)

    # Stable ordering: P0 before P1 before P2.
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    actions.sort(key=lambda item: order.get(item.get("priority", "P3"), 3))
    return actions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--output", default="reports/ai-remediation-plan.md")
    parser.add_argument("--json-output", default="reports/ai-remediation-plan.json")
    args = parser.parse_args()

    reports = Path(args.reports)
    actions = build_actions(reports)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "action_count": len(actions),
        "actions": actions,
    }
    Path(args.json_output).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    md = ["# AI Remediation Plan", "", f"Generated: `{payload['generated_at']}`", ""]
    md.append("This report converts scanner evidence into an ordered developer fix queue. It does not replace scanner output; it summarizes it for execution.")
    md.append("")
    if not actions:
        md.append("No remediation actions were generated from the available reports. Run SonarQube, Dependency Check, Trivy, and policy gates for richer output.")
    else:
        md.append("## Ordered Fix Queue")
        md.append("")
        md.append("| Priority | Source | Action | Detail |")
        md.append("|---|---|---|---|")
        for item in actions[:50]:
            detail = str(item.get("detail", "")).replace("|", "\\|")[:220]
            title = str(item.get("title", "")).replace("|", "\\|")
            md.append(f"| {item.get('priority')} | {item.get('source')} | {title} | {detail} |")
        md.append("")
        md.append("## Suggested Developer Workflow")
        md.append("")
        md.append("1. Fix all P0 items first and add regression tests.")
        md.append("2. Re-run `mvn -B clean verify` and the Day 11-13 scripts.")
        md.append("3. Fix P1 items before image publishing or deployment.")
        md.append("4. Convert any accepted-risk item into a documented exception with owner and expiry date.")
    md.append("")
    Path(args.output).write_text("\n".join(md), encoding="utf-8")
    print(f"AI remediation plan written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
