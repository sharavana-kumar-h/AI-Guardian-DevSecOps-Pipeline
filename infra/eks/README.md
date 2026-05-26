# AWS EKS Infrastructure Notes

This folder contains a minimal `eksctl` cluster config for the Day 9-10 deployment path.

Default region is `ap-south-1`. Change it if your AWS account has limits or pricing constraints in another region.

## Create cluster

```bash
export AWS_REGION=ap-south-1
export EKS_CLUSTER_NAME=ai-devsecops-eks
bash scripts/create_eks_cluster.sh
```

## Update kubeconfig

```bash
aws eks update-kubeconfig --name ai-devsecops-eks --region ap-south-1
```

## Delete cluster after demo

```bash
eksctl delete cluster --name ai-devsecops-eks --region ap-south-1
```

## Cost warning

EKS, LoadBalancers, NAT gateways, and worker nodes can create real charges. Delete the cluster when done.
