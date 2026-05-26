# Day 18 — Trivy Policy Enforcement

Day 18 converts Trivy scan output into a local pass/fail decision. Trivy remains the scanner source of truth; the project-owned policy decides whether the image can be promoted.

Run:

```bash
export IMAGE=local/ai-devsecops-demo:day18
bash scripts/run_day18_trivy_policy.sh
```

Strict mode:

```bash
export FAIL_TRIVY_POLICY=true
bash scripts/run_day18_trivy_policy.sh
```

Generated evidence:

- `reports/trivy-image.json`
- `reports/trivy-image.txt`
- `reports/trivy-policy-result.json`
- `reports/trivy-policy-result.md`

Policy file:

- `config/container-security-policy.json`

The default threshold allows zero critical vulnerabilities, zero high/critical secrets, and zero high/critical misconfigurations.
