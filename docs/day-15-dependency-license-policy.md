# Day 15 — Dependency Risk and License Policy

## Goal

Convert dependency evidence into a deploy/no-deploy policy decision.

## Added

- `config/sca-risk-policy.json`
- `config/license-policy.json`
- `scripts/sca_risk_policy.py`
- `scripts/license_policy_check.py`
- `scripts/run_day15_dependency_policy.sh`

## Checks

The dependency risk policy checks:

- SBOM presence
- Dependency Check report presence when required
- Critical vulnerability threshold
- High vulnerability threshold
- CVSS hard-fail threshold
- Medium severity warning threshold

The license policy checks:

- Denied license families such as AGPL, GPL-3, SSPL, BUSL, and Commons Clause
- Warning license families such as LGPL, GPL, and MPL
- Unknown license metadata count

## Run

```bash
bash scripts/run_day15_dependency_policy.sh
```

Strict mode:

```bash
export FAIL_DEP_POLICY=true
bash scripts/run_day15_dependency_policy.sh
```

## Expected Artifacts

- `reports/sca-policy-result.json`
- `reports/sca-policy-result.md`
- `reports/license-policy-result.json`
- `reports/license-policy-result.md`
