"""glb_export.py — export the mop-on-a-bottle as a textured GLB (+ an openscad preview).

py cad/glb_export.py
  -> build/megamop.glb            (the deliverable: PBR materials, drop into any 3D viewer)
  -> build/glb_preview.png        (openscad sanity render of the same scene)

Scene: realistic Gatorade-style bottle (clear shell + orange liquid + label) with the
angled-neck mop + flexible TPU dome threaded onto the neck.
"""
import os
import subprocess
from build123d import Pos, export_stl

import machine_params as M
from machine_params import place
import bottle
import base_angled as base
import dome_ring
import dome_tpu

OUT = "build"
MOP_Z = bottle.NECK_TOP - 10.0          # drop the skirt ~10mm over the neck
UP = Pos(0, 0, MOP_Z)

# (name, build123d solid, RGBA, metallic, roughness)
SCENE = [
    ("bottle_shell",  bottle.shell(),  (0.90, 0.95, 0.97, 0.22), 0.0, 0.05),
    ("bottle_liquid", bottle.liquid(), (0.96, 0.42, 0.04, 1.0),  0.0, 0.25),
    ("bottle_label",  bottle.label(),  (0.93, 0.93, 0.93, 1.0),  0.0, 0.6),
    ("mop_base",  UP * base.part(),                                            (0.05, 0.05, 0.06, 1.0), 0.1, 0.5),
    ("mop_ring",  UP * place(dome_ring.part(), dome_ring.MATES["seat"],
                            base.MATES["collar"] * Pos(0, 0, M.DTPU_FLANGE_T)),(0.07, 0.07, 0.08, 1.0), 0.2, 0.5),
    ("mop_dome",  UP * place(dome_tpu.part(), dome_tpu.MATES["flange"],
                            base.MATES["mesh_seat"]),                          (0.82, 0.08, 0.10, 1.0), 0.0, 0.7),
]

# openscad preview colours mirror the GLB
PREVIEW = {
    "bottle_shell": "[0.85,0.92,0.95,0.25]", "bottle_liquid": "[0.96,0.42,0.04]",
    "bottle_label": "[0.93,0.93,0.93]", "mop_base": "[0.10,0.10,0.12]",
    "mop_ring": "[0.12,0.12,0.14]", "mop_dome": "[0.82,0.08,0.10]",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, solid, *_ in SCENE:
        # finer tessellation for the smooth bottle surfaces
        if name.startswith("bottle"):
            export_stl(solid, f"{OUT}/glb_{name}.stl",
                       tolerance=0.02, angular_tolerance=0.05)
        else:
            export_stl(solid, f"{OUT}/glb_{name}.stl")

    # --- openscad preview ------------------------------------------------------
    scad = "$fn=120;\n" + "".join(
        f'color({PREVIEW[n]}) import("glb_{n}.stl");\n' for n, *_ in SCENE)
    with open(f"{OUT}/glb_preview.scad", "w") as fh:
        fh.write(scad)
    r = subprocess.run(["openscad", "-o", f"{OUT}/glb_preview.png",
                        f"{OUT}/glb_preview.scad", "--imgsize=900,1200",
                        "--projection=p", "--camera=0,0,0,72,0,22,0",
                        "--viewall", "--autocenter", "--colorscheme=Tomorrow"],
                       capture_output=True, text=True)
    print("preview:", f"{OUT}/glb_preview.png" if r.returncode == 0 else r.stderr[-300:])

    # --- GLB with PBR materials ------------------------------------------------
    import trimesh
    from trimesh.visual.material import PBRMaterial
    scene = trimesh.Scene()
    for name, _solid, rgba, metal, rough in SCENE:
        m = trimesh.load(f"{OUT}/glb_{name}.stl")
        m.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(
            name=name, baseColorFactor=rgba, metallicFactor=metal,
            roughnessFactor=rough, alphaMode="BLEND" if rgba[3] < 1.0 else "OPAQUE",
            doubleSided=True))
        scene.add_geometry(m, geom_name=name)
    # Z-up (CAD) -> Y-up (glTF convention) so it stands upright in viewers
    scene.apply_transform(trimesh.transformations.rotation_matrix(-1.5708, [1, 0, 0]))
    scene.export(f"{OUT}/megamop.glb")
    print("GLB:", f"{OUT}/megamop.glb",
          f"({os.path.getsize(f'{OUT}/megamop.glb')//1024} KB)")


if __name__ == "__main__":
    main()
