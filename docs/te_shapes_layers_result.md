# C101 result — the push at every layer: deeper layers bend less, and only deep edits are straighter than chance

2026-10-19. Pre-registration `docs/prereg_te_shapes_layers.md` (fa87423; amendment 1 before the run). Encodes by
Antigravity (`docs/RENDERS_2026-10-18_te_shapes_layers.md`, 1 h 58 min): gates (a), (b), (c) passed; gate (d) against C93
seven of seven at relative error 0.000000. 140 trajectories, 1,460 rows. Rules by Claude: `experiments/te_shapes_layers.py
--rules` → `data/te_shapes_layers_tests.csv`. Figures `Text2Img/_te_shapes/C101_overview.png`, `C101_grid_*.png`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| **1** — depth orders the bend (MLP, positive, 35 layers) | Spearman ρ **−0.655**, permutation p 0.0002 | **depth orders the bend: deeper bends less** |
| **2** — the edit bends less than its random control | **24 of 35**; not less at layers 2, 3, 4, 8, 9, 10, 11, 14, 15, 17, 34 | **depends on the layer** |
| 3 — shapes (reported) | MLP positive: "other" (one bend) at 35 of 35 edits; controls 34 other, 1 straight (L34) | — |
| amendment 1 (reported) | two trajectories cut at d = 10 (L32 and L34 MLP, fp16 overflow) | — |

## Reported

**Total turn, MLP, positive (0.05 → 10):** from 82° (layer 11) to 35° (layer 30); the edit minus its random control is
+1° in layers 0–11 (median), −5.5° in layers 12–23, −15.9° in layers 24–34. Early edits bend like a random push of the
same size at the same place; from the middle of the encoder on, the edit is straighter than chance, and more so with
depth.

**Layer 34's control is straight (6°):** a push added at the last edited layer reaches the only tap left (35, read before
layer 35) with no layer in between, so it cannot bend; the edit still bends 44° because its push is a nonlinear function
of the dose. This shows the controls bend only through the layers that follow them, as expected.

**Attention, positive:** median 60° against 65° for the MLP; attention bends more at 8 of 35 layers.

**Attention, negative — an algebraic symmetry, not a behaviour.** Every attention trajectory past −1 gets a "clip"
(34 of 35 layers) and a median total turn of 142°. This is a property of the edit, found after the run: scaling q, k, v,
o by (1 + d) leaves attention unchanged when the factor is −1 (d = −2: q and k change sign together, and so do v and o;
Qwen3's q/k norm keeps the sign), and makes d = −3 identical to d = +1. Measured: push length at d = −2 below 1e-5 at
every attention layer; push at −3 equal to push at +1 (relative difference 0.0). The step through a zero push reads as a
≈ 90° clip. The negative attention trajectories are therefore not interpretable past −1, and rule 4's 142° is not a
result. The same symmetry acts on the attention half of C100's "whole layer 6, negative" beyond −1. The MLP has no such
symmetry (SiLU): its push at −2 is not zero.

**Doses beyond 3 / −1 change the label in 53 of 140 trajectories**, most of them the attention-negative artefact above.

## Reading

Two findings from the 35 curves. The size of the bend is ordered by depth: early edits turn the conditioning most,
late ones least. And C93's "the edit bends less than a random push" is a property of the middle and late encoder only:
in the first third an edit and a random push of the same size bend the same way, so the bend there is the network's,
not the edit's. Combined with C100 (one curve per edit, any prompt), a dose curve can be predicted from the layer, and
early-layer edits carry no direction of their own beyond what the network imposes.

## Limits

One prompt (C100: the shape varies by at most 7° over six prompts); mean over tokens; controls for MLP positive only;
layers 33–34 seen through one tap. The attention symmetry was not anticipated in the pre-registration; it is reported,
not removed.
