# C78 result — punctuation, BREAK and labels on two complex four-character prompts

2026-10-15. Pre-registration `docs/prereg_te_punct.md` (amendments 3–6 for this part). Labels: Alessandro, blind to
version and seed, committed as downloaded (`data/te_punct_alessandro.csv`, 2,640 answers, e973a23). Tally:
`experiments/te_punct_tally.py` (committed before the counts), outputs `data/te_punct_tests.csv`,
`data/te_punct_by_picture.csv`, `data/te_punct_secondary.csv`. Plain Krea-2, 8 seeds, 1024×1536.

## Reliability

Cohen κ 0.954 on 95 repeat pairs of the primary questions (0.982 on all 175): gate passed. The eight questions written
in the negative agree with themselves 32 of 32 times; the positive ones 142 of 143.

## Primary test (12 questions per prompt, fixed before the pilot)

| version | mean errors | d against original | better / worse / tied (16 pairs) | P3 d | P4 d | verdict |
|---|---|---|---|---|---|---|
| original | 1.50 | | | | | |
| comma | 1.44 | −0.06 | 5 / 4 / 7 | −0.38 | +0.25 | no difference |
| period | 1.31 | −0.19 | 4 / 1 / 11 | −0.38 | 0.00 | no difference |
| semicolon | 1.31 | −0.19 | 6 / 3 / 7 | −0.50 | +0.13 | no difference |
| no punctuation | 1.75 | +0.25 | 2 / 6 / 8 | +0.13 | +0.38 | no difference |
| BREAK | 7.00 | **+5.50** | 0 / **16** / 0 | +3.88 | +7.13 | **hurts** |
| no labels | 1.69 | +0.19 | 1 / 3 / 12 | +0.25 | +0.13 | no difference |

* **Separators do not matter here.** Commas, periods, semicolons, no punctuation at all, and the same text without
  the "Character N (…):" labels all land within a quarter of an error of the original, as predicted.
* **BREAK breaks the scene.** In every one of the 16 pairs the BREAK picture is worse, by 5.5 errors on average. Not
  all four characters are present in any BREAK picture of either prompt (secondary s01, s04: 0 of 16); the catfolk
  is never humanoid (s02, s05: 0 of 16); in the prison break the tiefling, her hammer and the catfolk's place are
  lost in 8 of 8. Encoded alone, each part is a description with no scene around it, and the staging paragraph
  names characters it can no longer see.
* **The errors left in the other versions are omissions the model makes everywhere**: the elf's blue sparks in the
  totem (0 of 8 in every version), the tiefling's golden aura in the prison break (at most 1 of 8), the catfolk
  clinging in mid-air (0 to 2 of 8). No version fixes them.

## Secondary (chosen after seeing the original pictures; they decide nothing)

Shares of "yes" among yes/no answers, 8 pictures per cell (`data/te_punct_secondary.csv`):

| question | original | comma | period | semicolon | no punct. | BREAK | no labels |
|---|---|---|---|---|---|---|---|
| p13 elf's fist silver, no green (prison) | 2/8 | 2/8 | 2/8 | 0/8 | 4/8 | 0/8 | **7/8** |
| t15 tiefling's arms not folded like the orc's (totem) | 1/8 | 2/8 | 4/8 | 1/8 | 5/8 | 6/7 | **8/8** |
| y02 orc's linen-wrapped arms deflecting halberds | 3/8 | 6/8 | 2/8 | 4/8 | 4/8 | 0/8 | 7/8 |
| s02 catfolk humanoid (totem) | 8/8 | 8/8 | 7/8 | 8/8 | 7/8 | 0/8 | **1/8** |
| x03b catfolk's tail raised (totem) | 5/8 | 4/8 | 6/8 | 6/8 | 0/8 | 0/8 | 6/8 |

* **Removing the labels removes the two leaks seen in the pilot**: the orc's green on the elf's fist (7 of 8 clean
  against 2 of 8) and the orc's folded arms on the tiefling (8 of 8 against 1 of 8). Other versions stay close to
  the original, so this is not only the regression to the mean the amendment warned about.
* **But it turns the totem's catfolk into an ordinary cat** in 7 of 8 pictures. Without "Character 3 (The Thief):"
  in front of it, "male catfolk rogue" seems to lose to the cat the rest of the sentence describes. In the prison
  break the catfolk stays humanoid without labels (8 of 8).
* These are exploratory: one labeller, 8 seeds, questions chosen after looking, six versions compared.

## Reading

