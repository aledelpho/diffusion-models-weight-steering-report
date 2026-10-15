# Pre-registration C78 — does punctuation keep the concepts of a prompt apart?

Written 2026-10-15, **before any C78 render.** Renders authorised by Alessandro on 2026-10-15 (prompts designed with
him). Code: `experiments/te_punct.py` (plan, queue, gate). Plan: `data/te_punct_plan.csv`, 69 rows.

## Why

Readers of the post asked whether commas, periods or semicolons change how the text encoder splits a prompt. C68
found that text-encoder edits push groups of 2–4 tokens whose boundaries follow the commas, from layer 11 on. C45
found that rewriting a prompt (tags, prose, synonyms) changes an edit's effect no more than a change of seed. Neither
compared separators, and neither used prompts built to make concepts leak into each other.

## Material

**Built prompts** (four parts joined by the separator; words identical; lowercase after a period):

* **P1 three styles:** "a samurai drawn as a flat 2D cartoon ⟨sep⟩ a robot rendered as low-poly 3D ⟨sep⟩ both
  sitting at a wooden table ⟨sep⟩ inside a photorealistic old pub"
* **P2 held clothes:** "a man wearing a plain white t-shirt ⟨sep⟩ holding a red leather jacket in his left hand
  ⟨sep⟩ holding a blue wool cap in his right hand ⟨sep⟩ grey background"

Separators: comma ", ", period ". ", semicolon "; ". Eight seeds: 2645751, 3316624, 3605551, 4123105, 1618033,
3141592, 2718281, 1234567. 2 × 3 × 8 = 48 renders.

**Natural prompts** (every ", " replaced; existing periods kept): the D1 dwarf (C52 prompt) at its four C52 seeds,
period and semicolon (the comma pictures exist); the elf brawler (C64 prompt) at 1618033, 3141592, 2718281, 1234567,
all three versions. 19 renders.

**Gate:** D1 comma at 2645751 and the elf comma at 1618033, re-rendered, must equal the existing pictures pixel for
pixel.

## Pilot rule (fixed now)

The 16 comma pictures of P1 and P2 are rendered first. Claude looks at them (not blind; this decides only whether to
continue, the pictures are labelled blind later with the rest). For each prompt, count the pictures with at least one
failure as defined below. **The prompt goes on to the period and semicolon renders if it fails in 2 to 6 of 8.** With
0–1 or 7–8 failures there is no room to see an effect: that prompt stops, and any replacement is a dated amendment
approved by Alessandro.

## Questions (yes / no / cannot tell; fixed now)

**P1:** (a) Il samurai è disegnato come un cartone animato piatto? (b) Il robot è un 3D low-poly? (c) Il pub è
fotorealistico? (d) Ci sono un samurai e un robot, entrambi?
**P2:** (a) La maglietta che indossa è bianca? (b) La giacca è rossa? (c) La giacca è tenuta in mano, non indossata?
(d) Il cappello è blu? (e) Il cappello è tenuto in mano, non in testa? (f) Ci sono sia la giacca sia il cappello?

**Failure:** a picture fails if any answer is "no". "Cannot tell" counts as neither, and a picture with only "yes" and
"cannot tell" does not fail.

**Labelling:** Alessandro, on a page like C75's: one question at a time over all pictures of one prompt, shuffled with
a fixed seed, no version or seed shown. The separator is not visible in the picture. 4 repeats per prompt for a
test–retest gate: Cohen κ ≥ 0.60, otherwise no test may be stated as holding.

## Tests

Unit: picture. F(v) = share of failing pictures among the 16 of P1 and P2 together (or among the 8 of one prompt, if
only one passes the pilot). Pairs are matched by prompt and seed.

| test | comparison | rule |
|---|---|---|
| H1 | period against comma | F(period) ≤ F(comma) − 0.25 and better pairs ≥ worse pairs + 2 → **periods separate better**; \|F difference\| ≤ 0.125 → **no difference**; the mirror image → **periods separate worse**; otherwise inconclusive |
| H2 | semicolon against comma | same rule |

**Prediction:** no difference for both (C45, C68: rewriting changes the picture like a seed does, without a
systematic gain).

## Reported, deciding nothing

* Each question's counts by version: which concept leaks, and where.
* Encoder side (encodes only, no images, script written after this document): for each tap, the mean cosine
  similarity of tokens of the same part minus that of tokens of different parts, by version. Expected: larger with
  periods than commas from layer 11 on. Reported, not a test.
* Natural prompts: the D1 dwarf answered with the C75 trait questions (version hidden); the elf brawler described.
* A side-by-side card for the post: same seed, three versions.

## Limits

Two built prompts, eight seeds, one labeller. A change of separator also changes the composition, as any rewording
does (C45), so a difference in failures can come from a different layout rather than a cleaner split. The pairs by
seed do not remove this; the encoder measure is there to say whether the split itself changed.
