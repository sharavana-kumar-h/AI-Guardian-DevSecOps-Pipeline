# Day 20 — AI Container Remediation Queue

Day 20 converts container evidence into a developer-facing remediation queue. It reads Trivy policy output, image metadata findings, provenance data, and container-risk evidence, then ranks the next fixes.

Run:

```bash
export IMAGE=local/ai-devsecops-demo:day20
bash scripts/run_day20_ai_container_remediation.sh
```

Generated evidence:

- `reports/ai-container-remediation.json`
- `reports/ai-container-remediation.md`
- `reports/ai-security-report.md`

The correct explanation is: AI helps prioritize and explain scanner evidence. It does not replace Trivy, Docker metadata inspection, SBOM generation, or policy enforcement.
