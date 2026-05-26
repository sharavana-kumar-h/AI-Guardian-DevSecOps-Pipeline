# Changelog

## Days 21-25 — Manifest review, release readiness, RDS integration, runtime detection, and final validation

- Added `config/k8s-manifest-security-policy.json` and AI-style Kubernetes manifest security review.
- Added release readiness policy and evidence checker for GitHub demo packaging.
- Added RDS PostgreSQL integration support with safe Kubernetes Secret rendering and RDS reference infrastructure notes.
- Added runtime threat rule configuration and AI-style Kubernetes log/event analysis.
- Added final offline validator for required files, JSON/YAML parsing, Python compilation, shell syntax, and external tool snapshot.
- Added GitHub Actions validation workflow under `.github/workflows/validate.yml`.
- Added final submission documentation and updated README, Makefile, DAILY_LOG, and project plan.

## Days 17-20 — Container hardening, Trivy policy, image SBOM/provenance, and AI container remediation

- Added OCI image labels and build args to the Dockerfile for traceability.
- Added `config/container-security-policy.json` and `config/oci-labels.example.env`.
- Added `scripts/image_metadata_report.py` for Dockerfile/image metadata hardening evidence.
- Added `scripts/trivy_policy_enforcer.py` for local Trivy vulnerability, misconfiguration, and secret thresholds.
- Added `scripts/generate_image_sbom.sh` and `scripts/image_provenance_report.py` for image SBOM/provenance reporting.
- Added `scripts/ai_container_remediation.py` to convert container evidence into a prioritized developer fix queue.
- Added Day 17, Day 18, Day 19, and Day 20 wrapper scripts and documentation.
- Updated Jenkinsfile, Makefile, README, project plan, daily log, and AI security report integration.

## Days 14-16 — SBOM, dependency policy, license policy, and AI dependency remediation

- Added CycloneDX Maven plugin configuration for SBOM generation.
- Added `scripts/generate_sbom.sh` with fallback SBOM generation for offline demo environments.
- Added `scripts/dependency_inventory.py` to produce machine-readable and human-readable dependency inventory reports.
- Added `config/sca-risk-policy.json` and `scripts/sca_risk_policy.py` for local dependency risk policy decisions.
- Added `config/license-policy.json` and `scripts/license_policy_check.py` for license compliance evidence.
- Added `scripts/ai_dependency_remediation.py` to convert supply-chain evidence into a prioritized developer fix queue.
- Added Day 14, Day 15, and Day 16 wrapper scripts and documentation.
- Updated Jenkinsfile, Makefile, README, daily log, and AI security report integration.

## Days 11-13 — Deep SAST, local quality policy, and AI remediation planning

- Added project-owned secure-code review rules in `config/secure-code-review-rules.json`.
- Added `scripts/secure_code_review.py` for fast Java/config security checks before heavy scanners.
- Enriched SonarQube evidence collection with measures and security hotspot data.
- Added `scripts/sonar_issue_triage.py` to convert raw Sonar issues into a prioritized remediation queue.
- Added `config/sonar-quality-gate.json` and `scripts/sonar_sast_policy.py` for local SAST policy enforcement.
- Added Day 11, Day 12, and Day 13 wrapper scripts.
- Added `scripts/ai_remediation_plan.py` to generate a developer-facing remediation plan from scanner evidence.
- Updated Jenkinsfile with Day 11-13 parameters and stages.
- Updated README, daily log, project plan, and generated status reports.


## Days 6-10 — Docker publishing, Kubernetes hardening, local K8s, and EKS deployment

- Added Docker Hub publishing workflow with dry-run mode and publish evidence reports.
- Added `scripts/docker_publish.sh` and `scripts/run_day6_docker_publish.sh`.
- Hardened Kubernetes Deployment with startup probe, rolling updates, topology spread constraints, stricter security context, and limited revision history.
- Added `HorizontalPodAutoscaler` and `PodDisruptionBudget` manifests.
- Added `scripts/k8s_hardening_check.py` and `scripts/run_day7_k8s_hardening.sh`.
- Added Kind cluster config for local Kubernetes testing.
- Added local Kubernetes rollout and smoke-test automation.
- Added AWS/EKS prerequisite checker and eksctl cluster configuration.
- Added EKS cluster creation wrapper with dry-run support.
- Added Day 10 EKS deployment wrapper with kubeconfig update, workload status capture, LoadBalancer discovery, and runtime signal collection.
- Updated Jenkinsfile with Day 6, Day 7, Day 9, and Day 10 stages.
- Added daily documentation for Days 6-10 and `DAILY_LOG.md`.

## Days 3-5 — SAST, SCA, container security, and policy-as-code

- Added SonarQube SAST stage and quality gate flow in Jenkins.
- Added `scripts/fetch_sonar_report.py` for SonarQube evidence collection.
- Added OWASP Dependency Check suppression config.
- Added Trivy configuration and Jenkins image scan stage.
- Added `scripts/ai_cve_prioritizer.py` for deterministic CVE prioritization.
- Added `scripts/container_risk_score.py` for image risk scoring.
- Hardened Dockerfile with non-root UID, health check, and apt cache cleanup.
- Added stronger Dockerfile and Kubernetes Rego policies.
- Added rendered Kubernetes manifest workflow before Conftest validation.
- Added `scripts/enforce_security_gates.py` to fail builds from collected evidence.
- Expanded `scripts/ai_security_report.py` to summarize SonarQube, Dependency Check, Trivy, and Conftest evidence.
- Added Day 3, Day 4, and Day 5 documentation.
- Added Makefile and `.env.example` for local execution.

## Day 2 — Testing and coverage gate

- Added AI-ready test case generation script.
- Added Jenkins `AI Test Case Generation` stage.
- Expanded JUnit 5 test coverage for service, controller, and model layers.
- Added test profile configuration with isolated H2 database settings.
- Raised JaCoCo instruction coverage gate from 50% to 70%.
- Updated local check runner to execute secret scan, AI test-plan generation, Maven verification, and AI security summary.

## Day 1 — Initial scaffold

- Created Java Spring Boot calculator API.
- Added Maven, Dockerfile, Jenkinsfile, Kubernetes manifests, OPA policies, and security-report scaffolding.
