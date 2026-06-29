"""threads.py — helical thread rib generator, shared by base.py and collar.py.

Approach: sweep a trapezoidal thread profile along a build123d Helix, once per
start, and return the ribs as a list of solids to FUSE onto a core/wall. Profiles
sink `weld` mm into the supporting body so the fuse welds cleanly (build123d-part
rule: weld with real volume overlap, not a sliver).

  external thread -> ridge points +radial (outward), supported by a solid cylinder
  internal thread -> ridge points -radial (inward),  supported by a bored wall

Geometry conventions (radial = local +x in the swept profile plane, axial ~ +y):
  external: set mean_r = R_core,  crest at mean_r + depth  (== major/2)
  internal: set mean_r = R_bore,  crest at mean_r - depth  (== female crest/2)
"""
from build123d import (
    BuildPart, BuildSketch, BuildLine, Polyline, make_face, sweep, Helix,
    Plane, Pos, Rot, Vector,
)


def thread_ribs(mean_r, pitch, starts, length, depth, external=True,
                crest_frac=0.35, root_frac=0.80, hand_right=True, weld=0.5,
                z0=0.0):
    """Return a list of `starts` thread-rib solids (fuse them onto the body).

    mean_r  : radius of the supporting surface the ribs grow from
    pitch   : axial crest-to-crest spacing (LEAD = pitch * starts)
    length  : axial length of the threaded section
    depth   : radial thread depth (crest <-> root)
    external: True -> ridge outward, False -> ridge inward
    z0      : axial start of the threaded section
    """
    lead = pitch * starts
    sign = 1.0 if external else -1.0
    crest_w = crest_frac * pitch
    root_w = root_frac * pitch
    crest_x = sign * depth
    base_x = -sign * weld
    ribs = []
    for s in range(starts):
        path = Helix(pitch=lead, height=length, radius=mean_r,
                     lefthand=not hand_right)
        # offset each start: lift z by s*pitch and rotate so it tucks between others
        path = Pos(0, 0, z0) * Rot(0, 0, s * 360.0 / starts) * path
        start = path @ 0
        tan = path % 0
        radial = Vector(start.X, start.Y, 0)
        if radial.length < 1e-6:
            radial = Vector(1, 0, 0)
        radial = radial.normalized()
        pl = Plane(origin=start, x_dir=radial, z_dir=tan)
        with BuildPart() as bp:
            with BuildSketch(pl):
                with BuildLine():
                    Polyline(
                        (base_x, -root_w / 2),
                        (crest_x, -crest_w / 2),
                        (crest_x, crest_w / 2),
                        (base_x, root_w / 2),
                        (base_x, -root_w / 2),
                    )
                make_face()
            sweep(path=path)
        ribs.append(bp.part)
    return ribs


if __name__ == "__main__":
    # Self-test: build an internal-threaded ring and an external-threaded post,
    # fuse, and report watertight / body count.
    import os
    from build123d import Cylinder, Pos, Align, export_stl
    import trimesh

    os.makedirs("build", exist_ok=True)

    # internal: Ø38 2-start bottle-style thread inside a tube
    bore_r = 19.0 + 1.4
    tube = Cylinder(bore_r + 3, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tube -= Cylinder(bore_r, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ribs = thread_ribs(bore_r, pitch=3.6, starts=2, length=12, depth=1.4,
                        external=False)
    tube = tube.fuse(*ribs)
    export_stl(tube, "build/_test_internal.stl")
    m = trimesh.load("build/_test_internal.stl")
    print("internal:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)

    # external: thread on a solid post
    core_r = 28.0
    post = Cylinder(core_r, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ribs = thread_ribs(core_r, pitch=3.0, starts=1, length=9, depth=1.5,
                       external=True)
    post = post.fuse(*ribs)
    export_stl(post, "build/_test_external.stl")
    m = trimesh.load("build/_test_external.stl")
    print("external:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight)
