#!/usr/bin/env python3
"""Apply a local deploy/no-deploy policy to SonarQube evidence."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECURITY_TYPES = {"VULNERABILITY", "SECURITY_HOTSPOT"}


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def get_measure(sonar: dict[str, Any], metric: str) -> float | None:
    measures = ((sonar.get("measures") or {}).get("component") or {}).get("measures") or []
    for item in measures:
        if item.get("metric") == metric:
            try:
                return float(item.get("value"))
            except (TypeError, ValueError):
                return None
    return None


def count_issues(sonar: dict[str, Any], severity: str | None = None, security_only: bool = False) -> int:
    issues = ((sonar.get("issues") or {}).get("issues") or [])
    count = 0
    for issue in issues:
        if severity and str(issue.get("severity", "")).upper() != severity:
            continue
        if security_only and str(issue.get("type", "")).upper() not in SECURITY_TYPES:
            continue
        count += 1
    return count


def hotspot_count(sonar: dict[str, Any]) -> int:
    hotspots = sonar.get("security_hotspots") or {}
    if isinstance(hotspots, dict):
        try:
            return int(hotspots.get("paging", {}).get("total") or hotspots.get("total") or 0)
        except (TypeError, ValueError):
            pass
    measure = get_measure(sonar, "security_hotspots")
    return int(measure or 0)


def evaluate(sonar: dict[str, Any] | None, config: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    thresholds = config.get("thresholds", {})
    deploy = config.get("deployment_decision", {})
    facts: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_name": config.get("policy_name"),
        "sonar_available": bool(isinstance(sonar, dict) and not sonar.get("error")),
    }
    failures: list[str] = []

    if not facts["sonar_available"]:
        error = sonar.get("error") if isinstance(sonar, dict) else "sonar evidence missing"
        facts["sonar_error"] = error
        if deploy.get("fail_on_unavailable_sonar", False):
            failures.append(f"SonarQube evidence unavailable: {error}")
        return ("FAILED" if failures else "WARNING", failures, facts)

    gate_status = (((sonar or {}).get("quality_gate") or {}).get("projectStatus") or {}).get("status", "UNKNOWN")
    facts["quality_gate_status"] = gate_status
    allowed = set(thresholds.get("allowed_quality_gate_statuses", ["OK"]))
    if gate_status not in allowed:
        failures.append(f"SonarQube quality gate status is {gate_status}; allowed statuses: {sorted(allowed)}")

    blocker = count_issues(sonar, "BLOCKER")
    critical = count_issues(sonar, "CRITICAL")
    major_security = count_issues(sonar, "MAJOR", security_only=True)
    hotspots = hotspot_count(sonar)
    coverage = get_measure(sonar, "coverage")
    dup = get_measure(sonar, "duplicated_lines_density")

    facts.update({
        "blocker_issues": blocker,
        "critical_issues": critical,
        "major_security_issues": major_security,
        "open_security_hotspots": hotspots,
        "coverage_percent": coverage,
        "duplicated_lines_density_percent": dup,
    })

    if blocker > thresholds.get("max_blocker_issues", 0):
        failures.append(f"Blocker issues: {blocker} > {thresholds.get('max_blocker_issues', 0)}")
    if critical > thresholds.get("max_critical_issues", 0):
        failures.append(f"Critical issues: {critical} > {thresholds.get('max_critical_issues', 0)}")
    if major_security > thresholds.get("max_major_security_issues", 0):
        failures.append(f"Major security issues: {major_security} > {thresholds.get('max_major_security_issues', 0)}")
    if deploy.get("fail_on_unreviewed_hotspots", False) and hotspots > thresholds.get("max_open_security_hotspots", 5):
        failures.append(f"Open security hotspots: {hotspots} > {thresholds.get('max_open_security_hotspots', 5)}")
    if coverage is not None and coverage < thresholds.get("min_coverage_percent", 70.0):
        failures.append(f"Coverage: {coverage}% < {thresholds.get('min_coverage_percent', 70.0)}%")
    if dup is not None and dup > thresholds.get("max_duplicated_lines_density_percent", 5.0):
        failures.append(f"Duplicated lines density: {dup}% > {thresholds.get('max_duplicated_lines_density_percent', 5.0)}%")

    return ("FAILED" if failures else "PASSED", failures, facts)


def write_outputs(status: str, failures: list[str], facts: dict[str, Any], json_output: Path, md_output: Path) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": status, "failures": failures, "facts": facts}
    json_output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md = ["# SonarQube Local SAST Policy Result", "", f"Status: **{status}**", "", "## Facts", ""]
    md.append("| Check | Value |")
    md.append("|---|---:|")
    for key, value in facts.items():
        md.append(f"| {key} | `{value}` |")
    md.append("")
    if failures:
        md.append("## Policy Violations")
        md.append("")
        for item in failures:
            md.append(f"- {item}")
    else:
        md.append("No local SAST policy violations were detected.")
    md.append("")
    md_output.write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sonar", default="reports/sonar-findings.json")
    parser.add_argument("--config", default="config/sonar-quality-gate.json")
    parser.add_argument("--json-output", default="reports/sonar-policy-result.json")
    parser.add_argument("--markdown-output", default="reports/sonar-policy-result.md")
    parser.add_argument("--fail", action="store_true", help="Exit non-zero when the local policy fails.")
    args = parser.parse_args()

    sonar = load_json(Path(args.sonar))
    config = load_json(Path(args.config)) or {}
    status, failures, facts = evaluate(sonar, config)
    write_outputs(status, failures, facts, Path(args.json_output), Path(args.markdown_output))
    print(f"Sonar local SAST policy status: {status}")
    if args.fail and status == "FAILED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
