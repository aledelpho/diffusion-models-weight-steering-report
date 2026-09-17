# Pre-registration — Chromatic signatures of weight-space interventions

**Written before the confirmation renders exist.** Committed on 2026-09-17.
Nothing below may be revised once the first confirmation render is produced; if
something has to change, the change is appended with a date and a reason, and the
original stays visible.

## What is claimed

Every weight-space intervention we apply — the preset, the block-shuffle control,
the random-sign control, and each of their negatives — pushes the colour palette
of the output in a direction of its **own**, and that direction survives changing
the subject of the image.

The random-sign condition is **not a null here.** It has the same Frobenius
displacement as the preset and no internal structure, which makes it the right
control for "my direction is special" — but that is a different question. For
this claim it is a seventh treatment, and a chromatic signature of its own is a
confirmation, not a failure.

## What was already observed (exploratory, and the reason this document exists)

On 14 prompts drawn from stage 5 and stage 6, measured after the fact on a corpus
that had already been measured thirteen times for other purposes:

| condition | cross-prompt cosine | Holm |
|---|---|---|
| randsign − | +0.263 | 7.3e-4 |
| randsign + | +0.187 | 1.8e-3 |
| preset + | +0.149 | 2.4e-3 |
| blockshuffle − | +0.084 | 9.5e-3 |
| preset − | +0.025 | 0.35 |
| blockshuffle + | +0.018 | 0.35 |

Within-condition coherence 0.121 against 0.041 between conditions; the gap of
0.080 sits at roughly nine times the 95th percentile of a label-permutation null
(p = 1e-4). Four conditions of six, and a clear separation between them.

None of this counts as evidence for the claim. The statistics were chosen after
seeing the data, on a corpus selected for other reasons. That is what the
confirmation is for.

## Measurement, frozen

Six swatches per render — the darkest, the lightest, and the four most distant in
saturation and hue — plus the paper and the ink estimated as the extreme-lightness
clusters carrying at least 3% of the image. Each of those eight slots enters as
(L\*, a\*, b\*), giving a 24-dimensional vector. Hue is reconstructed into a\* and
b\* rather than used in degrees, because a circular quantity cannot be averaged or
subtracted.

Every vector is the **difference from the same prompt and the same seed under
baseline**. Absolute palettes are dominated by which character is depicted
(pitfall 19). Seeds within a prompt are averaged before anything else, and the
unit of analysis is the prompt (pitfall 17).

Scripts, by SHA-1 of their contents at the time of writing:

```
analyze_palette.py            8e67ebfc6f49
analyze_palette_coherence.py  1d07551eadcd
palette_stage4_baseline.py    e8163dd35fec
```

The analysis is run by executing these files unchanged. A change to any of them
before the confirmation is analysed voids the pre-registration.

## The two tests, and what decides them

**Primary 1 — each condition has a coherent direction.** For each condition, the
mean pairwise cosine between its per-prompt direction vectors, over pairs of
distinct prompts. Null: exact sign-flip permutation across prompts. Holm across
the six conditions.

> Confirmed if **at least four of six** survive Holm at 0.05.
> Refuted if two or fewer do.
> Three is an ambiguous outcome and will be reported as such, not rounded up.

**Primary 2 — the directions differ from one another.** Mean within-condition
coherence minus the mean absolute cosine between different conditions, both
computed over pairs of distinct prompts. Null: permutation of the condition
labels within each prompt, 10 000 draws.

> Confirmed if p < 0.05.

**Secondary, directional.** The same four conditions — randsign ±, preset +,
blockshuffle − — are the ones that survive. This is a prediction about which,
not merely how many, and it is recorded so that a shuffle of identities between
runs is visible rather than absorbed.

## Corpus

Sixteen prompts that have not been used in stage 4, 5 or 6, times seven cells —
baseline plus the six conditions — times the five standard seeds
(42, 777, 1337, 9999, 4242145). 560 renders.

The sixteen are chosen to **span the colour circle deliberately**, because the
existing 14 cluster in warm hues: nine of them have a mean swatch hue between 5°
and 95°. At least four of the new prompts must land in the 150°–300° arc, and at
least two must describe a near-monochrome subject. Prompt texts are fixed and
hashed before rendering; `prompt_sha1` is what identifies them afterwards.

**Prompts are never edited** — not to shorten them, not to improve them, not to
harmonise a comma. `prompt_sha1` exists so that an edit cannot pass unnoticed.

## Stage 4

Stage 4's four prompts carry seven conditions and no baseline rows, so they
produce no difference vectors. The baseline renders exist — `stage4_images.csv`
lists twenty distinct `baseline_path` entries — and are recovered by reading them,
not by re-rendering. That brings the exploratory set to 18 prompts.

Recovering stage 4 **changes the exploratory numbers above**, and the table will
be restated when it does. It does not touch the confirmation, which runs on the
sixteen new prompts alone.

## What would end the claim

