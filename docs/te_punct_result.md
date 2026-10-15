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

## Not yet done

* The natural prompts (dwarf and elf brawler in five versions) are not labelled; the gold gorget and gold gauntlet
  seen by eye stay descriptive.
* The encoder-side measure (same-part vs cross-part similarity by version) is not computed.

## Limits

Two prompts, eight seeds, one labeller who wrote the prompts and saw the pilot. The primary questions sit near the
ceiling for most versions, so small effects of punctuation cannot be excluded. Six versions were tested with no
correction; BREAK's 16 of 16 would survive any.
