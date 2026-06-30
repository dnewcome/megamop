"""dome_tpu.py — FLEXIBLE perforated dome insert (print in TPU).

py cad/dome_tpu.py -> build/dome_tpu_stiff.stl, build/dome_tpu_soft.stl, build/dome_tpu.stl

The soft abrasion face. A thin perforated spherical shell on a flat clamp flange: the flange
is pinched between dome_ring's lip and the cup rim, the dome bulges up through the ring's
aperture, the proud wick pokes through the throat, paint bleeds out the hole grid.

TWO flex variants are kept (print both, compare on a wall):
  'stiff' = the original (rise 14, shell 1.8) — held its shape, but needed firm pressure to
            flatten against a flat surface.
  'soft'  = print-test revision (rise 11, shell 1.2, bigger/denser holes) — flattens with much
            less pressure (shell bending stiffness ~ thickness^3) and flows more.
dome_tpu.stl is the DEFAULT ('soft'), used by the assemblies / GLB. Local frame: z=0 flange
bottom (on the rim), apex up. No threads on this part — the rigid ring carries the thread.
"""
import os
import math
from build123d import Cylinder, Sphere, Box, Pos, Rot, Align, export_stl
import machine_params as M

VARIANTS = {
    "stiff": dict(rise=14.0, t=1.8, hole_d=3.6,
                  rings=[(0, 1), (16, 6), (30, 10), (43, 12), (52, 12)]),
    "soft":  dict(rise=11.0, t=1.2, hole_d=4.4,
                  rings=[(0, 1), (13, 7), (25, 13), (37, 18), (46, 22)]),
}
DEFAULT = "soft"


def _sphere(v):
    """Return (R, ZF, Cz) for the dome sphere of this variant."""
    a = M.DTPU_BASE_R
    h = v["rise"]
    R = (a * a + h * h) / (2 * h)
    ZF = M.DTPU_FLANGE_T
    return R, ZF, ZF + h - R


def _holes(v):
    R, ZF, Cz = _sphere(v)
    holes = []
    rr = v["hole_d"] / 2
    L = v["t"] + 6
    rmid = R - v["t"] / 2
    for theta_deg, n in v["rings"]:
        th = math.radians(theta_deg)
        for k in range(n):
            phi = 360.0 * k / n + theta_deg * 0.5
            cx = rmid * math.sin(th) * math.cos(math.radians(phi))
            cy = rmid * math.sin(th) * math.sin(math.radians(phi))
            cz = Cz + rmid * math.cos(th)
            cyl = Cylinder(rr, L, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            holes.append(Pos(cx, cy, cz) * Rot(0, 0, phi) * Rot(0, theta_deg, 0) * cyl)
    return holes


def part(variant=DEFAULT):
    v = VARIANTS[variant]
    R, ZF, Cz = _sphere(v)
    C = (Align.CENTER, Align.CENTER, Align.MIN)
    # flat clamp flange (ring, throat hole in the middle)
    flange = Cylinder(M.DTPU_FLANGE_R, ZF, align=C)
    flange -= Cylinder(M.DTPU_THROAT_R, ZF + 1, align=C)
    # solid dome cap above the flange plane, then hollow to a shell
    cap = Pos(0, 0, Cz) * Sphere(R)
    cap = cap & Pos(0, 0, ZF) * Box(4 * R, 4 * R, 4 * R, align=C)
    body = flange.fuse(cap)
    body = body.cut(Pos(0, 0, Cz) * Sphere(R - v["t"]))          # dome cavity
    body = body.cut(Cylinder(M.DTPU_THROAT_R, ZF + 1, align=C))  # keep throat open
    body = body.cut(*_holes(v))
    return body


MATES = {
    "flange": Pos(0, 0, 0),   # flange bottom sits on the cup rim
}

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    import trimesh
    for name in ("stiff", "soft"):
        export_stl(part(name), f"build/dome_tpu_{name}.stl")
        m = trimesh.load(f"build/dome_tpu_{name}.stl")
        print(f"dome_tpu[{name}]:", (m.bounds[1] - m.bounds[0]).round(2),
              "bodies:", len(m.split(only_watertight=False)),
              "watertight:", m.is_watertight)
    export_stl(part(DEFAULT), "build/dome_tpu.stl")   # default used by assemblies/GLB
    print(f"dome_tpu.stl = '{DEFAULT}' (default)")
