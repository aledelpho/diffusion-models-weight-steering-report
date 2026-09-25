# Claim map — from "this preset" to "this instrument"

- **Written:** 2026-09-25, while the atlas Phase 1 render queue stood at 52 %.
- **Purpose:** decide, for each of the notebook's 43 claims, where it belongs in a report about
  the **tuner** rather than about one preset, and whether it can move as it stands.
- **Machine-readable form:** `data/claim_map.csv`, written by `experiments/build_claim_map.py`,
  which reads every page and status from `notebook/` and aborts if a claim is unclassified or a
  classification names a claim the notebook does not contain. **This document edits no page.**

---

## 0. The rule this whole exercise runs under

> **A claim may change chapter. It may not change its statement without re-running its script.**

Repointing 43 claims at a new question is the industrial-scale version of the error already in
this project's own log as pitfall 50: a difference measured between treatment and control,
written up as a property of the treatment — arithmetically true, causally backwards. If a new
sentence does not fall out of the data file that already exists, it is not a move. It is a new
claim and it needs its own pre-registration.

## 1. The inventory, corrected

An earlier count of these statuses was wrong. Each page carries a page-level `status:` in its
front matter, which a naive scan absorbs as if it were a claim's, shifting every row by one.
`build_claim_map.py` parses per claim block. The true distribution:

| status | n |
|---|---|
| `holds` | **15** |
| `open` | **18** |
| `ambiguous` | **6** |
| `overturned` | **4** |
| total | 43 |

| page | holds | open | ambiguous | overturned |
|---|---|---|---|---|
| 00 the-bench | 5 | 1 | – | – |
| 01 mark-style | – | **7** | – | – |
| 02 attribute-emergence | – | 2 | 2 | – |
| 03 what-ends-up | 2 | 1 | – | – |
| 04 where-in-the-model | – | 2 | 1 | – |
| 05 knob-or-cost | 3 | – | – | 2 |
| 06 hatching-axis | 1 | – | 1 | 1 |
| 07 chromatic | 1 | 1 | 1 | – |
| 08 block1-vs-block6 | 2 | – | 1 | – |
| 09 style-direction | 1 | 1 | – | 1 |
| 10 all-blocks-clean | – | 3 | – | – |

## 2. Why the reframing is legitimate, stated as a number and not as a preference

| chapter | claims | `holds` | share |
|---|---|---|---|
| **C1 — what the instrument does** | 7 | 5 | **71 %** |
| **C2 — what is safe to touch** | 15 | 6 | **40 %** |
| **C3 — what the instrument can produce** | 20 | 4 | **20 %** |
| M — method appendix | 1 | 0 | – |

**Eleven of the fifteen surviving claims sit in C1 and C2** — the bench and the sensitivity map,
that is, the instrument and its safety envelope. The page that carried the old framing,
`01-mark-style`, is **0 of 7**.

This is the whole argument for the rewrite, and it is not a rescue narrative: the new spine puts
its weight on the evidence that already survived, and leaves the weakest pages where they are —
open. It also sets the honest expectation for C3: the chapter the observer most wants is the
chapter with the least support, and it is the one the atlas has to earn.

## 3. C1 — What the instrument does (7 claims, 5 hold)

`node-is-identity-at-zero`, `deterministic-across-sessions`, `roundtrip-does-not-return`,
`cliplult-is-a-dead-arm`, `noise-floor-measured`, `an-edit-is-a-direction` move as they stand.

This chapter is already written; it simply lives under a title that does not announce it. Note
two entries an instrument report must treat differently from a notebook:

- `roundtrip-does-not-return` is an **operating limit**, not a curiosity: the weights return to
  D = 0 and the image does not, by a mean of 16 of 255. The tool has no image-level undo, and
  that belongs in its documentation.
- `cliplult-is-a-dead-arm` is a **defect**: one control is exactly inert at every dose while its
  sibling runs 23.5 to 34.0. A report about a tool lists its dead controls.

`two-arms-undiagnosed` (**open**) is the only re-derivation here, and it is the cheapest item in
this document: one run that prints the patch count says whether two further arms are architecture
or a delivery bug. In a preset-centred notebook that is a footnote. In an instrument report it is
an undiagnosed fault in the product.

## 4. C2 — What is safe to touch (15 claims, 6 hold)

This is the observer's stated purpose for the atlas — *what is dangerous to touch and what can be
pushed harder* — and it already exists in pieces.

**Moves as it stands (12).** `cost-grows-with-depth` (23 of 28 blocks below 1, r = −0.659),
`first-block-is-an-inverted-knob`, `tail-is-rectified` (9.1× asymmetry on block 26),
`blocks-separate-by-direction-not-distance`, `block1-coheres-at-matched-displacement`,
`block1-does-not-replicate`, `response-grows-monotonically-with-angle`,
`specialization-disagrees-with-separability`, `output-lead-survives-dose-normalisation`, and the
two falsifications `mirror-response-is-the-rule` and `extremes-are-violent-both-ways`.

Two entries change meaning when the chapter changes, and both changes are legitimate because the
statement does not move:

- The **falsifications are operating information**. That 17 of 28 blocks are mirror-symmetric
  within 3σ was a failed prediction; for someone deciding which control to turn, it is the map.
