#!/usr/bin/env python3
"""Evaluate CycloneDX SBOM component licenses against a local license policy."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def license_names(licenses: list[Any]) -> list[str]:
    values: list[str] = []
    for item in licenses or []:
        if not isinstance(item, dict):
            continue
        lic = item.get("license") or {}
        if isinstance(lic, dict):
            value = lic.get("id") or lic.get("name")
            if value:
                values.append(str(value))
        expr = item.get("expression")
        if expr:
            values.append(str(expr))
    return values


def component_id(component: dict[str, Any]) -> str:
    group = component.get("group") or ""
    name = component.get("name") or "unknown"
    version = component.get("version") or "unknown"
    return f"{group}:{name}:{version}" if group else f"{name}:{version}"


def evaluate(sbom: dict[str, Any] | None, policy: dict[str, Any]) -> dict[str, Any]:
    allowed = set(policy.get("allowed_license_ids", []))
    deny_keywords = [str(item).lower() for item in policy.get("deny_license_keywords", [])]
    warn_keywords = [str(item).lower() for item in policy.get("warn_license_keywords", [])]
    components = sbom.get("components", []) if isinstance(sbom, dict) else []
    denied: list[dict[str, Any]] = []
    warned: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    allowed_components: list[dict[str, Any]] = []

    for component in components:
        names = license_names(component.get("licenses", []) or [])
        cid = component_id(component)
        if not names:
            unknown.append({"component": cid, "reason": "missing license metadata"})
            continue
        lowered = " | ".join(names).lower()
        if any(keyword in lowered for keyword in deny_keywords):
            denied.append({"component": cid, "licenses": names})
        elif any(keyword in lowered for keyword in warn_keywords):
            warned.append({"component": cid, "licenses": names})
        elif allowed and not any(name in allowed for name in names):
            warned.append({"component": cid, "licenses": names, "reason": "not in allowlist"})
        else:
            allowed_components.append({"component": cid, "licenses": names})

    failures: list[str] = []
    if policy.get("fail_on_denied_license", True) and denied:
        failures.append(f"Denied license detected on {len(denied)} component(s).")
    if policy.get("fail_on_unknown_license", False) and unknown:
        failures.append(f"Unknown license detected on {len(unknown)} component(s).")
    max_unknown = int(policy.get("max_unknown_licenses", 999999))
    if len(unknown) > max_unknown:
        failures.append(f"Unknown license count {len(unknown)} exceeds maximum {max_unknown}.")

    return {
        "component_count": len(components),
        "allowed_count": len(allowed_components),
        "denied": denied,
        "warned": warned,
        "unknown": unknown,
        "failures": failures,
    }


def markdown(report: dict[str, Any]) -> str:
    ev = report["evaluation"]
    failures = "\n".join(f"- {item}" for item in ev["failures"]) or "- None"
    denied = "\n".join(f"- `{item['component']}` -> {', '.join(item.get('licenses', []))}" for item in ev["denied"][:20]) or "- None"
    warned = "\n".join(f"- `{item['component']}` -> {', '.join(item.get('licenses', []))}" for item in ev["warned"][:20]) or "- None"
    unknown = "\n".join(f"- `{item['component']}`" for item in ev["unknown"][:30]) or "- None"
    return f"""# Day 15 License Policy Result

Generated: {report['generated_at']}

## Decision

**{report['decision']}**

## Counts

| Signal | Count |
|---|---:|
| SBOM components | {ev['component_count']} |
| Allowed license components | {ev['allowed_count']} |
| Denied license components | {len(ev['denied'])} |
| Warning license components | {len(ev['warned'])} |
| Unknown license components | {len(ev['unknown'])} |

## Failures

{failures}

## Denied Licenses

{denied}

## Warning Licenses

{warned}

## Unknown Licenses

{unknown}

## Notes

Missing license metadata is common in fallback SBOM mode. For stricter evidence, run the CycloneDX Maven plugin and archive the generated `target/bom.json`.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sbom", default="reports/bom.json")
    parser.add_argument("--policy", default="config/license-policy.json")
    parser.add_argument("--json-output", default="reports/license-policy-result.json")
    parser.add_argument("--markdown-output", default="reports/license-policy-result.md")
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args()

    policy = load_json(Path(args.policy)) or {}
    sbom = load_json(Path(args.sbom))
    ev = evaluate(sbom, policy)
    decision = "FAIL" if ev["failures"] else "PASS_WITH_WARNINGS" if ev["warned"] or ev["unknown"] else "PASS"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "sbom_path": args.sbom,
        "policy": policy,
        "evaluation": ev,
    }
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(report), encoding="utf-8")
    print(Path(args.markdown_output).read_text(encoding="utf-8"))
    if args.fail and ev["failures"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
