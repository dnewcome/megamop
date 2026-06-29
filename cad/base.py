"""base.py — megamop base: screws onto a Gatorade bottle, carries the wick + mesh.

py cad/base.py -> build/base.stl

Body (one revolve of a meridian) + fused threads:
  - internal Gatorade thread on the skirt bore (bottle screws in here)
  - a bottle-neck stop shoulder, then a Ø FEED_BORE paint passage
  - a ~2" wick chamber (cup) with a perforated/ribbed floor (paint feed + wick backstop)
  - an EXTERNAL thread on the cup outer wall for the collar
The cup rim top face is the clamp seat: the collar lip pinches mesh + wick against it.
"""
import os
from build123d import (
    BuildPart, BuildSketch, BuildLine, Polyline, make_face, revolve,
    Axis, Plane, Pos, Rot, Box, Cylinder, Align, export_stl,
)
import machine_params as M
from threads import thread_ribs

# --- radii (all derived from the shared params) ----------------------------
r_bore      = M.SKIRT_BORE_R        # skirt internal thread root (bore wall)
r_skirt_out = M.SKIRT_OUTER_R
r_feed      = M.FEED_BORE_D / 2     # paint passage radius
r_cham      = M.WICK_CHAMBER_R      # wick chamber bore (~2")
r_cup_out   = M.CUP_OUTER_R         # cup outer wall == collar-thread root

# --- axial levels ----------------------------------------------------------
Z_STOP    = M.BOTTLE_THREAD_LEN + 1.0     # bottle-neck top seats here (~12)
Z_SKIRT   = M.SKIRT_H                      # top of straight skirt (15)
TRANS_H   = 6.0
Z_CUPBASE = Z_SKIRT + TRANS_H              # cup floor / transition top (21)
Z_RIM     = Z_CUPBASE + M.WICK_CHAMBER_H   # rim top = clamp seat (37)

ENTRY_CH  = 1.2   # lead-in flare at the skirt mouth so the bottle starts easily


def part():
    # Meridian cross-section in the X(=radius)–Z plane, closed loop.
    pts = [
        (r_bore + ENTRY_CH, 0.0),      # flared mouth (lead-in for the bottle)
        (r_bore, ENTRY_CH),
        (r_bore, Z_STOP),              # up the threaded skirt bore
        (r_feed, Z_STOP),              # bottle-neck stop shoulder (reduce to feed bore)
        (r_feed, Z_CUPBASE),           # feed passage wall
        (r_cham, Z_CUPBASE),           # wick chamber floor (annular ring)
        (r_cham, Z_RIM),               # chamber wall
        (r_cup_out, Z_RIM),            # rim top face (the clamp seat)
        (r_cup_out, Z_CUPBASE),        # cup outer wall (collar thread fuses here)
        (r_skirt_out, Z_SKIRT),        # transition cone cup->skirt
        (r_skirt_out, 0.0),            # skirt outer wall
    ]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        revolve(axis=Axis.Z)
    body = bp.part

    ribs = []
    # internal Gatorade thread on the skirt bore
    ribs += thread_ribs(
        r_bore, pitch=M.BOTTLE_THREAD_PITCH, starts=M.BOTTLE_THREAD_STARTS,
        length=M.BOTTLE_THREAD_LEN, depth=M.BOTTLE_THREAD_DEPTH,
        external=False, z0=ENTRY_CH + 0.3,
    )
    # external collar thread on the cup outer wall (ends ~2mm below rim for a lead)
    ext_len = M.CUP_THREAD_LEN
    ribs += thread_ribs(
        M.CUP_THREAD_ROOT_R, pitch=M.CUP_THREAD_PITCH, starts=M.CUP_THREAD_STARTS,
        length=ext_len, depth=M.CUP_THREAD_DEPTH, external=True,
        z0=Z_RIM - 2.0 - ext_len,
    )
    body = body.fuse(*ribs)

    # wick backstop: a cross-rib across the feed bore at the chamber floor, so the
    # foam can't get sucked back into the bottle on release. Welds into the floor ring.
    rib_len = 2 * r_cham            # spans the bore, sinks into the floor ring both ends
    bar = Box(rib_len, M.FEED_RIB_W, M.FEED_RIB_T,
              align=(Align.CENTER, Align.CENTER, Align.MIN))
    bar = Pos(0, 0, Z_CUPBASE) * bar
    body = body.fuse(bar, Rot(0, 0, 90) * bar)
    return body


# --- mate points (local frame, derived from constants) ---------------------
MATES = {
    "bottle":    Pos(0, 0, 0) * Rot(180, 0, 0),  # bottle joins from below, +Z points down
    "collar":    Pos(0, 0, Z_RIM),               # collar lip seats on the rim, +Z up
    "wick_seat": Pos(0, 0, Z_CUPBASE),           # wick floor
    "mesh_seat": Pos(0, 0, Z_RIM),               # mesh drapes over the rim
}

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    p = part()
    export_stl(p, "build/base.stl")
    import trimesh
    m = trimesh.load("build/base.stl")
    print("base:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)
