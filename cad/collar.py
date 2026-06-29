"""collar.py — megamop screw-on collar: clamps the mesh + wick onto the base.

py cad/collar.py -> build/collar.stl

A ring with an internal thread (mates the base cup's external thread) and an inward
top lip. Screwing it down drives the lip onto the mesh + proud wick, pinching their
perimeter against the cup rim while leaving a ~2" (COLLAR_APERTURE_D) face exposed.
Local frame: z=0 at the thread-entrance (bottom), lip at the top.
"""
import os
from build123d import (
    BuildPart, BuildSketch, BuildLine, Polyline, make_face, revolve,
    Axis, Plane, Pos, Rot, Box, Align, PolarLocations, export_stl,
)
import machine_params as M
from threads import thread_ribs

r_bore  = M.COLLAR_BORE_R       # internal thread root (bore wall)
r_out   = M.COLLAR_OUTER_R
r_ap    = M.COLLAR_APERTURE_R   # aperture that exposes the wick face

H        = 14.0                 # overall collar height
LIP_T    = M.COLLAR_LIP_T       # top clamping lip thickness
Z_SEAT   = H - LIP_T            # lip underside (the clamp face) — the seat plane
N_GRIP   = 10                   # finger-grip flutes
GRIP_W   = 3.0
GRIP_D   = 1.2


def part():
    pts = [
        (r_bore, 0.0),       # bottom inner (thread entrance)
        (r_bore, Z_SEAT),    # internal-thread bore wall
        (r_ap,   Z_SEAT),    # lip underside (clamp face), step in to the aperture
        (r_ap,   H),         # aperture wall through the lip
        (r_out,  H),         # top face
        (r_out,  0.0),       # outer wall
    ]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        revolve(axis=Axis.Z)
    body = bp.part

    # internal thread matching the base cup external thread
    ribs = thread_ribs(
        r_bore, pitch=M.CUP_THREAD_PITCH, starts=M.CUP_THREAD_STARTS,
        length=M.CUP_THREAD_LEN, depth=M.CUP_THREAD_DEPTH, external=False,
        z0=1.0,
    )
    body = body.fuse(*ribs)

    # subtract finger-grip flutes from the outer wall for purchase
    flutes = []
    with BuildPart() as fp:
        with PolarLocations(r_out, N_GRIP):
            Box(GRIP_D * 2, GRIP_W, H + 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body.cut(*fp.solids())
    return body


MATES = {
    # lip underside contacts the base rim; +Z up so the collar sits upright
    "seat": Pos(0, 0, Z_SEAT),
}

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    p = part()
    export_stl(p, "build/collar.stl")
    import trimesh
    m = trimesh.load("build/collar.stl")
    print("collar:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)
