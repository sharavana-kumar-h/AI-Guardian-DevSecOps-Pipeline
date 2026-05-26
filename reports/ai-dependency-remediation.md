# Day 16 AI Dependency Remediation Plan

Generated: 2026-05-05T16:20:44.145530+00:00

## Executive Summary

- Total actions: **2**
- P0/P1 actions: **0**
- Recommended deploy decision: **ALLOW after standard validation**

## Remediation Queue

| Priority | Category | Target | Finding | Recommended Fix |
|---|---|---|---|---|
| P2 | License Metadata | `7 component(s)` | Missing license metadata | Generate a full CycloneDX SBOM with Maven instead of relying on fallback SBOM mode. |
| P3 | SBOM Quality | `Dependency graph completeness` | SBOM appears to contain direct dependencies only | Ensure CycloneDX Maven plugin runs successfully and includes runtime/compile scopes. |

## Validation Commands

- `bash scripts/run_day14_sca_inventory.sh`
- `jq '.components | length' reports/bom.json`

## Operating Rules

1. Patch direct dependencies first.
2. Do not suppress dependency findings unless they are proven false positives.
3. Every suppression should include a reason, owner, and expiry date.
4. Regenerate SBOM and rerun SCA after each dependency change.
5. Archive SBOM, Dependency Check report, license report, and this plan as build artifacts.
