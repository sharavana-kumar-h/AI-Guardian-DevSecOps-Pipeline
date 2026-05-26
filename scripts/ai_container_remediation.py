#!/usr/bin/env python3
"""Build an AI-style container remediation queue from Trivy, image metadata, and provenance evidence."""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

SEV_WEIGHT = {"CRITICAL": 100, "HIGH": 70, "MEDIUM": 40, "LOW": 15, "INFO": 5, "UNKNOWN": 10}


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def add_task(tasks: list[dict[str, Any]], title: str, severity: str, evidence: str, action: str, source: str) -> None:
    tasks.append({
        "title": title,
        "severity": severity,
        "score": SEV_WEIGHT.get(severity, 10),
        "evidence": evidence,
        "recommended_action": action,
        "source": source,
    })


def build_tasks(reports: Path) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    trivy_policy = read_json(reports/'trivy-policy-result.json', {})
    for v in trivy_policy.get('violations', []) or []:
        sev = str(v.get('severity', 'UNKNOWN')).upper()
        add_task(
            tasks,
            f"Reduce {v.get('type')} {sev} findings below policy threshold",
            sev if sev in SEV_WEIGHT else 'HIGH',
            v.get('message', 'Policy threshold violation'),
            "Upgrade affected packages, change base image, or add a justified temporary exception only after review.",
            'trivy-policy-result.json',
        )
    examples = trivy_policy.get('summary', {}).get('examples', {})
    for vuln in examples.get('vulnerabilities', [])[:8]:
        sev = str(vuln.get('severity', 'UNKNOWN')).upper()
        pkg = vuln.get('package') or 'unknown package'
        fixed = vuln.get('fixed') or 'no fixed version listed'
        add_task(
            tasks,
            f"Patch container package {pkg}",
            sev if sev in SEV_WEIGHT else 'MEDIUM',
            f"{vuln.get('id')} in {pkg}; installed={vuln.get('installed')}; fixed={fixed}",
            "Prefer a patched base image. If this is an app dependency, upgrade the dependency and rebuild the image.",
            'trivy-image.json',
        )
    metadata = read_json(reports/'image-metadata.json', {})
    for f in metadata.get('findings', []) or []:
        sev = str(f.get('severity', 'INFO')).upper()
        add_task(tasks, f.get('title', 'Container metadata finding'), sev if sev in SEV_WEIGHT else 'INFO', f.get('evidence', ''), f.get('recommendation', 'Review container hardening.'), 'image-metadata.json')
    provenance = read_json(reports/'image-provenance.json', {})
    missing = [k for k, v in provenance.get('hashes', {}).items() if not v]
    if missing:
        add_task(tasks, 'Complete image provenance evidence', 'MEDIUM', ', '.join(missing), 'Generate missing SBOM/build evidence before promoting the image.', 'image-provenance.json')
    if not tasks:
        add_task(tasks, 'Maintain current container baseline', 'INFO', 'No container remediation tasks were produced from available reports.', 'Continue scanning on every commit and after base-image updates.', 'container-remediation')
    return sorted(tasks, key=lambda t: (-int(t.get('score', 0)), t.get('title', '')))


def md(tasks: list[dict[str, Any]], generated_at: str) -> str:
    lines = ["# Day 20 - AI Container Remediation Queue", ""]
    lines.append(f"Generated: `{generated_at}`")
    lines.append("")
    lines.append("This report converts image-scan, image-metadata, and provenance evidence into a practical container fix queue.")
    lines.append("")
    lines.append("## Prioritized tasks")
    lines.append("| Priority | Severity | Task | Evidence | Recommended action | Source |")
    lines.append("|---:|---|---|---|---|---|")
    for i, t in enumerate(tasks, 1):
        lines.append(f"| {i} | {t['severity']} | {t['title']} | {t['evidence']} | {t['recommended_action']} | `{t['source']}` |")
    lines.append("")
    lines.append("## Suggested Day 20 demo")
    lines.append("1. Run Trivy and policy enforcement.")
    lines.append("2. Show a failing threshold or metadata warning.")
    lines.append("3. Open this remediation queue and explain the first three fixes.")
    lines.append("4. Rebuild the image and rerun the policy to show improvement.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--reports', default='reports')
    ap.add_argument('--json-output', default='reports/ai-container-remediation.json')
    ap.add_argument('--markdown-output', default='reports/ai-container-remediation.md')
    args = ap.parse_args()
    reports = Path(args.reports)
    reports.mkdir(exist_ok=True)
    generated_at = dt.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
    tasks = build_tasks(reports)
    payload = {'generated_at': generated_at, 'task_count': len(tasks), 'tasks': tasks}
    Path(args.json_output).write_text(json.dumps(payload, indent=2))
    Path(args.markdown_output).write_text(md(tasks, generated_at))
    print(f"Wrote {args.markdown_output}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
