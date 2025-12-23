# Filesystem Contract (HSE)

HSE writes all public outputs under a web-served assets root.
This document locks the canonical layout for all generated jobs.

## Canonical Public Root
/assets/surface/

## Canonical Layout (Single Source of Truth)
/
assets/surface/
  └── <subfolder?>/
      └── <job_id>/
          ├── job.json
          ├── previews.json
          ├── enclosure/
          │   ├── enclosure.stl
          │   └── enclosure.obj            (or enclosure.glb)
          ├── textures/
          │   ├── texture.png
          │   ├── heightmap.png
          │   └── heightmap.exr            (optional)
          └── previews/
              ├── hero.png
              ├── iso.png
              ├── top.png
              └── side.png

## Subfolder Rules
- subfolder is optional.
- If omitted or invalid, job is written directly under /assets/surface/<job_id>/.
- If present, job is written under /assets/surface/<subfolder>/<job_id>/.
- subfolder must be sanitized to a safe single directory name (see INTERFACES.md).

## Job ID Rules
- job_id is canonical.
- job_id must be filesystem-safe and unique.
- job_id is the folder name and the stable lookup key for APIs.
- Human-friendly labels may exist inside job.json but are not used as folder names.

## Guaranteed Outputs (v1)
- job.json
- previews.json
- enclosure/enclosure.stl
- textures/texture.png
- textures/heightmap.png
- previews/hero.png, previews/iso.png, previews/top.png, previews/side.png

## Optional Outputs
- textures/heightmap.exr
- enclosure/enclosure.obj OR enclosure/enclosure.glb (at least one handoff format recommended)

## Public vs Internal
Public:
- Everything under /assets/surface/** is public and must be safe to serve.

Internal-only (never written under /assets/surface/):
- temp files, caches, intermediate renders, raw inference artifacts, debug dumps

## Do Not Break These Paths
- /assets/surface/ must remain stable across versions.
- The <job_id>/ folder boundary is the stable unit of download and caching.
- The previews/* and textures/* paths must remain stable once shipped.
