"""machine_params.py — SINGLE SOURCE OF TRUTH for the megamop assembly.

megamop = a 3D-printable graffiti "mop" paint applicator that threads onto a
common Gatorade bottle. Two printed parts:
  - base.py   : screws onto the bottle, carries the wick + mesh, has an external
                thread for the collar
  - collar.py : screws onto the base, clamps the mesh + foam/felt wick

Plus two NON-printed consumables modeled only as assembly stand-ins:
  - a ~2" stainless / Kevlar mesh disc (abrasion face)
  - a ~2" open-cell foam OR felt wick

All shared dimensions live here and are imported, never re-typed.

NOTE ON THE BOTTLE THREAD (the one risky number): the Gatorade "38 mm" finish is
reverse-engineered from community measurements (2-start, ~7.2 coarse thread). The
split between pitch-vs-lead and the exact depth are UNVERIFIED — that is exactly
what cad/coupon.py exists to test on a real bottle. Treat these as a starting
guess; update after the test coupon fits.
"""
from build123d import Location, Pos, Rot

# ---------------------------------------------------------------------------
# 1. GATORADE BOTTLE THREAD  (controlling interface — VERIFY with cad/coupon.py)
# ---------------------------------------------------------------------------
# DIAMETER follows the 38-400 standard (T = 37.19 across peaks, E = 34.80 at root; calipers
# read ~37.5). But the THREAD IS DOUBLE-START: the real bottle has TWO thread entries 180deg
# apart, each wrapping only ~180-200deg -> a 2-START thread (a sports-bottle variant on a 38mm
# neck; the published "400" is single-start, but Gatorade's actual neck is not).
# MEASURED adjacent crest-to-crest spacing along the neck = 3.0mm -> with 2 starts, LEAD = 6.0mm.
BOTTLE_THREAD_MAJOR_D = 37.19      # 38-400 "T", across the thread peaks
BOTTLE_THREAD_ROOT_D  = 34.80      # 38-400 "E", neck OD at the thread root
BOTTLE_THREAD_DEPTH   = (BOTTLE_THREAD_MAJOR_D - BOTTLE_THREAD_ROOT_D) / 2   # ~1.2mm
BOTTLE_THREAD_STARTS  = 2          # DOUBLE-start (two entries 180deg apart) — seen on the bottle
BOTTLE_THREAD_PITCH   = 3.0        # MEASURED adjacent-crest spacing -> LEAD = PITCH*STARTS = 6.0mm
BOTTLE_THREAD_LEN     = 10.0       # threaded engagement length on the neck
BOTTLE_MOUTH_ID       = 31.1       # 38-400 "I" inner diameter (the paint passage)

THREAD_CLEAR_R        = 0.35   # radial clearance, female-vs-male, for FDM fit

# ---------------------------------------------------------------------------
# 2. BASE — bottle skirt (internal Gatorade thread)
# ---------------------------------------------------------------------------
# Internal (female) thread. For the flanks to MESH, the female crest must reach radially
# INWARD to the male ROOT + clearance (NOT the male major) — otherwise the two threads sit
# in disjoint radial bands and the parts slip together without grabbing.
#   male (bottle): crest = MAJOR/2, root = MAJOR/2 - DEPTH
SKIRT_CREST_R = BOTTLE_THREAD_MAJOR_D / 2 - BOTTLE_THREAD_DEPTH + THREAD_CLEAR_R   # female crest
SKIRT_BORE_R  = SKIRT_CREST_R + BOTTLE_THREAD_DEPTH    # bore wall (female root) = MAJOR/2 + clear
SKIRT_WALL    = 3.0
SKIRT_OUTER_R = SKIRT_BORE_R + SKIRT_WALL
SKIRT_H       = BOTTLE_THREAD_LEN + 4.0   # thread length + a lead-in / stop region

