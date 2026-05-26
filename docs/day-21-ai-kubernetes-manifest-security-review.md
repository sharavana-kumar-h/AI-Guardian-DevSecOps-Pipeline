# Day 21 - AI Kubernetes Manifest Security Review

## Objective

Add an AI-style Kubernetes manifest security review gate after manifest rendering and hardening.

## What was added

- `config/k8s-manifest-security-policy.json`
- `scripts/k8s_manifest_security_review.py`
- `scripts/run_day21_manifest_security_review.sh`
- `reports/manifest-security-review.md`
- `reports/manifest-security-review.json`

## Checks performed

- Image tag pinning
- Pod and container `runAsNonRoot`
- `allowPrivilegeEscalation: false`
- `privileged: false`
- `readOnlyRootFilesystem: true`
- Linux capability drop set to `ALL`
- CPU/memory requests and limits
- readiness/liveness/startup probes
- dedicated ServiceAccount
- disabled service account token automount
- seccomp profile set to `RuntimeDefault`
- NetworkPolicy, PDB, and HPA presence
- RBAC wildcard verb/resource detection

## Run

```bash
export IMAGE=local/ai-devsecops-demo:day21
bash scripts/run_day21_manifest_security_review.sh
```

## Output

```text
reports/manifest-security-review.md
reports/manifest-security-review.json
reports/ai-security-report.md
```