On a model whose text encoder is a full language model, the separators between parts of a prompt make no
measurable difference, even on prompts complex enough to produce errors. What the parts are attached to does: the
labels "Character N (…)" change which attributes travel between characters, in both directions, and encoding the
parts separately (BREAK) destroys the scene. The community advice that comes from CLIP-based models (use BREAK to
stop concepts bleeding) does the opposite of what it promises here.

## Encoder-side measure (reported, deciding nothing)

Script: `experiments/te_punct_encoder.py` (bit-exact gate against `benchmark_te_conditioning/elf/P1_elfbrawler_baseline.npz`: `max_abs_diff = 0.0`, `GATE PASS`). Outputs: `data/te_punct_encoder_by_tap.csv` (384 rows), `data/te_punct_encoder_summary.csv` (16 rows). For each tap, mean cosine similarity of content tokens in the same part minus content tokens in different parts, both on raw tap vectors and on position-centred tap vectors (mean across tokens subtracted per tap):

| set & scope | version | raw (all 12 taps) | raw (L11–L35) | centred (all 12 taps) | centred (L11–L35) |
|---|---|---|---|---|---|
| built (`P1`, `P2`, 4 parts) | comma | 0.02969 | 0.03595 | 0.07717 | 0.09973 |
| built (`P1`, `P2`, 4 parts) | period | 0.02940 | 0.03584 | 0.07373 | 0.09564 |
| built (`P1`, `P2`, 4 parts) | semicolon | 0.03047 | 0.03679 | 0.07723 | 0.09960 |
| built (`P1`, `P2`, 4 parts) | no punctuation | 0.03061 | 0.03724 | 0.07571 | 0.09810 |
| complex (`P3`, `P4`, all 7 parts) | original | 0.03086 | 0.03688 | 0.06801 | 0.08437 |
| complex (`P3`, `P4`, all 7 parts) | comma | 0.02986 | 0.03589 | 0.06588 | 0.08198 |
| complex (`P3`, `P4`, all 7 parts) | period | 0.03043 | 0.03644 | 0.06717 | 0.08350 |
| complex (`P3`, `P4`, all 7 parts) | semicolon | 0.03054 | 0.03667 | 0.06721 | 0.08361 |
| complex (`P3`, `P4`, all 7 parts) | no punctuation | 0.03178 | 0.03807 | 0.07139 | 0.08871 |
| complex (`P3`, `P4`, all 7 parts) | no labels | 0.02811 | 0.03361 | 0.06307 | 0.07814 |
| complex (`P3`, `P4`, Characters 1–4) | original | 0.01936 | 0.02519 | 0.04246 | 0.05455 |
| complex (`P3`, `P4`, Characters 1–4) | comma | 0.01948 | 0.02538 | 0.04338 | 0.05573 |
| complex (`P3`, `P4`, Characters 1–4) | period | 0.01926 | 0.02503 | 0.04194 | 0.05391 |
| complex (`P3`, `P4`, Characters 1–4) | semicolon | 0.01939 | 0.02526 | 0.04240 | 0.05458 |
| complex (`P3`, `P4`, Characters 1–4) | no punctuation | 0.02144 | 0.02762 | 0.04874 | 0.06252 |
| complex (`P3`, `P4`, Characters 1–4) | no labels | 0.01831 | 0.02376 | 0.04180 | 0.05351 |

* **The pre-registered expectation ("larger with periods than commas from layer 11 on") does not hold.** Across `built_4parts`, `complex_all7`, and `chars_1to4`, `period`, `comma`, `semicolon`, and `original` sit within `0.0010` of each other on raw cosine (`0.03584`–`0.03688` on all parts; `0.02503`–`0.02538` on Characters 1–4) and within `0.0041` on centred cosine (`0.05391` vs `0.05573` on Characters 1–4, with `period` slightly below `comma`). Removing punctuation altogether (`nopunct`) does not reduce within-part similarity (`0.02762` raw / `0.06252` centred on Characters 1–4). The separator character does not measurably change how the tapped layers group the parts of the prompt, which agrees with the null result on the images. What does drive the grouping (position, word content) was not tested.

## Not yet done

* The natural prompts (dwarf and elf brawler in five versions) are not labelled; the gold gorget and gold gauntlet
  seen by eye stay descriptive.

## Limits

Two prompts, eight seeds, one labeller who wrote the prompts and saw the pilot. The primary questions sit near the
ceiling for most versions, so small effects of punctuation cannot be excluded. Six versions were tested with no
correction; BREAK's 16 of 16 would survive any.
