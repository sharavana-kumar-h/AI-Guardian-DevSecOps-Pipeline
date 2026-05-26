# Day 2 — Maven, JUnit, JaCoCo, and AI Test Case Generation

## Goal

Day 2 turns the repository from a simple scaffold into a test-gated build. No security scanner should run against an artifact that has not passed compile, unit tests, validation tests, and coverage enforcement.

## What was added

- Parameterized JUnit 5 service tests for supported calculator operations.
- Defensive tests for division by zero, unsupported operations, and missing operation names.
- Controller tests for valid requests, request validation failures, and history retrieval.
- Model test for calculation-record construction.
- `application-test.yml` for isolated H2-backed Spring test execution.
- JaCoCo instruction coverage gate raised to 70%.
- `scripts/ai_test_case_generator.py` to generate an AI-ready test-case review report.
- Jenkins stage: `AI Test Case Generation` before `Maven Build + JUnit + JaCoCo`.

## Run Day 2 locally

```bash
bash scripts/run_local_checks.sh
```

Or run the build directly:

```bash
mvn -B clean verify
```

## Expected outputs

- `reports/ai-test-plan.md`
- `target/surefire-reports/*.xml`
- `target/site/jacoco/index.html`
- `target/site/jacoco/jacoco.xml`

## Coverage policy

The current JaCoCo gate is intentionally strict enough to matter but not so strict that it blocks early development:

```xml
<minimum>0.70</minimum>
```

Raise it later when integration tests and repository tests are added.

## AI test generation policy

The AI step is not allowed to silently commit tests. It creates a reviewable test plan. This keeps the pipeline honest:

1. Source code is scanned.
2. A structured test-plan prompt/report is generated.
3. Missing tests are reviewed by the developer.
4. Only reviewed tests are committed.
5. Maven/JUnit/JaCoCo enforce the final result.

## Day 2 completion criteria

- `mvn -B clean verify` passes.
- JaCoCo coverage gate passes.
- JUnit XML reports are generated.
- `reports/ai-test-plan.md` is generated.
- Jenkins archives test, coverage, and AI test-plan artifacts.
