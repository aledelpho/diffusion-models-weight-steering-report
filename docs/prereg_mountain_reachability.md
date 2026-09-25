# Pre-registration — is the look already on the mountain?

**Deposited** 2026-09-24, before any of the statistics below were computed.
**Status** frozen. Amendments go at the bottom, dated, never in the body.
**Runs** locally (Antigravity). Phase 1 renders nothing.

---

## 1. The claim being tested

From the tool's own announcement, in the author's words:

> Think of a model as a mountain range and your prompt as the spot where you pour a bucket of
> water. [...] **It's highly probable that the exact look you want already exists somewhere on
> that mountain** [...] It just never shows up, because the terrain doesn't incentivize the water
> to reach it. [...] dig one canal, shift one ridge, and the water finds a new home.

Nothing in the notebook tests this. Every page so far asks *how much* an edit moves the image and
*in which direction*; none asks **whether the place it moves to is somewhere the model already
goes.** That is the difference between an edit that re-routes and an edit that invents — and it
is the difference between a tool that surfaces what the checkpoint already knows and a tool that
manufactures artefacts.

Two readings. Both are tested; the second is primary because it is the one the analogy makes.

**R1 — on the mountain.** An edited render lands inside the region of feature space the base
model already occupies. It is a place on the mountain, not a new mountain.

**R2 — the water found an existing valley.** The edit moves *this prompt's* output **toward** the
region the base model already occupies **for other prompts and seeds**. The look was already in
the repertoire; the edit re-routed this scene into it.

The interesting refutation is R2 failing with a positive sign: the edit pushes the output **away**
from everything the base model does anywhere, which would mean the canal is not a canal but a hole.

---

## 2. The measure — fixed, not negotiable after the data

**Space.** The 23 numeric style features of `experiments/style_features.py`, the same set used by
`experiments/arm_coherence.py`. Standardised **once**, on the base cloud defined in §3, and that
standardisation applied to every render including the edited ones (pitfall 33: a separate
standardisation per condition manufactures whatever you were hoping for).

**The base cloud `B`.** Every clean baseline render the repository can account for: condition
`baseline`, resolution 1024x1280, listed in a manifest under `data/`. No edited render enters `B`.

**Distances.** Euclidean in the standardised space.

For a render `x` belonging to prompt `P`:

```
d_out(x) = min over b in B with prompt(b) != P      of  ||x - b||
d_in (x) = min over b in B with b != x               of  ||x - b||
```

`d_out` deliberately excludes the render's own prompt. In this space the dominant axis is prompt
identity — a low-poly render is far from a watercolour one whatever you do to the weights — so a
nearest neighbour drawn from the same prompt would answer a different and much duller question.

**Primary statistic.** Per cell `(P, s)`:

```
Delta(P, s) = d_out(edited at P,s) - d_out(baseline at P,s)
```

Negative means the edit moved this scene **toward** the rest of the model's repertoire. Positive
means away from it. Cells are averaged **within prompt first**; the prompt is the unit of
analysis and the seeds are repeated measures (pitfall 17). The test is an exact sign-flip over
prompts, two-tailed, with its floor `2/2^n` reported beside it, Holm-corrected across the arms in
§4.

**Secondary statistic (R1).** The same paired difference on `d_in`, read against the base cloud's
own spacing: for every baseline in `B`, its `d_out` to another baseline. If an edited render's
`d_out` sits inside the range that baselines already occupy, the edit stayed on the mountain.

**Reported alongside, not tested.** `||Delta_features||` per cell, so the reader can see that an
edit which barely moves cannot move toward or away from anything.

---

## 3. The corpus

Phase 1 uses renders that already exist. **No generation.**

**Base cloud.** Assembled from the baseline rows of every manifest under `data/` that records a
`condition`/`cond_name` of `baseline`, a resolution, and an on-disk path. Candidates, to be
confirmed by the inventory step, not assumed:

