"""dome_tpu.py — FLEXIBLE perforated dome insert (print in TPU).

py cad/dome_tpu.py -> build/dome_tpu.stl   (print flexible: TPU ~95A)

The soft abrasion face. A thin perforated spherical shell on a flat clamp flange: the
flange is pinched between dome_ring's lip and the cup rim, the dome bulges up through the
ring's aperture, the proud wick pokes through the throat into the dome, and paint bleeds
out the hole grid. Thin shell (DTPU_T) + TPU lets it conform to brick/concrete and not
crack. Local frame: z=0 flange bottom (on the rim), apex up.
"""
import os
import math
from build123d import Cylinder, Sphere, Box, Pos, Rot, Align, export_stl
import machine_params as M

a = M.DTPU_BASE_R            # spring radius
h = M.DTPU_RISE
R = (a * a + h * h) / (2 * h)
ZF = M.DTPU_FLANGE_T         # flange top / dome spring plane
Cz = ZF + h - R              # sphere center

RINGS = [(0, 1), (16, 6), (30, 10), (43, 12), (52, 12)]


def _holes():
    holes = []
    rr = M.DTPU_HOLE_D / 2
    L = M.DTPU_T + 6
    rmid = R - M.DTPU_T / 2
    for theta_deg, n in RINGS:
        th = math.radians(theta_deg)
        for k in range(n):
            phi = 360.0 * k / n + theta_deg * 0.5
            cx = rmid * math.sin(th) * math.cos(math.radians(phi))
            cy = rmid * math.sin(th) * math.sin(math.radians(phi))
            cz = Cz + rmid * math.cos(th)
            cyl = Cylinder(rr, L, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            holes.append(Pos(cx, cy, cz) * Rot(0, 0, phi) * Rot(0, theta_deg, 0) * cyl)
    return holes


def part():
    C = (Align.CENTER, Align.CENTER, Align.MIN)
    # flat clamp flange (ring, throat hole in the middle)
    flange = Cylinder(M.DTPU_FLANGE_R, ZF, align=C)
    flange -= Cylinder(M.DTPU_THROAT_R, ZF + 1, align=C)
    # solid dome cap above the flange plane, then hollow to a shell
    cap = Pos(0, 0, Cz) * Sphere(R)
    cap = cap & Pos(0, 0, ZF) * Box(4 * R, 4 * R, 4 * R, align=C)
    body = flange.fuse(cap)
    body = body.cut(Pos(0, 0, Cz) * Sphere(R - M.DTPU_T))   # dome cavity
    body = body.cut(Cylinder(M.DTPU_THROAT_R, ZF + 1, align=C))  # keep throat open
    body = body.cut(*_holes())
    return body


MATES = {
    "flange": Pos(0, 0, 0),   # flange bottom sits on the cup rim
}

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    p = part()
    export_stl(p, "build/dome_tpu.stl")
    import trimesh
    m = trimesh.load("build/dome_tpu.stl")
    print("dome_tpu:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)
