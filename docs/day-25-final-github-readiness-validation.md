# Day 25 - Final GitHub Readiness Validation

## Objective

Create the final GitHub-ready package and run all offline validations possible in this environment.

## What was added

- `scripts/final_project_validator.py`
- `scripts/run_day25_final_validation.sh`
- `.github/workflows/validate.yml`
- `docs/final-github-submission.md`
- `reports/final-validation.md`
- `reports/final-validation.json`

## Offline validations

- Required file presence
- JSON config parsing
- YAML parsing for Kubernetes, infrastructure, and GitHub workflow files
- Python script compilation
- Shell script syntax checks
- External tool availability snapshot
- Manifest rendering and hardening report generation
- AI security report generation

## Run

```bash
bash scripts/run_day25_final_validation.sh
```

## Limitations

The offline validator cannot prove live execution for Maven, Docker, Trivy, SonarQube, Conftest, Kubernetes, or AWS/EKS unless those tools and credentials are available on the machine running the checks.
