"""coupon.py — thread test coupons to dial the thread PROFILE width.

py cad/coupon.py -> build/coupon_thin.stl    (ridge 40% of pitch, 1 nub)
                    build/coupon_thinner.stl (ridge 28% of pitch, 2 nubs)

Geometry is pinned (Ø38 38-400, 2-start, pitch 3.0/lead 6.0). The bottle's MALE threads are
thick, so our female ridges must be thin enough that the valleys accept them — too-fat ridges
bind as you screw in. These two coupons differ only in ridge width; print both, screw onto the
bottle, use whichever threads on cleanly (the thinner one if the bottle threads are very thick).
1 nub = thin, 2 nubs = thinner.
"""
import os
from build123d import (
    Cylinder, Box, Pos, Align, PolarLocations, BuildPart, export_stl,
)
import machine_params as M
from threads import thread_ribs

WALL = 2.2
H = 7.0


def coupon(root_frac, crest_frac, n_nubs):
    crest_r = M.BOTTLE_THREAD_ROOT_D / 2 + M.THREAD_CLEAR_R
    bore_r = crest_r + M.BOTTLE_THREAD_DEPTH
    r_out = bore_r + WALL
    tube = Cylinder(r_out, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tube -= Cylinder(bore_r, H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ribs = thread_ribs(bore_r, pitch=M.BOTTLE_THREAD_PITCH, starts=M.BOTTLE_THREAD_STARTS,
                       length=H - 2, depth=M.BOTTLE_THREAD_DEPTH, external=False, z0=1.0,
                       root_frac=root_frac, crest_frac=crest_frac)
    tube = tube.fuse(*ribs)
    with BuildPart() as nb:
        with PolarLocations(r_out - 1, n_nubs, start_angle=0, angular_range=40 * n_nubs):
            Box(2, 2, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tube = tube.fuse(*[Pos(0, 0, H) * s for s in nb.solids()])
    return tube


if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    import trimesh
    for name, rf, cf, nubs in [("thin", 0.40, 0.18, 1), ("thinner", 0.28, 0.14, 2)]:
        p = coupon(rf, cf, nubs)
        f = f"build/coupon_{name}.stl"
        export_stl(p, f)
        m = trimesh.load(f)
        print(f"coupon {name} (ridge {int(rf*100)}% of pitch):",
              (m.bounds[1] - m.bounds[0]).round(2),
              "bodies:", len(m.split(only_watertight=False)),
              "watertight:", m.is_watertight)
