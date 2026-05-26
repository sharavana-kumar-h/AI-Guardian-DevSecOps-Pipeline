#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p reports
IMAGE="${IMAGE:-local/ai-devsecops-demo:day19}"

bash scripts/generate_image_sbom.sh
python3 scripts/image_metadata_report.py --image "$IMAGE" --dockerfile Dockerfile --policy config/container-security-policy.json
python3 scripts/image_provenance_report.py --image "$IMAGE" --sbom reports/image-sbom.cdx.json --metadata reports/image-metadata.json

{
  echo "# Day 19 - Image SBOM and Provenance Status"
  echo
  printf 'Image: `%s`
' "$IMAGE"
  echo
  echo "Generated:"
  echo
  echo "- \`reports/image-sbom.cdx.json\`"
  echo "- \`reports/image-sbom-generation.md\`"
  echo "- \`reports/image-metadata.md\`"
  echo "- \`reports/image-provenance.md\`"
} > reports/day-19-image-sbom-provenance-status.md
