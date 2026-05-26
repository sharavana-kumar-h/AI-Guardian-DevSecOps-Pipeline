#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports
EXTRA=""
if [ "${FAIL_RELEASE_READINESS:-false}" = "true" ]; then
  EXTRA="--fail"
fi
python3 scripts/release_readiness_check.py \
  --config config/release-readiness-policy.json \
  --output reports/release-readiness.md \
  --json-output reports/release-readiness.json \
  $EXTRA
cat > reports/day-22-release-readiness-status.md <<'EOF'
# Day 22 Status

Completed release readiness review for GitHub demo packaging.
EOF
