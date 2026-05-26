#!/usr/bin/env python3
"""Evaluate dependency vulnerability evidence against a local SCA risk policy."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def find_depcheck(explicit: str | None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            Path("target/dependency-check-report/dependency-check-report.json"),
            Path("reports/dependency-check-report.json"),
        ]
    )
    for path in candidates:
        if path.exists():
            return path
    return None


def max_cvss(vuln: dict[str, Any]) -> float:
    score = 0.0
    for key in ("cvssv4", "cvssv3", "cvssv2"):
        value = vuln.get(key) or {}
        for score_key in ("baseScore", "score"):
            try:
                score = max(score, float(value.get(score_key) or 0))
            except (TypeError, ValueError):
                pass
    try:
        score = max(score, float(vuln.get("cvssScore") or 0))
    except (TypeError, ValueError):
        pass
    return score


def normalize_severity(vuln: dict[str, Any]) -> str:
    severity = str(vuln.get("severity", "")).upper()
    if severity in SEVERITIES:
        return severity
    score = max_cvss(vuln)
    if score >= 9:
        return "CRITICAL"
    if score >= 7:
        return "HIGH"
    if score >= 4:
        return "MEDIUM"
    if score > 0:
        return "LOW"
    return "UNKNOWN"


def summarize_depcheck(data: Any) -> tuple[dict[str, int], list[dict[str, Any]]]:
    counts = {sev: 0 for sev in SEVERITIES}
    findings: list[dict[str, Any]] = []
    if not isinstance(data, dict):
        return counts, findings
    for dep in data.get("dependencies", []) or []:
        dep_name = dep.get("fileName") or dep.get("filePath") or dep.get("packagePath") or "unknown-dependency"
        for vuln in dep.get("vulnerabilities", []) or []:
            severity = normalize_severity(vuln)
            counts[severity] += 1
            findings.append(
                {
                    "dependency": dep_name,
                    "name": vuln.get("name", "unknown-cve"),
                    "severity": severity,
                    "cvss": max_cvss(vuln),
                    "source": vuln.get("source", "dependency-check"),
                    "description": (vuln.get("description") or "")[:500],
                }
            )
    findings.sort(key=lambda item: (item["cvss"], item["severity"]), reverse=True)
    return counts, findings


def sbom_component_count(path: Path) -> int:
    data = load_json(path)
    if not isinstance(data, dict):
        return 0
    return len(data.get("components", []) or [])


def markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    failures = report["failures"]
    warnings = report["warnings"]
    top = report["top_findings"]
    top_rows = "\n".join(
        f"| `{f['dependency']}` | `{f['name']}` | {f['severity']} | {f['cvss']:.1f} |" for f in top[:15]
    ) or "| _No Dependency Check vulnerabilities available_ | - | - | - |"
    fail_text = "\n".join(f"- {item}" for item in failures) or "- None"
    warn_text = "\n".join(f"- {item}" for item in warnings) or "- None"
    actions = "\n".join(f"{idx}. {item}" for idx, item in enumerate(report["recommended_actions"], start=1))
    return f"""# Day 15 SCA Risk Policy Result

Generated: {report['generated_at']}

## Decision

**{report['decision']}**

## Vulnerability Counts

| Severity | Count |
|---|---:|
| Critical | {counts['CRITICAL']} |
| High | {counts['HIGH']} |
| Medium | {counts['MEDIUM']} |
| Low | {counts['LOW']} |
| Unknown | {counts['UNKNOWN']} |

## SBOM Status

- SBOM required: **{report['policy'].get('require_sbom')}**
- SBOM path: `{report['sbom_path']}`
- SBOM component count: **{report['sbom_component_count']}**
- Dependency Check report: `{report['dependency_check_path']}`

## Failures

{fail_text}

## Warnings

{warn_text}

## Highest Priority Findings

| Dependency | Finding | Severity | CVSS |
|---|---|---:|---:|
{top_rows}

## Recommended Actions

{actions}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default="config/sca-risk-policy.json")
    parser.add_argument("--dependency-check", default=None)
    parser.add_argument("--sbom", default="reports/bom.json")
    parser.add_argument("--json-output", default="reports/sca-policy-result.json")
    parser.add_argument("--markdown-output", default="reports/sca-policy-result.md")
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args()

    policy = load_json(Path(args.policy)) or {}
    dep_path = find_depcheck(args.dependency_check)
    dep_data = load_json(dep_path) if dep_path else None
    counts, findings = summarize_depcheck(dep_data)

    failures: list[str] = []
    warnings: list[str] = []
    sbom_path = Path(args.sbom)
    component_count = sbom_component_count(sbom_path)

    if policy.get("require_sbom", True) and component_count == 0:
        failures.append("SBOM is required but no valid SBOM components were found.")
    if policy.get("require_dependency_check_report", False) and dep_path is None:
        failures.append("Dependency Check report is required but was not found.")
    elif dep_path is None:
        warnings.append("Dependency Check report not found; policy evaluated SBOM presence only.")

    if counts["CRITICAL"] > int(policy.get("max_critical_vulnerabilities", 0)):
        failures.append(f"Critical vulnerabilities exceed policy: {counts['CRITICAL']} found.")
    if counts["HIGH"] > int(policy.get("max_high_vulnerabilities", 0)):
        failures.append(f"High vulnerabilities exceed policy: {counts['HIGH']} found.")
    if counts["MEDIUM"] > int(policy.get("max_medium_vulnerabilities", 999999)):
        warnings.append(f"Medium vulnerabilities exceed warning threshold: {counts['MEDIUM']} found.")
    hard_cvss = float(policy.get("fail_on_cvss_at_or_above", 9.0))
    warn_cvss = float(policy.get("warn_on_cvss_at_or_above", 7.0))
    for finding in findings:
        if finding["cvss"] >= hard_cvss:
            failures.append(f"{finding['name']} on {finding['dependency']} has CVSS {finding['cvss']:.1f}.")
        elif finding["cvss"] >= warn_cvss:
            warnings.append(f"{finding['name']} on {finding['dependency']} has CVSS {finding['cvss']:.1f}.")

    # De-duplicate while preserving order.
    failures = list(dict.fromkeys(failures))
    warnings = list(dict.fromkeys(warnings))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": "FAIL" if failures else "PASS_WITH_WARNINGS" if warnings else "PASS",
        "policy": policy,
        "dependency_check_path": str(dep_path) if dep_path else None,
        "sbom_path": str(sbom_path) if sbom_path.exists() else None,
        "sbom_component_count": component_count,
        "counts": counts,
        "top_findings": findings[:25],
        "failures": failures,
        "warnings": warnings,
        "recommended_actions": policy.get("recommended_actions", []),
    }
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(report), encoding="utf-8")
    print(Path(args.markdown_output).read_text(encoding="utf-8"))
    if args.fail and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
