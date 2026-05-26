# Day 23 - RDS PostgreSQL Integration Report

## Rendered Kubernetes secret

- Output: `reports/generated-rds-secret.yaml`
- Namespace: `ai-devsecops`
- Secret name: `ai-devsecops-demo-db`

## Connection values

- SPRING_DATASOURCE_URL: `jdbc:postgresql://YOUR_RDS_ENDPOINT:5432/devsecops`
- SPRING_DATASOURCE_USERNAME: `devsecops_user`
- SPRING_DATASOURCE_PASSWORD: `CH****ME`
- SPRING_DATASOURCE_DRIVER: `org.postgresql.Driver`
- SPRING_JPA_HIBERNATE_DDL_AUTO: `validate`

## Security note

Do not commit real RDS credentials. Use Jenkins credentials, AWS Secrets Manager, External Secrets, Sealed Secrets, or a short-lived CI secret injection flow for real deployments.
