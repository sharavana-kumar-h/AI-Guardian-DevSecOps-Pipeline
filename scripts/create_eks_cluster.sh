#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
: "${AWS_REGION:=ap-south-1}"
: "${EKS_CLUSTER_NAME:=ai-devsecops-eks}"
: "${EKS_CONFIG:=infra/eks/cluster.yaml}"
: "${DRY_RUN:=false}"

bash scripts/check_aws_eks_prereqs.sh || {
  echo "Prerequisite check failed. See reports/aws-eks-prereq-check.md"
  exit 1
}

if [[ "$DRY_RUN" == "true" ]]; then
  cat > reports/eks-create-report.md <<EOF
# EKS Cluster Create Report

DRY_RUN=true. No cluster was created.

Command that would run:

\`eksctl create cluster -f $EKS_CONFIG\`
EOF
  echo "Dry run complete."
  exit 0
fi

eksctl create cluster -f "$EKS_CONFIG" | tee reports/eks-create.log
aws eks update-kubeconfig --name "$EKS_CLUSTER_NAME" --region "$AWS_REGION" | tee -a reports/eks-create.log
kubectl get nodes -o wide | tee reports/eks-nodes.txt

cat > reports/eks-create-report.md <<EOF
# EKS Cluster Create Report

Status: requested/completed by eksctl.

- Cluster: \`$EKS_CLUSTER_NAME\`
- Region: \`$AWS_REGION\`
- Config: \`$EKS_CONFIG\`

See \`reports/eks-create.log\` and \`reports/eks-nodes.txt\`.
EOF
