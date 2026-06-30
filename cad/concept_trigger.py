"""concept_trigger.py — CONCEPT massing model of the trigger-handle paint applicator.

py cad/concept_trigger.py -> build/concept_trigger.glb (+ per-part STLs)

NOT a working mechanism or a printable part — a form study for renders: an inverted Gatorade
bottle (paint reservoir, gravity-feed) on a pistol-grip body with a trigger, and the perforated
mop dome projecting forward. Reuses the real bottle + dome for context. Frame: +X forward, +Z up.
"""
import os
from build123d import (
    Box, Cylinder, Cone, Sphere, Pos, Rot, Align, BuildPart, fillet, export_stl,
)
import machine_params as M
import bottle
import dome_ring
import dome_tpu

C = (Align.CENTER, Align.CENTER, Align.CENTER)


def rounded_box(x, y, z, r):
    with BuildPart() as bp:
        Box(x, y, z)
        fillet(bp.edges(), r)
    return bp.part


def capsule(r, length):
    c = Cylinder(r, length, align=C)
    return c.fuse(Pos(0, 0, length / 2) * Sphere(r), Pos(0, 0, -length / 2) * Sphere(r))


def bottle_local():
    # neck at origin pointing -Z (down), body going +Z (so it can hang inverted on the body)
    return Rot(0, 180, 0) * Pos(0, 0, -bottle.NECK_TOP) * bottle.shell()


def tip_local():
    # ring + red perforated dome stacked, apex pointing +Z in local frame
    ring = dome_ring.part()
    dome = Pos(0, 0, M.DOME_RING_H - M.DRING_LIP_T) * dome_tpu.part()
    return ring, dome


def torus_guard():
    from build123d import Torus
    g = Rot(90, 0, 0) * Torus(21, 3.6)        # loop in the X-Z (side-profile) plane
    return g


# ---- world placement of the massing ----------------------------------------
T_BOTTLE = Pos(-7, 0, 26) * Rot(0, -7, 0)            # inverted reservoir, slight back lean
T_GRIP = Pos(-15, 0, -66) * Rot(0, 15, 0)           # longer raked pistol grip
T_TRIG = Pos(7, 0, -46) * Rot(0, -14, 0)            # trigger blade inside the guard
T_GUARD = Pos(7, 0, -47)                            # trigger guard loop
T_TIP = Pos(54, 0, -16) * Rot(0, 118, 0)            # mop tip projects forward + ~28deg down
T_NECK = Pos(30, 0, -6) * Rot(0, 118, 0)            # barrel/neck from body front to the tip

ring_l, dome_l = tip_local()
ORANGE = (0.95, 0.45, 0.06, 1.0)
CHARCOAL = (0.15, 0.15, 0.17, 1.0)

# (name, world solid, rgba, metallic, roughness)
SCENE = [
    ("body",   rounded_box(58, 40, 54, 8),                           CHARCOAL, 0.2, 0.45),
    ("grip",   T_GRIP * capsule(15, 82),                             ORANGE, 0.0, 0.6),
    ("guard",  T_GUARD * torus_guard(),                              CHARCOAL, 0.2, 0.5),
    ("trigger", T_TRIG * rounded_box(5, 12, 26, 2.2),                ORANGE, 0.0, 0.6),
    ("neck",   T_NECK * Cone(17, 18, 34, align=(Align.CENTER, Align.CENTER, Align.MIN)),
                                                                     CHARCOAL, 0.2, 0.45),
    ("tip_ring", T_TIP * ring_l,                                     (0.11, 0.11, 0.12, 1.0), 0.2, 0.5),
    ("tip_dome", T_TIP * dome_l,                                     (0.83, 0.09, 0.11, 1.0), 0.0, 0.7),
    ("bottle", T_BOTTLE * bottle_local(),                            (0.88, 0.42, 0.08, 0.40), 0.0, 0.10),
    ("label",  T_BOTTLE * Rot(0, 180, 0) * Pos(0, 0, -bottle.NECK_TOP) * bottle.label(),
                                                                     (0.93, 0.93, 0.93, 1.0), 0.0, 0.6),
]


def main():
    os.makedirs("build", exist_ok=True)
    for name, sol, *_ in SCENE:
        export_stl(sol, f"build/ct_{name}.stl",
                   tolerance=0.03, angular_tolerance=0.1)

    import trimesh
    from trimesh.visual.material import PBRMaterial
    scene = trimesh.Scene()
    for name, _sol, rgba, metal, rough in SCENE:
        m = trimesh.load(f"build/ct_{name}.stl")
        m.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(
            name=name, baseColorFactor=rgba, metallicFactor=metal, roughnessFactor=rough,
            alphaMode="BLEND" if rgba[3] < 1.0 else "OPAQUE", doubleSided=True))
        scene.add_geometry(m, geom_name=name)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-1.5708, [1, 0, 0]))  # Z-up->Y-up
    scene.export("build/concept_trigger.glb")
    print("GLB:", f"build/concept_trigger.glb ({os.path.getsize('build/concept_trigger.glb')//1024} KB)",
          " extents:", scene.extents.round(0))


if __name__ == "__main__":
    main()
