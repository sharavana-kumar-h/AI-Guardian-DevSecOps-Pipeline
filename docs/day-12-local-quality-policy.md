# Day 12 — Local SAST Quality Policy

## Goal

Day 12 adds a local deploy/no-deploy policy around SonarQube evidence. This complements SonarQube's built-in Quality Gate and makes the project policy explicit in version control.

## Added

- `config/sonar-quality-gate.json`
- `scripts/sonar_sast_policy.py`
- `scripts/run_day12_quality_policy.sh`

## Policy checks

The local SAST policy can check:

- Blocker issues
- Critical issues
- Major security issues
- Open security hotspots
- Minimum coverage percentage
- Maximum duplicated-lines density
- Allowed SonarQube quality-gate status

## Report-only mode

```bash
bash scripts/run_day12_quality_policy.sh
```

## Strict mode

```bash
export FAIL_LOCAL_SONAR_POLICY=1
export FAIL_SECURITY_GATES=true
bash scripts/run_day12_quality_policy.sh
```

## Outputs

```text
reports/sonar-policy-result.json
reports/sonar-policy-result.md
reports/security-gate-result.md
```
