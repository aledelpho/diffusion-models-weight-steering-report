# C93 result — the shape of an edit's push along the dose

2026-10-18. Pre-registration `docs/prereg_te_shapes.md` and script `experiments/te_shapes.py` (a84fd67, before any
encode). Encodes by Antigravity (`docs/RENDERS_2026-10-18_te_shapes.md`): gates passed (elf baseline bit-identical;
L06 MLP at 1.00 within 0.000276 of C67, limit 0.000977); 3 characters × 5 edits × 2 signs + 9 random controls, 3744
trajectories (`data/te_shapes_trajectories.csv`), 26 minutes. Rules by `--rules` (`data/te_shapes_tests.csv`).

## Correction found after the run

The per-tap level included taps an edit cannot reach (a tap reads the stream *entering* its layer: an edit of layer 14
leaves taps 0–4 untouched). Their push is zero, the angle comes out at exactly 90°, and they were classified as
"clip + accelerating" (138 rows, all of them). Rule 2 is recomputed on reachable taps only; the uncorrected value is
kept here for the record.

## Verdicts

| rule | value | verdict |
|---|---|---|
| 1 — which shapes belong to the edits (whole encoder, MLP, positive dose; 9 edits vs 9 controls) | straight 0/0, spiral 0/0, wave 0/0, clip 0/0, accelerating 0/0, **other 9/9 vs 9/9** | none of the four shapes; "other" belongs to the network |
| 2 — the shape lives in the taps | reachable taps: per-tap shape differs from the whole in 20 of 30 (bar 2/3), early vs late majority differs in **11 of 30** (bar 1/2) | **one shape for the whole encoder** (uncorrected: 30/30 and 20/30, "lives in the taps" — wrong) |
| 3 — per token (reported) | edits: other 0.99, spiral 0.01; controls: other 0.97, spiral 0.03 (747 tokens) | — |

## What the trajectories are (whole encoder, measured)

* **One smooth arc, turning early.** The MLP edits turn by 45–77° from the smallest to the largest dose, in one
  direction (no reversals), almost in a plane (planarity 0.86–0.96), without jumps (largest step 10–19°). Almost all the
  turning happens at small push length (share of turning in the last third of the push: 0.03–0.06): the direction moves
  first and then settles. That is the opposite of an accelerating spiral, and short of the 90° the spiral rule asked.
  L28 turns least (45–47°), L14 most (76–77°).
* **Random pushes injected at the same place also bend**, by 66–88°: the bend is the network's, not the concepts'. But
  they bend less cleanly: planarity 0.77–0.90, up to two small reversals, steps up to 44°. (Reported, not a rule.)
* **The three characters give the same shape** to within a degree or two for every edit: the trajectory is a property
  of the edit and the encoder, not of the prompt — as C88 found for the push itself.
* **Negative doses** of the L06 halves turn sharply near −1, where the half is zeroed (largest steps 64–70° for the
  MLP, 80–81° for attention); two of the three L06 MLP negative trajectories pass the spiral rule, and L06 attention at
  positive doses passes it at all three characters (rotation 92°, planarity 0.82). Reported.

## Reading

Alessandro's four shapes were the right questions, and the answer is mostly no: an edit's push does not spiral, wave,
jump across or accelerate; it bends once, early, in one plane, and then goes straight. The bend is something any push
injected at that point suffers (random controls bend as much), so it says how the encoder transforms a push, not how
concepts are arranged. What distinguishes real edits from random pushes is smoothness, not shape. For the tool: a dose
picks a point on a smooth arc whose direction is set early; at small doses a knob also steers, at large doses it mostly
scales.

## Limits

Three characters; mean over tokens at the whole and tap levels; the per-tap rule was corrected after the run (reported
above); the random control is one choice among several.
