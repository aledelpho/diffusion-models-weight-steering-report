# Render spec — single blocks on eight styles (exploratory)

- **For:** Alessandro, who launches every render; queue script ready for Antigravity.
- **456 renders**, one pass. **Exploratory: no hypothesis, no claim.** What comes out is looked at
  first; anything that seems to hold is written down afterwards and checked on new seeds.
- **Origin:** the single-block atlas of 2026-09-29, Alessandro's reading of where artefacts appear
  (`data/single_blocks_eye_artifacts_alessandro.md`), and his point that a realistic style leaves the
  weights no room except content interpretation.

## What it is

The **same subject** — the fantasy close-up `F4_closeup`, word for word — under **eight** prompts.
The original's rendering instructions (*realistic western comics style, bold ink outlines, hatched
shadows*) and its locked palette (*blue overall hue, monochromatic blue*) are removed, so line,
shading and colour are left free for the blocks to move.

| id | first words |
|---|---|
| `E1_cartoon` | Cartoon style illustration. |
| `E2_watercolor` | Watercolor painting. |
| `E3_oil` | Oil painting. |
| `E4_colorpencil` | Colored pencil drawing. |
| `E5_childrensbook` | Children's book illustration. |
| `E6_claymation` | Claymation, stop-motion style. |
| `E7_sepiaphoto` | Vintage sepia photograph. — how a "realistic" rendering moves |
| `E8_cartoon_styleend` | **`E1`'s exact words, with the style sentence moved to the end** — does prompt structure change the rendering? |

Kept from the original subject on purpose: *"a gold necklace is flying around"* (the one element the
model can "interpret" — the first thing to check if a block seems to change content) and the typo
*"metty"*.

## Drive and doses

One block at a time: one slot of the 34-slot `vectors_override`, `Real Value`, exactly as the atlas.
**One seed, 2718281**, the atlas's — Alessandro expects the signatures to hold across seeds; that is
checked later, not here. Settings: `euler_ancestral` · `simple` · 9 steps · cfg 1.0 · denoise 1.0 ·
1024×1280.

**Doses are calibrated per block and per arm** from Alessandro's reading at ±0.350, capped at 0.450:

| his label at 0.350 | dose here | arms |
|---|--:|--:|
| OK | 0.450 | 23 negative, 10 positive |
| VWA | 0.400 | 1 negative, 6 positive |
| WA | 0.300 | 1 negative, 5 positive |
| SA | 0.250 | 3 negative, 5 positive |
| BROKEN | 0.150 | 2 positive (26+, 27+) |

His labels came from three prompts, two of them comics; on watercolour, oil or claymation the onset
can arrive earlier or later. These doses are a first estimate to correct by eye.

## Queue

- Plan: `data/single_blocks_styles_plan.csv` (456 rows: 8 baselines + 8 × 56), written by
  `experiments/make_single_blocks_styles_plan.py`; each row carries the dose and the label it came from.
- Queue: `python experiments/queue_single_blocks_styles.py --check-only`, then `--all`. It is
  `queue_single_blocks_atlas.py` with only the plan and the output folder changed (checked by diff).
- Monitor: `experiments/monitor_single_blocks_styles.py`.
- Output: `benchmark_single_blocks_styles/renders`. Keep `tuner_logger_capture.log`.

## After the renders

`python experiments/build_annotation_page.py single_blocks_styles` builds the page: eight prompts
stacked per block, each column labelled with the dose actually used, notes per preset and per block.
Compare `E1_cartoon` with `E8_cartoon_styleend` directly — same words, style at the other end.
