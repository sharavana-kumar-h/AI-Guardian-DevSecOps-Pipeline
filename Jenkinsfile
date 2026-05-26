pipeline {
    agent any

    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(name: 'ENABLE_SONAR', defaultValue: false, description: 'Day 3: Run SonarQube SAST and quality gate')
        booleanParam(name: 'ENABLE_DEP_CHECK', defaultValue: false, description: 'Day 4: Run OWASP Dependency Check SCA')
        booleanParam(name: 'ENABLE_DOCKER', defaultValue: false, description: 'Day 4: Build Docker image')
        booleanParam(name: 'ENABLE_TRIVY', defaultValue: false, description: 'Day 4: Run Trivy image scan')
        booleanParam(name: 'ENABLE_OPA', defaultValue: false, description: 'Day 5: Run OPA/Conftest policy checks')
        booleanParam(name: 'ENFORCE_SECURITY_GATES', defaultValue: false, description: 'Fail build based on collected scanner evidence')
        booleanParam(name: 'ENABLE_DOCKER_PUSH', defaultValue: false, description: 'Day 6: Push image to Docker Hub after all gates')
        booleanParam(name: 'PUSH_LATEST', defaultValue: false, description: 'Day 6: Also tag and push latest. Keep false for safer demos.')
        booleanParam(name: 'ENABLE_K8S_DEPLOY', defaultValue: false, description: 'Day 8/10: Deploy to current Kubernetes context or EKS after all gates')
        booleanParam(name: 'ENABLE_EKS_KUBECONFIG', defaultValue: false, description: 'Day 10: Run aws eks update-kubeconfig before deployment')
        booleanParam(name: 'ENABLE_DEEP_SAST', defaultValue: false, description: 'Day 11: Run secure-code review and Sonar issue triage')
        booleanParam(name: 'ENABLE_LOCAL_SONAR_POLICY', defaultValue: false, description: 'Day 12: Apply local SAST quality policy')
        booleanParam(name: 'FAIL_LOCAL_SONAR_POLICY', defaultValue: false, description: 'Day 12: Fail build when local SAST policy fails')
        booleanParam(name: 'ENABLE_AI_REMEDIATION_PLAN', defaultValue: false, description: 'Day 13: Generate developer remediation plan')
        booleanParam(name: 'ENABLE_SBOM', defaultValue: false, description: 'Day 14: Generate CycloneDX SBOM and dependency inventory')
        booleanParam(name: 'ENABLE_DEP_POLICY', defaultValue: false, description: 'Day 15: Apply dependency risk and license policies')
        booleanParam(name: 'FAIL_DEP_POLICY', defaultValue: false, description: 'Day 15: Fail build when dependency or license policy fails')
        booleanParam(name: 'ENABLE_AI_DEP_REMEDIATION', defaultValue: false, description: 'Day 16: Generate AI dependency remediation plan')
        booleanParam(name: 'ENABLE_CONTAINER_HARDENING', defaultValue: false, description: 'Day 17: Build/inspect hardened image and generate metadata report')
        booleanParam(name: 'ENABLE_TRIVY_POLICY', defaultValue: false, description: 'Day 18: Apply local Trivy vulnerability/misconfig/secret thresholds')
        booleanParam(name: 'FAIL_TRIVY_POLICY', defaultValue: false, description: 'Day 18: Fail build when Trivy policy fails')
        booleanParam(name: 'ENABLE_IMAGE_SBOM', defaultValue: false, description: 'Day 19: Generate image SBOM and provenance report')
        booleanParam(name: 'ENABLE_AI_CONTAINER_REMEDIATION', defaultValue: false, description: 'Day 20: Generate AI container remediation queue')
        booleanParam(name: 'ENABLE_MANIFEST_AI_REVIEW', defaultValue: false, description: 'Day 21: Generate AI-style Kubernetes manifest security review')
        booleanParam(name: 'ENABLE_RELEASE_READINESS', defaultValue: false, description: 'Day 22: Generate release readiness evidence report')
        booleanParam(name: 'FAIL_RELEASE_READINESS', defaultValue: false, description: 'Day 22: Fail pipeline if release readiness hard-fails')
        booleanParam(name: 'ENABLE_RDS_SECRET_RENDER', defaultValue: false, description: 'Day 23: Render RDS PostgreSQL Kubernetes Secret from CI environment')
        booleanParam(name: 'ALLOW_RDS_PLACEHOLDERS', defaultValue: true, description: 'Day 23: Allow placeholder DB values for demo-only secret output')
        booleanParam(name: 'ENABLE_RUNTIME_THREAT_ANALYSIS', defaultValue: false, description: 'Day 24: Analyze runtime logs/events for threat patterns')
        booleanParam(name: 'FAIL_ON_RUNTIME_HIGH', defaultValue: false, description: 'Day 24: Fail when runtime analyzer detects HIGH severity signals')
        booleanParam(name: 'ENABLE_FINAL_VALIDATION', defaultValue: false, description: 'Day 25: Run final offline GitHub readiness validation')
        string(name: 'AWS_REGION', defaultValue: 'ap-south-1', description: 'AWS region for EKS deployment')
        string(name: 'EKS_CLUSTER_NAME', defaultValue: 'ai-devsecops-eks', description: 'EKS cluster name')
    }

    environment {
        APP_NAME = 'ai-devsecops-demo'
        K8S_NAMESPACE = 'ai-devsecops'
        DOCKER_REPOSITORY = "${env.DOCKERHUB_USERNAME ?: 'your-dockerhub-user'}/ai-devsecops-demo"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        IMAGE = "${DOCKER_REPOSITORY}:${IMAGE_TAG}"
        SONAR_PROJECT_KEY = 'ai-devsecops-demo'
        SONAR_HOST_URL = "${env.SONAR_HOST_URL ?: 'http://localhost:9000'}"
        AWS_REGION = "${params.AWS_REGION}"
        EKS_CLUSTER_NAME = "${params.EKS_CLUSTER_NAME}"
        PUSH_LATEST = "${params.PUSH_LATEST}"
        ENABLE_EKS_KUBECONFIG = "${params.ENABLE_EKS_KUBECONFIG}"
        FAIL_LOCAL_SONAR_POLICY = "${params.FAIL_LOCAL_SONAR_POLICY}"
        FAIL_DEP_POLICY = "${params.FAIL_DEP_POLICY}"
        FAIL_TRIVY_POLICY = "${params.FAIL_TRIVY_POLICY}"
        FAIL_RELEASE_READINESS = "${params.FAIL_RELEASE_READINESS}"
        ALLOW_RDS_PLACEHOLDERS = "${params.ALLOW_RDS_PLACEHOLDERS}"
        FAIL_ON_RUNTIME_HIGH = "${params.FAIL_ON_RUNTIME_HIGH}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'mkdir -p reports'
            }
        }

        stage('Prerequisite Snapshot') {
            steps {
                sh 'bash scripts/validate_pipeline_prereqs.sh || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/prereq-check.md', allowEmptyArchive: true
                }
            }
        }

        stage('AI Secret Detection - Baseline') {
            steps {
                sh 'bash scripts/secret_scan.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/secret-scan.txt', allowEmptyArchive: true
                }
            }
        }

        stage('AI Test Case Generation') {
            steps {
                sh 'python3 scripts/ai_test_case_generator.py --source-root src/main/java --output reports/ai-test-plan.md'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/ai-test-plan.md', allowEmptyArchive: true
                }
            }
        }

        stage('Maven Build + JUnit + JaCoCo') {
            steps {
                sh 'mvn -B clean verify'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'target/surefire-reports/*.xml'
                    archiveArtifacts artifacts: 'target/site/jacoco/**, target/surefire-reports/**, target/*.jar', allowEmptyArchive: true
                }
            }
        }

        stage('Day 3 - SonarQube SAST') {
            when { expression { return params.ENABLE_SONAR } }
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn -B sonar:sonar -Dsonar.projectKey=$SONAR_PROJECT_KEY'
                }
            }
        }

        stage('Day 3 - SonarQube Quality Gate') {
            when { expression { return params.ENABLE_SONAR } }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Day 3 - Fetch Sonar Evidence') {
            when { expression { return params.ENABLE_SONAR } }
            steps {
                sh 'python3 scripts/fetch_sonar_report.py --host-url "$SONAR_HOST_URL" --project-key "$SONAR_PROJECT_KEY" --output reports/sonar-findings.json --markdown-output reports/sonar-evidence.md || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/sonar-*.json, reports/sonar-*.md', allowEmptyArchive: true
                }
            }
        }

        stage('Day 11 - Deep SAST Review') {
            when { expression { return params.ENABLE_DEEP_SAST } }
            steps {
                sh '''
                  python3 scripts/secure_code_review.py --root . --config config/secure-code-review-rules.json --json-output reports/secure-code-review.json --markdown-output reports/secure-code-review.md
                  python3 scripts/fetch_sonar_report.py --host-url "$SONAR_HOST_URL" --project-key "$SONAR_PROJECT_KEY" --output reports/sonar-findings.json --markdown-output reports/sonar-evidence.md || true
                  python3 scripts/sonar_issue_triage.py --input reports/sonar-findings.json --json-output reports/sonar-issue-triage.json --markdown-output reports/sonar-issue-triage.md
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/secure-code-review.*, reports/sonar-issue-triage.*, reports/sonar-evidence.md', allowEmptyArchive: true
                }
            }
        }

        stage('Day 12 - Local Sonar Policy') {
            when { expression { return params.ENABLE_LOCAL_SONAR_POLICY } }
            steps {
                sh '''
                  EXTRA=""
                  if [ "$FAIL_LOCAL_SONAR_POLICY" = "true" ]; then EXTRA="--fail"; fi
                  python3 scripts/sonar_sast_policy.py --sonar reports/sonar-findings.json --config config/sonar-quality-gate.json --json-output reports/sonar-policy-result.json --markdown-output reports/sonar-policy-result.md $EXTRA
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/sonar-policy-result.*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 13 - AI Remediation Plan') {
            when { expression { return params.ENABLE_AI_REMEDIATION_PLAN } }
            steps {
                sh 'python3 scripts/ai_remediation_plan.py --reports reports --output reports/ai-remediation-plan.md --json-output reports/ai-remediation-plan.json'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/ai-remediation-plan.*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 4 - OWASP Dependency Check SCA') {
            when { expression { return params.ENABLE_DEP_CHECK } }
            steps {
                sh 'mvn -B org.owasp:dependency-check-maven:check -Dformat=ALL -DfailBuildOnCVSS=11 || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'target/dependency-check-report/**', allowEmptyArchive: true
                }
            }
        }

        stage('Day 14 - SBOM + Dependency Inventory') {
            when { expression { return params.ENABLE_SBOM || params.ENABLE_DEP_POLICY || params.ENABLE_AI_DEP_REMEDIATION } }
            steps {
                sh 'bash scripts/run_day14_sca_inventory.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/bom.*, reports/sbom-*, reports/dependency-inventory.*, reports/day-14-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 15 - Dependency Risk + License Policy') {
            when { expression { return params.ENABLE_DEP_POLICY || params.ENABLE_AI_DEP_REMEDIATION } }
            steps {
                sh '''
                  if [ "$FAIL_DEP_POLICY" = "true" ]; then
                    FAIL_DEP_POLICY=true bash scripts/run_day15_dependency_policy.sh
                  else
                    bash scripts/run_day15_dependency_policy.sh
                  fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/sca-policy-result.*, reports/license-policy-result.*, reports/day-15-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 16 - AI Dependency Remediation') {
            when { expression { return params.ENABLE_AI_DEP_REMEDIATION } }
            steps {
                sh 'bash scripts/run_day16_ai_dependency_remediation.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/ai-dependency-remediation.*, reports/ai-security-report.md, reports/day-16-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 4 - Docker Build') {
            when { expression { return params.ENABLE_DOCKER } }
            steps {
                sh '''
                  docker build \
                    --build-arg APP_VERSION=0.1.0 \
                    --build-arg VCS_REF=${GIT_COMMIT:-local} \
                    --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
                    --build-arg IMAGE_SOURCE=${GIT_URL:-local} \
                    -t $IMAGE .
                '''
            }
        }

        stage('Day 17 - Container Metadata and Hardening') {
            when { expression { return params.ENABLE_CONTAINER_HARDENING || params.ENABLE_IMAGE_SBOM || params.ENABLE_AI_CONTAINER_REMEDIATION } }
            steps {
                sh '''
                  BUILD_IMAGE_FLAG=true
                  if [ "${ENABLE_DOCKER:-false}" = "true" ]; then BUILD_IMAGE_FLAG=false; fi
                  BUILD_IMAGE="$BUILD_IMAGE_FLAG" IMAGE="$IMAGE" bash scripts/run_day17_container_hardening.sh
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/image-metadata.*, reports/day-17-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 4 - Trivy Image Scan') {
            when { expression { return params.ENABLE_TRIVY } }
            steps {
                sh '''
                  mkdir -p reports
                  trivy image --config config/trivy.yaml --format json --output reports/trivy-image.json --exit-code 0 $IMAGE
                  trivy image --config config/trivy.yaml --format table --output reports/trivy-image.txt --exit-code 0 $IMAGE || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/trivy-image.*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 18 - Trivy Policy Enforcement') {
            when { expression { return params.ENABLE_TRIVY_POLICY || params.ENABLE_AI_CONTAINER_REMEDIATION } }
            steps {
                sh '''
                  if [ "$FAIL_TRIVY_POLICY" = "true" ]; then
                    FAIL_TRIVY_POLICY=true IMAGE="$IMAGE" bash scripts/run_day18_trivy_policy.sh
                  else
                    IMAGE="$IMAGE" bash scripts/run_day18_trivy_policy.sh
                  fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/trivy-policy-result.*, reports/day-18-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 4 - AI CVE Prioritization + Container Risk') {
            when { expression { return params.ENABLE_DEP_CHECK || params.ENABLE_TRIVY } }
            steps {
                sh '''
                  python3 scripts/ai_cve_prioritizer.py
                  python3 scripts/container_risk_score.py --dockerfile Dockerfile --trivy reports/trivy-image.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/ai-cve-priorities.*, reports/ai-container-risk.*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 19 - Image SBOM and Provenance') {
            when { expression { return params.ENABLE_IMAGE_SBOM || params.ENABLE_AI_CONTAINER_REMEDIATION } }
            steps {
                sh 'IMAGE="$IMAGE" bash scripts/run_day19_image_sbom_provenance.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/image-sbom*, reports/image-provenance.*, reports/image-metadata.*, reports/day-19-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 20 - AI Container Remediation') {
            when { expression { return params.ENABLE_AI_CONTAINER_REMEDIATION } }
            steps {
                sh 'IMAGE="$IMAGE" bash scripts/run_day20_ai_container_remediation.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/ai-container-remediation.*, reports/ai-security-report.md, reports/day-20-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 5 - Render Kubernetes Manifests') {
            when { expression { return params.ENABLE_OPA || params.ENABLE_K8S_DEPLOY } }
            steps {
                sh 'bash scripts/render_k8s_manifests.sh "$IMAGE" reports/rendered-k8s'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/rendered-k8s/**', allowEmptyArchive: true
                }
            }
        }

        stage('Day 7 - Kubernetes Hardening Review') {
            when { expression { return params.ENABLE_OPA || params.ENABLE_K8S_DEPLOY } }
            steps {
                sh 'python3 scripts/k8s_hardening_check.py --path reports/rendered-k8s --output reports/k8s-hardening-report.md'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/k8s-hardening-report.md', allowEmptyArchive: true
                }
            }
        }

        stage('Day 21 - AI Kubernetes Manifest Security Review') {
            when { expression { return params.ENABLE_MANIFEST_AI_REVIEW || params.ENABLE_K8S_DEPLOY } }
            steps {
                sh 'bash scripts/run_day21_manifest_security_review.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/manifest-security-review.*, reports/day-21-*, reports/ai-security-report.md', allowEmptyArchive: true
                }
            }
        }

        stage('Day 5 - OPA/Conftest Policy Checks') {
            when { expression { return params.ENABLE_OPA } }
            steps {
                sh '''
                  mkdir -p reports
                  conftest test Dockerfile --policy policies --output json > reports/conftest-dockerfile.json
                  conftest test Dockerfile --policy policies --output table > reports/conftest-dockerfile.txt
                  conftest test reports/rendered-k8s --policy policies --output json > reports/conftest-k8s.json
                  conftest test reports/rendered-k8s --policy policies --output table > reports/conftest-k8s.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/conftest-*', allowEmptyArchive: true
                }
            }
        }

        stage('AI Security Report') {
            steps {
                sh 'python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/ai-security-report.md', allowEmptyArchive: true
                }
            }
        }

        stage('Security Gate Enforcement') {
            when { expression { return params.ENFORCE_SECURITY_GATES } }
            steps {
                sh 'python3 scripts/enforce_security_gates.py --reports reports --allow-sonar-unavailable'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/security-gate-result.md', allowEmptyArchive: true
                }
            }
        }

        stage('Day 22 - Release Readiness') {
            when { expression { return params.ENABLE_RELEASE_READINESS } }
            steps {
                sh 'bash scripts/run_day22_release_readiness.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/release-readiness.*, reports/day-22-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 6 - Docker Hub Publish') {
            when { expression { return params.ENABLE_DOCKER_PUSH } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'DRY_RUN=false IMAGE="$IMAGE" PUSH_LATEST="$PUSH_LATEST" bash scripts/docker_publish.sh'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/docker-publish-report.md, reports/docker-push.log, reports/image-digest.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Day 9 - AWS/EKS Prerequisite Snapshot') {
            when { expression { return params.ENABLE_K8S_DEPLOY && params.ENABLE_EKS_KUBECONFIG } }
            steps {
                sh 'bash scripts/check_aws_eks_prereqs.sh || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/aws-eks-prereq-check.md, reports/aws-caller-identity.json', allowEmptyArchive: true
                }
            }
        }

        stage('Day 23 - RDS Secret Render') {
            when { expression { return params.ENABLE_RDS_SECRET_RENDER || params.ENABLE_K8S_DEPLOY } }
            steps {
                sh 'bash scripts/run_day23_rds_integration.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/rds-integration-report.md, reports/generated-rds-secret.yaml, reports/day-23-*', allowEmptyArchive: true
                }
            }
        }

        stage('Day 10 - Deploy to Kubernetes/EKS') {
            when { expression { return params.ENABLE_K8S_DEPLOY } }
            steps {
                sh '''
                  if [ "$ENABLE_EKS_KUBECONFIG" = "true" ]; then
                    aws eks update-kubeconfig --name "$EKS_CLUSTER_NAME" --region "$AWS_REGION"
                  fi
                  kubectl apply -f reports/rendered-k8s/namespace.yaml
                  kubectl apply -f reports/rendered-k8s/configmap.yaml
                  if [ -f reports/generated-rds-secret.yaml ]; then kubectl apply -f reports/generated-rds-secret.yaml; else kubectl apply -f reports/rendered-k8s/secret.template.yaml; fi
                  kubectl apply -f reports/rendered-k8s/rbac.yaml
                  kubectl apply -f reports/rendered-k8s/deployment.yaml
                  kubectl apply -f reports/rendered-k8s/service.yaml
                  kubectl apply -f reports/rendered-k8s/network-policy.yaml
                  kubectl apply -f reports/rendered-k8s/pdb.yaml || true
                  kubectl apply -f reports/rendered-k8s/hpa.yaml || true
                  kubectl rollout status deployment/$APP_NAME -n $K8S_NAMESPACE --timeout=300s
                  kubectl -n $K8S_NAMESPACE get deploy,pods,svc,hpa,pdb -o wide | tee reports/k8s-workload-status.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/k8s-workload-status.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Runtime Signal Collection') {
            when { expression { return params.ENABLE_K8S_DEPLOY } }
            steps {
                sh 'bash scripts/collect_runtime_signals.sh $K8S_NAMESPACE'
                sh 'python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/runtime-signals.txt, reports/ai-security-report.md', allowEmptyArchive: true
                }
            }
        }

        stage('Day 24 - AI Runtime Threat Analysis') {
            when { expression { return params.ENABLE_RUNTIME_THREAT_ANALYSIS || params.ENABLE_K8S_DEPLOY } }
            steps {
                sh 'bash scripts/run_day24_runtime_threat_detection.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/runtime-threat-summary.*, reports/runtime-signals.txt, reports/day-24-*, reports/ai-security-report.md', allowEmptyArchive: true
                }
            }
        }

        stage('Day 25 - Final GitHub Readiness Validation') {
            when { expression { return params.ENABLE_FINAL_VALIDATION } }
            steps {
                sh 'bash scripts/run_day25_final_validation.sh'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/final-validation.*, reports/day-25-*, reports/ai-security-report.md', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            cleanWs(deleteDirs: true, notFailBuild: true)
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check the security gate or build stage above.'
        }
    }
}
