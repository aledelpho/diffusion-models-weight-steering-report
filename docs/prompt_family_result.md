# C49 result — late-block presets are coherent inside a prompt family; middle blocks are coherent to the eye but not in the style statistics

2026-10-05. Pre-registration: `prereg_prompt_family.md` (+ amendment 1, before any render).
Code: `experiments/analyze_prompt_family.py`, unchanged since 7a9a489. Data:
`data/prompt_family_style_features.csv`, `data/prompt_family_arms.csv`,
`data/prompt_family_test.csv`, `data/prompt_family_within_by_family.csv` (per-family W, added
after the test, descriptive). Eye pass `data/prompt_family_eye_alessandro.csv`, deposited
(a748ed8) before the scoring ran. Renders 433/433, REPRO pixel-identical.

## 1. Pre-registered verdicts — all four supported

| | rule | result | verdict |
|---|---|---|---|
| H1 family matters | W > B on ≥ 5/6 arms, median W − B ≥ 0.10 | 6/6, **+0.19** | supported |
| H2 coherence usable | median W ≥ 0.40 | **0.53** | supported |
| H3 middle control (blk09 +) below | W < tested median | **0.16** vs 0.53 | supported |
| H4 Style band less coherent | median W < late median − 0.10 | **0.16** vs 0.53 | supported |

Reference: the seed floor S (same prompt, two seeds) has median 0.76 on the tested arms, so
inside a family a late-block preset keeps about 70 % of the coherence it has across seeds.
Combo preset: W 0.53, B 0.26, S 0.75.

## 2. The eye agrees on the late blocks — family by family

Within-family W split by family (descriptive):

| arm | cartoon | oil | photo | eye (cartoon / oil / photo) |
|---|---|---|---|---|
| blk16 +0.30 | 0.79 | 0.34 | 0.14 | yes / yes / partly |
| blk20 +0.45 | 0.80 | 0.55 | 0.29 | yes / yes / **no** |
| blk23 −0.30 | 0.56 | 0.28 | 0.13 | yes / yes / **no** |
| blk26 +0.15 | 0.65 | 0.71 | 0.53 | yes / yes / yes |
| blk27 −0.25 | 0.56 | 0.59 | 0.42 | yes / yes / yes |
| combo | 0.76 | 0.36 | 0.48 | yes / yes / yes |

Where Alessandro saw no common look (blk20 and blk23 on photographs) the numbers are
among the lowest. **Coherence is strongest on cartoon and weakest on photographs**, in line
with the earlier observation that photographic style is the hardest to steer.

## 3. The eye disagrees on the middle blocks

Numbers: the Style arms and the blk09 control have W 0.06–0.17 — barely above B. Eye: 8 of
12 Style-arm cells and 2 of 3 blk09 cells marked **yes, a common recognisable look**. His notes
say what the look is: blk09 + "raises realism coherently in all" (cartoon blacksmith becomes a
3-D render), and turns the female blacksmith into a man in all three families; on photographs it
"idealises instead of making more realistic"; blk17 + reads as "focus on the subject" on photos.

These are changes of **what is depicted** (realism, identity, stereotype), and the 23 style
features measure **how it is rendered** (texture, edges, colour). Per pitfall 90 the statistic
is the suspect: H3 and H4 are supported *as statements about rendering statistics*; they do
not show that middle blocks lack a family-coherent effect. They show that their effect is not
a rendering effect. The blacksmith-to-man change is itself a finding: blk09 + moves the image
toward the more common reading of the words ("blacksmith" → man), consistent with
Alessandro's earlier note that some blocks weight "what" over "how".

## 4. The cost

Eye: blk26 +0.15 and blk27 −0.25 "not acceptable" in all families ("a uniform patina of noise
— lower the value"); combo "partly" in two families (too many artefacts); blk03 +, blk13 −
start showing grain on dark areas. Numbers agree on blk26: edge density up on 36/36 images.
blk27 −0.25 raises none of the four texture statistics (it blurs; the "noise" seen may be a
blur-plus-grain mixture the statistics split). The doses calibrated on single images are too
high for a preset meant to be used across a family.

## 5. What this lets Alessandro say

- **Supported:** a preset built from late blocks gives a family of prompts (same style,
  different subjects) a common direction of change — strongly on cartoon, moderately on oil,
  weakly on photographs — at about 70 % of the coherence it has across seeds.
- **Supported by eye only:** middle blocks also give a recognisable common change inside a
  family, but it is a change of content (realism, identity), measured here by nothing.
- **Not yet:** "the price is a little noise, you can clean it up later". At these doses the
  noise is not little for blk26/blk27, and no clean-up has been tested (phase 2).
