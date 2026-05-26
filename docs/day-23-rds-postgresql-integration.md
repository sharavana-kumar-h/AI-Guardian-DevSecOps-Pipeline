# Day 23 - RDS PostgreSQL Integration

## Objective

Prepare the application for production-style database configuration using AWS RDS PostgreSQL while keeping secrets out of Git.

## What was added

- `scripts/render_rds_secret.py`
- `scripts/run_day23_rds_integration.sh`
- `infra/rds/rds-postgres-minimal.yaml`
- `infra/rds/README.md`
- `reports/rds-integration-report.md`
- `reports/generated-rds-secret.yaml`

## Environment variables

```bash
export SPRING_DATASOURCE_URL=jdbc:postgresql://YOUR_RDS_ENDPOINT:5432/devsecops
export SPRING_DATASOURCE_USERNAME=devsecops_user
export SPRING_DATASOURCE_PASSWORD='replace-with-secret'
export SPRING_DATASOURCE_DRIVER=org.postgresql.Driver
export SPRING_JPA_HIBERNATE_DDL_AUTO=validate
```

## Run

Documentation-only output with placeholders:

```bash
export ALLOW_RDS_PLACEHOLDERS=true
bash scripts/run_day23_rds_integration.sh
```

Real secret rendering:

```bash
export ALLOW_RDS_PLACEHOLDERS=false
export SPRING_DATASOURCE_URL=jdbc:postgresql://actual-endpoint:5432/devsecops
export SPRING_DATASOURCE_USERNAME=actual_user
export SPRING_DATASOURCE_PASSWORD='actual-password'
bash scripts/run_day23_rds_integration.sh
```

## Security note

Do not commit real database credentials. Use Jenkins credentials, AWS Secrets Manager, External Secrets, or Sealed Secrets.
