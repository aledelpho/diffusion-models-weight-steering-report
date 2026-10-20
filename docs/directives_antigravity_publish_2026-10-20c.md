# Directive for Antigravity — third publish round of 2026-10-20 (after the export error)

Follow **`docs/directives_antigravity_publish_results.md`** (the reusable publish directive), Steps 1–5, exactly, from
Step 1 again. Notes for this round:

* Round b stopped at Step 3: page 31 linked `../docs/prereg_domain_specificity.md`, which the export does not rewrite
  (`docs/PUBLISH_2026-10-20b.md`). Fixed in 859084f: the path is now written in backticks, as on the other pages.
* Claude ran on 2026-10-20, after the fix: `build_notebook.py --dir results --check` `up to date` (12 pages, 78
  claims); `validate_notebook.py --dir results` `PASS -- 0 error(s)`; and a test export of HEAD with
  `--allow-unpushed` to a scratch folder: `PASS -- every link and image resolves; no '../' left; every cited data file
  present`.
* New commits since round b's push: the fix, the C107 pre-registration and script, and this directive (plus the C107
  render report, if it is committed first). Pushing them is expected.
* Expected untracked or modified files, to leave alone and list in the paste-back: `Claude outputs/`,
  `docs/te_traits_list_bozza.csv`, `docs/PUBLISH_2026-10-20.md`, `docs/PUBLISH_2026-10-20b.md`,
  `docs/directives_antigravity_publish_2026-10-20.md` (one-line change, not to be committed).
* `*.stale.<number>` files under `.git` are old lock files moved aside; leave them.
* Hard rules as always: no renders in this directive, do not close or shut down anything, no force push, no history
  rewriting, do not edit any page.

Paste back into `docs/PUBLISH_2026-10-20c.md`: the commands and outputs of every step, the `<SHA>`, and the two site
checks (page 31 should appear in the page list of both sites). Do not commit that file.
