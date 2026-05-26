# Day 15 SCA Risk Policy Result

Generated: 2026-05-05T16:20:05.646206+00:00

## Decision

**PASS_WITH_WARNINGS**

## Vulnerability Counts

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Unknown | 0 |

## SBOM Status

- SBOM required: **True**
- SBOM path: `reports/bom.json`
- SBOM component count: **7**
- Dependency Check report: `None`

## Failures

- None

## Warnings

- Dependency Check report not found; policy evaluated SBOM presence only.

## Highest Priority Findings

| Dependency | Finding | Severity | CVSS |
|---|---|---:|---:|
| _No Dependency Check vulnerabilities available_ | - | - | - |

## Recommended Actions

1. Upgrade direct dependencies first because they are controlled by the application team.
2. Prefer patched minor versions before major upgrades to reduce regression risk.
3. Use suppression files only for false positives with expiry dates and justification.
4. Regenerate the SBOM after every dependency change and archive it with the build.
