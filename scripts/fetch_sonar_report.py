#!/usr/bin/env python3
"""Fetch SonarQube quality gate and issue evidence for AI analysis.

This script is safe to run even when SonarQube is not available. It writes a
machine-readable JSON file with status metadata so Jenkins can archive evidence
without breaking unrelated stages.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def request_json(url: str, token: str | None) -> Any:
    headers = {"Accept": "application/json"}
    if token:
        raw = f"{token}:".encode("utf-8")
        headers["Authorization"] = "Basic " + base64.b64encode(raw).decode("ascii")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:  # nosec - local/user-provided SonarQube URL
        return json.loads(response.read().decode("utf-8", errors="replace"))


def write_outputs(output: Path, markdown_output: Path, payload: dict[str, Any]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    gate = payload.get("quality_gate", {})
    issues = payload.get("issues", {}).get("issues", []) if isinstance(payload.get("issues"), dict) else []
    measures = payload.get("measures", {}).get("component", {}).get("measures", []) if isinstance(payload.get("measures"), dict) else []
    measure_map = {item.get("metric"): item.get("value") for item in measures if isinstance(item, dict)}
    issue_rows = []
    for issue in issues[:20]:
        issue_rows.append(
            f"| {issue.get('severity', 'NA')} | {issue.get('type', 'NA')} | "
            f"{issue.get('component', 'NA')}:{issue.get('line', '')} | {str(issue.get('message', ''))[:120]} |"
        )

    md = "# SonarQube Evidence\n\n"
    md += f"Generated: `{payload.get('generated_at')}`\n\n"
    md += f"Project: `{payload.get('project_key')}`\n\n"
    if payload.get("error"):
        md += f"Status: `UNAVAILABLE`\n\nError: `{payload['error']}`\n"
    else:
        md += f"Quality gate status: **{gate.get('projectStatus', {}).get('status', 'UNKNOWN')}**\n\n"
        if measure_map:
            md += "## Key Measures\n\n"
            md += "| Metric | Value |\n|---|---:|\n"
            for key in ["bugs", "vulnerabilities", "security_hotspots", "code_smells", "coverage", "duplicated_lines_density", "ncloc"]:
                md += f"| {key} | {measure_map.get(key, 'NA')} |\n"
            md += "\n"
        md += "## Top Issues\n\n"
        if issue_rows:
            md += "| Severity | Type | Location | Message |\n|---|---|---|---|\n"
            md += "\n".join(issue_rows) + "\n"
        else:
            md += "No issues returned by the API query.\n"
    markdown_output.write_text(md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-url", default=os.getenv("SONAR_HOST_URL", "http://localhost:9000"))
    parser.add_argument("--project-key", default=os.getenv("SONAR_PROJECT_KEY", "ai-devsecops-demo"))
    parser.add_argument("--token", default=os.getenv("SONAR_TOKEN") or os.getenv("SONAR_AUTH_TOKEN"))
    parser.add_argument("--output", default="reports/sonar-findings.json")
    parser.add_argument("--markdown-output", default="reports/sonar-evidence.md")
    args = parser.parse_args()

    host = args.host_url.rstrip("/")
    project = args.project_key
    output = Path(args.output)
    markdown_output = Path(args.markdown_output)

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_key": project,
        "host_url": host,
        "quality_gate": {},
        "issues": {},
    }

    try:
        q_project = urllib.parse.quote(project, safe="")
        payload["quality_gate"] = request_json(
            f"{host}/api/qualitygates/project_status?projectKey={q_project}", args.token
        )
        issue_query = urllib.parse.urlencode(
            {
                "componentKeys": project,
                "severities": "BLOCKER,CRITICAL,MAJOR",
                "resolved": "false",
                "ps": "100",
            }
        )
        payload["issues"] = request_json(f"{host}/api/issues/search?{issue_query}", args.token)

        metrics_query = urllib.parse.urlencode({
            "component": project,
            "metricKeys": ",".join([
                "bugs",
                "vulnerabilities",
                "security_hotspots",
                "code_smells",
                "coverage",
                "duplicated_lines_density",
                "ncloc",
                "reliability_rating",
                "security_rating",
                "sqale_rating",
            ]),
        })
        payload["measures"] = request_json(f"{host}/api/measures/component?{metrics_query}", args.token)

        hotspots_query = urllib.parse.urlencode({
            "projectKey": project,
            "status": "TO_REVIEW",
            "ps": "100",
        })
        try:
            payload["security_hotspots"] = request_json(f"{host}/api/hotspots/search?{hotspots_query}", args.token)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as hotspot_exc:
            payload["security_hotspots_error"] = str(hotspot_exc)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        payload["error"] = str(exc)
        write_outputs(output, markdown_output, payload)
        print(f"SonarQube evidence unavailable: {exc}", file=sys.stderr)
        return 0

    write_outputs(output, markdown_output, payload)
    print(f"SonarQube evidence written to {output} and {markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
