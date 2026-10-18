# Pre-registration C93 — the shape of an edit's push along the dose: straight, spiral, wave, clip, accelerating; whole encoder or per tap; against random pushes of the same size

Written 2026-10-18 by Claude, **before any C93 encode or computation.** Proposed by Alessandro (2026-10-18). No renders:
encoder only, GPU (Antigravity), after C97.

## 1. Why

C89 (three doses, the elf) found pushes linear at small doses and turning by about 50° at full dose, not in clean arcs.
Three doses cannot tell shapes apart. Alessandro proposed four shapes — a real spiral, a wave (one side, then the
other), a "clip" spiral (out on one side, back in on the other) and an accelerating spiral — and asked whether the
shape lives in the whole encoder or inside its blocks. A curve alone does not mean the concepts are organised along
it: any non-linear network bends a straight input. So every shape is compared with **random pushes of the same size
injected at the same layer**.

## 2. Design (no renders)

* **Prompts (3):** `D1_dwarf_paladin`, `E2_elf_rogue`, `O4_halforc_fighter` (C74/C75/C79/C87 texts).
* **Edits (5):** MLP of L06, L14, L28 and attention of L06, L14, applied with the Arthemy CLIP tuner (W × (1 + d)), as in
  every render of this report.
* **Doses:** positive 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.25, 1.50, 1.75, 2.00,
  2.50, 3.00 (18); negative the same up to 1.00 (12; −1.00 zeroes the half). 30 doses per edit and prompt.
* **Random control (MLP edits, positive doses):** in the unedited encoder, a forward hook adds to the output of the
  same MLP a random vector per token (unit directions fixed per token, seed 9393) whose length per token equals the
  length of the real edit's change of that MLP output at that dose. The control is a straight line injected at the
  same place with the same sizes; whatever bends downstream bends because of the network.
* **Captured:** the conditioning (12 taps × 2560 per token). Push p(d) = conditioning − unedited conditioning; each tap
  divided by the mean token norm of the unedited tap (as C89).
* **Gates:** (a) the unedited conditioning of the elf equals the C67 encode bit for bit; (b) L06 MLP at d = 1.00 on the
  dwarf reproduces the C67 encode (`chars/D1_dwarf_paladin_L06_mlp_p1.00.npz`, relative push within 2 × float16 floor);
  (c) the control hook at length 0 leaves the conditioning bit-identical.

## 3. Measures (per trajectory: one edit or control × prompt × sign × level)

Levels: **whole** (the 12 taps concatenated, mean over tokens), **per tap** (each of the 12 taps, mean over tokens),
**per token** (each content token, the 12 taps concatenated). With u(d) the unit direction of p(d) at the n doses:

* **Total turn** θ = angle(u(first), u(last)).
* **Planarity** P = share of the energy of the u(d) in their first two principal directions (uncentred: directions
  live on the sphere around the origin).
* **Rotation in the plane:** polar angle φ(d) of u(d) in that plane (unwrapped); **reversals** = sign changes of the
  increments of φ larger than 2° in size; **swing** = the smallest excursion between two reversals.
* **Largest step:** the largest angle between u at two consecutive doses.
* **Acceleration:** turning between consecutive doses, assigned to the length of the push |p| at that step (not to the
  dose, which would make any MLP edit "accelerate", nor to the path length, which rotation itself lengthens); A = share
  of the total turning that happens in the top third of the range of |p|.

## 4. Shapes (fixed now; a trajectory can have more than one)

*Measures of section 3 and the clip rule corrected after the synthetic selftest, before any encode: rotation was
measured around the centroid (inflating it), a steady spiral past 120° counted as a clip, and acceleration measured
against path length hid late turning.*

| shape | rule |
|---|---|
| straight | θ < 20° |
| spiral (steady rotation) | θ ≥ 20°, P ≥ 0.80, reversals ≤ 1, total rotation |φ(last) − φ(first)| ≥ 90°, largest step < 90° |
| wave | reversals ≥ 2, each swing ≥ 10° |
| clip (out on one side, back in on the other) | largest step ≥ 90°: the direction jumps across in one dose step |
| accelerating | θ ≥ 20° and A ≥ 0.60 (0.33 = even turning) |
| other | θ ≥ 20° and none of the above |

## 5. Decision rules

1. **A shape belongs to the edits, not to the network,** if at the whole level (positive sign, MLP edits, 9
   trajectories) it occurs in ≥ 5 of 9 edit trajectories and in ≤ 2 of the 9 matching controls. **It belongs to the
   network** if it occurs in ≥ 5 of 9 in both. Reported for every shape.
2. **The shape lives in the taps, not in the whole,** if, over the edit trajectories (all edits, both signs, 30), in
   ≥ 2/3 the per-tap shapes are not all the same as the whole-level shape **and** the early taps (2–8) and the late taps
   (9–11) have different majority shapes in ≥ 1/2. Otherwise: one shape for the whole encoder.
3. **Per token (reported):** the share of content tokens with each shape, edits against controls.

**Tool rule.** Straight: a knob is calibrated by push length. A shape the controls do not share: the concepts are
organised along it, and a knob must follow the curve (and, for a clip, needs an upper bound). A shape the controls
share: the bend belongs to the network and says nothing about how concepts are organised.

## 6. Limits known in advance

Three prompts; the mean over tokens can hide turns that the per-token level shows; controls only for MLP edits and
positive doses; random directions per token are one choice of control among several; float32 on GPU, bf16 weights.

Script: `experiments/te_shapes.py`. Directive: `docs/directives_antigravity_te_shapes.md`.
