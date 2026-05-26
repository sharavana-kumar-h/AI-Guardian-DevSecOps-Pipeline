#!/usr/bin/env python3
"""AI-style Kubernetes manifest security review from rendered YAML manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def load_yaml_documents(root: Path) -> list[dict[str, Any]]:
    if yaml is None:
        raise SystemExit("PyYAML is required for Kubernetes manifest review.")
    docs: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.y*ml")):
        if path.name.endswith(".template.yaml"):
            # Templates are reviewed as templates but not treated as deployable manifests.
            pass
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for doc in yaml.safe_load_all(handle):
                if isinstance(doc, dict):
                    doc["__file"] = str(path)
                    docs.append(doc)
    return docs


def nested(mapping: dict[str, Any], dotted: str) -> Any:
    current: Any = mapping
    for part in dotted.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def add(findings: list[dict[str, Any]], severity: str, check: str, message: str, file: str, recommendation: str) -> None:
    findings.append({
        "severity": severity,
        "check": check,
        "message": message,
        "file": file,
        "recommendation": recommendation,
    })


def review_deployment(doc: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    file = doc.get("__file", "unknown")
    spec = doc.get("spec", {}).get("template", {}).get("spec", {})
    pod_sc = spec.get("securityContext", {}) or {}

    if spec.get("automountServiceAccountToken") is not False:
        add(findings, "HIGH", "service-account-token", "Pod service account token is automounted.", file, "Set automountServiceAccountToken: false unless the app genuinely needs Kubernetes API access.")
    if spec.get("serviceAccountName") in {None, "", "default"}:
        add(findings, "HIGH", "service-account", "Deployment uses the default or missing service account.", file, "Use a dedicated least-privilege ServiceAccount.")
    if pod_sc.get("runAsNonRoot") is not True:
        add(findings, "HIGH", "pod-run-as-non-root", "Pod securityContext does not enforce runAsNonRoot.", file, "Set spec.template.spec.securityContext.runAsNonRoot: true.")
    if nested(pod_sc, "seccompProfile.type") != "RuntimeDefault":
        add(findings, "MEDIUM", "seccomp", "Pod seccomp profile is not RuntimeDefault.", file, "Set seccompProfile.type: RuntimeDefault.")

    containers = spec.get("containers", []) or []
    if not containers:
        add(findings, "HIGH", "containers", "Deployment has no containers.", file, "Define at least one application container.")

    for container in containers:
        name = container.get("name", "unnamed")
        image = str(container.get("image", ""))
        sc = container.get("securityContext", {}) or {}
        resources = container.get("resources", {}) or {}

        if image.endswith(":latest") or ":" not in image:
            add(findings, "HIGH", "image-tag", f"Container {name} uses a mutable or missing image tag: {image}", file, "Pin the image to a release tag or digest.")
        if sc.get("allowPrivilegeEscalation") is not False:
            add(findings, "HIGH", "privilege-escalation", f"Container {name} does not block privilege escalation.", file, "Set allowPrivilegeEscalation: false.")
        if sc.get("privileged") is not False:
            add(findings, "HIGH", "privileged", f"Container {name} does not explicitly set privileged: false.", file, "Set privileged: false.")
        if sc.get("runAsNonRoot") is not True:
            add(findings, "HIGH", "container-run-as-non-root", f"Container {name} does not enforce runAsNonRoot.", file, "Set container securityContext.runAsNonRoot: true.")
        if sc.get("readOnlyRootFilesystem") is not True:
            add(findings, "MEDIUM", "read-only-rootfs", f"Container {name} does not use a read-only root filesystem.", file, "Set readOnlyRootFilesystem: true and mount writable temp directories explicitly.")
        drops = set((sc.get("capabilities", {}) or {}).get("drop", []) or [])
        if "ALL" not in drops:
            add(findings, "HIGH", "linux-capabilities", f"Container {name} does not drop all Linux capabilities.", file, "Set capabilities.drop: [\"ALL\"].")
        for key in ["requests.cpu", "requests.memory", "limits.cpu", "limits.memory"]:
            if nested(resources, key) in {None, ""}:
                add(findings, "MEDIUM", "resources", f"Container {name} is missing resources.{key}.", file, "Set CPU and memory requests/limits.")
        for probe in ["readinessProbe", "livenessProbe", "startupProbe"]:
            if probe not in container:
                add(findings, "LOW", "health-probe", f"Container {name} is missing {probe}.", file, "Add health probes to improve rollout safety.")


def review_rbac(doc: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    file = doc.get("__file", "unknown")
    kind = doc.get("kind")
    if kind not in {"Role", "ClusterRole"}:
        return
    for rule in doc.get("rules", []) or []:
        verbs = set(rule.get("verbs", []) or [])
        resources = set(rule.get("resources", []) or [])
        if "*" in verbs:
            add(findings, "HIGH", "rbac-wildcard-verbs", f"{kind} uses wildcard verbs.", file, "Replace wildcard verbs with the minimal verb list.")
        if "*" in resources:
            add(findings, "HIGH", "rbac-wildcard-resources", f"{kind} uses wildcard resources.", file, "Replace wildcard resources with minimal resource names.")
        if {"create", "update", "patch", "delete"} & verbs:
            add(findings, "MEDIUM", "rbac-write-access", f"{kind} grants write access: {sorted(verbs)}.", file, "Confirm the workload needs write access; prefer read-only where possible.")


def review_cluster_controls(docs: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:
    kinds = {doc.get("kind") for doc in docs}
    if "NetworkPolicy" not in kinds:
        add(findings, "HIGH", "network-policy", "No NetworkPolicy found.", "k8s/", "Add default deny/allow-list NetworkPolicy for workload traffic.")
    if "PodDisruptionBudget" not in kinds:
        add(findings, "MEDIUM", "pdb", "No PodDisruptionBudget found.", "k8s/", "Add a PDB to protect availability during node drains.")
    if "HorizontalPodAutoscaler" not in kinds:
        add(findings, "LOW", "hpa", "No HorizontalPodAutoscaler found.", "k8s/", "Add HPA for scalable production-like behavior.")
    for doc in docs:
        if doc.get("kind") == "Service" and nested(doc, "spec.type") == "LoadBalancer":
            add(findings, "LOW", "load-balancer-exposure", "Service type is LoadBalancer.", doc.get("__file", "unknown"), "For production, restrict source ranges or use an ingress/WAF pattern.")
        if doc.get("kind") == "Secret" and "template" in str(doc.get("__file", "")):
            add(findings, "LOW", "secret-template", "Secret is committed only as a template.", doc.get("__file", "unknown"), "Generate real secrets from CI/CD credentials or a secrets manager.")


def score(findings: list[dict[str, Any]]) -> int:
    weights = {"HIGH": 15, "MEDIUM": 7, "LOW": 2}
    penalty = sum(weights.get(item["severity"], 1) for item in findings)
    return max(0, 100 - penalty)


def markdown(findings: list[dict[str, Any]], manifest_score: int) -> str:
    by_sev = {sev: [f for f in findings if f["severity"] == sev] for sev in ["HIGH", "MEDIUM", "LOW"]}
    lines = [
        "# Day 21 - AI Kubernetes Manifest Security Review",
        "",
        f"**Manifest security score:** {manifest_score}/100",
        "",
        "## Summary",
        "",
        f"- High findings: {len(by_sev['HIGH'])}",
        f"- Medium findings: {len(by_sev['MEDIUM'])}",
        f"- Low findings: {len(by_sev['LOW'])}",
        "",
    ]
    if not findings:
        lines.extend(["No manifest security findings were detected by the offline reviewer.", ""])
    else:
        lines.append("## Findings")
        lines.append("")
        for item in findings:
            lines.extend([
                f"### {item['severity']} - {item['check']}",
                f"- **File:** `{item['file']}`",
                f"- **Finding:** {item['message']}",
                f"- **Recommendation:** {item['recommendation']}",
                "",
            ])
    lines.extend([
        "## Reviewer note",
        "",
        "This is an AI-style deterministic review. It does not replace admission control, kube-bench, managed cloud security findings, or a human review, but it gives the pipeline a consistent manifest security decision point.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="reports/rendered-k8s")
    parser.add_argument("--config", default="config/k8s-manifest-security-policy.json")
    parser.add_argument("--json-output", default="reports/manifest-security-review.json")
    parser.add_argument("--markdown-output", default="reports/manifest-security-review.md")
    parser.add_argument("--fail-below", type=int, default=None)
    args = parser.parse_args()

    root = Path(args.path)
    findings: list[dict[str, Any]] = []
    docs = load_yaml_documents(root)
    for doc in docs:
        if doc.get("kind") == "Deployment":
            review_deployment(doc, findings)
        review_rbac(doc, findings)
    review_cluster_controls(docs, findings)
    manifest_score = score(findings)

    payload = {"score": manifest_score, "findings": findings, "documents_reviewed": len(docs)}
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(findings, manifest_score), encoding="utf-8")
    print(f"Manifest security score: {manifest_score}/100")
    threshold = args.fail_below
    if threshold is not None and manifest_score < threshold:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
