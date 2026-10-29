# Directive for Antigravity — publish round of 2026-10-29

Follow **`docs/directives_antigravity_publish_results.md`** (the reusable publish directive), Steps 1–5, exactly. Notes
for this round:

* New since the last round (about 87 commits, this directive included): MOSS-Image work (paused), Block Studio and the
  Split Mixer, C109 and C111–C115 (pre-registrations, render reports, keys, labels, corrections, results), **new
  results page 32** (`results/32-an-edit-as-a-switch.md`, figures F32.1–F32.8, nine claims), STORY section 12 (old 12
  and 13 renumbered 13 and 14), README (abstract, introduction, pages 31 and 32 in the table), pitfalls 95–96, and two
  fixes to the blind-page builder (`eye_grid_page.py`).
* Claude ran Step 1 on 2026-10-29: `build_notebook.py --dir results --check` `up to date` (13 pages, 91 claims),
  `build_notebook.py --check` `up to date` (14 pages); `validate_notebook.py --dir results` and `validate_notebook.py`
  both `PASS -- 0 error(s)`; a test export of HEAD with `--allow-unpushed`: `PASS -- every link and image resolves; no
  '../' left; every cited data file present` (16 pages, 226 data files).
* Expected untracked or modified files, to leave alone and list in the paste-back: `Claude outputs/`,
  `analyze_saturation.py`, `docs/te_traits_list_bozza.csv`, `docs/PUBLISH_2026-10-20*.md`, `docs/PUBLISH_2026-10-22.md`,
  `experiments/watchdog_moss_atlas_shutdown.py`, `scratch/fig32_snippet.py`, `scratch/story12.md`,
  `docs/directives_antigravity_publish_2026-10-20.md` (one-line change, not to be committed).
* `*.stale.<number>` files under `.git` are old lock files moved aside; leave them.
* Hard rules as always: no renders, do not close or shut down anything, no force push, no history rewriting, do not
  edit any page.

Paste back into `docs/PUBLISH_2026-10-29.md`: the commands and outputs of every step, the `<SHA>`, and the two site
checks (page 32 should show F32.1–F32.8; the story should show section 12). Do not commit that file.
