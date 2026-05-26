#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p reports
IMAGE="${IMAGE:-local/ai-devsecops-demo:day18}"
FAIL_TRIVY_POLICY="${FAIL_TRIVY_POLICY:-false}"
TRIVY_TIMEOUT="${TRIVY_TIMEOUT:-45s}"

{
  echo "# Day 18 - Trivy Policy Status"
  echo
  printf 'Image: `%s`
' "$IMAGE"
} > reports/day-18-trivy-policy-status.md

if command -v trivy >/dev/null 2>&1; then
  timeout "$TRIVY_TIMEOUT" trivy image --config config/trivy.yaml --format json --output reports/trivy-image.json --exit-code 0 "$IMAGE" || true
  timeout "$TRIVY_TIMEOUT" trivy image --config config/trivy.yaml --format table --output reports/trivy-image.txt --exit-code 0 "$IMAGE" || true
  echo "- Trivy scan: attempted" >> reports/day-18-trivy-policy-status.md
else
  echo '{"Results": []}' > reports/trivy-image.json
  echo "Trivy unavailable; created empty fallback scan." > reports/trivy-image.txt
  echo "- Trivy scan: fallback because trivy is unavailable" >> reports/day-18-trivy-policy-status.md
fi

EXTRA=""
if [ "$FAIL_TRIVY_POLICY" = "true" ]; then EXTRA="--fail"; fi
python3 scripts/trivy_policy_enforcer.py --input reports/trivy-image.json --policy config/container-security-policy.json $EXTRA
python3 scripts/container_risk_score.py --dockerfile Dockerfile --trivy reports/trivy-image.json || true
printf '%s
' '- Policy report: `reports/trivy-policy-result.md`' >> reports/day-18-trivy-policy-status.md
