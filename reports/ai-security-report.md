# AI-Assisted Security Report

## Executive Risk Rating

**LOW**

Blocker summary: No hard blocker identified from available evidence.

## Evidence Summary

| Signal | Result |
|---|---:|
| SonarQube quality gate | UNKNOWN |
| SonarQube blocker issues | 0 |
| SonarQube critical issues | 0 |
| SonarQube major issues returned | 0 |
| Trivy critical CVEs | 0 |
| Trivy high CVEs | 0 |
| Trivy medium CVEs | 0 |
| OWASP Dependency Check critical/high findings | 0 |
| Vulnerable dependencies | 0 |
| SCA policy decision | PASS_WITH_WARNINGS |
| License policy decision | PASS_WITH_WARNINGS |
| Trivy image policy decision | PASS |
| Container metadata findings | 2 |
| Container metadata high/critical findings | 0 |
| Manifest security score | 96 |
| Runtime threat score | 100 |
| Release readiness decision | PASS |
| Dockerfile policy failures | 0 |
| Kubernetes policy failures | 0 |
| Secure-code critical findings | 0 |
| Secure-code high findings | 0 |

## Prioritized Remediation

1. Revoke and rotate any exposed secret before continuing the pipeline.
2. Fix SonarQube blocker/critical findings and pass the quality gate.
3. Patch critical/high dependency and container CVEs before pushing the image.
4. Fix OPA/Conftest policy failures before deployment.
5. Re-run all scans, archive evidence, and review runtime signals after deployment.

## Secure Code Review

# Secure Code Review Report

Generated: `2026-05-05T16:04:10.856103+00:00`

## Severity Summary

| Severity | Count |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| INFO | 0 |

No findings from project-owned secure-code review rules.


## Local Sonar Policy

# SonarQube Local SAST Policy Result

Status: **WARNING**

## Facts

| Check | Value |
|---|---:|
| generated_at | `2026-05-05T16:04:38.364679+00:00` |
| policy_name | `AI Guardian SonarQube Local Security Gate` |
| sonar_available | `False` |
| sonar_error | `<urlopen error [Errno 111] Connection refused>` |

No local SAST policy violations were detected.


## AI CVE Prioritization

# AI CVE Prioritization Report

This report ranks scanner findings by severity, deployability impact, and fix availability.

Total findings: **0** | Critical: **0** | High: **0**

No Dependency Check or Trivy findings were available. Run Day 4 scans first.


## Dependency Inventory and SBOM

# Day 14 Dependency Inventory and SBOM Summary

Generated: 2026-05-05T16:20:00.371887+00:00

## SBOM Status

- Status: **available**
- Path: `reports/bom.json`
- Format: `CycloneDX`
- Spec version: `1.5`
- Components discovered from SBOM: **7**
- Direct dependencies from `pom.xml`: **7**

## Dependency Scope Counts

- **compile**: 4
- **required**: 4
- **runtime**: 4
- **test**: 2

## Direct Maven Dependencies

| Dependency | Version | Scope |
|---|---:|---|
| `org.springframework.boot:spring-boot-starter-web` | `managed-by-parent-or-bom` | `compile` |
| `org.springframework.boot:spring-boot-starter-actuator` | `managed-by-parent-or-bom` | `compile` |
| `org.springframework.boot:spring-boot-starter-data-jpa` | `managed-by-parent-or-bom` | `compile` |
| `org.springframework.boot:spring-boot-starter-validation` | `managed-by-parent-or-bom` | `compile` |
| `org.postgresql:postgresql` | `managed-by-parent-or-bom` | `runtime` |
| `com.h2database:h2` | `managed-by-parent-or-bom` | `runtime` |
| `org.springframework.boot:spring-boot-starter-test` | `managed-by-parent-or-bom` | `test` |

## First 25 SBOM Components

