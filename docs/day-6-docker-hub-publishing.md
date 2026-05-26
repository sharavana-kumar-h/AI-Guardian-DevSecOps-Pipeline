# Day 6 — Docker Hub Publishing

## Goal

Publish only a security-validated Docker image to Docker Hub.

## What changed

- Added `scripts/docker_publish.sh`
- Added `scripts/run_day6_docker_publish.sh`
- Updated Jenkins to use the publish script instead of an inline push only
- Added report artifacts for Docker publish evidence

## Local dry run

```bash
export IMAGE=your-dockerhub-user/ai-devsecops-demo:day6
export DRY_RUN=true
bash scripts/run_day6_docker_publish.sh
```

## Real push

```bash
export IMAGE=your-dockerhub-user/ai-devsecops-demo:day6
export DOCKER_USER=your-dockerhub-user
export DOCKER_PASS=your-dockerhub-token
export DRY_RUN=false
bash scripts/run_day6_docker_publish.sh
```

## Security rule

The Docker push stage must happen only after build, tests, scanner evidence, policy checks, and security gate enforcement.