# ---------------------------------------------------------------------------
# 3. TIP / WICK CHAMBER  (~2" round mop face)
# ---------------------------------------------------------------------------
WICK_D            = 50.0   # ~2" wick diameter -> chamber ID
WICK_CHAMBER_R    = WICK_D / 2
WICK_CHAMBER_H    = 16.0   # how deep the foam/felt sits in the cup
WICK_PROUD        = 4.0    # uncompressed wick stands proud of the rim (gets squished)
FEED_BORE_D       = 26.0   # paint passage from bottle into the back of the wick
FEED_RIB_W        = 3.0    # cross-rib across the feed bore: backstop so wick can't retract
FEED_RIB_T        = 2.0

CUP_WALL          = 3.0
CUP_OUTER_R       = WICK_CHAMBER_R + CUP_WALL   # 28.0  (rim top is the clamp seat)

# ---------------------------------------------------------------------------
# 4. COLLAR THREAD  (base<->collar — our own choice, made robust/printable)
# ---------------------------------------------------------------------------
CUP_THREAD_PITCH  = 3.0
CUP_THREAD_STARTS = 1
CUP_THREAD_DEPTH  = 1.5
CUP_THREAD_LEN    = 9.0
# External thread on the cup: root sits on the cup outer wall, crest stands proud.
CUP_THREAD_ROOT_R = CUP_OUTER_R                 # 28.0
CUP_THREAD_CREST_R = CUP_THREAD_ROOT_R + CUP_THREAD_DEPTH   # 29.5  (major dia 59)

# female crest reaches in to the male ROOT + clearance so the flanks mesh (see skirt note)
COLLAR_CREST_R    = CUP_THREAD_ROOT_R + THREAD_CLEAR_R      # female crest (inner)
COLLAR_BORE_R     = COLLAR_CREST_R + CUP_THREAD_DEPTH       # collar bore wall (female root)
COLLAR_WALL       = 3.0
COLLAR_OUTER_R    = COLLAR_BORE_R + COLLAR_WALL
COLLAR_LIP_T      = 3.0    # thickness of the inward clamping lip (top of collar)
COLLAR_APERTURE_D = 44.0   # opening that exposes the wick face; lip clamps the rest
COLLAR_APERTURE_R = COLLAR_APERTURE_D / 2

# ---------------------------------------------------------------------------
# 4b. ANGLED-NECK VARIANT  (base_angled.py) — cup canted off the bottle axis so
#     paint feeds the tip when the bottle is tilted toward the wall.
# ---------------------------------------------------------------------------
CANT_DEG     = 20.0                       # cup tilt off the bottle axis
NECK_OUTER_R = FEED_BORE_D / 2 + 3.0      # elbow/neck pipe outer radius (3mm wall)
NECK_STUB    = 18.0                       # cup-side neck length before the chamber
ELBOW_Z      = SKIRT_H + 8.0              # elbow pivot height on the bottle axis
ELBOW_BALL_R = NECK_OUTER_R + 1.0         # knuckle ball radius (> neck for clean weld)

# ---------------------------------------------------------------------------
# 4c. DOME CAP (dome_cap.py) — PRINTED perforated spherical dome that replaces the
#     sourced steel mesh: caps/retains the wick, bulges past the collar, and bleeds
#     paint through a grid of holes onto the wall.
# ---------------------------------------------------------------------------
DOME_RISE     = 14.0          # how far the dome apex stands above the clamp seat
DOME_T        = 2.6           # dome shell thickness (abrasion + strength)
DOME_BASE_R   = WICK_CHAMBER_R       # dome springs from the chamber/wick edge (25)
DOME_THROAT_R = WICK_CHAMBER_R - 5.0 # central opening the proud wick pokes through (20)
DOME_HOLE_D   = 3.6           # perforation hole diameter
DOME_RING_H   = 12.0          # threaded ring height (matches cup external thread)
DOME_SEAT_T   = 3.0           # flange/seat thickness (clamp face onto the cup rim)

