# Runbook — the capability judge, end to end

- **For:** the agent with ComfyUI and Ollama attached over API.
- **Governed by:** `docs/prereg_capability_judge.md` and
  `docs/prereg_capability_judge_amendment_01.md`, both frozen before any call.
- **Generates no render.** Every image it needs already exists on disk.

---

## 0. Standing constraints — these override anything convenient

- **Do not generate renders.** Not one. This study reads existing PNGs.
- **Do not write anything under `notebook/`.** No page, no claim, no status.
- `python experiments/validate_notebook.py` must print **0 errors** before every commit.
- Commit messages in **Italian**, small and descriptive. **Do not push.**
- Do not shut down or close anything.
- **Do not change the status of any published claim.** If a result here bears on one, say so in
  the report and stop.

## 1. The one rule that makes this study worth running

**This study is gated, and the gate is not a formality.**

The judge is a measuring instrument that has never been calibrated for this task. The gate of
step 2 decides whether it is an instrument at all. **No image of any preset is shown to the judge
until the gate has printed PASS.** `judge_capability_run.py` enforces this itself and refuses to
start otherwise; do not work around it.

**If the gate fails, the failure is the result.** Write it up and stop. Specifically, do **not**:

- reword the questions until the judge passes;
- try model after model until one passes and report only that one;
- lower the thresholds of `docs/prereg_capability_judge_amendment_01.md` §3 (6 of 8 scenes,
  polarity agreement ≤ 0.20) — they were fixed before any call existed;
- drop the negated-polarity questions because they look redundant. They are the only thing that
  catches a judge answering by wording rather than by pixels;
- resize or crop the images. Native resolution, 1024 × 1280, whole. A 224 px pipeline is blind to
  what this project measures.

A previous VLM run on this project, `data/vlm_gate_20260915.csv`, answered "B" on all four trials
of the two easiest pairs and invented a visible difference between two identical baselines, at
confidence 5 on all twelve rows. That is what an uncalibrated judge looks like, and it is why
these steps are in this order.

## 2. Which model, and which not

Read from the manifests already on disk:

| model in Ollama | vision projector | use as judge |
|---|---|---|
| `qwen3.8:27b` | **yes**, 931 MB | **primary** |
| `qwen3.8:27b-fable` | yes, 928 MB | **second judge**, different weights |
| `gemma4:31b` | **none** | **unusable** — no image input at all |

`gemma4:31b` has no projector layer: it cannot take pixels. Do not attempt it, and do not report
its answers if it is somehow made to produce any.

Declare in the report: `qwen3.8` is **not** the model the tuner patches — that is `qwen3vl_4b` —
but it is the same vendor family. That is weaker independence than intended and it is stated, not
hidden.

## 3. Steps

Renders live at
`C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_atlas_phase1\renders`.

### Step 1 — the gate (128 calls, a few minutes)

    python experiments/judge_style_gate.py --renders "<renders>" --model qwen3.8:27b

It shows **only the 8 baselines** and asks the style question about all 8 styles, both polarities.
It prints its own verdict. Then repeat with `--model qwen3.8:27b-fable`; the output file appends.

Commit: `data/capability_judge_gate.csv`.

**If both judges FAIL → stop here.** Report the 8 × 8 matrices and the two verdicts. That is a
complete and publishable negative about the instrument, and it closes the capability question by a
second route after `docs/prereg_style_axis_tradeoff.md` already closed it by the first.

### Step 2 — the measurement, only for a judge that passed (~920 calls, 1–2 h)

    python experiments/judge_capability_run.py --renders "<renders>" --model <the judge that passed>

200 images at seed 42, two questions, both polarities, plus 30 images asked twice for the
test-retest. It is **resumable**: if it is interrupted, run the same command again and it skips
what is already answered. Do not delete the CSV to "start clean".

Commit: `data/capability_judge_raw.csv`.

### Step 3 — the analysis

    python experiments/judge_capability_analyze.py

It runs the guards first and will print `judge_unusable` if any fails — that is a valid outcome,
not an error to fix. Then Cost, the trade-off count and its p against the judge's own noise.

Commit: `data/capability_judge_tests.csv`.

## 4. What to report back, in this order

1. The gate: per judge, how many of 8 scenes passed, the polarity agreement, and the 8 × 8 matrix.
2. The guards: test-retest per question, yes-share, share of items discarded for polarity.
3. Cost per question, the trade-off count and its p, and the per-scene costs.
4. The verdict string the script produced, **verbatim**, without interpreting it.
5. Anything that did not go as this runbook says, however small.

Do not write the interpretation. The wordings for each outcome are already fixed in
`docs/prereg_capability_judge.md` §6, and choosing between them is not this run's job.

## 5. Two things that are already known to be wrong and must not be repeated

- `experiments/vlm_gate.py` never logged which model answered, and a week later nobody could say.
  All three scripts here write `judge_model`, `backend`, `url` and `run_utc` on every row. Keep it.
- The automatic quality gate once marked `blockshuf_neg_2x` DEGRADED in 6 styles of 8 — exactly the
  six where the observer judged it best — and the count was retracted. The 1-to-5 quality question
  was withdrawn for the same reason (amendment 01 §5). **Do not add it back.**
