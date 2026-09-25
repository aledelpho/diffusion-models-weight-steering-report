# Amendment 02 to `docs/prereg_perturbation_atlas.md`

- **Written:** 2026-09-25
- **Amends:** §3 of Amendment 01 — the claim that the second base draw must be generated
  by hand.
- **Everything else in the frozen document and in Amendment 01 is unchanged.**
- **Written before a single preset has been derived and before any render exists.**

---

## 1. What was wrong

Amendment 01 §3 stated that the second base draw "is Alessandro's to generate; nothing
here authorises the agent to produce, approximate or synthesise one."

**That was an assumption, not a fact, and it is false.** It was written without inspecting
the tuner's code.

`custom_nodes/Arthemy_Krea2_Tuner/arthemy_geometry_engine.py` exposes

```
fast_style_compass_rotation(weight_tensor, ..., seed=42, ...)
```

as an ordinary Python function whose only imports are `torch`, `safetensors`, `math`,
`zlib`, `base64`, `os` and `typing`. It needs no ComfyUI runtime, no node graph and no
user interface; its generator runs on CPU. `experiments/derive_chaos_presets.py` already
loads the model and CLIP weights from safetensors, so the machinery to feed it exists in
the repository.

The function's own docstring records what the seed does: *"`seed` only permutes the plane
pairing, and does so identically for every layer, so a given seed is a reproducible style
flavour that stays coherent across blocks."*

Generating a second draw is therefore a scripted operation. **No manual tuner run is
required and none is requested.**

## 2. §3 of Amendment 01 replaced

The second base draw is produced by script, by calling
`fast_style_compass_rotation` with **parameters identical to `Arthemy_Bench_Base` and four
different seeds**: same recipe type, same style direction (180.0), same rotation angle
(10.0), same target block (`Block_3`, all 10–14), same depth reach, same manifold
(`Output Manifold (R @ W)`), same sub-components (all). Only the four seeds change.

The seeds of the first draw are **82, 60, 59, 56**, recorded in
`presets/Arthemy_Bench_Base.json`. The second draw's four seeds are chosen by a rule fixed
here and not by preference: `random.Random(20260925).sample(range(1, 1000), 4)`, with the
drawn values written to the output before any weight is touched. Any collision with
{82, 60, 59, 56} is redrawn, and that is recorded.

The hand-set CLIP plateaus of the base preset are **copied unchanged** into the second
draw. They are deterministic, they are not a product of the seed, and Amendment 01 §4
already records what that costs: the two draws share a fixed component and differ only in
their random one, so their agreement is weaker evidence than full independence would give.

## 3. The reproduction gate — mandatory, runs first, has a stop

A second draw produced by our own call into that function is only trustworthy if our call
reproduces the first draw.

**Before generating anything new:** call `fast_style_compass_rotation` with the recorded
seeds **82, 60, 59, 56** and the recorded parameters, apply the same four rotations in the
same order, and compare the resulting per-tensor multipliers with
`presets/Arthemy_Bench_Base.json`.

- **Identical** — every one of the 430 model and 629 CLIP multipliers matching to at least
  1e-9 — the reimplementation is faithful and the second draw may be generated.
- **Not identical** — **STOP**. Report the number of mismatched tensors and the largest
  discrepancy. Do not generate a second draw, do not adjust tolerances, and do not guess
  which parameter differs. A draw produced by a call that cannot reproduce the original is
  not the same kind of object as the original, and comparing the two would measure our
  reimplementation rather than the model.

Write the outcome to `data/perturbation_atlas_draw_check.csv` regardless of which way it
goes, with the per-tensor maximum absolute difference and the count of mismatches.

## 4. If the gate fails

The study falls back to the single-draw path already specified in Amendment 01 §3: ten
presets, every row marked `single_draw_unreplicated`, no claim promoted about where colour
lives. The fallback is unchanged; only the reason for reaching it is different.

## 5. What is not changed

The four bands of seven blocks and the ten regions (Amendment 01 §2), the partial
independence of the two draws and its cost (Amendment 01 §4), and every section of the
frozen document remain in force. The hard stop at J2 remains: the ten regions are seen
before a single preset is derived.
