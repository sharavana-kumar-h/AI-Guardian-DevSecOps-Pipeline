#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
: "${AWS_REGION:=ap-south-1}"
: "${EKS_CLUSTER_NAME:=ai-devsecops-eks}"
: "${K8S_NAMESPACE:=ai-devsecops}"
: "${IMAGE:?Set IMAGE to a pushed Docker Hub image, for example youruser/ai-devsecops-demo:10}"
: "${UPDATE_KUBECONFIG:=true}"

bash scripts/check_aws_eks_prereqs.sh

if [[ "$UPDATE_KUBECONFIG" == "true" ]]; then
  aws eks update-kubeconfig --name "$EKS_CLUSTER_NAME" --region "$AWS_REGION"
fi

kubectl cluster-info
bash scripts/render_k8s_manifests.sh "$IMAGE" reports/rendered-k8s

kubectl apply -f reports/rendered-k8s/namespace.yaml
kubectl apply -f reports/rendered-k8s/configmap.yaml
kubectl apply -f reports/rendered-k8s/secret.template.yaml
kubectl apply -f reports/rendered-k8s/rbac.yaml
kubectl apply -f reports/rendered-k8s/deployment.yaml
kubectl apply -f reports/rendered-k8s/service.yaml
kubectl apply -f reports/rendered-k8s/network-policy.yaml
kubectl apply -f reports/rendered-k8s/pdb.yaml || true
kubectl apply -f reports/rendered-k8s/hpa.yaml || true
kubectl rollout status deployment/ai-devsecops-demo -n "$K8S_NAMESPACE" --timeout=300s

kubectl -n "$K8S_NAMESPACE" get deploy,pods,svc,hpa,pdb -o wide | tee reports/eks-workload-status.txt
bash scripts/collect_runtime_signals.sh "$K8S_NAMESPACE" || true
python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md || true

LB_HOST="$(kubectl -n "$K8S_NAMESPACE" get svc ai-devsecops-demo -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)"
LB_IP="$(kubectl -n "$K8S_NAMESPACE" get svc ai-devsecops-demo -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"

cat > reports/day-10-eks-deploy.md <<EOF
# Day 10 EKS Deployment

Status: deployment command completed.

- Cluster: \`$EKS_CLUSTER_NAME\`
- Region: \`$AWS_REGION\`
- Namespace: \`$K8S_NAMESPACE\`
- Image: \`$IMAGE\`
- LoadBalancer hostname: \`${LB_HOST:-pending}\`
- LoadBalancer IP: \`${LB_IP:-pending}\`

If the LoadBalancer is pending, wait 2-5 minutes and run:

\`kubectl -n $K8S_NAMESPACE get svc ai-devsecops-demo -o wide\`
EOF

echo "Day 10 EKS deployment completed. See reports/day-10-eks-deploy.md"
