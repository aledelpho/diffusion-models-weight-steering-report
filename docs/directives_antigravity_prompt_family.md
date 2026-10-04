# Directives for Antigravity — C49 prompt family bench (launch only)

Written by Claude on 2026-10-04. **Alessandro authorises Antigravity to queue these 433
renders.** Design: `docs/prereg_prompt_family.md`. The plan is already committed
(`data/prompt_family_plan.csv`); all code is Claude's.

## Hard rules

1. Do not write or modify any script, plan or document, except the RENDERS doc in step 6.
2. Never use `monitor_and_shutdown.py`; do not shut down, sleep or close anything.
3. Do not analyse or interpret; do not run `analyze_prompt_family.py`.
4. If an output does not match what is written here, stop and report.
5. Commits in Italian, only your file, no push; `python experiments/validate_notebook.py`
   (0 errors) before the commit.

## Steps

1. `python experiments/prompt_family.py --queue --first 1` — the REPRO row only. Wait for the file.
2. `python experiments/prompt_family.py --repro` — must print `REPRO PASS max abs diff 0`. If not, stop.
3. `python experiments/prompt_family.py --queue` — the other 432. Wait for the ComfyUI queue to
   empty by polling `/queue`.
4. `python experiments/prompt_family.py --count` — must print `expected 433 missing 0 ... duplicates 0`.
5. `python experiments/build_prompt_family_eye_page.py` — builds the eye page (no numbers).
6. Write `docs/RENDERS_2026-10-04_prompt_family.md`: commands and raw outputs of steps 2, 4, 5.
   Commit it. Report to Alessandro and stop.
