# Pre-registration C101 — the push's shape at every layer of the text encoder

Written 2026-10-18 by Claude, **before any C101 encode.** Asked by Alessandro after the C93 figure ("queste curve sarebbe
bello disegnarle per tutti i layer"). No renders: encoder only, GPU. Queued after C100.

## 1. Why

C93 drew the push of three edits (MLP of L06, L14, L28) and found one early, planar bend of 45–77°, smaller than a random
push of the same size at the same place (66–88°), with L28 bending least. Three layers out of 36 cannot say whether the
bend changes with depth, whether "the edit bends less than a random push" holds everywhere, or whether some layer has a
shape the three did not show (spiral, wave, clip). C101 draws the curve for every layer.

## 2. Design

* **Prompt:** `D1_dwarf_paladin` only (the C93 and C100 anchor). Whether the shape depends on the prompt is C100's question;
  C101 is read through C100's verdict.
* **Edits:** MLP (gate, up, down) and attention (q, k, v, o) of each layer 0–34, one at a time. Layer 35 is left out: an
  edit there reaches no tap (taps are read before layers 2, 5, …, 35). Layers 33–34 reach only the last tap.
* **Doses:** as C100 — positive 0.05 → 3.00 (C93's 18) plus 4, 5, 7, 10; negative −0.05 → −1.00 plus −1.5, −2, −3.
* **Random control** for every MLP edit at positive doses, as C93 (per-token random directions, seed 9393, lengths
  matched to the real change of that layer's MLP output).
* **Measures and shape labels exactly as C93** (`experiments/te_shapes.py`), at the whole level (12 taps, mean over
  tokens) on the full dose range and on the C93 range, plus per reachable tap.
* **Gates:** (a) elf baseline bit-identical; (b) L06 MLP 1.00 against C67, within twice the fp16 floor; (c) a zero-length
  control leaves the conditioning bit-identical; (d) where C93 has the same trajectory (L06, L14, L28 MLP and L06, L14
  attention, edit and control), the first 18 (or 12) doses match it within twice the fp16 floor in relative norm. Any
  failure stops the run.
* About 3,400 encodes, about 2.5 hours.

## 3. Rules (fixed now)

1. **Does depth order the bend?** Spearman ρ between layer and total turn θ, MLP edits, positive doses, 35 layers;
   permutation p (10,000, seed 0). *Depth orders the bend* if |ρ| ≥ 0.5 and p < 0.01 (the sign says which way; C93
   suggests deeper bends less); *no order* if |ρ| < 0.3; otherwise weak.
2. **Does the edit bend less than a random push everywhere?** Number of layers where θ(edit) < θ(control), MLP, positive.
   *Everywhere* if ≥ 28 of 35; *the opposite* if ≤ 7 of 35; otherwise *depends on the layer* (the layers are listed).
3. **New shapes (reported):** for edits and controls, the count of each shape label over the layers, and the layers where
   a spiral, wave or clip appears.
4. **Reported:** θ of MLP against attention per layer, both signs; the share of layers whose label changes when the doses
   beyond 3 (or −1) are added.

**Tool rule.** Rule 1 "depth orders the bend": the knob's curve is predictable from the layer, so one calibration per
layer band suffices. Rule 2 "everywhere": the edit's push is straighter than chance at every depth, so the structure C93
found is a property of the learned weights, not of where the push enters. A clip at some layer: that layer's knob needs
an upper bound.

## 4. Limits

One prompt; mean over tokens at the whole level; controls for MLP positive edits only; late layers (33–34) are seen through
one tap only. Descriptive above all: the figures are the main output, and the rules only keep the reading honest.

Script: `experiments/te_shapes_layers.py`. Figures: `experiments/plot_te_shapes_layers.py`.
Directive: `docs/directives_antigravity_te_shapes_layers.md`.
