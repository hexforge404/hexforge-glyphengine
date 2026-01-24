from __future__ import annotations

import os
from fastapi import FastAPI

from hse.fs.paths import assets_root

ROOT_PATH = os.getenv("ROOT_PATH", "/api/surface")

if os.getenv("GLYPHENGINE_DEBUG") == "1":
    surface_dir = os.getenv("SURFACE_OUTPUT_DIR", "/data/hexforge3d/surface")
    print(
        f"[glyphengine] SURFACE_OUTPUT_DIR={surface_dir} resolved_assets_root={assets_root()}",
        flush=True,
    )

app = FastAPI(title="HexForge GlyphEngine", version="contracts-v1")


@app.get(f"{ROOT_PATH}/health")
def health():
    return {"ok": True, "service": "hexforge-glyphengine"}


# Mount job routes (contracts-v1)
from hse.routes.jobs import router as jobs_router  # noqa: E402

app.include_router(jobs_router, prefix=ROOT_PATH)
