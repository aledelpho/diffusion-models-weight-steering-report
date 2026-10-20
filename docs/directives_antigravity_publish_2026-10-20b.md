# Directive for Antigravity — second publish round of 2026-10-20

Follow **`docs/directives_antigravity_publish_results.md`** (the reusable publish directive), Steps 1–5, exactly. Notes
for this round:

* The first round of today is done (`docs/PUBLISH_2026-10-20.md`, untracked, leave it). Since then the main repository
  has new commits: C106 (pre-registration, labels, result) and the new results page **31 · What a text-encoder edit
  leaves** (figures F31.1–F31.6, STORY section 11, README), plus this directive.
* Claude ran Step 1 on 2026-10-20 after the page: `build_notebook.py --dir results --check` says `up to date` (12 pages,
  78 claims), `build_notebook.py --check` `up to date` (14 pages); `validate_notebook.py --dir results` and
  `validate_notebook.py` both `PASS -- 0 error(s)`.
* In Step 5, the results site should now list page 31 in the page list and `prompts.html` should still show sections
  20 to 30 (page 31 adds no new prompts section unless the build added one: report what you see).
* Expected untracked or modified files, to leave alone and list in the paste-back: `Claude outputs/`,
  `docs/te_traits_list_bozza.csv`, `docs/PUBLISH_2026-10-20.md`, `docs/directives_antigravity_publish_2026-10-20.md`
  (one-line change, not to be committed).
* Many files named `*.stale.<number>` under `.git` are old lock files moved aside; leave them.
* Hard rules as always: no renders, do not close or shut down anything, no force push, no history rewriting. Do not
  edit any page.

Paste back into `docs/PUBLISH_2026-10-20b.md`: the commands and outputs of every step, the `<SHA>`, and the two site
checks. Do not commit that file.
