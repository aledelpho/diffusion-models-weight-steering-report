# Pre-registration — does a declared colour move more, or less?

**Deposited**: 2026-09-27, **before the statistic below was computed.**
**Material**: `data/style_features.csv`, already in the repository. **No render, no new extraction.**
**Origin**: Alessandro's question of 2026-09-27, and his recollection — correct — that the matched
corpus already exists.

---

## 1. The design was built a fortnight ago and never used for this

`prereg_family_coherence.md` §3 documents two prompt families:

| family | description | prompts |
|---|---|---|
| **A1** | Western comics, extreme close-up head only, white background, **one pinned monochromatic hue per prompt** | F1–F4, G1–G6, H01–H08 |
| **A2** | *"same template as A1, **no colour clause**"* | S7_01 – S7_06 |

and states: *"A2 is matched one-to-one with G1–G6: same subject, with and without the colour clause
(prompt-text similarity 0.94, 0.94, 0.78, 0.95, 0.45, 0.95)."*

**Six matched pairs, same subject, the only systematic difference being an explicit colour
declaration.** Both arms carry the same six conditions — `rand ±`, `preset ±`, `blockshuf ±` — at
the same five seeds, with baselines. This is a within-subject design and it needs nothing new.

The declared colour in the A1 arm is a *rim-light hue*: `teal` (G1), `yellow` (G2), `teal` (G3),
`chartreuse` (G4), `blue` (G5), `purple` (G6).

## 2. Statistic

Per prompt, per trait, the seed noise σ comes from **that prompt's own baselines** (pitfall 33), and
only from the **five shared seeds**, so the two arms are estimated on equal footing — A1 has fifteen
baselines and A2 eight, and an unequal σ is the kind of denominator that has already misled this
project twice today.

```
z(trait)  = mean over the 6 conditions × 5 seeds of |x − baseline_mean| / σ
colour_z  = mean of z over the 4 colour traits
texture_z = mean of z over the 8 texture traits
ratio     = colour_z / texture_z            <- PRIMARY, per prompt
```

The **ratio** is primary because it is taken within a prompt: whether one prompt is globally more
perturbable than another cancels, and only the *relative* mobility of colour survives. `colour_z`
alone is reported as a secondary.

**Unit of analysis: the pair.** n = 6. Exact two-sided sign test, floor **2/2⁶ = 0.03125** — which
only a 6/6 split can reach. No p below that can be produced by this design and none will be claimed.

## 3. The two hypotheses predict opposite signs

| | mechanism | prediction |
|---|---|---|
| **Alessandro** | a declared colour is a live variable carried by the text encoder, so perturbing the weights perturbs it | `ratio(A1) > ratio(A2)` — declared colour moves **more** |
| **ColorWave** (arXiv 2503.09864) | a declared colour token binds through the **key** projection and *dominates*; overriding it fails for semantically distant colours | `ratio(A1) < ratio(A2)` — declared colour moves **less** |

**H-A (Alessandro)**: confirmed if `ratio(A1) > ratio(A2)` in **≥ 5 of 6** pairs.
**H-C (ColorWave)**: confirmed if `ratio(A1) < ratio(A2)` in **≥ 5 of 6** pairs.
**Neither**: 3–3 or 4–2 either way is reported as undecided, and undecided is the most likely
outcome with six pairs.

The analyst's own expectation, deposited: **H-C**, because today's transfer test found the colour
response to be subject-bound (0.514 at chance) and ColorWave locates the binding in exactly the
projection family this project measured as sign-blind.

## 4. Declared in advance

* **Pair 5** (`S7_05` against `G5`) has prompt-text similarity **0.45**, far below the other five
  (0.78–0.95). The primary is computed on all six; a sensitivity check **excluding pair 5** is
  reported beside it, and if the two disagree, **neither is claimed**.
* Both arms are extreme close-ups on a white background, so framing, style and medium are held
  constant. The residual confound is the subject wording itself, which differs slightly even in a
  matched pair.
* `preset_half` exists only in A1 and is **excluded** from both arms.
* This is a test of what **the four colour descriptors** see. A colour effect invisible to them will
  not appear.
* No claim status changes on this result.
