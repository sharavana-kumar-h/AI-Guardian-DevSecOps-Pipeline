#!/usr/bin/env python3
"""Apply local severity thresholds to Trivy image scan output."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def bump(counts: dict[str, int], severity: str | None) -> None:
    sev = (severity or "UNKNOWN").upper()
    if sev not in counts:
        sev = "UNKNOWN"
    counts[sev] += 1


def collect(scan: dict[str, Any]) -> dict[str, Any]:
    counts = {
        "vulnerabilities": {s: 0 for s in SEVERITIES},
        "misconfigurations": {s: 0 for s in SEVERITIES},
        "secrets": {s: 0 for s in SEVERITIES},
    }
    examples = {"vulnerabilities": [], "misconfigurations": [], "secrets": []}
    for result in scan.get("Results", []) or []:
        target = result.get("Target", "unknown")
        for item in result.get("Vulnerabilities", []) or []:
            bump(counts["vulnerabilities"], item.get("Severity"))
            if len(examples["vulnerabilities"]) < 12:
                examples["vulnerabilities"].append({
                    "target": target,
                    "id": item.get("VulnerabilityID"),
                    "severity": item.get("Severity", "UNKNOWN"),
                    "package": item.get("PkgName"),
                    "installed": item.get("InstalledVersion"),
                    "fixed": item.get("FixedVersion"),
                    "title": item.get("Title") or item.get("Description", "")[:120],
                })
        for item in result.get("Misconfigurations", []) or []:
            bump(counts["misconfigurations"], item.get("Severity"))
            if len(examples["misconfigurations"]) < 12:
                examples["misconfigurations"].append({
                    "target": target,
                    "id": item.get("ID"),
                    "severity": item.get("Severity", "UNKNOWN"),
                    "title": item.get("Title"),
                    "message": item.get("Message"),
                })
        for item in result.get("Secrets", []) or []:
            bump(counts["secrets"], item.get("Severity"))
            if len(examples["secrets"]) < 12:
                examples["secrets"].append({
                    "target": target,
                    "rule": item.get("RuleID"),
                    "severity": item.get("Severity", "UNKNOWN"),
                    "title": item.get("Title"),
                    "location": item.get("StartLine"),
                })
    return {"counts": counts, "examples": examples}


def evaluate(summary: dict[str, Any], policy: dict[str, Any], scan_missing: bool) -> tuple[str, list[dict[str, Any]]]:
    violations: list[dict[str, Any]] = []
    if scan_missing and policy.get("fail_when_scan_missing"):
        violations.append({"type": "scan", "severity": "HIGH", "message": "Trivy image scan is missing"})
    mappings = [
        ("vulnerabilities", "vulnerability_thresholds"),
        ("misconfigurations", "misconfiguration_thresholds"),
        ("secrets", "secret_thresholds"),
    ]
    for bucket, key in mappings:
        thresholds = policy.get(key, {})
        for sev, limit in thresholds.items():
            observed = summary["counts"].get(bucket, {}).get(sev.upper(), 0)
            if observed > int(limit):
                violations.append({
                    "type": bucket,
                    "severity": sev.upper(),
                    "observed": observed,
                    "allowed": int(limit),
                    "message": f"{bucket} {sev.upper()} count {observed} exceeds allowed {limit}",
                })
    return ("FAIL" if violations else "PASS", violations)


def md(payload: dict[str, Any]) -> str:
    lines = ["# Day 18 - Trivy Container Security Policy Result", ""]
    lines.append(f"Generated: `{payload['generated_at']}`")
    lines.append(f"Input: `{payload['input']}`")
    lines.append(f"Decision: **{payload['decision']}**")
    lines.append("")
    if payload.get("scan_missing"):
        lines.append("> Trivy scan output was not available. Generate it with `trivy image --format json --output reports/trivy-image.json $IMAGE`.")
        lines.append("")
    lines.append("## Counts")
    for bucket, counts in payload["summary"]["counts"].items():
        lines.append(f"### {bucket.title()}")
        lines.append("| Severity | Count |")
        lines.append("|---|---:|")
        for sev in SEVERITIES:
            lines.append(f"| {sev} | {counts.get(sev,0)} |")
        lines.append("")
    lines.append("## Violations")
    if not payload["violations"]:
        lines.append("No policy threshold violations detected.")
    else:
        lines.append("| Type | Severity | Observed | Allowed | Message |")
        lines.append("|---|---|---:|---:|---|")
        for v in payload["violations"]:
            lines.append(f"| {v.get('type')} | {v.get('severity')} | {v.get('observed','-')} | {v.get('allowed','-')} | {v.get('message')} |")
    lines.append("")
    lines.append("## Top examples")
    for bucket, rows in payload["summary"].get("examples", {}).items():
        if not rows:
            continue
        lines.append(f"### {bucket.title()}")
        for row in rows[:8]:
            title = row.get("title") or row.get("message") or "No title"
            ident = row.get("id") or row.get("rule") or "unknown"
            lines.append(f"- **{row.get('severity','UNKNOWN')}** `{ident}` in `{row.get('target','unknown')}` — {title}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="reports/trivy-image.json")
    ap.add_argument("--policy", default="config/container-security-policy.json")
    ap.add_argument("--json-output", default="reports/trivy-policy-result.json")
    ap.add_argument("--markdown-output", default="reports/trivy-policy-result.md")
    ap.add_argument("--fail", action="store_true")
    args = ap.parse_args()
    Path("reports").mkdir(exist_ok=True)
    policy = read_json(Path(args.policy), {})
    scan_path = Path(args.input)
    scan_missing = not scan_path.exists()
    scan = read_json(scan_path, {"Results": []})
    summary = collect(scan)
    decision, violations = evaluate(summary, policy, scan_missing)
    payload = {
        "generated_at": dt.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
        "input": args.input,
        "policy": policy.get("policy_name", "container-security-policy"),
        "scan_missing": scan_missing,
        "summary": summary,
        "decision": decision,
        "violations": violations,
    }
    Path(args.json_output).write_text(json.dumps(payload, indent=2))
    Path(args.markdown_output).write_text(md(payload))
    print(f"Container policy decision: {decision}")
    if args.fail and decision == "FAIL":
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
