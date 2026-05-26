# Day 14 SBOM Generation Result

- SBOM JSON: `reports/bom.json`
- Dependency inventory: `reports/dependency-inventory.md`
- Raw log: `reports/sbom-generation.log`

The CycloneDX Maven plugin is preferred. If Maven or the plugin is unavailable, the script creates a fallback SBOM from direct Maven dependencies so downstream policy checks can still run in demo mode.
