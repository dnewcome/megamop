"""machine_angled.py — ANGLED megamop assembly with the printed perforated dome cap.

py cad/machine_angled.py
  -> build/base_angled.stl, build/dome_cap.stl    (the PRINTED parts)
  -> build/megamop_angled_iso.png + _section.png  (renders)

Same parts placed by mates as the straight build, but on base_angled's canted cup and
using dome_cap (printed perforated dome) instead of collar + sourced mesh. The wick is
the only remaining sourced consumable.
"""
import os
import subprocess
from build123d import Cylinder, Pos, Align, export_stl

import machine_params as M
from machine_params import place
import base_angled as base
import dome_cap


OUT = "build"
NAME = "megamop_angled"


def wick_standin():
    # foam/felt: fills the chamber, then a compressed nub squeezes up through the dome
    # throat into the dome cavity (representing the soft wick deforming through it)
    C = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Cylinder(M.WICK_CHAMBER_R - 0.5, M.WICK_CHAMBER_H, align=C)
    nub = Pos(0, 0, M.WICK_CHAMBER_H) * Cylinder(M.DOME_THROAT_R - 1.0, 9, align=C)
    return body.fuse(nub)


def bottle_standin():
    neck = Cylinder(M.BOTTLE_THREAD_MAJOR_D / 2, 14,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    shoulder = Pos(0, 0, 14) * Cylinder(34, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return neck.fuse(shoulder)


def assembly():
    return {
        "base":   base.part(),
        "cap":    place(dome_cap.part(), dome_cap.MATES["seat"], base.MATES["collar"]),
        "wick":   place(wick_standin(), Pos(0, 0, 0), base.MATES["wick_seat"]),
        "bottle": place(bottle_standin(), Pos(0, 0, 0), base.MATES["bottle"]),
    }


SCAD = """// %s — auto-written
$fn=96;
color([0.20,0.50,0.90]) import("asm_a_base.stl");
color([0.93,0.58,0.18]) import("asm_a_cap.stl");
color([0.95,0.90,0.45]) import("asm_a_wick.stl");
%%import("asm_a_bottle.stl");
""" % NAME

SCAD_SECTION = """// %s section — auto-written
$fn=96;
module half(c,f){ color(c) difference(){ import(f);
  translate([-200,0,-200]) cube([400,200,400]); } }
half([0.20,0.50,0.90],"asm_a_base.stl");
half([0.93,0.58,0.18],"asm_a_cap.stl");
half([0.95,0.90,0.45],"asm_a_wick.stl");
half([0.55,0.75,0.55],"asm_a_bottle.stl");
""" % NAME


def main():
    os.makedirs(OUT, exist_ok=True)
    parts = assembly()
    export_stl(base.part(), f"{OUT}/base_angled.stl")
    export_stl(dome_cap.part(), f"{OUT}/dome_cap.stl")
    for name, sol in parts.items():
        export_stl(sol, f"{OUT}/asm_a_{name}.stl")

    with open(f"{OUT}/{NAME}.scad", "w") as fh:
        fh.write(SCAD)
    with open(f"{OUT}/{NAME}_section.scad", "w") as fh:
        fh.write(SCAD_SECTION)

    import trimesh
    print(f"{'part':8} bbox(mm)")
    whole = []
    for name, sol in parts.items():
        m = trimesh.load(f"{OUT}/asm_a_{name}.stl")
        print(f"{name:8} {(m.bounds[1]-m.bounds[0]).round(1)}")
        whole.append(m)
    allm = trimesh.util.concatenate(whole)
    print("ASSEMBLY bbox:", (allm.bounds[1]-allm.bounds[0]).round(1),
          "z:", allm.bounds[:, 2].round(1))

    for scad, png, cam in [
        (f"{OUT}/{NAME}.scad", f"{OUT}/{NAME}_iso.png", "0,0,0,62,0,28,0"),
        (f"{OUT}/{NAME}_section.scad", f"{OUT}/{NAME}_section.png", "0,0,0,90,0,0,0"),
    ]:
        cmd = ["openscad", "-o", png, scad, "--imgsize=1100,900", "--projection=o",
               f"--camera={cam}", "--viewall", "--autocenter", "--colorscheme=Tomorrow"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print("render:", png if r.returncode == 0 else f"FAILED\n{r.stderr[-400:]}")


if __name__ == "__main__":
    main()
