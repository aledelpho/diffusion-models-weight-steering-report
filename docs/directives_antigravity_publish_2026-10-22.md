# Directive for Antigravity — publish round of 2026-10-22

Follow **`docs/directives_antigravity_publish_results.md`** (the reusable publish directive), Steps 1–5, exactly. Notes
for this round:

* New since the last round: C107 and C108 (pre-registrations, renders reports, keys, labels, results), page 31 extended
  with them (figures F31.7–F31.9, four new claims), STORY section 11, and a fix to `validate_notebook.py` (hyphenated
  words such as "non-binary" count as one word). About 14 commits, this directive included.
* Claude ran Step 1 on 2026-10-22: `build_notebook.py --dir results --check` `up to date` (12 pages, 82 claims),
  `build_notebook.py --check` `up to date` (14 pages); both `validate_notebook.py` runs `PASS -- 0 error(s)`; a test
  export of HEAD with `--allow-unpushed`: `PASS -- every link and image resolves; no '../' left; every cited data file
  present`.
* Expected untracked or modified files, to leave alone and list in the paste-back: `Claude outputs/`,
  `docs/te_traits_list_bozza.csv`, `docs/PUBLISH_2026-10-20.md`, `docs/PUBLISH_2026-10-20b.md`,
  `docs/PUBLISH_2026-10-20c.md`, `docs/directives_antigravity_publish_2026-10-20.md` (one-line change, not to be committed).
* `*.stale.<number>` files under `.git` are old lock files moved aside; leave them.
* Hard rules as always: no renders, do not close or shut down anything, no force push, no history rewriting, do not
  edit any page.

Paste back into `docs/PUBLISH_2026-10-22.md`: the commands and outputs of every step, the `<SHA>`, and the two site
checks (page 31 should show F31.7–F31.9). Do not commit that file.
