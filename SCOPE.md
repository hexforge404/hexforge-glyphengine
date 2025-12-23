# Scope (Lock)

This file defines what HSE v1 is allowed to do. Anything outside this scope requires an explicit “scope bump” decision recorded in DECISIONS.md.

## In Scope (v1)

### Textures
- Diffusion texture generation (image outputs)
- Convert textures to heightmaps (PNG required, EXR optional)
- Generate preview renders for texture + applied surfaces

### Enclosures
- Parametric enclosure base geometry generation
- Basic enclosure features: wall thickness, lid/base split, simple standoffs, connector cutouts (rect/circle)
- Export STL for printing (required)
- Export a Blender/CAD handoff format (OBJ/GLB recommended) for displacement workflows

### Integration
- Stable file/folder contract for all outputs
- API endpoints for job create/status/result
- Assistant orchestration hooks (create job, validate parameters, request previews)

## Out of Scope (v1)
- Full AI mesh generation (text→3D, image→3D)
- Auto retopology / complex mesh repair
- Full boolean editing UI
- Direct-to-slicer G-code generation
- User accounts / monetization / marketplace inside HSE itself

## Deferred but Planned (v2+)
- Material-specific presets (PLA/PETG/wood engraving)
- “Style packs” (circuit, hexgrid, matrix, topo, etc.)
- More advanced enclosure geometry (organic shapes, snap fits, gasket channels)
