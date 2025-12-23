# Architecture

HSE is a modular pipeline that produces two primary artifact families:
1) Surface assets (textures/heightmaps + previews)
2) Enclosure geometry (base models + handoff assets + previews)

## Components

### A) Surface Engine Service (HSE Core)
- Recommended language: Python
- Responsibilities:
  - Job orchestration
  - Calling texture generator(s)
  - Converting textures to heightmaps
  - Writing outputs to canonical filesystem paths
  - Producing previews (direct render or Blender-based)

### B) Texture Generator (Diffusion)
- Can be local (ComfyUI) or remote (rented GPU later)
- Outputs image textures (PNG)

### C) Enclosure Generator
- CadQuery recommended for parametric CAD-like modeling
- Produces STL (required) and a Blender/CAD handoff format (OBJ/GLB recommended)

### D) Blender Integration Layer
- Used for:
  - Applying displacement to preview renders
  - Rendering product-quality preview images (hero/iso/top/side)
- Hard rule (v1): HSE does not need to bake textures into the final printable STL.
  The printable STL may remain a clean base enclosure; textured output is provided as
  heightmaps + optional relief meshes + previews.

### E) HexForge Backend (API Gateway)
- Routes requests from frontend to HSE
- Handles auth/session/rate-limit if required by the main site

### F) HexForge Assistant
- Orchestrator only (no direct filesystem writes)
- Responsibilities:
  - Guide parameter entry
  - Validate dimensions and ranges
  - Provide prompt templates (circuit/hexgrid/matrix/topo/etc.)
  - Trigger jobs via API and summarize outputs

## Data Flow
Frontend → Backend Gateway → HSE Core
HSE Core → Diffusion → Texture outputs
HSE Core → CadQuery → Enclosure geometry outputs
HSE Core → Blender (optional) → Previews
HSE Core → Public assets filesystem → Frontend downloads

## Operational Notes
- HSE should be stateless except for writing job outputs to the assets folder.
- job.json must contain enough metadata to re-render previews later.
- All externally-consumed URLs must be derived from canonical public paths.