Two or fewer conditions coherent, or primary 2 not significant. In that case the
chromatic signature is written up as not established, the reference sheet is kept
as a description of one corpus, and nothing in the README claims a colour result.

---

## Amendment 1 — 2026-09-17, before any confirmation render exists

**Reason.** The corpus section above required that at least four of the sixteen
prompts land in the 150°–300° hue arc and at least two be near-monochrome. Hue is
a property of the rendered image, not of the prompt text, so as written the
criterion could only be applied by looking at renders and then choosing — an
unspecified selection step. The requirement is kept; the way it is satisfied is
made explicit here, before anything is rendered.

**Corpus construction becomes two stages.**

*Stage A — candidates, baseline only.* Twenty-four new prompts, none used in
stage 4, 5 or 6, rendered at **baseline only**, five seeds each. 120 renders.
Alessandro writes the twenty-four; the brief is that roughly a third should
describe subjects he would expect to come out cool (sea, night, ice, verdigris,
moonlight) and roughly a sixth near-monochrome (charcoal study, ink wash,
bone-white), so that the arcs below can actually be filled. He is not asked to
predict the measurement, only to give it something to select from.

*Selection.* Each candidate's mean swatch hue is computed by `analyze_palette.py`
on its five baseline renders, averaged circularly. The hue circle is cut into
four arcs — 0–90°, 90–180°, 180–270°, 270–360° — and the **four prompts with the
lowest `prompt_sha1` in lexicographic order** are taken from each arc. If an arc
holds fewer than four candidates, the shortfall is filled from the arc with the
most candidates, again by lowest `prompt_sha1`, and the shortfall is reported.

The tie-break is `prompt_sha1` and not chroma, coherence, or anything a person
would prefer, precisely so that no judgement enters. The selection reads
**baseline renders only** and never touches a condition, so it cannot select for
the effect, which is defined as a difference from baseline.

*Stage B — conditions.* The six conditions on the sixteen selected prompts, five
seeds each. 480 renders. Their baselines already exist from stage A.

**Total: 600 renders, not 560.** The extra 40 buy the coverage requirement the
original text asked for and could not deliver.

**Power, and where the number 16 comes from.** Subsampling the 18 exploratory
prompts and re-running the whole analysis 100 times per size:

| prompts | ≥4 of 6 survive Holm | the same 4 | primary 2 |
|---|---|---|---|
| 8 | 8% | 4% | 100% |
| 12 | 39% | 30% | 100% |
| 14 | 78% | 73% | 100% |
| 16 | 100% | 94% | 100% |

This curve resamples the prompts it is estimating from and assumes the true
effect equals the observed one, so it is optimistic. Sixteen is a floor, not a
margin. Primary 2 is saturated at every size tried; primary 1 is what the corpus
is being bought for.

**No interim look.** The analysis runs once, on all sixteen, after stage B is
complete. Neither test is computed on a partial corpus, and the thresholds are
not revisited afterwards.

---

## Result — 2026-09-17, stage 7, analysis run once

### Protocol deviation, recorded first

`analyze_palette_coherence.py` was **not** at the frozen hash when stage 7 closed.
It read `1888908f95cf` against the registered `1d07551eadcd`. The cause was mine:
after writing this document I fixed a reporting bug in that script — it printed
the floor of the exact permutation test while running Monte Carlo above 16
prompts — and in doing so broke the freeze I had just declared.

The frozen version was reconstructed by inverting that patch; it hashes to
`1d07551eadcd` exactly, and **the analysis below is that script's output**. The
current version was then run on the same file and produced identical numbers to
every printed digit, because at n = 16 both take the exact enumeration path and
the edit only touched the Monte Carlo branch and a print statement. The deviation
is therefore inert here. It is recorded anyway, because a freeze that is only
honoured when convenient is not a freeze.

### Corpus — the coverage requirement was not met

Amendment 1 required four prompts in each of four 90° arcs. The selection
returned **14 in 0–90°, one in 90–180°, one in 270–360°, and none in 180–270°**.
The rule executed correctly and filled the shortfall from the largest arc, as
written; the candidate pool simply did not contain what was asked for.

The lesson is specific: the brief asked for prompts describing cool subjects, but
these are close-up character portraits, where the six swatches are dominated by
skin and paper whatever the scene describes. A cool *subject* does not produce a
cool *palette* under this framing. Prompt text is the wrong lever for controlling
measured hue.

Note the direction of that bias: a corpus of more similar prompts should make
cross-prompt coherence **easier** to detect, not harder. It does not excuse what
follows.

Verified before analysis: 560 rows, 16 prompts × 7 conditions × 5 seeds, no cell
short of five seeds, no duplicates, and **no prompt_sha1 shared with stage 4, 5
or 6**.

### Primary 1 — AMBIGUOUS

