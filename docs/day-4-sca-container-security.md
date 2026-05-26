# Day 4 — OWASP Dependency Check, AI CVE Prioritization, and Trivy Image Scanning

## Goal

Add software composition analysis and container vulnerability scanning before an image is pushed or deployed.

## What was added

- `Day 4 - OWASP Dependency Check SCA` Jenkins stage
- `Day 4 - Docker Build` Jenkins stage
- `Day 4 - Trivy Image Scan` Jenkins stage
- `scripts/ai_cve_prioritizer.py`
- `scripts/container_risk_score.py`
- `config/dependency-check-suppression.xml`
- `config/trivy.yaml`
- AI security report sections for CVE priority and container risk

## Local run

```bash
export IMAGE=local/ai-devsecops-demo:day4
bash scripts/run_day4_sca_container.sh
```

Expected reports:

- `target/dependency-check-report/dependency-check-report.html`
- `target/dependency-check-report/dependency-check-report.json`
- `reports/trivy-image.json`
- `reports/trivy-image.txt`
- `reports/ai-cve-priorities.md`
- `reports/ai-container-risk.md`
- `reports/ai-security-report.md`

## Gate policy

Recommended starting threshold:

- Dependency Check: block high/critical findings after report generation
- Trivy: block critical and high findings
- Suppress only proven false positives
- Every suppression must have a reason and expiry date

## Interview explanation

“Dependency Check covers vulnerable third-party libraries. Trivy covers OS packages and image-layer risk. The AI prioritizer ranks the scanner findings by severity, fix availability, and deployment impact, but it never fabricates CVEs.”
