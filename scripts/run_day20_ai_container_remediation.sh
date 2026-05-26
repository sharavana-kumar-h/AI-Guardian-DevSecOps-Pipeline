#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p reports
IMAGE="${IMAGE:-local/ai-devsecops-demo:day20}"

# Best-effort generation of prerequisite reports.
if [ ! -f reports/trivy-policy-result.json ]; then
  FAIL_TRIVY_POLICY=false IMAGE="$IMAGE" bash scripts/run_day18_trivy_policy.sh || true
fi
if [ ! -f reports/image-provenance.json ]; then
  IMAGE="$IMAGE" bash scripts/run_day19_image_sbom_provenance.sh || true
fi

python3 scripts/ai_container_remediation.py --reports reports --json-output reports/ai-container-remediation.json --markdown-output reports/ai-container-remediation.md
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md || true

{
  echo "# Day 20 - AI Container Remediation Status"
  echo
  printf 'Image: `%s`
' "$IMAGE"
  echo
  echo "Generated:"
  echo
  echo "- \`reports/ai-container-remediation.md\`"
  echo "- \`reports/ai-container-remediation.json\`"
  echo "- \`reports/ai-security-report.md\`"
} > reports/day-20-ai-container-remediation-status.md
