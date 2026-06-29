"""machine_flex.py — angled megamop with the TWO-PIECE flexible TPU dome (config view).

py cad/machine_flex.py -> build/megamop_flex_iso.png + _section.png

Rigid dome_ring (PETG) clamps the flexible dome_tpu (TPU) flange against the cup rim; the
soft perforated dome bulges through the ring aperture. TPU dome drawn red to flag material.
The cap.py storage cap still fits over the Ø68 ring (not shown here).
"""
import os
import subprocess
from build123d import Cylinder, Pos, Align, export_stl

import machine_params as M
from machine_params import place
import base_angled as base
import dome_ring
import dome_tpu

OUT = "build"
NAME = "megamop_flex"


def wick_standin():
    C = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Cylinder(M.WICK_CHAMBER_R - 0.5, M.WICK_CHAMBER_H, align=C)
    nub = Pos(0, 0, M.WICK_CHAMBER_H) * Cylinder(M.DTPU_THROAT_R - 1.0, 8, align=C)
    return body.fuse(nub)


def assembly():
    rim = base.MATES["mesh_seat"]      # cup rim (where the TPU flange sits)
    return {
        "base": base.part(),
        "tpu":  place(dome_tpu.part(), dome_tpu.MATES["flange"], rim),
        "ring": place(dome_ring.part(), dome_ring.MATES["seat"],
                      rim * Pos(0, 0, M.DTPU_FLANGE_T)),   # lip clamps onto the 2mm flange
        "wick": place(wick_standin(), Pos(0, 0, 0), base.MATES["wick_seat"]),
    }


SCAD = """// %s — auto-written
$fn=96;
color([0.20,0.50,0.90]) import("asm_f_base.stl");
color([0.88,0.20,0.25]) import("asm_f_tpu.stl");
color([0.93,0.58,0.18]) import("asm_f_ring.stl");
color([0.95,0.90,0.45]) import("asm_f_wick.stl");
""" % NAME

SCAD_SECTION = """// %s section — auto-written
$fn=96;
module half(c,f){ color(c) difference(){ import(f);
  translate([-200,0,-200]) cube([400,200,400]); } }
half([0.20,0.50,0.90],"asm_f_base.stl");
half([0.88,0.20,0.25],"asm_f_tpu.stl");
half([0.93,0.58,0.18],"asm_f_ring.stl");
half([0.95,0.90,0.45],"asm_f_wick.stl");
""" % NAME


def main():
    os.makedirs(OUT, exist_ok=True)
    parts = assembly()
    export_stl(dome_ring.part(), f"{OUT}/dome_ring.stl")
    export_stl(dome_tpu.part(), f"{OUT}/dome_tpu.stl")
    for n, s in parts.items():
        export_stl(s, f"{OUT}/asm_f_{n}.stl")
    with open(f"{OUT}/{NAME}.scad", "w") as fh:
        fh.write(SCAD)
    with open(f"{OUT}/{NAME}_section.scad", "w") as fh:
        fh.write(SCAD_SECTION)

    import trimesh
    for n in parts:
        m = trimesh.load(f"{OUT}/asm_f_{n}.stl")
        print(f"{n:5} {(m.bounds[1]-m.bounds[0]).round(1)}")

    for scad, png, cam in [
        (f"{OUT}/{NAME}.scad", f"{OUT}/{NAME}_iso.png", "0,0,0,62,0,28,0"),
        (f"{OUT}/{NAME}_section.scad", f"{OUT}/{NAME}_section.png", "0,0,0,90,0,0,0"),
    ]:
        r = subprocess.run(["openscad", "-o", png, scad, "--imgsize=1100,900",
                            "--projection=o", f"--camera={cam}", "--viewall",
                            "--autocenter", "--colorscheme=Tomorrow"],
                           capture_output=True, text=True)
        print("render:", png if r.returncode == 0 else f"FAILED {r.stderr[-300:]}")


if __name__ == "__main__":
    main()
