# Directive for Antigravity — push the main repository, then publish the results repository

2026-10-05. Written by Claude for Alessandro. **No renders. Do not shut down or close anything.
Do not use `monitor_and_shutdown.py`.** If any step fails, stop and paste the output; do not
improvise a workaround (no force push, no rewriting history, no deleting files).

## Step 1 — push the main repository as it is

Only what is already committed goes online. Uncommitted files stay where they are.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report
git status --short
git push origin main
```

- Do **not** run `git add` of any kind before pushing (no `git add .`, no `git add -A`). The
  untracked files and the four modified files (`data/single_blocks_styles_plan.csv`,
  `experiments/build_annotation_page.py`, `experiments/make_single_blocks_styles_plan.py`,
  `experiments/monitor_single_blocks_styles.py`) are **not** part of this push; deciding about
  them is Alessandro's.
- If the push is rejected (non-fast-forward, size limit, anything): stop and paste the output.
  **Never** `--force`.
- If `.git/index.lock` or `HEAD.lock` exist and git refuses to run, delete only those lock files.

## Step 2 — record the commit the results will point to

```powershell
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
```

The two shas must be identical. That full 40-character sha is `<SHA>` below.

## Step 3 — build the results repository folder

```powershell
python experiments\export_results_repo.py --sha <SHA> --out C:\Users\aless\Desktop\<REPO_NAME>
```

It must end with `PASS -- every link and image resolves ...`. If it prints any `ERROR`, stop and
paste the output. Do not edit the exported files by hand; do not add files to the folder.

## Step 4 — create the repository on GitHub and push it

Name and visibility are Alessandro's choice (suggested name: `krea2-weight-knobs-results`).

```powershell
cd C:\Users\aless\Desktop\<REPO_NAME>
git init -b main
git add .
git commit -m "Results: single-block weight scaling in Krea-2 (pages 20-27), linked to the main repository at <SHA short>"
```

Create the empty repository on GitHub (no README, no licence, no .gitignore — the folder already
has them), then:

```powershell
git remote add origin https://github.com/aledelpho/<REPO_NAME>.git
git push -u origin main
```

Do not add GitHub Actions or any other file. (GitHub Pages: see step 5 of the update section, and
only that.)

## Step 5 — paste back to Claude

1. The output of `git push origin main` (step 1).
2. The `<SHA>` of step 2.
3. The full output of the export script (step 3).
4. The URL of the new repository.

## Updating the results repository (every later round)

1. In the main repository: `git push origin main`, then `git fetch origin` and take the new
   `<SHA>` exactly as in steps 1–2 (same rules: no `git add`, never `--force`).
2. Export into a **new, empty** temporary folder:
   `python experiments\export_results_repo.py --sha <SHA> --out C:\Users\aless\Desktop\_results_export`
   It must print `PASS`.
3. In `C:\Users\aless\Desktop\krea2-weight-knobs-results`: delete every tracked file except the
   `.git` folder (`git rm -r -q .`), copy in the whole content of `_results_export`, then
   `git add .`, `git commit -m "Update to main repository <SHA short>"`, `git push`.
4. Delete `_results_export`. Paste back the push output, `<SHA>` and the export output.
5. **Once only — GitHub Pages for the public blind test** (authorised by Alessandro on 2026-10-05,
   for `try-the-test.html`). In the results repository on GitHub: Settings → Pages → Build and
   deployment → Source: *Deploy from a branch*, Branch: `main`, folder `/ (root)`, Save. No
   Actions, no custom domain, no theme. The export already writes an empty `.nojekyll`, so the files
   are served as they are. After a minute, open
   https://aledelpho.github.io/krea2-weight-knobs-results/try-the-test.html, click "No, start the
   test" and check that the first two portraits appear. Paste back whether they do. Do not answer
   the test.
