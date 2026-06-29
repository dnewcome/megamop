"""dome_cap.py — PRINTED perforated dome cap (replaces the sourced steel/Kevlar mesh).

py cad/dome_cap.py -> build/dome_cap.stl

Screws onto the base cup (same internal thread as collar.py). Instead of a flat lip
clamping a separate mesh disc, the top is a spherical shell perforated with a grid of
radial holes. It:
  - caps and RETAINS the wick (the proud foam/felt pokes up through the throat into the
    dome cavity and bears on the shell),
  - BULGES past the rim so the rounded dome is what drags on the wall,
  - bleeds paint through the hole grid onto the surface.
Local frame: z=0 at the thread entrance, dome apex at the top.

Build order matters: the dome's sphere booleans are done on the un-threaded body FIRST
(sphere ∩ helical thread is a known boolean failure), threads are fused LAST.
"""
import os
import math
from build123d import (
    Cylinder, Cone, Sphere, Box, Pos, Rot, Align, export_stl,
)
import machine_params as M
from threads import thread_ribs

r_bore = M.COLLAR_BORE_R          # internal thread root (mates cup external thread)
r_out  = M.COLLAR_OUTER_R
Z_SEAT = M.DOME_RING_H            # flange underside = clamp seat plane

# spherical-cap geometry: base radius a, rise h  ->  sphere radius R, center Cz
a = M.DOME_BASE_R
h = M.DOME_RISE
R = (a * a + h * h) / (2 * h)
Cz = Z_SEAT + h - R               # sphere center (below the seat)

# hole grid: (polar angle deg from apex, count). Stop short of the rim so the base ring
# stays solid. Apex gets a single hole.
RINGS = [(0, 1), (16, 6), (30, 10), (43, 12), (52, 12)]


def _dome_holes():
    holes = []
    rr = M.DOME_HOLE_D / 2
    L = M.DOME_T + 6
    rmid = R - M.DOME_T / 2
    for theta_deg, n in RINGS:
        th = math.radians(theta_deg)
        for k in range(n):
            phi = 360.0 * k / n + (theta_deg * 0.5)   # stagger rings
            # cylinder along +Z, rotated to the radial (theta about Y, phi about Z),
            # centered mid-shell so it cleanly spans the shell wall
            cx = rmid * math.sin(th) * math.cos(math.radians(phi))
            cy = rmid * math.sin(th) * math.sin(math.radians(phi))
            cz = Cz + rmid * math.cos(th)
            cyl = Cylinder(rr, L, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            holes.append(Pos(cx, cy, cz) * Rot(0, 0, phi) * Rot(0, theta_deg, 0) * cyl)
    return holes


def part():
    C = (Align.CENTER, Align.CENTER, Align.MIN)
    # --- solid envelope: threaded ring + frustum flange + solid dome cap ----------
    ring = Cylinder(r_out, Z_SEAT, align=C)
    frus = Pos(0, 0, Z_SEAT) * Cone(r_out, a, M.DOME_SEAT_T, align=C)   # ring -> dome base
    cap = Sphere(R)
    cap = Pos(0, 0, Cz) * cap
    # keep only the cap above the seat plane
    cap = cap & Pos(0, 0, Z_SEAT) * Box(2 * R, 2 * R, 2 * R, align=C)
    body = ring.fuse(frus, cap)

    # --- hollow it: thread bore + wick throat + dome cavity ------------------------
    body = body.cut(Cylinder(r_bore, Z_SEAT, align=C))                  # threaded bore
    body = body.cut(Cylinder(M.DOME_THROAT_R, Z_SEAT + 1, align=C))     # wick throat
    body = body.cut(Pos(0, 0, Cz) * Sphere(R - M.DOME_T))               # dome cavity

    # --- perforate the dome --------------------------------------------------------
    body = body.cut(*_dome_holes())

    # --- threads last (sphere booleans are done) -----------------------------------
    ribs = thread_ribs(r_bore, pitch=M.CUP_THREAD_PITCH, starts=M.CUP_THREAD_STARTS,
                       length=M.CUP_THREAD_LEN, depth=M.CUP_THREAD_DEPTH,
                       external=False, z0=1.0)
    body = body.fuse(*ribs)

    # --- grip flutes ---------------------------------------------------------------
    from build123d import PolarLocations, BuildPart
    with BuildPart() as fp:
        with PolarLocations(r_out, 10):
            Box(2.4, 3.0, Z_SEAT + 2, align=C)
    body = body.cut(*fp.solids())
    return body


MATES = {
    "seat": Pos(0, 0, Z_SEAT),   # flange underside contacts the cup rim, +Z up
}

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    p = part()
    export_stl(p, "build/dome_cap.stl")
    import trimesh
    m = trimesh.load("build/dome_cap.stl")
    print("dome_cap:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)
