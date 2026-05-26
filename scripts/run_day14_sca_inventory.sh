#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports
bash scripts/generate_sbom.sh
python3 scripts/dependency_inventory.py --sbom reports/bom.json --json-output reports/dependency-inventory.json --markdown-output reports/dependency-inventory.md
cat > reports/day-14-sca-inventory-status.md <<'EOF'
# Day 14 Status

Completed SBOM generation and dependency inventory.

Artifacts:

- `reports/bom.json`
- `reports/bom.xml` when CycloneDX Maven output is available
- `reports/dependency-inventory.json`
- `reports/dependency-inventory.md`
- `reports/sbom-generation.md`
EOF
cat reports/day-14-sca-inventory-status.md
