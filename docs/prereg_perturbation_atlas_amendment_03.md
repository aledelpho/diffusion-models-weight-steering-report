# Amendment 03 to `docs/prereg_perturbation_atlas.md`

- **Written:** 2026-09-25
- **Amends:** §2 of the frozen document and §3–§4 of Amendment 01.
- **Supersedes Amendment 02 in full.** `fast_style_compass_rotation` is no longer called;
  its reproduction gate is moot.
- **Written before a single preset has been derived and before any render exists.**

---

## 1. Why the perturbation is being redefined

An inspection on 2026-09-25 established that **all fourteen presets in
`presets/` carry the same four `style_compass` rotation recipes** on `Block_3`, seeds
82/60/59/56 (`rotation_recipes_count = 4` in every one).
`experiments/derive_chaos_presets.py` never touches them: it deep-copies the base and
rewrites only the scalar patches. The tuner's loader reads `rotation_recipes` and applies
them.

Every arm measured by this project is therefore **the same rotation plus different scalar
multipliers**, including the arms used as random controls. The rotation is not a variable
that could differ between arms; it is a constant floor underneath every comparison made so
far.

The atlas will not inherit it.

## 2. The perturbation, redefined — scalars only, generated, nothing inherited

An atlas preset consists of **per-tensor scalar multipliers and nothing else**:

- `rotation_recipes: []`, `chaos_rotation_recipes: []`, `channel_recipes: []`,
  `chaos_recipes: []`, and `suite_rotation_effective: false`.
- No value is copied from `Arthemy_Bench_Base.json`. The hand-set CLIP plateaus are gone
  along with everything else, and with them the partial-independence problem recorded in
  Amendment 01 §4, which no longer applies.

**Generation, per draw and per region:**

1. For every tensor in the target region, draw a multiplier i.i.d. from a standard normal,
   `torch.Generator(device="cpu").manual_seed(draw_seed)`, tensors visited in sorted name
   order so the draw is reproducible. Tensors outside the region get exactly `0.0`.
2. Rescale with the **existing, unmodified `scale_subset`** of
   `experiments/derive_chaos_presets.py` so that the norm-weighted displacement matches the
   anchor below. The convergence check and its exception stay as they are.

**Zero mean is deliberate.** A non-zero mean would be a systematic scaling of the region,
which is a different perturbation and a different question. This family scales some tensors
up and some down.

**Anchor.** The target displacement stays the one the six existing chaos presets share:
`d_model = 267.3721462683354`, `d_clip = 55.27659756535684`. Nothing else is comparable
with the old corpus (§5), but keeping the magnitude on a known scale is free and useful.

**Draws.** Two, as before: `draw_seed` from
`random.Random(20260925).sample(range(1, 1000), 2)`, written to the output before any
weight is touched. The two draws are now **fully independent** — they share no component
at all.

## 3. One condition added, and why

The ten regions of Amendment 01 §2 are unchanged. **An eleventh condition is added:
`uniform_all`** — the same generated scalars spread over every patched tensor of both
domains, at the same anchor displacement, no region targeting.

It is the reference against which "this region does more" means anything: without it, ten
regional numbers can be compared only with each other, and nothing says whether any of them
beats simply perturbing everything. This is an addition by the analyst, made before any
preset exists, and it costs three renders per prompt.

Phase 1 becomes **11 x 2 draws x 3 seeds + 3 baselines = 69 renders** for one prompt.
Phase 2 at 8 prompts becomes **552**.

## 4. Verification gates — before anything is rendered

1. **Determinism.** Generate the same (region, draw) preset twice. Every multiplier must be
   bit-identical. Not identical -> **STOP**.
2. **Convergence.** `scale_subset` must converge for all 22 presets. Any that does not is
   **dropped and reported**, never replaced.
3. **Anchor.** Every preset's measured displacement must match the anchor to at least
   twelve significant digits, the precision the existing calibration already achieves. It
   does not -> **STOP** and report the residual.
4. **Emptiness.** Every preset must carry `rotation_recipes: []` and
   `suite_rotation_effective: false`, asserted by reading the written file back from disk,
   not by trusting the writer.

All four to `data/perturbation_atlas_draw_check.csv`.

## 5. What this costs, stated plainly

**The atlas shares nothing with the existing corpus.** Its presets contain no rotation, no
hand-set plateau and no value inherited from `Arthemy_Bench_Base.json`.

No number from the atlas may be placed in a table, a test or a sentence alongside a number
from `data/arm_coherence*.csv`, `data/shared_axis*.csv`, `data/mountain_reachability*.csv`,
`data/palette_*.csv` or `data/arm_identifiability*.csv`. They measure different objects.
A page that compares them is wrong, and this paragraph travels with the results.

What is gained in exchange: for the first time in this project, **the perturbation's entire
content is specified in a document** rather than inherited from a file whose composition had
to be reverse-engineered after the fact.

## 6. The question this leaves open, deliberately unanswered

How much of what has already been measured is the shared rotation? It is answerable — the
existing arms would be regenerated with `rotation_recipes: []` and re-rendered — but that is
a separate study, it needs new renders, and **it is not authorised here**. It is recorded so
that it is not forgotten.

## 7. What is not changed

The two questions (§1 of the frozen document), the magnitude matching and its limitation
(§3), the phases and the gate between them (§5), the reused measurement machinery and the
four palette-extent features (§6), the decision rules (§7), the kill conditions (§8) and the
outputs (§9) remain in force. The four bands of seven blocks and the ten regions of
Amendment 01 §2 remain, plus `uniform_all`. The hard stop at J2 remains: the regions are
seen before a single preset is derived.
