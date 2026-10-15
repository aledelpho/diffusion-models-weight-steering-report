# Directive for Antigravity — publish the notebook and the results pages (reusable)

Written by Claude for Alessandro, 2026-10-11. Use it for every publish round from now on. **No renders. Do not
shut down or close anything. Do not use `monitor_and_shutdown.py`.** If any step fails, stop and paste the
output; no force push, no rewriting history, no deleting files other than git lock files.

Two sites are updated:

* the **main repository** — notebook and `results/` pages — at
  https://aledelpho.github.io/diffusion-models-weight-steering-report/ (updated by the push in step 2);
* the **results repository** `krea2-weight-knobs-results` — the stand-alone results site with the blind test — at
  https://aledelpho.github.io/krea2-weight-knobs-results/ (updated by steps 3-4).

## Step 1 — check that the pages are built

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report
git status --short
python experiments\build_notebook.py --check
python experiments\build_notebook.py --dir results --check
python experiments\validate_notebook.py
python experiments\validate_notebook.py --dir results
```

Both `--check` runs must say `up to date`, both validations `PASS -- 0 error(s)`. If a `--check` says the
outputs are out of date, **do not rebuild them yourself**: stop and paste, Claude regenerates and commits them.

## Step 2 — push the main repository as it is

```powershell
git push origin main
```

* No `git add` of any kind before pushing; untracked or modified files stay as they are — list them in the
  paste-back.
* If `.git\index.lock` or `.git\HEAD.lock` exist and git refuses to run, delete only those lock files.
* Rejected push: stop and paste. Never `--force`.

Then:

```powershell
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
```

The two must be identical; that 40-character sha is `<SHA>`.

## Step 3 — export the results site

```powershell
python experiments\export_results_repo.py --sha <SHA> --out C:\Users\aless\Desktop\_results_export
```

It must end with `PASS`. Do not edit the exported files.

## Step 4 — update the results repository

```powershell
cd C:\Users\aless\Desktop\krea2-weight-knobs-results
git rm -r -q .
```

Copy the whole content of `C:\Users\aless\Desktop\_results_export` into this folder (including `.nojekyll`),
then:

```powershell
git add .
git status --short
git commit -m "Update to main repository <SHA short>"
git push
```

Delete `C:\Users\aless\Desktop\_results_export`. GitHub Pages is already on for both repositories; change
nothing in the settings.

## Step 5 — check both sites (after one or two minutes)

1. https://aledelpho.github.io/diffusion-models-weight-steering-report/results/index.html — the "Start here" list
   must include **FAQ: what I learned, for everyone** and must no longer include a blind-test link.
2. https://aledelpho.github.io/krea2-weight-knobs-results/ — the same check; then open
   https://aledelpho.github.io/krea2-weight-knobs-results/faq.html and confirm it loads. Then open
   https://aledelpho.github.io/krea2-weight-knobs-results/prompts.html (2026-10-15): it must load and show
   "The prompts" with sections 20 to 30; "Start here" must list **Every prompt, in full**.
3. https://aledelpho.github.io/krea2-weight-knobs-results/try-the-test.html — must now give **404** (the blind
   test is no longer published, 2026-10-14). Do not delete anything by hand to obtain this: step 4 already does it.

## Step 6 — paste back

The outputs of steps 1 and 2 (`git push`, `<SHA>`), the full output of the export, the output of the results
push, and the result of the checks in step 5.