# ---------------------------------------------------------------------------
# 4c-flex. TWO-PIECE FLEXIBLE DOME — a rigid threaded retainer (dome_ring.py, PETG)
#     that clamps a flexible perforated TPU dome (dome_tpu.py). The TPU face conforms
#     to brick/concrete instead of cracking; the rigid ring keeps a reliable thread.
#     Same Ø68 outer ring as dome_cap, so cap.py still fits over it.
# ---------------------------------------------------------------------------
DTPU_BASE_R    = 24.0     # dome springs from here (Ø48 application face, ~1.9")
DTPU_FLANGE_R  = CUP_OUTER_R         # flange OD = cup rim (28), clamped on the rim
DTPU_THROAT_R  = 19.0     # central hole the proud wick pokes through into the dome
DTPU_FLANGE_T  = 2.0      # TPU flange thickness (clamped/compressed by the ring lip)
# Print-test feedback: the dome was too stiff to flatten against a wall. A spherical shell
# resists inward load (arch action), so: thinner shell (stiffness ~ t^3), flatter dome (less
# arch), and more-open perforation lower the force to conform. TWO flex variants are kept —
# 'stiff' (original) and 'soft' (revision) — defined in dome_tpu.py VARIANTS; print both to compare.
DRING_APERTURE_R = 25.0   # rigid-ring opening the TPU dome bulges through (Ø50)
DRING_LIP_T    = 3.0      # rigid-ring clamping lip thickness

# ---------------------------------------------------------------------------
# 4d. STORAGE CAP (cap.py) — snaps over the dome cap to keep the wet wick from
#     drying / smearing. Grabs the dome-cap ring (no thread; the cup thread is taken),
#     slotted skirt detents hook under the ring's bottom edge.
# ---------------------------------------------------------------------------
CAP_CLEAR     = 0.7                          # radial slip clearance over the dome-cap ring.
# NOTE: this also sets how far the detents must flex to pass the ring (= CAP_CLEAR..CAP_CLEAR+? ).
# Detent tip lands at CAP_INNER_R - CAP_DETENT; interference over the ring OD = CAP_DETENT - CAP_CLEAR
# (1.4-0.7 = 0.7mm catch). Was 0.4 -> 1.0mm interference, which printed "too tight to go on" in PETG.
CAP_WALL      = 2.0   # thinned from 2.5: skirt flex force ~ wall^3, so 2.5->2.0 ~= half the snap force
                      # (this cap is held by snap detents, NOT threads, so a softer wall is fine here;
                      #  TPU would go further but inverts the tuning — needs MORE detent to retain)
CAP_INNER_R   = COLLAR_OUTER_R + CAP_CLEAR   # slips over the Ø68 dome-cap ring
CAP_OUTER_R   = CAP_INNER_R + CAP_WALL
CAP_DOME_CLR  = 2.5                          # axial clearance over the dome apex
CAP_RIM_BELOW = 3.0                          # cap rim sits this far below the ring bottom
CAP_CAVITY_H  = (DOME_RING_H + DOME_RISE) + CAP_RIM_BELOW + CAP_DOME_CLR
CAP_N_SNAP    = 6                            # slotted flex segments
# Friction-taper retention (replaces the snap detents): an internal LAND the dome-ring top
# rests against (positive seated stop), plus tapered WEDGE ribs on the skirt that grip the ring
# OD with friction that grows as it seats and releases gradually on pull-off (no snap threshold).
CAP_LAND_IR     = 27.0   # inner radius of the land the dome-ring TOP face rests on. Must clear the
                         # dome bulge (rigid base Ø50 / TPU base Ø48) yet overlap the ring top
                         # annulus (Ø50..Ø66) -> ~Ø54..Ø66 face contact = the axial stop.
CAP_WEDGE_INTERF = 0.5   # radial interference at the TOP (seated) end of the friction wedges;
                         # tapers to ~0 at the rim end -> continuous friction grip, not a snap bead.
CAP_DETENT    = 1.4                          # LEGACY (old snap bead); kept so older scripts import OK

# ---------------------------------------------------------------------------
# 5. CONSUMABLES (assembly stand-ins only — sourced, not printed)
# ---------------------------------------------------------------------------
# (the steel/Kevlar mesh is now the printed dome cap; kept for the old flat collar)
MESH_D = 54.0
MESH_T = 0.6

# ---------------------------------------------------------------------------
# Assembly helper: snap a part so its local mate `frm` lands on world mate `onto`.
# ---------------------------------------------------------------------------
def place(solid, frm: Location, onto: Location):
    """Snap `solid` so its local-frame mate `frm` coincides with world `onto`."""
    return (onto * frm.inverse()) * solid
