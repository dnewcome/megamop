"""bottle.py — a realistic Gatorade-style contour bottle for renders / GLB (NOT printed).

py cad/bottle.py -> build/bottle_shell.stl, bottle_liquid.stl, bottle_label.stl

A surface-of-revolution silhouette: domed base -> waisted grip body -> shoulder -> a
Ø38 neck that matches the real bottle finish so the mop visibly threads on. Built as a
thin shell (clear plastic) with a separate orange liquid solid and a label band, so the
GLB can give each its own PBR material.
"""
import os
from build123d import (
    BuildPart, BuildSketch, BuildLine, Spline, Line, make_face, revolve,
    Axis, Plane, Pos, Box, Cylinder, Align, export_stl,
)
import machine_params as M

NECK_R   = M.BOTTLE_THREAD_MAJOR_D / 2     # 19.0 — matches the mop skirt
NECK_TOP = 214.0
WALL     = 1.6
FILL_Z   = 150.0                            # liquid level

# outer silhouette (r, z), base edge -> neck top
OUTER = [
    (34.0, 0.0), (37.5, 7.0), (38.0, 28.0), (37.2, 70.0),
    (33.0, 108.0),                          # the grip waist
    (37.2, 150.0), (35.5, 168.0), (29.0, 182.0),
    (21.0, 192.0), (NECK_R, 198.0), (NECK_R, NECK_TOP),
]
INNER = [(max(r - WALL, 1.0), z + (WALL if z < 1 else 0)) for r, z in OUTER]


def _revolve(points, ztop):
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Line((0, 0), (points[0][0], 0))
                Spline(*points)
                Line(points[-1], (0, ztop))
                Line((0, ztop), (0, 0))
            make_face()
        revolve(axis=Axis.Z)
    return bp.part


def shell():
    outer = _revolve(OUTER, NECK_TOP)
    inner = _revolve([(r, z) for r, z in INNER], NECK_TOP + 6)   # taller -> opens the neck
    return outer.cut(inner)


def liquid():
    inner = _revolve([(r, z) for r, z in INNER], NECK_TOP + 6)
    clip = Pos(0, 0, FILL_Z) * Box(200, 200, 2 * FILL_Z,
                                   align=(Align.CENTER, Align.CENTER, Align.MAX))
    return inner & clip


def label():
    band = Cylinder(38.3, 52, align=(Align.CENTER, Align.CENTER, Align.MIN))
    band -= Cylinder(37.4, 60, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, 0, 36) * band


if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    import trimesh
    for name, part in [("shell", shell()), ("liquid", liquid()), ("label", label())]:
        f = f"build/bottle_{name}.stl"
        export_stl(part, f)
        m = trimesh.load(f)
        print(f"bottle_{name}:", (m.bounds[1] - m.bounds[0]).round(1),
              "watertight:", m.is_watertight)
