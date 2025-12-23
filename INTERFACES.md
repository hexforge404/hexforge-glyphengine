# Interfaces (Routes, Ports, Contracts)

This document defines the public and internal interface contract for the HexForge Surface Engine (HSE).
All consumers (frontend, backend, assistant) must conform to this contract.

## Service Identity
- Service name (docker): surface-engine
- Internal base URL: http://surface-engine:8092

## Ports
- 8092/tcp : HSE HTTP API
- 8188/tcp : Optional local ComfyUI (internal only)
- Blender integration runs headless; no public port required

## API Overview (v1)
- All endpoints are versioned implicitly by repository version.
- All responses MUST include job_id and status.
- All public file references MUST be relative paths starting with /assets/.

### POST /api/surface/jobs
Creates a new surface + enclosure job.

Request body (minimal v1 example):
{
  "subfolder": "optional-project-or-product",
  "enclosure": {
    "inner_mm": [70, 40, 18],
    "wall_mm": 2.4,
    "lid_split": "z",
    "lid_ratio": 0.25,
    "features": {
      "standoffs": [],
      "cutouts": []
    }
  },
  "texture": {
    "prompt": "circuit board, cyberpunk, clean lines",
    "seed": 123,
    "size": [1024, 1024]
  }
}

### GET /api/surface/jobs/{job_id}
Returns job status and public asset references when complete.

### GET /api/surface/jobs/{job_id}/assets
Returns a structured list of downloadable public assets.

## Response Contract (example)
{
  "job_id": "hse_2025-12-22_abcdef",
  "status": "complete",
  "result": {
    "public": {
      "root": "/assets/surface/<subfolder?>/<job_id>/" ,
      "enclosure": {
        "stl": "/assets/surface/.../enclosure/enclosure.stl",
        "handoff": "/assets/surface/.../enclosure/enclosure.obj"
      },
      "textures": {
        "texture_png": "/assets/surface/.../textures/texture.png",
        "heightmap_png": "/assets/surface/.../textures/heightmap.png",
        "heightmap_exr": "/assets/surface/.../textures/heightmap.exr"
      },
      "previews": {
        "hero": "/assets/surface/.../previews/hero.png",
        "iso": "/assets/surface/.../previews/iso.png",
        "top": "/assets/surface/.../previews/top.png",
        "side": "/assets/surface/.../previews/side.png"
      },
      "job_json": "/assets/surface/.../job.json"
    }
  }
}

## URL Rules
- HSE returns ONLY relative URLs for public assets.
- Frontend and assistant resolve absolute URLs using environment configuration.
- This ensures compatibility with nginx, reverse proxies, and Cloudflare.

## Subfolder Rules
- subfolder is optional.
- If provided, it must be sanitized to a single folder name:
  - allowed: letters, numbers, dash (-), underscore (_)
  - forbidden: slashes, dots, traversal sequences
- Invalid subfolders must be ignored or replaced with a sanitized value.

## Assistant Permissions
- Assistant may:
  - Create jobs
  - Poll job status
  - Read public asset paths
- Assistant may NOT:
  - Write files directly
  - Modify completed jobs
  - Access internal-only directories
