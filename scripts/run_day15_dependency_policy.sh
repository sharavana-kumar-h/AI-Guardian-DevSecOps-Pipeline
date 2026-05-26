#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
if [ ! -f reports/bom.json ]; then
  echo "SBOM not found. Running Day 14 inventory first."
  bash scripts/run_day14_sca_inventory.sh
fi

FAIL_ARGS=""
if [ "${FAIL_DEPENDENCY_POLICY:-false}" = "true" ] || [ "${FAIL_DEP_POLICY:-false}" = "true" ]; then
  FAIL_ARGS="--fail"
fi

python3 scripts/sca_risk_policy.py --policy config/sca-risk-policy.json --sbom reports/bom.json --json-output reports/sca-policy-result.json --markdown-output reports/sca-policy-result.md $FAIL_ARGS
python3 scripts/license_policy_check.py --policy config/license-policy.json --sbom reports/bom.json --json-output reports/license-policy-result.json --markdown-output reports/license-policy-result.md $FAIL_ARGS

cat > reports/day-15-dependency-policy-status.md <<'EOF'
# Day 15 Status

Completed dependency risk and license policy checks.

Artifacts:

- `reports/sca-policy-result.json`
- `reports/sca-policy-result.md`
- `reports/license-policy-result.json`
- `reports/license-policy-result.md`
EOF
cat reports/day-15-dependency-policy-status.md
