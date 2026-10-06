# C58 result — block 23 split in two: the registered measure did not see the noise; the eye did

2026-10-06. Pre-registration `docs/prereg_blk23_split.md` (+ amendment 1, doses ±1.0). Renders
`docs/RENDERS_2026-10-06_blk23_split.md`: 165 of 165; all five checks identical to the pixel (the eight
matrices through `granular_json` reproduce the whole block at −0.45, +0.30, −1.0, +1.0, so attention
+ MLP are the whole block and nothing else in it matters). Eye pass deposited before the measures
(`51ad771`): `data/blk23_split_eye_alessandro.csv`, key `data/blk23_split_eye_key.csv`; self-agreement
5 of 6 (noise) and 6 of 6 (saturation). Measures `data/blk23_split_measures.csv`, tests
`data/blk23_split_tests.csv`.

## Registered verdict: not decided at all four doses

The gate — the whole block adds noise by the Immerkær estimate in ≥ 10 of 16 cells — fails everywhere
(9, 0, 8, 4 of 16 at −0.45, +0.30, −1.0, +1.0), so H1, H2 and H4 are void and the thesis is "not
decided" by its own rule. H3 (the attention carries the colour) holds only at +0.30 (14/16); at −0.45,
−1.0 and +1.0 it is not supported (7/16 each).

## Why: the measure, not the eye, failed (pitfall 90)

Looked at before writing this (fox and oil-painted elf, all arms and doses): at **+1.0 the whole block
turns the picture into coloured confetti** — the subject is gone — and the registered measure calls it
*less* noisy than the baseline (median ΔN −0.30). The Immerkær estimate reads pixel-scale grain with a
3×3 mask; the confetti is made of blobs several pixels wide, and the sharp line art of the baselines
scores high on that mask. It measures fine grain, not the noise the eye sees. The registered verdict
stands as "not decided"; what follows is descriptive.

## What the eye and the images show (blind eye pass, descriptive)

| dose | "most noise" (16 sheets each) | "most saturated" |
|---|---|---|
| −1.0 | base 7, attention 5, whole 3, MLP 1 | MLP 9, whole 7 |
| −0.45 | base 10, attention 6 | whole 10, MLP 6 |
| +0.30 | whole 9, MLP 7 | base 13, attention 2, MLP 1 |
| +1.0 | **whole 16** | base 16 |

* **Pushed positive, the noise lives in the MLP.** At +1.0 the MLP alone gives a soft, mottled,
  woolly picture that has lost its line work; the attention alone gives a clean picture, desaturated;
  together they give confetti. At +0.30 Alessandro picked the whole block or the MLP as noisiest in all
  16 sheets, never the attention. This is his thesis, seen clearly, on the positive side.
* **Pushed negative, cutting the MLP makes the picture cleaner, not noisier:** the noisiest image was
  the baseline or the attention-only one, never the MLP-only one. Consistent with the thesis read the
  other way (less MLP, less noise).
* **The attention alone desaturates while keeping the picture** (not uniformly across hues: see the
  addendum). At +1.0: chroma −4.25 against −4.46 for the whole block,
  with layout r 0.80 against 0.36 (the whole block destroys the picture).
* **But the colour is not only in the attention.** Pushed negative (more colour), the MLP alone adds
  more chroma than the attention alone (median +2.8 against +1.8 at −0.45; +3.6 against +3.0 at −1.0),
  and Alessandro picked the MLP-only image as the most saturated in 15 of 32 sheets, the attention-only
  one in none. The block's colour is split between the two parts; the noise is not.

## What would make it a result

A noise measure that agrees with the eye first: validate candidates (multi-scale versions of the same
estimate, BRISQUE) against these 64 blind labels, exploratory; then a fresh pre-registered bench at new
seeds with the measure chosen before. The decomposition itself — attention desaturates cleanly at +1.0,
the MLP degrades — is the lead to confirm.

## Addendum (2026-10-06, after the result) — the attention's desaturation is not uniform across hues

Alessandro, looking at the images: "clean" is too strong; greens and light blues seem to stay lit more
than other hues. Measured on the 16 cells, descriptive (`data/blk23_split_hue_profile.csv`; CIELAB at
256×320, seven hue bins on the hue angle, pixels with chroma > 6; images are regenerated, so these are
distributions per hue, not pixel-to-pixel changes):

* **How strongly each hue is desaturated, where it stays coloured** (median ratio of mean chroma
  within the hue, attention alone at +1.0): red 0.73, orange 0.74, green 0.76, blue 0.76, yellow 0.81,
  cyan 0.82. Nearly even: cool hues keep slightly more in 10 of 15 cells, median +0.03.
* **How much of each hue stays coloured at all** (median ratio of the share of pixels in the hue,
  attention alone at +1.0): **red 0.28**, cyan 0.46, orange 0.63, blue 0.65, yellow 1.09, **green 1.25**.
  Reds lose most of their coloured area; green holds, and even grows.

So the attention's desaturation is uneven in *which hues survive* rather than in how much each is
dimmed: reds drop out first, greens and yellows remain. Light blues are mixed (cyan loses area, keeps
intensity). Caveat: some of the "green" gained may be neutral greys taking a slight green cast as they
lose colour; this was not separated. At +0.30 the pattern is weaker (red area 0.55, the others
0.83–1.10).
