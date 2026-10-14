# C77 result — layer 0 of the text encoder switched off (replication of the C64 observation)

2026-10-14. Rule and prediction: docstring of `experiments/te_layer0.py`, committed (7e8b25d) before any render.
Renders: `Text2Img\benchmark_te_layer0` (log `docs/RENDERS_2026-10-14_te_layer0.md`). Gate: the C64 elf re-rendered,
max abs diff 0.

**Readings below are Claude's, pending Alessandro's confirmation** (the rule names him as the judge).

| prompt (seed 1618033) | attention × 0 | MLP × 0 |
|---|---|---|
| D1 dwarf, comic | text ("close-up") | no text: tiled pattern |
| R6 dragonborn, comic | text ("...style, close-u", "fronto") | no text: tiled pattern |
| D1W dwarf, watercolour | text ("close-up", "frontal view") | text ("experXon", likely *expression*) |

**Verdict by the rule: 4 of 6, open** (holds at 5 or more, fails at 3 or fewer).

* With the C64 elf: attention off gives text in 4 of 4 prompts, MLP off in 2 of 4.
* The C64 elf page (MLP off) is the cleanest case. The new pictures are text inside heavy coloured noise.

## Exploratory, outside the plan: the whole layer off

Run by Alessandro the same day (`Text2Img\benchmark_te_layer0_block`, `experiments/te_layer0_block.py`), same four
prompts and seed, all seven matrices of layer 0 × 0 (verified in the PNG metadata). **No text in 4 of 4**: tiled,
repeating coloured patterns.

This weakens the reading of the C64 notes ("without layer 0 the encoder keeps token identity and loses meaning, so
the DiT writes the words"): skipping the whole layer passes the raw token embeddings on, and should then give the
clearest text, yet it gives none. Text appears only with half of the layer still working. Why is not known. A
candidate, not checked: early layers of Qwen-family models build a few very large activations that later layers
rely on (Sun et al. 2024, "Massive activations"); without them the conditioning may arrive at the wrong scale.

## Limits

One seed, four prompts, readings not blind. No claim is added to the results pages.
