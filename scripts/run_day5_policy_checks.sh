#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
IMAGE="${IMAGE:-local/ai-devsecops-demo:day5}"
STRICT_TOOLS="${STRICT_TOOLS:-false}"

echo "Day 5: OPA/Conftest policy-as-code + AI policy recommendation"

bash scripts/render_k8s_manifests.sh "$IMAGE" reports/rendered-k8s

if command -v conftest >/dev/null 2>&1; then
  echo "[1/3] Dockerfile policy checks"
  conftest test Dockerfile --policy policies --output json > reports/conftest-dockerfile.json
  conftest test Dockerfile --policy policies --output table > reports/conftest-dockerfile.txt

  echo "[2/3] Kubernetes manifest policy checks"
  conftest test reports/rendered-k8s --policy policies --output json > reports/conftest-k8s.json
  conftest test reports/rendered-k8s --policy policies --output table > reports/conftest-k8s.txt
else
  echo '[]' > reports/conftest-dockerfile.json
  echo '[]' > reports/conftest-k8s.json
  echo "Conftest is missing. Wrote empty conftest placeholders."
  [ "$STRICT_TOOLS" = "true" ] && exit 1
fi

echo "[3/3] Generating AI security report"
python3 scripts/container_risk_score.py --dockerfile Dockerfile --trivy reports/trivy-image.json
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md
