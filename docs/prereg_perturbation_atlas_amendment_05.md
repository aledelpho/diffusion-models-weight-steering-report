# Amendment 05 to `docs/prereg_perturbation_atlas.md`

- **Written:** 2026-09-25
- **Amends:** the anchor definition of Amendment 03 §2.
- **Everything else in the frozen document and in Amendments 01, 03 and 04 is unchanged.**
- **Written before a single preset has been derived and before any render exists.**

---

## 1. The gap

Amendment 03 §2 fixed the anchor as two numbers, one per domain:
`d_model = 267.3721462683354` and `d_clip = 55.27659756535684`. That is how the six
existing chaos presets are calibrated, and it works for them because every one of them
perturbs both domains.

Ten of the thirteen conditions of Amendment 04 do not.

| condition | model | CLIP |
|---|---|---|
| the eight depth-by-component regions, `modulation_norm`, `txtfusion`, `model_only` | yes | **none** |
| `clip_only` | **none** | yes |
| `uniform_all` | yes | yes |

Under the per-domain anchor, a model-only region would carry a total displacement of
`267.37` and `clip_only` would carry `55.28` — **a factor of about 4.8**. `uniform_all`,
holding both, would carry more than either.

The entire purpose of matching the magnitude was so that "this region does more" could not
mean "this region was pushed harder". As written, it would mean exactly that: CLIP would
look weak by construction, and `uniform_all` would be useless as the reference Amendment 03
§3 introduced it to be.

There is also an immediate practical failure: `scale_subset` raises
`"Il sottoinsieme filtrato ha norma zero"` on an empty subset, so a model-only region would
stop the script when it reached the CLIP domain.

This is an incomplete specification by the author, not a change of design.

## 2. The anchor replaced — one scalar, across both domains

A single total displacement, identical for all thirteen conditions:

```
D = sqrt(d_model^2 + d_clip^2)
```

computed from the two anchor values above. Every condition is rescaled so that its
norm-weighted displacement **summed across both domains** equals `D`, wherever it lives:
`clip_only` puts all of `D` into CLIP, `early_attn` puts all of `D` into the attention
tensors of blocks 0–6, `uniform_all` spreads `D` over everything.

**The script computes `D` and writes it to `data/perturbation_atlas_calibration.csv`.** It
is not transcribed from this document, and no number in this paragraph is to be copied into
code.

A domain that a condition does not touch is left at exactly zero and is **not** passed to
`scale_subset`. The zero-norm exception is not caught, suppressed or worked around; the
domain is simply not rescaled.

## 3. The one authorised change to the rescaling logic

`scale_subset` currently targets a displacement **per domain**. It must instead accept a
target for the **combined** displacement across the domains a condition touches.

This is the **only** modification to that logic authorised anywhere in this study. Its
convergence check and the exception it raises on non-convergence stay exactly as they are.
The change is recorded in `data/perturbation_atlas_calibration.csv` as a column naming the
code path used.

**Regression gate, before any atlas preset is derived.** Re-derive the six existing chaos
presets — `CHAOS_ATTN`, `CHAOS_EDGES`, `CHAOS_MID`, `CHAOS_MLP`, `CHAOS_RAMP`,
`CHAOS_RAND2` — through the modified script and compare against
`data/chaos_presets_calibration.csv`.

- Every `d_model_measured` and `d_clip_measured` reproduces to the twelve significant
  digits already recorded -> the modification is behaviour-preserving for the old path,
  and the atlas may proceed.
- Any of them moves -> **STOP**. The modification has changed the machinery that produced
  every calibration figure in the repository, and that must be understood before anything
  is built on it. Do not adjust a tolerance and do not proceed.

Write the outcome to `data/perturbation_atlas_draw_check.csv` alongside the four gates of
Amendment 03 §4.

## 4. What this costs

`D` is not numerically equal to either per-domain anchor, so the atlas presets do not carry
the same displacement figures as the six existing chaos presets. That is one more reason
the atlas is not comparable with the existing corpus, which Amendment 03 §5 already states
and which this does not change — it adds a reason rather than a new problem.

## 5. What is not changed

The thirteen conditions and their tensor counts (Amendment 04 §3), the scalar-only
generated perturbation (Amendment 03 §2), the four verification gates (Amendment 03 §4),
the recorded properties of the design (Amendment 04 §4), the four bands of seven blocks
(Amendment 01 §2), and every section of the frozen document remain in force.
