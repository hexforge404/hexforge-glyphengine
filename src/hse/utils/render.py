from __future__ import annotations

import numpy as np
import matplotlib

# Force headless backend for containers
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
from pathlib import Path  # noqa: E402
import trimesh  # noqa: E402
from PIL import Image  # noqa: E402


def _shaded_colors(normals: np.ndarray) -> np.ndarray:
    light_dir = np.array([0.35, 0.45, 0.83], dtype=float)
    light_dir = light_dir / np.linalg.norm(light_dir)
    dots = np.clip(normals @ light_dir, 0.0, 1.0)
    base = np.array([0.40, 0.78, 1.00], dtype=float)
    amb = 0.12
    colors = amb + base * dots[:, None]
    return np.clip(colors, 0.0, 1.0)


def render_hero_from_stl(stl_path: Path, out_path: Path, size_px: int = 640) -> dict:
    if not stl_path.exists():
        raise FileNotFoundError(f"stl missing: {stl_path}")

    mesh = trimesh.load(stl_path, force="mesh", skip_materials=True)
    if mesh.is_empty or mesh.vertices.size == 0 or mesh.faces.size == 0:
        raise ValueError("invalid or empty mesh")

    diag = float(np.linalg.norm(mesh.extents))
    if diag < 1e-3:
        raise ValueError("stl_bbox_degenerate")

    verts = mesh.vertices - mesh.centroid
    faces = mesh.faces
    normals = mesh.face_normals

    colors = _shaded_colors(normals)
    tris = verts[faces]

    fig = plt.figure(figsize=(size_px / 100.0, size_px / 100.0), dpi=100)
    ax = fig.add_subplot(111, projection="3d")

    coll = Poly3DCollection(tris, facecolors=colors, edgecolor=(0.05, 0.12, 0.20), linewidths=0.1)
    ax.add_collection3d(coll)

    extent = (verts.max(axis=0) - verts.min(axis=0)).max() or 1.0
    limit = extent * 0.65
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)

    ax.view_init(elev=30, azim=35)
    ax.set_proj_type("persp")
    ax.axis("off")

    background = "#0b1020"
    ax.set_facecolor(background)
    fig.patch.set_facecolor(background)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        out_path,
        facecolor=background,
        bbox_inches="tight",
        pad_inches=0,
        transparent=False,
    )
    plt.close(fig)

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError("hero_render_failed: empty output")

    img = Image.open(out_path).convert("RGB")
    arr = np.asarray(img, dtype=np.float32)
    variance = float(arr.var())
    if variance < 2.0:
        raise RuntimeError("hero_render_failed: flat preview")

    return {"variance": variance, "bbox_diag": diag}


__all__ = ["render_hero_from_stl"]
