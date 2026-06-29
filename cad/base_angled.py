"""base_angled.py — megamop base, ANGLED-NECK variant.

py cad/base_angled.py -> build/base_angled.stl

Same interfaces as base.py (bottle thread below, external collar thread on the cup,
~2" wick chamber) but the cup is canted CANT_DEG off the bottle axis so paint feeds
the tip when you hold the bottle tilted toward the wall. Geometry can't be one revolve
anymore, so it's built as:
    vertical skirt+riser (revolve, around Z)
  + a ball KNUCKLE at the elbow  (robust weld + rounds the bend)
  + a canted cup (revolve, rotated about Y at the elbow)
then the bent paint passage is bored through. All dims come from machine_params; the
cup/threads are identical to the straight base so the SAME collar/dome cap fits.
"""
import os
from build123d import (
    BuildPart, BuildSketch, BuildLine, Polyline, make_face, revolve,
    Axis, Plane, Pos, Rot, Box, Cylinder, Sphere, Align, export_stl,
)
import machine_params as M
from threads import thread_ribs

# shared radii
r_bore      = M.SKIRT_BORE_R
r_skirt_out = M.SKIRT_OUTER_R
r_feed      = M.FEED_BORE_D / 2
r_cham      = M.WICK_CHAMBER_R
r_cup_out   = M.CUP_OUTER_R
r_neck      = M.NECK_OUTER_R

Z_STOP   = M.BOTTLE_THREAD_LEN + 1.0
Z_SKIRT  = M.SKIRT_H
Z_P      = M.ELBOW_Z                 # elbow pivot on the bottle axis
ENTRY_CH = 1.2
RIM_LOC  = M.NECK_STUB + M.WICK_CHAMBER_H   # cup-local rim height (clamp seat)

# transform that cants the cup: neck base lands at the elbow P, axis tilts CANT about Y
T = Pos(0, 0, Z_P) * Rot(0, M.CANT_DEG, 0)


def skirt_lower():
    pts = [
        (r_bore + ENTRY_CH, 0.0),
        (r_bore, ENTRY_CH),
        (r_bore, Z_STOP),          # threaded skirt bore (bottle screws in)
        (r_feed, Z_STOP),          # bottle-neck stop shoulder
        (r_feed, Z_P),             # feed bore up to the elbow (open top)
        (r_neck, Z_P),             # riser top annulus
        (r_skirt_out, Z_SKIRT),    # outer: neck down to the fat skirt
        (r_skirt_out, 0.0),
    ]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        revolve(axis=Axis.Z)
    body = bp.part
    ribs = thread_ribs(r_bore, pitch=M.BOTTLE_THREAD_PITCH,
                       starts=M.BOTTLE_THREAD_STARTS, length=M.BOTTLE_THREAD_LEN,
                       depth=M.BOTTLE_THREAD_DEPTH, external=False, z0=ENTRY_CH + 0.3)
    return body.fuse(*ribs)


def cup_unit():
    """Hollow cup in its own local frame (z=0 neck base, +Z = cup axis)."""
    pts = [
        (r_feed, 0.0),
        (r_feed, M.NECK_STUB),         # neck bore
        (r_cham, M.NECK_STUB),         # chamber floor
        (r_cham, RIM_LOC),             # chamber wall
        (r_cup_out, RIM_LOC),          # rim top (clamp seat)
        (r_cup_out, M.NECK_STUB),      # cup outer wall
        (r_neck, 0.0),                 # taper cup -> neck
    ]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        revolve(axis=Axis.Z)
    body = bp.part
    # external collar thread on the cup outer (ends ~2mm below the rim)
    ribs = thread_ribs(M.CUP_THREAD_ROOT_R, pitch=M.CUP_THREAD_PITCH,
                       starts=M.CUP_THREAD_STARTS, length=M.CUP_THREAD_LEN,
                       depth=M.CUP_THREAD_DEPTH, external=True,
                       z0=RIM_LOC - 2.0 - M.CUP_THREAD_LEN)
    body = body.fuse(*ribs)
    # cross-rib wick backstop across the feed bore at the chamber floor
    bar = Box(2 * r_cham, M.FEED_RIB_W, M.FEED_RIB_T,
              align=(Align.CENTER, Align.CENTER, Align.MIN))
    bar = Pos(0, 0, M.NECK_STUB) * bar
    body = body.fuse(bar, Rot(0, 0, 90) * bar)
    return body


def part():
    # NOTE: a Sphere knuckle fuses badly onto the threaded skirt (splits into pieces);
    # two interpenetrating solid cylinders weld cleanly, so the elbow is built that way
    # and the bent paint channel is bored back through afterward.
    C = (Align.CENTER, Align.CENTER, Align.MIN)
    skirt = skirt_lower()
    cup = T * cup_unit()
    # solid elbow bridge: a vertical riser + a canted neck that interpenetrate at the elbow
    vert = Pos(0, 0, Z_SKIRT) * Cylinder(r_neck, (Z_P + 8) - Z_SKIRT, align=C)
    tilt = T * Pos(0, 0, -7) * Cylinder(r_neck, M.NECK_STUB + 7, align=C)
    body = skirt.fuse(vert, tilt, cup)
    # bore the bent feed channel back through the solid bridge (two overlapping bores)
    body = body.cut(Pos(0, 0, Z_STOP) * Cylinder(r_feed, (Z_P + 6) - Z_STOP, align=C))
    body = body.cut(T * Pos(0, 0, -7) * Cylinder(r_feed, M.NECK_STUB + 7, align=C))
    return body


MATES = {
    "bottle":    Pos(0, 0, 0) * Rot(180, 0, 0),
    "collar":    T * Pos(0, 0, RIM_LOC),        # tilted rim — collar/dome cap seats here
    "wick_seat": T * Pos(0, 0, M.NECK_STUB),
    "mesh_seat": T * Pos(0, 0, RIM_LOC),
}

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    p = part()
    export_stl(p, "build/base_angled.stl")
    import trimesh
    m = trimesh.load("build/base_angled.stl")
    print("base_angled:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)
