#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

: "${IMAGE:=local/ai-devsecops-demo:day6}"
: "${DRY_RUN:=true}"
: "${PUSH_LATEST:=false}"

printf '# Day 6 Docker Hub Publishing\n\n' > reports/day-6-docker-publish.md
printf -- '- Image: `%s`\n- Dry run: `%s`\n- Push latest: `%s`\n\n' "$IMAGE" "$DRY_RUN" "$PUSH_LATEST" >> reports/day-6-docker-publish.md

echo "Building image $IMAGE"
docker build -t "$IMAGE" .

IMAGE="$IMAGE" DRY_RUN="$DRY_RUN" PUSH_LATEST="$PUSH_LATEST" bash scripts/docker_publish.sh
cat reports/docker-publish-report.md >> reports/day-6-docker-publish.md

echo "Day 6 completed. See reports/day-6-docker-publish.md"
