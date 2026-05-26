# Day 2 AI Test Case Generation Report

## Objective
Generate and track tests before the pipeline proceeds to security scanning. The scanner and test reports remain the source of truth; AI is used to suggest additional cases and reduce blind spots.

## Detected source surface
- `com/example/devsecops/DevSecOpsDemoApplication.java` — `DevSecOpsDemoApplication`
- `com/example/devsecops/controller/CalculatorController.java` — `CalculatorController`
  - Methods: CalculationRequest, CalculationResponse, calculate, history
  - Mappings: GetMapping("/history"), PostMapping("/"), RequestMapping("/api/calculator")
- `com/example/devsecops/controller/HealthController.java` — `HealthController`
  - Mappings: GetMapping("/")
- `com/example/devsecops/model/CalculationRecord.java` — `CalculationRecord`
  - Methods: getCreatedAt, getExpression, getId, getResult
- `com/example/devsecops/repository/CalculationRepository.java` — `CalculationRepository`
- `com/example/devsecops/service/CalculatorService.java` — `CalculatorService`
  - Methods: calculate, divide, normalizeOperation

## Recommended Day 2 test cases

### Service/unit tests
- Supported operations: add, subtract, multiply, divide.
- Numeric edge cases: negative numbers, decimal results, zero dividend.
- Defensive cases: unsupported operation, null/blank operation, division by zero.
- Normalization cases: uppercase and whitespace-padded operations.

### Controller/API tests
- `POST /api/calculator` returns expression and result for valid input.
- Invalid request body returns HTTP 400 before business logic runs.
- `GET /api/calculator/history` returns stored calculation records.

### Persistence/model tests
- Calculation records preserve expression, result, and creation timestamp.
- Database-backed repository tests can be added on Day 6 when PostgreSQL/RDS work begins.

## Coverage gate
- Current JaCoCo gate target: 70% instruction coverage at bundle level.
- Treat this as the minimum. Raise it gradually after controller and persistence tests mature.

## LLM prompt for expanding tests
```text
You are reviewing a Java Spring Boot calculator API for test coverage. Based on the source surface below, propose missing JUnit 5 tests only. Do not rewrite production code unless a clear defect is found. Group suggestions as service, controller, validation, persistence, and security abuse cases.

File: com/example/devsecops/service/CalculatorService.java
Class: CalculatorService
Methods: calculate, divide, normalizeOperation

File: com/example/devsecops/controller/CalculatorController.java
Class: CalculatorController
Methods: CalculationRequest, CalculationResponse, calculate, history
Endpoints: GetMapping("/history"), PostMapping("/"), RequestMapping("/api/calculator")

File: com/example/devsecops/controller/HealthController.java
Class: HealthController
Endpoints: GetMapping("/")

File: com/example/devsecops/model/CalculationRecord.java
Class: CalculationRecord
Methods: getCreatedAt, getExpression, getId, getResult

Return output as:
1. Missing critical tests
2. Nice-to-have tests
3. Test data table
4. Any production defects discovered
```

## Day 2 status
- AI test-plan generation: implemented as an offline deterministic report.
- Human/LLM review step: optional; commit generated tests only after review.
