# Directive for Antigravity — C61 cost floor (page 05)

Authorised by Alessandro on 2026-10-07. 913 renders (~8 h 40 min at 34 s): a night. Do not shut down or close
anything; do not use `monitor_and_shutdown.py`; do not change power or system settings.

ComfyUI must be running (StabilityMatrix). Then, in a terminal:

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python cost_floor_test.py --queue --checks
```

Wait for the image (about 35 s), then:

```powershell
python cost_floor_test.py --check
```

**Only if it prints `CHECK PASS`** (diff 0):

```powershell
python cost_floor_test.py --queue
```

When ComfyUI's queue is empty:

```powershell
python cost_floor_test.py --count
```

It must print `expected 913 missing 0`. Write the outputs of the four commands, as printed, to
`docs/RENDERS_2026-10-08_cost_floor.md` (same layout as `docs/RENDERS_2026-10-07_comic_form.md`) and commit
only that file:

```powershell
git add docs/RENDERS_2026-10-08_cost_floor.md
git commit -m "C61: note dei render (913, check PASS)"
```

If `--check` prints FAIL: stop, queue nothing else, write the output to the same file and tell Alessandro.
If the night ends before the queue does, run `--count`, write it down, and `--queue` again later: it skips what
exists. Do not push.
