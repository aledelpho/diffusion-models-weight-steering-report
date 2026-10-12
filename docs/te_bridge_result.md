# C69 result — attention maps in the DiT under text-encoder edits

Analysis run 2026-10-12 on the 25 renders of `docs/RENDERS_2026-10-12_te_bridge.md`.
Pre-registration: `docs/prereg_te_bridge.md`. Data: `data/te_bridge_maps.csv` (cond × step × block),
`data/te_bridge_units.csv`, `data/te_bridge_style.csv`, `data/te_bridge_readings.csv`.

## Gate

The probe changed nothing: all 25 images are **pixel-identical** to the existing ones, and each render left 9
attention files (`REPRO PASS: 25`).

## Readings

| reading | value | rule | verdict |
|---|---|---|---|
| P1 order divergence gain, mean over steps and blocks | L06 MLP+ −0.0038 · L12 MLP+ +0.0595 · L10 MLP− −0.0385 · L19 attn− −0.0069 | min(strong) > max(mild) | **holds by the rule, with a margin of 0.003**; only L12 raises the divergence above the baseline |
| P2 first step where both strong edits exceed both mild ones | step 0 | ≤ 2 | **holds**, but the separation is not kept: at steps 3–6 L06 falls below L19 |
| P3 blocks with the largest gain under the strong edits | 12 (+0.073), 25, 18, 15, 16 | reported | middle blocks, plus 25 |
| P4 change of the maps vs baseline | L06 0.290 · L12 0.295 · L10 0.159 · L19 0.127 | min(strong) > max(mild) | **holds** clearly |
| P5 change in style share (baseline 0.095) | L06 −0.041 · L12 +0.026 · L10 −0.020 · L19 +0.005 | max(Δ strong) < min(Δ mild) | **does not hold** |
| P6 attention mass on all text (baseline 0.220) | L06 0.210 · L12 0.185 · L10 0.221 · L19 0.220 | reported | the strong edits lower it, L12 most |

Order divergence by step (baseline): 0.065, 0.144, 0.188, 0.223, 0.236, 0.241, 0.254, 0.258, 0.272. With the same seed
the five orders start from the same noise, so at step 0 the maps differ only because of the text; afterwards they
also follow the different images being formed.

## What this says

* **Size carries over into the DiT (P4).** The two strong edits move where the image reads each clause about twice as
  much as the mild ones. This matches C67 E1: the size of the conditioning push predicts the size of the change in
  the attention.
* **The divergence between word orders does not follow "strong vs mild" (P1, P2).** P1 holds only by a margin of
  0.003. Of the two strong edits, only L12 MLP+ makes the five orders read their clauses in more different places,
  and it does so from step 1 onward (0.177 vs 0.144 at step 1; 0.355 vs 0.272 at the end). L06 MLP+ stays at the
  level of the baseline, yet its images scored 5 like L12. So a large divergence between the five pictures can come
  without a larger divergence of the attention maps. The bridge is not, or not only, *where* the text is read.
* **The default-style reading (P5) is split between the two strong edits.** L06 MLP+ cuts the share of text attention
  that goes to the style clauses from 0.095 to 0.054, in all five orders. That fits Alessandro's hypothesis: the
  style words lose weight and other styles appear. L12 MLP+ does the opposite (0.121). Its highest share is in V2
  (0.137), the order Alessandro described as "una donna gatto animata". As preregistered, P5 does not hold.
* **L12 lowers the attention on the text as a whole (P6: 0.185 vs 0.220).** The image tokens attend more to each
  other, so the model leans more on its own prior. This could be a second route to a default style, different from
  L06's. It is not preregistered, and two edits are too few to tell routes apart.

## Limits

* One seed, one prompt family, two vs two edits; no p-values.
* After step 0, the divergence of the maps is partly a *consequence* of different images, not only a cause.
* The clauses that change most (pointed ears, eyepatch, antlers) are small, peaked regions where the cosine is
  unstable.
* Attention is not influence. L06 could change what the clauses *say* (the value vectors) without changing where
  they are read; this measurement cannot see that.
* The genre of each image (anime, comic, cartoon) has not been measured, so P5 cannot be tied to the switch image by
  image. That needs per-image genre labels or C66.
