# Decisions Log

This file records decisions that affect architecture, interfaces, filesystem, and scope.
Every scope change or breaking change must be recorded here.

## 2025-12-22 — Project Name
- Chosen: HexForge Surface Engine
- Reason: “Surface” covers textures + displacement + enclosures without locking to boxes only.

## 2025-12-22 — Strategy
- Texture-first to ship marketable assets quickly.
- Full AI mesh generation deferred.

## 2025-12-22 — Enclosure Generator Approach
- Prefer CadQuery over OpenSCAD/YAPP fork.
- Reason: Python-native integration and easier extension for style workflows.

## 2025-12-22 — URL + Filesystem
- HSE returns relative public paths only.
- Frontend resolves absolute URLs using environment configuration.
- Public root locked: /assets/surface/
- Subfolder preserved when provided; sanitized safely.
