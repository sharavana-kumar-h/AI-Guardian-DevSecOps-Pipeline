# Day 16 — AI Dependency Remediation Plan

## Goal

Generate a developer-facing remediation queue from SBOM, dependency risk, and license policy evidence.

## Added

- `scripts/ai_dependency_remediation.py`
- `scripts/run_day16_ai_dependency_remediation.sh`
- AI security report integration for supply-chain reports

## Run

```bash
bash scripts/run_day16_ai_dependency_remediation.sh
```

## Expected Artifacts

- `reports/ai-dependency-remediation.json`
- `reports/ai-dependency-remediation.md`
- `reports/ai-security-report.md`

## How to Use the Report

Treat P0/P1 dependency actions as release blockers. P2/P3 items are improvement tasks unless your organization requires stricter compliance.

The report is deterministic by default and does not replace scanner evidence. It turns scanner evidence into a prioritized fix queue.
