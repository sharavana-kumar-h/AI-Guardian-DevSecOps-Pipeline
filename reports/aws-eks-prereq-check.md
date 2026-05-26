# AWS/EKS Prerequisite Check

- AWS_REGION: `ap-south-1`
- EKS_CLUSTER_NAME: `ai-devsecops-eks`

## Tool checks
- aws: missing
- eksctl: missing
- kubectl: missing
- docker: missing

## AWS identity
- aws sts get-caller-identity: failed or not configured

## Minimum IAM permissions to verify manually

- EKS cluster create/read/update/delete permissions
- EC2 VPC, subnet, security group, and launch template permissions used by eksctl
- IAM role creation/attachment permissions for EKS and node groups
- CloudFormation stack permissions
- Elastic Load Balancing permissions for Service type LoadBalancer
