# Amendment 01 to `docs/prereg_groove_or_hole.md`

- **Written:** 2026-09-28, before any statistic of the study was computed. So far only file counts,
  column names and render locations have been read.
- **Amends:** §5 G0, §3.1 (how prompt texts are resolved), §3.2 (a fallback for `N(p)`), §4.3 (what a "visible cell" is), and adds where the renders are read from.

---

## 1. G0 pointed at a number computed under a different standardisation

§5 G0 asked the script to reproduce the parent's stage-7 row for `preset_pos` (mean Δ 0.501902). That
row was **not** computed with the parent's §2 standardisation. The parent's amendment 01 §7 z-scores
the stage-7 replication on the **stage-7 baselines only**. This study uses the parent's §2 rule: one
z-score, on the base cloud `B`. Reproducing a number made under another rule checks the distance
mechanics, but not the standardisation this study depends on.

**G0 now requires both reproductions, each under its own rule, to four decimals:**

- **G0a:** stage 9, `preset_pos_1x`, mean Δ over the 8 style prompts = **0.530427**. This uses the
  parent's §2 standardisation on `B` and the parent's prompt-id matching, which is exactly this
  study's measure except for the prompt matching.
- **G0b:** stage 7, `preset_pos`, mean Δ = **0.501902** with Holm p = **0.002441**. This uses the
  parent's amendment-01 standardisation on the stage-7 baselines.

If either fails, the study stops.

## 2. How prompt texts are resolved

§3.1 matches prompts by the SHA-1 of their text. The repository's manifests store `prompt_sha1` as
the first **10** hex characters of `sha1(prompt_text.encode("utf-8"))`. This study uses the same
convention.

Resolution order, per render:
1. `prompt_sha1`, or `prompt_text` hashed, from any manifest in `data/` that lists the file;
2. otherwise the positive prompt read from the PNG's embedded graph. The sampler node's `positive`
   input is followed back to the node carrying a `text` input.

A read-only inventory found that 377 of the 409 cloud rows resolve through step 1. The other 32 are
the P01 and P02 baselines of `benchmark_pavimento_rumore` and `benchmark_latenti_b6`, whose renders
are on disk for step 2. **Any cloud row or tested render that resolves through neither step aborts
the study.** An id that maps to two texts is not an error in `B` (`S7` is known to), but it is an
error for a tested prompt.

## 2b. When a tested prompt has no copies in the cloud

§3.2 defines the seed-noise unit `N(p)` from the baselines of prompt `p` in `B`. The eight atlas
scenes (bench Q) may have prompt texts that differ from the eight stage-9 style prompts in `B`. If
so, `B` holds no baseline of theirs.

**Rule:** `N(p)` uses the baselines in `B` whose text matches `p`, if there are at least 3.
Otherwise it uses the bench's own baselines of `p`: 3 seeds, 3 pairs. Each row records which source
was used (`n_source` = `cloud` / `bench`).

`d_out` is not affected. It always excludes by text, and a similar but different prompt stays in
`B` by design (§10).

## 2c. What "visible cell" means in §4.3

The pooled count in §4.3 ("at least half of all visible cells … are holes") is taken over units
`(condition, dose, prompt)`:

- a unit is **visible** iff `V(c,p) ≥ 1.0`;
- a visible unit is a **hole** iff its seed-mean `Δout > 0`;
- in bench Q, a unit is a `(condition, scene)` pair.

## 3. Where the renders are read from

- **Bench M, Q and the atlas baselines:** the features already in `data/style_features_mappa.csv`,
  `data/style_features_qkvo.csv` and `data/style_features_atlas_phase1.csv`, used as they are.
- **Benches K and D:** features extracted with `experiments/style_features.py`, unmodified, from the
  renders in `C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_blk16_ladder`,
  `…\benchmark_profondita` and `…\benchmark_profondita_neg`. They are cached as
  `data/style_features_blk16_ladder.csv` and `data/style_features_profondita.csv` before anything else
  runs.
- **G1 and G3** read PNG metadata and pixels from those same folders and from the `benchmark_mappa`,
  `benchmark_qkvo_atlas` and `benchmark_atlas_phase1` folders there.

**G1b, the same extractor on both sides.** Benches K and D compare freshly extracted edits with
baselines whose features come from `style_features_mappa.csv`. Before any of those comparisons, the
six mappa baselines (P01, P02 × 3 seeds) are re-extracted with the same call used for K and D. Each
feature must agree with the cached value within 1% of its cloud standard deviation. The colour-cluster
features, whose k-means is known not to be bit-reproducible, get 5%. If any feature fails, K and D
use the freshly extracted baselines instead, and the substitution is recorded.

## 4. What is not changed

The measure (§3), the gates, the decision rules (§4), G1–G4, G_eye, the predictions (§7) and
Stage B are unchanged. The script still refuses to compute any `Δout` for the four benches while §7
reads "PENDING".
