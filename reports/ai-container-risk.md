# AI Container Risk Score

| Metric | Value |
|---|---:|
| Risk rating | **LOW** |
| Score | **100/100** |
| Critical CVEs | 0 |
| High CVEs | 0 |
| Medium CVEs | 0 |
| Non-root USER | True |
| Avoids latest tag | True |
| Multi-stage build | True |
| Healthcheck present | True |

Base images: `maven:3.9.11-eclipse-temurin-21, eclipse-temurin:21-jre-jammy`

## Recommendation

- Do not push or deploy when the rating is HIGH or CRITICAL.
- Patch critical/high CVEs or switch to a cleaner base image.
- Keep non-root execution, health checks, and multi-stage builds enabled.