- `double-dose-arm-is-degraded` is **reclassified from page 09 to this chapter**. It is the only
  measured ceiling the project has on how hard the tool can be pushed: at double amplitude, 18
  cells of 24 fall outside a quality gate frozen before any feature was extracted, the worst at
  z = 131.7. Under the old framing it was an embarrassment about one arm. Here it is the first
  point on the safety curve.

**Needs re-derivation (3).** `position-beats-displacement` (exploratory, one seed per cell, one
unsigned metric), `blocks-point-in-different-directions` (the family of comparisons was never
declared and the result sits exactly on the boundary that declaration would have decided), and
`position-function-or-proximity`. The last is worth naming precisely: the atlas crosses
**early/late with attention/mlp**, which puts two different functions at one depth, so for the
first time the design can separate *what a block does* from *how little network remains
downstream of it*. That claim has been open since it was written; the instrument that closes it
is already rendering.

## 5. C3 — What the instrument can produce (20 claims, 4 hold)

The chapter that has to be earned. Four hold: `subject-enlargement-replicates` (pre-registered,
geometric mean ratio 1.234 on ten styles that did not exist when the prediction was frozen),
`hatching-axis-holds-under-derangement` (16 fresh prompts, 79 pairs of 80, at the exact
permutation floor), `edits-move-colour-in-different-directions` (twice on its Monte Carlo floor,
on independent corpora), and `blinding-is-a-measurement-and-it-failed`.

The first three are the only **named, replicated, useful effects** the project owns. If the hunt
for resonances needs a starting point, it is those three and not a new search.

**Seven need re-derivation**, and the reasons are specific:

| claim | what is actually missing |
|---|---|
| `tiny-payload-shifts-mark-style` | says 53 KB; the file is **50 026 bytes and 1 059 scalars**. Restate as a payload claim. |
| `mark-style-generalises` | no generalisation criterion was ever frozen, and the 2026-09-25 numbers bound it: transfer 0.38–0.47 inside a style domain, **0.05 across**. |
| `preset-is-a-sharp-operator` | the most preset-centred sentence in the notebook; the instrument version is about what *a* preset of the tuner does. |
| `permutation-adds-a-neglected-attribute` | exploratory, no threshold fixed in advance. |
| `edit-adds-and-removes-unasked-traits` | the confirmation could not resolve: 9 of its 10 prompts never light a headlight in **any** condition. The corpus failed, not the effect. |
| `attribute-emergence-generality-untested` | the pre-registered table was never filled; the primary test exists on paper only. |
| `enlargement-structure-or-magnitude` | the sign-scrambled arm at the identical displacement was never rendered, so no point on the magnitude axis exists. |
| `blinding-is-a-measurement-and-it-failed` | see §7. |

**Read this row carefully:** *trait combinations* — the property the observer lists as already
established — is `02-attribute-emergence`, and that page is **0 of 4**, two ambiguous and two
open, with its designed test never run. It belongs in the objectives, not in the premises.

## 6. The gaps, named as experiments

1. **Style capacity.** How many mutually distinguishable presets the tuner produces at one
   displacement. The atlas Phase 1 is the instrument. Pre-register **before the renders land**.
2. **The patch-count run.** Closes `two-arms-undiagnosed`. One run.
3. **The missing visual check** of `hatching-axis-preset-runs-the-other-way`. The
   pre-registration made that row conditional on a visual check of one pair, recorded before the
   analysis; no outcome exists. One check, not a corpus.
4. **The magnitude control for enlargement.** A sign-scrambled arm at D = 0.0538 on the ten
   styles: 10 × 5 = 50 renders.
5. **The crossed domain design.** 4 comics prompts + 4 style prompts, `baseline`/`preset_pos`/
   `rand_pos`/`blockshuf_neg`, five seeds, **one queue** = 160 renders. Closes both
   `shared-scene-is-not-separated-from-style` and the provisional result of
   `docs/prereg_domain_specificity.md`.
6. **Trait combinations.** The factorial with a control matched on tensor count — the design
   sketched as "Block K" and deferred. Nothing in C3 will carry the observer's third premise
   until it runs.

## 7. Two relabelling traps, written down before they are stepped in

**Trap 1 — one dataset, two claims.** The 17/20 of the four-way forced choice supports
*"hashed filenames do not blind an expert observer"* and would support *"the style the tuner
produces is perceivable"*. These are different claims. The frozen bar was **5 joint hits in 20**,
chosen to detect a blinding failure; a perceptibility claim needs its own statement, its own bar,
and the disclosure that the test ran at **double** amplitude, on a lineup that **included the
untouched baseline**. The number passes either way. The claim still has to be re-registered.

**Trap 2 — two results that sound alike.** `style-does-not-steer-direction` (overturned) says
the *declared style* does not steer the direction an edit imprints. The 2026-09-25 domain
result says the direction does not *transfer* between style domains. One is about steering, one
about transfer; they were measured on different corpora under different pre-registrations.
Merging them into a single sentence would be the neatest error available in this rewrite.

## 8. Order of work

1. This map (done), and the capacity pre-registration **before Phase 1 lands**.
2. The three one-run items: patch count, the missing visual check, the enlargement control.
3. Rewrite C1 and C2, which are 18 of 22 claims already in hand.
4. Leave C3 open until the atlas says what the capacity is. It is the chapter that decides
   whether the product claim is a number or a hope, and it is the one chapter that must not be
   written first.
