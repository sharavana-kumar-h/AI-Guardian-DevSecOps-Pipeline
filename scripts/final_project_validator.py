#!/usr/bin/env python3
"""Offline final validator for the GitHub-ready AI DevSecOps repository."""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import subprocess
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        return result.returncode, result.stdout.strip()
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired:
        return 124, "command timed out"


def check_python(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
            rows.append({"check": "python-syntax", "target": str(path), "status": "PASS", "detail": "compiled"})
        except Exception as exc:
            rows.append({"check": "python-syntax", "target": str(path), "status": "FAIL", "detail": str(exc)})
    return rows


def check_shell(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((root / "scripts").glob("*.sh")):
        code, out = run(["bash", "-n", str(path)], root)
        rows.append({"check": "shell-syntax", "target": str(path), "status": "PASS" if code == 0 else "FAIL", "detail": out})
    return rows


def check_json(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((root / "config").glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
            rows.append({"check": "json-parse", "target": str(path), "status": "PASS", "detail": "valid JSON"})
        except Exception as exc:
            rows.append({"check": "json-parse", "target": str(path), "status": "FAIL", "detail": str(exc)})
    return rows


def check_yaml(root: Path) -> list[dict[str, Any]]:
    rows = []
    if yaml is None:
        return [{"check": "yaml-parse", "target": "PyYAML", "status": "WARN", "detail": "PyYAML unavailable"}]
    for folder in [root / "k8s", root / "infra", root / ".github"]:
        if not folder.exists():
            continue
        for path in sorted(list(folder.rglob("*.yml")) + list(folder.rglob("*.yaml"))):
            try:
                list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
                rows.append({"check": "yaml-parse", "target": str(path), "status": "PASS", "detail": "valid YAML"})
            except Exception as exc:
                rows.append({"check": "yaml-parse", "target": str(path), "status": "FAIL", "detail": str(exc)})
    return rows


def check_required_files(root: Path) -> list[dict[str, Any]]:
    required = [
        "README.md", "DAILY_LOG.md", "CHANGELOG.md", "PROJECT_PLAN_90_DAYS.md", "Jenkinsfile", "Dockerfile", "pom.xml",
        ".github/workflows/validate.yml", "scripts/run_day25_final_validation.sh", "docs/final-github-submission.md",
    ]
    return [{"check": "required-file", "target": item, "status": "PASS" if (root / item).exists() else "FAIL", "detail": "present" if (root / item).exists() else "missing"} for item in required]


def check_external_tools(root: Path) -> list[dict[str, Any]]:
    tools = ["java", "mvn", "docker", "trivy", "conftest", "kubectl", "aws", "eksctl"]
    rows = []
    for tool in tools:
        code, out = run(["bash", "-lc", f"command -v {tool} >/dev/null && {tool} --version 2>&1 | head -n 1 || true"], root)
        detail = out if out else "not installed in this environment"
        rows.append({"check": "external-tool", "target": tool, "status": "INFO" if out else "WARN", "detail": detail})
    return rows


def summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return counts


def markdown(rows: list[dict[str, Any]], counts: dict[str, int]) -> str:
    decision = "PASS" if counts.get("FAIL", 0) == 0 else "FAIL"
    lines = [
        "# Day 25 - Final GitHub Readiness Validation",
        "",
        f"**Offline validation decision:** {decision}",
        "",
        "## Summary",
        "",
        f"- PASS: {counts.get('PASS', 0)}",
        f"- FAIL: {counts.get('FAIL', 0)}",
        f"- WARN: {counts.get('WARN', 0)}",
        f"- INFO: {counts.get('INFO', 0)}",
        "",
        "## Validation results",
        "",
        "| Check | Target | Status | Detail |",
        "|---|---|---|---|",
    ]
    for row in rows:
        detail = str(row.get("detail", "")).replace("|", "\\|").replace("\n", "<br>")[:400]
        lines.append(f"| {row['check']} | `{row['target']}` | {row['status']} | {detail} |")
    lines.extend([
        "",
        "## Important limitation",
        "",
        "This validator is an offline repository validator. It verifies file structure, script syntax, JSON/YAML parsing, and local report generation. It cannot prove Maven, Docker, Trivy, SonarQube, Conftest, kubectl, or AWS/EKS execution unless those tools and credentials are available in the runner.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json-output", default="reports/final-validation.json")
    parser.add_argument("--markdown-output", default="reports/final-validation.md")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    rows: list[dict[str, Any]] = []
    rows.extend(check_required_files(root))
    rows.extend(check_json(root))
    rows.extend(check_yaml(root))
    rows.extend(check_python(root))
    rows.extend(check_shell(root))
    rows.extend(check_external_tools(root))

    counts = summary(rows)
    payload = {"decision": "PASS" if counts.get("FAIL", 0) == 0 else "FAIL", "counts": counts, "results": rows}
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(rows, counts), encoding="utf-8")
    print(f"Final offline validation: {payload['decision']} ({counts})")
    return 0 if payload["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
