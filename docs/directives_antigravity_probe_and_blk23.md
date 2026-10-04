# Directives for Antigravity — residual probe (C48) and blk23 vs "colorful" (C47)

Written by Claude on 2026-10-04. **Alessandro has authorised Antigravity, for these
two benches only, to queue renders in ComfyUI.** The standing rule that Antigravity
never renders still applies to everything else, including C45 (`prompt_writing`),
unless Alessandro extends it in writing.

## Hard rules

1. Queue only what is listed here. No extra conditions, prompts, seeds or test images
   beyond the single probe trial in step A2.
2. **Never use `monitor_and_shutdown.py`.** Do not shut down, sleep or close the PC,
   ComfyUI, StabilityMatrix or any window. If ComfyUI must be restarted (step A1), ask
   Alessandro to do it, or wait until he says you may do it.
3. Do not edit any prompt text, dose, seed or setting fixed in
   `docs/prereg_residual_probe.md` and `docs/prereg_blk23_vs_colorful.md`.
4. **Do not analyse or interpret.** Run only the checks named below and paste their raw
   output. Do not write findings or summaries of results, and do not use the
   "Delta_Crollo" measure. Claude scores both benches with code already committed.
5. Do not modify or delete files you did not create in this task. Do not touch
   `experiments/analyze_residual_probe.py`, `experiments/analyze_blk23_vs_colorful.py`,
   `tools/comfy_residual_probe/`, or any pre-registration.
6. Everything in the repository in English; commits small, descriptive, in Italian; **no
   push**. `git status` before `git add`; add only your files; run
   `python experiments/validate_notebook.py` (0 errors) before each commit.
7. If anything fails or does not match an expectation below, **stop and report**; do not
   work around it.

## A. Residual probe (C48) — 23 renders + 1 trial

1. Copy the folder `tools/comfy_residual_probe` from the repository to
   `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\comfy_residual_probe`
   (copy, do not move). ComfyUI then needs a restart (rule 2). After the restart,
   confirm that `ArthemyResidualProbe` appears in `http://127.0.0.1:8188/object_info`.
2. Trial: `python experiments/queue_residual_probe.py --first 1`. When it finishes,
   check that `data/residual_probe_raw.csv` exists and has 9 × 28 = 252 data rows for
   that run. Then **delete nothing**; move the trial CSV to
   `data/residual_probe_raw_trial.csv` so the main run starts from an empty file, and
   leave the trial image where it is (the main run will skip nothing: re-rendering it is
   fine).
3. Main run: `python experiments/queue_residual_probe.py`. Wait for the queue to empty
   (poll `/queue`; never with the shutdown script).
4. Run `python experiments/analyze_residual_probe.py --repro` and paste the output. If
   it does not say `REPRO PASS 23 images` (a trial duplicate may make it 24 — report
   the exact line), stop.
5. Check `data/residual_probe_raw.csv`: 23 × 9 × 28 = 5 796 data rows. Commit
   `data/residual_probe_raw.csv` (and the trial file) with an Italian message. Do not
   run the analysis without `--repro`.

## B. blk23 vs "colorful" (C47) — 128 renders

1. `experiments/make_blk23_colorful_plan.py` → `data/blk23_colorful_plan.csv`, exactly as
   `docs/prereg_blk23_vs_colorful.md` §Design specifies:
   - 8 prompts × 2 seeds × 8 conditions = **128 rows**; assert the count;
   - prompt text read from the source plan's baseline row;
   - suffix rule implemented as written;
   - the 34-slot `vectors_override` all zeros except slot 23 = the signed dose (−0.45,
     −0.30, −0.15, +0.15, +0.30), formatted like the existing plans (three decimals,
     comma separated);
   - output prefix `{prompt_id}_{cond}_krea2_seed{seed}` in folder
     `benchmark_blk23_colorful`, so files come out as
     `{prompt_id}_{cond}_krea2_seed{seed}_00001_.png`, the pattern
     `analyze_blk23_vs_colorful.py` reads.
2. `experiments/queue_blk23_colorful.py`: a copy of the workflow in
   `experiments/queue_order_experiment_seed2.py` (UNETLoader `krea2_turbo_bf16`,
   CLIPLoader `qwen3vl_4b_bf16` type `krea2`, VAE `qwen_image_vae`, ResetPatcher, and
   `ArthemyKrea2ModelTuner` only for the `b23_*` rows). It must skip files that already
   exist.
3. Self-check before queuing, pasted into the RENDERS doc: for each of the 8 prompts,
   the SHA-1 of the plan's `baseline` text against the source plan's text (must be
   equal), and the full `txtpos` and `txtneg` texts of one styles prompt and one v3
   prompt.
4. Queue, wait for the queue to empty, then run a reproducibility check (write
   `experiments/check_blk23_colorful_repro.py`): every seed-A image whose condition
   already exists in `benchmark_single_blocks_styles` or `_v3` (baseline, blk23 at the
   same signed dose) must be pixel-identical. Paste max absolute difference per pair.
5. `docs/RENDERS_2026-10-04_blk23_colorful.md`: commands run, counts, the self-check, the
   repro output. Commit plan, scripts and RENDERS doc.

## Then

Report to Alessandro: files created, counts, the outputs of A4, A5, B3 and B4. Do not
run `analyze_residual_probe.py` without `--repro`, and do not run
`analyze_blk23_vs_colorful.py`; Claude does.
