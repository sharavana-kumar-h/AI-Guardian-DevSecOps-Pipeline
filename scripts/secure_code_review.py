#!/usr/bin/env python3
"""Lightweight secure-code review gate for the AI DevSecOps pipeline.

This is intentionally simple and transparent: it uses project-owned regex rules
as a fast pre-Sonar safety net. SonarQube remains the main SAST engine.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Finding:
    rule_id: str
    name: str
    severity: str
    file: str
    line: int
    evidence: str
    recommendation: str


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def should_ignore(path: Path, ignored: list[str], ignored_files: list[str], root: Path) -> bool:
    parts = set(path.parts)
    rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    return any(item in parts for item in ignored) or rel in ignored_files


def is_allowlisted(line: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        try:
            if re.search(pattern, line):
                return True
        except re.error:
            continue
    return False


def scan(root: Path, config: dict[str, Any]) -> list[Finding]:
    ignored = config.get("ignored_paths", [])
    ignored_files = config.get("ignored_files", [])
    allowlist_patterns = config.get("allowlist_evidence_patterns", [])
    findings: list[Finding] = []
    rules = config.get("rules", [])
    compiled = []
    for rule in rules:
        try:
            compiled.append((rule, re.compile(rule["pattern"])))
        except re.error as exc:
            print(f"Skipping invalid rule {rule.get('id')}: {exc}", file=sys.stderr)

    for file_path in root.rglob("*"):
        if not file_path.is_file() or should_ignore(file_path, ignored, ignored_files, root):
            continue
        suffix = file_path.suffix.lower()
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        for rule, regex in compiled:
            allowed = [x.lower() for x in rule.get("include_extensions", [])]
            if allowed and suffix not in allowed:
                continue
            for idx, line in enumerate(lines, start=1):
                if regex.search(line) and not is_allowlisted(line, allowlist_patterns):
                    evidence = line.strip()
                    if len(evidence) > 180:
                        evidence = evidence[:177] + "..."
                    findings.append(
                        Finding(
                            rule_id=rule.get("id", "UNKNOWN"),
                            name=rule.get("name", "Unnamed rule"),
                            severity=rule.get("severity", "INFO"),
                            file=str(file_path.relative_to(root)),
                            line=idx,
                            evidence=evidence,
                            recommendation=rule.get("recommendation", "Review and remediate."),
                        )
                    )
    return findings


def severity_counts(findings: list[Finding]) -> dict[str, int]:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for item in findings:
        sev = item.severity.upper()
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def write_reports(findings: list[Finding], json_output: Path, md_output: Path) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "secure_code_review.py",
        "finding_count": len(findings),
        "severity_counts": severity_counts(findings),
        "findings": [item.__dict__ for item in findings],
    }
    json_output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    md = ["# Secure Code Review Report", "", f"Generated: `{payload['generated_at']}`", ""]
    counts = payload["severity_counts"]
    md.append("## Severity Summary")
    md.append("")
    md.append("| Severity | Count |")
    md.append("|---|---:|")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        md.append(f"| {sev} | {counts.get(sev, 0)} |")
    md.append("")

    if findings:
        md.append("## Findings")
        md.append("")
        md.append("| Severity | Rule | Location | Evidence | Recommendation |")
        md.append("|---|---|---|---|---|")
        for item in findings[:100]:
            evidence = item.evidence.replace("|", "\\|")
            rec = item.recommendation.replace("|", "\\|")
            md.append(f"| {item.severity} | {item.rule_id} - {item.name} | `{item.file}:{item.line}` | `{evidence}` | {rec} |")
    else:
        md.append("No findings from project-owned secure-code review rules.")
    md.append("")
    md_output.write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", default="config/secure-code-review-rules.json")
    parser.add_argument("--json-output", default="reports/secure-code-review.json")
    parser.add_argument("--markdown-output", default="reports/secure-code-review.md")
    parser.add_argument("--fail-on-critical", action="store_true")
    parser.add_argument("--fail-on-high", action="store_true")
    args = parser.parse_args()

    findings = scan(Path(args.root), load_config(Path(args.config)))
    write_reports(findings, Path(args.json_output), Path(args.markdown_output))
    counts = severity_counts(findings)
    print(f"Secure-code review completed. Findings: {len(findings)}")
    if args.fail_on_critical and counts.get("CRITICAL", 0) > 0:
        return 1
    if args.fail_on_high and counts.get("HIGH", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
