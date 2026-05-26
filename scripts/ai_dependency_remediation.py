#!/usr/bin/env python3
"""Generate an AI-style remediation plan for dependency and license risk evidence."""

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


def dependency_label(item: dict[str, Any]) -> str:
    return str(item.get("dependency") or item.get("component") or "unknown")


def build_actions(sca: dict[str, Any] | None, license_report: dict[str, Any] | None, inventory: dict[str, Any] | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if isinstance(sca, dict):
        for finding in sca.get("top_findings", [])[:15]:
            severity = finding.get("severity", "UNKNOWN")
            cvss = float(finding.get("cvss") or 0)
            priority = "P0" if severity == "CRITICAL" or cvss >= 9 else "P1" if severity == "HIGH" or cvss >= 7 else "P2"
            actions.append(
                {
                    "priority": priority,
                    "category": "Vulnerability",
                    "target": dependency_label(finding),
                    "finding": finding.get("name", "dependency vulnerability"),
                    "reason": f"{severity} dependency issue with CVSS {cvss:.1f}.",
                    "recommended_fix": "Upgrade to the nearest patched version, then re-run OWASP Dependency Check and regression tests.",
                    "validation": "mvn -B clean verify && mvn -B org.owasp:dependency-check-maven:check",
                }
            )
        if sca.get("failures") and not actions:
            for failure in sca.get("failures", [])[:5]:
                actions.append(
                    {
                        "priority": "P1",
                        "category": "SCA Policy",
                        "target": "dependency policy",
                        "finding": failure,
                        "reason": "The local SCA policy did not pass.",
                        "recommended_fix": "Review Dependency Check evidence and patch or justify the dependency risk.",
                        "validation": "bash scripts/run_day15_dependency_policy.sh",
                    }
                )
    if isinstance(license_report, dict):
        ev = license_report.get("evaluation", {}) or {}
        for item in ev.get("denied", [])[:10]:
            actions.append(
                {
                    "priority": "P1",
                    "category": "License",
                    "target": dependency_label(item),
                    "finding": "Denied license family detected",
                    "reason": "The license policy flags this dependency as risky for redistribution or commercial use.",
                    "recommended_fix": "Replace the dependency, obtain legal approval, or document a time-bound exception.",
                    "validation": "python3 scripts/license_policy_check.py --sbom reports/bom.json",
                }
            )
        unknowns = ev.get("unknown", []) or []
        if unknowns:
            actions.append(
                {
                    "priority": "P2",
                    "category": "License Metadata",
                    "target": f"{len(unknowns)} component(s)",
                    "finding": "Missing license metadata",
                    "reason": "License visibility is incomplete, which weakens compliance evidence.",
                    "recommended_fix": "Generate a full CycloneDX SBOM with Maven instead of relying on fallback SBOM mode.",
                    "validation": "bash scripts/run_day14_sca_inventory.sh",
                }
            )
    if isinstance(inventory, dict):
        direct_count = len(inventory.get("direct_dependencies", []) or [])
        sbom_count = len(inventory.get("sbom_components", []) or [])
        if sbom_count == 0:
            actions.append(
                {
                    "priority": "P1",
                    "category": "SBOM",
                    "target": "CycloneDX SBOM",
                    "finding": "No SBOM components found",
                    "reason": "Without SBOM evidence, the build cannot prove exactly what dependencies shipped.",
                    "recommended_fix": "Install Maven and run the CycloneDX Maven plugin in the Day 14 script.",
                    "validation": "test -f reports/bom.json && python3 scripts/dependency_inventory.py",
                }
            )
        elif sbom_count <= direct_count:
            actions.append(
                {
                    "priority": "P3",
                    "category": "SBOM Quality",
                    "target": "Dependency graph completeness",
                    "finding": "SBOM appears to contain direct dependencies only",
                    "reason": "A complete SBOM should include transitive dependencies for stronger vulnerability evidence.",
                    "recommended_fix": "Ensure CycloneDX Maven plugin runs successfully and includes runtime/compile scopes.",
                    "validation": "jq '.components | length' reports/bom.json",
                }
            )
    if not actions:
        actions.append(
            {
                "priority": "P3",
                "category": "Maintenance",
                "target": "dependency posture",
                "finding": "No immediate blocker detected from available dependency evidence",
                "reason": "Current SCA, SBOM, and license reports do not show hard failures.",
                "recommended_fix": "Keep Dependency Check NVD data fresh and regenerate SBOM on every build.",
                "validation": "bash scripts/run_day14_sca_inventory.sh && bash scripts/run_day15_dependency_policy.sh",
            }
        )
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    actions.sort(key=lambda item: priority_order.get(item["priority"], 9))
    return actions


def markdown(report: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {a['priority']} | {a['category']} | `{a['target']}` | {a['finding']} | {a['recommended_fix']} |" for a in report["actions"]
    )
    p0p1 = [a for a in report["actions"] if a["priority"] in {"P0", "P1"}]
    validation = "\n".join(f"- `{a['validation']}`" for a in report["actions"][:8])
    return f"""# Day 16 AI Dependency Remediation Plan

Generated: {report['generated_at']}

## Executive Summary

- Total actions: **{len(report['actions'])}**
- P0/P1 actions: **{len(p0p1)}**
- Recommended deploy decision: **{'BLOCK until P0/P1 dependency actions are resolved' if p0p1 else 'ALLOW after standard validation'}**

## Remediation Queue

| Priority | Category | Target | Finding | Recommended Fix |
|---|---|---|---|---|
{rows}

## Validation Commands

{validation}

## Operating Rules

1. Patch direct dependencies first.
2. Do not suppress dependency findings unless they are proven false positives.
3. Every suppression should include a reason, owner, and expiry date.
4. Regenerate SBOM and rerun SCA after each dependency change.
5. Archive SBOM, Dependency Check report, license report, and this plan as build artifacts.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sca", default="reports/sca-policy-result.json")
    parser.add_argument("--license", default="reports/license-policy-result.json")
    parser.add_argument("--inventory", default="reports/dependency-inventory.json")
    parser.add_argument("--json-output", default="reports/ai-dependency-remediation.json")
    parser.add_argument("--markdown-output", default="reports/ai-dependency-remediation.md")
    args = parser.parse_args()

    sca = load_json(Path(args.sca))
    lic = load_json(Path(args.license))
    inv = load_json(Path(args.inventory))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {"sca": args.sca, "license": args.license, "inventory": args.inventory},
        "actions": build_actions(sca, lic, inv),
    }
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(report), encoding="utf-8")
    print(Path(args.markdown_output).read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
