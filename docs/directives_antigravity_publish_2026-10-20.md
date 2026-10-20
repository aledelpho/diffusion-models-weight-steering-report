# Directive for Antigravity — publish round of 2026-10-20

Follow **`docs/directives_antigravity_publish_results.md`** (the reusable publish directive), Steps 1–5, exactly. Notes
for this round:

* The main repository is 85 commits ahead of `origin/main`, this directive included (C93–C105, TEP2, the move to D:). Claude ran Step 1 on
  2026-10-20: both `--check` say `up to date` (14 and 11 pages), both validations `PASS -- 0 error(s)`.
* Expected untracked files, to leave alone and list in the paste-back: `Claude outputs/`, `docs/te_traits_list_bozza.csv`.
* Many files named `*.stale.<number>` under `.git` are old lock files moved aside; leave them.
* StabilityMatrix now lives on `D:\StabilityMatrix-win-x64`; nothing in the publish steps needs it.
* The results pages do not yet describe C93–C105: this round publishes the repository (docs, data, scripts) as it is.
  Do not edit any page.
* Hard rules as always: no renders, do not close or shut down anything, no force push, no history rewriting.

Paste back into `docs/PUBLISH_2026-10-20.md`: the commands and outputs of every step, the `<SHA>`, and the two site
checks. Do not commit that file.
