# Day 11 — Deep SAST Review

## Goal

Day 11 adds a deeper static-analysis layer on top of the existing SonarQube workflow.

The goal is not to replace SonarQube. The goal is to add a fast, transparent, project-owned secure-code review pass and then convert SonarQube evidence into a developer-friendly remediation queue.

## Added

- `config/secure-code-review-rules.json`
- `scripts/secure_code_review.py`
- SonarQube measures and hotspot enrichment in `scripts/fetch_sonar_report.py`
- `scripts/sonar_issue_triage.py`
- `scripts/run_day11_sast_deep_scan.sh`

## What it checks

The secure-code review rules look for common risky patterns:

- Potential hardcoded secrets
- Weak randomness in Java code
- Possible SQL string concatenation
- Wildcard CORS origins
- Overexposed actuator endpoints
- Plain HTTP endpoints in config

## Run

```bash
export SONAR_HOST_URL=http://localhost:9000
export SONAR_PROJECT_KEY=ai-devsecops-demo
export SONAR_TOKEN=<your-token>
bash scripts/run_day11_sast_deep_scan.sh
```

If SonarQube is unavailable, the script still produces local secure-code review reports and a best-effort Sonar availability report.

## Outputs

```text
reports/secure-code-review.json
reports/secure-code-review.md
reports/sonar-findings.json
reports/sonar-evidence.md
reports/sonar-issue-triage.json
reports/sonar-issue-triage.md
```
