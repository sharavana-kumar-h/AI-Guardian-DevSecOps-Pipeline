# Day 17 — Container Image Hardening and Metadata

Day 17 adds image-level hardening evidence beyond a successful Docker build. The Dockerfile now supports OCI metadata labels through build args, keeps a non-root runtime user, exposes a single service port, and preserves a healthcheck for local container validation.

Run:

```bash
export IMAGE=local/ai-devsecops-demo:day17
bash scripts/run_day17_container_hardening.sh
```

Generated evidence:

- `reports/image-metadata.json`
- `reports/image-metadata.md`
- `reports/day-17-container-hardening-status.md`

What to show in demo:

1. Explain the hardened Dockerfile.
2. Show the non-root user and OCI labels.
3. Open the metadata report and discuss any hardening findings.