| condition | cosine | p | Holm |
|---|---|---|---|
| blockshuffle − | +0.109 | 3.7e-4 | 2.2e-3 ✓ |
| randsign − | +0.093 | 2.1e-3 | 1.1e-2 ✓ |
| preset + | +0.059 | 5.2e-3 | 2.1e-2 ✓ |
| randsign + | +0.048 | 1.7e-2 | **5.10e-2** ✗ |
| preset − | +0.017 | 1.7e-1 | 3.5e-1 ✗ |
| blockshuffle + | +0.017 | 2.0e-1 | 3.5e-1 ✗ |

**Three of six.** The registered rule reads: four or more confirmed, two or fewer
refuted, *three ambiguous and reported as ambiguous, not rounded up*. So:
ambiguous.

`rand_pos` lands at Holm = 5.10e-2. It is not counted. This is the entire reason
the threshold was written down in advance.

### Primary 2 — CONFIRMED

Within-condition coherence +0.057, between-condition +0.023, difference **+0.080
→ +0.035**, against a label-permutation null with mean −0.003 and a 95th
percentile of +0.007. p = 1e-4, the Monte Carlo floor.

### Secondary, directional — FAILED

Predicted: randsign ±, preset +, blockshuffle −. Observed: blockshuffle −,
randsign −, preset +. Three of the four, with `rand_pos` dropping out. The set
does not match, and the prediction was about which, not how many.

### The finding that matters most: the effects roughly halved

| | exploratory (18 prompts) | confirmation (16 new) |
|---|---|---|
| randsign − | +0.276 | +0.093 |
| randsign + | +0.196 | +0.048 |
| preset + | +0.119 | +0.059 |
| blockshuffle − | +0.087 | +0.109 |
| mean within-condition | +0.120 | +0.057 |

The power curve in amendment 1 assumed the true effect equalled the exploratory
one and predicted ~100% at sixteen prompts. The true effect is about half that,
the study was underpowered for it, and the sentence "sixteen is a floor, not a
margin" turned out to be the operative one. The ranking also reshuffled:
`blockshuffle −` was fourth and is now first; `randsign −` fell from first to
second at a third of its size.

### What stands, and what does not

**Not established:** that each individual condition imprints a chromatic
direction that survives a change of subject. Three of six is not four, on a
corpus that was biased in favour of detecting it.

**Established, twice, on independent corpora, at the permutation floor both
times:** that the conditions move the palette in directions that **differ from
one another**. That is the claim the notebook may carry.

The distinction is not cosmetic. "Every displacement has its own chromatic
signature" is the claim that failed here. "Different displacements move colour
differently" is the claim that held.


---

## Addendum — 2026-09-17, same evening: the shrinkage is confounded

Written after the result above and after the push was prepared, because it was noticed late and leaving it
unwritten would have been worse than admitting when it was found.

**The verdict does not change.** Three of six against a registered bar of four is ambiguous, and it stays
ambiguous. What changes is the *explanation* offered above for why the effects halved.

The explanation given was regression from an inflated exploratory estimate. That is one candidate. Here is the
other, and it was hiding in this repository's own §1.4 the whole time:

| | colour-pinned prompts | mean within-condition coherence |
|---|---|---|
| exploratory, 18 prompts | **18 of 18** | +0.120 |
| confirmation, 16 prompts | **0 of 16** | +0.057 |

Every prompt in the exploratory set carries `monochromatic <colour>` or `<colour> overall hue` or a
colour-tinted rim light. **Not one prompt in the confirmation set does.** §1.4 had already established, on a
completely different colour instrument, that the palette effect is present where the prompt pins the palette
and vanishes where it does not — and the confirmation was then run entirely on the side where §1.4 predicts
little to find.

So the confirmation is **consistent with two readings that this design cannot separate**: the exploratory
estimate was inflated, or colour signatures depend on the prompt naming a colour, exactly as §1.4 said. The
corpus changed on that variable at the same time as it changed from exploratory to confirmatory, and the two
cannot be untangled after the fact.

This is a design error and it is ours. The pre-registration fixed the statistics, the thresholds and the
scripts, and did not fix the one prompt property already known to govern the effect being measured. A
stratification requirement was written — the hue-coverage rule — but it was aimed at the *measured* hue of the
render and not at the *stated* colour in the prompt, which is the variable that §1.4 had implicated.

**The test that separates them**, and it is cheap: matched pairs. The same subject written twice, once with the
colour-pinning clause and once without, rendered in the same run under the same six conditions and the same
five seeds, and the coherence compared between the two arms. If the pinned arm returns to ~0.12 while the free
arm stays near ~0.06, prompt-stated colour is the governing variable and the confirmation was run on the wrong
side of it. If both arms sit near ~0.06, the exploratory estimate was simply inflated and the ambiguous verdict
stands on its own feet.

Until that runs, §1.5 must not be read as "colour signatures are weak". It should be read as: **tested on
prompts that do not name a colour, three conditions of six carry a coherent chromatic direction, and whether
naming a colour changes that is an open and now-registered question.**
