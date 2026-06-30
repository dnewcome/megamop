"""concept_trigger_cutaway.py — labeled cutaway schematic of the trigger-pumped-air mechanism.

py cad/concept_trigger_cutaway.py -> build/concept_trigger_cutaway.png (+ .svg)

A 2D engineering cutaway (not CAD) of the leading mechanism: a trigger pumps AIR up a dip-tube
into the inverted bottle's headspace (pressurizing it); the pressure pushes paint to a
trigger-cammed pinch valve and out the perforated dome. Air path = blue, paint path = amber.
Uses the real bottle silhouette (bottle.OUTER).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch, Rectangle, FancyArrowPatch
import bottle

PAINT, PAINT_DK = "#cf7e34", "#9c5a1c"
AIR = "#2f78cf"
PLASTIC = "#2c2c33"
ACCENT = "#e8761a"
BPLAST = "#e6ebee"
RED = "#c8242c"
EDGE = "#15151a"

CX, S, Y0 = 40.0, 0.30, 120.0
def yz(z): return Y0 - z * S
def bx(r, side=1): return CX + side * r * S
NECK_Y = yz(214)


def bottle_poly(zmin=0.0, zmax=214.0):
    p = [(bx(r, -1), yz(z)) for r, z in bottle.OUTER if zmin <= z <= zmax]
    p += [(bx(r, +1), yz(z)) for r, z in reversed(bottle.OUTER) if zmin <= z <= zmax]
    return p


def arrow(ax, p0, p1, color, lw=2.6):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=15, lw=lw,
                                 color=color, zorder=7))


def tri(ax, cx, cy, color, up=True, sz=3.0):  # one-way valve glyph
    s = sz if up else -sz
    ax.add_patch(Polygon([(cx - sz, cy - s), (cx + sz, cy - s), (cx, cy + s)],
                         closed=True, facecolor="white", edgecolor=color, lw=1.6, zorder=8))


def lbl(ax, text, xy, xytext, ha):
    ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va="center", fontsize=10, color="#111",
                zorder=11, arrowprops=dict(arrowstyle="-", color="#666", lw=1.0))


def main():
    os.makedirs("build", exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(-12, 116); ax.set_ylim(-2, 128); ax.axis("off"); ax.set_aspect("equal")
    ax.set_title("megamop — trigger-pumped-air applicator (cutaway concept)",
                 fontsize=15, fontweight="bold", pad=10)

    # bottle ----------------------------------------------------------------------
    ax.add_patch(Polygon(bottle_poly(), closed=True, facecolor=BPLAST, edgecolor=EDGE, lw=2, zorder=1))
    ax.add_patch(Polygon(bottle_poly(138, 214), closed=True, facecolor=PAINT, alpha=0.9,
                         edgecolor="none", zorder=2))
    ax.text(CX, yz(72), "AIR\n(pressurized\nheadspace)", ha="center", va="center",
            fontsize=11, color=AIR, fontweight="bold", zorder=5)
    ax.text(CX, yz(190), "paint", ha="center", va="center", fontsize=10.5,
            color="#4a2c0c", fontweight="bold", zorder=5)

    # cap + o-ring + relief -------------------------------------------------------
    ax.add_patch(FancyBboxPatch((CX - 11, NECK_Y - 7), 22, 8.5, boxstyle="round,pad=0.2,rounding_size=1",
                                facecolor="#3a3a42", edgecolor=EDGE, lw=1.6, zorder=4))
    for sx in (-7.4, 7.4):
        ax.add_patch(Circle((CX + sx, NECK_Y - 2), 1.1, facecolor="#0a0a0a", zorder=6))
    ax.add_patch(Rectangle((CX - 4, NECK_Y - 2.5), 4, 5, facecolor="#888", edgecolor=EDGE, lw=1, zorder=5))
    arrow(ax, (CX - 2, NECK_Y + 1), (CX - 6, NECK_Y + 5), "#888", 1.6)        # relief vent

    # body / grip / trigger -------------------------------------------------------
    ax.add_patch(FancyBboxPatch((CX - 16, NECK_Y - 32), 42, 26, boxstyle="round,pad=0.3,rounding_size=3",
                                facecolor=PLASTIC, edgecolor=EDGE, lw=1.8, zorder=3))
    ax.add_patch(Polygon([(CX - 13, NECK_Y - 30), (CX - 4, NECK_Y - 30), (CX - 12, NECK_Y - 58),
                          (CX - 21, NECK_Y - 58)], closed=True, facecolor=ACCENT, edgecolor=EDGE, lw=1.6, zorder=2))
    ax.add_patch(Polygon([(CX + 5, NECK_Y - 18), (CX + 10, NECK_Y - 22), (CX + 8, NECK_Y - 36),
                          (CX + 3, NECK_Y - 32)], closed=True, facecolor=ACCENT, edgecolor=EDGE, lw=1.6, zorder=6))

    # AIR pump (bellows) + path to headspace --------------------------------------
    bxp, byt, byb = CX + 18, NECK_Y - 20, NECK_Y - 34
    zig = [(bxp + (2.4 if i % 2 else -2.4), byt - i * (byt - byb) / 7) for i in range(8)]
    ax.plot([p[0] for p in zig], [p[1] for p in zig], color=AIR, lw=3.2, zorder=5)
    arrow(ax, (bxp + 12, byb + 1), (bxp + 4, byb + 1), AIR, 2.0)              # atmosphere intake
    tri(ax, bxp + 4, byb + 1, AIR, up=False, sz=2.4)                          # intake check valve
    ax.plot([bxp, bxp, CX, CX], [byt, NECK_Y - 3, NECK_Y - 3, yz(96)], color=AIR, lw=2.6, zorder=4)
    arrow(ax, (CX, yz(124)), (CX, yz(104)), AIR, 2.6)
    tri(ax, CX, yz(96), AIR, up=True, sz=3.2)                                 # umbrella valve

    # PAINT path: neck -> pinch valve -> dome -------------------------------------
    pinx, piny = CX + 40, NECK_Y - 16
    ax.plot([CX, CX, pinx - 5], [NECK_Y - 2, NECK_Y - 16, piny], color=PAINT_DK, lw=3.4, zorder=4)
    arrow(ax, (CX, NECK_Y - 6), (CX, NECK_Y - 13), PAINT_DK, 2.6)
    arrow(ax, (CX + 14, NECK_Y - 16), (CX + 26, NECK_Y - 16), PAINT_DK, 2.6)
    ax.add_patch(Rectangle((pinx - 5, piny - 1.8), 11, 3.6, facecolor="#d6b8b8",
                           edgecolor=PAINT_DK, lw=1.4, zorder=4))             # pinch tube
    ax.add_patch(Polygon([(pinx, piny + 6), (pinx + 3.5, piny + 2), (pinx - 1, piny + 1.8)],
                         closed=True, facecolor="#666", edgecolor=EDGE, lw=1.2, zorder=7))   # cam
    domx = pinx + 16
    ax.add_patch(Polygon([(domx - 6, piny - 7), (domx - 6, piny + 7), (domx + 5, piny + 4),
                          (domx + 5, piny - 4)], closed=True, facecolor="#222", edgecolor=EDGE, lw=1.4, zorder=4))
    ax.add_patch(Polygon([(domx + 3, piny + 7), (domx + 11, piny + 4), (domx + 11, piny - 4),
                          (domx + 3, piny - 7)], closed=True, facecolor=RED, alpha=0.9, edgecolor=EDGE, lw=1, zorder=5))
    for i in (-4, -1.3, 1.3, 4):
        ax.add_patch(Circle((domx + 7, piny + i), 0.8, facecolor="#7a0f12", zorder=6))
    arrow(ax, (domx + 11, piny), (domx + 20, piny - 3), PAINT, 2.8)          # paint out

    # labels: left column ---------------------------------------------------------
    lbl(ax, "Inverted Gatorade bottle\n(paint reservoir)", (bx(-33), yz(45)), (-12, yz(45)), "left")
    lbl(ax, "O-ring neck seal", (CX - 7.4, NECK_Y - 2), (-12, NECK_Y - 1), "left")
    lbl(ax, "Pressure-relief valve\n(\"pressure check\")", (CX - 4, NECK_Y), (-12, NECK_Y - 14), "left")
    lbl(ax, "Trigger", (CX + 5, NECK_Y - 27), (-12, NECK_Y - 30), "left")
    lbl(ax, "Grip", (CX - 16, NECK_Y - 48), (-12, NECK_Y - 48), "left")
    # labels: right column --------------------------------------------------------
    lbl(ax, "Umbrella check valve\n(air in; paint can't back up)", (CX + 3, yz(96)), (66, yz(96)), "left")
    lbl(ax, "Air dip-tube", (CX, yz(150)), (66, yz(150)), "left")
    lbl(ax, "Air pump (TPU bellows)\n+ intake check valve", (bxp + 2, (byt + byb) / 2), (70, NECK_Y - 40), "left")
    lbl(ax, "Spring-loaded PINCH valve\n(trigger-cammed = the control)", (pinx, piny + 4), (70, NECK_Y - 2), "left")
    lbl(ax, "Perforated mop dome", (domx + 4, piny), (88, NECK_Y - 26), "left")

    # trigger timing inset --------------------------------------------------------
    ix, iy, iw = -10, 6, 46
    ax.add_patch(FancyBboxPatch((ix, iy), iw, 18, boxstyle="round,pad=0.5,rounding_size=2",
                                facecolor="#f4f4f6", edgecolor="#999", lw=1, zorder=9))
    ax.text(ix + iw / 2, iy + 15, "trigger travel  →", ha="center", fontsize=10, fontweight="bold", zorder=10)
    for col, a, b in [("#cc4040", 0, .15), ("#f0c020", .15, .35), ("#52a05a", .35, 1)]:
        ax.add_patch(Rectangle((ix + 4 + a * (iw - 8), iy + 8), (b - a) * (iw - 8), 3.4,
                               facecolor=col, edgecolor="none", zorder=10))
    ax.text(ix + 4 + .07 * (iw - 8), iy + 5.5, "release\n= CLOSED", ha="center", fontsize=7.5, zorder=10)
    ax.text(ix + 4 + .25 * (iw - 8), iy + 12.5, "valve\nopens", ha="center", fontsize=7.5, zorder=10)
    ax.text(ix + 4 + .67 * (iw - 8), iy + 5.5, "half-pump here = flow + pressure", ha="center",
            fontsize=8, zorder=10)

    fig.savefig("build/concept_trigger_cutaway.png", dpi=130, bbox_inches="tight", facecolor="white")
    fig.savefig("build/concept_trigger_cutaway.svg", bbox_inches="tight", facecolor="white")
    print("wrote build/concept_trigger_cutaway.png (+ .svg)")


if __name__ == "__main__":
    main()
