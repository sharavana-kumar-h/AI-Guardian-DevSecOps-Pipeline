#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports
EXTRA=""
if [ "${ALLOW_RDS_PLACEHOLDERS:-true}" = "true" ]; then
  EXTRA="--allow-placeholders"
fi
python3 scripts/render_rds_secret.py \
  --namespace "${K8S_NAMESPACE:-ai-devsecops}" \
  --output reports/generated-rds-secret.yaml \
  --report reports/rds-integration-report.md \
  $EXTRA
cat > reports/day-23-rds-integration-status.md <<'EOF'
# Day 23 Status

Completed RDS PostgreSQL integration support with safe Kubernetes Secret rendering and documentation.
EOF
