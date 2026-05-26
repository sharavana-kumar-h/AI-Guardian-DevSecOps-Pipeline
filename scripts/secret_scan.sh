#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
REPORT="reports/secret-scan.txt"
: > "$REPORT"

# Lightweight baseline scanner for the first build.
# Replace this with gitleaks/trufflehog in the hardened pipeline phase.
PATTERNS=(
  'AKIA[0-9A-Z]{16}'
  '-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----'
  'ghp_[A-Za-z0-9_]{30,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'password\s*=\s*[^\s]+'
  'secret\s*=\s*[^\s]+'
)

EXIT_CODE=0
for pattern in "${PATTERNS[@]}"; do
  if grep -RInE --exclude-dir=.git --exclude-dir=target --exclude-dir=reports "$pattern" . >> "$REPORT"; then
    EXIT_CODE=1
  fi
done

if [[ "$EXIT_CODE" -ne 0 ]]; then
  echo "Potential secret detected. Review $REPORT"
  exit 1
fi

echo "No obvious secrets detected." | tee -a "$REPORT"
