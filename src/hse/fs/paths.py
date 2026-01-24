from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

# Only allow filesystem-safe identifiers (no traversal, whitespace, or dots)
_SAFE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
# Only allow a single safe folder name (no slashes, dots, whitespace, traversal)
_SUBFOLDER_RE = _SAFE_RE


def assert_valid_job_id(value: str) -> str:
    """Ensure job_id is filesystem-safe and at least 3 characters."""
    v = str(value or "").strip()
    if len(v) < 3:
        raise ValueError("job_id must be at least 3 characters")
    if not _SAFE_RE.match(v):
        raise ValueError("job_id must contain only letters, numbers, underscore, or dash")
    return v


def sanitize_subfolder(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return None
    if not _SUBFOLDER_RE.match(v):
        return None
    return v


def assets_root() -> Path:
    """
    Root folder where engine writes job folders.
    Mounted in docker-compose as /data/hexforge3d and we use /data/hexforge3d/surface by default.
    """
    base = Path(os.getenv("SURFACE_OUTPUT_DIR", "/data/hexforge3d/surface")).resolve()
    # Normalize to ensure final component is "surface" so URLs stay /assets/surface/<subfolder?>/<job_id>
    if base.name != "surface":
        base = base / "surface"
    return base


def public_prefix() -> str:
    """
    URL prefix where the public files are served from (nginx or media_api).
    Must remain a relative URL like /assets/surface (Surface v1 rule).
    """
    return os.getenv("SURFACE_PUBLIC_PREFIX", "/assets/surface").rstrip("/")


def job_dir(job_id: str, *, subfolder: Optional[str] = None) -> Path:
    jid = assert_valid_job_id(job_id)
    sf = sanitize_subfolder(subfolder)
    if sf:
        return assets_root() / sf / jid
    return assets_root() / jid


def public_root(job_id: str, *, subfolder: Optional[str] = None) -> str:
    """
    Public URL base for a given job.
    Example: /assets/surface/<subfolder?>/<job_id>
    """
    jid = assert_valid_job_id(job_id)
    sf = sanitize_subfolder(subfolder)
    if sf:
        return f"{public_prefix()}/{sf}/{jid}"
    return f"{public_prefix()}/{jid}"


def manifest_path(job_id: str, *, subfolder: Optional[str] = None) -> Path:
    # keep filename stable across engines
    return job_dir(job_id, subfolder=subfolder) / "job_manifest.json"


def job_json_path(job_id: str, *, subfolder: Optional[str] = None) -> Path:
    return job_dir(job_id, subfolder=subfolder) / "job.json"


__all__ = [
    "assert_valid_job_id",
    "sanitize_subfolder",
    "assets_root",
    "public_prefix",
    "public_root",
    "job_dir",
    "manifest_path",
    "job_json_path",
]
