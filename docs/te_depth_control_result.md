# C102 result — at the same conditioning push, deep edits barely move the picture; the depth-gives-direction claim is not supported

2026-10-19. Pre-registration `docs/prereg_te_depth_control.md` (b325447). Encodes and 156 renders by Antigravity
(`docs/RENDERS_2026-10-19_te_depth_control.md`): every push target reached within 1%; gates 3 of 3 pixel-identical.
Data committed as delivered (51b0552); blind page and key written after the renders, before any label or rule (f6ba410);
Alessandro's labels committed as downloaded (1613ce3; 54 units, U19 left unanswered). Rules by Claude:
`experiments/te_depth_control.py --rules` → `data/te_depth_control_tests.csv`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| **1** — Δκ (edit − its random control), computed | L26 ≥ 0.10 in **4 of 8** cells; L09 < 0.10 in 5 of 8 | **mixed** |
| **2** — blind: (s(L26) − s(R26)) − (s(L09) − s(R09)) | **−0.04** (means: L04 0.69, L09 0.62, R09 0.71, L26 0.25, L30 0.00, R26 0.38) | **the eye does not separate them** |
| combined | — | **not supported** |
| blind test–retest (reported) | 5 of 6 identical | — |

## The finding that dominates: equal push in the conditioning is not equal change in the picture

* **At the same τ, the deep edits move the picture far less** (reported rule 3): deep (mean of L26, L30) moves less than
  early (L04, L09) in **23 of 24** prompt × seed × level cells. Median DINOv2 distance to the plain render at τ₂ (the push
  of L06 at d = 1): L04 0.53, L09 0.34, random at L09 0.46; L26 0.06, L30 0.04, random at L26 0.05.
* **Looked at** (Claude, conditions known; sheet `Text2Img/_te_shapes/C102_sheet_t2.jpg`): at τ₂, L04 breaks the
  pictures into glitch patterns; L09 changes content (the teapot becomes a cup, the paladin loses the armour); the random
  push at L09 changes as much (a realistic painted woman, a glitched kitchen, a horned demon instead of the dragon); L26,
  L30 and the random push at L26 leave the pictures almost as they were.
* The deep layers reached the targets with *smaller* doses (L26 ≈ 0.40 and 0.80, L30 ≈ 0.35 and 0.70) than L06: they
  change the conditioning a lot (in the late taps) and the image model responds little to that change.

## Reading

The pre-registered question cannot be answered fairly at these levels: the deep conditions moved the pictures so little
that direction was not judgeable. Alessandro's notes say so for most deep units ("cambia troppo poco per poterlo dire");
the "no" answers mix "different directions" and "nothing visible", a flaw of the question (no "not visible" option).
What the data do show:

1. **Early layers: the network imposes a direction.** A random push at L09 changes the three seeds the same way as often
   as the edit does (blind 0.71 against 0.62; κ high for both at τ₂): the picture-level counterpart of C101, where early
   edits bend like a random push. Early-layer change is consistent, but it is not the edit's.
2. **Deep layers: large changes in the conditioning, small changes in the picture.** The image model is much less
   sensitive to what the late text-encoder layers change, at least at these amplitudes.

C101's "deep edits are straighter than chance" remains a property of the conditioning; whether it carries into the
picture needs deep edits that move the picture visibly.

## Tool rule

Conditioning push is not a common currency across layers: a dose must be calibrated on the picture, not on τ. Early
layers act as strong, network-shaped moves (or breakage); deep layers are gentle at equal push.

## Limits

Three seeds per cell; two layers per band; matching on τ (full tensor) was a design choice that turned out to equalise
the wrong quantity; the blind question had no "not visible" option. **Exploratory, not pre-registered:** counting only
units where Alessandro saw a change (dropping notes that say "too little / not visible") would leave 2–3 deep units, too
few to compute rule 2.
