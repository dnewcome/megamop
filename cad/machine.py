"""machine.py — megamop assembly: place every part by its mates, render, export.

py cad/machine.py
  -> build/base.stl, build/collar.stl        (the two PRINTED parts)
  -> build/asm_*.stl + build/megamop.scad    (assembly render inputs)
  -> build/megamop_iso.png                   (openscad iso render; run via this script)

No part is hand-placed: the collar snaps onto the base's "collar" mate, the wick and
mesh stand-ins (sourced, not printed) snap onto their seats. A manifest prints so a
missing/flung part is obvious (bbox blow-up == a bad mate).
"""
import os
import subprocess
from functools import reduce
from build123d import Cylinder, Pos, Rot, Align, Compound, export_stl

import machine_params as M
from machine_params import place
import base
import collar

OUT = "build"


def wick_standin():
    # foam/felt stand-in: sits on the chamber floor, filling the ~2" cup
    return Cylinder(M.WICK_D / 2, M.WICK_CHAMBER_H,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))


def mesh_standin():
    return Cylinder(M.MESH_D / 2, M.MESH_T,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))


def bottle_standin():
    # crude Gatorade neck for render context (not a printed part). Built pointing +Z
    # so the "bottle" mate (which points -Z) flips it to sit BELOW the base.
    neck = Cylinder(M.BOTTLE_THREAD_MAJOR_D / 2, 14,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    shoulder = Pos(0, 0, 14) * Cylinder(34, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return neck.fuse(shoulder)


def assembly():
    parts = {}
    parts["base"] = base.part()
    parts["collar"] = place(collar.part(), collar.MATES["seat"], base.MATES["collar"])
    parts["wick"] = place(wick_standin(), Pos(0, 0, 0), base.MATES["wick_seat"])
    parts["mesh"] = place(mesh_standin(), Pos(0, 0, 0), base.MATES["mesh_seat"])
    parts["bottle"] = place(bottle_standin(), Pos(0, 0, 0), base.MATES["bottle"])
    return parts


SCAD = """// megamop assembly — auto-written by machine.py
$fn=96;
color([0.20,0.50,0.90]) import("asm_base.stl");
color([0.93,0.58,0.18]) import("asm_collar.stl");
color([0.95,0.90,0.45]) import("asm_wick.stl");
color([0.80,0.80,0.82]) import("asm_mesh.stl");
%import("asm_bottle.stl");
"""

# half-section: keep the y<0 half of each part so the interior is visible
SCAD_SECTION = """// megamop half-section — auto-written by machine.py
$fn=96;
module half(c,f){ color(c) difference(){ import(f);
  translate([-200,0,-200]) cube([400,200,400]); } }
half([0.20,0.50,0.90],"asm_base.stl");
half([0.93,0.58,0.18],"asm_collar.stl");
half([0.95,0.90,0.45],"asm_wick.stl");
half([0.80,0.80,0.82],"asm_mesh.stl");
half([0.55,0.75,0.55],"asm_bottle.stl");
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    parts = assembly()

    # export the two real print parts (local frame) + the placed assembly pieces
    export_stl(base.part(), f"{OUT}/base.stl")
    export_stl(collar.part(), f"{OUT}/collar.stl")
    for name, sol in parts.items():
        export_stl(sol, f"{OUT}/asm_{name}.stl")

    with open(f"{OUT}/megamop.scad", "w") as fh:
        fh.write(SCAD)
    with open(f"{OUT}/megamop_section.scad", "w") as fh:
        fh.write(SCAD_SECTION)

    # manifest — bbox per part; a wrong mate shows up as a flung bbox
    import trimesh
    print(f"{'part':8} {'count':>5}  bbox(mm)")
    whole = []
    for name, sol in parts.items():
        m = trimesh.load(f"{OUT}/asm_{name}.stl")
        bb = (m.bounds[1] - m.bounds[0]).round(1)
        print(f"{name:8} {1:>5}  {bb}")
        whole.append(m)
    allmesh = trimesh.util.concatenate(whole)
    print("ASSEMBLY bbox:", (allmesh.bounds[1] - allmesh.bounds[0]).round(1),
          " z-range:", allmesh.bounds[:, 2].round(1))

    # render iso + half-section via openscad (headless)
    for scad, png, cam in [
        (f"{OUT}/megamop.scad", f"{OUT}/megamop_iso.png", "0,0,0,62,0,28,0"),
        (f"{OUT}/megamop_section.scad", f"{OUT}/megamop_section.png", "0,0,0,90,0,0,0"),
    ]:
        cmd = ["openscad", "-o", png, scad, "--imgsize=1100,900",
               "--projection=o", f"--camera={cam}", "--viewall", "--autocenter",
               "--colorscheme=Tomorrow"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print("render:", png if r.returncode == 0 else f"FAILED\n{r.stderr[-400:]}")


if __name__ == "__main__":
    main()
