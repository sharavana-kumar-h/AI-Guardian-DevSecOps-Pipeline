#!/usr/bin/env python3
"""Render a Kubernetes Secret manifest for the Spring Boot RDS PostgreSQL connection."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def masked(value: str) -> str:
    if not value:
        return "<empty>"
    if len(value) <= 4:
        return "****"
    return value[:2] + "****" + value[-2:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default=os.getenv("K8S_NAMESPACE", "ai-devsecops"))
    parser.add_argument("--name", default="ai-devsecops-demo-db")
    parser.add_argument("--output", default="reports/generated-rds-secret.yaml")
    parser.add_argument("--report", default="reports/rds-integration-report.md")
    parser.add_argument("--allow-placeholders", action="store_true")
    args = parser.parse_args()

    url = os.getenv("SPRING_DATASOURCE_URL", "jdbc:postgresql://YOUR_RDS_ENDPOINT:5432/devsecops")
    username = os.getenv("SPRING_DATASOURCE_USERNAME", "devsecops_user")
    password = os.getenv("SPRING_DATASOURCE_PASSWORD", "CHANGE_ME")
    driver = os.getenv("SPRING_DATASOURCE_DRIVER", "org.postgresql.Driver")
    ddl = os.getenv("SPRING_JPA_HIBERNATE_DDL_AUTO", "validate")

    placeholders = [item for item in [url, username, password] if "YOUR_" in item or item in {"CHANGE_ME", "devsecops_user"}]
    if placeholders and not args.allow_placeholders:
        print("RDS secret render blocked because placeholder values are still present. Use --allow-placeholders for documentation-only output.")
        return 1

    manifest = f"""apiVersion: v1
kind: Secret
metadata:
  name: {args.name}
  namespace: {args.namespace}
type: Opaque
stringData:
  SPRING_DATASOURCE_URL: "{url}"
  SPRING_DATASOURCE_USERNAME: "{username}"
  SPRING_DATASOURCE_PASSWORD: "{password}"
  SPRING_DATASOURCE_DRIVER: "{driver}"
  SPRING_JPA_HIBERNATE_DDL_AUTO: "{ddl}"
"""
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(manifest, encoding="utf-8")

    report = "\n".join([
        "# Day 23 - RDS PostgreSQL Integration Report",
        "",
        "## Rendered Kubernetes secret",
        "",
        f"- Output: `{args.output}`",
        f"- Namespace: `{args.namespace}`",
        f"- Secret name: `{args.name}`",
        "",
        "## Connection values",
        "",
        f"- SPRING_DATASOURCE_URL: `{url}`",
        f"- SPRING_DATASOURCE_USERNAME: `{username}`",
        f"- SPRING_DATASOURCE_PASSWORD: `{masked(password)}`",
        f"- SPRING_DATASOURCE_DRIVER: `{driver}`",
        f"- SPRING_JPA_HIBERNATE_DDL_AUTO: `{ddl}`",
        "",
        "## Security note",
        "",
        "Do not commit real RDS credentials. Use Jenkins credentials, AWS Secrets Manager, External Secrets, Sealed Secrets, or a short-lived CI secret injection flow for real deployments.",
        "",
    ])
    Path(args.report).write_text(report, encoding="utf-8")
    print(f"RDS secret manifest written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
