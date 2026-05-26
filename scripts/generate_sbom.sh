#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR="${REPORT_DIR:-reports}"
mkdir -p "$REPORT_DIR"
LOG="$REPORT_DIR/sbom-generation.log"
: > "$LOG"

echo "# Day 14 SBOM Generation" | tee -a "$LOG"
echo "Generated at: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"

if command -v mvn >/dev/null 2>&1; then
  echo "Running CycloneDX Maven plugin..." | tee -a "$LOG"
  if mvn -B -DskipTests org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom 2>&1 | tee -a "$LOG"; then
    echo "CycloneDX Maven plugin completed." | tee -a "$LOG"
  else
    echo "CycloneDX Maven plugin failed; creating fallback SBOM from pom.xml." | tee -a "$LOG"
  fi
else
  echo "Maven not found; creating fallback SBOM from pom.xml." | tee -a "$LOG"
fi

if [ -f target/bom.json ]; then
  cp target/bom.json "$REPORT_DIR/bom.json"
fi
if [ -f target/bom.xml ]; then
  cp target/bom.xml "$REPORT_DIR/bom.xml"
fi

if [ ! -f "$REPORT_DIR/bom.json" ]; then
  python3 - <<'PY'
from __future__ import annotations
import json, uuid, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
NS={"m":"http://maven.apache.org/POM/4.0.0"}
pom=Path("pom.xml")
components=[]
if pom.exists():
    root=ET.parse(pom).getroot()
    for dep in root.findall("m:dependencies/m:dependency", NS):
        gid=(dep.findtext("m:groupId", default="", namespaces=NS) or "").strip()
        aid=(dep.findtext("m:artifactId", default="", namespaces=NS) or "").strip()
        ver=(dep.findtext("m:version", default="managed-by-parent-or-bom", namespaces=NS) or "managed-by-parent-or-bom").strip()
        scope=(dep.findtext("m:scope", default="required", namespaces=NS) or "required").strip()
        components.append({
            "type":"library",
            "group":gid,
            "name":aid,
            "version":ver,
            "scope":scope,
            "purl":f"pkg:maven/{gid}/{aid}@{ver}" if gid and aid else "",
            "licenses":[]
        })
bom={
    "bomFormat":"CycloneDX",
    "specVersion":"1.5",
    "serialNumber":"urn:uuid:"+str(uuid.uuid4()),
    "version":1,
    "metadata":{"timestamp":datetime.now(timezone.utc).isoformat(),"tools":[{"vendor":"project-script","name":"fallback-sbom-generator"}]},
    "components":components
}
out=Path("reports/sbom-fallback.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(bom, indent=2), encoding="utf-8")
Path("reports/bom.json").write_text(json.dumps(bom, indent=2), encoding="utf-8")
print(f"Wrote fallback SBOM with {len(components)} components")
PY
fi

python3 scripts/dependency_inventory.py --sbom "$REPORT_DIR/bom.json" --json-output "$REPORT_DIR/dependency-inventory.json" --markdown-output "$REPORT_DIR/dependency-inventory.md"

cat > "$REPORT_DIR/sbom-generation.md" <<EOF
# Day 14 SBOM Generation Result

- SBOM JSON: \`$REPORT_DIR/bom.json\`
- Dependency inventory: \`$REPORT_DIR/dependency-inventory.md\`
- Raw log: \`$LOG\`

The CycloneDX Maven plugin is preferred. If Maven or the plugin is unavailable, the script creates a fallback SBOM from direct Maven dependencies so downstream policy checks can still run in demo mode.
EOF

cat "$REPORT_DIR/sbom-generation.md"
