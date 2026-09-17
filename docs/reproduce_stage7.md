# Reproducing stage 7

Stage 7 is the confirmation round behind §1.5 and §1.6: 600 renders at 1024 × 1280, across 16 prompts
that share nothing with any earlier stage. This file has everything needed to get from the base
checkpoint to the numbers in those two sections.

**Three levels, pick the one you need.** To re-run the statistics, use the published feature CSVs — no
GPU, no download, a few seconds. To check that the features were extracted correctly, regenerate the
renders from the recipe below and re-run the extractors. To check the recipe itself, the seven presets
are in this repository and are 50–60 KB each.

## Where the renders are

All 600 are published, in two forms, because the two analyses in §5 have different needs.

* **Browsable, in this repository** — every render at 480 × 600, webp quality 82, under
  [`assets/01_steering_stage7/`](../assets/01_steering_stage7/), laid out as
  `<cond_name>/<prompt_id>_<tag>_<prompt_sha1>/<seed>.webp`. The baselines of all **24** candidate prompts
  are there, not only the 16 selected, so that the selection step can be checked rather than trusted.
* **Full resolution, as a release asset** — the 600 original PNGs at 1024 × 1280 in a single archive
  attached to the tagged release ([`stage7-confirmation`](https://github.com/aledelpho/diffusion-models-weight-steering-report/releases/tag/stage7-confirmation)), with its sha256 published below. They are not committed to the
  repository: a gigabyte of binaries in git history is permanent, and a release asset is not.

**Use the PNGs for anything to do with colour.** §5.1 measures chroma and hue, and webp at quality 82
shifts both; re-extracting palette features from the webp would reproduce the analysis on degraded input.
§5.2 is about stroke orientation, which is structure rather than colour, and survives the webp fine.

## What was rendered

| | |
| --- | --- |
| Base model | Krea-2 Turbo (12.8 B MMDiT, 28 blocks) |
| Sampler | `euler_ancestral` |
| Steps | 9 |
| CFG | 1.0 |
| Size | 1024 × 1280 |
| Seeds | 42, 777, 1337, 9999, 4242145 |
| Suite commit | `ba28b12532175220` |

Two passes:

* **Stage 7a** — 24 candidate prompts, **baseline only**, 5 seeds = 120 renders.
* **Stage 7b** — the 16 prompts chosen from them, **six conditions**, 5 seeds = 480 renders.

The 16 were picked by [`experiments/select_confirmation_prompts.py`](../experiments/select_confirmation_prompts.py),
which reads only the baseline renders and breaks ties on `prompt_sha1` in lexicographic order, so that
no judgement enters the selection. Its output is [`data/confirmation_prompts.csv`](../data/confirmation_prompts.csv).

## The six conditions

Every condition is the same base checkpoint plus one preset applied through
[Arthemy-Krea2-Tuner](https://github.com/aledelpho/comfyui-arthemy-krea2-tuner), all matched to the
identical relative Frobenius displacement **D = 0.0538**.

| `cond_name` | `operation` | preset file |
| --- | --- | --- |
| `preset_pos` | `preset` | `Arthemy_Bench_Base.json` |
| `preset_neg` | `preset` | `Arthemy_Bench_NEG.json` |
| `blockshuf_pos` | `preset_blockshuffle` | `Arthemy_Bench_BLOCKSHUFFLE.json` |
| `blockshuf_neg` | `preset_blockshuffle` | `Arthemy_Bench_BLOCKSHUFFLE_NEG.json` |
| `rand_pos` | `preset_randsign` | `Arthemy_Bench_RANDSIGN.json` |
| `rand_neg` | `preset_randsign` | `Arthemy_Bench_RANDSIGN_NEG.json` |

`Arthemy_Bench_HALF.json` is published too — it is the half-amplitude preset used in earlier stages and
is **not** part of the stage 7 test.

## The prompts

Full verbatim text for all 24 candidates, with `prompt_sha1`, seed and output filename for every render,
is in the manifests:

* [`data/stage7a_images.csv`](../data/stage7a_images.csv) — 120 rows
* [`data/stage7b_images.csv`](../data/stage7b_images.csv) — 480 rows

`prompt_sha1` is the first ten hex characters of `sha1(prompt_text)`. **Prompts are never edited** — not
shortened, not improved, not re-punctuated. That hash is how anyone, including the author, can prove it.

## Regenerating the renders

```
python experiments/run_stage7a.py     # 24 prompts, baseline only, 120 renders
python experiments/select_confirmation_prompts.py \
    --baselines palette_features_stage7a_candidates.csv \
    --out confirmation_prompts.csv
python experiments/run_stage7b.py     # the 16 selected, 6 conditions, 480 renders
```

Output naming is `renders/<PROMPT_ID>_<cond_name>_seed<SEED>_00001_.png`. The extractors below verify
that the seed in the filename matches the seed in the manifest and stop if it does not.

**One trap worth knowing about**: a 228-render pilot from two days earlier, unrelated to this test, also
wrote into `benchmark_stage7\renders` under an `S7_` prefix, and on disk its manifest was also called
`stage7_images.csv`. Any harvester pointed at that folder — or at that filename — measures the wrong images
and reports a clean run. Both extractors here read the manifest and never the directory, and the pilot's
manifest is published under an unambiguous name, [`data/stage6b_pilot_images.csv`](../data/stage6b_pilot_images.csv),
so the collision cannot be inherited by anyone reading this repository.

## Re-measuring, without regenerating

```
python experiments/palette_from_manifest.py \
    --manifest data/stage7b_images.csv --renders-root <renders> \
    --out palette_features_stage7.csv

python experiments/style_from_manifest.py \
    --manifest data/stage7b_images.csv --renders-root <renders> \
    --also "data/stage7a_images.csv=<renders 7a>" \
    --out style_features_stage7.csv
```

## Rerunning the analyses with no renders at all

Both published pre-registrations are reproduced from the CSVs alone:

```
# §5.1 — chromatic signatures
python experiments/analyze_palette_coherence.py \
    --features data/palette_features_stage7_all.csv \
    --out-matrix data/palette_condition_cosines_stage7.csv
```

The hatching test of §5.2 is a paired sign-flip permutation on `crosshatch_entropy_mean` in
[`data/style_features_stage7.csv`](../data/style_features_stage7.csv), filtered to the 16 prompts in
`confirmation_prompts.csv`, with seeds averaged per prompt before testing.

## Integrity — every published input, by hash


**Presets (the 53 KB payload, one file per condition)**

| file | sha1 | bytes |
| --- | --- | --- |
| `presets/Arthemy_Bench_BLOCKSHUFFLE.json` | `f407687fcece` | 60,331 |
| `presets/Arthemy_Bench_BLOCKSHUFFLE_NEG.json` | `783060b1de25` | 60,121 |
| `presets/Arthemy_Bench_Base.json` | `26b554cc2be9` | 50,026 |
| `presets/Arthemy_Bench_HALF.json` | `74f1cdade8b6` | 50,897 |
| `presets/Arthemy_Bench_NEG.json` | `4e084461329c` | 49,800 |
| `presets/Arthemy_Bench_RANDSIGN.json` | `ab51459af0d8` | 49,912 |
| `presets/Arthemy_Bench_RANDSIGN_NEG.json` | `2bdbced1e9eb` | 49,973 |

**Stage 7 data**

| file | sha1 | bytes |
| --- | --- | --- |
| `data/confirmation_prompts.csv` | `bf848cc9e1d2` | 413 |
| `data/palette_condition_cosines.csv` | `822369907fb3` | 418 |
| `data/palette_condition_cosines_stage7.csv` | `4fc37f638fb6` | 406 |
| `data/palette_features_all.csv` | `a03aea787148` | 358,783 |
| `data/palette_features_stage7.csv` | `f84f8f6f19d2` | 230,147 |
| `data/palette_features_stage7_all.csv` | `e4fd89990240` | 267,857 |
| `data/palette_features_stage7a_candidates.csv` | `c6773bc19c95` | 58,464 |
| `data/stage6b_pilot_images.csv` | `96924a0b8873` | 239,996 |
| `data/stage7a_images.csv` | `21f8213faed0` | 88,272 |
| `data/stage7b_images.csv` | `cc8beb32ec4e` | 372,432 |
| `data/style_features_stage7.csv` | `1980edcbedb1` | 308,268 |

**Analysis scripts**

| file | sha1 | bytes |
| --- | --- | --- |
| `experiments/analyze_palette.py` | `8e67ebfc6f49` | 22,877 |
| `experiments/analyze_palette_coherence.py` | `1888908f95cf` | 9,783 |
| `experiments/analyze_palette_sa.py` | `7487b245d156` | 4,425 |
| `experiments/build_palette_sheet.py` | `83124240c482` | 6,405 |
| `experiments/palette_from_manifest.py` | `b6e0b43fd721` | 5,013 |
| `experiments/palette_stage4_baseline.py` | `e8163dd35fec` | 4,459 |
| `experiments/run_stage7a.py` | `838429e0e52b` | 6,554 |
| `experiments/run_stage7b.py` | `cff1f69d6cb6` | 9,174 |
| `experiments/select_confirmation_prompts.py` | `dbdd756fad47` | 4,056 |
| `experiments/stage7_prompts.py` | `72105db08d83` | 12,803 |
| `experiments/style_from_manifest.py` | `e1b18fa23783` | 4,742 |

**Release archives** (attached to release [`stage7-confirmation`](https://github.com/aledelpho/diffusion-models-weight-steering-report/releases/tag/stage7-confirmation))

| file | sha256 | size |
| --- | --- | --- |
| `stage7_renders_png.tar.gz` | `3721639e16c44e19cbf6fa5199c7f1efb6720d36fa4335255e9d9d4edfce8c38` | 1.07 GB (1,150,016,109 bytes) |
| `krea2_steering_png_originals.zip` | `7b7dc3d8002178682825ac83e5c69748cc25f245fa12386e47a1d97ca76b545d` | 498 MB (521,828,283 bytes) |
| `krea2_attribute_emergence_png_originals.zip` | `406e89e677a53c96339a229d9b055476d16290c26b3d8441ca3bda50b076008a` | 642 MB (672,733,698 bytes) |

The measurement scripts named in the pre-registrations were frozen by hash before stage 7 ran; the
hashes and the one deviation that occurred are recorded in
[`prereg_chromatic_signatures.md`](prereg_chromatic_signatures.md).

## What is not in this repository

The base checkpoint, which is Krea-2 Turbo and is not ours to redistribute. Everything else needed to go
from that checkpoint to the numbers in §5 is here.
