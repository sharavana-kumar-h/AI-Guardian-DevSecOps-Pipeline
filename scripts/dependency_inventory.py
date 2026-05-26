#!/usr/bin/env python3
"""Create a dependency inventory from pom.xml and an optional CycloneDX SBOM."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def text(node: ET.Element | None, default: str = "") -> str:
    return (node.text or default).strip() if node is not None else default


def parse_properties(root: ET.Element) -> dict[str, str]:
    props: dict[str, str] = {}
    props_node = root.find("m:properties", NS)
    if props_node is not None:
        for child in list(props_node):
            key = child.tag.split("}", 1)[-1]
            props[key] = text(child)
    return props


def resolve(value: str, props: dict[str, str]) -> str:
    if value.startswith("${") and value.endswith("}"):
        return props.get(value[2:-1], value)
    return value


def parse_pom(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    root = ET.parse(path).getroot()
    props = parse_properties(root)
    deps: list[dict[str, str]] = []
    deps_node = root.find("m:dependencies", NS)
    if deps_node is None:
        return deps
    for dep in deps_node.findall("m:dependency", NS):
        scope = text(dep.find("m:scope", NS), "compile")
        version = text(dep.find("m:version", NS), "managed-by-parent-or-bom")
        deps.append(
            {
                "group_id": text(dep.find("m:groupId", NS)),
                "artifact_id": text(dep.find("m:artifactId", NS)),
                "version": resolve(version, props),
                "scope": scope,
                "direct": "true",
                "source": "pom.xml",
            }
        )
    return deps


def find_sbom(explicit: str | None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            Path("target/bom.json"),
            Path("reports/bom.json"),
            Path("reports/sbom.json"),
            Path("reports/sbom-fallback.json"),
        ]
    )
    for path in candidates:
        if path.exists():
            return path
    return None


def parse_sbom(path: Path | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if path is None:
        return [], {"available": False, "path": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return [], {"available": False, "path": str(path), "error": "invalid JSON"}
    components: list[dict[str, Any]] = []
    for component in data.get("components", []) or []:
        components.append(
            {
                "name": component.get("name", "unknown"),
                "group": component.get("group", ""),
                "version": component.get("version", "unknown"),
                "type": component.get("type", "library"),
                "scope": component.get("scope", "unknown"),
                "purl": component.get("purl", ""),
                "licenses": component.get("licenses", []) or [],
            }
        )
    metadata = {
        "available": True,
        "path": str(path),
        "bom_format": data.get("bomFormat", "unknown"),
        "spec_version": data.get("specVersion", "unknown"),
        "serial_number": data.get("serialNumber", "not-present"),
    }
    return components, metadata


def markdown(report: dict[str, Any]) -> str:
    direct = report["direct_dependencies"]
    components = report["sbom_components"]
    scope_counts = report["scope_counts"]
    sbom = report["sbom_metadata"]
    direct_rows = "\n".join(
        f"| `{d['group_id']}:{d['artifact_id']}` | `{d['version']}` | `{d['scope']}` |" for d in direct
    ) or "| _none_ | _none_ | _none_ |"
    top_components = "\n".join(
        f"| `{c.get('group') or '-'}:{c.get('name')}` | `{c.get('version')}` | `{c.get('scope')}` |" for c in components[:25]
    ) or "| _SBOM not generated yet_ | _-_ | _-_ |"
    scope_lines = "\n".join(f"- **{scope}**: {count}" for scope, count in sorted(scope_counts.items())) or "- No scope data available"
    sbom_status = "available" if sbom.get("available") else "missing"
    return f"""# Day 14 Dependency Inventory and SBOM Summary

Generated: {report['generated_at']}

## SBOM Status

- Status: **{sbom_status}**
- Path: `{sbom.get('path')}`
- Format: `{sbom.get('bom_format', 'unknown')}`
- Spec version: `{sbom.get('spec_version', 'unknown')}`
- Components discovered from SBOM: **{len(components)}**
- Direct dependencies from `pom.xml`: **{len(direct)}**

## Dependency Scope Counts

{scope_lines}

## Direct Maven Dependencies

| Dependency | Version | Scope |
|---|---:|---|
{direct_rows}

## First 25 SBOM Components

| Component | Version | Scope |
|---|---:|---|
{top_components}

## Supply-Chain Notes

1. Archive the SBOM with every Jenkins build so later vulnerability investigations can identify exactly what shipped.
2. Treat direct dependencies as the fastest patch path; transitive dependency fixes may require parent upgrades or exclusions.
3. Regenerate the SBOM after every dependency or base-image change.
4. Use this inventory as input for the Day 15 dependency and license policy checks.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pom", default="pom.xml")
    parser.add_argument("--sbom", default=None)
    parser.add_argument("--json-output", default="reports/dependency-inventory.json")
    parser.add_argument("--markdown-output", default="reports/dependency-inventory.md")
    args = parser.parse_args()

    direct = parse_pom(Path(args.pom))
    sbom_path = find_sbom(args.sbom)
    components, metadata = parse_sbom(sbom_path)
    scope_counts: dict[str, int] = {}
    for dep in direct:
        scope_counts[dep["scope"]] = scope_counts.get(dep["scope"], 0) + 1
    for component in components:
        scope = str(component.get("scope") or "unknown")
        scope_counts[scope] = scope_counts.get(scope, 0) + 1

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "direct_dependencies": direct,
        "sbom_metadata": metadata,
        "sbom_components": components,
        "scope_counts": scope_counts,
    }
    json_path = Path(args.json_output)
    md_path = Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(f"Wrote {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
