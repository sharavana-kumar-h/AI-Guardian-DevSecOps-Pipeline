# Day 7 — Kubernetes Manifest Hardening

## Goal

Make the Kubernetes workload deployment safer before deploying it to any cluster.

## What changed

- Added `startupProbe`
- Added `privileged: false`
- Added stricter container and pod security context
- Added `revisionHistoryLimit`
- Added rolling update strategy
- Added topology spread constraints
- Added `PodDisruptionBudget`
- Added `HorizontalPodAutoscaler`
- Added offline Kubernetes hardening checker

## Run

```bash
export IMAGE=local/ai-devsecops-demo:day7
bash scripts/run_day7_k8s_hardening.sh
```

## Output

- `reports/rendered-k8s/`
- `reports/k8s-hardening-report.md`
- `reports/conftest-k8s.txt` if Conftest is installed

## Hardening checklist

- Non-root pod and container
- Read-only root filesystem
- No privilege escalation
- Drops all Linux capabilities
- Seccomp RuntimeDefault
- Resource requests and limits
- Probes configured
- NetworkPolicy present
- ServiceAccount token not auto-mounted
- No `latest` image tag
