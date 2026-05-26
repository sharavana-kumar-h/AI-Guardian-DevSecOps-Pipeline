#!/usr/bin/env python3
"""Offline Kubernetes hardening checks for Day 7.

This does not replace OPA/Conftest. It gives a readable fallback report when a learner
has kubectl but not Conftest installed yet.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


def load_docs(path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    targets = [path] if path.is_file() else sorted(path.glob("*.yaml"))
    for target in targets:
        with target.open("r", encoding="utf-8") as fh:
            for doc in yaml.safe_load_all(fh):
                if isinstance(doc, dict):
                    doc["__source"] = str(target)
                    docs.append(doc)
    return docs


def check_deployment(doc: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    name = doc.get("metadata", {}).get("name", "unknown")
    spec = doc.get("spec", {})
    tmpl_spec = spec.get("template", {}).get("spec", {})
    pod_sc = tmpl_spec.get("securityContext", {})

    if spec.get("replicas", 0) < 2:
        findings.append(f"Deployment/{name}: replicas should be at least 2 for demo availability.")
    if spec.get("revisionHistoryLimit", 10) > 5:
        findings.append(f"Deployment/{name}: revisionHistoryLimit should be small, e.g. 3.")
    if tmpl_spec.get("automountServiceAccountToken") is not False:
        findings.append(f"Deployment/{name}: automountServiceAccountToken must be false.")
    if pod_sc.get("runAsNonRoot") is not True:
        findings.append(f"Deployment/{name}: pod securityContext.runAsNonRoot must be true.")
    if pod_sc.get("seccompProfile", {}).get("type") != "RuntimeDefault":
        findings.append(f"Deployment/{name}: seccompProfile.type must be RuntimeDefault.")

    for c in tmpl_spec.get("containers", []):
        cname = c.get("name", "container")
        image = c.get("image", "")
        sc = c.get("securityContext", {})
        res = c.get("resources", {})
        if not image or image == "IMAGE_PLACEHOLDER" or image.endswith(":latest"):
            findings.append(f"Deployment/{name}/{cname}: image must be rendered and must not use latest.")
        if sc.get("allowPrivilegeEscalation") is not False:
            findings.append(f"Deployment/{name}/{cname}: allowPrivilegeEscalation must be false.")
        if sc.get("readOnlyRootFilesystem") is not True:
            findings.append(f"Deployment/{name}/{cname}: readOnlyRootFilesystem must be true.")
        if sc.get("privileged") is True:
            findings.append(f"Deployment/{name}/{cname}: privileged must not be true.")
        if "ALL" not in sc.get("capabilities", {}).get("drop", []):
            findings.append(f"Deployment/{name}/{cname}: must drop ALL Linux capabilities.")
        for branch in ("requests", "limits"):
            if not res.get(branch, {}).get("cpu") or not res.get(branch, {}).get("memory"):
                findings.append(f"Deployment/{name}/{cname}: resources.{branch}.cpu and memory are required.")
        for probe in ("readinessProbe", "livenessProbe", "startupProbe"):
            if probe not in c:
                findings.append(f"Deployment/{name}/{cname}: {probe} is required.")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="reports/rendered-k8s")
    parser.add_argument("--output", default="reports/k8s-hardening-report.md")
    args = parser.parse_args()

    docs = load_docs(Path(args.path))
    findings: list[str] = []
    kinds = {doc.get("kind") for doc in docs}

    for doc in docs:
        if doc.get("kind") == "Deployment":
            findings.extend(check_deployment(doc))

    if "NetworkPolicy" not in kinds:
        findings.append("A NetworkPolicy should be present.")
    if "PodDisruptionBudget" not in kinds:
        findings.append("A PodDisruptionBudget should be present.")
    if "HorizontalPodAutoscaler" not in kinds:
        findings.append("A HorizontalPodAutoscaler should be present for the Day 7 hardening target.")
    if "ServiceAccount" not in kinds:
        findings.append("A dedicated ServiceAccount should be present.")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if not findings else "REVIEW_REQUIRED"
    lines = ["# Kubernetes Hardening Report", "", f"Status: **{status}**", ""]
    lines.append(f"Checked manifests from `{args.path}`.")
    lines.append("")
    if findings:
        lines.append("## Findings")
        lines.extend(f"- {item}" for item in findings)
    else:
        lines.append("No hardening issues found by the offline checker.")
    lines.append("")
    lines.append("OPA/Conftest remains the authoritative policy gate for this project.")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