| source | what it contributes |
|---|---|
| `stage2_images.csv`, `stage4_images.csv` | the F-prompt family, many seeds each |
| `stage5_images.csv`, `stage6_images.csv`, `stage6b_pilot_images.csv` | the F/G, H and S7 families — the 1272 corpus of page 01 |
| `stage7a_images.csv`, `stage7b_images.csv` | the 24 I-prompts |
| `stage9_images.csv` | 32 prompts x 5 seeds, incl. the 8 style prompts |
| `benchmark_pavimento_rumore` | 2 prompts x 16 seeds — the densest per-prompt sample there is |

**Edited renders.** The six arms of the stage-9 bench: `preset_pos_1x`, `preset_pos_2x`,
`blockshuf_neg_1x`, `blockshuf_neg_2x`, `rand_pos_1x`, `rand_pos_2x`, on the eight style prompts,
five seeds each. 240 renders, all already extracted in `data/style_features_stage9.csv`.

**Exclusions, declared now.** Any render not 1024x1280 (the HUD census, `data/hud_contaminated_images.csv`).
Any prompt whose baselines are fewer than 3 seeds. `chaos_edges_v2`, because it ran on different
prompts from the other arms.

**Power.** The inventory step must print, before any statistic is computed: the number of
distinct prompts in `B`, the number of renders, and the median `d_out` among baselines. If `B`
holds fewer than **12 distinct prompts**, phase 1 is declared underpowered and only reported as
descriptive — the nearest neighbour in a sparse cloud is an accident of sampling, not a fact
about the model.

---

## 4. What counts as what — written before looking

Tested on four arms: `preset_pos_1x`, `preset_pos_2x`, `blockshuf_neg_1x`, `rand_pos_1x`.
Holm across those four.

| outcome | criterion |
|---|---|
| **R2 confirmed for an arm** | mean `Delta` negative **and** Holm p <= 0.05 **and** negative on at least 6 prompts of 8 |
| **R2 refuted for an arm** | mean `Delta` positive **and** Holm p <= 0.05 |
| **R2 ambiguous** | anything else, including a clear sign with p above the bar |
| **R1 holds** | the edited `d_out` distribution lies inside the 5th-95th percentile band of the baselines' own `d_out` |
| **R1 fails** | more than a quarter of edited renders sit above the 95th percentile of that band |

The headline claim of the analogy is confirmed only if **R2 is confirmed for the calibrated
preset at at least one amplitude.** The random scramble is the control: if the scramble also
re-routes, then re-routing is a property of moving the weights at all, exactly as the seed-level
coherence turned out to be (`data/arm_coherence_tests.csv`), and the analogy describes
perturbation in general rather than calibration.

**Declared in advance:** I expect R2 confirmed for the preset and ambiguous or refuted for the
scramble at double amplitude. Writing this down is what makes it possible to be wrong.

---

## 5. Traps this design is built to avoid

* **Prompt identity swamping the space** — hence `d_out` excludes the render's own prompt.
* **Cloud density** — a nearest-neighbour distance shrinks where the cloud is dense. Edited and
  baseline are compared **against the same cloud, at the same prompt**, so the bias is shared and
  cancels in the paired difference. It does not cancel across prompts, which is why prompts are
  the unit and the test is a sign-flip rather than a pooled t.
* **Leakage** — no edited render may enter `B`, and a render is never its own nearest neighbour.
* **Contamination** — 1024x1280 only.
* **Space-shopping** — the primary space is the 23 style features, frozen here. The palette space
  of `data/palette_features_stage9.csv` is a **secondary replication**, declared now, reported
  whatever it says. No third space.
* **Unmatched displacement** — the arms of this bench are not at matched displacement (page 09).
  Magnitudes are therefore descriptive. The sign of `Delta` is what is tested, and it does not
  depend on how hard the arm was pushed.

---

## 6. How to run it

### Step 1 — deposit this file

```
git add docs/prereg_mountain_reachability.md
git commit -m "prereg: la terza promessa, il look e' gia' sulla montagna"
```

