#!/usr/bin/env bash
set -euo pipefail

ENGINE_CONTAINER="${HEXFORGE_ENGINE_CONTAINER:-}"
is_running() {
    docker ps --format '{{.Names}}' | grep -Fx "$1" >/dev/null 2>&1
}

if [[ -z "$ENGINE_CONTAINER" ]]; then
    if is_running "hexforge-surface-engine"; then
        ENGINE_CONTAINER="hexforge-surface-engine"
    elif is_running "hexforge-surface-engine-worker"; then
        ENGINE_CONTAINER="hexforge-surface-engine-worker"
    else
        echo "ERROR: no engine container running. Tried hexforge-surface-engine, hexforge-surface-engine-worker." >&2
        echo "Running containers:" >&2
        docker ps --format ' - {{.Names}}' >&2
        exit 1
    fi
elif ! is_running "$ENGINE_CONTAINER"; then
    echo "ERROR: specified HEXFORGE_ENGINE_CONTAINER=$ENGINE_CONTAINER is not running." >&2
    echo "Running containers:" >&2
    docker ps --format ' - {{.Names}}' >&2
    exit 1
fi

BASE_ROOT="${HEXFORGE_BASE_URL:-http://127.0.0.1:8092}"
if [[ -z "${HEXFORGE_BASE_URL:-}" && "$ENGINE_CONTAINER" == *worker* ]]; then
    BASE_ROOT="http://hexforge-surface-engine:8092"
fi
BASE="${BASE_ROOT%/}/api/surface"

docker exec -i "$ENGINE_CONTAINER" python - <<PY
import json, urllib.request
from jsonschema import validate
from hse.contracts import load_contract_schema
from hse.fs.paths import manifest_path

base = "${BASE}"
status_schema = load_contract_schema("job_status.schema.json")
manifest_schema = load_contract_schema("job_manifest.schema.json")

req = urllib.request.Request(
    f"{base}/jobs",
    data=json.dumps({}).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as r:
    created = json.loads(r.read().decode("utf-8"))

validate(created, status_schema)
job_id = created["job_id"]
print("OK POST job_status:", job_id)

with urllib.request.urlopen(f"{base}/jobs/{job_id}") as r:
    st = json.loads(r.read().decode("utf-8"))
validate(st, status_schema)
print("OK GET job_status:", job_id, st["status"])

mp = manifest_path(job_id, subfolder=None)
m = json.loads(mp.read_text(encoding="utf-8"))
validate(m, manifest_schema)
print("OK manifest schema:", mp)
PY

echo "✅ contracts verified"
