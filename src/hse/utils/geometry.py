from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from PIL import Image


@dataclass
class STLMetadata:
    triangles: int
    bbox_min: Tuple[float, float, float]
    bbox_max: Tuple[float, float, float]

    @property
    def z_range_mm(self) -> float:
        return self.bbox_max[2] - self.bbox_min[2]

    def as_dict(self) -> Dict[str, object]:
        return {
            "triangles": int(self.triangles),
            "bbox": {"min": list(self.bbox_min), "max": list(self.bbox_max)},
            "z_range_mm": float(self.z_range_mm),
        }


def _init_bbox() -> List[float]:
    return [math.inf, math.inf, math.inf], [-math.inf, -math.inf, -math.inf]


def _update_bbox(bmin: List[float], bmax: List[float], pts: Iterable[Tuple[float, float, float]]) -> None:
    for x, y, z in pts:
        if x < bmin[0]:
            bmin[0] = x
        if y < bmin[1]:
            bmin[1] = y
        if z < bmin[2]:
            bmin[2] = z
        if x > bmax[0]:
            bmax[0] = x
        if y > bmax[1]:
            bmax[1] = y
        if z > bmax[2]:
            bmax[2] = z


def _parse_binary_stl(path: Path) -> STLMetadata:
    with path.open("rb") as fh:
        head = fh.read(80)
        _ = head  # unused header
        tri_bytes = fh.read(4)
        if len(tri_bytes) != 4:
            raise ValueError("invalid STL: missing triangle count")
        tri_count = struct.unpack("<I", tri_bytes)[0]

        bmin, bmax = _init_bbox()
        actual = 0
        for _ in range(tri_count):
            data = fh.read(50)
            if len(data) < 50:
                break
            actual += 1
            floats = struct.unpack("<12fH", data)[:12]
            pts = [
                (floats[3], floats[4], floats[5]),
                (floats[6], floats[7], floats[8]),
                (floats[9], floats[10], floats[11]),
            ]
            _update_bbox(bmin, bmax, pts)

    if actual == 0:
        raise ValueError("invalid STL: zero triangles")

    return STLMetadata(actual, tuple(bmin), tuple(bmax))


def _parse_ascii_stl(path: Path) -> STLMetadata:
    bmin, bmax = _init_bbox()
    tri_count = 0

    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            stripped = line.lstrip()
            if stripped.startswith("facet"):
                tri_count += 1
            if stripped.startswith("vertex"):
                parts = stripped.split()
                if len(parts) >= 4:
                    try:
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        _update_bbox(bmin, bmax, [(x, y, z)])
                    except ValueError:
                        continue

    if tri_count == 0:
        raise ValueError("invalid STL: zero triangles")

    return STLMetadata(tri_count, tuple(bmin), tuple(bmax))


def parse_stl_metadata(path: Path) -> STLMetadata:
    head = path.read_bytes()[:256]
    looks_ascii = head.startswith(b"solid") and b"facet" in head

    try:
        if looks_ascii:
            return _parse_ascii_stl(path)
        return _parse_binary_stl(path)
    except ValueError:
        # Fallback: if the heuristic failed, try the other parser once.
        if looks_ascii:
            return _parse_binary_stl(path)
        return _parse_ascii_stl(path)


def sample_heightmap_range(path: Path, sample_px: int = 128) -> Optional[Tuple[float, float]]:
    if not path.exists():
        return None
    img = Image.open(path).convert("L")
    img = img.resize((sample_px, sample_px))
    pixels = list(img.getdata())
    if not pixels:
        return None
    min_v = min(pixels)
    max_v = max(pixels)
    return float(min_v), float(max_v)


def evaluate_geometry(
    *,
    stl_path: Path,
    heightmap_range: Optional[Tuple[float, float]],
    min_displacement_mm: float = 0.2,
    non_uniform_threshold: float = 1.0,
) -> Dict[str, object]:
    meta = parse_stl_metadata(stl_path).as_dict()
    reason: Optional[str] = None
    passed = True

    if meta["triangles"] <= 0:
        passed = False
        reason = "no_triangles"

    if heightmap_range is not None:
        hmin, hmax = heightmap_range
        spread = hmax - hmin
        if spread > non_uniform_threshold and meta["z_range_mm"] < min_displacement_mm:
            passed = False
            reason = "stl_flat_no_displacement"

    meta.update({"passed": passed, "reason": reason})
    return meta
