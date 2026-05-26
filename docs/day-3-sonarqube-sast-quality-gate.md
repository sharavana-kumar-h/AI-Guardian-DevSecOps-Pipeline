# Day 3 — SonarQube SAST, AI Vulnerability Analysis, and Quality Gate

## Goal

Add a real SAST gate before any dependency scan, image build, or deployment happens.

## What was added

- `Day 3 - SonarQube SAST` stage in `Jenkinsfile`
- `Day 3 - SonarQube Quality Gate` hard stop using Jenkins `waitForQualityGate`
- `scripts/fetch_sonar_report.py` to fetch SonarQube quality gate and top issue evidence
- `config/sonar-quality-gate-notes.md` with the starter gate definition
- AI security report support for SonarQube blocker, critical, major, and quality gate signals

## Local setup

Start local SonarQube:

```bash
docker compose -f infra/local/docker-compose.yml up -d sonarqube
```

Open `http://localhost:9000`, finish first login, create a token, then run:

```bash
export SONAR_HOST_URL=http://localhost:9000
export SONAR_PROJECT_KEY=ai-devsecops-demo
export SONAR_TOKEN=<your-token>
bash scripts/run_day3_sonar.sh
```

Expected reports:

- `reports/sonar-findings.json`
- `reports/sonar-evidence.md`
- `reports/ai-security-report.md`

## Jenkins setup

Required Jenkins plugin/config:

- SonarQube Scanner for Jenkins plugin
- SonarQube server named `SonarQube` in Jenkins system configuration
- Webhook from SonarQube to Jenkins for quality gate callback

Suggested flow:

1. Run build/test/coverage first.
2. Send analysis to SonarQube.
3. Wait for quality gate.
4. Stop the pipeline immediately if the gate fails.
5. Fetch evidence for the AI report.

## Interview explanation

“SonarQube is the source-of-truth SAST engine. The AI layer does not replace SonarQube; it summarizes SonarQube output, explains likely business impact, and helps developers prioritize remediation.”
