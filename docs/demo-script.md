# Demo Script

## 1. Show project structure

Open the repository and explain the main folders: `src`, `scripts`, `k8s`, `policies`, `infra`, `docs`, and `reports`.

## 2. Run local build and test gate

```bash
mvn -B clean verify
```

Show JUnit and JaCoCo outputs.

## 3. Show security gates

Run or show reports from:

```bash
bash scripts/run_day3_sonar.sh
bash scripts/run_day4_sca_container.sh
bash scripts/run_day5_policy_checks.sh
```

Explain that SonarQube, Dependency Check, Trivy, and OPA produce evidence, while AI scripts summarize and prioritize.

## 4. Show Docker image publishing workflow

```bash
export IMAGE=your-dockerhub-user/ai-devsecops-demo:demo
export DRY_RUN=true
bash scripts/run_day6_docker_publish.sh
```

Explain how real publish uses Docker Hub credentials.

## 5. Show Kubernetes hardening

```bash
export IMAGE=local/ai-devsecops-demo:demo
bash scripts/run_day7_k8s_hardening.sh
```

Show `reports/k8s-hardening-report.md`.

## 6. Show local Kubernetes deployment

```bash
kind create cluster --config infra/kind/kind-cluster.yaml
export IMAGE=local/ai-devsecops-demo:demo
bash scripts/run_day8_local_k8s.sh
```

Show rollout, service, and smoke test output.

## 7. Show AWS EKS preparation

```bash
bash scripts/run_day9_eks_prep.sh
```

Show the prereq report and explain cost controls.

## 8. Show AWS EKS deployment path

```bash
export AWS_REGION=ap-south-1
export EKS_CLUSTER_NAME=ai-devsecops-eks
export IMAGE=your-dockerhub-user/ai-devsecops-demo:demo
bash scripts/run_day10_eks_deploy.sh
```

Show `kubectl get deploy,pods,svc,hpa,pdb -n ai-devsecops`.

## 9. Show final AI report

```bash
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md
```

Explain that AI helps triage; it does not replace security tools.
