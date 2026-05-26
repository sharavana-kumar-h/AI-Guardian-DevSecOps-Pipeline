# Day 20 - AI Container Remediation Queue

Generated: `2026-05-05T16:44:06Z`

This report converts image-scan, image-metadata, and provenance evidence into a practical container fix queue.

## Prioritized tasks
| Priority | Severity | Task | Evidence | Recommended action | Source |
|---:|---|---|---|---|---|
| 1 | LOW | Runtime image installs OS packages | ca-certificates, curl | Keep runtime packages minimal; remove package managers where possible or consider a distroless runtime. | `image-metadata.json` |
| 2 | INFO | Image digest not captured | No digest file or RepoDigest detected | Capture the registry digest after push for deployment traceability. | `image-metadata.json` |

## Suggested Day 20 demo
1. Run Trivy and policy enforcement.
2. Show a failing threshold or metadata warning.
3. Open this remediation queue and explain the first three fixes.
4. Rebuild the image and rerun the policy to show improvement.