| Component | Version | Scope |
|---|---:|---|
| `org.springframework.boot:spring-boot-starter-web` | `managed-by-parent-or-bom` | `required` |
| `org.springframework.boot:spring-boot-starter-actuator` | `managed-by-parent-or-bom` | `required` |
| `org.springframework.boot:spring-boot-starter-data-jpa` | `managed-by-parent-or-bom` | `required` |
| `org.springframework.boot:spring-boot-starter-validation` | `managed-by-parent-or-bom` | `required` |
| `org.postgresql:postgresql` | `managed-by-parent-or-bom` | `runtime` |
| `com.h2database:h2` | `managed-by-parent-or-bom` | `runtime` |
| `org.springframework.boot:spring-boot-starter-test` | `managed-by-parent-or-bom` | `test` |

## Supply-Chain Notes

1. Archive the SBOM with every Jenkins build so later vulnerability investigations can identify exactly what shipped.
2. Treat direct dependencies as the fastest patch path; transitive dependency fixes may require parent upgrades or exclusions.
3. Regenerate the SBOM after every dependency or base-image change.
4. Use this inventory as input for the Day 15 dependency and license policy checks.


## Dependency Risk Policy

# Day 15 SCA Risk Policy Result

Generated: 2026-05-05T16:20:05.646206+00:00

## Decision

**PASS_WITH_WARNINGS**

## Vulnerability Counts

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Unknown | 0 |

## SBOM Status

- SBOM required: **True**
- SBOM path: `reports/bom.json`
- SBOM component count: **7**
- Dependency Check report: `None`

## Failures

- None

## Warnings

- Dependency Check report not found; policy evaluated SBOM presence only.

## Highest Priority Findings

| Dependency | Finding | Severity | CVSS |
|---|---|---:|---:|
| _No Dependency Check vulnerabilities available_ | - | - | - |

## Recommended Actions

1. Upgrade direct dependencies first because they are controlled by the application team.
2. Prefer patched minor versions before major upgrades to reduce regression risk.
3. Use suppression files only for false positives with expiry dates and justification.
4. Regenerate the SBOM after every dependency change and archive it with the build.


## License Policy

# Day 15 License Policy Result

Generated: 2026-05-05T16:20:10.765492+00:00

## Decision

**PASS_WITH_WARNINGS**

## Counts

| Signal | Count |
|---|---:|
| SBOM components | 7 |
| Allowed license components | 0 |
| Denied license components | 0 |
| Warning license components | 0 |
| Unknown license components | 7 |

## Failures

- None

## Denied Licenses

- None

## Warning Licenses

- None

## Unknown Licenses

- `org.springframework.boot:spring-boot-starter-web:managed-by-parent-or-bom`
- `org.springframework.boot:spring-boot-starter-actuator:managed-by-parent-or-bom`
- `org.springframework.boot:spring-boot-starter-data-jpa:managed-by-parent-or-bom`
- `org.springframework.boot:spring-boot-starter-validation:managed-by-parent-or-bom`
- `org.postgresql:postgresql:managed-by-parent-or-bom`
- `com.h2database:h2:managed-by-parent-or-bom`
- `org.springframework.boot:spring-boot-starter-test:managed-by-parent-or-bom`

## Notes

Missing license metadata is common in fallback SBOM mode. For stricter evidence, run the CycloneDX Maven plugin and archive the generated `target/bom.json`.


## AI Dependency Remediation

# Day 16 AI Dependency Remediation Plan

Generated: 2026-05-05T16:20:44.145530+00:00

## Executive Summary

- Total actions: **2**
- P0/P1 actions: **0**
- Recommended deploy decision: **ALLOW after standard validation**

## Remediation Queue

| Priority | Category | Target | Finding | Recommended Fix |
|---|---|---|---|---|
| P2 | License Metadata | `7 component(s)` | Missing license metadata | Generate a full CycloneDX SBOM with Maven instead of relying on fallback SBOM mode. |
| P3 | SBOM Quality | `Dependency graph completeness` | SBOM appears to contain direct dependencies only | Ensure CycloneDX Maven plugin runs successfully and includes runtime/compile scopes. |

## Validation Commands

- `bash scripts/run_day14_sca_inventory.sh`
- `jq '.components | length' reports/bom.json`

## Operating Rules

