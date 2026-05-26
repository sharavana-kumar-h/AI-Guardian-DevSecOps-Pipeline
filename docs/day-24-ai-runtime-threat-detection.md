# Day 24 - AI Runtime Threat Detection

## Objective

Add a runtime-analysis stage that reads Kubernetes events and application logs, detects suspicious patterns, and creates an AI-style runtime threat summary.

## What was added

- `config/runtime-threat-rules.json`
- `scripts/runtime_threat_analyzer.py`
- `scripts/run_day24_runtime_threat_detection.sh`
- `reports/runtime-threat-summary.md`
- `reports/runtime-threat-summary.json`

## Signals detected

- CrashLoopBackOff
- image pull failures
- OOMKilled events
- unauthorized/forbidden/RBAC errors
- readiness/liveness/startup probe failures
- application exceptions and error logs
- HTTP 5xx patterns

## Run

```bash
export K8S_NAMESPACE=ai-devsecops
bash scripts/run_day24_runtime_threat_detection.sh
```

Strict mode:

```bash
export FAIL_ON_RUNTIME_HIGH=true
bash scripts/run_day24_runtime_threat_detection.sh
```
