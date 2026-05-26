#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/rendered-k8s
IMAGE="${IMAGE:-local/ai-devsecops-demo:day21}"
bash scripts/render_k8s_manifests.sh "$IMAGE" reports/rendered-k8s
python3 scripts/k8s_manifest_security_review.py \
  --path reports/rendered-k8s \
  --config config/k8s-manifest-security-policy.json \
  --json-output reports/manifest-security-review.json \
  --markdown-output reports/manifest-security-review.md
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md
cat > reports/day-21-manifest-security-review-status.md <<'EOF'
# Day 21 Status

Completed Kubernetes manifest security review and regenerated the AI security report.
EOF
