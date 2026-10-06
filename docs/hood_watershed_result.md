# C54 result — almost any edit completes the archer's half-formed hood

2026-10-06. Exploratory; criteria in `docs/prereg_hood_watershed.md` (+ amendment 1, the label
*abbassato*), committed before any label. Labels: Alessandro (`data/hood_labels_alessandro.csv`,
deposited before the tally), blind to the condition; tally `data/hood_tally_alessandro.csv`.
Agreement check: Claude (`data/hood_labels_claude.csv`).

## Reliability

* Self-agreement of Alessandro on the 12 repeated images: **12 of 12** — the labels are usable.
* Agreement with Claude's independent labels: 71 of 78 exact; **74 of 78** on *complete on the
  head* against anything else. The disagreements are mostly *a metà* against *abbassato* — the
  boundary between a hood that stops halfway and one lying behind the head is the fuzzy one.

## Result

**Seed 3141592** (baseline: *a metà*), 69 edits:

| outcome | n | which |
|---|---|---|
| completes the hood | **58** | every block from 00 to 27, both signs, among them blk27 −0.075 (the smallest dose in the set) and the words "colorful" |
| leaves it half-formed | 6 | blk02 −0.45, blk05 −0.55, blk21 +0.25, blk22 +0.25, blk27 +0.05, the words "muted" |
| lowers it (whole, behind the head) | 4 | blk13 −0.45, blk15 −0.45, blk17 +0.40, blk23 +0.15 |
| unclear | 1 | blk27 −0.25 |

**Seed 4669201** (baseline: *completo*): none of the 7 edits there (blk23 at five doses, the two
wordings) breaks the hood.

**The expectation written in advance** — middle blocks change the hood more often than end blocks —
is **not supported**: the end blocks (00–01, 21–27) complete it in 17 of 22 edits, the middle
(05–14) in 21 of 23.

## Reading

The half-formed hood is not something block 23 repairs: it is an unstable state of this seed, and
almost any change to the weights — at any depth, either sign, a dose as small as 0.075, or two words
added to the prompt — tips it, mostly toward the hood the prompt asks for. The sampler is
`euler_ancestral`, which injects noise at every step; a small change early in the trajectory is
enough to land in another basin. In Alessandro's terms, a *watershed* is a point where the
baseline is balanced on the ridge, and the edit does not need to push in any particular direction
to make it fall.

Two consequences for the rest of the report:

1. **C53.** The repair that drew observer A to the blk23 image is a property of regenerating the
   image at all, not of block 23. It is the general confound of any in-model edit against a slider
   on the finished image: the edit gets a second draw on every unstable detail, for better or worse.
2. **Any "this edit fixed that detail" from one seed** needs this control: other edits of the same
   seed. Here 58 of 69 do the same. A claim that a block *specifically* repairs something would need
   many seeds and a comparison with edits that should be unrelated.

Not tested: whether the completed hoods are better in other ways, or whether a different
half-formed detail on another seed behaves the same. One prompt, one unstable seed.
