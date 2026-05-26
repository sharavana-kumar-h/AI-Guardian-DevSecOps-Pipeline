# Days 14-16 Status

Completed supply-chain security expansion.

## Day 14

- Added SBOM generation using CycloneDX-compatible output.
- Added fallback SBOM generation when Maven is unavailable.
- Added dependency inventory from `pom.xml` and SBOM evidence.

## Day 15

- Added dependency vulnerability risk policy.
- Added license policy checks.
- Added strict failure mode through `FAIL_DEP_POLICY=true`.

## Day 16

- Added AI dependency remediation plan.
- Integrated dependency/license/SBOM evidence into the main AI security report.

## Key Artifacts

- `reports/bom.json`
- `reports/dependency-inventory.md`
- `reports/sca-policy-result.md`
- `reports/license-policy-result.md`
- `reports/ai-dependency-remediation.md`
- `reports/ai-security-report.md`
