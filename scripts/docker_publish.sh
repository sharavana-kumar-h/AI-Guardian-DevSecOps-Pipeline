#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

IMAGE="${IMAGE:-${1:-}}"
DOCKER_REPOSITORY="${DOCKER_REPOSITORY:-}"
IMAGE_TAG="${IMAGE_TAG:-}"
PUSH_LATEST="${PUSH_LATEST:-false}"
DRY_RUN="${DRY_RUN:-false}"

if [[ -z "$IMAGE" ]]; then
  if [[ -n "$DOCKER_REPOSITORY" && -n "$IMAGE_TAG" ]]; then
    IMAGE="${DOCKER_REPOSITORY}:${IMAGE_TAG}"
  else
    echo "ERROR: Set IMAGE or DOCKER_REPOSITORY + IMAGE_TAG." | tee reports/docker-publish-report.md
    exit 1
  fi
fi

cat > reports/docker-publish-report.md <<EOF
# Docker Publish Report

- Image: \`$IMAGE\`
- Push latest: \`$PUSH_LATEST\`
- Dry run: \`$DRY_RUN\`

EOF

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker CLI is not installed." | tee -a reports/docker-publish-report.md
  exit 1
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "Local image not found. Building $IMAGE..." | tee -a reports/docker-publish-report.md
  docker build -t "$IMAGE" .
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "DRY_RUN=true, skipping docker login and push." | tee -a reports/docker-publish-report.md
  docker image inspect "$IMAGE" --format='Image ID: {{.Id}}' | tee -a reports/docker-publish-report.md || true
  exit 0
fi

if [[ -n "${DOCKER_USER:-}" && -n "${DOCKER_PASS:-}" ]]; then
  echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
else
  echo "DOCKER_USER/DOCKER_PASS not set. Assuming docker is already logged in." | tee -a reports/docker-publish-report.md
fi

docker push "$IMAGE" | tee reports/docker-push.log
cat reports/docker-push.log >> reports/docker-publish-report.md

if [[ "$PUSH_LATEST" == "true" ]]; then
  latest_image="${IMAGE%:*}:latest"
  docker tag "$IMAGE" "$latest_image"
  docker push "$latest_image" | tee -a reports/docker-push.log
  echo "\nAlso pushed: \`$latest_image\`" >> reports/docker-publish-report.md
fi

if docker buildx version >/dev/null 2>&1; then
  docker buildx imagetools inspect "$IMAGE" > reports/image-digest.txt 2>/dev/null || true
fi

echo "\nDocker publish completed." >> reports/docker-publish-report.md
