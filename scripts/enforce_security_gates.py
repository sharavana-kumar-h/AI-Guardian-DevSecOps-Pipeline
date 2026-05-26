#!/usr/bin/env python3
"""Fail the build when scanner evidence violates configured security gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def trivy_counts(data: Any) -> dict[str, int]:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0}
    if not isinstance(data, dict):
        return counts
    for result in data.get("Results", []) or []:
        for vuln in result.get("Vulnerabilities", []) or []:
            sev = str(vuln.get("Severity", "")).upper()
            if sev in counts:
                counts[sev] += 1
    return counts


def dependency_highs(data: Any) -> int:
    if not isinstance(data, dict):
        return 0
    total = 0
    for dep in data.get("dependencies", []) or []:
        for vuln in dep.get("vulnerabilities", []) or []:
            sev = str(vuln.get("severity", "")).upper()
            score = 0.0
            for key in ("cvssv4", "cvssv3", "cvssv2"):
                try:
                    score = max(score, float((vuln.get(key) or {}).get("baseScore") or (vuln.get(key) or {}).get("score") or 0))
                except (TypeError, ValueError):
                    pass
            if sev in {"CRITICAL", "HIGH"} or score >= 7:
                total += 1
    return total


def conftest_failures(data: Any) -> int:
    if not isinstance(data, list):
        return 0
    return sum(len(result.get("failures", []) or []) for result in data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--max-trivy-critical", type=int, default=0)
    parser.add_argument("--max-trivy-high", type=int, default=0)
    parser.add_argument("--max-dependency-high", type=int, default=0)
    parser.add_argument("--allow-sonar-unavailable", action="store_true")
    args = parser.parse_args()

    reports = Path(args.reports)
    failures: list[str] = []

    secret = (reports / "secret-scan.txt").read_text(encoding="utf-8", errors="replace") if (reports / "secret-scan.txt").exists() else ""
    if "Potential secret" in secret:
        failures.append("Secret scan found potential exposed credentials.")

    sonar = load_json(reports / "sonar-findings.json")
    if isinstance(sonar, dict) and not sonar.get("error"):
        status = (sonar.get("quality_gate", {}).get("projectStatus", {}) or {}).get("status")
        if status == "ERROR":
            failures.append("SonarQube quality gate failed.")
    elif not args.allow_sonar_unavailable and (reports / "sonar-findings.json").exists():
        failures.append("SonarQube evidence file exists but quality gate could not be verified.")

    dep_high = dependency_highs(load_json(Path("target/dependency-check-report/dependency-check-report.json")))
    if dep_high > args.max_dependency_high:
        failures.append(f"Dependency Check has {dep_high} high/critical findings; allowed {args.max_dependency_high}.")

    trivy = trivy_counts(load_json(reports / "trivy-image.json"))
    if trivy["CRITICAL"] > args.max_trivy_critical:
        failures.append(f"Trivy has {trivy['CRITICAL']} critical findings; allowed {args.max_trivy_critical}.")
    if trivy["HIGH"] > args.max_trivy_high:
        failures.append(f"Trivy has {trivy['HIGH']} high findings; allowed {args.max_trivy_high}.")

    sca_policy = load_json(reports / "sca-policy-result.json")
    if isinstance(sca_policy, dict) and sca_policy.get("decision") == "FAIL":
        failures.append("Dependency risk policy failed.")
    license_policy = load_json(reports / "license-policy-result.json")
    if isinstance(license_policy, dict) and license_policy.get("decision") == "FAIL":
        failures.append("License policy failed.")

    docker_policy = conftest_failures(load_json(reports / "conftest-dockerfile.json"))
    k8s_policy = conftest_failures(load_json(reports / "conftest-k8s.json"))
    if docker_policy:
        failures.append(f"Dockerfile policy check has {docker_policy} failure(s).")
    if k8s_policy:
        failures.append(f"Kubernetes policy check has {k8s_policy} failure(s).")

    output = reports / "security-gate-result.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    if failures:
        output.write_text("# Security Gate Result\n\nFAILED\n\n" + "\n".join(f"- {item}" for item in failures) + "\n", encoding="utf-8")
        print(output.read_text(encoding="utf-8"), file=sys.stderr)
        return 1

    output.write_text("# Security Gate Result\n\nPASSED\n", encoding="utf-8")
    print("Security gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
