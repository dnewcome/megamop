# Concept: trigger-bottle paint applicator

A form study (not a working design) for a future direction: a **trigger-handle applicator** with
an **inverted Gatorade bottle** as the paint reservoir, where pulling a trigger meters paint out
the perforated mop dome. Reuses the real bottle + dome for context; body/grip/trigger are notional.

![hero](cad/build/concept_trigger_hero.png)
![turntable](cad/build/concept_trigger_turntable.gif)

Build it: `python3 cad/concept_trigger.py` → `cad/build/concept_trigger.glb` + render PNGs.
Renders via the `product-design` skill (Blender, `LC_ALL=C`).

## Status: interesting, NOT resolved
The form reads, but it doesn't work as-is — the full-size bottle dominates the ergonomics, and
**the mechanism is the unsolved part.** The crux: get viscous, pigmented paint to flow *on demand*
from an inverted reservoir, hand-triggered, and still be **cleanable**.

## Candidate mechanisms (for whoever picks this up)
1. **Trigger pinch-valve (simplest, most cleanable).** Paint gravity-/squeeze-feeds through a soft
   tube; the trigger pinches the tube to stop flow, releases it to let paint through. Only wetted
   moving part is the tube (cheap to clean/replace). No pump — pressure comes from gravity + a
   bottle squeeze. Effectively adds **drip control** to today's squeeze mop. Good first step.
2. **Diaphragm / piston trigger pump.** Trigger drives a piston or diaphragm in a chamber with two
   **ball check valves** (inlet from reservoir, outlet to tip) + a return spring; meters a shot per
   pull (trigger-sprayer principle). Real flow control, but internal valves clog with paint — needs
   wide bores and tool-free disassembly to clean.
3. **Pressurized reservoir + trigger shutoff.** Pre-pressurize the bottle (hand pump, or just
   squeeze), trigger is only an on/off valve. Needs sealed, pressure-holding joints (o-rings); a
   Gatorade bottle isn't pressure-rated, so low pressure only — and messy if it lets go.

**Shared gotchas:** an inverted bottle dribbles unless there's a **positive shutoff at the tip**;
viscous paint wants **wide passages + cleanable (ball) valves**; o-rings/gaskets are needed
anywhere pressure is held (printed threads alone won't seal).

**Pragmatic path:** start with #1 (a trigger pinch-valve for drip control on the existing squeeze
action) — achievable and cleanable — then graduate to #2 if you want true metered pumping. This is
`build123d-machine` territory (multi-part mechanism + mates), and a good candidate for a `kickoff`
to choose pump-vs-pressurized and a MuJoCo sim of the trigger/valve motion before CAD.
