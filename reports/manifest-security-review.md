# Day 21 - AI Kubernetes Manifest Security Review

**Manifest security score:** 96/100

## Summary

- High findings: 0
- Medium findings: 0
- Low findings: 2

## Findings

### LOW - secret-template
- **File:** `reports/rendered-k8s/secret.template.yaml`
- **Finding:** Secret is committed only as a template.
- **Recommendation:** Generate real secrets from CI/CD credentials or a secrets manager.

### LOW - load-balancer-exposure
- **File:** `reports/rendered-k8s/service.yaml`
- **Finding:** Service type is LoadBalancer.
- **Recommendation:** For production, restrict source ranges or use an ingress/WAF pattern.

## Reviewer note

This is an AI-style deterministic review. It does not replace admission control, kube-bench, managed cloud security findings, or a human review, but it gives the pipeline a consistent manifest security decision point.
