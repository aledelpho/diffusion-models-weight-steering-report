# Night report — 2026-09-21

Autonomous session on `main`, resumed the same day. Seven commits, **no push**. Working tree
clean, `validate_notebook.py` at 0 errors, the self-test at 18/18.

```
93f986e  feat(notebook): capitolo 03 - ingrandimento del soggetto e cecita' misurata
f0fb0a2  fix(02): i pitfall 8 e 10 citati non erano pitfall, erano regole
4d0fde4  docs: report della notte 2026-09-21
0ab9261  docs: il registro delle claim, e l'inventario aggiornato
aadf9fa  feat(notebook): capitolo 02 - attribute emergence, e il primo builder vero
ed709c3  fix(figure): l'alt di F05.3 pubblicava il 12,4x ritrattato
4d066c6  docs: inventario misurato del notebook prima della migrazione
```

Five of the fifteen pages are live: 00, 02, 03, 05, 06. The claims ledger stands at 9 migrated
and 16 pending, all 23 original bullets accounted for.

---

## 1. What was done

**The inventory first** — `docs/inventario_notebook.md`, 3,600 words. Every file in `docs/`
(44 + 2 directories), `experiments/` (70 scripts), `data/` (111 files) and `assets/`
(8 directories, 1,417 files), each with its destination; the section-by-section map of the old
README; and a page map of **fifteen** pages rather than eight. Section 0 of that file lists the
nine assumptions of the migration plan that do not survive contact with the tree.

**The retracted ratio** — F05.3's alt text still published 12.4×, the figure the commit
`c843d61` withdrew. The page body already said 9.1×, so the figure's own claim contradicted the
page carrying it. Corrected against `data/punto7_blocks.csv` (13.621680 / 1.495314 = 9.11) in
`figures.yaml`, in the page, and in the two `AUTHORING.md` examples that were teaching 12.4× as
the model of a well-written alt text.

**Page 02** — `notebook/02-attribute-emergence.md`, migrated from lines 845–1127 of
`c843d61:README.md`. Five registered figures, all whole frames, all built from measurement
files. Three claims, which are the three the brief expected.

**The first real builder** — `experiments/notebook_figures.py`. The contract has named this
module since it was written and it had never existed; every entry in `figures.yaml` pointed
into it. It now holds one working function, `barnacle_census`, which reads
`data/attribute_emergence.csv`, derives every panel caption from the row it is drawing, raises
rather than draw a panel it cannot look up, shows whole frames and draws on `#1a1a19`. F02.4
and F02.5 come from it.

**A number that lived only in prose** — the per-style headlight table was typed into the old
README and existed in no file. `experiments/headlights_by_style.py` derives it from the sealed
blind round into `data/stage9_headlights_by_style.csv`.

**The claims ledger** — `notebook/_migrating.yaml`, reconstructed from the old README's prose
ledger. 23 claims, 3 migrated, 20 pending, each with its source section and destination page.

---

## 2. What was found wrong

In descending order of how much it blocks.

1. **`experiments/notebook_charts.py` does not exist, and eight of the nine builders named in
   `figures.yaml` still do not.** `AUTHORING.md` §4.2 and §4.4 both depend on modules that were
   never committed. The validator never noticed because it checks that the figure *file* exists,
   never that the builder does.

2. **`docs/prereg_punto7_simmetria_segno.md` does not exist.** `05-knob-or-cost.md` — the
   notebook's only confirmatory page — names it in front matter and links it in the body. The
   validator checks only that the field is non-null. The text appears to survive as a project
   note timestamped 2026-09-20 12:48 UTC, which is 14:48 Europe/Rome against the ~14:50 the
   document itself states. **Not restored**: putting back the record that underwrites a
   published `holds` claim is a decision for the author, not a repair.

3. **The order 01-then-02 could not be followed.** Page 01's evidence figures sample at
   RGB (154, 149, 139). They are light-theme, `AUTHORING.md` §4.4 requires regeneration rather
   than recolouring, and the generator does not exist, so `validate_notebook.py` would reject
   every one of them. Page 02's figures are already dark and already derived from data, so 02
   went first.

4. **`data/stage7_manifest.csv`, the declared source of F01.1 and F01.2, does not exist.**
   Candidates on disk: `stage7a_images.csv`, `stage7b_images.csv`, `style_features_stage7.csv`,
   `palette_features_stage7.csv`.

