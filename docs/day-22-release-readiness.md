# Day 22 - Release Readiness and Evidence Packaging

## Objective

Add a release-readiness gate that verifies the repository has the minimum documentation, configuration, scripts, and evidence reports expected from a GitHub-ready DevSecOps portfolio project.

## What was added

- `config/release-readiness-policy.json`
- `scripts/release_readiness_check.py`
- `scripts/run_day22_release_readiness.sh`
- `reports/release-readiness.md`
- `reports/release-readiness.json`

## What it checks

- Required repository files
- Required security evidence reports
- Recommended scanner outputs
- Overall readiness score
- Missing artifact notes

## Run

```bash
bash scripts/run_day22_release_readiness.sh
```

Strict mode:

```bash
export FAIL_RELEASE_READINESS=true
bash scripts/run_day22_release_readiness.sh
```
