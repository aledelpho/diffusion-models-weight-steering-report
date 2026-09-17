# Pre-registration — attribute emergence, stage 7

**Written on 2026-09-17, before the twenty-four candidate prompts have been
analysed and before any stage 7 render exists.** Second, independent
pre-registration on the same corpus as
`prereg_chromatic_signatures.md`. Different measurement, different statistics,
declared separately; neither contaminates the other, because both are fixed
before the renders.

## The prediction being registered

Alessandro, in his own words and before the data:

> I am certain we will have cases like the appearance of the barnacles in some of
> the presets, showing that weight displacements lead to new *trends* emerging in
> how the same prompt is read.

## Why the prediction cannot be tested as stated

Stage 7 will produce 480 images. The space of "attributes that might emerge" is
unbounded, so whatever happens, an attribute can be found afterwards that appears
more often under one condition than another. A prediction that cannot fail is not
evidence when it succeeds.

The barnacles were found by looking at renders and **then** re-tested on a fresh
scoring round — that is legitimate discovery followed by confirmation. A second
find-by-looking is a second discovery, not a confirmation of the first.

The fix is to name the attributes before the renders exist. That is what the
table below is for.

## The attribute table — filled before rendering, void afterwards

For each of the twenty-four candidate prompts, **two phrases** whose visual
realisation is genuinely uncertain: things the model may render or may drop.
Written by Alessandro, once, before stage A completes.

| prompt id | prompt_sha1 | attribute 1 (verbatim phrase) | attribute 2 (verbatim phrase) |
|---|---|---|---|
| I01 | | | |
| … | | | |
| I24 | | | |

Rules that make the table worth having:

- The phrases are **quoted verbatim from the prompt**. An attribute described in
  other words is an attribute that can drift during scoring.
- Both phrases are chosen for **uncertainty**, not for interest. A phrase the
  model always renders (`upper body portrait`) and one it never renders carry no
  information. The useful ones are the marginal ones.
- Nothing about the conditions is consulted when choosing. Only the prompt text.
- Once the first stage A render exists, the table is closed. If it is filled or
  edited afterwards, this document is void and must say so.

Only the sixteen prompts selected by `select_confirmation_prompts.py` carry into
the analysis: **32 units of `(prompt × attribute)`**.

## Scoring, and the one real upgrade over the barnacle round

Each render is scored **present / absent / ambiguous** for each of its two
attributes.

**Scoring is blind to condition.** In the barnacle round the scorer knew which
condition each image came from; here the renders are copied to a working folder
under hashed names, the key is written to a file that is not opened until every
score is recorded, and the scores are joined to the conditions afterwards. This
is the single largest improvement available, and it costs one script.

`ambiguous` is neither present nor absent: it leaves both the numerator and the
denominator, and the count of ambiguous calls is reported per condition. A
condition that produces many ambiguous calls is itself a finding and must not be
hidden inside a rate.

## The test

Five seeds per cell means an exact McNemar on a single cell has a floor of
2/2^5 = 0.0625 and can never reach significance, whatever the effect. The unit of
analysis is therefore the `(prompt, attribute)` pair, not the cell.

For each unit and each condition: the rate `k/5` of seeds showing the attribute,
minus the same rate under baseline. Across the 32 units, the mean difference is
tested by exact sign-flip permutation, with Holm across the six conditions.

> **Primary.** At least one condition shows a mean rate difference from baseline
> that survives Holm at 0.05.
>
> **Refuted** if none does. In that case the claim on record is that weight
> displacement at this magnitude does not measurably change which named prompt
> attributes get rendered, and the barnacle case stands as a single result on a
> single prompt, not a general phenomenon.

**Direction is not predicted.** Barnacles appeared under blockshuffle and
vanished elsewhere; a condition that *suppresses* attributes is the same
phenomenon with the opposite sign, and the two-sided test treats it as such.

**Secondary, descriptive, not tested.** The per-unit rates are published in full
so a reader can see which prompts and which attributes moved, without those
being claimed.

## What this design cannot answer

Whether a *specific* attribute in a *specific* prompt emerges under a specific
condition. That needs roughly twenty seeds in the cell, as the barnacle round
had, and sixteen prompts at five seeds cannot be re-cut to provide it. If the
primary test fires, the natural follow-up is exactly that: the units that moved
most, re-rendered at twenty seeds, pre-registered separately — and chosen by a
rule written down before their rates are read.
