# Day 5 — AI Container Risk Scoring, OPA/Conftest Dockerfile Policy, and AI Policy Recommendations

## Goal

Prevent unsafe Dockerfile and Kubernetes configuration from reaching deployment.

## What was added

- `Day 5 - Render Kubernetes Manifests` Jenkins stage
- `Day 5 - OPA/Conftest Policy Checks` Jenkins stage
- Stronger Dockerfile policies in `policies/dockerfile.rego`
- Stronger Kubernetes policies in `policies/kubernetes.rego`
- `scripts/render_k8s_manifests.sh`
- `scripts/run_day5_policy_checks.sh`
- `scripts/enforce_security_gates.py`
- AI security report policy recommendation section

## Policies enforced

Dockerfile:

- No `latest` base image tag
- Must define non-root `USER`
- `USER` must not be root
- `apt-get install` must use `--no-install-recommends`
- apt package cache must be removed
- Must define `HEALTHCHECK`

Kubernetes:

- `runAsNonRoot=true`
- `automountServiceAccountToken=false`
- `seccompProfile=RuntimeDefault`
- CPU and memory requests/limits required
- `allowPrivilegeEscalation=false`
- No privileged containers
- `readOnlyRootFilesystem=true`
- Drop all Linux capabilities
- No `latest` image tag
- Readiness and liveness probes required
- No `hostPath` volumes

## Local run

```bash
export IMAGE=local/ai-devsecops-demo:day5
bash scripts/run_day5_policy_checks.sh
```

Expected reports:

- `reports/rendered-k8s/*.yaml`
- `reports/conftest-dockerfile.json`
- `reports/conftest-dockerfile.txt`
- `reports/conftest-k8s.json`
- `reports/conftest-k8s.txt`
- `reports/ai-container-risk.md`
- `reports/ai-security-report.md`

## Interview explanation

“OPA/Conftest acts as a deterministic policy gate. The AI layer reviews policy failures and recommends missing guardrails, but the final pass/fail decision remains code-defined and auditable.”
