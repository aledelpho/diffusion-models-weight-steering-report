# Directives for Antigravity — C45 prompt writing bench (preparation only)

Written by Claude on 2026-10-04 at Alessandro's request. The design and the prompt
texts are fixed in `docs/prereg_prompt_writing.md`; this page says what to build.

## Hard rules

1. **Do not generate renders.** Do not POST to ComfyUI, do not run the queue script,
   not even one test image. Alessandro launches every render.
2. **Do not use `monitor_and_shutdown.py`**, do not shut down or close anything.
3. **Do not edit the prompt texts.** Copy them from `docs/prereg_prompt_writing.md`
   byte for byte (read them from the file programmatically, between the ``` fences, or
   by the substitution rules given there). No "cleaning", no reformatting, no added
   quality tags.
4. **Do not analyse, interpret or write findings** about this bench, and do not reuse
   the "Delta_Crollo" measure (`docs/semantic_routing_audit.md`). Scoring is done by
   Claude with code fixed in the pre-registration.
5. Do not touch files you did not create in this task. Do not delete files.
6. Everything in the repository in English; commits small, descriptive, in Italian;
   **no push**. Run `python experiments/validate_notebook.py` (0 errors) before each
   commit; `git status` before `git add`; add only your own files.

## What to build

1. `experiments/make_prompt_writing_plan.py` → `data/prompt_writing_plan.csv`
   - 8 prompt ids: `S1_W3_tags`, `S1_W4_synonyms`, `S1_C1_flamegauntlet`,
     `S2_W1_original`, `S2_W2_reordered`, `S2_W3_tags`, `S2_W4_synonyms`, `S2_C1_oldman`.
   - 25 conditions each: `baseline` and the 24 arms of blocks 00, 02, 05, 08, 09, 12,
     13, 15, 17, 19, 23, 27, both signs. **Copy `dose`, `sign`, `vector` and
     `override_dict` for each `cond_id` from `data/prompt_order_experiment_plan_full.csv`**
     (rows of `V1_Original`, seed 3141592) and assert they are identical across the
     two seeds there. Do not recompute vectors.
   - Seeds 3141592 and 1234567. Settings copied from the same plan rows (checkpoint
     mode, sampler, scheduler, steps, cfg, denoise, width, height) — assert they match
     `euler_ancestral / simple / 9 / 1.0 / 1.0 / 1024 / 1280`.
   - Row 0: reproducibility render, prompt `V1_Original` text, baseline, seed 3141592,
     prefix `REPRO_V1_Original_baseline_krea2_seed3141592`.
   - Filename prefix: `{prompt_id}_{cond_id-with-block-sign-dose}_krea2_seed{seed}`,
     the same pattern as `benchmark_prompt_order` (e.g.
     `S2_W3_tags_blk23_neg_d0.350_krea2_seed1234567`).
   - Expected total: **401 rows**. The script prints the count by prompt and seed and
     fails if it is not 8 × 25 × 2 + 1.
2. `experiments/queue_prompt_writing.py` — a copy of `queue_order_experiment_seed2.py`
   with only the plan path and the output folder changed (`benchmark_prompt_writing`).
   The workflow graph must stay identical (same UNETLoader file, same CLIPLoader
   `qwen3vl_4b_bf16.safetensors` type `krea2`, same tuner node). It must skip rows whose
   expected file already exists, so it can be resumed. **Do not run it.**
3. `experiments/check_prompt_writing_repro.py` — compares the REPRO render with
   `benchmark_prompt_order/V1_Original_baseline_krea2_seed3141592_00001_.png` pixel by
   pixel and prints PASS / FAIL with the max absolute difference. Alessandro runs it
   after the first image; if FAIL, the queue is stopped and nothing is scored.
4. `docs/RENDERS_2026-10-04_prompt_writing.md` — how to launch (command lines), the
   401 count, expected disk use, folder, and the order: REPRO first, check, then the rest.
5. A self-check you run and paste at the end of the RENDERS doc: for 3 random rows,
   the prompt text in the CSV equals the text in the pre-registration (print the
   first and last 60 characters and the SHA-1 of both).

## Then

Stop and report to Alessandro: files created, row count, the self-check output.
Nothing else.

## Phase 2 — launch (added 2026-10-04, on Alessandro's authorisation)

Alessandro has authorised Antigravity to queue the C45 renders. This replaces hard rule 1
**for these 401 renders only**. Rules 2–6 still apply. The directive for C47/C48
(`directives_antigravity_probe_and_blk23.md`) is **on hold**: do not start it until
Alessandro says so.

1. `python experiments/queue_prompt_writing.py --first 1` (the REPRO row only). Wait until
   the image exists.
2. `python experiments/check_prompt_writing_repro.py`. Paste the output. If it is not
   `PASS`, **stop** and report; queue nothing else.
3. `python experiments/queue_prompt_writing.py`. Wait for the ComfyUI queue to empty by
   polling `/queue` (never with `monitor_and_shutdown.py`; close nothing).
4. Count the files: 401 PNG in `benchmark_prompt_writing` (no `_00002_` duplicates). List any
   missing expected filename.
5. `python experiments/prompt_writing_eye_sheets.py` (builds sheets for Alessandro's eye;
   produces no numbers).
6. Append to `docs/RENDERS_2026-10-04_prompt_writing.md`: the commands run, the REPRO output,
   the file count. Commit in Italian. Do **not** run `analyze_prompt_writing.py`.
7. Report to Alessandro and stop.