5. **The pitfall backlog is four entries, not eleven.** `errors_log.md` holds 1–63 with no gaps.
   `_pitfalls_44_47_da_inserire.md` and `_pitfalls_48_50_da_inserire.md` were merged some time
   ago and are now stale duplicates; only `_pitfalls_64_67_da_inserire.md` is pending.

6. **The self-test has 18 cases, not 20, and all 18 pass.** It also copies the whole 2.4 GB tree
   once per case — about 48 GB of I/O — although the validator reads only `notebook/`,
   `experiments/figures.yaml` and `assets/<page-id>/`. On a pruned tree the same suite runs in
   seconds and returns the identical 18/18. Every self-test result in this report was obtained
   that way; the full-tree run does not complete inside the session's command timeout.

7. **`data/punto7_blocks.csv` and `data/bench_checks.csv` have no producing script.** They are
   the only source of every published number on the two pages that were already live.

8. **Four images were scored twice during the blind headlight round**, two of them differently.
   The published rates reproduce exactly under "the later score wins" and under no other rule.
   That rule is now written into `headlights_by_style.py` and into page 02. It touches only the
   scrambled control at double strength (2/36 rather than 3/37).

9. **21 files in `data/` are named by no script and by no document** — and they are precisely
   the measurements behind the documents queued for pages 10 to 14. Those pages will hit rule 7
   the moment anyone writes them.

---

## 3. Left for the author

1. **Page 02's status.** Filed `ambiguous` / `exploratory`. No threshold was frozen before
   either arm, the barnacle round was scored with the condition visible, the headlight round is
   blind but measures on the renders that produced the observation, and the pre-registered
   confirmation was never run. The contract forbids `holds` on an exploratory page. The
   reasoning is on the page; the judgement is still a judgement.
2. **Restoring `docs/prereg_punto7_simmetria_segno.md`.**
3. **Merging pitfalls 64–67** and removing the two stale staging files.
4. **`.git/_stale_locks/`** — git lock files and temporary objects this session could not
   unlink, because deletion is denied in the connected folder. Inert, and safe to delete.

## 4. Where to restart

In this order, because each unblocks the next.

1. **Write `experiments/notebook_charts.py`** with the three statistical builders page 05
   already claims (`knob_vs_cost_scatter`, `depth_profile`, `rectification_bars`) reading
   `data/punto7_blocks.csv`, and the palette §4.4 declares. This regenerates three of the eight
   existing figures from their measurement file for the first time.
2. **Add two checks to `validate_notebook.py`**: every non-null `builder` resolves to a callable,
   and `preregistration` resolves to a file on disk. Both will be red on the current tree — that
   is the point — so land them together with the two fixes above.
3. **Page 03**, not page 01: `assets/03_what_ends_up_in_the_picture/_figures` already holds three
   finished dark figures, `prereg_stage12_ingrandimento.md` is a real pre-registration that was
   executed, and the source text is lines 1128–1218 of `c843d61:README.md`. It is the cheapest
   confirmatory page left.
4. **Page 01** once a figure generator exists, or with the light-theme figures dropped and the
   page written around F01.1 and F01.2 rebuilt from `stage7a/b_images.csv`.

The old README is recovered with `git show c843d61:README.md`. Nothing else in the working tree
contains it.


---

## 5. The second pass — page 03, and three things it turned up

**Page 03 is live and filed `holds` / `confirmatory`**, which makes it the second genuinely
confirmatory page in the notebook. `docs/prereg_stage12_ingrandimento.md` was deposited before a
single render and, unlike the attribute-emergence pre-registration, it was actually executed —
both of it, including experiment 12-B with its threshold of five joint hits in twenty fixed in
advance.

**`experiments/notebook_charts.py` now exists too**, with three builders that read a measurement
file and derive their own titles and annotations from it. Together with `notebook_figures.py`
that closes most of §0 item 3: the two modules the contract has named since it was written are
no longer fiction. What remains missing is `extract_repro.py` and the eight builders that the
figures of pages 00 and 05 name, which is why those eight figures still cannot be regenerated.

### 5.1 A published verdict that does not reproduce

