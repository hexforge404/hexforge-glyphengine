from __future__ import annotations

import json
import os
import time
import traceback
from pathlib import Path
from typing import List, Optional, Tuple

from hse.contracts.envelopes import now_iso
from hse.fs.paths import assets_root, assert_valid_job_id, sanitize_subfolder
from hse.fs.writer import write_manifest, write_surface_job_json
from hse.routes.jobs import infer_status_from_files
from hse.workers.surface_worker import _read_job_state, run_surface_job


POLL_SECONDS = float(os.getenv("HSE_WORKER_POLL_INTERVAL", "2"))


def _heartbeat_path() -> Path:
    """Location for a simple freshness file used by docker healthchecks."""
    override = os.getenv("HSE_WORKER_HEARTBEAT")
    if override:
        return Path(override)
    return assets_root() / ".worker_heartbeat"


def _touch_heartbeat() -> None:
    hb = _heartbeat_path()
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text(now_iso(), encoding="utf-8")


def _read_status(job_json: Path) -> str:
    try:
        doc = json.loads(job_json.read_text(encoding="utf-8"))
        status = str(doc.get("status") or "").strip().lower()
        return status or "queued"
    except Exception:
        return "queued"


def _job_from_path(job_json: Path, root: Path) -> Tuple[str, Optional[str]]:
    job_dir = job_json.parent
    job_id = assert_valid_job_id(job_dir.name)

    subfolder: Optional[str] = None
    if job_dir.parent != root:
        # Handles /surface/<subfolder>/<job_id>/job.json layout
        subfolder = sanitize_subfolder(job_dir.parent.name)

    return job_id, subfolder


def _discover_queued_jobs() -> List[Tuple[str, Optional[str]]]:
    """Find Surface jobs that are still queued."""
    root = assets_root()
    root.mkdir(parents=True, exist_ok=True)

    jobs: List[Tuple[str, Optional[str]]] = []
    seen: set[Tuple[str, Optional[str]]] = set()

    # direct jobs: /surface/<job_id>/job.json
    for job_json in root.glob("*/job.json"):
        job_id, subfolder = _job_from_path(job_json, root)
        status = _read_status(job_json)
        if status != "queued":
            continue
        if infer_status_from_files(job_id, subfolder=subfolder) != "queued":
            continue
        key = (job_id, subfolder)
        if key not in seen:
            seen.add(key)
            jobs.append(key)

    # subfolder jobs: /surface/<subfolder>/<job_id>/job.json
    for job_json in root.glob("*/*/job.json"):
        job_id, subfolder = _job_from_path(job_json, root)
        status = _read_status(job_json)
        if status != "queued":
            continue
        if infer_status_from_files(job_id, subfolder=subfolder) != "queued":
            continue
        key = (job_id, subfolder)
        if key not in seen:
            seen.add(key)
            jobs.append(key)

    return jobs


def _mark_failed(job_id: str, subfolder: Optional[str], err: Exception) -> None:
    created_at, params, artifacts = _read_job_state(job_id, subfolder)
    now = now_iso()
    target = (params or {}).get("target") or "tile"
    target = "pi4b_case" if str(target).strip().lower() == "pi4b_case" else "tile"
    emboss_mode = (params or {}).get("emboss_mode") or "tile"
    write_surface_job_json(
        job_id=job_id,
        subfolder=subfolder,
        status="failed",
        created_at=created_at,
        updated_at=now,
        finished_at=now,
        params=params,
        artifacts=artifacts,
        error={
            "message": str(err),
            "code": "worker_exception",
            "detail": "worker loop failed",
        },
    )
    write_manifest(job_id=job_id, subfolder=subfolder, updated_at=now, target=target, emboss_mode=emboss_mode)

    print(f"[worker] job {job_id} failed: {err}")
    traceback.print_exc()


def run_worker_forever() -> None:
    print("[worker] Surface worker started. Polling for queued jobs...")
    while True:
        queued = _discover_queued_jobs()
        if not queued:
            _touch_heartbeat()
            time.sleep(POLL_SECONDS)
            continue

        for job_id, subfolder in queued:
            try:
                print(f"[worker] processing job {job_id} (subfolder={subfolder or 'root'})")
                run_surface_job(job_id, subfolder=subfolder)
                print(f"[worker] completed job {job_id}")
            except Exception as exc:  # pragma: no cover - best effort logging
                _mark_failed(job_id, subfolder, exc)

        _touch_heartbeat()


if __name__ == "__main__":
    run_worker_forever()