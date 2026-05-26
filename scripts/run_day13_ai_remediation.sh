#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "[Day 13] Refreshing AI security summary..."
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md

echo "[Day 13] Building developer remediation queue..."
python3 scripts/ai_remediation_plan.py \
  --reports reports \
  --output reports/ai-remediation-plan.md \
  --json-output reports/ai-remediation-plan.json

echo "[Day 13] Remediation plan generated: reports/ai-remediation-plan.md"
