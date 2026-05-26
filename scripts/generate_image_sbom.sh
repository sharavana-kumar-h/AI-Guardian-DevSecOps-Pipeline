#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p reports
IMAGE="${IMAGE:-local/ai-devsecops-demo:day19}"
OUT="${IMAGE_SBOM_OUT:-reports/image-sbom.cdx.json}"
IMAGE_SBOM_TIMEOUT="${IMAGE_SBOM_TIMEOUT:-30s}"
LOG="reports/image-sbom-generation.log"
MD="reports/image-sbom-generation.md"

{
  echo "# Day 19 - Container Image SBOM Generation"
  echo
  printf 'Image: `%s`
' "$IMAGE"
  printf 'Output: `%s`
' "$OUT"
  echo
} > "$MD"

if command -v trivy >/dev/null 2>&1; then
  echo "Using Trivy CycloneDX SBOM mode" | tee "$LOG"
  if timeout "$IMAGE_SBOM_TIMEOUT" trivy image --format cyclonedx --output "$OUT" --exit-code 0 "$IMAGE" >> "$LOG" 2>&1; then
    echo "- Generator: Trivy" >> "$MD"
    echo "- Status: generated" >> "$MD"
    exit 0
  fi
  echo "Trivy SBOM generation failed; trying Syft fallback" >> "$LOG"
fi

if command -v syft >/dev/null 2>&1; then
  echo "Using Syft CycloneDX JSON mode" >> "$LOG"
  if timeout "$IMAGE_SBOM_TIMEOUT" syft "$IMAGE" -o cyclonedx-json="$OUT" >> "$LOG" 2>&1; then
    echo "- Generator: Syft" >> "$MD"
    echo "- Status: generated" >> "$MD"
    exit 0
  fi
  echo "Syft SBOM generation failed; creating fallback SBOM" >> "$LOG"
fi

cat > "$OUT" <<JSON
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "metadata": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "component": {
      "type": "container",
      "name": "$IMAGE"
    },
    "properties": [
      {"name": "generated_by", "value": "fallback"},
      {"name": "reason", "value": "trivy/syft unavailable or image inaccessible"}
    ]
  },
  "components": []
}
JSON
{
  echo "- Generator: fallback"
  echo "- Status: generated minimal SBOM"
  echo "- Note: install Trivy or Syft and ensure the image exists locally/registry-side for a full image SBOM."
} >> "$MD"