1. Patch direct dependencies first.
2. Do not suppress dependency findings unless they are proven false positives.
3. Every suppression should include a reason, owner, and expiry date.
4. Regenerate SBOM and rerun SCA after each dependency change.
5. Archive SBOM, Dependency Check report, license report, and this plan as build artifacts.


## AI Container Risk

# AI Container Risk Score

| Metric | Value |
|---|---:|
| Risk rating | **LOW** |
| Score | **100/100** |
| Critical CVEs | 0 |
| High CVEs | 0 |
| Medium CVEs | 0 |
| Non-root USER | True |
| Avoids latest tag | True |
| Multi-stage build | True |
| Healthcheck present | True |

Base images: `maven:3.9.11-eclipse-temurin-21, eclipse-temurin:21-jre-jammy`

## Recommendation

- Do not push or deploy when the rating is HIGH or CRITICAL.
- Patch critical/high CVEs or switch to a cleaner base image.
- Keep non-root execution, health checks, and multi-stage builds enabled.


## Trivy Image Policy

# Day 18 - Trivy Container Security Policy Result

Generated: `2026-05-05T16:42:22Z`
Input: `reports/trivy-image.json`
Decision: **PASS**

## Counts
### Vulnerabilities
| Severity | Count |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| UNKNOWN | 0 |

### Misconfigurations
| Severity | Count |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| UNKNOWN | 0 |

### Secrets
| Severity | Count |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| UNKNOWN | 0 |

## Violations
No policy threshold violations detected.

## Top examples


## Container Image Metadata

# Day 17 - Container Image Metadata and Hardening Report

Generated: `2026-05-05T16:43:12Z`
Image: `local/test:day19`

## Dockerfile summary
- Dockerfile exists: **True**
- Base images: maven:3.9.11-eclipse-temurin-21, eclipse-temurin:21-jre-jammy
- Runtime user: `appuser`
- Healthcheck: **True**
- Exposed ports: 8080

## Docker image inspect
- Inspect unavailable: docker CLI is not installed

## Findings
| Severity | ID | Finding | Recommendation |
|---|---|---|---|
| LOW | IMG005 | Runtime image installs OS packages — ca-certificates, curl | Keep runtime packages minimal; remove package managers where possible or consider a distroless runtime. |
| INFO | IMG007 | Image digest not captured — No digest file or RepoDigest detected | Capture the registry digest after push for deployment traceability. |

## Decision
- Status: **PASS**


## Image Provenance

# Day 19 - Image Provenance and Traceability Report

Generated: `2026-05-05T16:43:21Z`
Image: `local/test:day19`

## Source traceability
- Git commit: `unavailable`
- Git branch: `unavailable`
- Working tree dirty: **False**

## Artifact hashes
| Artifact | SHA-256 |
|---|---|
| Dockerfile | `0365b40665db4a1f442d19b82d007ade22aacce7db5a83dc0de619b3fa3db141` |
| pom.xml | `81943d2e4dae418024397f814a4619c0765bf47e63f48d61ec651dc2abee437e` |
| Jenkinsfile | `3a3e5d97fba73f9ad0ef2fee4d68abd95d906028e7592d4a728757cf4c3d06ac` |
| application_sbom | `0617f8e7de58a03148d745bd8a53bcb94a9f3645c03ba140ac270e3adc4f589f` |
| image_sbom | `079e854157079293ccbc65b8016ff6f82ef3b71ff29dc646bdbd48fadc52bfdc` |

## Image metadata
- Metadata findings: **2**
- High/critical metadata findings: **0**
- Inspect unavailable: docker CLI is not installed

## SBOM
- SBOM path: `reports/image-sbom.cdx.json`
- SBOM hash: `079e854157079293ccbc65b8016ff6f82ef3b71ff29dc646bdbd48fadc52bfdc`
- SBOM format: `CycloneDX`

## Decision
**PASS** — Source and build evidence files are present.


## AI Container Remediation

# Day 20 - AI Container Remediation Queue

Generated: `2026-05-05T16:44:06Z`

This report converts image-scan, image-metadata, and provenance evidence into a practical container fix queue.

