# Directive for Antigravity — C63 clean six

Authorised by Alessandro on 2026-10-11. 109 renders (~1 h at 34 s). Do not shut down or close anything; do not
use `monitor_and_shutdown.py`; do not change power or system settings.

ComfyUI must be running (StabilityMatrix). In a terminal:

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python clean_six_test.py --queue --checks
```

Wait for the image (about 35 s), then:

```powershell
python clean_six_test.py --check
```

**Only if it prints `CHECK PASS`** (diff 0):

```powershell
python clean_six_test.py --queue
```

When ComfyUI's queue is empty:

```powershell
python clean_six_test.py --count
```

It must print `expected 109 missing 0`. If it prints missing files (for example because the PC slept), run
`python clean_six_test.py --queue` again — it skips what exists — and `--count` once more.

Write the outputs of the commands, as printed, to `docs/RENDERS_2026-10-11_clean_six.md` (same layout as
`docs/RENDERS_2026-10-07_comic_form.md`) and commit only that file:

```powershell
git add docs/RENDERS_2026-10-11_clean_six.md
git commit -m "C63: note dei render (109, check PASS)"
```

If `--check` prints FAIL: stop, queue nothing else, write the output to the same file and tell Alessandro.
Do not push in this step (the publish directive is separate).
