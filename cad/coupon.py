"""coupon.py — quick-print thread test coupons to VERIFY the Gatorade fit.

py cad/coupon.py -> build/coupon_A_lead7.2.stl  (pitch 3.6, 2-start, lead 7.2)
                    build/coupon_B_lead14.4.stl (pitch 7.2, 2-start, lead 14.4)

The one risky number in this whole design is the bottle thread. Print BOTH coupons
(each is a stubby ~15mm ring, a few minutes of filament) and screw them onto a real
Gatorade bottle. Whichever threads on cleanly tells us the true lead; report back:
  - threads on snug      -> that coupon's pitch is correct
  - too loose / strips   -> reduce THREAD_CLEAR_R
  - won't start / binds  -> wrong lead (use the other coupon) or increase clearance
A = 1 locating nub on the rim, B = 2 nubs, so you can tell them apart after printing.
"""
import os
from build123d import (
    Cylinder, Box, Pos, Rot, Align, PolarLocations, BuildPart, export_stl,
)
import machine_params as M
from threads import thread_ribs

WALL = 3.0
H = 14.0
r_bore = M.SKIRT_BORE_R                     # internal thread root (bore wall)
r_out = r_bore + WALL


def coupon(pitch, n_nubs):
    tube = Cylinder(r_out, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tube -= Cylinder(r_bore, H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ribs = thread_ribs(r_bore, pitch=pitch, starts=M.BOTTLE_THREAD_STARTS,
                       length=H - 2, depth=M.BOTTLE_THREAD_DEPTH,
                       external=False, z0=1.0)
    tube = tube.fuse(*ribs)
    # locating nubs on the top rim so A vs B is tactile after printing
    with BuildPart() as nb:
        with PolarLocations(r_out - 1, n_nubs, start_angle=0, angular_range=40 * n_nubs):
            Box(2, 2, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tube = tube.fuse(*[Pos(0, 0, H) * s for s in nb.solids()])
    return tube


if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    import trimesh
    for name, pitch, nubs in [("A_lead7.2", 3.6, 1), ("B_lead14.4", 7.2, 2)]:
        p = coupon(pitch, nubs)
        f = f"build/coupon_{name}.stl"
        export_stl(p, f)
        m = trimesh.load(f)
        print(f"coupon {name}:", (m.bounds[1] - m.bounds[0]).round(2),
              "bodies:", len(m.split(only_watertight=False)),
              "watertight:", m.is_watertight)
