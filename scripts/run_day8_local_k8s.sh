#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
: "${IMAGE:=local/ai-devsecops-demo:day8}"
: "${K8S_NAMESPACE:=ai-devsecops}"
: "${SKIP_DOCKER_BUILD:=false}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required for Day 8 local deployment." | tee reports/day-8-local-k8s.md
  exit 1
fi

kubectl cluster-info >/dev/null

if [[ "$SKIP_DOCKER_BUILD" != "true" ]]; then
  docker build -t "$IMAGE" .
  if command -v kind >/dev/null 2>&1 && kubectl config current-context | grep -q 'kind-'; then
    kind load docker-image "$IMAGE" || true
  fi
fi

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
kubectl rollout status deployment/ai-devsecops-demo -n "$K8S_NAMESPACE" --timeout=180s

bash scripts/smoke_test_k8s.sh "$K8S_NAMESPACE" ai-devsecops-demo
bash scripts/collect_runtime_signals.sh "$K8S_NAMESPACE" || true

cat > reports/day-8-local-k8s.md <<EOF
# Day 8 Local Kubernetes Deployment

Status: completed

- Image: \`$IMAGE\`
- Namespace: \`$K8S_NAMESPACE\`
- Smoke test: see \`reports/k8s-smoke-test.md\`
- Runtime signals: see \`reports/runtime-signals.txt\`
EOF

echo "Day 8 local Kubernetes deployment completed."
