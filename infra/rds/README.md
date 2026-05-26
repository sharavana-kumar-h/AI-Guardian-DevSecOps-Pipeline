# RDS PostgreSQL Notes

This folder contains a minimal CloudFormation-style starting point for an RDS PostgreSQL instance used by the demo application.

For a real deployment, restrict the DB security group to the EKS worker node/security group, enable backups, set deletion protection, and store credentials in AWS Secrets Manager rather than plain Kubernetes Secrets.

The application reads database configuration from Kubernetes environment variables:

- `SPRING_DATASOURCE_URL`
- `SPRING_DATASOURCE_USERNAME`
- `SPRING_DATASOURCE_PASSWORD`
- `SPRING_DATASOURCE_DRIVER`
- `SPRING_JPA_HIBERNATE_DDL_AUTO`
