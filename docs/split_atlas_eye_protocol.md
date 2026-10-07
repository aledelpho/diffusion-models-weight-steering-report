# C59 eye pass — protocol

2026-10-07. Written after the split atlas measures (`docs/split_atlas_result.md`) and before any label.
Asked for by Alessandro: an eye pass on the artefacts, with a classification and an intensity per class.

## What is shown

Seed 2718281 only (the seed where the whole block exists; Alessandro reports that what happens at one
seed repeats at the others). One sheet = one block × condition (attention, MLP, whole) × sign (±0.35),
the three prompts side by side at full resolution: 28 × 6 = 168 sheets. Blind: anonymous file names,
order shuffled (rng 59), 20 sheets shown a second time later in the sequence, unannounced, for
self-agreement. The three baselines are one key press away (Space). Built by
`experiments/split_atlas_eye.py --build`; key `data/split_atlas_eye_key.csv`, committed before any label.
Page and images: `Text2Img/benchmark_split_atlas/eye_test/eye_test.html` (not in the repo).

## What is asked

For each of eight classes, absent or lieve / medio / forte; or "Nessun artefatto"; plus "non in tutti e
tre i prompt" and a free field for other attributes. The classes come from my own look at the contact
sheets (`docs/split_atlas_result.md`), not from a literature:

| key | class | example shown before the test |
|---|---|---|
| chiazze | mottled noise (blotches of tens of pixels, image still readable) | P01, seed 3141592, block 26 attention + |
| grana | fine grain | F4, seed 4669201, block 27 attention + |
| collasso | collapse into noise | C2 rally, C58, whole block 23 at +1.0 |
| retino | regular dot or line screen | S1, seed 3141592, block 27 MLP − |
| poster | posterisation / colour blocks | F4, seed 3141592, block 0 attention − |
| sostituito | content replaced / abstract | P01, seed 3141592, block 0 MLP − |
| morbido | softening / blur | none (description only) |
| tratteggio | stronger hatching | none (the candidate I picked did not show it) |

The examples are from other seeds or another test, never from the sheets themselves. They show the
same block and part as some test sheets, so they prime recognition of a kind of artefact, not of a label:
the sheet never says which block or part it is.

## What will be reported (fixed now, descriptive)

1. Self-agreement on the 20 repeats, per class: presence (any intensity) and exact intensity. A class
   whose presence agreement is below 0.8 is reported but not used for the comparisons below (pitfall 89).
2. Map: for each block, part and sign, the intensity per class (first showing).
3. Where the noise sits (chiazze, grana, collasso, retino): per block, attention vs MLP at the same sign.
4. Whole vs halves: sheets where the whole block's intensity in a class exceeds both halves'.
5. Measures against the eye: for presence of any noise class, the ranking of page 05's HF ratio and of the
   post-hoc band ratio (AUC per measure), on the 504 per-prompt rows of seed 2718281 — a sheet counts as
   noisy for all three prompts unless "non in tutti e tre" is ticked, in which case it is left out.

Labels: `data/split_atlas_eye_alessandro.csv`, committed as downloaded before `--tally` runs.
