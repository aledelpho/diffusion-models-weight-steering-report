# C77 result — layer 0 of the text encoder switched off (replication of the C64 observation)

2026-10-14. Rule and prediction: docstring of `experiments/te_layer0.py`, committed (7e8b25d) before any render.
Renders: `Text2Img\benchmark_te_layer0` (log `docs/RENDERS_2026-10-14_te_layer0.md`). Gate: the C64 elf re-rendered,
max abs diff 0.

**Readings below were confirmed by Alessandro on 2026-10-17** (`docs/te_layer0_contact_sheet.jpg`).

| prompt (seed 1618033) | attention × 0 | MLP × 0 |
|---|---|---|
| D1 dwarf, comic | text ("close-up") | no text: tiled pattern |
| R6 dragonborn, comic | text ("...style, close-u", "fronto") | no text: tiled pattern |
| D1W dwarf, watercolour | text ("close-up", "frontal view") | text ("experXon", likely *expression*) |

**Verdict by the rule: 4 of 6, open** (holds at 5 or more, fails at 3 or fewer; visual inspection confirmed by Alessandro on 2026-10-17).

* With the C64 elf: attention off gives text in 4 of 4 prompts, MLP off in 2 of 4.
* The C64 elf page (MLP off) is the cleanest case. The new pictures are text inside heavy coloured noise.

## Exploratory, outside the plan: the whole layer off

Run by Alessandro the same day (`Text2Img\benchmark_te_layer0_block`, `experiments/te_layer0_block.py`), same four
prompts and seed, all seven matrices of layer 0 × 0 (verified in the PNG metadata). **No text in 4 of 4**: tiled,
repeating coloured patterns.

This weakens the reading of the C64 notes ("without layer 0 the encoder keeps token identity and loses meaning, so
the DiT writes the words"): skipping the whole layer passes the raw token embeddings on, and should then give the
clearest text, yet it gives none. Text appears only with half of the layer still working.

## Encoder-side check: scale, massive activations, and token identity across the 12 taps

Checked on 2026-10-17 with `experiments/te_layer0_encoder.py` (baseline bit-exact gate `max_abs_diff = 0.0`; tuner gate against C67 `CHK_active_L02_mlp_p1.00.npz` `max_rel_err = 0.000297 <= 0.000977`; outputs `data/te_layer0_encoder_by_tap.csv` and `data/te_layer0_encoder_summary.csv`, averaged over the 4 prompts `P1_elfbrawler`, `D1_dwarf_paladin`, `R6_dragonborn_cleric`, `D1W_dwarf_paladin_watercolor`):

| condition | Tap 0 (`L02`) L2 norm (ratio) | Tap 1 (`L05`) L2 norm (ratio) | Tap 11 (`L35`) L2 norm (ratio) | mean norm ratio (12 taps) | mean `big2 / median` (12 taps) | Tap 0 (`L02`) Logit-Lens self top-1 / top-5 |
|---|---|---|---|---|---|---|
| `baseline` | 11.80 (1.0000×) | 22.64 (1.0000×) | 548.77 (1.0000×) | 1.000× | 53.7 | 0.5120 / 0.6920 |
| `L00_attn_m1.00` (attention × 0) | 10.02 (0.8513×) | 18.63 (0.8239×) | 591.53 (1.0779×) | 0.984× | 67.1 | 0.5189 / 0.6646 |
| `L00_mlp_m1.00` (MLP × 0) | 8.81 (0.7464×) | 16.09 (0.7093×) | 537.52 (0.9795×) | 0.841× | 63.8 | 0.6185 / 0.7566 |
| `L00_block_m1.00` (whole block × 0) | **127.17 (10.8005×)** | **1401.81 (62.0284×)** | **1704.44 (3.1067×)** | **21.688×** | **14.8** | **0.0000 / 0.0000** |

* **Whole layer off (`L00_block_m1.00`), no text in the picture:** the conditioning is far from normal. Its norm is
  10.8× the baseline at tap 0 (L02) and 62.0× at tap 1 (L05), 21.7× on average over the 12 taps; its direction
  is unrelated to the baseline (cosine −0.06 at tap 0); the ratio of the largest channels to the median falls from
  53.7 to 14.8; and the logit lens recovers no token's own identity at any tap (top-1 and top-5 = 0).
* **Half of the layer off, text in the picture:** the conditioning keeps a near-normal scale (0.98× and 0.84× on
  average) and its largest channels (ratio 67.1 and 63.8), and at tap 0 the logit lens still recovers the token's
  own identity in 51.9 % (attention off) and 61.9 % (MLP off) of positions, against 51.2 % for the baseline.
* **Reading, not tested:** the picture writes the prompt when the conditioning keeps the identity of the tokens
  at a normal scale but has lost part of what layer 0 adds; with the whole layer gone, scale and identity are both
  lost and the picture turns to noise. This fits the measurements but is not shown by them: no experiment varies
  scale and identity separately.

## Limits

One seed, four prompts, readings not blind. No claim is added to the results pages.
