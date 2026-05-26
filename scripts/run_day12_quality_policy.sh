#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "[Day 12] Applying local SonarQube SAST policy..."
python3 scripts/sonar_sast_policy.py \
  --sonar reports/sonar-findings.json \
  --config config/sonar-quality-gate.json \
  --json-output reports/sonar-policy-result.json \
  --markdown-output reports/sonar-policy-result.md \
  ${FAIL_LOCAL_SONAR_POLICY:+--fail}

echo "[Day 12] Applying cross-tool security gate in report-only mode by default..."
python3 scripts/enforce_security_gates.py --reports reports --allow-sonar-unavailable || {
  echo "[Day 12] Cross-tool gate detected violations. See reports/security-gate-result.md"
  if [ "${FAIL_SECURITY_GATES:-false}" = "true" ]; then
    exit 1
  fi
}

echo "[Day 12] Quality policy reports generated in reports/."
