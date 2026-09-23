# The recovered bench — what the HUD actually did

**Date**: 2026-09-23. Run log: `data/recovery_run_log.md`, revision 2.

The recovery worked: 555 images cropped to 555 distinct destinations, no collisions, all measured,
and the six recovered feature tables carry the original schema — 225, 210 and 330 rows, the same
keys and column names, so the frozen analyser reads them unchanged.

---

## 1. A mistake of mine, first, because it voids one comparison

`analyze_block1_vs_block6.py` writes each of its two outputs **twice**: once to the report's data
directory and once to the pilot's. My derived copy redirected only the two report constants. On
this machine the pilot path resolves to the same folder, so the un-redirected write landed on the
original filename.

**`data/rotations_block1_vs_block6_results.csv` and `..._prompt_scores.csv` were overwritten with
the recovered numbers.** Both files now have the same md5 and the same mtime as their `_recovered`
twins — which is why phase 5 printed the same table twice and why its closing line, "where they
agree the HUD never mattered", was a table compared with itself. Ignore it.

Nothing is lost: both files are committed. Restore with

```
git show HEAD:data/rotations_block1_vs_block6_results.csv       > data/rotations_block1_vs_block6_results.csv
git show HEAD:data/rotations_block1_vs_block6_prompt_scores.csv > data/rotations_block1_vs_block6_prompt_scores.csv
```

and re-check the published figures against the restored file rather than against this document,
which quotes them from the page text.

## 2. What the recovered run says

Same bench, same prompts, same seeds, same dose, same frozen analyser. Only the pixels differ.

| | published (HUD) | recovered (real pixels) |
| --- | ---: | ---: |
| same-block advantage V, primary space | +1.039 | **+1.108** |
| scramble null V_scr | +0.532 | **+0.274** |
| excess V − V_scr | +0.506 | **+0.834** |
| coherence `Block_1` | 0.949 | **0.942** |
| coherence `Block_6` | 0.958 | **0.977** |
| falsification criterion | passed | **passed, in all five spaces** |

**The HUD was inflating the null, not the effect.** The 480-pixel panel was identical in every
image, so it injected a shared component into every feature vector and made two arbitrary
scrambles look more alike than they are. Strip it and the control gets stricter: the null halves,
the advantage barely moves, and the excess the page actually rests on **nearly doubles**.

That is the opposite of what a contamination usually does, and it means the published result was
conservative rather than inflated.

## 3. A correction to what I told you on 2026-09-23

I reported that page 08's coherence claim did not survive, citing 0.616 against a published 0.949.
That reading was wrong in its attribution. The 0.616 comes from `rotations_matched_v3`, which runs
at **D = 0.0071**; the recovered bench at the registered **D = 0.045** gives **0.942**, essentially
the published number.

So the coherence of `Block_1` does not collapse because of the HUD. It collapses **with the dose**,
and that is a different claim with a different remedy. `block1-coheres-at-matched-displacement`
stands at the dose it was registered at, and the open question is whether it should have been
registered at a dose the later quality gate rejects.

## 4. Where the recovered run is still not clean

**The palette space is.** `palette_features` refused 24 images whose subject mask fell below 5%,
so **13 of 210** rows in the recovered b1b6 palette table and 13 of 330 in the triangle's keep
their contaminated values (`data/recovered_extraction_failures.csv`). The refusals are almost all
**`Block_6_pos`**. Treat the `Palette LAB/Chroma` and `Global 23 Features` rows of the recovered
results as unreliable until those images are handled by name.

The primary space is not affected: Texture is built from three style features, and the style
tables updated 225/225, 210/210 and 330/330.

**And the refusals are themselves a finding.** `Block_6_pos` at D = 0.045 drives the subject mask
under 5% in ten prompts of ten. That is independent of the HUD and it agrees with what
`rotations_matched_v3` found at a seventh of the dose: the last block group at the registered dose
is outside the usable regime, and the evidence for it now comes from two unrelated measurements.

## 5. The twelve-prompt secondary run

| space | V | 12 prompts positive | p | V_scr | excess | p of excess |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Texture (primary) | +1.017 | 12 / 12 | 0.000488 = floor | **+0.925** | +0.092 | 0.333 |
| Linework | +0.484 | 10 / 12 | 0.0054 | +0.034 | +0.450 | 0.016 |
| Shadow | +1.499 | 11 / 12 | 0.00098 | +0.055 | +1.444 | 0.00098 |
| Palette | +0.607 | 11 / 12 | 0.00098 | +0.645 | −0.038 | 0.709 |

At v3's dose the null is **+0.925 against an effect of +1.017** and the excess is not significant.
At the registered dose on recovered pixels the null is +0.274 against +1.108. Two doses, two
completely different pictures of what an arbitrary perturbation does — which is candidate pitfall
72 again, now visible in the null rather than in the sign.

Still secondary, still not confirmatory: the twelve-prompt corpus mixes two prompt families, and
`scrB` is degraded in all of it.

## 6. `all_blocks_clean_v2`, with the keying bug fixed

Response magnitude, antisymmetric, primary space — now monotonic in angle for every block, which
it was not before the fix:

| block | low | mid | high |
| --- | ---: | ---: | ---: |
| B1 | 0.119 | 0.397 | 0.898 |
| B2 | 0.092 | 0.087 | 0.134 |
| B3 | 0.170 | 0.259 | 0.386 |
| B4 | 0.141 | 0.183 | 0.441 |
| B5 | 0.070 | 0.112 | 0.166 |
| **B6** | **0.634** | **1.651** | **3.706** |

*(My earlier note that B3 decreases with angle was an artefact of the same keying bug. It does not.)*

Separability, 45 block pairs: the three pairs at the exact floor are **B1–B6 (−0.514)**,
**B1–B2 (−0.481)** and **B1–B4 (−0.462)**, all at mid angle. `Block_1` separates from three
different groups by about the same amount. That weakens the reading in which B1 and B6 form a
special pair: on this corpus B1 is simply unlike most things, and B6 is mostly bigger.

Which sits against phase 7's ratio finding, where B1 and B6 were the closest of all fifteen pairs.
Two statistics on the same corpus pointing different ways is exactly the state that deserves a
designed test rather than a preferred reading.
