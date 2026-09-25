# Amendment 01 to `docs/prereg_perturbation_atlas.md`

- **Written:** 2026-09-25
- **Amends:** §2 and §4 of `docs/prereg_perturbation_atlas.md` (committed `6d3c817`).
- **Everything else in that document is unchanged and remains in force.**
- **Written before a single preset has been derived and before any render exists.**

---

## 1. What was wrong

The J2 stop fired correctly. Three defects, all in the drafting of §4 and §2:

1. **The partition does not exist.** §4 asked for five contiguous bands of equal size
   covering every block. The DiT has **28 blocks** (`blocks.0` to `blocks.27`), and 28 is
   not divisible by 5. No such partition exists.
2. **The two dropped cells were never specified.** §4 required dropping two of the ten
   depth-by-component cells without naming them or giving a criterion — while §4 also
   forbade the agent from choosing regions itself. That is an instruction that cannot be
   followed, and the agent was right to refuse rather than invent one.
3. **Only one base draw exists.** §2 requires two. The repository holds
   `presets/Arthemy_Bench_Base.json` and no second, independently seeded draw.

## 2. §4 replaced — four bands, and nothing is dropped

**28 = 4 x 7.** Four contiguous bands of exactly seven blocks each cover the DiT with no
gaps, no overlaps and no remainder:

| band | blocks |
|---|---|
| `early` | 0–6 |
| `early_mid` | 7–13 |
| `late_mid` | 14–20 |
| `late` | 21–27 |

Crossed with the two components, **attention** and **MLP**, that is **8 regions**. Plus
the two degenerate cases, **`clip_only`** (no model patch) and **`model_only`** (no CLIP
patch), for **exactly 10**.

**No cell is dropped, because none needs to be.** The arithmetic fixes the list, not a
judgement call — which is the property the original rule was trying and failing to have.

The script still prints the exact block indices, the exact tensor-name patterns and the
tensor count per region to `data/perturbation_atlas_regions.csv` and **still stops** before
deriving anything. If a component name does not match the model's actual tensor names, it
stops and reports rather than substituting.

## 3. §2 amended — the second draw, and what happens without it

The second base draw must be produced by the tuner with **parameters identical to
`Arthemy_Bench_Base` and different seeds**: the same recipe type, the same style
direction, the same rotation angle, the same target block, the same depth reach and the
same manifold, with only the four seeds changed. It is Alessandro's to generate; nothing
here authorises the agent to produce, approximate or synthesise one.

**If the second draw does not exist when Block J runs:**

- The study proceeds with **10 presets, not 20** — the ten regions of §2, single draw.
- Every region result is then **unreplicated**, and is recorded in
  `data/perturbation_atlas_tests.csv` with `n_draws = 1` and the verdict qualified as
  **`single_draw_unreplicated`** in every row.
- A region effect from a single draw cannot be distinguished from a peculiarity of that
  draw. **No claim about where colour lives is promoted from a single-draw run**, whatever
  its p-value. The run is a pilot for the two-draw study, and is described that way.

This is a real cost, not a formality: one draw answers "does this perturbation behave
differently in different regions", which is interesting, and cannot answer "do
perturbations in general behave differently in different regions", which is the question.

## 4. New — the two draws are not fully independent, and this is declared

`presets/Arthemy_Bench_Base.json` is a hybrid. Its CLIP patches hold **six distinct values
across 629 tensors**, 343 of them exactly `-0.025`: uniform plateaus set by hand. Its model
patches hold 345 distinct values across 430 tensors, mixing those plateaus with the
irregular footprint of four seeded `style_compass` rotations.

A second draw generated as §3 specifies would differ **only in its rotation component**.
The hand-set plateaus are deterministic and would be identical in both.

Consequences, stated rather than worked around:

- The two draws are **partially independent**. They share a fixed, hand-authored component
  and differ in their random one.
- **The region factor is unaffected.** Whatever the perturbation is made of, it is held
  identical across the ten regions and only its destination changes; that comparison stays
  clean.
- **The draw factor is weakened.** Two draws sharing a deterministic component will agree
  more than two fully independent draws would, so agreement between them is weaker
  evidence than it looks. Where §7 of the frozen document asks for consistency across
  draws, that consistency is to be read with this in mind, and the sentence travels with
  the result.

Separating the plateaus from the rotations is a better design and is **not authorised
here**: it would need its own amendment and would change what is being redistributed.

## 5. What is not changed

The two questions of §1, the magnitude matching and its limitation (§3), the phases and
the gate between them (§5), the reused measurement machinery and the four palette-extent
features (§6), the decision rules (§7), the kill conditions (§8) and the outputs (§9) are
unchanged and remain binding. The hard stop at J2 remains: the ten regions are seen before
a single preset is derived.