`docs/stage12_verifica.md` §5 reports the stage-12 primary test failing under the statistic it
calls the most defensible — the mean of the per-prompt log ratios — at 0.0176 raw and 0.0527
after Holm, and concludes "confirmed with reservation".

Two independent recomputations here, one in plain Python and one in numpy, give **0.0117 raw**
(12 of the 1024 sign patterns, not 18) and **0.0352 after Holm**. That is also precisely what
`data/stage12_bbox_results.csv` has recorded since the round was run, beside its own verdict of
`CONFERMATO`. Duplicate handling does not move it; one- versus two-tailed does not produce
0.0176 either.

All four readings of the registered statistic pass after correction — 0.0352, 0.0234, 0.0293,
0.0176 — so the reservation that survives is not "one statistic fails" but "the
pre-registration named the test and not the statistic". Page 03 says that in the open, in *Why
I might be wrong*. The whole table is in `data/stage12_enlargement_tests.csv`;
`python experiments/stage12_enlargement_by_prompt.py` rebuilds it. **If the 0.0527 does
reproduce by some route not tried here, that claim goes back to `ambiguous`.**

### 5.2 Fifty renders that were never looked at, and a confirmation sitting inside them

The stage-12 batch is 250 renders across five conditions; the bounding-box round annotated four
of them. The 50 renders of `preset_pos_1x` were never scored.

They are not a spare arm. The pre-registration registers a **second confirmatory hypothesis** on
that same corpus — the headlight confirmation, with its own frozen directional prediction and
its own clause about a wrong sign counting as failure — and it required exactly that fifth
condition. No headlight scoring file for stage 12 exists in `data/`.

Page 02's headlight claim is currently `ambiguous` precisely because it quantifies an
observation on the renders that produced it. The confirmation it needs is a scoring pass over
images **that already exist on disk**. No new generation, which is the constraint that was set.
This is the cheapest upgrade available anywhere in the notebook.

### 5.3 Two numberings in the error log, and I fell into it

`docs/errors_log.md` carries the fifteen methodological rules at the top and the 63-entry
pitfall registry below. The prose documents write "rule 8" and "rule 10" meaning the first; page
02's front matter recorded them as pitfalls 8 and 10, which are "CLIP adherence computed against
`prompt_tag`" and "round-trip sentinel composition" — two entries with no bearing on that page.
Fixed in `f0fb0a2`, with every reference checked one at a time against the registry.

The corrected list turned out better than the original: **pitfall 35 is literally that round.**
Its registry entry reads "a scoring viewer that appends a row when the scorer goes back to
correct — 284 rows for 280 images: four re-scores, two with a changed verdict", and prescribes
"key on the item id and keep the last entry". That is the rule derived from the data on the
first pass, before the entry was read. And **pitfall 34 is page 03's own result**, quoted in the
registry with the 17-of-20 and 12-of-20 figures.

### 5.4 Numbers that had no file, now persisted

Three tables written by `experiments/stage12_enlargement_by_prompt.py`, all reproducing the
prose write-ups to the digit:

- `data/stage12_enlargement_by_prompt.csv` — 30 per-prompt ratios crossed with the per-style
  discriminability;
- `data/stage12_enlargement_tests.csv` — four statistics × three conditions, exact sign-flip p
  over all 1024 patterns, and Holm;
- `data/stage12_annotator_noise.csv` — test-retest from the 20 hidden duplicates (0.27 points of
  canvas, r = +0.995) and the disturbance regression over the 50 original baselines (saturation
  r = −0.096, p = 0.50).

### 5.5 Where to restart, revised

1. **Score the 50 `preset_pos_1x` renders** for headlights and run the registered stage-12
   confirmation. It upgrades page 02 and costs no generation.
2. **Write the eight missing builders** in `notebook_charts.py` and `notebook_figures.py` for the
   figures of pages 00 and 05, following the four now in place.
3. **Add the two validator checks**: every non-null `builder` resolves to a callable, and
   `preregistration` resolves to a file. The second is red today because of page 05.
4. **Page 06**, the hatching axis: a real executed pre-registration
   (`prereg_hatching_axis_stage7.md`), source text at lines 681–803 of `c843d61:README.md`,
   measurements in `data/style_features_stage7.csv`. Page 01 stays blocked on its light-theme
   figures.


---

## 6. Third pass — page 06, and four defects the restored documents exposed

