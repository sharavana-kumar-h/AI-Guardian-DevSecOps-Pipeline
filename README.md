# AI Guardian DevSecOps Pipeline

![Status](https://img.shields.io/badge/status-day_25_complete-green)
![Security](https://img.shields.io/badge/security-DevSecOps-blue)
![Kubernetes](https://img.shields.io/badge/kubernetes-EKS_ready-blue)
![AI](https://img.shields.io/badge/AI-augmented-purple)

AI Guardian DevSecOps Pipeline is a portfolio-grade DevSecOps project that builds, tests, scans, policy-validates, containerizes, publishes, and deploys a Java Spring Boot application using an AI-assisted security reporting layer.

Current status: **Days 1–20 complete** — core application, Maven/JUnit/JaCoCo, Jenkins, SonarQube workflow, OWASP Dependency Check, Trivy, OPA/Conftest, Docker Hub publishing workflow, Kubernetes hardening, local Kubernetes deployment, AWS EKS automation, deep SAST review, local quality policy enforcement, AI remediation planning, SBOM generation, dependency/license policy checks, AI dependency remediation, container image hardening, Trivy policy enforcement, image SBOM/provenance, and AI container remediation are implemented.

## What this project demonstrates

- CI/CD automation with Jenkins Declarative Pipeline
- Shift-left security gates
- Unit testing and coverage enforcement
- SAST with SonarQube
- SCA with OWASP Dependency Check
- Container scanning with Trivy
- Policy-as-code with OPA/Conftest
- Docker image publishing to Docker Hub
- Hardened Kubernetes manifests
- Local Kubernetes validation
- AWS EKS deployment path
- AI-assisted vulnerability, CVE, dependency, license, container-risk, policy, remediation, and runtime summaries
- SBOM generation with CycloneDX-compatible output
- Container image metadata, provenance, and remediation evidence

## Architecture

```text
Developer Commit
      |
      v
GitHub Repository
      |
      v
Jenkins Pipeline
      |
      v
Secret Scan -> Maven Build -> JUnit -> JaCoCo
      |
      v
SonarQube SAST -> AI Vulnerability Summary
      |
      v
OWASP Dependency Check -> SBOM -> Dependency/License Policy -> AI Dependency Remediation
      |
      v
Docker Build -> Image Metadata -> Trivy Scan -> Trivy Policy -> Image SBOM/Provenance -> AI Container Remediation
      |
      v
OPA/Conftest -> Kubernetes Hardening Review
      |
      v
Docker Hub Publish
      |
      v
Local Kubernetes / AWS EKS Deployment
      |
      v
Runtime Signals -> AI Runtime Security Summary
      |
      v
AI Remediation Plan
```

## Repository structure

```text
.
├── Jenkinsfile
├── Dockerfile
├── Makefile
├── pom.xml
├── README.md
├── DAILY_LOG.md
├── PROJECT_PLAN_90_DAYS.md
├── src/
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.template.yaml
│   ├── rbac.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── network-policy.yaml
│   ├── hpa.yaml
│   └── pdb.yaml
├── policies/
│   ├── dockerfile.rego
│   └── kubernetes.rego
├── scripts/
│   ├── run_local_checks.sh
│   ├── run_day3_sonar.sh
│   ├── run_day4_sca_container.sh
│   ├── run_day5_policy_checks.sh
│   ├── run_day6_docker_publish.sh
│   ├── run_day7_k8s_hardening.sh
│   ├── run_day8_local_k8s.sh
│   ├── run_day9_eks_prep.sh
│   ├── run_day10_eks_deploy.sh
│   ├── run_day11_sast_deep_scan.sh
│   ├── run_day12_quality_policy.sh
│   ├── run_day13_ai_remediation.sh
│   ├── run_day14_sca_inventory.sh
│   ├── run_day15_dependency_policy.sh
│   ├── run_day16_ai_dependency_remediation.sh
│   ├── run_day17_container_hardening.sh
│   ├── run_day18_trivy_policy.sh
│   ├── run_day19_image_sbom_provenance.sh
│   ├── run_day20_ai_container_remediation.sh
│   ├── run_day21_manifest_security_review.sh
│   ├── run_day22_release_readiness.sh
│   ├── run_day23_rds_integration.sh
│   ├── run_day24_runtime_threat_detection.sh
│   ├── run_day25_final_validation.sh
│   └── *.py / helper scripts
├── infra/
│   ├── kind/kind-cluster.yaml
│   └── eks/cluster.yaml
├── config/
├── docs/
└── reports/
```

## Prerequisites

Base tools:

```bash
java --version
mvn --version
python3 --version
docker --version
```

Security/Kubernetes/cloud tools for later stages:

```bash
trivy --version
conftest --version
kubectl version --client
kind version
aws --version
eksctl version
```

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/ai-guardian-devsecops-pipeline.git
cd ai-guardian-devsecops-pipeline
mvn -B clean verify
mvn spring-boot:run
```

Test API:

```bash
curl http://localhost:8080/
curl -X POST http://localhost:8080/api/calculator \
  -H 'Content-Type: application/json' \
  -d '{"operation":"add","a":10,"b":5}'
```

## Run baseline local checks

```bash
bash scripts/run_local_checks.sh
```

This runs secret scan, AI test plan generation, Maven tests, JaCoCo, and AI summary generation. Heavy external gates are opt-in.

## Day-by-day commands

### Day 3 — SonarQube SAST

```bash
export SONAR_HOST_URL=http://localhost:9000
export SONAR_PROJECT_KEY=ai-devsecops-demo
export SONAR_TOKEN=<your-token>
bash scripts/run_day3_sonar.sh
```

### Day 4 — SCA and container security

```bash
export IMAGE=local/ai-devsecops-demo:day4
bash scripts/run_day4_sca_container.sh
```

### Day 5 — OPA/Conftest policy checks

```bash
export IMAGE=local/ai-devsecops-demo:day5
bash scripts/run_day5_policy_checks.sh
```

### Day 6 — Docker Hub publishing

Dry run:

```bash
export IMAGE=your-dockerhub-user/ai-devsecops-demo:day6
export DRY_RUN=true
bash scripts/run_day6_docker_publish.sh
```

Real push:

```bash
export IMAGE=your-dockerhub-user/ai-devsecops-demo:day6
export DOCKER_USER=your-dockerhub-user
export DOCKER_PASS=your-dockerhub-token
export DRY_RUN=false
bash scripts/run_day6_docker_publish.sh
```

### Day 7 — Kubernetes hardening

```bash
export IMAGE=local/ai-devsecops-demo:day7
bash scripts/run_day7_k8s_hardening.sh
```

### Day 8 — Local Kubernetes deployment

Kind example:

```bash
kind create cluster --config infra/kind/kind-cluster.yaml
export IMAGE=local/ai-devsecops-demo:day8
bash scripts/run_day8_local_k8s.sh
```

### Day 9 — AWS EKS preparation

```bash
export AWS_REGION=ap-south-1
export EKS_CLUSTER_NAME=ai-devsecops-eks
bash scripts/run_day9_eks_prep.sh
```

### Day 10 — AWS EKS deployment

The image must already be pushed to Docker Hub.

```bash
export AWS_REGION=ap-south-1
export EKS_CLUSTER_NAME=ai-devsecops-eks
export IMAGE=your-dockerhub-user/ai-devsecops-demo:day10
bash scripts/run_day10_eks_deploy.sh
```


### Day 11 — Deep SAST review

This runs project-owned secure-code review rules, refreshes SonarQube evidence, and triages Sonar issues into a developer queue.

```bash
export SONAR_HOST_URL=http://localhost:9000
export SONAR_PROJECT_KEY=ai-devsecops-demo
export SONAR_TOKEN=<your-token>
bash scripts/run_day11_sast_deep_scan.sh
```

The script still produces best-effort reports if SonarQube is unavailable.

### Day 12 — Local SAST quality policy

```bash
bash scripts/run_day12_quality_policy.sh
```

Strict failure mode:

```bash
export FAIL_LOCAL_SONAR_POLICY=1
export FAIL_SECURITY_GATES=true
bash scripts/run_day12_quality_policy.sh
```

### Day 13 — AI remediation plan

```bash
bash scripts/run_day13_ai_remediation.sh
```

### Day 14 — SBOM and dependency inventory

```bash
bash scripts/run_day14_sca_inventory.sh
```

This generates `reports/bom.json`, `reports/dependency-inventory.json`, and `reports/dependency-inventory.md`.

### Day 15 — Dependency risk and license policy

```bash
bash scripts/run_day15_dependency_policy.sh
```

Strict failure mode:

```bash
export FAIL_DEP_POLICY=true
bash scripts/run_day15_dependency_policy.sh
```

### Day 16 — AI dependency remediation

```bash
bash scripts/run_day16_ai_dependency_remediation.sh
```

This creates a prioritized supply-chain remediation queue from SBOM, SCA, and license evidence.

### Day 17 — Container image hardening and metadata

```bash
export IMAGE=local/ai-devsecops-demo:day17
bash scripts/run_day17_container_hardening.sh
```

This creates `reports/image-metadata.md` and validates Dockerfile/image hardening signals such as non-root user, healthcheck, OCI labels, and mutable tag usage.

### Day 18 — Trivy image policy enforcement

```bash
export IMAGE=local/ai-devsecops-demo:day18
bash scripts/run_day18_trivy_policy.sh
```

Strict failure mode:

```bash
export FAIL_TRIVY_POLICY=true
bash scripts/run_day18_trivy_policy.sh
```

This creates `reports/trivy-policy-result.md` from `config/container-security-policy.json`.

### Day 19 — Image SBOM and provenance

```bash
export IMAGE=local/ai-devsecops-demo:day19
bash scripts/run_day19_image_sbom_provenance.sh
```

This creates `reports/image-sbom.cdx.json` and `reports/image-provenance.md`. Trivy or Syft is used when available; otherwise a minimal fallback SBOM is created for workflow continuity.

### Day 20 — AI container remediation

```bash
export IMAGE=local/ai-devsecops-demo:day20
bash scripts/run_day20_ai_container_remediation.sh
```

This creates `reports/ai-container-remediation.md`, a prioritized fix queue for image vulnerabilities, metadata issues, and provenance gaps.


## Jenkins parameters

| Parameter | Purpose |
|---|---|
| `ENABLE_SONAR` | Run SonarQube SAST and quality gate |
| `ENABLE_DEP_CHECK` | Run OWASP Dependency Check |
| `ENABLE_DOCKER` | Build Docker image |
| `ENABLE_TRIVY` | Scan Docker image with Trivy |
| `ENABLE_OPA` | Run OPA/Conftest checks |
| `ENFORCE_SECURITY_GATES` | Fail build using collected security evidence |
| `ENABLE_DOCKER_PUSH` | Push image to Docker Hub |
| `PUSH_LATEST` | Also push a `latest` tag; normally keep false |
| `ENABLE_K8S_DEPLOY` | Deploy to current Kubernetes context or EKS |
| `ENABLE_EKS_KUBECONFIG` | Run `aws eks update-kubeconfig` before deploy |
| `ENABLE_DEEP_SAST` | Run Day 11 secure-code review and Sonar issue triage |
| `ENABLE_LOCAL_SONAR_POLICY` | Run Day 12 local SAST quality policy |
| `FAIL_LOCAL_SONAR_POLICY` | Fail the build if the local SAST policy fails |
| `ENABLE_AI_REMEDIATION_PLAN` | Generate Day 13 developer remediation plan |
| `ENABLE_SBOM` | Generate Day 14 SBOM and dependency inventory |
| `ENABLE_DEP_POLICY` | Run Day 15 dependency and license policies |
| `FAIL_DEP_POLICY` | Fail build if dependency or license policy fails |
| `ENABLE_AI_DEP_REMEDIATION` | Generate Day 16 dependency remediation plan |
| `ENABLE_CONTAINER_HARDENING` | Run Day 17 image metadata and hardening report |
| `ENABLE_TRIVY_POLICY` | Run Day 18 Trivy policy enforcement |
| `FAIL_TRIVY_POLICY` | Fail build if Trivy policy fails |
| `ENABLE_IMAGE_SBOM` | Generate Day 19 image SBOM and provenance report |
| `ENABLE_AI_CONTAINER_REMEDIATION` | Generate Day 20 container remediation queue |
| `AWS_REGION` | EKS region |
| `EKS_CLUSTER_NAME` | EKS cluster name |

## Security gates

| Gate | Tool |
|---|---|
| Secret detection | `scripts/secret_scan.sh` |
| Unit test gate | JUnit |
| Coverage gate | JaCoCo |
| SAST | SonarQube |
| SCA | OWASP Dependency Check |
| Image scan | Trivy |
| Dockerfile policy | OPA/Conftest |
| Kubernetes policy | OPA/Conftest |
| Kubernetes hardening review | `scripts/k8s_hardening_check.py` |
| Secure code review | `scripts/secure_code_review.py` |
| Local SAST policy | `scripts/sonar_sast_policy.py` |
| SBOM generation | CycloneDX Maven plugin + `scripts/generate_sbom.sh` |
| Dependency risk policy | `scripts/sca_risk_policy.py` |
| License policy | `scripts/license_policy_check.py` |
| AI remediation queue | `scripts/ai_remediation_plan.py` |
| AI dependency remediation queue | `scripts/ai_dependency_remediation.py` |
| Container metadata review | `scripts/image_metadata_report.py` |
| Trivy policy enforcement | `scripts/trivy_policy_enforcer.py` |
| Image SBOM generation | `scripts/generate_image_sbom.sh` |
| Image provenance | `scripts/image_provenance_report.py` |
| AI container remediation queue | `scripts/ai_container_remediation.py` |
| Risk summary | AI report scripts |

## Generated reports

Common outputs:

```text
reports/secret-scan.txt
reports/ai-test-plan.md
reports/sonar-evidence.md
reports/secure-code-review.md
reports/sonar-issue-triage.md
reports/sonar-policy-result.md
reports/ai-remediation-plan.md
reports/bom.json
reports/dependency-inventory.md
reports/sca-policy-result.md
reports/license-policy-result.md
reports/ai-dependency-remediation.md
reports/image-metadata.md
reports/trivy-policy-result.md
reports/image-sbom.cdx.json
reports/image-provenance.md
reports/ai-container-remediation.md
reports/ai-cve-priorities.md
reports/ai-container-risk.md
reports/conftest-k8s.txt
reports/k8s-hardening-report.md
reports/docker-publish-report.md
reports/k8s-smoke-test.md
reports/aws-eks-prereq-check.md
reports/day-10-eks-deploy.md
reports/ai-security-report.md
```

## Daily work log

See [`DAILY_LOG.md`](DAILY_LOG.md) for the day-by-day implementation record and recommended commit messages.

## Cost warning

AWS EKS and LoadBalancers can create real charges. Delete the cluster when finished:

```bash
eksctl delete cluster --name ai-devsecops-eks --region ap-south-1
```

## Project status

Days 1–25 are implemented as runnable project assets. Full execution of Docker Hub push, live SonarQube scans, Trivy/Syft full image SBOM generation, Kubernetes deployment, RDS integration, and EKS deployment requires your Docker Hub credentials, SonarQube token, AWS credentials, local tool installation, and an AWS account with sufficient permissions.


### Day 21 — AI Kubernetes manifest security review

```bash
export IMAGE=local/ai-devsecops-demo:day21
bash scripts/run_day21_manifest_security_review.sh
```

### Day 22 — Release readiness

```bash
bash scripts/run_day22_release_readiness.sh
```

### Day 23 — RDS PostgreSQL integration

```bash
export ALLOW_RDS_PLACEHOLDERS=true
bash scripts/run_day23_rds_integration.sh
```

### Day 24 — AI runtime threat detection

```bash
export K8S_NAMESPACE=ai-devsecops
bash scripts/run_day24_runtime_threat_detection.sh
```

