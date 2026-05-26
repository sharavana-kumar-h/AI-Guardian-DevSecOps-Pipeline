# Day 19 — Image SBOM and Provenance

Day 19 adds image-level SBOM and provenance evidence. Application SBOMs answer “what libraries are in my app?” while image SBOMs answer “what is inside the final container image?”

Run:

```bash
export IMAGE=local/ai-devsecops-demo:day19
bash scripts/run_day19_image_sbom_provenance.sh
```

Generated evidence:

- `reports/image-sbom.cdx.json`
- `reports/image-sbom-generation.md`
- `reports/image-metadata.md`
- `reports/image-provenance.json`
- `reports/image-provenance.md`

The script uses Trivy or Syft when available. If neither is installed, it creates a minimal fallback CycloneDX document so the workflow still demonstrates the expected pipeline shape.