The pre-registration of page 05 is back in the repository, the stage-12 headlights have been
scored, and page 06 is live. Each of those turned up something.

### 6.1 The eight predictions of page 05 are now checkable, and one row was wrong

With `docs/prereg_punto7_simmetria_segno.md` restored, every row of page 05's prediction table
was recomputed from `data/punto7_blocks.csv` against the frozen §3. Seven reproduce exactly.
The eighth, P2, named the **swing** `s` where the pre-registration names the **specularity**
`m`. The verdict was always the specularity one — 17 of 28 blocks mirror-symmetric within 3σ,
which falsifies it — but under `s` the same window holds 8 blocks and nothing would have been
falsified. The table contradicted its own outcome. Corrected, and `m` added to the
decomposition, which listed only `c` and `s` while testing `m`.

The validator now checks that the file named in `preregistration` exists. That is exactly the
hole that let a confirmatory page ship for a day citing a document that had never been
committed. The self-test went from 18 to 19 cases.

### 6.2 The stage-12 headlight confirmation ran, and could not resolve anything

Not because the effect is absent: **nine of the ten styles never light a headlight in any
condition, the untouched model included.** All sixteen lit renders belong to one style. With one
informative prompt the exact sign-flip floor is 2/2¹ = 1.0, so no effect of any magnitude could
have reached significance — decidable from the prompt before rendering, since the subject
sentence pins `golden hour, clear sky`.

Inside the one informative style the arms behave as predicted and cannot be tested: the
untouched model lights 5 of 5, so the positive arm has no room, and the derangement takes it to
3 of 5 and then 1 of 5. Page 02's headlight claim therefore stays `ambiguous` — it gains a
boundary rather than a confirmation, and the round that would settle it needs a corpus where
headlights are **marginal**, chosen on that criterion before rendering.

The scoring itself is sound: every tile re-joins to the sealed key without a disagreement,
19 of 20 re-shown tiles scored identically, and the sensitivity the criterion promised and did
not deliver (excluding the 27 tiles seen before the criterion was tightened) changes nothing.

### 6.3 Page 06 reports a primary that failed, and a check that was never recorded

The hatching axis is the cleanest confirmatory result in the notebook — two families at the
exact permutation floor, 16 prompts of 16, 80 pairs of 80 and 79 of 80, effect sizes holding
across an independent corpus to within five per cent. Three things had to be said alongside it:

1. **The primary was a conjunction over three families and it was not met.** Two of three. The
   page says so as the first sentence of its verdict.
2. **One row of the published table is counted on a different rule from the others.** The sign
   scramble's "11/16 prompts, 50/80 pairs" counts agreement with its *observed* sign while the
   rows above it count agreement with the *predicted* one. Under the same rule it is 5/16 and
   30/80.
3. **A pre-registered validity check has no recorded outcome.** The pre-registration licenses
   `crosshatch_entropy_mean` as a stand-in for what the eye saw on the derangement family only,
   states that the preset family "has not been checked against the eye", schedules an
   inspection of one pair before the analysis, and says the preset row is *withdrawn in
   writing* if the check fails. The outcome is not in the document or anywhere in `docs/`. The
   preset claim is filed `ambiguous` for that reason alone; one look at one pair closes it.

### 6.4 The pitfall registry is merged and contiguous

64 to 67 are in `errors_log.md`, which now runs 1 to 67 with no gaps, and the two counts inside
the document were updated. The four new rows are **not** placed in the invariant families —
that is taxonomy, not transcription — and a suggested placement is written at the head of the
table for the author to confirm or replace. All three `_da_inserire` files carry a MERGED
banner; they still need deleting by hand.

### 6.5 Where to restart, revised again

1. **Look at one `preset_pos` / `preset_neg` pair** and record what you see. It is the cheapest
   open item in the notebook and it decides a published claim's status.
2. **Page 07, chromatic signatures** — the third pre-registration on the same 560 renders,
   verdict ambiguous and to be written as ambiguous, source text at lines 567–680 of
   `c843d61:README.md`, measurements in the `data/palette_*` family.
3. **The eight missing builders** for the figures of pages 00 and 05, then the validator check
   that a `builder` resolves to a callable.
4. **A corpus where headlights are marginal**, if the headlight claim is worth confirming.
5. Page 01 stays blocked on its light-theme figures.
