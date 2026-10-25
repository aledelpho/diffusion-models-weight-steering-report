# Pre-registration MOSS2 — the MOSS bench: reproducibility, a clean tuner, the seed floor, a first sensitivity ladder

Written 2026-10-25 by Claude, **before any MOSS2 render.** Authorised by Alessandro ("Procediamo"). Stage: verification
(page 20's checks repeated on MOSS-Image SFT), plus a descriptive dose ladder. Tool: `tools/comfyui_moss_tuner` v3
(MOSS1 gates passed, `docs/RENDERS_2026-10-25_moss_gates.md`). Script: `experiments/moss_bench.py`.

## Design (77 renders, about 1 h 50 min at about 85 s each)

Sampling as MOSS1 (SFT bf16, er_sde, simple, 25 steps, CFG 2.5, 1024 × 1280, no SLG, no prompt enhancer). Every render
goes through both MOSS tuners ("{}" when unedited): plain and edited pictures share one route.

* **V1 (1):** the dwarf at 2645751, plain, rendered again in a new session; compared with MOSS1's `empty_json`.
* **Floor (24):** six C100 prompts (dwarf, rally, still life, comic page, lotus canoe, leaf) × four seeds (2645751,
  3316624, 2718281, 1618033), plain.
* **V2 (4):** DiT layer 41, its four matrices × 1.0001 (in bf16 this should leave every weight unchanged), dwarf and
  rally; and, reported, TE layer 31 MLP down × 1.0001 (its F32 channel scale does change).
* **Ladder (48):** dwarf and rally at 2645751; DiT MLP down of layers 6, 20, 35 and TE MLP down of layers 6, 15, 27; d =
  0.01, 0.03, 0.10, 0.30.

## Criteria (fixed now)

* **V1 PASS:** maximum pixel difference 0. **V2 PASS (DiT):** maximum difference 0 for both prompts; otherwise reported as
  "bf16 rounding moved". A V1 failure stops every later MOSS test.
* **Floor (reported):** per prompt, the median DINOv2 distance between the four seeds (6 pairs). It is MOSS's reference
  for "a change as large as a change of seed".
* **Ladder (reported, descriptive):** DINOv2 distance to the plain render per edit and dose; the smallest dose at which
  it exceeds 0.02, and where it crosses the seed floor. This is a first sensitivity scale for Alessandro's question
  (how light can an edit be and still show), not a test. No eye pass in MOSS2.

## Limits

One seed for the ladder; DINOv2 is content-oriented (pitfall 94: its cosines do not track "the same change", but its
distance to the plain render was used for calibration throughout C103–C109).

## Amendment 1 (2026-10-25, before any MOSS2 result was looked at or kept)

Alessandro stopped the first run: the template settings (er_sde, 25 steps, CFG 2.5) give pictures far from what MOSS
can do, and his best MOSS pictures used euler, 50 steps, CFG 3 (also the official recommendation). Changes:

* **Sampling for MOSS2 and every later MOSS test:** euler, simple, **50 steps, CFG 3**, 1024 × 1280 (kept for direct
  comparison with Krea-2), no SLG, no prompt enhancer. About 170 s per picture.
* **Sampler check (12 renders, added at Alessandro's request):** the six floor prompts at seeds 2645751 and 3316624 with
  **euler_ancestral** (Krea-2's sampler), same settings otherwise. Reported: DINOv2 distance to the euler render of the
  same prompt and seed, and a sheet for Alessandro's eye. Decision on the sampler is his, after looking.
* **V1** is now two renders of the dwarf at 2645751 in one session, with a zero-dose JSON on the second so that ComfyUI's
  cache cannot return the first (MOSS1's `plain_b` was served from the cache in 0.15 s, so it did not test determinism).
* Total 89 renders, about 4 h 10 min. The pictures of the stopped run are moved aside and not used.

## Amendment 2 (2026-10-25, before any MOSS2 render)

After MOSS-S2 (`docs/moss_settings2_result.md`): **working setting T10** (lodestones DMD2 LoRA at 1.0, euler, 10 steps, CFG
1, simple, shift 5, 1024 × 1280); the euler_ancestral block is dropped (tested in MOSS-S2); ladder doses **0.10, 0.30,
1.00, 2.00** (d ≤ 0.30 barely moves MOSS); **confirmation cells named now:** the dwarf at 2645751, plain and the six
ladder edits at d = 1.00, rendered at R50 (euler, 50, CFG 3). A confirmation counts when Alessandro, blind, sees the same
kind of change at T10 and at R50 (page written after the renders); DINOv2 distances reported. 84 renders: 77 at T10
(about 30 min) and 7 at R50 (about 20 min).

## Amendment 3 (2026-10-25, before any confirmation label was exported)

Alessandro opened the confirmation page: at d = 1.0 the change is too small to judge. The confirmation cells move to
**d = 2.0** (the T10 ladder already has them): 6 more R50 renders of the dwarf at 2645751 (block `confirm2`, about 17
min). New page `occhio_MOSS2b.html`, key `data/moss_confirm2_key.csv`, labels `data/moss_confirm2_labels.csv`; same
cards, question and rule. The d = 1.0 page (`occhio_MOSS2.html`, key `data/moss_confirm_key.csv`) is superseded.
