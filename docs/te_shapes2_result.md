# C100 result — the push's shape is a property of the edit, on very different prompts and up to d = 10

2026-10-18. Pre-registration `docs/prereg_te_shapes2.md` (0514c61, before any encode; amendment 1 after the first run
stopped, before any measure). Encodes by Antigravity (`docs/RENDERS_2026-10-18_te_shapes2.md`): gates (a) and (b)
passed (b: max rel err 0.000276, limit 0.000977); 60 trajectories, 756 rows. Rules by Claude: `experiments/te_shapes2.py
--rules` → `data/te_shapes2_tests.csv`. Data `data/te_shapes2_trajectories.csv`, `Text2Img/benchmark_te_shapes2/*.npz`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| **1** — shapes of edits against random controls (whole, single MLP, positive; 18 vs 18) | "other" (one bend, none of the four shapes) in 18 of 18 edits and 18 of 18 controls; straight, spiral, wave, clip, accelerating 0 of 18 in both | **belongs to the network** (as C93) |
| **2** — range of the total turn over the 6 prompts, per edit × sign (10) | 2–7°; ≤ 15° in **10 of 10**, ≥ 30° in 0 of 10 | **a property of the edit** |
| **3** — heavy doses (reported) | label changes when doses beyond 3 / −1 are added: 9 of 60; new clips at the whole level: 0 | — |
| amendment 1 (reported) | one trajectory cut: dwarf, whole layer 6, positive, from d = 10 (conditioning outside the fp16 range) | — |

Rule 2 is not affected by the cut: the whole-layer-6 positive range is 2° with the dwarf measured up to d = 7 and the other
prompts up to d = 10.

## Reported

**Median total turn, positive doses to 10** (min–max over the 6 prompts): L06 MLP 72.6° (72–75); L14 MLP 80.5° (78–83);
L28 MLP 50.1° (48–53); whole layer 6 82.1° (81–83); L06 + L14 + L28 84.8° (84–87). Random controls at the same place:
L06 89.0°, L14 77.3°, L28 65.2°. The edit bends less than its random control at L06 and L28, **not at L14** (80.5° against
77.3°): C93's "the edit bends less than a random push" does not hold at every layer (C101 tests it at all 35).

**Positive heavy doses (4 → 10) add nothing new at the whole level.** The turn happens at small push length (share of
turning in the top third of |p|: median 0.007–0.012), steps stay small (median largest step 10–30°), no reversals: the
heavy doses extend the straight part.

**Past the sign flip the push changes direction.** Labels change in 9 of 60 trajectories, all at the "spiral"
threshold (rotation ≥ 90°): L14 MLP negative turns 37° up to −1 and 82° up to −3 (all six prompts); whole layer 6 and L06
MLP negative turn back (largest step 60–78°, up to 4 reversals). Per tap, 22 clips (one step ≥ 90°), **all at negative
doses**: 14 on the still life. Two places: between −0.8 and −0.9 for L06 MLP (the MLP is almost switched off there:
its three matrices are scaled by 0.2 and 0.1, and the push length jumps tenfold in one step), and between −1.5 and −2 for
the whole layer 6.

## Reading

One curve per edit: with prompts as different as a comic portrait, a rally car photo, a dreamlike scene, a four-panel
comic page, a cartoon still life and a macro leaf, the total turn of each edit varies by at most 7°. The bend is the
network's (random pushes have the same one-bend shape) and its size is the edit's (L28 turns least, the stacked edits
most). Positive doses can be pushed to 10 without new behaviour in the conditioning, until the whole layer 6 leaves the
fp16 range at d = 10. The negative side is not the mirror of the positive: near d = −1 the edited matrices approach zero
(an ablation) and past it they change sign, and there the push turns sharply.

## Tool rule

A dose curve calibrated once per edit can be used on any prompt. The negative knob needs a bound before −1,
where the edited matrices reach zero. Heavy positive doses are bounded by image damage, not by the shape of the push;
the whole layer 6 also by the fp16 range.

## Limits

Conditioning only, no renders: the shape says nothing about what the image does at these doses. Mean over tokens at the
whole level. Random controls for single-MLP positive edits only. The shape thresholds are C93's; the spiral threshold
(rotation ≥ 90°) is crossed by turns of 81–90°, so "spiral" labels here are at the margin.
