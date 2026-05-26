#!/usr/bin/env python3
"""
AI-ready test case generation helper.

Offline mode deliberately does not invent scanner results. It reads the current Java sources,
extracts obvious API/service contracts, and writes a structured Markdown test plan. In a real
pipeline, the Markdown prompt section can be sent to an LLM endpoint and reviewed before tests
are committed.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceSummary:
    path: Path
    class_name: str
    methods: list[str]
    endpoints: list[str]


def read_sources(source_root: Path) -> list[SourceSummary]:
    summaries: list[SourceSummary] = []
    for path in sorted(source_root.rglob("*.java")):
        text = path.read_text(encoding="utf-8")
        class_match = re.search(r"\b(class|record|interface)\s+(\w+)", text)
        class_name = class_match.group(2) if class_match else path.stem
        methods = re.findall(r"(?:public|private|protected)\s+[\w<>.?]+\s+(\w+)\s*\([^)]*\)", text)
        endpoints = []
        for annotation in ("GetMapping", "PostMapping", "PutMapping", "DeleteMapping", "PatchMapping", "RequestMapping"):
            for match in re.finditer(rf"@{annotation}(?:\(([^)]*)\))?", text):
                endpoint = match.group(1) or '"/"'
                endpoints.append(f"{annotation}({endpoint})")
        summaries.append(SourceSummary(path, class_name, methods, endpoints))
    return summaries


def build_markdown(summaries: list[SourceSummary]) -> str:
    service_classes = [s for s in summaries if "service" in str(s.path).lower()]
    controller_classes = [s for s in summaries if "controller" in str(s.path).lower()]
    model_classes = [s for s in summaries if "model" in str(s.path).lower()]

    lines: list[str] = [
        "# Day 2 AI Test Case Generation Report",
        "",
        "## Objective",
        "Generate and track tests before the pipeline proceeds to security scanning. The scanner and test reports remain the source of truth; AI is used to suggest additional cases and reduce blind spots.",
        "",
        "## Detected source surface",
    ]

    for summary in summaries:
        rel = summary.path.as_posix().split("src/main/java/", 1)[-1]
        lines.append(f"- `{rel}` — `{summary.class_name}`")
        if summary.methods:
            lines.append(f"  - Methods: {', '.join(sorted(set(summary.methods)))}")
        if summary.endpoints:
            lines.append(f"  - Mappings: {', '.join(summary.endpoints)}")

    lines.extend([
        "",
        "## Recommended Day 2 test cases",
        "",
        "### Service/unit tests",
        "- Supported operations: add, subtract, multiply, divide.",
        "- Numeric edge cases: negative numbers, decimal results, zero dividend.",
        "- Defensive cases: unsupported operation, null/blank operation, division by zero.",
        "- Normalization cases: uppercase and whitespace-padded operations.",
        "",
        "### Controller/API tests",
        "- `POST /api/calculator` returns expression and result for valid input.",
        "- Invalid request body returns HTTP 400 before business logic runs.",
        "- `GET /api/calculator/history` returns stored calculation records.",
        "",
        "### Persistence/model tests",
        "- Calculation records preserve expression, result, and creation timestamp.",
        "- Database-backed repository tests can be added on Day 6 when PostgreSQL/RDS work begins.",
        "",
        "## Coverage gate",
        "- Current JaCoCo gate target: 70% instruction coverage at bundle level.",
        "- Treat this as the minimum. Raise it gradually after controller and persistence tests mature.",
        "",
        "## LLM prompt for expanding tests",
        "```text",
        "You are reviewing a Java Spring Boot calculator API for test coverage. Based on the source surface below, propose missing JUnit 5 tests only. Do not rewrite production code unless a clear defect is found. Group suggestions as service, controller, validation, persistence, and security abuse cases.",
        "",
    ])

    for summary in service_classes + controller_classes + model_classes:
        rel = summary.path.as_posix().split("src/main/java/", 1)[-1]
        lines.append(f"File: {rel}")
        lines.append(f"Class: {summary.class_name}")
        if summary.methods:
            lines.append(f"Methods: {', '.join(sorted(set(summary.methods)))}")
        if summary.endpoints:
            lines.append(f"Endpoints: {', '.join(summary.endpoints)}")
        lines.append("")

    lines.extend([
        "Return output as:",
        "1. Missing critical tests",
        "2. Nice-to-have tests",
        "3. Test data table",
        "4. Any production defects discovered",
        "```",
        "",
        "## Day 2 status",
        "- AI test-plan generation: implemented as an offline deterministic report.",
        "- Human/LLM review step: optional; commit generated tests only after review.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an AI-ready test case report for the project.")
    parser.add_argument("--source-root", default="src/main/java", help="Java source root to inspect")
    parser.add_argument("--output", default="reports/ai-test-plan.md", help="Markdown report path")
    args = parser.parse_args()

    source_root = Path(args.source_root)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if not source_root.exists():
        raise SystemExit(f"Source root not found: {source_root}")

    summaries = read_sources(source_root)
    output.write_text(build_markdown(summaries), encoding="utf-8")
    print(f"AI-ready test case report written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
