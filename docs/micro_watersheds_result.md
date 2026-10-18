# C96 result — micro-watersheds: minimal edits flip the same small regions

2026-10-18. Pre-registration `docs/prereg_micro_watersheds.md` and script `experiments/micro_watersheds.py`, committed
together (74f0071) before the run; the T2 statistic was changed before any real data was read, after the selftest
showed the first one missed sparse flips (both noted in the files; the selftest has a positive and a negative case:
0.44 against −0.05). No new renders: the archer at seed 3141592, 26 minimal edits (C56 doses 0.01–0.04 on blocks
00, 10, 20, 23, both signs; C55 block 27 ±0.004, one bf16 step on every weight) and 16 larger ones (0.08, 0.16).
Baseline checked pixel-identical to C55 N0. Outputs `data/micro_watersheds_edits.csv`, `_pairs.csv`, `_tests.csv`;
maps and crops in `Text2Img/_micro_watersheds/`.

## Verdicts

| test | value | rule | verdict |
|---|---|---|---|
| T1 — the change is carried by flips (Δ ≥ 32), not a shimmer | flip share ≥ 0.50 in **26 of 26** small edits, median 0.69 | ≥ 2/3 | supported |
| T2 — the same places flip, baseline texture removed (primary) | median partial correlation **0.506** over 325 pairs (without the texture control 0.682) | ≥ 0.30 | **supported** |
| T3 — recurring patches hold two alternatives | 217 of 258 with bimodality coefficient > 0.555 (median 0.68) | ≥ 50% | supported, with a caveat |

T2 holds across different blocks (0.500, 264 pairs) and across opposite signs (0.500, 169 pairs): pushing the weights
of block 00 down or block 23 up reshuffles largely the same places. Same block and sign: 0.692.

## What flips (looked at, Claude, conditions known)

* **One rounding step on every weight of block 27 makes an object appear.** The largest flip region of blk27 +0.004
  (3,724 pixels) is the arrow's fletching next to the drawing hand: plain shaft in the baseline, white and black
  feathers in the edit. Block 00 −0.010 does the same at the same place (5,199 pixels). The flip is discrete: the
  feathers are there or not.
* **The places that flip most often** (map `flip_frequency_overlay.png`, small edits) are discrete details: the
  fletching, the bowstring, the quiver feathers by the head, the tips of the fir branches, the bracer, the hood edge.
* **Part of the flips are moved edges.** 69–75% of flip pixels of the small edits lie in the 36% of the picture next to
  strong edges; a stroke shifted by a pixel or two gives a large Δ along it. But 77–79% of the flip energy sits in a
  few connected regions of ≥ 256 pixels (4–19 per small edit), which is where the objects above appear.

## Caveats

* **T3 is weaker than it looks.** The bimodality coefficient is also high for a distribution that is only skewed —
  most edits like the baseline, a few scattered elsewhere. "Two solutions" is supported by the fletching (seen) more
  than by the coefficient.
* **One prompt, one seed, and a seed chosen because it sits on a watershed** (the hood). It may be more fragile than
  most. The texture control is linear and coarse (16-pixel patches); edges are only partly removed.
* **What decides the places is not tested.** The starting noise, the content (fletching is an object the prompt asks for
  and the model draws or not), and the 16-pixel token grid are all candidates.

## Reading

Alessandro's hypothesis holds on this picture: the smallest change the weights can take does not shift everything a
little, it tips a set of details that sit between two versions, and the same details tip whatever block is pushed and
in whichever direction. The half-formed hood is the large, visible member of a family of small watersheds spread over
the picture. Every edit in this report carries this reshuffling along with its intended effect (page 22 said it for the
hood; this measures it for the whole picture).

## Next (renders, to approve)

The same tiny edits on several seeds of two prompts, with the initial latent noise saved: do the fragile places follow
the noise, the content, or the token grid?
