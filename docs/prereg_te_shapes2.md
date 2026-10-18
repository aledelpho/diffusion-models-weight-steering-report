# Pre-registration C100 — the push's shape with very different prompts and much heavier edits

Written 2026-10-18 by Claude, **before any C100 encode.** Asked by Alessandro after C93 ("cosa succede con prompt molto
diversi ed edit molto più pesanti"). No renders: encoder only, GPU.

## 1. Why

C93 (`docs/te_shapes_result.md`): on three comic portraits, every MLP edit's push bends once, early, in one plane
(45–77°), then goes straight; random pushes injected at the same place bend as much, less cleanly; the three characters
gave the same shape within a degree or two. Open: is the shape a property of the edit for *any* prompt, and does anything
new happen far beyond d = 3 or past the sign flip?

## 2. Design

* **Prompts (6, chosen to differ in subject, style and length):** `D1_dwarf_paladin` (comic portrait, the C93 anchor),
  `S1_rally` (realistic photo of a rally car), `P2_lotuscanoe` (dreamlike top-down scene), `P5_comic_panels` (a comic
  page of four panels), `C4_stilllife` (cartoon still life, no person), `LN` (a single leaf, macro photo). Texts from
  the plans they were rendered with.
* **Edits (5):** MLP of L06, L14, L28 (as C93); the whole layer 6 (attention and MLP, seven matrices); and L06 + L14 + L28
  MLP together.
* **Doses:** positive — C93's 18 (0.05 → 3.00) plus 4, 5, 7, 10 (22); negative — C93's 12 (−0.05 → −1.00) plus −1.5, −2, −3
  (15; past −1 the matrices change sign).
* **Random control** for the three single-MLP edits at positive doses, as C93 (per-token random directions, seed 9393,
  lengths matched to the real change of the MLP output).
* **Gates as C93:** (a) the elf baseline bit-identical; (b) L06 MLP at 1.00 on the dwarf against the C67 encode, within
  twice the fp16 floor; (c) a zero-length control leaves each prompt's conditioning bit-identical. Any failure stops the run.
* **Measures and shape rules exactly as C93** (`experiments/te_shapes.py`: `measures`, `shapes`), at the whole level
  (12 taps concatenated, mean over tokens), plus per tap on **reachable taps only** (the C93 correction).

## 3. Rules (fixed now)

1. **Shapes of edits against controls** (whole, single-MLP edits, positive doses; 18 edit and 18 control trajectories):
   a shape *belongs to the edits* if it occurs in ≥ 10 of 18 edits and ≤ 4 of 18 controls; *to the network* if ≥ 10 of 18
   in both.
2. **Does the prompt change the shape?** For each edit × sign (10), the range of the total turn θ over the 6 prompts.
   *A property of the edit* if the range is ≤ 15° in ≥ 2/3 of them; *depends on the prompt* if ≥ 30° in ≥ 1/2;
   otherwise mixed.
3. **Heavy doses (reported):** the share of trajectories whose shape label changes when the doses beyond 3 (or beyond
   −1) are added; in particular whether a clip (one step ≥ 90°) appears.
4. **Reported:** whole layer 6 and the three-layer combination against L06 MLP alone; per-tap shapes on reachable taps.

**Tool rule.** Rule 2 "property of the edit": one curve per edit can be calibrated once and used on any prompt. "Depends
on the prompt": a dose must be calibrated per prompt. Rule 3: whether heavy doses add new behaviour or only extend the
straight part.

## 4. Limits

Six prompts, one seed-free encoder pass each (the encoder does not depend on the seed); mean over tokens at the whole
level; random controls only for single-MLP positive edits.

Script: `experiments/te_shapes2.py`. Directive: `docs/directives_antigravity_te_shapes2.md`.
