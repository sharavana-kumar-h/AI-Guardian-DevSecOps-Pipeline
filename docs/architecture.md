# Architecture

## End-to-end flow

```text
Developer Commit
  -> GitHub
  -> Jenkins Declarative Pipeline
  -> Secret Scan
  -> AI Test Case Suggestions
  -> Maven Build
  -> JUnit Tests
  -> JaCoCo Coverage Gate
  -> SonarQube SAST
  -> SonarQube Quality Gate
  -> Sonar Evidence Fetcher
  -> OWASP Dependency Check
  -> Docker Build
  -> Trivy Image Scan
  -> AI CVE Prioritization
  -> AI Container Risk Score
  -> Rendered Kubernetes Manifests
  -> Kubernetes Hardening Review
  -> OPA/Conftest Policy Checks
  -> Security Gate Enforcement
  -> Docker Hub Publish
  -> Local Kubernetes or AWS EKS Deployment
  -> Runtime Signal Collection
  -> AI-Assisted Security Report
```

## Design principle

The scanners and policy engines remain the source of truth. The AI layer summarizes evidence, prioritizes remediation, and creates developer-friendly explanations.

## Deployment targets

### Local Kubernetes

Used for Day 8 validation. The scripts support Kind/Minikube-style deployment and run smoke tests through `kubectl port-forward`.

### AWS EKS

Used for Day 10 cloud deployment. The project includes an `eksctl` cluster config, AWS prereq checks, kubeconfig update flow, and EKS deploy wrapper.

## Security boundaries

- Application runs as non-root UID `10001`.
- Pod and container security contexts are enforced.
- Linux capabilities are dropped.
- Privilege escalation is disabled.
- Root filesystem is read-only with `/tmp` mounted as an `emptyDir`.
- NetworkPolicy is present.
- Resource requests/limits are required.
- Service account token auto-mount is disabled.
- OPA/Conftest validates manifests before deployment.
