#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
IMAGE="${IMAGE:-local/ai-devsecops-demo:day4}"
STRICT_TOOLS="${STRICT_TOOLS:-false}"

echo "Day 4: OWASP Dependency Check + Docker build + Trivy scan"

echo "[1/4] Running OWASP Dependency Check"
mvn -B org.owasp:dependency-check-maven:check -Dformat=ALL -DfailBuildOnCVSS="${FAIL_BUILD_ON_CVSS:-8}"

echo "[2/4] Building Docker image: $IMAGE"
if command -v docker >/dev/null 2>&1; then
  docker build -t "$IMAGE" .
else
  echo "docker is missing. Skipping image build."
  [ "$STRICT_TOOLS" = "true" ] && exit 1
fi

echo "[3/4] Running Trivy image scan"
if command -v trivy >/dev/null 2>&1 && command -v docker >/dev/null 2>&1; then
  trivy image --config config/trivy.yaml --format json --output reports/trivy-image.json "$IMAGE" || true
  trivy image --config config/trivy.yaml --format table --output reports/trivy-image.txt "$IMAGE" || true
else
  echo '{"Results": []}' > reports/trivy-image.json
  echo "Trivy or Docker is missing. Wrote empty reports/trivy-image.json placeholder."
  [ "$STRICT_TOOLS" = "true" ] && exit 1
fi

echo "[4/4] Prioritizing CVEs"
python3 scripts/ai_cve_prioritizer.py
python3 scripts/container_risk_score.py --dockerfile Dockerfile --trivy reports/trivy-image.json
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md
