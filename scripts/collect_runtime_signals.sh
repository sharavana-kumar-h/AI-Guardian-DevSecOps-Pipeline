#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-ai-devsecops}"
mkdir -p reports
{
  echo "# Kubernetes Events"
  kubectl get events -n "$NAMESPACE" --sort-by=.lastTimestamp || true
  echo
  echo "# Pods"
  kubectl get pods -n "$NAMESPACE" -o wide || true
  echo
  echo "# Recent App Logs"
  kubectl logs -n "$NAMESPACE" deploy/ai-devsecops-demo --tail=100 || true
} > reports/runtime-signals.txt

echo "Runtime signals written to reports/runtime-signals.txt"
