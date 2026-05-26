# 90-Day Build Plan

## Days 1-10: Core CI/CD foundation and Kubernetes deployment path

- [x] Java/Maven app
- [x] JUnit tests
- [x] JaCoCo coverage gate
- [x] AI-ready test case generation
- [x] Jenkins pipeline scaffold
- [x] Dockerfile and image build
- [x] Docker Hub publishing workflow
- [x] Kubernetes manifest hardening
- [x] Local Kubernetes deployment script
- [x] AWS EKS preparation assets
- [x] EKS deployment automation
- [ ] GitHub webhook setup in actual Jenkins instance

## Days 11-22: Static and dependency security expansion

- [x] SonarQube SAST Jenkins stage
- [x] Quality Gate stage
- [x] SonarQube evidence fetcher
- [x] Deep SAST secure-code review rules
- [x] SonarQube metrics and hotspot evidence enrichment
- [x] Sonar issue triage report
- [x] Local SAST quality policy enforcement
- [x] AI remediation planning report
- [x] OWASP Dependency Check config
- [x] SBOM generation with CycloneDX-compatible output
- [x] Dependency inventory report
- [x] Dependency risk policy
- [x] License policy checks
- [x] AI dependency remediation plan
- [x] Baseline secret scanning
- [ ] Replace baseline secret scanner with Gitleaks or TruffleHog
- [x] Add GitHub Actions validation workflow
- [ ] Add GitHub branch protection notes
- [ ] Add scanner failure demo commits
- [ ] Add Gitleaks or TruffleHog replacement for baseline secret scanning

## Days 23-34: Container security depth

- [x] Dockerfile hardening
- [x] Docker image build stage
- [x] Trivy scan config and Jenkins stage
- [x] AI container risk score
- [x] AI container remediation queue
- [x] Docker Hub push automation
- [x] Maven/CycloneDX SBOM generation
- [x] Container metadata and hardening report
- [x] Trivy image policy enforcement
- [x] Container SBOM generation with Syft or Trivy SBOM
- [x] Image provenance report
- [ ] Image signing with Cosign
- [ ] Base image comparison report

## Days 35-48: Policy-as-code depth

- [x] OPA/Conftest policies
- [x] Dockerfile checks
- [x] Kubernetes manifest checks
- [x] Rendered manifest workflow
- [x] Policy recommendations in AI security report
- [x] Offline Kubernetes hardening checker
- [ ] Policy failure examples for demo
- [ ] Add policy unit tests

## Days 49-62: Kubernetes and AWS EKS hardening

- [x] EKS cluster config with eksctl
- [x] Namespace, Deployment, Service
- [x] RBAC
- [x] securityContext
- [x] rollout from Jenkins/current kube context
- [ ] Replace template secret with External Secrets or Sealed Secrets
- [ ] Add Ingress controller path or ALB controller notes
- [ ] Add namespace-level resource quota and limit range

## Days 63-70: RDS PostgreSQL

- [ ] RDS instance
- [x] Kubernetes Secret integration support
- [ ] App DB connectivity
- [ ] CRUD/history feature validation on RDS
- [x] Add RDS security group notes

## Days 71-82: AI security layer

- [x] AI vulnerability analysis report structure
- [x] AI remediation fix queue
- [x] AI CVE prioritization
- [x] AI dependency remediation queue
- [x] AI container risk score
- [x] AI policy recommendation
- [x] AI runtime report integration scaffold
- [x] AI manifest review deep-dive
- [ ] Optional LLM endpoint integration test
- [ ] Add prompt templates and output examples

## Days 83-90: Runtime analysis and portfolio polish

- [x] Runtime log/event collection scaffold
- [x] AI runtime threat summary with offline/demo logs
- [ ] AI runtime threat summary with real cluster logs
- [ ] README screenshots
- [ ] Architecture diagram image
- [ ] Demo video
- [x] Final validation report
- [ ] Final report
