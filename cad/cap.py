"""cap.py — snap-on STORAGE CAP that covers the dome cap (keeps the wick wet / tidy).

py cap/cap.py -> build/cap.stl

The cup thread is occupied by the dome cap, so this cover grabs the dome cap's outer
RING instead: a tall cup that slips over the bulging dome, with a slotted skirt whose
rounded detents snap inward under the ring's bottom edge. Pull-off flexes the segments
back over the ring. No change to dome_cap. Local frame: z=0 at the open rim, +Z up to
the closed top; in use the rim points toward the bottle.

Fits whichever body is underneath (straight or angled) — it only references the dome cap.
"""
import os
import math
from build123d import (
    Cylinder, Box, Pos, Rot, Align, PolarLocations, BuildPart, export_stl,
)
import machine_params as M

r_in   = M.CAP_INNER_R
r_out  = M.CAP_OUTER_R
H      = M.CAP_CAVITY_H + M.CAP_WALL     # total height (cavity + closed top)
Z_RING = M.CAP_RIM_BELOW                  # ring-bottom ledge sits here in cap frame
DET_Z  = Z_RING - 1.0                     # detent centered just under the ledge
SLOT_W = 2.2
SLOT_H = 13.0                             # slot length up from the rim (flex length)


def part():
    C = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Cylinder(r_out, H, align=C)
    body -= Cylinder(r_in, M.CAP_CAVITY_H, align=C)        # open cavity from the rim up

    # rounded detent beads (tangential cylinders) that hook under the ring bottom edge
    beads = []
    rb = M.CAP_DETENT
    for k in range(M.CAP_N_SNAP):
        th = 360.0 * k / M.CAP_N_SNAP
        bead = (Rot(0, 0, th) * Pos(r_in, 0, DET_Z) * Rot(90, 0, 0)
                * Cylinder(rb, 6.0, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
        beads.append(bead)
    body = body.fuse(*beads)

    # flex slots through the skirt, staggered between the detents
    slots = []
    for k in range(M.CAP_N_SNAP):
        th = 360.0 * k / M.CAP_N_SNAP + 360.0 / (2 * M.CAP_N_SNAP)
        slot = Rot(0, 0, th) * Pos(r_in, 0, 0) * Box(
            2 * M.CAP_WALL + 2, SLOT_W, SLOT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        slots.append(slot)
    body = body.cut(*slots)

    # grip flutes on the outside
    with BuildPart() as fp:
        with PolarLocations(r_out, 12):
            Box(2.4, 3.0, H, align=C)
    body = body.cut(*fp.solids())
    return body


MATES = {
    "rim": Pos(0, 0, 0),    # open rim; placed ~CAP_RIM_BELOW under the dome-cap ring
}

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    p = part()
    export_stl(p, "build/cap.stl")
    import trimesh
    m = trimesh.load("build/cap.stl")
    print("cap:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)
