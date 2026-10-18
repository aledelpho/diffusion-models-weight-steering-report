# C92 result — do characters deviate from an edit's usual destination consistently?

2026-10-18. Pre-registration `docs/prereg_te_character_consistency.md` and script
`experiments/te_character_consistency.py`, committed together (01ea59b) before the run; the predictor was replaced
before any real data was read, after the selftest (positive and negative case) showed the first one did not use a
character's own bias. Outputs `data/te_character_consistency_tests.csv`, `_cases.csv`. No renders: C73 genre labels,
7 characters × 11 MLP-doubled edits × 2 seeds (152 labelled cases).

## Verdict

| predictor (leave one character × edit out) | accuracy |
|---|---|
| MAJ, most frequent genre | 0.454 |
| EDIT, the edit's usual genre on the other characters | 0.487 |
| **CHAR+EDIT**, the character's own genres on the other edits + the edit's on the other characters | **0.572** |

**Rule: inconclusive.** CHAR − EDIT = **+0.086** (bar +0.10), permutation p = **0.014** (bar 0.05): the improvement is
unlikely to be chance, but smaller than the size fixed in advance.

## Where it comes from

The gain is carried by three characters with a clear bias of their own: the elf rogue (anime or comic in 20 of 22
labels; EDIT 0.27 → 0.55), the tiefling (comic in 17 of 22; 0.50 → 0.73) and the dwarf (comic or cartoon in 18 of 22;
0.55 → 0.73). The gnome, the halfling and the half-orc spread over painting, realistic and comic and gain nothing; the
dragonborn loses (0.68 → 0.59).

## Reading

A first, partial signal for Alessandro's hypothesis: some prompts have a consistent way of reacting to text-encoder
edits, which shows across edits and can be learned from a few of them. It is not general (three of seven characters)
and not large enough for the rule. With C88 (the push itself carries nothing beyond the edit), the picture is: *where* an
edit goes depends on the edit, plus a prompt-specific bias that some prompts have and others do not.

## Limits

One labeller, coarse genres, 7 characters, MLP-doubled edits only; the result sits between the two thresholds.
