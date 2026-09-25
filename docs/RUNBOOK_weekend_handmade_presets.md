# Runbook — hand-made presets at free displacement

- **Written:** 2026-09-25, before any of these presets exist.
- **For:** a batch of presets authored by hand, on whichever blocks the author judges safe,
  **without** matching the Frobenius displacement.
- **Answers:** capacity, identity and aimability — the product claims.
- **Gives up:** every claim of the form *structure, not magnitude*. Read §1 before starting.

---

## 1. What dropping the norm costs, and what it does not

Frobenius matching is a **control for a causal question**: *is the effect due to the structure
of the edit or merely to its size?* Without it, that question cannot be asked of this batch.

It is **not** needed for the product questions. A user of the tuner does not hold D fixed. Asking
"are these styles distinguishable from one another and recognisable across subjects" requires no
matching at all. So this batch is the right material for the capacity claim and the wrong
material for the mechanism claim. Nothing is lost that this project has not already measured at
matched displacement.

**One condition, non-negotiable: D must still be recorded.** It costs one command and it is what
allows every result to be reported a second time per unit of displacement — the correction that
`output-lead-survives-dose-normalisation` shows is not optional. Without it, a preset that is
simply bigger will look more distinctive and nothing will be able to tell the difference.

    python experiments/measure_all_displacements.py --all --out data/preset_displacements_weekend.csv

`--all` measures every `presets/*.json`. With no argument the script behaves exactly as before
and `data/preset_displacements.csv` is untouched.

## 2. The trap that would waste the whole weekend

The author will look at the renders and keep the presets that look good. **That selection is the
experiment's largest confound**, and it is invisible once it has happened: a set of presets
chosen for being visibly different will of course measure as visibly different.

Two rules make it harmless, and turn it into an extra result:

1. **Keep everything.** Every preset that gets authored gets rendered and measured, including the
   ones the author dislikes. Deleting a preset after seeing it is selection on the outcome.
2. **Record the judgement before the measurement**, in `data/weekend_presets_author_key.csv`,
   and commit its SHA256 in the same commit — the procedure already used for
   `data/stage12_pattern_key.sha256`. The author's eye then becomes a **variable that can be
   tested** rather than a filter that cannot be seen.

That second rule buys a claim this project does not have: *does the author's judgement predict
measured distinctiveness?* If it does, the tuner is aimable by the person holding it, which is a
stronger product statement than any capacity number.

## 3. The batch

**Presets.** N ≥ 8 hand-made, free displacement, any blocks. Plus **three anchors already
measured** — `Arthemy_Bench_Base` (`preset_pos`), `Arthemy_Bench_RANDSIGN` (`rand_pos`),
`Arthemy_Bench_BLOCKSHUFFLE_NEG` (`blockshuf_neg`) — and the **baseline**. The anchors are the
positive control: they are known to be identifiable at 80–96 % on unseen prompts
(`data/arm_identifiability_tests.csv`), so if the batch fails to recover them, the batch is
broken and not the presets.

**Prompts: 8, as 4 + 4 from two different style domains.** This is the single most valuable
choice in the runbook and it is free:

- 8 prompts make **leave-one-prompt-out** possible, which Phase 1 of the atlas cannot do with
  one prompt. Capacity then means *capacity that survives a change of subject*, which is the
  product claim rather than a claim about one scene.
- Two domains rendered **in one queue** is exactly the 4 + 4 design that
  `docs/prereg_domain_specificity.md` §8 asks for. The same batch replicates a provisional
  result for free.

Suggested: 4 of the `I` comics prompts already in the corpus, and 4 of the `S` style prompts
(photo, watercolour, pixel, charcoal). Reusing existing prompt texts lets the new batch be
compared directly against everything already measured.

**Seeds:** 42, 777, 1337 at minimum; add 9999 and 4242145 if the queue allows. The same seeds for
every preset and for the baseline — everything downstream is seed-paired against the baseline.

**One queue, one session.** Do not split the two domains across two runs; that is the confound
this design exists to remove.

**Cost.** (8 presets + 3 anchors + 1 baseline) × 8 prompts × 3 seeds = **288 renders**.
At 5 seeds, 480.

## 4. The manifest

One row per render, written while queueing, not reconstructed afterwards:

    row_index,type,preset_name,preset_file,preset_sha256,prompt_id,prompt_sha1,seed,
    sampler,scheduler,steps,cfg,denoise,width,height,expected_filename,prompt_text

as `data/weekend_presets_plan.csv`, and one row per preset in
`data/weekend_presets_author_key.csv`:

    preset_name,blocks_touched,sign,rough_magnitude,intent_one_line,
    author_keeps,author_distinctiveness_1_5,author_damage_1_5

`intent_one_line` is what the author was aiming for, in his own words, written **before**
rendering. It is the raw material for any future claim about aiming, and it cannot be
reconstructed later.

## 5. A quality gate, frozen now

Page 09 records that at double amplitude 18 cells of 24 fall outside a 3σ quality range, the
worst at z = 131.7. Free displacement can go further than that.

Gate, fixed before the first render: a preset is **out of range** on a prompt if its edge density
or its texture entropy is more than 3σ from the baseline's, where σ is the seed-to-seed spread of
the baseline on that prompt. Out-of-range presets are **kept and measured**, never dropped, and
every result is reported twice: over all presets, and over the in-range ones only. That is what
makes the ceiling a measurement instead of a housekeeping decision.

## 6. Running the evaluation

    python experiments/style_features.py --dir <renders> --out data/style_features_weekend.csv
    python experiments/measure_all_displacements.py --all --out data/preset_displacements_weekend.csv

Then the analyses, which exist and are frozen: the capacity machinery of
`experiments/style_capacity.py` (τ from the max-statistic, K as connected components, the
Euclidean/cosine pair), and the leave-one-prompt-out identification of
`experiments/arm_identifiability.py`. Both need a small adapter to read this manifest instead of
their own; **the adapter is written before the renders are measured**, and the statistics are not
touched.

## 7. What this batch cannot do

- It cannot say whether an effect comes from structure or from magnitude. See §1.
- It cannot compare cleanly against the atlas, whose conditions are displacement-matched.
- With 3 seeds, a preset's centroid rests on three images; the max-statistic null will be honest
  about that by returning a large τ, and a small K will mean "this batch could not resolve more",
  not "the tuner makes few styles".
