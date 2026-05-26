# Day 9 — AWS EKS Preparation

## Goal

Prepare the AWS/EKS deployment path without blindly creating paid cloud resources.

## What changed

- Added `infra/eks/cluster.yaml`
- Added `scripts/check_aws_eks_prereqs.sh`
- Added `scripts/create_eks_cluster.sh`
- Added `scripts/run_day9_eks_prep.sh`

## Run prereq check

```bash
export AWS_REGION=ap-south-1
export EKS_CLUSTER_NAME=ai-devsecops-eks
bash scripts/run_day9_eks_prep.sh
```

## Optional dry run

```bash
export DRY_RUN=true
bash scripts/create_eks_cluster.sh
```

## Real cluster creation

```bash
export DRY_RUN=false
bash scripts/create_eks_cluster.sh
```

## Cost control

Delete the cluster after your demo:

```bash
eksctl delete cluster --name ai-devsecops-eks --region ap-south-1
```
