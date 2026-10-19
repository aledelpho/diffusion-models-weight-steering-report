# C103 result — random edits: the computed measure and the blind eye disagree on "own direction or the network's"

2026-10-19. Pre-registration `docs/prereg_te_depth_control2.md` (5699b70, rewritten before anything ran after Alessandro's
objection). Renders by Antigravity (`docs/RENDERS_2026-10-19_te_depth_control2.md`): 132 calibration + 96 test renders,
gate 12 of 12 pixel-identical to C102; data and blind key committed as delivered (3fd8bcf); labels committed as
downloaded (7b2aec1; 55 units). Rules by Claude: `experiments/te_depth_control2.py --rules` → `data/te_depth_control2_tests.csv`.

**Unreachable:** on the comic page (`P5_comic_panels`), L09 and the three random pushes at L09 never reached D = 0.30 on
the calibration ladder: that prompt has no layer-9 conditions.

## Verdicts

| rule | layer 9 | layer 26 |
|---|---|---|
| 0 — match (realized median D, target 0.30, floor 0.15) | L09 0.35; R09a **0.13 not matched**, R09b 0.21, R09c 0.17 | L26 0.38; R26a 0.32, b 0.25, c 0.36 |
| **1** — a fixed random push changes the seeds the same way (Alessandro) | κ ≥ 0.30 in 4 of 6 (median 0.36); blind *stesso* **0.86** (n 7) → **disagreement** (blind yes, computed short of 75%) | κ ≥ 0.30 in 10 of 12 (median 0.55); blind *stesso* 0.55 (n 11) → **disagreement** (computed yes, blind short of 0.60) |
| **2** — own direction or the network's | ρ 0.58 / κ 0.36 → r 1.61 *network*; blind B *stesso* **0.22** (n 9) *own* → **disagreement** | ρ 0.48 / κ 0.55 → r 0.87 *network*; blind B *stesso* **0.00** (n 11) *own* → **disagreement** |
| 3 — depth | same answers at both layers | |

Reported: blind test–retest 6 of 6 identical; *non si vede* in 5 units of 55. Edit L09: κ 0.77 (its random pushes 0.36),
ε 0.50; edit L26: κ 0.53 (random 0.55), ε 0.30.

## What the pictures show (looked at, Claude, conditions known; sheet `Text2Img/_te_shapes/C103_sheet.jpg`)

* **Layer 26, three different random pushes, same seed:** the paladin becomes, three times, an older, more realistic woman
  with darker hair and the same gorget; the teapot becomes, three times, a vintage enamel kettle with a wooden or black
  handle, in a photographic rendering. The **content** of the change is strikingly the same across the three random
  directions; colour, rendering (photo or painted) and details differ.
* **Layer 26, the real edit:** goes elsewhere — a chibi, elf-eared paladin, a teapot with a figurine on it.
* **Layer 9:** the random pushes change less and in more varied ways (a kitchen behind the still life in one, almost
  nothing in another).

Alessandro's notes on the B units say the same in words: "ignoring style, they follow the direction" (V07, V09, V14),
"the car model changes coherently, the colours change a lot" (V20), "Teiera antica, fotorealismo" (V12, answered
*diversi*). His *in modi diversi* weighed rendering and colour; DINOv2, a content-oriented embedding, weighs content.

## Reading

The pre-registered rules end in disagreement at both layers, and they are reported as such. The pictures and the notes
suggest why: **different random pushes at the same layer share the content of the change (the network's direction), and
differ in how it is rendered.** At layer 26 the shared content is clear (realism, age, "vintage kettle"); the real L26
edit does not follow it. On Alessandro's hypothesis (rule 1): a fixed random push does change the seeds consistently in
most cases (blind 0.86 at layer 9, κ 0.55 at layer 26), with the two measures each falling short at one layer.

## Exploratory (not pre-registered)

Removing from each Δ its component along the plain picture's embedding (14% of |Δ|² in median) leaves r at 0.80 (layer 9)
and 0.78 (layer 26): the computed "network" reading is not an artefact of a shared "away from the original" direction.

## Limits

One target strength; three random directions per layer; R09a under-matched; DINOv2 is content-oriented and the eye also
weighed style, so the two measures did not ask exactly the same question. A follow-up would split the blind question in
two (content and style) and add a style embedding (CSD, already in `metric_validation.py`) next to DINOv2.
