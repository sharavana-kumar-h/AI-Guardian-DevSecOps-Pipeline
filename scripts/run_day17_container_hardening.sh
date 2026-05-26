#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p reports
IMAGE="${IMAGE:-local/ai-devsecops-demo:day17}"
APP_VERSION="${APP_VERSION:-0.1.0}"
VCS_REF="${VCS_REF:-$(git rev-parse --short HEAD 2>/dev/null || echo local)}"
BUILD_DATE="${BUILD_DATE:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"
IMAGE_SOURCE="${IMAGE_SOURCE:-https://github.com/YOUR_USERNAME/ai-guardian-devsecops-pipeline}"
BUILD_IMAGE="${BUILD_IMAGE:-true}"

{
  echo "# Day 17 - Container Hardening Status"
  echo
  printf 'Image: `%s`
' "$IMAGE"
} > reports/day-17-container-hardening-status.md

if [ "$BUILD_IMAGE" = "true" ]; then
  if command -v docker >/dev/null 2>&1; then
    if docker build       --build-arg APP_VERSION="$APP_VERSION"       --build-arg VCS_REF="$VCS_REF"       --build-arg BUILD_DATE="$BUILD_DATE"       --build-arg IMAGE_SOURCE="$IMAGE_SOURCE"       -t "$IMAGE" . | tee reports/day-17-docker-build.log; then
      echo "- Docker build: succeeded" >> reports/day-17-container-hardening-status.md
    else
      echo "- Docker build: failed or Docker daemon unavailable; metadata report will use Dockerfile evidence" >> reports/day-17-container-hardening-status.md
    fi
  else
    echo "- Docker build: skipped because docker is unavailable" >> reports/day-17-container-hardening-status.md
  fi
else
  echo "- Docker build: skipped by BUILD_IMAGE=false" >> reports/day-17-container-hardening-status.md
fi

python3 scripts/image_metadata_report.py --image "$IMAGE" --dockerfile Dockerfile --policy config/container-security-policy.json
printf '%s
' '- Metadata report: `reports/image-metadata.md`' >> reports/day-17-container-hardening-status.md
