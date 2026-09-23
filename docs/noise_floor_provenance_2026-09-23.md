# The noise floor, reproduced from the images for the first time

2026-09-23 · one new script, two new data files · **no published claim was changed**

`sigma(HF)` — how much high-frequency pixel energy varies between two renders that differ
only by their random seed — is the constant nearly every threshold in this notebook is
quoted against. Page 05 reports results "at 11 to 14 times the noise floor"; page 00
publishes the floor itself as a passing bench check. Until today no script in the repository
computed it. It existed as prose in `docs/punto7_attrito_e_rettificazione.md` §7 and as
hand-typed rows in `data/bench_checks.csv` and `data/noise_floor_history.csv` — the same
provenance status that `Delta L* = -3.30` had before `experiments/stage9_preset_shift.py`,
but with a far wider blast radius, because this constant calibrates other pages' thresholds.

It now reproduces exactly.

## 1. The bench, and where the 18 seeds actually come from

`benchmark_pavimento_rumore` is at
`C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_pavimento_rumore` — under
`Data\Images\Text2Img\`, not under `Data\Packages\ComfyUI\output\` where the HUD census
worked. It holds 32 PNG and 32 `.latent`: two prompts at seeds 42 and 101–115. Every render
is **1024 x 1280**, so the bench is clean and appears nowhere in
`data/hud_contaminated_images.csv`.

That is **16** seeds per prompt, and the notebook publishes **18**. The missing two are not
missing: they are in `benchmark_latenti_b6/renders`, the three pre-registered baselines at
seeds 42, 777 and 1337 named in `docs/prereg_punto7_simmetria_segno.md` §1. Seed 42 is in
both benches. So the corpus is

    benchmark_latenti_b6        seeds 42, 777, 1337
    benchmark_pavimento_rumore  seeds 42, 101..115
    distinct seeds per prompt   18      pairs  C(18, 2) = 153

and the published n is correct. The script asserts that the two seed-42 renders are
**pixel-identical** (they are; only their `tEXt` ComfyUI graphs differ, which is why an early
check on file hashes failed) and counts seed 42 once. Counting it twice would inject a
zero-variance duplicate and understate the sigma — pitfall 17 in miniature.

What is wrong is the Provenance line on page 00, which credits the 18-seed floor to
`benchmark_pavimento_rumore` alone. That bench supplies 16 of the 18.

## 2. The measure

Frozen in `docs/prereg_punto7_simmetria_segno.md` §1 before the data were seen, and
reproduced verbatim by the new script rather than re-invented:

```
g  = cvtColor(imread(file), COLOR_BGR2GRAY).astype(float32)
HF = std( g - GaussianBlur(g, ksize=(0,0), sigmaX=1.5) )
```

The floor is, per prompt, the sample standard deviation of HF across the 18 distinct
baseline seeds (ddof = 1), divided by the mean, in percent.

## 3. The result

| prompt | n seeds | pairs | mean HF | sd | relative sigma | published |
|---|--:|--:|--:|--:|--:|--:|
| P01 | 18 | 153 | 12.6754 | 0.2087 | **1.6468%** | 1.65% |
| P02 | 18 | 153 | 19.0735 | 0.3493 | **1.8313%** | 1.83% / 1.84% |

Written to `data/noise_floor_measured.csv`; the 38 per-render rows, with bench, seed,
resolution, HF, duplicate flag and sha256, to `data/noise_floor_hf_by_render.csv`.

P01 reproduces to the published digit. **P02 rounds to 1.83%, not 1.84%.**

## 4. One digit is wrong in four places

`docs/punto7_attrito_e_rettificazione.md` §7, the primary source, says 1.83%, and page 05
says 1.83% twice. Page 00 says 1.84% three times (the verdict, the checks table, the
history table) and so do `data/bench_checks.csv` and `data/noise_floor_history.csv`. The
measurement settles it at 1.8313%.

Places to correct, if the correction is wanted:

| file | what it says | should say |
|---|---|---|
| `notebook/00-the-bench.md` claim `evidence` | 1.84% on P02 | 1.83% |
| `notebook/00-the-bench.md` verdict prose | 1.84% on P02 | 1.83% |
| `notebook/00-the-bench.md` checks table | **1.84%** | **1.83%** |
| `notebook/00-the-bench.md` history table | **1.84%** (P02) | **1.83%** (P02) |
| `notebook/00-the-bench.md` F00.3 alt text | 1.65 and 1.84 percent | 1.65 and 1.83 percent |
| `data/bench_checks.csv` `noise_floor` P02 | 1.84 | 1.83 |
| `data/noise_floor_history.csv` estimate 4 | 1.84 | 1.83 |
| `experiments/notebook_charts.py` F00.3 subtitle | 1.65% and 1.84% | 1.65% and 1.83% |

None of this was applied. It changes a published number and therefore belongs to a decision,
not to a script.

## 5. Two corollaries about the retracted estimates

`data/noise_floor_history.csv` rows 1 and 2 have the weakest provenance in the file
(`source = data/bench_checks.csv note`). Both can now be sourced properly from
`docs/prereg_punto7_simmetria_segno.md`:

* **1.15%** — §1 of the pre-registration: "la deviazione relativa dell'HF del baseline fra
  seed vale 0.27% su P01 e 2.03% su P02, sigma tipico 1.15%", on the three seeds 42/777/1337.
  It is the mean of the two per-prompt figures, not a pooled sigma. Reproducible from the
  six `benchmark_latenti_b6` baselines.
* **5.20%** — the addendum at §177: sigma measured on a different corpus, three prompts,
  giving 3.26% (P2), 4.93% (P3), **5.20% (P1)**. So "borrowed from other prompts" is right,
  and the borrowed figure is identifiable: it is the P1 of that other corpus.

Neither of the two retracted estimates is a mystery any more. The `source` column of
`data/noise_floor_history.csv` can point at the pre-registration instead of at a note.

## 6. A by-product worth keeping

Before the pre-registered definition was found, the floor was looked for among the 23 numeric
features of `experiments/style_features.py`, on the same renders. Nothing lands on 1.65 /
1.83: `fft_high_freq_share`, the obvious candidate, gives 6.96% and 9.28%; the closest pair
is `color_cluster_entropy_norm` at 1.50% / 1.11%. That table is
`data/noise_floor_feature_cv_scan.csv`. It is negative evidence with a use: the floor is
**not** a `style_features` quantity, and the next person to assume it is will find out here
instead of by rebuilding it.

## 7. What is now closed and what is not

Closed: the floor has a script, the script reproduces both published values from the images,
the declared n = 18 and 153 pairs are correct and their corpus is identified, and the two
retracted estimates have real sources.

Applied the same day, once the reproduction settled them:

1. **1.84 -> 1.83** in all eight places (`notebook/00-the-bench.md` x5, `data/bench_checks.csv`,
   `data/noise_floor_history.csv`, the F00.3 subtitle in `experiments/notebook_charts.py`, and
   the alt text in `experiments/figures.yaml`). Nothing of this notebook has been published
   anywhere yet, so the digit was corrected rather than annotated: a reader is better served by
   the right number than by an asterisk on a wrong one nobody ever saw.
2. **The Provenance line on page 00** now credits both benches, 32 renders from
   `benchmark_pavimento_rumore` and 4 from `benchmark_latenti_b6`, and `corpus.renders` went
   from 423 to 427 with the status line to match.
3. **`data/noise_floor_history.csv`** now sources rows 1 and 2 from
   `docs/prereg_punto7_simmetria_segno.md` and rows 3 and 4 from `data/noise_floor_measured.csv`
   instead of from a note in another CSV.
4. **The F00.3 reference line stops being typed.** It was `axhline(1.745)` with the label
   "1.75%", a constant that would have silently disagreed with the file after the correction; it
   is now the mean of the rows marked `current`.
5. **`extract_repro.py`** reads `data/noise_floor_hf_by_render.csv` for this page, so the
   resolution field of the reproduction block is proven for 38 of the 427 renders instead of
   nothing.

Still open, and both are honest gaps rather than errors:

* `experiments/measure_bench.py` is named in the reproduction block and in Provenance and is not
  in the repository; the sha256 beside it is the hash of a file nobody can produce. Nine of the
  eleven rows of `data/bench_checks.csv` have no code behind them.
* Page 05 named three scripts that do not exist -- `verifica_punto7.py`,
  `run_pavimento_rumore.py`, `analisi_modo_comune.py` -- for the 28 rows of
  `data/punto7_blocks.csv`. The Provenance line now says so instead of naming them.

## Provenance of this note

* Benches read: `benchmark_pavimento_rumore/renders` (32, all 1024x1280),
  `benchmark_latenti_b6/renders` (6 baselines used of 18 files)
* Script: `experiments/measure_noise_floor.py` (new)
* Data written: `data/noise_floor_measured.csv`, `data/noise_floor_hf_by_render.csv`,
  `data/noise_floor_feature_cv_scan.csv`
* Definition source: `docs/prereg_punto7_simmetria_segno.md` §1 (pre-registered)
* Value source: `docs/punto7_attrito_e_rettificazione.md` §7
* Not touched: `notebook/*.md`, `data/bench_checks.csv`, `data/noise_floor_history.csv`
