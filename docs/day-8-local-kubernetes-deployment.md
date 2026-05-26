# Day 8 — Local Kubernetes Deployment

## Goal

Prove the secured workload can run in a real Kubernetes cluster before moving to AWS EKS.

## Recommended local cluster

Use Kind or Minikube.

Kind example:

```bash
kind create cluster --config infra/kind/kind-cluster.yaml
kubectl cluster-info
```

## Run deployment

```bash
export IMAGE=local/ai-devsecops-demo:day8
bash scripts/run_day8_local_k8s.sh
```

The script builds the image, renders manifests, applies Kubernetes resources, waits for rollout, runs a smoke test with port-forward, and collects runtime signals.

## Outputs

- `reports/k8s-smoke-test.md`
- `reports/k8s-health.json`
- `reports/runtime-signals.txt`
- `reports/day-8-local-k8s.md`

## Cleanup

```bash
kubectl delete namespace ai-devsecops
kind delete cluster --name ai-devsecops-local
```
