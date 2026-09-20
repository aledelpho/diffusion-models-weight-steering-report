# Night report — 2026-09-21

Session 22:25–00:5x UTC, autonomous, on `main`. Four commits, **no push**. Working tree clean,
`validate_notebook.py` at 0 errors, the self-test at 18/18.

```
0ab9261  docs: il registro delle claim, e l'inventario aggiornato
aadf9fa  feat(notebook): capitolo 02 - attribute emergence, e il primo builder vero
ed709c3  fix(figure): l'alt di F05.3 pubblicava il 12,4x ritrattato
4d066c6  docs: inventario misurato del notebook prima della migrazione
```

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
