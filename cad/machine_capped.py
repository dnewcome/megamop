"""machine_capped.py — angled megamop with the snap-on storage cap fitted (config view).

py cad/machine_capped.py -> build/megamop_capped_iso.png + _section.png

Same parts as machine_angled.py plus cap.py snapped over the dome cap. The cover is drawn
translucent so the dome reads through it. Verifies fit/clearance of the storage cap.
"""
import os
import subprocess
from build123d import Pos, export_stl

import machine_params as M
from machine_params import place
import base_angled as base
import dome_cap
import cap

OUT = "build"
NAME = "megamop_capped"


def assembly():
    collar = base.MATES["collar"]
    return {
        "base":  base.part(),
        "dome":  place(dome_cap.part(), dome_cap.MATES["seat"], collar),
        "cover": place(cap.part(), cap.MATES["rim"],
                       collar * Pos(0, 0, -(M.DOME_RING_H + M.CAP_RIM_BELOW))),
    }


SCAD = """// %s — auto-written
$fn=96;
color([0.20,0.50,0.90])     import("asm_cap_base.stl");
color([0.93,0.58,0.18])     import("asm_cap_dome.stl");
color([0.45,0.78,0.55,0.45]) import("asm_cap_cover.stl");
""" % NAME

SCAD_SECTION = """// %s section — auto-written
$fn=96;
module half(c,f){ color(c) difference(){ import(f);
  translate([-200,0,-200]) cube([400,200,400]); } }
half([0.20,0.50,0.90],"asm_cap_base.stl");
half([0.93,0.58,0.18],"asm_cap_dome.stl");
half([0.45,0.78,0.55],"asm_cap_cover.stl");
""" % NAME


def main():
    os.makedirs(OUT, exist_ok=True)
    parts = assembly()
    export_stl(cap.part(), f"{OUT}/cap.stl")
    for n, s in parts.items():
        export_stl(s, f"{OUT}/asm_cap_{n}.stl")
    with open(f"{OUT}/{NAME}.scad", "w") as fh:
        fh.write(SCAD)
    with open(f"{OUT}/{NAME}_section.scad", "w") as fh:
        fh.write(SCAD_SECTION)

    import trimesh
    for n in parts:
        m = trimesh.load(f"{OUT}/asm_cap_{n}.stl")
        print(f"{n:6} {(m.bounds[1]-m.bounds[0]).round(1)}")

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
