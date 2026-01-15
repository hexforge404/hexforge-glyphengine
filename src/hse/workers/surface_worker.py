import json
import time
from typing import Dict, Optional, Tuple

from hse.contracts.envelopes import now_iso
from hse.fs.paths import assert_valid_job_id, job_dir, job_json_path, sanitize_subfolder
from hse.fs.writer import write_manifest, write_surface_job_json


def _read_job_state(job_id: str, subfolder: Optional[str]) -> Tuple[str, Dict, Dict]:
    """Preserve created_at and params/artifacts from the queued job.json."""
    p = job_json_path(job_id, subfolder=subfolder)
    if p.exists():
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(doc, dict):
                created = str(doc.get("created_at") or now_iso())
                params = doc.get("params") or {}
                artifacts = doc.get("artifacts") or {}
                return created, params, artifacts
        except Exception:
            pass
    return now_iso(), {}, {}


def run_surface_job(job_id: str, subfolder: Optional[str] = None) -> None:
    """
    Minimal worker loop:
    - preserves created_at
    - marks job running
    - simulates work
    - writes non-empty placeholder outputs
    - marks job complete
    - bumps manifest updated_at
    """
    job_id = assert_valid_job_id(job_id)
    subfolder = sanitize_subfolder(subfolder)
    root = job_dir(job_id, subfolder=subfolder)
    created_at, params, artifacts = _read_job_state(job_id, subfolder)

    # Mark running
    write_surface_job_json(
        job_id=job_id,
        subfolder=subfolder,
        status="running",
        created_at=created_at,
        updated_at=now_iso(),
        params=params,
        artifacts=artifacts,
    )

    # --- simulate real work ---
    time.sleep(2)

    # Create expected output dirs
    (root / "textures").mkdir(parents=True, exist_ok=True)
    (root / "enclosure").mkdir(parents=True, exist_ok=True)
    (root / "previews").mkdir(parents=True, exist_ok=True)

    # Write non-empty placeholder outputs so status can become "complete"
    png_sig = b"\x89PNG\r\n\x1a\n"
    (root / "previews" / "hero.png").write_bytes(png_sig)
    (root / "previews" / "iso.png").write_bytes(png_sig)
    (root / "previews" / "top.png").write_bytes(png_sig)
    (root / "previews" / "side.png").write_bytes(png_sig)
    (root / "enclosure" / "enclosure.stl").write_text(
        "solid dummy\nendsolid dummy\n", encoding="utf-8"
    )
    (root / "textures" / "texture.png").write_bytes(png_sig)
    (root / "textures" / "heightmap.png").write_bytes(png_sig)

    # Ensure files are non-empty before marking complete
    for required in [
        root / "previews" / "hero.png",
        root / "previews" / "iso.png",
        root / "previews" / "top.png",
        root / "previews" / "side.png",
        root / "enclosure" / "enclosure.stl",
        root / "textures" / "texture.png",
        root / "textures" / "heightmap.png",
    ]:
        if not required.exists() or required.stat().st_size == 0:
            raise RuntimeError(f"output missing or empty: {required}")

    # Final status write
    finished_at = now_iso()
    write_surface_job_json(
        job_id=job_id,
        subfolder=subfolder,
        status="complete",
        created_at=created_at,
        updated_at=finished_at,
        params=params,
        artifacts=artifacts,
    )

    # Bump manifest updated_at (keeps API timestamps honest)
    write_manifest(
        job_id=job_id,
        subfolder=subfolder,
        updated_at=finished_at,
    )
