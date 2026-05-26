#!/usr/bin/env python3
"""Score container image risk from Dockerfile and Trivy output."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def count_trivy(data: Any) -> dict[str, int]:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    if not isinstance(data, dict):
        return counts
    for result in data.get("Results", []) or []:
        for vuln in result.get("Vulnerabilities", []) or []:
            sev = str(vuln.get("Severity", "UNKNOWN")).upper()
            counts[sev if sev in counts else "UNKNOWN"] += 1
    return counts


def inspect_dockerfile(path: Path) -> dict[str, bool | str]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    return {
        "has_non_root_user": bool(re.search(r"^USER\s+(?!root\b).+", text, re.IGNORECASE | re.MULTILINE)),
        "uses_latest_tag": bool(re.search(r"^FROM\s+\S+:latest\b", text, re.IGNORECASE | re.MULTILINE)),
        "has_healthcheck": bool(re.search(r"^HEALTHCHECK\b", text, re.IGNORECASE | re.MULTILINE)),
        "uses_multi_stage": len(re.findall(r"^FROM\s+", text, re.IGNORECASE | re.MULTILINE)) >= 2,
        "base_images": ", ".join(re.findall(r"^FROM\s+([^\s]+)", text, re.IGNORECASE | re.MULTILINE)) or "unknown",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dockerfile", default="Dockerfile")
    parser.add_argument("--trivy", default="reports/trivy-image.json")
    parser.add_argument("--output", default="reports/ai-container-risk.md")
    parser.add_argument("--json-output", default="reports/ai-container-risk.json")
    args = parser.parse_args()

    trivy = count_trivy(load_json(Path(args.trivy)))
    docker = inspect_dockerfile(Path(args.dockerfile))

    score = 100
    score -= trivy["CRITICAL"] * 25
    score -= trivy["HIGH"] * 10
    score -= min(trivy["MEDIUM"] * 2, 20)
    if docker["uses_latest_tag"]:
        score -= 20
    if not docker["has_non_root_user"]:
        score -= 25
    if not docker["has_healthcheck"]:
        score -= 5
    if not docker["uses_multi_stage"]:
        score -= 5
    score = max(score, 0)

    rating = "LOW" if score >= 85 else "MEDIUM" if score >= 65 else "HIGH" if score >= 40 else "CRITICAL"
    payload = {"score": score, "risk_rating": rating, "trivy_counts": trivy, "dockerfile": docker}

    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = f"""# AI Container Risk Score

| Metric | Value |
|---|---:|
| Risk rating | **{rating}** |
| Score | **{score}/100** |
| Critical CVEs | {trivy['CRITICAL']} |
| High CVEs | {trivy['HIGH']} |
| Medium CVEs | {trivy['MEDIUM']} |
| Non-root USER | {docker['has_non_root_user']} |
| Avoids latest tag | {not docker['uses_latest_tag']} |
| Multi-stage build | {docker['uses_multi_stage']} |
| Healthcheck present | {docker['has_healthcheck']} |

Base images: `{docker['base_images']}`

## Recommendation

- Do not push or deploy when the rating is HIGH or CRITICAL.
- Patch critical/high CVEs or switch to a cleaner base image.
- Keep non-root execution, health checks, and multi-stage builds enabled.
"""
    Path(args.output).write_text(md, encoding="utf-8")
    print(f"Container risk score written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
