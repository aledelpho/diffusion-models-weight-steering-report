# Directive for Antigravity — publish round of 2026-10-11

Written by Claude for Alessandro. **No renders. Do not shut down or close anything. Do not use
`monitor_and_shutdown.py`.** If any step fails, stop and paste the output; no force push, no rewriting
history, no deleting files other than git lock files.

What goes online: every commit up to and including the C63 pre-registration (about 55 commits since the last
push, C53-C63), among them the new results page 29 (inside a block: attention against MLP) and the replication
note on notebook page 05.

## Step 1 — push the main repository as it is

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report
git status --short
git push origin main
```

* No `git add` of any kind before pushing. Untracked or modified files stay as they are; listing them in the
  paste-back is enough.
* If `.git\index.lock` or `.git\HEAD.lock` exist and git refuses to run, delete only those lock files.
* Rejected push (non-fast-forward, size, anything): stop and paste. Never `--force`.

## Step 2 — the commit the results point to

```powershell
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
```

The two must be identical; that 40-character sha is `<SHA>`.

## Step 3 — update the results repository

Exactly as in "Updating the results repository" of `docs/directives_antigravity_publish.md`:

```powershell
python experiments\export_results_repo.py --sha <SHA> --out C:\Users\aless\Desktop\_results_export
```

It must print `PASS`. Then in `C:\Users\aless\Desktop\krea2-weight-knobs-results`:

```powershell
git rm -r -q .
```

copy in the whole content of `_results_export`, then:

```powershell
git add .
git commit -m "Update to main repository <SHA short>: page 29, inside a block"
git push
```

Delete `_results_export`. GitHub Pages is already on; nothing to change there.

## Step 4 — paste back

1. The output of `git push origin main`.
2. `<SHA>`.
3. The full output of the export script.
4. The output of the results-repository push, and whether
   https://aledelpho.github.io/krea2-weight-knobs-results/ now lists page 29.
