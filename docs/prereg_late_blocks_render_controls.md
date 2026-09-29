# Test spec — are blocks 22–27 near-linear "rendering" controls?

**Deposited 2026-09-29, before any of the quantities below was computed for this claim.**

## The claim, verbatim

Alessandro: *"I blocchi dal 22 al 27 sono quasi controlli lineari (cambia pochissimo il soggetto e
moltissimo la resa). 22: Vividezza del colore · 23: Saturazione del colore · 24: Contrasto ·
25: Texture (da valutare, anche su questo ho dubbi) · 26: Sharpness (da valutare, su questo ho dei
dubbi) · 27: Focus (focal point / messa a fuoco)."*

## What the analyst had already seen — not blind

`data/single_blocks_map.csv` (committed `de69c1c`) printed, per block, the saturation ratio and the
three most consistent features. So **for 22 (vividness) and 23 (saturation) the analyst has seen
related numbers**; for 24–27 and for "subject change" he has not. The replication on
`benchmark_profondita` (H4) has not been looked at for any block.

## Measures — one per word, fixed now

| block | his word | measure | source |
|---|---|---|---|
| 22 | vividezza | `colorfulness_hs` (Hasler–Süsstrunk colourfulness: the standard "vividness" statistic) | cached |
| 23 | saturazione | mean HSV saturation | `retro_texture_axes.measure()`, cached as `sat` |
| 24 | contrasto | RMS contrast: standard deviation of luminance | computed |
| 25 | texture | `lbp_entropy` (local-binary-pattern entropy, micro-texture) | cached |
| 26 | sharpness | `fft_high_freq_share` (share of spectral energy at high frequency) | cached |
| 27 | focus | **concentration of sharpness**: coefficient of variation, over a 16×20 grid of tiles, of the tile-mean \|Laplacian\| — high when sharp detail is concentrated in part of the frame, as with a focal point | computed |
| all | "cambia pochissimo il soggetto" | **layout similarity**: Pearson r between render and baseline, grey, downsampled 16× (64×80), standardised | computed |

## Hypotheses

- **H1 — two poles on its own axis.** For each block b in 22–27, on its own measure m_b:
  (m(+0.350) − m(0)) and (m(−0.350) − m(0)) have **opposite signs on all three prompts**. Direction
  not predicted — he did not say which way.
- **H2 — specificity: each block is the knob for its own word.** Swing S[b, m] = mean over prompts of
  (m(+) − m(−)) / m(0), standardised per measure by its SD across all 28 blocks. For each of the six
  blocks: **(a)** among the six measures, is |z| largest on its own? Chance 1/6; count k/6, exact
  binomial. **(b)** among the 28 blocks, where does it rank on its own measure? Top-3 counts as a hit.
- **H3 — subject preserved.** Mean layout similarity (over 3 prompts × 2 signs) is **higher for
  blocks 22–27 than for blocks 0–21**. Exact one-sided Mann–Whitney, 6 vs 22.
- **H4 — replication at another dose and seed.** On `benchmark_profondita` (±0.200, seed 42, P01 and
  P02) against the seed-42 baselines in `benchmark_latenti_b6` (settings checked from the PNG graph
  before use): for each block, does its own measure move in the **same direction** as in the atlas,
  arm by arm? Count out of 6 blocks × 2 arms × 2 prompts = 24.

**"Linear" cannot be tested**: the atlas has one dose per arm. H1 tests two poles through the
baseline, which is necessary for a linear control but not sufficient.

## Verdict rule

A block's label is **supported** if it passes H1 **and** H2(a) **and** H4 on at least 3 of its 4
arm × prompt cells. **Partly supported** if H1 and H4 pass but another measure moves more (H2a
fails). **Not supported** otherwise.