## Prioritized tasks
| Priority | Severity | Task | Evidence | Recommended action | Source |
|---:|---|---|---|---|---|
| 1 | LOW | Runtime image installs OS packages | ca-certificates, curl | Keep runtime packages minimal; remove package managers where possible or consider a distroless runtime. | `image-metadata.json` |
| 2 | INFO | Image digest not captured | No digest file or RepoDigest detected | Capture the registry digest after push for deployment traceability. | `image-metadata.json` |

## Suggested Day 20 demo
1. Run Trivy and policy enforcement.
2. Show a failing threshold or metadata warning.
3. Open this remediation queue and explain the first three fixes.
4. Rebuild the image and rerun the policy to show improvement.


## Kubernetes Manifest Security Review

# Day 21 - AI Kubernetes Manifest Security Review

**Manifest security score:** 96/100

## Summary

- High findings: 0
- Medium findings: 0
- Low findings: 2

## Findings

### LOW - secret-template
- **File:** `reports/rendered-k8s/secret.template.yaml`
- **Finding:** Secret is committed only as a template.
- **Recommendation:** Generate real secrets from CI/CD credentials or a secrets manager.

### LOW - load-balancer-exposure
- **File:** `reports/rendered-k8s/service.yaml`
- **Finding:** Service type is LoadBalancer.
- **Recommendation:** For production, restrict source ranges or use an ingress/WAF pattern.

## Reviewer note

This is an AI-style deterministic review. It does not replace admission control, kube-bench, managed cloud security findings, or a human review, but it gives the pipeline a consistent manifest security decision point.


## Release Readiness

# Day 22 - Release Readiness Report

**Decision:** PASS
**Readiness score:** 100/100

## Required repository files

| File | Status |
|---|---|
| `README.md` | present |
| `DAILY_LOG.md` | present |
| `CHANGELOG.md` | present |
| `Jenkinsfile` | present |
| `Dockerfile` | present |
| `pom.xml` | present |
| `k8s/deployment.yaml` | present |
| `k8s/service.yaml` | present |
| `policies/kubernetes.rego` | present |
| `policies/dockerfile.rego` | present |

## Required evidence reports

| Report | Status |
|---|---|
| `reports/ai-test-plan.md` | present |
| `reports/k8s-hardening-report.md` | present |
| `reports/ai-security-report.md` | present |
| `reports/ai-container-remediation.md` | present |
| `reports/ai-dependency-remediation.md` | present |

## Recommended evidence reports

| Report | Status |
|---|---|
| `reports/sonar-evidence.md` | present |
| `reports/trivy-policy-result.md` | present |
| `reports/sca-policy-result.md` | present |
| `reports/manifest-security-review.md` | present |
| `reports/runtime-threat-summary.md` | present |

## Notes

- No readiness gaps detected by the offline checker.


## RDS PostgreSQL Integration

# Day 23 - RDS PostgreSQL Integration Report

## Rendered Kubernetes secret

- Output: `reports/generated-rds-secret.yaml`
- Namespace: `ai-devsecops`
- Secret name: `ai-devsecops-demo-db`

## Connection values

- SPRING_DATASOURCE_URL: `jdbc:postgresql://YOUR_RDS_ENDPOINT:5432/devsecops`
- SPRING_DATASOURCE_USERNAME: `devsecops_user`
- SPRING_DATASOURCE_PASSWORD: `CH****ME`
- SPRING_DATASOURCE_DRIVER: `org.postgresql.Driver`
- SPRING_JPA_HIBERNATE_DDL_AUTO: `validate`

## Security note

Do not commit real RDS credentials. Use Jenkins credentials, AWS Secrets Manager, External Secrets, Sealed Secrets, or a short-lived CI secret injection flow for real deployments.


## AI Runtime Threat Summary

# Day 24 - AI Runtime Threat Summary

**Runtime security score:** 100/100
**Source:** `reports/runtime-signals.txt`

## Detection summary

- High signals: 0
- Medium signals: 0
- Low signals: 0

No configured runtime threat patterns were detected in the collected logs/events.

## Recommended next steps

