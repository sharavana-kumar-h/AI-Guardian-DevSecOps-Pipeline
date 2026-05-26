#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
: "${AWS_REGION:=ap-south-1}"
: "${EKS_CLUSTER_NAME:=ai-devsecops-eks}"

REPORT=reports/aws-eks-prereq-check.md
{
  echo "# AWS/EKS Prerequisite Check"
  echo
  echo "- AWS_REGION: \`$AWS_REGION\`"
  echo "- EKS_CLUSTER_NAME: \`$EKS_CLUSTER_NAME\`"
  echo
  echo "## Tool checks"
} > "$REPORT"

missing=0
for tool in aws eksctl kubectl docker; do
  if command -v "$tool" >/dev/null 2>&1; then
    version="$($tool version 2>&1 | head -1 || true)"
    echo "- $tool: found — $version" >> "$REPORT"
  else
    echo "- $tool: missing" >> "$REPORT"
    missing=1
  fi
done

{
  echo
  echo "## AWS identity"
} >> "$REPORT"

if command -v aws >/dev/null 2>&1 && aws sts get-caller-identity >/tmp/aws_identity.json 2>/tmp/aws_identity.err; then
  cat /tmp/aws_identity.json > reports/aws-caller-identity.json
  echo "- aws sts get-caller-identity: passed" >> "$REPORT"
else
  echo "- aws sts get-caller-identity: failed or not configured" >> "$REPORT"
  if [[ -s /tmp/aws_identity.err ]]; then
    sed 's/^/  /' /tmp/aws_identity.err >> "$REPORT"
  fi
  missing=1
fi

{
  echo
  echo "## Minimum IAM permissions to verify manually"
  echo
  echo "- EKS cluster create/read/update/delete permissions"
  echo "- EC2 VPC, subnet, security group, and launch template permissions used by eksctl"
  echo "- IAM role creation/attachment permissions for EKS and node groups"
  echo "- CloudFormation stack permissions"
  echo "- Elastic Load Balancing permissions for Service type LoadBalancer"
} >> "$REPORT"

echo "$REPORT"
exit "$missing"
