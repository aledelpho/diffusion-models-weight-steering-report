# Amendment 01 to `docs/prereg_family_coherence.md`

- **Written:** 2026-09-25
- **Status:** written **before** the analysis script exists and before any statistic is
  computed. The parent pre-registration is frozen at commit `35de33e`.
- **Reason:** three facts about the corpora were established after the parent document was
  written and contradict it. Each is recorded here rather than silently absorbed.

---

## 1. Prompt-id collision — `S7`

Two different prompts in this study are called `S7`:

- `S7_01` … `S7_06` — the colour-free close-ups of family **A2**, in
  `data/style_features.csv` (run `stage7_20260915_123328`);
- `S7_glass` — the stained-glass style of family **C**, in
  `data/style_features_stage9.csv` (run `stage9_20260918_085644`).

They are unrelated prompts. Merging the three feature files on the bare prompt id would
silently fuse a close-up portrait with a rally car.

**Correction.** Prompt identity is the pair (source feature file, prompt id). The eight
family-C prompts carry the internal ids `ST1` … `ST8` in every output file, and the mapping
`ST1 = S1_photo`, …, `ST7 = S7_glass`, `ST8 = S8_charcoal` is written into
`data/family_coherence_inventory.csv`. Nothing else in the study uses a bare prompt id.

## 2. The run label is a property of (prompt, arm), not of the prompt

§2 and §6 of the parent document assign one run per prompt. That is false for family A1.
The manifests give:

| prompts | baseline | `preset_*`, `rand_*` | `blockshuf_*` |
|---|---|---|---|
| F1–F4 | `stage2_family_20260913_190334` | `stage4_preset_20260914_175453` | `stage5_20260915_080853` |
| G1–G6 | `stage5_20260915_080853` | `stage5_20260915_080853` | `stage5_20260915_080853` |
| H01–H08 | `stage6_20260915_122957` | `stage6_20260915_122957` | `stage6_20260915_122957` |
| S7_01–S7_06 | `stage7_20260915_123328` | `stage7_20260915_123328` | `stage7_20260915_123328` |
| I… | `stage7a_20260917_121226` | `stage7b_20260917_132611` | `stage7b_20260917_132611` |
| ST1–ST8 | `stage9_20260918_085644` | `stage9_20260918_085644` | `stage9_20260918_085644` |

**Correction.** The run label used by Guard R1 and Guard R2 is read from the manifests for
each (prompt, arm) separately, not assumed. Consequently the within-A1 run partition
differs by arm: for `preset_*` and `rand_*` it is {F=4, G=6, H=8}, giving
4·6 + 4·8 + 6·8 = **104** cross-run pairs inside A1; for `blockshuf_*` it is
{F∪G = 10, H = 8}, giving 10·8 = **80**. Both counts are asserted by the script and a
mismatch aborts the run.

## 3. Family A1 is not homogeneous in how its displacement is anchored

For F1–F4 the baseline was rendered on 2026-09-13 and the `preset_*` / `rand_*` arms on
2026-09-14; the `blockshuf_*` arms on 2026-09-15. Δ(F, a) therefore crosses runs by
construction, while Δ(G, a) and Δ(H, a) do not. For family B the baseline and the arms come
from two runs of the same day.

**Correction — one extra analysis, specified now.** The whole primary analysis is repeated
with F1–F4 removed (A1 = 14 prompts, 44 prompts in total). This is a robustness check, not
a second primary.

**Added decision rule, appended to §7 of the parent document:** if the verdict reached on
the 48-prompt set and the verdict reached on the 44-prompt set are not the same verdict,
the result is recorded as *ambiguous — the family effect depends on four prompts whose
baseline was rendered on another day* and is not published as a claim. This rule is fixed
before any number exists.

## 4. What does not change

Feature set, standardisation from baselines only, the Δ definition, the cosine, the
permutation null and its 10 000 draws with `random.Random(1337)`, the bootstrap over
prompts, the Holm correction, the 2× factor of §7 rules 3 and 4, and the texture-only
sensitivity of §8 are unchanged. No new render is generated.
