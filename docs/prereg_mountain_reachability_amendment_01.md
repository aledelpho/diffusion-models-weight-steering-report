# Amendment 01 to `docs/prereg_mountain_reachability.md`

- **Written:** 2026-09-25
- **Amends:** the phase-2 section and the power gate of
  `docs/prereg_mountain_reachability.md` (committed `c932b2e`).
- **Everything else in that document is unchanged and remains in force.**
- **Written before any render of this extension exists.**

---

## 1. What the frozen document gets wrong

Phase 2, as written, renders **384 baselines with no tuner in the graph**. That grows the
base cloud `B` against which `d_out` is measured. It adds **no prompt to the test**.

The unit of analysis is the prompt of the *edited* images, and after Block C that is still
the eight stage-9 style prompts S1–S8. The sign-flip floor is `2/2^8 = 0.0078`; after Holm
across four arms the best achievable p is `0.031`. `preset_pos_2x` reached 7 prompts out
of 8 (`p = 0.0156`, Holm `0.0625`) and missed by one.

Phase 2 as frozen leaves that exactly where it is.

The §3 power gate is also ambiguous: it says "under 12 distinct prompts, descriptive only"
without saying *which* prompts. It was implemented against `|B|` (52 prompts, passed) while
the test ran on 8. The ambiguity is the author's.

## 2. The power gate, restated unambiguously

**The power gate counts the distinct prompts on which the *arms* are rendered — the unit
of the test. It never counts the size of the base cloud `B`.**

Under 12 such prompts the analysis is **descriptive only**: no p-value, no verdict, no
claim. This replaces the §3 wording and applies retrospectively: **the committed Block C
run (`3f7dcc6`) is descriptive**, not confirmatory. Its numbers stand as recorded; their
interpretation is downgraded, and any page citing them says so.

## 3. The cheapest fix costs nothing: replicate on stage 7

An inventory of the repository carried out on 2026-09-25, **before this amendment and
before any render was authorised**, establishes:

- `data/style_features_stage7.csv` holds 24 prompts, of which **16 carry the arms**
  (`I01`–`I24` subset) as `baseline + 6 arms` x 5 seeds, and 8 are baseline-only
  (`I03`, `I04`, `I08`, `I13`, `I14`, `I15`, `I19`, `I22`). 120 (condition, prompt) cells
  of exactly five seeds each. The arms include `preset_pos`, `blockshuf_neg` and
  `rand_pos`. **The test therefore runs on 16 prompts, not 24** — an earlier draft of this
  amendment said 24, which counted prompts that have no arms.
- 18 further prompts (F1–F4, G1–G6, H01–H08) carry the same arm family in
  `data/palette_features_all.csv`.
- Of the 40 prompts in `data/prompts.json`, **only six have never been rendered with any
  arm**: `S7_01`–`S7_06`, the whole `colour-free` family. The `colour-pinned` and
  `stage7_confirmation` families are fully used.

Therefore the primary extension is a **replication on stage 7, with no new renders**:

- **16** test prompts, sign-flip floor `2/2^16 = 3.052e-05` (against `0.0078` on the
  8-prompt stage-9 test)
- arms `preset_pos`, `blockshuf_neg`, `rand_pos`, plus `baseline`
- base cloud `B` built by the same rule as before, from the stage-7 baselines plus every
  other baseline already available
- `d_out`, `Delta(P,s)`, R1, R2, the exact sign-flip test and the Holm correction are
  **unchanged**

**This is a replication on a different corpus, not an enlargement of the stage-9 test.**
The stage-7 arms are not the same objects as stage 9's `_1x` and `_2x` doses. The two
results are reported side by side in separate rows, each naming its corpus and its arm
set. **They are never pooled into one test.** Pooling benches that used different preset
files or different doses is the accorpamento pitfall this project has already been bitten
by once.

If stage 7 and stage 9 agree, the conclusion is strengthened by replication. If they
disagree, that disagreement is the finding and no claim is promoted.

## 4. The render-based extension, only if §3 proves impossible

Run this **only** if the stage-7 replication cannot be made to work for a stated technical
reason, or if the `_1x` / `_2x` dose arms are judged essential to the question. Alessandro
decides; Antigravity does not.

The eligible pool is **six prompts** — `S7_01`–`S7_06` — giving **14 test prompts**
(8 + 6), which clears the gate of §2. Sign-flip floor `2/2^14 = 1.221e-04`; after Holm
across four arms, `4.883e-04`.

Per prompt: 5 seeds x 5 conditions (`baseline`, `preset_pos_1x`, `preset_pos_2x`,
`blockshuf_neg_1x`, `rand_pos_1x`) = 25 renders. **150 renders in total.**

- folder `benchmark_stage9_ext`, naming and sampler identical to stage 9
  (euler_ancestral, 9 steps, cfg 1.0, simple, denoise 1.0, 1024x1280)
- manifest `data/stage9_ext_images.csv`, same columns as `data/stage9_images.csv`
- features `data/style_features_stage9_ext.csv`, produced by the **unmodified** feature
  script already in the repository

**No prompt is authored for this study.** The six are taken whole from the frozen
catalogue, whose own note records that prompts are never edited and are proven by their
hash. Writing new prompts now, knowing what we hope to find, would make prompt authorship
a free parameter; if it ever becomes necessary it needs its own amendment and its own
rule.

Because all six eligible prompts are used, **there is no selection step and nothing to
draw**. That removes the largest opportunity for bias in this extension: the current
per-prompt results are known — `preset_pos_1x` produced its largest positive deltas on S7
(+1.532) and S8 (+1.918) — and any rule that let us *pick* new prompts would have been an
invitation to pick ones that resemble those.

## 5. Phase 2's 384 baselines

Still worth rendering on their own merits, and independent of §3 and §4: `d_out` is a
minimum over `B`, and a sparse cloud inflates it. The specification in the frozen document
is unchanged. **It does not raise the power and must never be reported as if it did.**

## 6. Environment determinism check — runs first, has a stop

Required before any new render counts, for §4 and for phase 2 alike.

Re-render **S1 baseline seed 42** with the current environment and compare it byte for
byte with the committed render of the same name.

- **Identical** -> the environment has not drifted; proceed.
- **Not identical** -> **STOP**. Every comparison between old and new renders is
  contaminated. Measure and report the size of the drift before anything else is decided.
  Do not proceed on the assumption that a small difference is harmless.

## 7. Standardisation

Features are standardised using **baselines only**, computed once over the baseline set of
the corpus being analysed, and applied unchanged to every cell of that corpus (pitfall 33).
Stage 7 and stage 9 each get their own standardisation, from their own baselines. Neither
is applied to the other.

If §4 runs, the stage-9 standardisation is recomputed over the combined baseline set (the
original eight prompts plus the six new ones). This changes the numbers for the original
eight, which is expected and must be **visible**: the results file carries both the
8-prompt rows under the old standardisation and the 14-prompt rows under the new one, in
separate labelled rows, so a reader can see how much of any change came from new prompts
and how much from the change of reference frame.

## 8. What is not changed

The definition of `d_out`, the primary statistic `Delta(P,s)`, R1 and R2, the exact
sign-flip permutation, the Holm correction across arms, and the requirement that the
prompt is the unit of analysis are all unchanged and remain binding.

## 9. What would kill this

- The determinism check of §6 fails.
- The stage-7 replication and the stage-9 test disagree in sign: reported as the finding,
  no claim promoted.
- The re-standardisation of §7 moves the original eight prompts' deltas by more than the
  effect being tested: the comparison is then dominated by the change of reference frame,
  and that is reported as the finding.
