"""dome_ring.py — RIGID retainer ring that clamps the flexible TPU dome (dome_tpu.py).

py cad/dome_ring.py -> build/dome_ring.stl   (print rigid: PETG / PLA)

Same threaded ring + Ø68 outer as dome_cap/collar (so cap.py still snaps over it), but
the top lip has a wide aperture the TPU dome bulges through; the lip underside pinches the
TPU dome's flange against the cup rim. Local frame: z=0 thread entrance, lip at top.
"""
import os
from build123d import (
    BuildPart, BuildSketch, BuildLine, Polyline, make_face, revolve,
    Axis, Plane, Pos, Box, Align, PolarLocations, export_stl,
)
import machine_params as M
from threads import thread_ribs

r_bore = M.COLLAR_BORE_R
r_out  = M.COLLAR_OUTER_R
r_ap   = M.DRING_APERTURE_R           # wide opening for the TPU dome
H      = M.DOME_RING_H
Z_SEAT = H - M.DRING_LIP_T            # lip underside = clamp face on the flange/rim


def part():
    pts = [
        (r_bore, 0.0),
        (r_bore, Z_SEAT),     # internal-thread bore
        (r_ap,   Z_SEAT),     # lip underside (clamps the TPU flange)
        (r_ap,   H),          # aperture wall through the lip
        (r_out,  H),          # top face
        (r_out,  0.0),        # outer wall
    ]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        revolve(axis=Axis.Z)
    body = bp.part

    # thread must fit inside the (short) bore below the lip
    ribs = thread_ribs(r_bore, pitch=M.CUP_THREAD_PITCH, starts=M.CUP_THREAD_STARTS,
                       length=Z_SEAT - 2.0, depth=M.CUP_THREAD_DEPTH,
                       external=False, z0=1.0)
    body = body.fuse(*ribs)

    with BuildPart() as fp:
        with PolarLocations(r_out, 10):
            Box(2.4, 3.0, H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body.cut(*fp.solids())
    return body


MATES = {
    "seat": Pos(0, 0, Z_SEAT),   # lip underside; lands on the TPU flange (on the rim)
}

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    p = part()
    export_stl(p, "build/dome_ring.stl")
    import trimesh
    m = trimesh.load("build/dome_ring.stl")
    print("dome_ring:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)
