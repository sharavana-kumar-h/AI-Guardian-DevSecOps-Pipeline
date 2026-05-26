# Day 13 — AI Remediation Plan

## Goal

Day 13 converts scanner evidence into a prioritized developer fix queue.

The AI remediation plan does not replace security scanners. It reads evidence from secure-code review, SonarQube triage, CVE prioritization, container risk scoring, and local quality policy checks, then produces an ordered remediation report.

## Added

- `scripts/ai_remediation_plan.py`
- `scripts/run_day13_ai_remediation.sh`
- Jenkins parameter: `ENABLE_AI_REMEDIATION_PLAN`

## Run

```bash
bash scripts/run_day13_ai_remediation.sh
```

## Outputs

```text
reports/ai-remediation-plan.json
reports/ai-remediation-plan.md
reports/ai-security-report.md
```

## Priority model

- `P0`: Must fix before deploy
- `P1`: Fix before image publishing or production-like deployment
- `P2`: Fix soon or document accepted risk
- `P3`: Backlog or hygiene improvement
