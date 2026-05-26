#!/usr/bin/env bash
set -euo pipefail

IMAGE="${1:-${IMAGE:-local/ai-devsecops-demo:dev}}"
OUTPUT_DIR="${2:-reports/rendered-k8s}"

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

for file in k8s/*.yaml; do
  name="$(basename "$file")"
  sed "s|IMAGE_PLACEHOLDER|$IMAGE|g" "$file" > "$OUTPUT_DIR/$name"
done

echo "Rendered Kubernetes manifests to $OUTPUT_DIR using image $IMAGE"
