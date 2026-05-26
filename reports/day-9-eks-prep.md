# Day 9 AWS EKS Preparation

Generated assets:

- `infra/eks/cluster.yaml` — minimal eksctl cluster configuration
- `reports/aws-eks-prereq-check.md` — local AWS/EKS readiness report

Manual checks before Day 10:

1. AWS CLI is authenticated with the correct account.
2. Billing alerts are enabled.
3. The target region has EKS and EC2 quota available.
4. Docker image is already pushed to Docker Hub.
5. `aws eks update-kubeconfig` can write to your kubeconfig.
6. You understand how to delete the cluster after the demo.

Delete command after demo:

```bash
eksctl delete cluster --name ai-devsecops-eks --region ap-south-1
```
