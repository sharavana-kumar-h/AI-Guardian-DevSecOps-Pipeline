#!/usr/bin/env python3
"""Generate an AI-assisted security report from scanner outputs.

Modes:
1. Offline deterministic mode: summarizes local reports with transparent heuristics.
2. LLM mode: when LLM_API_URL and LLM_API_KEY are set, sends a compact prompt to your chosen model endpoint.

The scanner outputs remain the source of truth. This script prioritizes and explains evidence; it does not invent findings.
"""

from __future__ import annotations

import argparse
import json
import os
import textwrap
import urllib.request
from pathlib import Path
from typing import Any


def read_text(path: Path, max_chars: int = 12_000) -> str:
    if not path.exists():
        return f"[missing] {path}"
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception as exc:  # pragma: no cover
        return f"[error reading {path}: {exc}]"


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def summarize_trivy(data: Any) -> dict[str, int]:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    if not isinstance(data, dict):
        return counts
    for result in data.get("Results", []) or []:
        for vuln in result.get("Vulnerabilities", []) or []:
            sev = str(vuln.get("Severity", "UNKNOWN")).upper()
            counts[sev if sev in counts else "UNKNOWN"] += 1
    return counts


def summarize_dependency_check(data: Any) -> dict[str, int]:
    counts = {"critical_or_high": 0, "total_vulnerable_dependencies": 0, "total_vulnerabilities": 0}
    if not isinstance(data, dict):
        return counts
    for dep in data.get("dependencies", []) or []:
        vulns = dep.get("vulnerabilities", []) or []
        if vulns:
            counts["total_vulnerable_dependencies"] += 1
        for vuln in vulns:
            counts["total_vulnerabilities"] += 1
            severity = str(vuln.get("severity", "")).upper()
            score = 0.0
            for key in ("cvssv4", "cvssv3", "cvssv2"):
                try:
                    score = max(score, float((vuln.get(key) or {}).get("baseScore") or (vuln.get(key) or {}).get("score") or 0))
                except (TypeError, ValueError):
                    pass
            if severity in {"CRITICAL", "HIGH"} or score >= 7:
                counts["critical_or_high"] += 1
    return counts


def summarize_sonar(data: Any) -> dict[str, Any]:
    summary = {"quality_gate": "UNKNOWN", "blocker": 0, "critical": 0, "major": 0, "total": 0, "available": False}
    if not isinstance(data, dict) or data.get("error"):
        return summary
    summary["available"] = True
    summary["quality_gate"] = (data.get("quality_gate", {}).get("projectStatus", {}) or {}).get("status", "UNKNOWN")
    issues = data.get("issues", {}).get("issues", []) if isinstance(data.get("issues"), dict) else []
    summary["total"] = len(issues)
    for issue in issues:
        sev = str(issue.get("severity", "")).upper()
        if sev == "BLOCKER":
            summary["blocker"] += 1
        elif sev == "CRITICAL":
            summary["critical"] += 1
        elif sev == "MAJOR":
            summary["major"] += 1
    return summary


def summarize_conftest(data: Any) -> dict[str, int]:
    summary = {"failures": 0, "warnings": 0, "successes": 0}
    if not isinstance(data, list):
        return summary
    for result in data:
        summary["failures"] += len(result.get("failures", []) or [])
        summary["warnings"] += len(result.get("warnings", []) or [])
        summary["successes"] += len(result.get("successes", []) or [])
    return summary


def build_policy_recommendations(conftest_docker: dict[str, int], conftest_k8s: dict[str, int]) -> list[str]:
    recommendations = []
    if conftest_docker["failures"] or conftest_k8s["failures"]:
        recommendations.append("Fix all Conftest deny results before image push or Kubernetes deployment.")
    else:
        recommendations.append("Current Dockerfile and Kubernetes manifests passed the included policy checks.")
    recommendations.extend(
        [
            "Add future policies for image digest pinning, signed images, and SBOM attestation.",
            "Add environment-specific policy bundles for dev, staging, and production namespaces.",
            "Review exceptions through time-bound suppressions instead of permanent bypasses.",
        ]
    )
    return recommendations


