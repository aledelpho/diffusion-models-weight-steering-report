# Amendment 02 to `docs/prereg_style_capacity.md` — one region never happened

- **Written:** 2026-09-25, after the first run and **before** the re-run it specifies.
- **Nature:** a validity exclusion with an objective criterion, not a selection on outcome.

---

## 1. The finding

The observer, having seen only the first prompt family, stated that two presets looked the same
(`docs/observer_predictions_atlas_phase1.md` §5, prediction G, recorded before any distance
existed) and then named them: **`modulation_norm` draw 1 and draw 2**.

Measured:

- Their pairwise distance is **exactly 0.000000 on all eight prompts**, rank **1 of 325** in every
  one of them.
- Their displacement from the baseline is **exactly zero in all 23 features**, on every prompt and
  every seed.
- Their renders are **bit-identical to the baseline in pixels**: maximum channel difference **0**,
  0.00 % of pixels different. The PNG files differ from the baseline only by 246 bytes of embedded
  metadata.

`modulation_norm` does not produce a style. It produces the baseline.

## 2. Why, as far as the data can say

The preset files are well formed. Both draws carry 84 non-zero model patches, all of them on
`blocks.N.mod.lin`, `blocks.N.prenorm.scale`, `blocks.N.postnorm.scale`, all 84 keys present in
`Arthemy_Bench_Base.json`, and `data/perturbation_atlas_calibration.csv` records them at
`d_total_measured = 273.02631162314486`, matching the anchor to twelve digits, `status PASS`.

So the measurement path counts these tensors and the render path does not move them.

**`modulation_norm` is the only one of the thirteen regions whose keys are 100 % non-`.weight`,
and it is the only one that is inert.** The shares, from the preset files:

| region | non-`.weight` share of its non-zero model keys |
|---|---|
| `modulation_norm` | **100 %** (28 `mod.lin`, 28 `prenorm.scale`, 28 `postnorm.scale`) |
| `model_only`, `uniform_all` | 38.6 % |
| `txtfusion` | 32.7 % |
| the four `*_attn` regions | 28.6 % (`qnorm.scale`, `knorm.scale`) |
| the four `*_mlp` regions | **0 %** |

The hypothesis this suggests — that the tuner applies patches only to tensors whose name ends in
`.weight` — is **not established here**. It is the simplest account of a region that is 100 %
non-`.weight` being the one that does nothing, and it is stated as a hypothesis with a decisive
test in §4.

**A caution against over-reading it.** The table counts *tensors*, not displacement. Scale and
modulation tensors are small: reaching the anchor using only them required a multiplier
`model_alpha = 0.9365`, against 0.12–0.23 for the other regions, i.e. their combined Frobenius
mass is about 291 against 1646 for `early_attn`. So for the `*_attn` regions the share of
*displacement* sitting on inert tensors is probably far below 28.6 %. The tensor-count share is an
upper bound on the confound, not an estimate of it.

## 3. The exclusion, and its criterion

> A preset whose displacement is **exactly zero in every feature, on every prompt and every
> seed** did not happen. It is removed from the capacity analysis and reported as an instrument
> defect.

This is the same category as `cliplult-is-a-dead-arm` on page 00 of the notebook: an arm that is
exactly inert. It is not a style the tuner makes, and counting it as one would inflate every
indistinguishability statistic with two rows that are the baseline.

The criterion is mechanical and leaves no discretion: exact zero, all features, all cells.
`modulation_norm_draw1` and `modulation_norm_draw2` meet it; no other preset does.

After exclusion: **24 presets, 12 regions, 276 pairs, 12 within-region pairs.** Everything else —
the scale, the null, τ, K_common with its 5-of-8 majority, Q1, Q2, the leave-one-prompt-out
identification — is unchanged and re-run as frozen.

Both the 26-preset and the 24-preset results are reported. The 26-preset run stays on the record
in git; it is not deleted.

## 4. What must be run on the tuner, not on the renders

One run settles the mechanism and this study cannot do it, because it needs the model weights:

- apply `Arthemy_Atlas_modulation_norm_draw1.json` and **print how many tensors the patcher
  actually touched**, against the 84 the preset declares;
- if the answer is 0, the apply path filters these keys out and the measurement path does not —
  two code paths disagreeing, which is a bug in the instrument and bears on every displacement
  this project has published, since `Arthemy_Bench_Base.json` itself carries `mod.lin`,
  `prenorm.scale` and `postnorm.scale` entries among its 430;
- if the answer is 84, the tensors are moved and the forward pass is insensitive to them, which
  is a fact about the architecture and belongs in the sensitivity map.

Until that run exists, the atlas's own claim that its thirteen conditions sit at one displacement
is true of the **weights as measured** and unverified for the **weights as applied**.
