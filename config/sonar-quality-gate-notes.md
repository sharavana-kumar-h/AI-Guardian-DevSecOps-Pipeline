# SonarQube Quality Gate Baseline

Recommended starter gate for this project:

- Coverage on new code: >= 70%
- Duplicated lines on new code: <= 3%
- Maintainability rating on new code: A
- Reliability rating on new code: A
- Security rating on new code: A
- Security hotspots reviewed: 100%

In Jenkins, the `waitForQualityGate abortPipeline: true` step should stop the pipeline before SCA, image build, or deployment when the gate fails.