def build_offline_report(reports_dir: Path, output_path: Path) -> str:
    trivy = summarize_trivy(load_json(reports_dir / "trivy-image.json"))
    depcheck = summarize_dependency_check(load_json(Path("target/dependency-check-report/dependency-check-report.json")))
    sonar = summarize_sonar(load_json(reports_dir / "sonar-findings.json"))
    conftest_docker = summarize_conftest(load_json(reports_dir / "conftest-dockerfile.json"))
    conftest_k8s = summarize_conftest(load_json(reports_dir / "conftest-k8s.json"))
    secret_scan = read_text(reports_dir / "secret-scan.txt", 2_000)
    runtime = read_text(reports_dir / "runtime-signals.txt", 3_000)
    cve_priorities = read_text(reports_dir / "ai-cve-priorities.md", 4_000)
    container_risk = read_text(reports_dir / "ai-container-risk.md", 2_000)
    sonar_evidence = read_text(reports_dir / "sonar-evidence.md", 3_000)
    secure_code_review = read_text(reports_dir / "secure-code-review.md", 3_000)
    sonar_policy = read_text(reports_dir / "sonar-policy-result.md", 2_000)
    remediation_plan = read_text(reports_dir / "ai-remediation-plan.md", 3_000)
    dependency_inventory = read_text(reports_dir / "dependency-inventory.md", 2_500)
    sca_policy = read_text(reports_dir / "sca-policy-result.md", 2_500)
    license_policy = read_text(reports_dir / "license-policy-result.md", 2_500)
    dependency_remediation = read_text(reports_dir / "ai-dependency-remediation.md", 3_000)
    trivy_policy = read_text(reports_dir / "trivy-policy-result.md", 2_500)
    image_metadata = read_text(reports_dir / "image-metadata.md", 2_500)
    image_provenance = read_text(reports_dir / "image-provenance.md", 2_500)
    container_remediation = read_text(reports_dir / "ai-container-remediation.md", 3_000)
    manifest_review = read_text(reports_dir / "manifest-security-review.md", 3_000)
    release_readiness = read_text(reports_dir / "release-readiness.md", 2_500)
    rds_integration = read_text(reports_dir / "rds-integration-report.md", 2_000)
    runtime_threat_summary = read_text(reports_dir / "runtime-threat-summary.md", 3_000)
    final_validation = read_text(reports_dir / "final-validation.md", 3_000)
    manifest_review_json = load_json(reports_dir / "manifest-security-review.json")
    runtime_threat_json = load_json(reports_dir / "runtime-threat-summary.json")
    release_readiness_json = load_json(reports_dir / "release-readiness.json")
    sca_policy_json = load_json(reports_dir / "sca-policy-result.json")
    license_policy_json = load_json(reports_dir / "license-policy-result.json")
    trivy_policy_json = load_json(reports_dir / "trivy-policy-result.json")
    image_metadata_json = load_json(reports_dir / "image-metadata.json")
    secure_code_json = load_json(reports_dir / "secure-code-review.json")
    secure_counts = (secure_code_json or {}).get("severity_counts", {}) if isinstance(secure_code_json, dict) else {}

    risk = "LOW"
    blockers = []
    if "Potential secret" in secret_scan:
        blockers.append("potential secret exposure")
    if sonar["quality_gate"] == "ERROR" or sonar["blocker"] > 0 or sonar["critical"] > 0:
        blockers.append("SonarQube quality/security gate issue")
    if trivy["CRITICAL"] > 0 or depcheck["critical_or_high"] > 0:
        blockers.append("critical/high CVE evidence")
    if conftest_docker["failures"] > 0 or conftest_k8s["failures"] > 0:
        blockers.append("policy-as-code failure")
    if secure_counts.get("CRITICAL", 0) or secure_counts.get("HIGH", 0):
        blockers.append("secure-code review high/critical finding")
    if isinstance(sca_policy_json, dict) and sca_policy_json.get("decision") == "FAIL":
        blockers.append("dependency risk policy failure")
    if isinstance(license_policy_json, dict) and license_policy_json.get("decision") == "FAIL":
        blockers.append("license policy failure")
    if isinstance(trivy_policy_json, dict) and trivy_policy_json.get("decision") == "FAIL":
        blockers.append("container image policy failure")
    if isinstance(image_metadata_json, dict) and (image_metadata_json.get("summary", {}) or {}).get("high_or_critical", 0):
        blockers.append("container metadata hardening issue")
    if isinstance(manifest_review_json, dict) and manifest_review_json.get("score", 100) < 80:
        blockers.append("Kubernetes manifest security review score below 80")
    if isinstance(runtime_threat_json, dict) and any(item.get("severity") == "HIGH" for item in runtime_threat_json.get("findings", [])):
        blockers.append("high-severity runtime threat signal")
    if isinstance(release_readiness_json, dict) and release_readiness_json.get("decision") == "FAIL":
        blockers.append("release readiness failure")

    if blockers:
        risk = "HIGH"
    elif trivy["HIGH"] > 0 or trivy["MEDIUM"] > 5 or sonar["major"] > 0:
        risk = "MEDIUM"

    policy_recommendations = "\n".join(f"{idx}. {item}" for idx, item in enumerate(build_policy_recommendations(conftest_docker, conftest_k8s), start=1))
    blockers_text = ", ".join(blockers) if blockers else "No hard blocker identified from available evidence."

    report = f"""# AI-Assisted Security Report

## Executive Risk Rating

**{risk}**

Blocker summary: {blockers_text}

## Evidence Summary

| Signal | Result |
|---|---:|
| SonarQube quality gate | {sonar['quality_gate']} |
| SonarQube blocker issues | {sonar['blocker']} |
| SonarQube critical issues | {sonar['critical']} |
| SonarQube major issues returned | {sonar['major']} |
| Trivy critical CVEs | {trivy['CRITICAL']} |
| Trivy high CVEs | {trivy['HIGH']} |
| Trivy medium CVEs | {trivy['MEDIUM']} |
| OWASP Dependency Check critical/high findings | {depcheck['critical_or_high']} |
| Vulnerable dependencies | {depcheck['total_vulnerable_dependencies']} |
| SCA policy decision | {(sca_policy_json or {}).get('decision', 'UNKNOWN') if isinstance(sca_policy_json, dict) else 'UNKNOWN'} |
| License policy decision | {(license_policy_json or {}).get('decision', 'UNKNOWN') if isinstance(license_policy_json, dict) else 'UNKNOWN'} |
| Trivy image policy decision | {(trivy_policy_json or {}).get('decision', 'UNKNOWN') if isinstance(trivy_policy_json, dict) else 'UNKNOWN'} |
| Container metadata findings | {(image_metadata_json or {}).get('summary', {}).get('total_findings', 'UNKNOWN') if isinstance(image_metadata_json, dict) else 'UNKNOWN'} |
| Container metadata high/critical findings | {(image_metadata_json or {}).get('summary', {}).get('high_or_critical', 'UNKNOWN') if isinstance(image_metadata_json, dict) else 'UNKNOWN'} |
| Manifest security score | {(manifest_review_json or {}).get('score', 'UNKNOWN') if isinstance(manifest_review_json, dict) else 'UNKNOWN'} |
| Runtime threat score | {(runtime_threat_json or {}).get('score', 'UNKNOWN') if isinstance(runtime_threat_json, dict) else 'UNKNOWN'} |
| Release readiness decision | {(release_readiness_json or {}).get('decision', 'UNKNOWN') if isinstance(release_readiness_json, dict) else 'UNKNOWN'} |
| Dockerfile policy failures | {conftest_docker['failures']} |
| Kubernetes policy failures | {conftest_k8s['failures']} |
| Secure-code critical findings | {secure_counts.get('CRITICAL', 0)} |
| Secure-code high findings | {secure_counts.get('HIGH', 0)} |

## Prioritized Remediation

1. Revoke and rotate any exposed secret before continuing the pipeline.
2. Fix SonarQube blocker/critical findings and pass the quality gate.
3. Patch critical/high dependency and container CVEs before pushing the image.
4. Fix OPA/Conftest policy failures before deployment.
5. Re-run all scans, archive evidence, and review runtime signals after deployment.

## Secure Code Review

{secure_code_review}

## Local Sonar Policy

{sonar_policy}

## AI CVE Prioritization

{cve_priorities}

## Dependency Inventory and SBOM

{dependency_inventory}

## Dependency Risk Policy

{sca_policy}

## License Policy

{license_policy}

## AI Dependency Remediation

{dependency_remediation}

## AI Container Risk

{container_risk}

## Trivy Image Policy

{trivy_policy}

## Container Image Metadata

{image_metadata}

## Image Provenance

{image_provenance}

## AI Container Remediation

{container_remediation}

## Kubernetes Manifest Security Review

{manifest_review}

## Release Readiness

{release_readiness}

## RDS PostgreSQL Integration

{rds_integration}

## AI Runtime Threat Summary

{runtime_threat_summary}

## Final Validation Snapshot

{final_validation}

## AI Policy Recommendations

{policy_recommendations}

## Scanner Notes

### Secret Scan

```text
{secret_scan}
```

### SonarQube Evidence

{sonar_evidence}

### Runtime Signals

```text
{runtime}
```

## AI Remediation Plan Snapshot

{remediation_plan}

## Limitations

This report is an assistant layer. Scanner outputs and Jenkins gate results remain the source of truth.
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return report


def call_llm(prompt: str) -> str | None:
    api_url = os.getenv("LLM_API_URL")
    api_key = os.getenv("LLM_API_KEY")
    if not api_url or not api_key:
        return None

    payload = json.dumps({"prompt": prompt, "max_tokens": 1600}).encode("utf-8")
    request = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # nosec - user-controlled endpoint by design
            body = response.read().decode("utf-8", errors="replace")
            data = json.loads(body)
            return data.get("text") or data.get("response") or data.get("choices", [{}])[0].get("text")
    except Exception as exc:
        return f"LLM call failed, using offline report only. Error: {exc}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", default="reports", help="Directory containing scanner outputs")
    parser.add_argument("--output", default="reports/ai-security-report.md", help="Markdown output path")
    args = parser.parse_args()

    reports_dir = Path(args.reports)
    output_path = Path(args.output)

    offline_report = build_offline_report(reports_dir, output_path)

    prompt = textwrap.dedent(
        f"""
        You are a DevSecOps security reviewer. Convert this evidence into a concise risk report.
        Preserve scanner evidence. Do not invent CVEs. Prioritize fix order.

        {offline_report[:10_000]}
        """
    )
    llm_report = call_llm(prompt)
    if llm_report and not llm_report.startswith("LLM call failed"):
        output_path.write_text(llm_report, encoding="utf-8")
    elif llm_report:
        output_path.write_text(offline_report + "\n\n" + llm_report + "\n", encoding="utf-8")

    print(f"Security report written to {output_path}")


if __name__ == "__main__":
    main()
