# Directive for Antigravity — C64 text-encoder pilot

Authorised by Alessandro on 2026-10-11. 463 renders (~4 h 30 min): an evening or a night. Do not shut down or
close anything; do not use `monitor_and_shutdown.py`; do not change power or system settings.

ComfyUI must be running (StabilityMatrix), with the Arthemy Krea2 Tuner loaded as for every bench. In a terminal:

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_pilot.py --queue --checks
```

Wait for the 7 images (about 4 minutes), then:

```powershell
python te_pilot.py --check
```

**Only if it prints `CHECK PASS`:**

```powershell
python te_pilot.py --queue
```

(The `structure:` part of the line is information, not a gate: paste it whatever it says.)

When ComfyUI's queue is empty:

```powershell
python te_pilot.py --count
```

It must print `expected 463 missing 0`. If files are missing (the PC slept, ComfyUI stopped), run
`python te_pilot.py --queue` again — it skips what exists — and `--count` once more.

Write the outputs of the commands, as printed, to `docs/RENDERS_2026-10-11_te_pilot.md` (same layout as the
earlier RENDERS notes) and commit only that file:

```powershell
git add docs/RENDERS_2026-10-11_te_pilot.md
git commit -m "C64: note dei render (463)"
```

If `--check` prints FAIL: stop, queue nothing else, write the output to the same file and tell Alessandro.
Do not push in this step.
