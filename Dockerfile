# syntax=docker/dockerfile:1.7
FROM maven:3.9.11-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml ./
RUN mvn -B -q dependency:go-offline
COPY src ./src
RUN mvn -B clean package -DskipTests

FROM eclipse-temurin:21-jre-jammy

ARG APP_VERSION=0.1.0
ARG VCS_REF=local
ARG BUILD_DATE=1970-01-01T00:00:00Z
ARG IMAGE_SOURCE=https://github.com/YOUR_USERNAME/ai-guardian-devsecops-pipeline

LABEL org.opencontainers.image.title="AI Guardian DevSecOps Demo" \
      org.opencontainers.image.description="Spring Boot workload for AI-augmented DevSecOps pipeline demos" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="${IMAGE_SOURCE}" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appgroup \
    && useradd --system --uid 10001 --gid appgroup --home-dir /app appuser
COPY --from=build /workspace/target/*.jar /app/app.jar
RUN chown -R appuser:appgroup /app \
    && chmod 500 /app \
    && chmod 400 /app/app.jar
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD curl -fsS http://localhost:8080/actuator/health || exit 1
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-Djava.io.tmpdir=/tmp", "-jar", "/app/app.jar"]