- Wire this stage to real Kubernetes events after every deployment.
- Add Falco, CloudWatch Container Insights, or Prometheus alerts for stronger runtime coverage.
- Keep this AI summary as an explanation layer, not as the only runtime detection engine.


## Final Validation Snapshot

# Day 25 - Final GitHub Readiness Validation

**Offline validation decision:** FAIL

## Summary

- PASS: 89
- FAIL: 1
- WARN: 7
- INFO: 1

## Validation results

| Check | Target | Status | Detail |
|---|---|---|---|
| required-file | `README.md` | PASS | present |
| required-file | `DAILY_LOG.md` | PASS | present |
| required-file | `CHANGELOG.md` | PASS | present |
| required-file | `PROJECT_PLAN_90_DAYS.md` | PASS | present |
| required-file | `Jenkinsfile` | PASS | present |
| required-file | `Dockerfile` | PASS | present |
| required-file | `pom.xml` | PASS | present |
| required-file | `.github/workflows/validate.yml` | PASS | present |
| required-file | `scripts/run_day25_final_validation.sh` | PASS | present |
| required-file | `docs/final-github-submission.md` | PASS | present |
| json-parse | `/mnt/data/final_work/ai-devsecops-pipeline/config/container-security-policy.json` | PASS | valid JSON |
| json-parse | `/mnt/data/final_work/ai-devsecops-pipeline/config/k8s-manifest-security-policy.json` | PASS | valid JSON |
| json-parse | `/mnt/data/final_work/ai-devsecops-pipeline/config/license-policy.json` | PASS | valid JSON |
| json-parse | `/mnt/data/final_work/ai-devsecops-pipeline/config/release-readiness-policy.json` | PASS | valid JSON |
| json-parse | `/mnt/data/final_work/ai-devsecops-pipeline/config/runtime-threat-rules.json` | PASS | valid JSON |
| json-parse | `/mnt/data/final_work/ai-devsecops-pipeline/config/sca-risk-policy.json` | PASS | valid JSON |
| json-parse | `/mnt/data/final_work/ai-devsecops-pipeline/config/secure-code-review-rules.json` | PASS | valid JSON |
| json-parse | `/mnt/data/final_work/ai-devsecops-pipeline/config/sonar-quality-gate.json` | PASS | valid JSON |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/configmap.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/deployment.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/hpa.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/namespace.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/network-policy.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/pdb.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/rbac.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/secret.template.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/k8s/service.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/infra/eks/cluster.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/infra/kind/kind-cluster.yaml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-devsecops-pipeline/infra/local/docker-compose.yml` | PASS | valid YAML |
| yaml-parse | `/mnt/data/final_work/ai-de

## AI Policy Recommendations

1. Current Dockerfile and Kubernetes manifests passed the included policy checks.
2. Add future policies for image digest pinning, signed images, and SBOM attestation.
3. Add environment-specific policy bundles for dev, staging, and production namespaces.
4. Review exceptions through time-bound suppressions instead of permanent bypasses.

## Scanner Notes

### Secret Scan

```text
[missing] reports/secret-scan.txt
```

### SonarQube Evidence

# SonarQube Evidence

Generated: `2026-05-05T16:04:17.857117+00:00`

Project: `ai-devsecops-demo`

Status: `UNAVAILABLE`

Error: `<urlopen error [Errno 111] Connection refused>`


### Runtime Signals

```text
# Kubernetes Events
No live Kubernetes context was available during offline validation.

# Pods
ai-devsecops-demo-0000000000-demo   2/2   Running   0   2m

# Recent App Logs
INFO ai-devsecops-demo started successfully
INFO readiness probe passed

```

## AI Remediation Plan Snapshot

# AI Remediation Plan

Generated: `2026-05-05T16:06:41.348445+00:00`

This report converts scanner evidence into an ordered developer fix queue. It does not replace scanner output; it summarizes it for execution.

No remediation actions were generated from the available reports. Run SonarQube, Dependency Check, Trivy, and policy gates for richer output.


## Limitations

This report is an assistant layer. Scanner outputs and Jenkins gate results remain the source of truth.
