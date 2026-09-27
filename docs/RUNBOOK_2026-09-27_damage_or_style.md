# Runbook — damage or style? The judge on `benchmark_mappa`

- **For:** the agent with ComfyUI and Ollama attached over API.
- **Governed by:** [`prereg_damage_or_style.md`](prereg_damage_or_style.md), frozen before any call.
- **Generates no render.** Every image it needs already exists on disk.
- **Runs unattended.** There is no step that waits for a human. Where something is wrong, the
  instruction is always *record it and carry on*, never *stop and ask*.

---

## 0. Standing constraints — these override anything convenient

- **Do not generate renders.** Not one. Alessandro launches every render; this study reads PNGs.
- **Do not write anything under `notebook/`.** No page, no claim, no status.
- **Do not change the status of any published claim.** If a result bears on one, say so in the
  report and leave the claim alone.
- `python experiments/validate_notebook.py` must print **0 errors** before every commit.
- Commit messages in **Italian**, small and descriptive. Everything that enters the repository is in
  **English**. **Do not push.**
- Do not shut down the PC and do not close anything. Do not run `monitor_and_shutdown.py`.
- After every commit: `del .git\*.lock` and remove any `.git\tmp_obj_*`, so the working tree is not
  left locked.

## 1. What this study is for, in one paragraph

Every measurement so far says **how far** a block edit moves the image. None says **where it lands**.
At dose 0.200 the image has moved 83–101 % of the way to a different seed — and a distance cannot
distinguish *ruined* from *restyled*. Damage is idiosyncratic; a style is reproducible. So the study
asks two questions of a judge: is the perturbed image defective (Arm A), and does the same edit
applied to a **different prompt and seed** produce a recognisably related image (Arm B). Arm B is
the one that decides, and its foil is matched in displacement magnitude so that it cannot be
answered by picking whichever candidate is equally broken.

## 2. Preconditions — check, record, continue

```bat
ollama list
curl http://127.0.0.1:11434/api/tags
dir "C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_mappa\renders" | find /c ".png"
```

Expect `qwen3.8:27b` present and **519** PNGs. `gemma4:31b` has no vision projector — do not use it,
and do not report an attempt with it as a failure of the judge.

If Ollama is unreachable: write `docs/report_damage_or_style.md` saying so, commit, and stop. That
is a complete outcome.

## 3. Step 1 — the multi-image gate. **Blocking.**

Every previous judge call in this project sent **one** image. This study sends two or three. That
the judge addresses them as separate images is **not** established and must not be assumed.

```bat
python experiments\judge_pairs_gate.py ^
  --renders "C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_mappa\renders" ^
  --model qwen3.8:27b
```

**54 calls** (Amendment 01). Three probes with certain ground truth — saturation, sharpness,
added noise — each on **all nine** baselines in both orders. Output: `data/damage_style_gate.csv`. The script prints PASS or FAIL and
exits 2 on failure.

**If the gate fails, the failure is the result.** Do **not**:

- reword the questions until it passes;
- try model after model and report only the one that passed;
- lower the thresholds of the pre-registration §4 — they were fixed before any call existed;
- resize or crop the images. Native 1024 × 1280, whole.

On failure: write the report from the gate CSV, commit, stop. Do not run step 2.

One nuance the script encodes: the three probes are scored **separately**. If only the
`degradation` probe fails, Arm A is void and **Arm B may still be run** — Arm B never asks the judge
to rank quality, only to match a treatment. Record that decision explicitly in the report if it
happens.

## 4. Step 2 — the run. 468 calls, resumable.

```bat
python experiments\judge_damage_style_run.py ^
  --renders "C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_mappa\renders" ^
  --model qwen3.8:27b --arm all
```

Output: `data/damage_style_answers.csv`. 234 items × 2 orders = **468 calls**; total for the study
is **554**. Interrupt and re-run the same command at any point; rows already on disk are skipped.
Expect several hours: the calls carry two or three full-resolution
images each.

What the script does on its own, and what you must not defeat:

