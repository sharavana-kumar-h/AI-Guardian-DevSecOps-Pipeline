#!/usr/bin/env python3
"""Create an AI-ready CVE priority report from SCA and image scan outputs.

The script uses deterministic scoring by default so it works without API keys.
It does not invent vulnerabilities; it only ranks findings present in scanner JSON.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class Finding:
    source: str
    id: str
    severity: str
    package: str
    installed_version: str
    fixed_version: str
    title: str
    score: float
    rationale: str


SEVERITY_WEIGHT = {
    "CRITICAL": 100,
    "HIGH": 75,
    "MEDIUM": 45,
    "LOW": 15,
    "UNKNOWN": 5,
}


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def normalize_severity(value: str | None) -> str:
    sev = str(value or "UNKNOWN").upper()
    return sev if sev in SEVERITY_WEIGHT else "UNKNOWN"


def score_finding(severity: str, fixed_version: str, source: str, title: str) -> tuple[float, str]:
    base = SEVERITY_WEIGHT.get(severity, 5)
    reasons = [f"{severity.lower()} severity"]
    if fixed_version and fixed_version not in {"", "None", "null", "unknown"}:
        base += 10
        reasons.append("fix version available")
    if source == "trivy-image":
        base += 5
        reasons.append("runs inside deployed container image")
    if any(token in title.lower() for token in ["remote code execution", "rce", "authentication bypass", "privilege escalation"]):
        base += 15
        reasons.append("high-impact exploit class mentioned")
    return min(base, 130), "; ".join(reasons)


def from_trivy(data: Any) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(data, dict):
        return findings
    for result in data.get("Results", []) or []:
        target = result.get("Target", "container-image")
        for vuln in result.get("Vulnerabilities", []) or []:
            sev = normalize_severity(vuln.get("Severity"))
            fixed = str(vuln.get("FixedVersion") or "")
            title = str(vuln.get("Title") or vuln.get("Description") or "")[:180]
            score, rationale = score_finding(sev, fixed, "trivy-image", title)
            findings.append(
                Finding(
                    source="trivy-image",
                    id=str(vuln.get("VulnerabilityID") or "UNKNOWN"),
                    severity=sev,
                    package=f"{target}:{vuln.get('PkgName', 'unknown')}",
                    installed_version=str(vuln.get("InstalledVersion") or ""),
                    fixed_version=fixed,
                    title=title or "Container/package vulnerability",
                    score=score,
                    rationale=rationale,
                )
            )
    return findings


def from_dependency_check(data: Any) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(data, dict):
        return findings
    for dep in data.get("dependencies", []) or []:
        package = str(dep.get("fileName") or dep.get("filePath") or "unknown dependency")
        for vuln in dep.get("vulnerabilities", []) or []:
            sev = normalize_severity(vuln.get("severity"))
            if sev == "UNKNOWN":
                score_data = vuln.get("cvssv3") or vuln.get("cvssv2") or {}
                try:
                    numeric = float(score_data.get("baseScore") or score_data.get("score") or 0)
                    sev = "CRITICAL" if numeric >= 9 else "HIGH" if numeric >= 7 else "MEDIUM" if numeric >= 4 else "LOW"
                except (TypeError, ValueError):
                    pass
            fixed = str(vuln.get("fixedVersion") or "")
            title = str(vuln.get("name") or vuln.get("description") or "")[:180]
            score, rationale = score_finding(sev, fixed, "dependency-check", title)
            findings.append(
                Finding(
                    source="dependency-check",
                    id=str(vuln.get("name") or "UNKNOWN"),
                    severity=sev,
                    package=package,
                    installed_version=str(dep.get("version") or ""),
                    fixed_version=fixed,
                    title=title or "Dependency vulnerability",
                    score=score,
                    rationale=rationale,
                )
            )
    return findings


def write_markdown(findings: list[Finding], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    critical = sum(1 for f in findings if f.severity == "CRITICAL")
    high = sum(1 for f in findings if f.severity == "HIGH")
    md = "# AI CVE Prioritization Report\n\n"
    md += "This report ranks scanner findings by severity, deployability impact, and fix availability.\n\n"
    md += f"Total findings: **{len(findings)}** | Critical: **{critical}** | High: **{high}**\n\n"
    if not findings:
        md += "No Dependency Check or Trivy findings were available. Run Day 4 scans first.\n"
    else:
        md += "| Rank | Source | ID | Severity | Package | Fix | Score | Why it matters |\n"
        md += "|---:|---|---|---|---|---|---:|---|\n"
        for index, finding in enumerate(findings[:25], start=1):
            fix = finding.fixed_version or "not listed"
            md += (
                f"| {index} | {finding.source} | {finding.id} | {finding.severity} | "
                f"{finding.package} | {fix} | {finding.score:.0f} | {finding.rationale} |\n"
            )
        md += "\n## Fix Order\n\n"
        md += "1. Fix critical findings with available patched versions.\n"
        md += "2. Replace vulnerable container base layers before pushing the image.\n"
        md += "3. Patch high-severity application dependencies used in reachable code paths.\n"
        md += "4. Re-run Dependency Check and Trivy, then regenerate this report.\n"
    output.write_text(md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dependency-check", default="target/dependency-check-report/dependency-check-report.json")
    parser.add_argument("--trivy", default="reports/trivy-image.json")
    parser.add_argument("--json-output", default="reports/ai-cve-priorities.json")
    parser.add_argument("--markdown-output", default="reports/ai-cve-priorities.md")
    args = parser.parse_args()

    findings = []
    findings.extend(from_dependency_check(load_json(Path(args.dependency_check))))
    findings.extend(from_trivy(load_json(Path(args.trivy))))
    findings.sort(key=lambda item: item.score, reverse=True)

    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps([asdict(f) for f in findings], indent=2), encoding="utf-8")
    write_markdown(findings, Path(args.markdown_output))
    print(f"CVE priorities written to {json_output} and {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
