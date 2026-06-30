"""cap.py — snap-on STORAGE CAP that covers the dome cap (keeps the wick wet / tidy).

py cad/cap.py -> build/cap.stl

The cup thread is occupied by the dome cap, so this cover grabs the dome cap's outer
RING instead. Two-part retention (no snap-over detent):

  - an internal LAND (annular shelf) that the dome-ring TOP face rests against — a positive
    axial stop, so the cap always seats at the same depth and the ring can't over-travel; and
  - tapered WEDGE ribs down the slotted skirt that bear on the ring's OUTER wall with friction
    that GROWS as the cap seats (thin end at the rim, full interference up near the land) and
    RELEASES gradually as you pull it off — continuous friction, not a bump you must clear.

Local frame: z=0 at the open rim, +Z up to the closed top; in use the rim points toward the
bottle. The dome enters through the rim and its ring stops on the land; the dome bulge clears
the land's central opening. Targets the 2-piece dome (dome_ring, flat ring top); also seats on
the 1-piece dome_cap (lands on its frustum a hair higher).
"""
import os
from build123d import (
    Cylinder, Box, Pos, Rot, Align, PolarLocations, BuildPart, BuildSketch,
    BuildLine, Polyline, make_face, revolve, extrude, Axis, Plane, export_stl,
)
import machine_params as M

r_in   = M.CAP_INNER_R                     # slip bore over the ring OD (ring OD + CAP_CLEAR)
r_out  = M.CAP_OUTER_R
ring_od = M.COLLAR_OUTER_R                 # the dome-ring outer wall the wedges grip
H      = M.CAP_CAVITY_H + M.CAP_WALL       # total height (cavity + closed top)
N      = M.CAP_N_SNAP

# Where the dome ring sits inside the cap (cap frame): bottom near the rim, top at the land.
Z_RING_BOT = M.CAP_RIM_BELOW                       # ring bottom edge (rim is CAP_RIM_BELOW lower)
Z_RING_TOP = M.CAP_RIM_BELOW + M.DOME_RING_H       # ring top face -> the land plane
LAND_IR    = M.CAP_LAND_IR

# friction wedge taper: protrusion grows from ~0 at the rim end to CAP_WEDGE_INTERF near the land
Z_WEDGE_BOT = Z_RING_BOT + 1.0
Z_WEDGE_TOP = Z_RING_TOP - 1.0
RIB_W       = 10.0                          # tangential width of each wedge rib
WELD        = 1.0                           # overlap into the wall so fuses are clean (no slivers)

SLOT_W = 2.2
SLOT_H = Z_RING_TOP + 1.0                    # slots span the whole rib+land zone -> the segments flex


def _land():
    """Annular shelf the dome-ring TOP rests on; 45deg back-chamfer (closed-top side) prints clean."""
    ramp = (r_in + WELD) - LAND_IR
    pts = [
        (LAND_IR,       Z_RING_TOP),         # land face inner edge (ring rests here)
        (r_in + WELD,   Z_RING_TOP),         # ...out into the wall (overlap weld)
        (r_in + WELD,   Z_RING_TOP + ramp),  # 45deg ramp up the closed-top side
    ]
    with BuildPart() as lp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        revolve(axis=Axis.Z)
    return lp.part


def _wedge_ribs():
    """N tapered ribs: inner face ramps from inside the wall (flush) to ring_od-INTERF near the land."""
    r_top = ring_od - M.CAP_WEDGE_INTERF     # inner radius at the seated (max-grip) end
    ribs = []
    for k in range(N):
        th = 360.0 * k / N
        with BuildPart() as wp:
            with BuildSketch(Plane.XZ):      # X = radial, Z = axial
                with BuildLine():
                    Polyline(
                        (r_in + WELD, Z_WEDGE_BOT),   # buried in the wall at the rim end
                        (r_in + WELD, Z_WEDGE_TOP),
                        (r_top,       Z_WEDGE_TOP),   # max protrusion at the land end
                        close=True,
                    )
                make_face()
            extrude(amount=RIB_W / 2, both=True)
        ribs.append(Rot(0, 0, th) * wp.part)
    return ribs


def part():
    C = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Cylinder(r_out, H, align=C)
    body -= Cylinder(r_in, M.CAP_CAVITY_H, align=C)        # open cavity from the rim up
    body = body.fuse(_land())                              # internal land = positive seated stop
    body = body.fuse(*_wedge_ribs())                       # friction taper ribs

    # flex slots through the skirt, staggered between the ribs so each segment carries one rib
    slots = []
    for k in range(N):
        th = 360.0 * k / N + 360.0 / (2 * N)
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
