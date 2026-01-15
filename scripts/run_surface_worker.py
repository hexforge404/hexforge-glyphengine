#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure /app is importable when running as a script
APP_ROOT = Path(__file__).resolve().parents[1]  # /app
sys.path.insert(0, str(APP_ROOT))

from hse.fs.paths import assert_valid_job_id
from hse.workers.surface_worker import run_surface_job  # noqa: E402


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_surface_worker.py <job_id> [subfolder]")
        sys.exit(1)

    job_id = sys.argv[1]
    try:
        job_id = assert_valid_job_id(job_id)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(2)

    subfolder = sys.argv[2] if len(sys.argv) > 2 else None

    run_surface_job(job_id, subfolder=subfolder)
