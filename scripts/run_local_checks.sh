#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

STEP_TOTAL=13

echo "[1/$STEP_TOTAL] Checking local prerequisites"
bash scripts/validate_pipeline_prereqs.sh || true

echo "[2/$STEP_TOTAL] Running baseline secret scan"
bash scripts/secret_scan.sh

echo "[3/$STEP_TOTAL] Generating AI-ready test case plan"
python3 scripts/ai_test_case_generator.py --source-root src/main/java --output reports/ai-test-plan.md

echo "[4/$STEP_TOTAL] Running Maven build, JUnit tests, and JaCoCo coverage gate"
mvn -B clean verify

echo "[5/$STEP_TOTAL] Day 3 SonarQube SAST gate"
if [ "${RUN_DAY3_SONAR:-false}" = "true" ]; then
  bash scripts/run_day3_sonar.sh
else
  echo "Skipping Day 3 SonarQube. Set RUN_DAY3_SONAR=true to execute."
fi

echo "[6/$STEP_TOTAL] Day 4 SCA and container scan"
if [ "${RUN_DAY4_SECURITY:-false}" = "true" ]; then
  bash scripts/run_day4_sca_container.sh
else
  echo "Skipping Day 4 Dependency Check/Trivy. Set RUN_DAY4_SECURITY=true to execute."
fi

echo "[7/$STEP_TOTAL] Day 5 policy-as-code checks"
if [ "${RUN_DAY5_POLICY:-false}" = "true" ]; then
  bash scripts/run_day5_policy_checks.sh
else
  bash scripts/render_k8s_manifests.sh "${IMAGE:-local/ai-devsecops-demo:dev}" reports/rendered-k8s
  echo "Skipping Conftest. Set RUN_DAY5_POLICY=true to execute policy checks."
fi

echo "[8/$STEP_TOTAL] Day 7 Kubernetes hardening review"
python3 scripts/k8s_hardening_check.py --path reports/rendered-k8s --output reports/k8s-hardening-report.md

echo "[9/$STEP_TOTAL] Optional Day 9 AWS/EKS prereq snapshot"
if [ "${RUN_DAY9_EKS_PREP:-false}" = "true" ]; then
  bash scripts/run_day9_eks_prep.sh || true
else
  echo "Skipping AWS/EKS prereq snapshot. Set RUN_DAY9_EKS_PREP=true to execute."
fi

echo "[10/$STEP_TOTAL] Optional Day 14 SBOM and dependency inventory"
if [ "${RUN_DAY14_SBOM:-false}" = "true" ]; then
  bash scripts/run_day14_sca_inventory.sh
else
  echo "Skipping Day 14 SBOM. Set RUN_DAY14_SBOM=true to execute."
fi

echo "[11/$STEP_TOTAL] Optional Day 15 dependency and license policy"
if [ "${RUN_DAY15_DEP_POLICY:-false}" = "true" ]; then
  bash scripts/run_day15_dependency_policy.sh
else
  echo "Skipping Day 15 dependency policy. Set RUN_DAY15_DEP_POLICY=true to execute."
fi

echo "[12/$STEP_TOTAL] Optional Day 16 AI dependency remediation"
if [ "${RUN_DAY16_DEP_REMEDIATION:-false}" = "true" ]; then
  bash scripts/run_day16_ai_dependency_remediation.sh
else
  echo "Skipping Day 16 dependency remediation. Set RUN_DAY16_DEP_REMEDIATION=true to execute."
fi

echo "[13/$STEP_TOTAL] Generating AI security summary"
python3 scripts/ai_cve_prioritizer.py || true
python3 scripts/container_risk_score.py --dockerfile Dockerfile --trivy reports/trivy-image.json || true
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md

echo "Local checks completed. Review:"
echo "- reports/prereq-check.md"
echo "- reports/secret-scan.txt"
echo "- reports/ai-test-plan.md"
echo "- target/site/jacoco/index.html"
echo "- reports/k8s-hardening-report.md"
echo "- reports/dependency-inventory.md (if Day 14 enabled)"
echo "- reports/sca-policy-result.md (if Day 15 enabled)"
echo "- reports/ai-dependency-remediation.md (if Day 16 enabled)"
echo "- reports/ai-security-report.md"
