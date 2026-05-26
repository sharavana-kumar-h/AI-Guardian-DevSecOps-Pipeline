#!/usr/bin/env python3
"""Create a deterministic image metadata and Dockerfile hardening report."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

SEV_ORDER = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}


def run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=45)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as exc:  # pragma: no cover
        return 1, "", str(exc)


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def parse_dockerfile(path: Path) -> dict[str, Any]:
    data = {
        "path": str(path),
        "exists": path.exists(),
        "base_images": [],
        "labels": {},
        "user": None,
        "expose": [],
        "healthcheck": False,
        "entrypoint": None,
        "cmd": None,
        "apt_packages": [],
        "copy_from_build": False,
        "raw_user_lines": [],
    }
    if not path.exists():
        return data
    text = path.read_text(errors="ignore")
    logical = []
    buf = ""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        buf += stripped[:-1].strip() + " " if stripped.endswith("\\") else stripped
        if not stripped.endswith("\\"):
            logical.append(buf.strip())
            buf = ""
    if buf:
        logical.append(buf.strip())
    for line in logical:
        upper = line.upper()
        if upper.startswith("FROM "):
            image = line.split()[1]
            alias = None
            if " AS " in upper:
                alias = line.split()[-1]
            data["base_images"].append({"image": image, "alias": alias})
        elif upper.startswith("LABEL "):
            for match in re.findall(r'([A-Za-z0-9_.-]+)=(?:"([^"]*)"|([^\s]+))', line[6:]):
                key, quoted, bare = match
                data["labels"][key] = quoted or bare
        elif upper.startswith("USER "):
            data["user"] = line.split(None, 1)[1].strip()
            data["raw_user_lines"].append(line)
        elif upper.startswith("EXPOSE "):
            data["expose"].append(line.split(None, 1)[1].strip())
        elif upper.startswith("HEALTHCHECK "):
            data["healthcheck"] = True
        elif upper.startswith("ENTRYPOINT "):
            data["entrypoint"] = line.split(None, 1)[1].strip()
        elif upper.startswith("CMD "):
            data["cmd"] = line.split(None, 1)[1].strip()
        if "APT-GET INSTALL" in upper or "APT INSTALL" in upper:
            # lightweight package extraction; stop at the next shell operator
            match = re.search(r"apt(?:-get)?\s+install\s+(?:-y\s+)?(?:--no-install-recommends\s+)?(.+?)(?:\s+&&\s+|$)", line, flags=re.I)
            if match:
                pkgs = re.split(r"\s+", match.group(1).strip())
                data["apt_packages"].extend([pkg for pkg in pkgs if pkg and not pkg.startswith("-") and pkg not in {"\\"}])
        if "COPY --from=" in line:
            data["copy_from_build"] = True
    return data


def inspect_image(image: str | None) -> dict[str, Any]:
    if not image:
        return {"available": False, "reason": "IMAGE was not provided"}
    if not shutil.which("docker"):
        return {"available": False, "reason": "docker CLI is not installed"}
    code, out, err = run(["docker", "image", "inspect", image])
    if code != 0:
        return {"available": False, "reason": err or out or f"docker inspect failed for {image}"}
    try:
        payload = json.loads(out)[0]
    except Exception as exc:
        return {"available": False, "reason": f"docker inspect output could not be parsed: {exc}"}
    cfg = payload.get("Config") or {}
    return {
        "available": True,
        "id": payload.get("Id"),
        "repo_tags": payload.get("RepoTags") or [],
        "repo_digests": payload.get("RepoDigests") or [],
        "created": payload.get("Created"),
        "size": payload.get("Size"),
        "architecture": payload.get("Architecture"),
        "os": payload.get("Os"),
        "user": cfg.get("User"),
        "labels": cfg.get("Labels") or {},
        "exposed_ports": sorted((cfg.get("ExposedPorts") or {}).keys()),
        "healthcheck": cfg.get("Healthcheck"),
        "entrypoint": cfg.get("Entrypoint"),
        "cmd": cfg.get("Cmd"),
    }


def assess(policy: dict[str, Any], dockerfile: dict[str, Any], image_inspect: dict[str, Any], image: str | None, digest: str | None) -> list[dict[str, Any]]:
    req = policy.get("image_metadata_requirements", {})
    findings: list[dict[str, Any]] = []
    tag = (image or "").split(":")[-1] if image and ":" in image else ""
    if req.get("disallow_latest_tag") and tag == "latest":
        findings.append({"severity": "HIGH", "id": "IMG001", "title": "Mutable latest tag is used", "evidence": image, "recommendation": "Use immutable release tags or image digests for deployment."})
    user = image_inspect.get("user") if image_inspect.get("available") else dockerfile.get("user")
    if req.get("require_non_root_user") and (not user or str(user).strip() in {"0", "root"}):
        findings.append({"severity": "HIGH", "id": "IMG002", "title": "Container may run as root", "evidence": user or "No USER directive detected", "recommendation": "Set a numeric non-root user in the Dockerfile and Kubernetes securityContext."})
    has_healthcheck = bool(image_inspect.get("healthcheck")) if image_inspect.get("available") else dockerfile.get("healthcheck")
    if req.get("require_healthcheck") and not has_healthcheck:
        findings.append({"severity": "MEDIUM", "id": "IMG003", "title": "Image healthcheck is missing", "evidence": "No HEALTHCHECK found", "recommendation": "Add a lightweight healthcheck or rely on Kubernetes probes and document the reason."})
    labels = image_inspect.get("labels") if image_inspect.get("available") else dockerfile.get("labels", {})
    labels = labels or {}
    if req.get("require_oci_labels"):
        missing = [k for k in req.get("required_oci_labels", []) if k not in labels]
        if missing:
            findings.append({"severity": "MEDIUM", "id": "IMG004", "title": "Required OCI image labels are missing", "evidence": ", ".join(missing), "recommendation": "Pass build args or add LABEL directives for traceability."})
    if dockerfile.get("apt_packages"):
        findings.append({"severity": "LOW", "id": "IMG005", "title": "Runtime image installs OS packages", "evidence": ", ".join(sorted(set(dockerfile["apt_packages"]))[:12]), "recommendation": "Keep runtime packages minimal; remove package managers where possible or consider a distroless runtime."})
    runtime = dockerfile.get("base_images", [])[-1]["image"] if dockerfile.get("base_images") else ""
    avoided = set(policy.get("base_image_guidance", {}).get("avoid_runtime_images", []))
    if runtime in avoided or runtime.endswith(":latest"):
        findings.append({"severity": "HIGH", "id": "IMG006", "title": "Runtime base image is discouraged", "evidence": runtime, "recommendation": "Use a pinned, maintained runtime base image and scan it continuously."})
    if not digest and not image_inspect.get("repo_digests"):
        findings.append({"severity": "INFO", "id": "IMG007", "title": "Image digest not captured", "evidence": "No digest file or RepoDigest detected", "recommendation": "Capture the registry digest after push for deployment traceability."})
    return findings


def md_report(payload: dict[str, Any]) -> str:
    lines = ["# Day 17 - Container Image Metadata and Hardening Report", ""]
    lines.append(f"Generated: `{payload['generated_at']}`")
    lines.append(f"Image: `{payload.get('image') or 'not provided'}`")
    lines.append("")
    lines.append("## Dockerfile summary")
    df = payload["dockerfile"]
    lines.append(f"- Dockerfile exists: **{df.get('exists')}**")
    lines.append(f"- Base images: {', '.join(b['image'] for b in df.get('base_images', [])) or 'not detected'}")
    lines.append(f"- Runtime user: `{df.get('user') or 'not detected'}`")
    lines.append(f"- Healthcheck: **{bool(df.get('healthcheck'))}**")
    lines.append(f"- Exposed ports: {', '.join(df.get('expose', [])) or 'not detected'}")
    lines.append("")
    img = payload["image_inspect"]
    lines.append("## Docker image inspect")
    if img.get("available"):
        lines.append(f"- Image ID: `{img.get('id')}`")
        lines.append(f"- Repo digests: {', '.join(img.get('repo_digests') or []) or 'none'}")
        lines.append(f"- Runtime user: `{img.get('user') or 'not set'}`")
        lines.append(f"- Labels: {len(img.get('labels') or {})}")
    else:
        lines.append(f"- Inspect unavailable: {img.get('reason')}")
    lines.append("")
    lines.append("## Findings")
    findings = payload.get("findings", [])
    if not findings:
        lines.append("No metadata or Dockerfile hardening findings detected.")
    else:
        lines.append("| Severity | ID | Finding | Recommendation |")
        lines.append("|---|---|---|---|")
        for f in findings:
            lines.append(f"| {f['severity']} | {f['id']} | {f['title']} — {f.get('evidence','')} | {f['recommendation']} |")
    lines.append("")
    lines.append("## Decision")
    high = sum(1 for f in findings if f.get("severity") in {"CRITICAL", "HIGH"})
    lines.append("- Status: **{}**".format("REVIEW_REQUIRED" if high else "PASS"))
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", default=os.getenv("IMAGE"))
    ap.add_argument("--dockerfile", default="Dockerfile")
    ap.add_argument("--policy", default="config/container-security-policy.json")
    ap.add_argument("--digest-file", default="reports/image-digest.txt")
    ap.add_argument("--json-output", default="reports/image-metadata.json")
    ap.add_argument("--markdown-output", default="reports/image-metadata.md")
    args = ap.parse_args()
    Path("reports").mkdir(exist_ok=True)
    policy = read_json(Path(args.policy), {})
    df = parse_dockerfile(Path(args.dockerfile))
    inspected = inspect_image(args.image)
    digest_path = Path(args.digest_file)
    digest = digest_path.read_text().strip() if digest_path.exists() else None
    findings = assess(policy, df, inspected, args.image, digest)
    payload = {
        "generated_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "image": args.image,
        "policy": policy.get("policy_name", "container-security-policy"),
        "dockerfile": df,
        "image_inspect": inspected,
        "digest": digest,
        "findings": findings,
        "summary": {"total_findings": len(findings), "high_or_critical": sum(1 for f in findings if f["severity"] in {"HIGH", "CRITICAL"})},
    }
    Path(args.json_output).write_text(json.dumps(payload, indent=2))
    Path(args.markdown_output).write_text(md_report(payload))
    print(f"Wrote {args.markdown_output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
