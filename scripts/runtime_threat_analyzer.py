#!/usr/bin/env python3
"""Analyze Kubernetes events/logs and produce an AI-style runtime threat summary."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_rules(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"rules": [], "score": {"HIGH": 20, "MEDIUM": 8, "LOW": 3}}


def severity_score(findings: list[dict[str, str]], weights: dict[str, int]) -> int:
    penalty = sum(int(weights.get(item["severity"], 1)) for item in findings)
    return max(0, 100 - penalty)


def markdown(findings: list[dict[str, str]], score: int, source: str) -> str:
    lines = [
        "# Day 24 - AI Runtime Threat Summary",
        "",
        f"**Runtime security score:** {score}/100",
        f"**Source:** `{source}`",
        "",
        "## Detection summary",
        "",
        f"- High signals: {sum(1 for f in findings if f['severity'] == 'HIGH')}",
        f"- Medium signals: {sum(1 for f in findings if f['severity'] == 'MEDIUM')}",
        f"- Low signals: {sum(1 for f in findings if f['severity'] == 'LOW')}",
        "",
    ]
    if not findings:
        lines.extend([
            "No configured runtime threat patterns were detected in the collected logs/events.",
            "",
        ])
    else:
        lines.append("## Findings")
        lines.append("")
        for item in findings:
            lines.extend([
                f"### {item['severity']} - {item['name']}",
                f"- **Matched line:** `{item['line'][:220]}`",
                f"- **Recommendation:** {item['recommendation']}",
                "",
            ])
    lines.extend([
        "## Recommended next steps",
        "",
        "- Wire this stage to real Kubernetes events after every deployment.",
        "- Add Falco, CloudWatch Container Insights, or Prometheus alerts for stronger runtime coverage.",
        "- Keep this AI summary as an explanation layer, not as the only runtime detection engine.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="reports/runtime-signals.txt")
    parser.add_argument("--rules", default="config/runtime-threat-rules.json")
    parser.add_argument("--json-output", default="reports/runtime-threat-summary.json")
    parser.add_argument("--markdown-output", default="reports/runtime-threat-summary.md")
    parser.add_argument("--fail-on-high", action="store_true")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8", errors="replace") if Path(args.input).exists() else ""
    config = load_rules(Path(args.rules))
    findings: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for rule in config.get("rules", []):
        pattern = rule.get("pattern", "")
        if not pattern:
            continue
        regex = re.compile(pattern, re.IGNORECASE)
        for line in text.splitlines():
            if regex.search(line):
                key = (rule.get("name", "runtime-signal"), line.strip())
                if key in seen:
                    continue
                seen.add(key)
                severity = str(rule.get("severity", "LOW")).upper()
                recommendation = {
                    "HIGH": "Investigate immediately before promoting this deployment. Check pod describe output, image availability, credentials, RBAC, and resource pressure.",
                    "MEDIUM": "Review application logs and rollout health. Add alerting if the pattern repeats.",
                    "LOW": "Track as hygiene and monitor for recurrence.",
                }.get(severity, "Review the signal and tune detection rules if needed.")
                findings.append({
                    "name": rule.get("name", "runtime-signal"),
                    "severity": severity,
                    "line": line.strip(),
                    "recommendation": recommendation,
                })

    score = severity_score(findings, config.get("score", {}))
    payload = {"score": score, "findings": findings, "source": args.input}
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(findings, score, args.input), encoding="utf-8")
    print(f"Runtime threat score: {score}/100 with {len(findings)} finding(s)")
    if args.fail_on_high and any(item["severity"] == "HIGH" for item in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
