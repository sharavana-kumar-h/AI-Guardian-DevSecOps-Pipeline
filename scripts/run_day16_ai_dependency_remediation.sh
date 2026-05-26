#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
if [ ! -f reports/dependency-inventory.json ]; then
  bash scripts/run_day14_sca_inventory.sh
fi
if [ ! -f reports/sca-policy-result.json ] || [ ! -f reports/license-policy-result.json ]; then
  bash scripts/run_day15_dependency_policy.sh
fi

python3 scripts/ai_dependency_remediation.py \
  --sca reports/sca-policy-result.json \
  --license reports/license-policy-result.json \
  --inventory reports/dependency-inventory.json \
  --json-output reports/ai-dependency-remediation.json \
  --markdown-output reports/ai-dependency-remediation.md

python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md

cat > reports/day-16-ai-dependency-remediation-status.md <<'EOF'
# Day 16 Status

Completed AI dependency remediation planning.

Artifacts:

- `reports/ai-dependency-remediation.json`
- `reports/ai-dependency-remediation.md`
- `reports/ai-security-report.md`
EOF
cat reports/day-16-ai-dependency-remediation-status.md
