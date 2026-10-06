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

## Addendum 2 (2026-10-06) — the fine-texture cost of notebook page 05, split

Question (Alessandro): does the "cost" that page 05 found in every block push — fine texture lost in
either direction, the common mode — remain when only the attention is moved? Same measure as page 05:
HF = std(gray − GaussianBlur(gray, σ = 1.5)), r± = HF±/HF_base, **common mode c = √(r⁺ r⁻)** (the cost;
below 1 = texture lost whichever way you push), swing s = r⁺/r⁻ (the steering). Descriptive, after the
fact, on the C58 renders (`data/blk23_split_common_mode.csv`). The C47 doses are asymmetric (+0.30 /
−0.45), so their common mode is an approximation of page 05's symmetric one; ±1.0 is symmetric.

| block 23 | r⁺ | r⁻ | common mode | cells below 1 |
|---|---|---|---|---|
| page 05, whole block, ±0.20 (6 renders per arm) | 0.864 | 1.035 | 0.945 | — |
| **whole block**, +0.30 / −0.45 | 0.866 | 1.065 | **0.933** | 11 / 16 |
| **attention only**, +0.30 / −0.45 | 1.051 | 0.943 | **0.991** | 10 / 16 |
| **MLP only**, +0.30 / −0.45 | 0.807 | 1.161 | **0.967** | 11 / 16 |
| whole block, ±1.0 | 1.449 | 0.989 | 1.195 | 2 / 16 |
| attention only, ±1.0 | 1.243 | 0.897 | 1.057 | 3 / 16 |
| MLP only, ±1.0 | 0.525 | 1.222 | 0.788 | 12 / 16 |

* **At the bench doses the cost reproduces for the whole block** (0.933, against 0.945 on page 05)
  and **almost vanishes for the attention alone** (0.991: about 1% of fine texture instead of about
  7%); the attention's common mode is closer to 1 than the whole block's in 12 of 16 cells. The MLP
  alone keeps about half of it (0.967).
* **The MLP is the texture knob of block 23**: pushed up it smooths (r⁺ 0.81, 0.53 at +1.0), pushed down
  it etches (r⁻ 1.16, 1.22) — a strong swing, the same direction as the whole block's. The attention's
  swing on texture is small and the other way (r⁺ 1.05, r⁻ 0.94).
* **At ±1.0 the measure changes meaning**: the whole block's confetti adds high-frequency energy
  (r⁺ 1.45), so its "common mode" rises above 1; that is destruction, not texture gained.

So the cost page 05 treated as unavoidable in a block push is, for block 23 at these doses, mostly not
in the attention: it comes from the MLP and from moving both together. One block, one measure of fine
texture, not pre-registered; whether the same split holds for other blocks is open.
