# Day 17 - Container Image Metadata and Hardening Report

Generated: `2026-05-05T16:43:12Z`
Image: `local/test:day19`

## Dockerfile summary
- Dockerfile exists: **True**
- Base images: maven:3.9.11-eclipse-temurin-21, eclipse-temurin:21-jre-jammy
- Runtime user: `appuser`
- Healthcheck: **True**
- Exposed ports: 8080

## Docker image inspect
- Inspect unavailable: docker CLI is not installed

## Findings
| Severity | ID | Finding | Recommendation |
|---|---|---|---|
| LOW | IMG005 | Runtime image installs OS packages — ca-certificates, curl | Keep runtime packages minimal; remove package managers where possible or consider a distroless runtime. |
| INFO | IMG007 | Image digest not captured — No digest file or RepoDigest detected | Capture the registry digest after push for deployment traceability. |

## Decision
- Status: **PASS**
