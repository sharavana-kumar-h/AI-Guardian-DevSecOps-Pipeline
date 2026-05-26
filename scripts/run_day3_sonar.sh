#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
SONAR_HOST_URL="${SONAR_HOST_URL:-http://localhost:9000}"
SONAR_PROJECT_KEY="${SONAR_PROJECT_KEY:-ai-devsecops-demo}"

cat <<MSG
Day 3: SonarQube SAST + Quality Gate
- Expected SonarQube URL: $SONAR_HOST_URL
- Project key: $SONAR_PROJECT_KEY
MSG

if [ "${START_LOCAL_SONAR:-false}" = "true" ]; then
  docker compose -f infra/local/docker-compose.yml up -d sonarqube
  echo "Local SonarQube requested. Open $SONAR_HOST_URL, finish first login, and create SONAR_TOKEN."
fi

if [ -z "${SONAR_TOKEN:-}" ] && [ -z "${SONAR_AUTH_TOKEN:-}" ]; then
  cat > reports/sonar-day3-status.md <<MSG
# Day 3 SonarQube Status

SonarQube scan not executed because SONAR_TOKEN / SONAR_AUTH_TOKEN is not set.

Run:

\`\`\`bash
export SONAR_HOST_URL=$SONAR_HOST_URL
export SONAR_TOKEN=<token-from-sonarqube>
mvn -B clean verify sonar:sonar -Dsonar.projectKey=$SONAR_PROJECT_KEY -Dsonar.host.url=$SONAR_HOST_URL -Dsonar.token=$SONAR_TOKEN
python3 scripts/fetch_sonar_report.py --host-url $SONAR_HOST_URL --project-key $SONAR_PROJECT_KEY
\`\`\`
MSG
  echo "SONAR_TOKEN is not set. Wrote reports/sonar-day3-status.md"
  exit 0
fi

TOKEN="${SONAR_TOKEN:-${SONAR_AUTH_TOKEN:-}}"
mvn -B clean verify sonar:sonar \
  -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
  -Dsonar.host.url="$SONAR_HOST_URL" \
  -Dsonar.token="$TOKEN"

python3 scripts/fetch_sonar_report.py \
  --host-url "$SONAR_HOST_URL" \
  --project-key "$SONAR_PROJECT_KEY" \
  --token "$TOKEN" \
  --output reports/sonar-findings.json \
  --markdown-output reports/sonar-evidence.md

python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md
