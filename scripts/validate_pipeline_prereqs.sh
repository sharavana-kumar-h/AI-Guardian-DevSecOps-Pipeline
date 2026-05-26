#!/usr/bin/env bash
set -euo pipefail

required=(python3 mvn)
optional=(docker trivy conftest kubectl kind aws eksctl)

missing_required=()
missing_optional=()

for tool in "${required[@]}"; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    missing_required+=("$tool")
  fi
done

for tool in "${optional[@]}"; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    missing_optional+=("$tool")
  fi
done

mkdir -p reports
{
  echo "# Pipeline Prerequisite Check"
  echo
  echo "Generated on: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "## Required tools"
  for tool in "${required[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
      echo "- $tool: OK ($(command -v "$tool"))"
    else
      echo "- $tool: MISSING"
    fi
  done
  echo
  echo "## Optional Day 3-10 tools"
  for tool in "${optional[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
      echo "- $tool: OK ($(command -v "$tool"))"
    else
      echo "- $tool: MISSING"
    fi
  done
} > reports/prereq-check.md

cat reports/prereq-check.md

if [ "${#missing_required[@]}" -gt 0 ]; then
  echo "Missing required tools: ${missing_required[*]}" >&2
  exit 1
fi

if [ "${#missing_optional[@]}" -gt 0 ]; then
  echo "Optional tools missing: ${missing_optional[*]}" >&2
  echo "Install these before running all Day 3-10 gates." >&2
fi
