# Pre-registration TEP2 — does the L06 edit do its damage through the massive activations?

Written 2026-10-18 by Claude, **before any TEP2 encode or render.** Approved by Alessandro the same day ("procedi facendo
TEP2 e prepara la direttiva per i render").

## 1. Why

The 36-layer probe (TEP, `data/te_residual_probe_summary.csv`): the MLP of layer 6 of Qwen3-VL-4B takes the residual
stream's size from about 400 to about 13,100 (33.8 times what it receives); layers 7–33 then write 1–8% each. This is the
signature of *massive activations* (Sun et al. 2024): a few entries of the stream, orders of magnitude larger than the
rest, that later layers use as fixed biases and attention sinks. L06 MLP doubled is the edit that turns portraits into
photographs and costs the most traits (C73–C75); C87 found its damage built across many taps, with no single tap. If
the edit works by disturbing the massive entries, restoring them should remove most of the damage. In the conditioning
itself (after the taps) the two large channels (0 and 4) carry only 3–11% of L06's push (`data/te_massive_channels.csv`),
so the test has to act inside the encoder.

## 2. Design

* **Characters (3):** D1 dwarf paladin, E2 elf rogue, O4 half-orc fighter (C74–C87 texts). **Seeds (2):** 2645751,
  3316624. **Edit:** L06 MLP × 2 (`layers.6.mlp.{gate,up,down}_proj.weight` at +1.00), with the Arthemy CLIP tuner.
* **Massive entries M** (per character, fixed from the encodes): positions (token, channel) of the residual stream at
  the output of layer 6 where |h| ≥ 100 **and** |h| ≥ 100 × median |h|, in the plain encoder **or** in the edited one
  (union). All tokens of the encoder's sequence count, including the template prefix, which later layers attend to.
* **Conditions** (forward hook on layer 6's output, values copied in place — never rebuilt by adding a difference,
  pitfall 92):
  * `C1 full` — the edited encoder, untouched;
  * `C2 restore` — the edited encoder with h[M] set to the plain values;
  * `C3 only` — the plain encoder with h[M] set to the edited values;
  * `C4 control` — the edited encoder with |M| entries outside M, chosen at random (seed 4242), set to the plain values.
* **Renders:** each conditioning is saved as a tensor and fed to the image model with the conditioning node's new
  variant `file` (it replaces the conditioning with the saved one, untouched). 3 characters × 2 seeds × 4 conditions =
  24 renders, plus the plain gate render: 25 (the dwarf's `C1` at 2645751 is itself gate (c)).
* **Gates:** (a) encoder: a no-op hook leaves the plain conditioning bit-identical; (b) render: the saved plain
  conditioning of the dwarf at 2645751 reproduces the `benchmark_portraits/phase_c` baseline pixel for pixel; (c) render:
  the saved `C1` of the dwarf at 2645751 reproduces `benchmark_te_characters/D1_dwarf_paladin_L06_mlp_p1.00` pixel for
  pixel. After the main block, all six `C1` renders must equal their `benchmark_te_characters` counterparts.

### Amendment 1 (2026-10-18, after the two gate renders, before any main render or any distance was computed)

Gate (b) passed (max abs diff 0). Gate (c) failed: the dwarf's `C1` at 2645751, rendered from the saved tensor, differs
from the in-graph `benchmark_te_characters` render by max abs diff 146 per channel, mean 1.91 out of 255, with 2.4% of
pixels differing by more than 16; the two images are the same picture by eye, and both lie at mean pixel distance 59.03
from the plain render. The plain conditioning goes through the same save-and-load route bit-identically, so the
difference is in the edited encode: the script's edited encoder and the in-graph tuner do not produce bit-identical
tensors (cause not yet located; a numeric-precision difference of the patched weights is the likely candidate).
Antigravity stopped as instructed. Approved by Alessandro:

* Gate (c), and the check of the six `C1` renders after the main block, become a tolerance: the file-route `C1` must lie
  at the same mean pixel distance from the same-seed plain render as the in-graph render, within 5% (relative). The max
  and mean pixel differences are still printed and reported.
* Nothing else changes. All f(X) were already defined against the file-route `C1` (`benchmark_te_massive`), so every
  condition shares the same route and the ratios stay internally consistent.
* Limit added: the saved `C1` is not bit-identical to the conditioning of earlier L06 renders; C87's validation of
  DINOv2 on this edit refers to the in-graph renders.

## 3. Measures

Image side (primary): DINOv2-large distance to the same-seed plain render, validated against Alessandro's blind trait
loss on these portraits and this edit in C87 (Spearman 0.878). f(X) = D(X) / D(C1) per character × seed (6 cells).
Encoder side (reported): |M|; the share of the full push norm per tap reproduced by C2, C3, C4; cosines with C1's push.

## 4. Rules (fixed now)

1. **The massive entries carry the damage:** f(C2) ≤ 0.50 in ≥ 5 of 6 cells, **and** f(C4) ≥ 0.80 in ≥ 5 of 6 (restoring
   as many ordinary entries does little), **and** median f(C3) ≥ 0.50 (the massive change alone does much of it).
2. **Not through the massive entries:** f(C2) ≥ 0.80 in ≥ 5 of 6 cells.
3. **Partly:** otherwise; reported with the numbers.

**Tool rule.** Rule 1: the layers that create massive activations are the ones a style tool must leave alone, a rule
that can be checked on any LLM text encoder (Anima uses Qwen3 0.6B). Rule 2: L06's destructiveness has another cause,
and "avoid early MLPs" stays an empirical map.

## 5. Limits

One edit, three characters, two seeds; the threshold for "massive" follows Sun et al. but is a choice; restoring M also
restores whatever else those entries carry.

Scripts: `experiments/te_massive.py`; node: `tools/comfyui_krea2_condpush/__init__.py` (variant `file`). Directive:
`docs/directives_antigravity_te_massive.md`.
