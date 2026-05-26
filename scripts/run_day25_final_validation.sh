#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports
# Ensure deterministic offline evidence exists for final validation.
bash scripts/render_k8s_manifests.sh "${IMAGE:-local/ai-devsecops-demo:final}" reports/rendered-k8s >/dev/null
python3 scripts/k8s_hardening_check.py --path reports/rendered-k8s --output reports/k8s-hardening-report.md >/dev/null
python3 scripts/k8s_manifest_security_review.py --path reports/rendered-k8s --json-output reports/manifest-security-review.json --markdown-output reports/manifest-security-review.md >/dev/null
python3 scripts/release_readiness_check.py --output reports/release-readiness.md --json-output reports/release-readiness.json >/dev/null
python3 scripts/runtime_threat_analyzer.py --input reports/runtime-signals.txt --json-output reports/runtime-threat-summary.json --markdown-output reports/runtime-threat-summary.md >/dev/null || true
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md >/dev/null
python3 scripts/final_project_validator.py --root . --json-output reports/final-validation.json --markdown-output reports/final-validation.md
cat > reports/day-25-final-validation-status.md <<'EOF'
# Day 25 Status

Completed final offline validation and generated GitHub readiness evidence.
EOF
