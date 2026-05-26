#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-${K8S_NAMESPACE:-ai-devsecops}}"
SERVICE="${2:-ai-devsecops-demo}"
LOCAL_PORT="${LOCAL_PORT:-18080}"
mkdir -p reports

kubectl -n "$NAMESPACE" get svc "$SERVICE" >/dev/null

kubectl -n "$NAMESPACE" port-forward "svc/${SERVICE}" "${LOCAL_PORT}:80" > reports/k8s-port-forward.log 2>&1 &
PF_PID=$!
trap 'kill "$PF_PID" >/dev/null 2>&1 || true' EXIT

sleep 5

{
  echo "# Kubernetes Smoke Test"
  echo
  echo "- Namespace: $NAMESPACE"
  echo "- Service: $SERVICE"
  echo "- Local URL: http://127.0.0.1:${LOCAL_PORT}"
  echo
} > reports/k8s-smoke-test.md

curl -fsS "http://127.0.0.1:${LOCAL_PORT}/actuator/health" | tee reports/k8s-health.json
curl -fsS "http://127.0.0.1:${LOCAL_PORT}/" | tee reports/k8s-root-response.txt

echo "Smoke test passed." | tee -a reports/k8s-smoke-test.md
