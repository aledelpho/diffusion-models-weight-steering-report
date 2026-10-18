# Pre-registration C97 — fragile places: do they replicate, and what decides them (starting noise or content)? Do tiny prompt changes hit the same places?

Written 2026-10-18 by Claude, **before any C97 render.** Approved by Alessandro (2026-10-18), including the prompt
micro-changes ("highest resolution" instead of "high resolution", his example).

## 1. Why

C96 (`docs/micro_watersheds_result.md`) found, on one picture (the archer, seed 3141592), that 26 minimal weight edits
flip the same small regions (partial correlation 0.506, bar 0.30), and that one bf16 step on block 27 makes the arrow's
fletching appear. Three limits: one prompt, one seed chosen because it sits on a watershed, and nothing about what
decides the places. The fletching is also an object the prompt asks for ("an arrow nocked and its feather fletching
visible"), which favours *content* over *noise*.

## 2. Related work (checked 2026-10-18)

* De Vita and Belagiannis (arXiv:2412.00205) estimate per-pixel instability by re-noising the denoised estimate during
  sampling; unstable pixels are mostly foreground details where artefacts lie, peaking late in sampling.
* Sclocchi, Favero and Wyart (PNAS 2025; arXiv:2402.16991): in forward–backward experiments high-level content flips
  abruptly at a threshold while low-level features change smoothly.
* Li and Chen (arXiv:2403.01633) and "Blink of an eye" (arXiv:2502.00921): features are decided in narrow time windows
  of sampling.
* Prompt-to-Prompt (ref. 23 of the README) motivates attention control precisely because a word change alters the whole
  picture; Patashnik et al. (ICCV 2023) localise object-level shape variations across prompts.

None compares *which places* flip across different kinds of perturbation (weights, prompt wording) on the same seed, or
asks whether the places follow the starting noise.

## 3. Design (108 renders)

* **Prompts (2):** `P3_archerforest` (complex painted scene, the C96 prompt) and `D1_dwarf_paladin` (comic close-up
  portrait on white, simple).
* **Seeds (6):** 3141592, 2645751, 1618033, 2718281, 3316624, 4123105 (the same six for both prompts).
* **Perturbations per (prompt, seed) — 9 renders:**
  * `base` — the plain picture;
  * five weight micro-edits (Arthemy tuner, image model): `W1` block 27 +0.004 and `W2` −0.004 (one bf16 step on every
    weight), `W3` block 00 −0.010, `W4` block 10 −0.010, `W5` block 23 +0.010;
  * three prompt micro-changes, words away from the subject:
    * archer: `M1` "reflect every detail" → "reflect each detail"; `M2` "A sense of depth" → "A feeling of depth";
      `M3` "The lighting is dim and dappled" → "The lighting is low and dappled";
    * dwarf: `M1` "resolute stern expression" → "resolute, stern expression"; `M2` "simple background" → "plain
      background"; `M3` "close-up portrait" → "closeup portrait".
* **Starting noise:** the initial latent noise of each seed, reconstructed on the GPU as ComfyUI draws it
  (`torch.manual_seed(seed)`, standard normal of the latent's shape) and saved (`--noise`). The ancestral noise added at
  each step is not saved.
* **Gates:** archer `base` at 3141592 must equal the C56 baseline, dwarf `base` at 2645751 must equal the
  `benchmark_portraits/phase_c` baseline (max abs diff 0). Otherwise stop.

## 4. Measures (as C96)

Change map Δ = max over RGB of |perturbed − base|; patches of 16 × 16 pixels; patch energy E = mean Δ²; texture T = mean
Sobel magnitude of the base's luminance. "Partial correlation" = Pearson correlation of log(1 + E) after a linear
regression on log(1 + T) (on both textures where two pictures are compared).

## 5. Rules (fixed now)

1. **R1 — replication (primary).** Per (prompt, seed) cell, the median partial correlation over the 10 pairs of weight
   edits. *Replicated* if ≥ 0.30 in ≥ 9 of 12 cells; *not replicated* if ≥ 0.30 in ≤ 4; otherwise mixed. Reported per
   prompt.
2. **R2 — prompt micro-changes hit the same places (primary).** Per cell and per M, the partial correlation between the M
   map and the mean of the five W maps (log energies). *Supported* if the median over the 36 values is ≥ 0.30; *refuted*
   if ≤ 0.10. Reported: how much larger the M changes are than the W changes (mean Δ).
3. **R3 — does the starting noise set the places? (primary).** Fragility map F of a cell = mean of the five W log
   energies, residualised on its own texture. Compare F of the archer and F of the dwarf **at the same seed** (6 pairs)
   with the 30 pairs **at different seeds**, controlling both textures.
   * *Noise sets the places* if mean(same seed) − mean(different seeds) ≥ 0.15 and a one-sided Mann–Whitney test gives
     p < 0.05.
   * *Not the noise* if the difference is < 0.05.
   * Otherwise inconclusive.
4. **Reported, deciding nothing:**
   * per-patch Spearman between F and statistics of the initial noise under the patch (mean, mean absolute value,
     low-frequency energy), pooled;
   * the share of flip energy in large regions (≥ 256 px) and near strong edges;
   * the five largest flip regions of each cell, described by Claude by eye (conditions known): which objects;
   * whether the objects that flip are ones the prompt asks for.

**Tool rule.** R1: fragility is a general property of pictures, not of one watershed seed. R2: a tool that perturbs
the wording slightly can find the same fragile places as one that perturbs the weights (cheaper, no tuner). R3 noise:
fragility can be scored from the seed before rendering; content: it belongs to the objects, and the tool should warn
on weakly bound details.

## 6. Limits known in advance

Two prompts that differ in everything (composition, style, background), so R3 compares fragility maps of different
pictures drawn from the same noise; `euler_ancestral` adds seeded noise at every step, which is part of "the noise" but
not saved; the noise reconstruction follows ComfyUI's code and is not checked inside the sampler.

Script: `experiments/watersheds_origin.py`. Directive: `docs/directives_antigravity_watersheds_origin.md`.
