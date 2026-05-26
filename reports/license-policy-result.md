# Day 15 License Policy Result

Generated: 2026-05-05T16:20:10.765492+00:00

## Decision

**PASS_WITH_WARNINGS**

## Counts

| Signal | Count |
|---|---:|
| SBOM components | 7 |
| Allowed license components | 0 |
| Denied license components | 0 |
| Warning license components | 0 |
| Unknown license components | 7 |

## Failures

- None

## Denied Licenses

- None

## Warning Licenses

- None

## Unknown Licenses

- `org.springframework.boot:spring-boot-starter-web:managed-by-parent-or-bom`
- `org.springframework.boot:spring-boot-starter-actuator:managed-by-parent-or-bom`
- `org.springframework.boot:spring-boot-starter-data-jpa:managed-by-parent-or-bom`
- `org.springframework.boot:spring-boot-starter-validation:managed-by-parent-or-bom`
- `org.postgresql:postgresql:managed-by-parent-or-bom`
- `com.h2database:h2:managed-by-parent-or-bom`
- `org.springframework.boot:spring-boot-starter-test:managed-by-parent-or-bom`

## Notes

Missing license metadata is common in fallback SBOM mode. For stricter evidence, run the CycloneDX Maven plugin and archive the generated `target/bom.json`.
