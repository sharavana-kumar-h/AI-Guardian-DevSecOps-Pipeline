.PHONY: prereq test day3 day4 day5 day6 day7 day8 day9 day10 day11 day12 day13 day14 day15 day16 day17 day18 day19 day20 day21 day22 day23 day24 day25 local render security-report docker-publish k8s-hardening eks-prereq remediation sbom dep-policy dependency-remediation container-hardening trivy-policy image-sbom container-remediation manifest-review release-readiness rds runtime-threat final-validation

prereq:
	bash scripts/validate_pipeline_prereqs.sh

test:
	mvn -B clean verify

render:
	bash scripts/render_k8s_manifests.sh "$${IMAGE:-local/ai-devsecops-demo:dev}" reports/rendered-k8s

day3:
	RUN_DAY3_SONAR=true bash scripts/run_day3_sonar.sh

day4:
	RUN_DAY4_SECURITY=true bash scripts/run_day4_sca_container.sh

day5:
	RUN_DAY5_POLICY=true bash scripts/run_day5_policy_checks.sh

day6 docker-publish:
	bash scripts/run_day6_docker_publish.sh

day7 k8s-hardening:
	bash scripts/run_day7_k8s_hardening.sh

day8:
	bash scripts/run_day8_local_k8s.sh

day9 eks-prereq:
	bash scripts/run_day9_eks_prep.sh

day10:
	bash scripts/run_day10_eks_deploy.sh

day11:
	bash scripts/run_day11_sast_deep_scan.sh

day12:
	bash scripts/run_day12_quality_policy.sh

day13 remediation:
	bash scripts/run_day13_ai_remediation.sh

day14 sbom:
	bash scripts/run_day14_sca_inventory.sh

day15 dep-policy:
	bash scripts/run_day15_dependency_policy.sh

day16 dependency-remediation:
	bash scripts/run_day16_ai_dependency_remediation.sh


day17 container-hardening:
	bash scripts/run_day17_container_hardening.sh

day18 trivy-policy:
	bash scripts/run_day18_trivy_policy.sh

day19 image-sbom:
	bash scripts/run_day19_image_sbom_provenance.sh

day20 container-remediation:
	bash scripts/run_day20_ai_container_remediation.sh


day21 manifest-review:
	bash scripts/run_day21_manifest_security_review.sh

day22 release-readiness:
	bash scripts/run_day22_release_readiness.sh

day23 rds:
	bash scripts/run_day23_rds_integration.sh

day24 runtime-threat:
	bash scripts/run_day24_runtime_threat_detection.sh

day25 final-validation:
	bash scripts/run_day25_final_validation.sh

security-report:
	python3 scripts/ai_security_report.py --reports reports --output reports/ai-security-report.md

local:
	bash scripts/run_local_checks.sh
