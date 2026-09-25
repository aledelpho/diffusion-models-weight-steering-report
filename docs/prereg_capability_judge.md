# Pre-registration — Does an edit cost capability, and does the cost differ by scene?

- **Written:** 2026-09-25, before any judge has been run and before any image has been shown to
  any model. **No new render.**
- **Relates to:** `docs/prereg_style_axis_tradeoff.md` (which returned *no signal* and whose §5
  named the reason: it measures style geometry, never capability).

---

## 0. Why a second attempt, and why it is not a second bite at the same apple

The style-axis study asked whether an edit moves a scene along the direction that defines its
style. It found nothing: M = −0.0280 against an exact null of [−0.087, +0.092], and T = 2.833
against a null mean of 3.057 — if anything *less* split than chance.

That result is about a **geometry of 23 texture features**. The observer's hypothesis is about
**capability**: that moving weights makes the model better at one thing and worse at another.
No feature in this project measures whether a render still *reads as* pixel art, or still
*contains* what the prompt asked for. That is a semantic judgement and it needs a judge.

This study is therefore a different measurement, not a re-analysis. It is still a second look at
the same renders, and that is stated here so it is on the record.

## 1. The judge — fixed before use

Two full multimodal models are already on disk, in ComfyUI format:

- `TextEncoders/qwen3vl_4b_bf16.safetensors` — 713 tensors, **315 of them `model.visual.*`**
- `TextEncoders/gemma4_e4b_it_fp8_scaled.safetensors` — 2 417 tensors, with `vision_model` (658),
  `audio_model` (751), `multi_modal_projector` and a bundled tokenizer

**The judge is Gemma, not Qwen3-VL, and the reason is independence:** `qwen3vl_4b` is the text
encoder this project's tuner patches, 629 tensors of it, in every single condition. A model from
the generating pipeline must not grade the pipeline's output. If Gemma cannot be run, the study
waits; it does not fall back to Qwen.

Fixed: temperature 0, one image per call, **file names never passed to the model**, questions
asked verbatim and in a fixed order, no conversation history between images.

## 2. Corpus — one seed, 200 images

Seed 42 only: 24 live presets × 8 scenes = 192, plus the 8 baselines. `modulation_norm` stays
excluded (amendment 02: its renders are the baseline, pixel for pixel). Further seeds are added
only if the guards of §4 pass.

## 3. The three questions — verbatim, frozen

1. `Is this image in the style of {style}? Answer only yes or no.`
   where `{style}` is the scene's own declared style, taken from its prompt
   (photography, watercolour, lowpoly 3D, claymation, ukiyo-e woodblock, 8-bit pixel art,
   stained glass, charcoal sketch).
2. `Does this image show a yellow and blue rally car in a jungle? Answer only yes or no.`
3. `Rate the technical quality of this image from 1 to 5. Answer with one digit.`

Q1 is style conformity, Q2 is subject retention, Q3 is quality. Q1 and Q2 are the capability
measures; Q3 is descriptive and is never used as the primary.

## 4. The guards, which run FIRST and can end the study

- **Test–retest.** 30 images, chosen by `random.Random(1337)` from the 200, are judged twice.
  Agreement on Q1 and Q2 is reported. **If agreement is below 80 % on either, the judge's noise
  is the finding and no capability number is computed.** The retest also yields σ_judge for Q3.
- **Positive control.** The 8 baselines against the 8 renders of `early_attn_draw2` — the preset
  the observer called "visibly broken" and which the damage gate puts out of range on 7 scenes of
  8. **If the judge does not separate those two sets on Q1 or Q2, it has no resolution and the
  study stops.**
- **Yes-bias.** The share of "yes" over all answers. If the judge answers "yes" to Q1 on more
  than 95 % of images, or less than 5 %, it is not discriminating and the study stops.

All three are reported whatever they show.

## 5. The statistics — frozen

For preset *p* and scene *s*: Δcap(p, s) = score(p, s) − score(baseline, s), on Q1 and on Q2
separately, score being 1 for yes and 0 for no.

- **Cost** = mean Δcap over all 192 cells. Negative means edits cost capability.
- **Trade-off, primary** = the number of presets whose 8 scenes contain **both** a −1 and a +1 on
  the same question. Null: the judge's own noise, estimated from the test–retest of §4 — a preset
  is counted only if its spread across scenes exceeds what re-judging the same images produces.
- **Per-scene cost** = mean Δcap by scene, descriptive: which styles the edits break and which
  they leave alone.

## 6. Decision rules — frozen

1. **Judge unusable** if any guard of §4 fails. Nothing else is computed.
2. **No cost** if Cost is within the test–retest noise on both questions. The edits do not
   measurably damage capability at this displacement, and the trade-off question is closed
   negative by two independent instruments.
3. **Uniform cost** if Cost < 0 beyond noise and the trade-off count is at noise level. Wording
   fixed now: *edits cost capability, equally across scenes.*
4. **Trade-off** if the trade-off count exceeds noise. Wording fixed now: *the same edit keeps a
   scene's capability and destroys another's.* **Only this supports the observer's hypothesis**,
   and even then it is one judge on one seed and requires a second judge before publication.

## 7. What would kill it

- One seed. A cell is one image and one answer; the test–retest is what makes that tolerable.
- Yes/no answers lose gradation; a style half-destroyed still answers "yes".
- Eight scenes, one subject. As in every study on this corpus.
- A VLM is not a calibrated instrument. Its agreement with a human has not been measured here,
  and no claim from it stands alone.

## 8. Outputs

`data/capability_judge_raw.csv` (one row per image and question, answers verbatim),
`data/capability_judge_tests.csv` (guards, Cost, trade-off count, per-scene cost, verdict).
