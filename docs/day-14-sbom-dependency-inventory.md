# Day 14 — SBOM and Dependency Inventory

## Goal

Create build-time supply-chain evidence by generating a CycloneDX SBOM and a human-readable dependency inventory.

## Added

- CycloneDX Maven plugin configuration in `pom.xml`
- `scripts/generate_sbom.sh`
- `scripts/dependency_inventory.py`
- `reports/bom.json` output path
- `reports/dependency-inventory.md` output path

## Run

```bash
bash scripts/run_day14_sca_inventory.sh
```

## Expected Artifacts

- `reports/bom.json`
- `reports/bom.xml` when Maven/CycloneDX is available
- `reports/dependency-inventory.json`
- `reports/dependency-inventory.md`
- `reports/sbom-generation.md`

## Notes

The script prefers the CycloneDX Maven plugin. If Maven or the plugin is unavailable, it creates a fallback SBOM from direct `pom.xml` dependencies so the rest of the supply-chain policy demo can still run.