- **The Arm A null runs first** (6 items, baseline against baseline at different seeds). This is
  guard **G3**: a judge that calls one of two baselines defective cannot measure degradation.
- **Guards G1 and G2 fire after the first 32 calls of each arm**, not in the analysis. An arm whose
  first-position share leaves [0.25, 0.75], or whose unparseable share reaches 10 %, **halts**. The
  other arm continues. *A halted arm is a result*: report it, do not restart it with different
  wording.
- **The foils are computed, not chosen.** `foil_table()` reads `data/sign_decomposition_cells.csv`
  and picks, for each block and dose, the other block closest in ‖D‖. Do not override it.
- **A missing file is skipped and printed**, never substituted.
- **A network or timeout error is recorded as an empty answer** and the run continues.

If the whole run dies, re-launch the same command. If it dies three times at the same item, note
the item in the report and run with `--arm A` and then `--arm B` separately.

## 5. Step 3 — determinism

```bat
python experiments\judge_damage_style_retest.py ^
  --renders "C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_mappa\renders" ^
  --model qwen3.8:27b
```

32 calls: **8 items from each arm**, both orders. The script snapshots the first run to
`data/damage_style_answers_run1.csv`, re-runs those items and prints the test–retest rate.

**Test–retest below 0.95 invalidates the run** and must be reported as such. The previous study
measured 1.000, so anything lower is news.

A superseded one-liner used to live here. It selected the items with `sorted(item_ids)[:16]`, and
because ids begin with `A|` and `B|` that put all sixteen in Arm A — Arm B, the arm this study
exists for, would never have been re-tested. Amendment 01 replaced it with the script above. Do not
reinstate a manual selection.

## 6. Step 4 — analysis

```bat
python experiments\judge_damage_style_analyze.py > data\damage_style_report.txt
type data\damage_style_report.txt
```

It prints the nulls, the position bias, the unparseable share, the six pre-registered predictions
D1–D6 with CONFIRMED / FALSIFIED / GREY against the frozen thresholds, and the quadrant table.

**Do not adjust a threshold to change a verdict.** GREY is a legitimate outcome and there are two
predictions expected to land there.

## 7. Step 5 — the report

Write `docs/report_damage_or_style.md`, in **English**, containing:

1. the gate result, per probe, with the numbers;
2. the nulls (Arm A null share, Arm B null share) and the position bias;
3. Arm A and Arm B tables as the analyser prints them, **including the order-disagreement rate**,
   which is a measurement and not a nuisance;
4. D1–D6, each with its frozen threshold beside the observed value;
5. the quadrant table;
6. any halted arm, skipped item, or skipped step, named;
7. a **Limits** section that says: two prompts, so the unit of analysis is thin (pitfall 17); the
   judge is one model with one gating; every statement is about *what this judge reports*, not about
   what the images *are*.

Rule 7 applies: **every published number must come from a file in `data/`.** The three files are
`damage_style_gate.csv`, `damage_style_answers.csv`, `damage_style_report.txt`. Name them.

## 8. Step 6 — commit

```bat
python experiments\validate_notebook.py
git add docs\prereg_damage_or_style.md docs\RUNBOOK_2026-09-27_damage_or_style.md ^
        docs\report_damage_or_style.md experiments\judge_multi_image.py ^
        experiments\judge_pairs_gate.py experiments\judge_damage_style_run.py ^
        experiments\judge_damage_style_retest.py ^
        experiments\judge_damage_style_analyze.py data\damage_style_*.csv data\damage_style_report.txt
git commit
del .git\*.lock
```

Commit message in Italian, describing what was measured and what came out — including a halted arm
or a failed gate, which are outcomes and belong in the message. Attribution lines:

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01FZMivSRYy2R8cD26dETdRb
```

**Do not push.**

## 9. What Alessandro gets back

One sentence per block × dose from the quadrant table: *pure damage*, *a style that costs quality*,
*a clean style*, or *nothing happened* — plus the honest note that this is one judge's report, and
that the question of whether a far-away image is a win was his, not the instrument's.
