# C97 result — fragile places replicate, prompt micro-changes hit them, and the starting noise does not set them

2026-10-18. Pre-registration `docs/prereg_watersheds_origin.md` (3d6c0ec, before any render; amendment 1 after C98,
before this analysis). Renders by Antigravity (`docs/RENDERS_2026-10-18_watersheds_origin.md`): 108 of 108; gates 7 of 7
pixel-identical (both bases; the archer's five weight edits at 3141592 against C55/C56), re-checked by Claude. Initial
noise `data/watersheds_origin_noise.npz`. Analysis `experiments/watersheds_origin.py --analyze`: outputs
`data/watersheds_origin_cells.csv`, `data/watersheds_origin_tests.csv`; overlay `Text2Img/_micro_watersheds/origin_overlay.jpg`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| **R1** — the five weight micro-edits flip the same places (per prompt × seed) | median partial r ≥ 0.30 in **12 of 12** cells (0.35–0.64; archer 6/6, dwarf 6/6) | **replicated** |
| **R2** — three prompt micro-changes ("every" → "each", a comma, "simple" → "plain"…) hit the same places as the weight edits | median partial r **0.488** over 36 | **supported** |
| **R3** — at the same seed, archer and dwarf are fragile in the same places | same seed +0.067, different seeds +0.085, difference −0.018, p 0.84 | **not the noise** |
| amendment 1 — R1, R2 with the one-pixel jitter control (reported) | 12 of 12; 0.488 | unchanged |
| R4 — fragility against the starting noise under each patch (reported) | Spearman −0.000, −0.002, −0.022 (mean, mean absolute, low-frequency energy) | no relation |

The prompt micro-changes move the picture more than the weight micro-edits (median mean Δ 12.3 against 5.3 of 255) but
in the same places.

## What flips (looked at, Claude, conditions known; overlay: red weight edits, blue prompt changes, magenta both)

* **Archer, every seed:** the arrow and its fletching, the bow, the bowstring, the drawing hand and bracer, the quiver
  feathers, the hood edge, the tips of the fir branches. The arrow and fletching flip at all six seeds — an object the
  prompt asks for ("an arrow nocked and its feather fletching visible").
* **Dwarf, every seed:** the reflections on the polished steel gorget ("polished steel gorget" is in the prompt), the
  outline of the braids and hair, the eyebrows. Prompt micro-changes touch the face more broadly.

## Reading

C96 was not a property of one watershed seed: on two very different prompts and six seeds, minimal changes of the
weights flip the same places, and minimal changes of the wording flip them too. Where those places are is not set by
the starting noise at fixed pixel positions (R3, R4): it follows the content — the same objects are fragile whatever the
seed, and they are details the prompt asks for and the model renders with little margin (an arrow's fletching, reflections
on polished steel, thin hair and braid outlines).

## Limits

Two prompts; the ancestral noise added at each sampling step is not saved, so "not the noise" means not the *starting*
noise at fixed positions; the noise reconstruction follows ComfyUI's code and was not checked inside the sampler; the
object readings are Claude's, not blind; R2 compares micro-changes that move the picture about twice as much.
