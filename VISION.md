# Vision

HexForge Surface Engine exists to make “custom-looking” fabrication assets repeatable and sellable.

Most enclosure generators produce functional boxes that look generic. HSE flips the focus:
- The enclosure is the substrate
- The surface treatment (texture, relief, engraving pattern) is the product

## What makes HSE different
- Texture-first workflow: patterns are a first-class output, not an afterthought.
- Fabrication-aware outputs: heightmaps and relief panels are generated with printing/engraving constraints in mind.
- Non-destructive application path: users can apply displacement textures in Blender/CAD without baking everything into geometry too early.

## Long-term Direction (not v1)
- Full “assistant-driven” workflow (guided prompts, parameter sanity checks, job recipes)
- Optional GPU-rented inference for higher fidelity diffusion models
- Optional text-to-3D and image-to-3D generation as a separate module once the surface workflow is stable
