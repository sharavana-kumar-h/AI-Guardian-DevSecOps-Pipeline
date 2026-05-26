# Day 14 Dependency Inventory and SBOM Summary

Generated: 2026-05-05T16:20:00.371887+00:00

## SBOM Status

- Status: **available**
- Path: `reports/bom.json`
- Format: `CycloneDX`
- Spec version: `1.5`
- Components discovered from SBOM: **7**
- Direct dependencies from `pom.xml`: **7**

## Dependency Scope Counts

- **compile**: 4
- **required**: 4
- **runtime**: 4
- **test**: 2

## Direct Maven Dependencies

| Dependency | Version | Scope |
|---|---:|---|
| `org.springframework.boot:spring-boot-starter-web` | `managed-by-parent-or-bom` | `compile` |
| `org.springframework.boot:spring-boot-starter-actuator` | `managed-by-parent-or-bom` | `compile` |
| `org.springframework.boot:spring-boot-starter-data-jpa` | `managed-by-parent-or-bom` | `compile` |
| `org.springframework.boot:spring-boot-starter-validation` | `managed-by-parent-or-bom` | `compile` |
| `org.postgresql:postgresql` | `managed-by-parent-or-bom` | `runtime` |
| `com.h2database:h2` | `managed-by-parent-or-bom` | `runtime` |
| `org.springframework.boot:spring-boot-starter-test` | `managed-by-parent-or-bom` | `test` |

## First 25 SBOM Components

| Component | Version | Scope |
|---|---:|---|
| `org.springframework.boot:spring-boot-starter-web` | `managed-by-parent-or-bom` | `required` |
| `org.springframework.boot:spring-boot-starter-actuator` | `managed-by-parent-or-bom` | `required` |
| `org.springframework.boot:spring-boot-starter-data-jpa` | `managed-by-parent-or-bom` | `required` |
| `org.springframework.boot:spring-boot-starter-validation` | `managed-by-parent-or-bom` | `required` |
| `org.postgresql:postgresql` | `managed-by-parent-or-bom` | `runtime` |
| `com.h2database:h2` | `managed-by-parent-or-bom` | `runtime` |
| `org.springframework.boot:spring-boot-starter-test` | `managed-by-parent-or-bom` | `test` |

## Supply-Chain Notes

1. Archive the SBOM with every Jenkins build so later vulnerability investigations can identify exactly what shipped.
2. Treat direct dependencies as the fastest patch path; transitive dependency fixes may require parent upgrades or exclusions.
3. Regenerate the SBOM after every dependency or base-image change.
4. Use this inventory as input for the Day 15 dependency and license policy checks.