Do this **before** step 2. A pre-registration committed after the numbers is a write-up.

### Step 2 — write `experiments/mountain_reachability.py`

One script, no rendering. Contract:

```
python experiments/mountain_reachability.py --inventory      # only §3, prints and stops
python experiments/mountain_reachability.py                  # the full run
python experiments/mountain_reachability.py --space palette  # the declared replication
```

It must:

1. Build `B` from the manifests, resolving each `image_path` against its `renders_root`, skipping
   any file not on disk and **printing how many it skipped** — a silently shrinking cloud is the
   failure mode here.
2. Extract features for any baseline not already in a `data/*_features*.csv`, reusing
   `experiments/style_features.py` unchanged. Cache to `data/mountain_base_features.csv` so a
   second run is cheap.
3. Standardise once on `B`; compute `d_out` and `d_in` for every baseline and every stage-9
   edited render.
4. Write three files:
   * `data/mountain_reachability.csv` — one row per (arm, prompt, seed): `d_out_edited`,
     `d_out_baseline`, `delta`, `d_in_edited`, `d_in_baseline`, `nearest_prompt_edited`,
     `nearest_prompt_baseline`, `delta_norm`
   * `data/mountain_reachability_by_prompt.csv` — the per-prompt means the test runs on
   * `data/mountain_reachability_tests.csv` — per arm: `mean_delta`, `prompts_negative`,
     `p_sign_flip`, `p_floor`, `p_holm`, `verdict` drawn from the table in §4 **verbatim**
5. Fail loudly rather than guess: no baseline for a cell, fewer than 12 prompts, a feature that
   does not vary — stop with a message naming the file.

`nearest_prompt_edited` is not decoration. If the preset on a charcoal render lands nearest a
*photography* baseline, that is the canal in one line, and it belongs in the output where anyone
can read it.

### Step 3 — run and report back

```
python experiments/mountain_reachability.py --inventory
python experiments/mountain_reachability.py
python experiments/mountain_reachability.py --space palette
python experiments/validate_notebook.py
```

Report: the inventory line (prompts, renders, skipped, median baseline `d_out`), the four rows of
`mountain_reachability_tests.csv` in both spaces, and the ten most common
`nearest_prompt_edited` values for `preset_pos_2x`.

### Step 4 — only if the inventory says underpowered

If `B` holds fewer than 12 distinct prompts, or fewer than 5 seeds on most of them, the cloud is
too sparse and phase 2 renders a proper one. **Baselines only, no tuner in the graph**, which is
the cheapest thing this project renders:

* 24 prompts spread across the families already in `data/prompts.json` — not 24 variations of one
  scene, the point is coverage of the mountain
* 16 seeds each: `42, 777, 1337, 9999, 4242145, 101..110`
* 384 renders, folder `benchmark_montagna`, naming
  `{prompt_id}_baseline_seed{seed}_00001_.png`, same sampler as every other bench
  (euler_ancestral, 9 steps, cfg 1.0, simple, denoise 1.0, 1024x1280)
* a manifest at `data/montagna_images.csv` with the same columns as `data/stage9_images.csv`

Then re-run step 3. Nothing about §2 or §4 changes; the corpus grows, the criteria do not.

---

## 7. What this cannot settle, whatever it returns

It compares an edited render to renders the base model produced **at the prompts and seeds we
happened to run**. The base model's true repertoire is larger than any sample of it, so a large
`d_out` means "far from everything we sampled", never "impossible for the model". The honest
phrasing of a refutation is *the edit leaves the sampled repertoire*, and the honest phrasing of a
confirmation is *the edit stays inside it* — neither is a statement about the checkpoint's limits.

And a render landing near another prompt's baseline is a statement about 23 summary statistics,
not about looking alike. The first thing to do with a confirmed re-routing is to put the edited
render and its nearest base neighbour side by side and look at them.

---

## Amendments

*(none yet — date and sign each one, and never edit above this line)*
