#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "[Day 11] Running project-owned secure-code review rules..."
python3 scripts/secure_code_review.py \
  --root . \
  --config config/secure-code-review-rules.json \
  --json-output reports/secure-code-review.json \
  --markdown-output reports/secure-code-review.md

if command -v mvn >/dev/null 2>&1 && [ -n "${SONAR_TOKEN:-}" ]; then
  echo "[Day 11] Running Maven verify before SonarQube scan..."
  mvn -B clean verify

  echo "[Day 11] Running SonarQube scan..."
  mvn -B sonar:sonar \
    -Dsonar.projectKey="${SONAR_PROJECT_KEY:-ai-devsecops-demo}" \
    -Dsonar.host.url="${SONAR_HOST_URL:-http://localhost:9000}" \
    -Dsonar.token="${SONAR_TOKEN}"
else
  echo "[Day 11] Maven or SONAR_TOKEN unavailable. Skipping live SonarQube scan and fetching best-effort evidence."
fi

python3 scripts/fetch_sonar_report.py \
  --host-url "${SONAR_HOST_URL:-http://localhost:9000}" \
  --project-key "${SONAR_PROJECT_KEY:-ai-devsecops-demo}" \
  --output reports/sonar-findings.json \
  --markdown-output reports/sonar-evidence.md || true

python3 scripts/sonar_issue_triage.py \
  --input reports/sonar-findings.json \
  --json-output reports/sonar-issue-triage.json \
  --markdown-output reports/sonar-issue-triage.md

echo "[Day 11] Deep SAST reports generated in reports/."
