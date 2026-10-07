# Directive for Antigravity — C60 comic form test

Authorised by Alessandro on 2026-10-07. 191 renders (~1 h 50 min at 34 s). Do not shut down or close
anything; do not use `monitor_and_shutdown.py`; do not change power or system settings.

ComfyUI must be running (StabilityMatrix). Then, in a terminal:

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python comic_form_test.py --queue --checks
```

Wait for the two images (about 70 s), then:

```powershell
python comic_form_test.py --check
```

**Only if it prints `CHECK PASS`** (both diffs 0):

```powershell
python comic_form_test.py --queue
```

When ComfyUI's queue is empty:

```powershell
python comic_form_test.py --count
```

It must print `expected 191 missing 0`. Write the outputs of the four commands, as printed, to
`docs/RENDERS_2026-10-07_comic_form.md` (same layout as `docs/RENDERS_2026-10-07_split_atlas.md`) and commit
only that file:

```powershell
git add docs/RENDERS_2026-10-07_comic_form.md
git commit -m "C60: note dei render (191, check PASS)"
```

If `--check` prints FAIL: stop, queue nothing else, write the output to the same file and tell Alessandro.
Do not push.
