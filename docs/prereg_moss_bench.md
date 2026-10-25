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
