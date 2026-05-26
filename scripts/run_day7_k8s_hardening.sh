#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
: "${IMAGE:=local/ai-devsecops-demo:day7}"

bash scripts/render_k8s_manifests.sh "$IMAGE" reports/rendered-k8s

set +e
python3 scripts/k8s_hardening_check.py --path reports/rendered-k8s --output reports/k8s-hardening-report.md
HARDENING_STATUS=$?
set -e

if command -v conftest >/dev/null 2>&1; then
  conftest test reports/rendered-k8s --policy policies --output table > reports/conftest-k8s.txt
  conftest test reports/rendered-k8s --policy policies --output json > reports/conftest-k8s.json
else
  echo "Conftest not installed; skipped OPA validation." > reports/conftest-k8s.txt
fi

if [[ "$HARDENING_STATUS" -ne 0 ]]; then
  echo "Day 7 hardening checker found review items. See reports/k8s-hardening-report.md"
  exit "$HARDENING_STATUS"
fi

echo "Day 7 Kubernetes hardening checks completed."
