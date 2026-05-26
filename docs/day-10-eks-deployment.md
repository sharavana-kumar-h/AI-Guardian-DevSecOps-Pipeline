# Day 10 — AWS EKS Deployment

## Goal

Deploy the validated Docker image to AWS EKS using the same hardened Kubernetes manifests from Day 7.

## Prerequisites

- EKS cluster exists
- AWS CLI is authenticated
- Docker image is already pushed to Docker Hub
- `kubectl` context can reach the EKS cluster

## Run

```bash
export AWS_REGION=ap-south-1
export EKS_CLUSTER_NAME=ai-devsecops-eks
export IMAGE=your-dockerhub-user/ai-devsecops-demo:day10
bash scripts/run_day10_eks_deploy.sh
```

## Outputs

- `reports/day-10-eks-deploy.md`
- `reports/eks-workload-status.txt`
- `reports/runtime-signals.txt`
- `reports/ai-security-report.md`

## Validate endpoint

```bash
kubectl -n ai-devsecops get svc ai-devsecops-demo -o wide
```

The LoadBalancer hostname may take a few minutes to appear.
