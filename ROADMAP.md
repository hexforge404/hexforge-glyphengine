# Roadmap

This roadmap is intentionally short. It exists to preserve momentum across chat resets.

## Phase 0 — Foundations
- [ ] Repo initialized with context docs (this commit)
- [ ] Decide service name + port contract (surface-engine:8092)
- [ ] Confirm /assets/surface is served by nginx (or via a mounted volume)
- [ ] Implement a stub API that returns a valid result.public payload (mock URLs)

## Phase 1 — Texture Engine Prototype
- [ ] Generate a texture PNG (placeholder first, diffusion later)
- [ ] Convert to heightmap PNG
- [ ] Write outputs to canonical filesystem paths
- [ ] Generate 4 preview images (simple plane render is acceptable)

## Phase 2 — Enclosure Generator Prototype
- [ ] CadQuery: simple enclosure from inner dims + wall thickness
- [ ] Export enclosure STL
- [ ] Add cutout support (rect + circle)
- [ ] Generate enclosure previews (no displacement required yet)

## Phase 3 — Apply Texture (Non-Destructive Preview)
- [ ] Define UV strategy for enclosure faces (box mapping acceptable)
- [ ] Blender headless render: displacement using heightmap
- [ ] Produce final preview pack (hero/iso/top/side)

## Phase 4 — Assistant Wiring
- [ ] Assistant can generate job payloads
- [ ] Assistant validates dimensions and suggests presets
- [ ] Assistant can poll job status and summarize outputs
