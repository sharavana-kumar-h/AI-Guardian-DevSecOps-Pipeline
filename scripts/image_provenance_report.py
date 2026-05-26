#!/usr/bin/env python3
"""Create a lightweight provenance/evidence report for a container image."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str]) -> str | None:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)
        return p.stdout.strip() if p.returncode == 0 else None
    except Exception:
        return None


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def md(payload: dict[str, Any]) -> str:
    lines = ["# Day 19 - Image Provenance and Traceability Report", ""]
    lines.append(f"Generated: `{payload['generated_at']}`")
    lines.append(f"Image: `{payload['image']}`")
    lines.append("")
    lines.append("## Source traceability")
    lines.append(f"- Git commit: `{payload['git'].get('commit') or 'unavailable'}`")
    lines.append(f"- Git branch: `{payload['git'].get('branch') or 'unavailable'}`")
    lines.append(f"- Working tree dirty: **{payload['git'].get('dirty')}**")
    lines.append("")
    lines.append("## Artifact hashes")
    lines.append("| Artifact | SHA-256 |")
    lines.append("|---|---|")
    for name, digest in payload['hashes'].items():
        lines.append(f"| {name} | `{digest or 'missing'}` |")
    lines.append("")
    lines.append("## Image metadata")
    meta = payload.get('image_metadata', {})
    if meta:
        lines.append(f"- Metadata findings: **{meta.get('summary',{}).get('total_findings','n/a')}**")
        lines.append(f"- High/critical metadata findings: **{meta.get('summary',{}).get('high_or_critical','n/a')}**")
        inspected = meta.get('image_inspect', {})
        if inspected.get('available'):
            lines.append(f"- Repo digests: {', '.join(inspected.get('repo_digests') or []) or 'none'}")
        else:
            lines.append(f"- Inspect unavailable: {inspected.get('reason','unknown')}")
    else:
        lines.append("- Image metadata report missing.")
    lines.append("")
    lines.append("## SBOM")
    lines.append(f"- SBOM path: `{payload['sbom'].get('path')}`")
    lines.append(f"- SBOM hash: `{payload['sbom'].get('sha256') or 'missing'}`")
    lines.append(f"- SBOM format: `{payload['sbom'].get('format')}`")
    lines.append("")
    lines.append("## Decision")
    missing = [k for k, v in payload['hashes'].items() if not v]
    if missing:
        lines.append("**REVIEW_REQUIRED** — Some expected provenance artifacts are missing: " + ", ".join(missing))
    else:
        lines.append("**PASS** — Source and build evidence files are present.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', default=os.getenv('IMAGE', 'local/ai-devsecops-demo:day19'))
    ap.add_argument('--sbom', default='reports/image-sbom.cdx.json')
    ap.add_argument('--metadata', default='reports/image-metadata.json')
    ap.add_argument('--json-output', default='reports/image-provenance.json')
    ap.add_argument('--markdown-output', default='reports/image-provenance.md')
    args = ap.parse_args()
    Path('reports').mkdir(exist_ok=True)
    sbom = Path(args.sbom)
    sbom_json = read_json(sbom, {})
    metadata = read_json(Path(args.metadata), {})
    payload = {
        'generated_at': dt.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
        'image': args.image,
        'git': {
            'commit': run(['git', 'rev-parse', 'HEAD']),
            'short_commit': run(['git', 'rev-parse', '--short', 'HEAD']),
            'branch': run(['git', 'rev-parse', '--abbrev-ref', 'HEAD']),
            'dirty': bool(run(['git', 'status', '--porcelain'])),
        },
        'hashes': {
            'Dockerfile': sha256(Path('Dockerfile')),
            'pom.xml': sha256(Path('pom.xml')),
            'Jenkinsfile': sha256(Path('Jenkinsfile')),
            'application_sbom': sha256(Path('reports/bom.json')),
            'image_sbom': sha256(sbom),
        },
        'sbom': {
            'path': str(sbom),
            'sha256': sha256(sbom),
            'format': sbom_json.get('bomFormat', 'unknown') if isinstance(sbom_json, dict) else 'unknown',
            'component_count': len(sbom_json.get('components', [])) if isinstance(sbom_json, dict) else 0,
        },
        'image_metadata': metadata,
    }
    Path(args.json_output).write_text(json.dumps(payload, indent=2))
    Path(args.markdown_output).write_text(md(payload))
    print(f"Wrote {args.markdown_output}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
