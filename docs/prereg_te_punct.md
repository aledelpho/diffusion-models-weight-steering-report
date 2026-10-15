# Pre-registration C78 — does punctuation keep the concepts of a prompt apart?

Written 2026-10-15, **before any C78 render.** Renders authorised by Alessandro on 2026-10-15 (prompts designed with
him). Code: `experiments/te_punct.py` (plan, queue, gate). Plan: `data/te_punct_plan.csv`, 69 rows (93 after amendment 1).

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

## Amendment 1 — 2026-10-15, before any C78 render: a BREAK arm

Asked by Alessandro after the literature check: the community's usual answer to concept bleeding is not punctuation
but A1111's `BREAK`, which encodes chunks of the prompt separately. In ComfyUI the equivalent is to encode each part
with its own `CLIPTextEncode` and join them with the core `ConditioningConcat` node. That is the fourth version.

* **Built prompts:** the four parts encoded separately, 8 seeds each (16 renders, in the `main` block).
* **Natural prompts:** BREAK between sentences (at ". " and at the line break), as people use it: 3 parts for the
  dwarf, 6 for the elf. Dwarf at its 4 seeds, elf at its 4 seeds (8 renders).
* **Smoke render:** the dwarf BREAK at 2645751 is rendered alone first. If the workflow errors, the BREAK arm is
  dropped and that is reported; nothing else changes.
* **H3:** BREAK against comma, same rule as H1. With an LLM text encoder each part is read with no context from the
  others, so this is the strongest separation of the four. Prediction: fewer failures than commas (the only
  directional prediction of C78), but the full rule must be met.
* **Encoder measure:** not computed for BREAK (the parts never meet inside the encoder, so the same-part /
  cross-part comparison is undefined).
* **Limit:** each part gets the encoder's own prompt wrapping, so the concatenated conditioning repeats those wrapping
  tokens. Whatever BREAK does here includes that.

Plan: 93 rows (gate 2, smoke 1, pilot 16, main 48, natural 26).

## Amendment 2 — 2026-10-15, recorded after the renders: the no-punctuation version (Alessandro's addition)

While the Step-2 renders ran, Alessandro queued a fifth version with every punctuation mark and line break removed
(`experiments/te_punct_nopunct.py`, written by Antigravity; files `EXTRA_nopunct_*`): P1, P2 and the D1 dwarf at the
eight seeds, 24 renders. It was not in this pre-registration. For the dwarf it is compared with the other versions on
the four D1 seeds only; the other four seeds are descriptive.

**Pilot outcome (Claude, by eye, not blind, as the pilot rule says):** P1 and P2 fail in 0 of 8 with commas, and in 0
of 8 without punctuation. Both prompts stop: the `main` block (48 renders) is not run. H1–H3 cannot be tested on
them. Seen by eye on the natural prompts, to be labelled blind: commas, periods and semicolons give nearly the same
picture at a seed; without punctuation the dwarf's steel gorget turns brass in 2 of 4 seeds; with BREAK the elf's
silver gauntlet turns gold and the gold pauldron disappears in 4 of 4.

## Amendment 3 — 2026-10-15, before any of these renders: two complex prompts, pilot

Two four-character prompts written by Alessandro, taken verbatim from the metadata of his pictures ComfyUI_07456
("totem") and ComfyUI_07459 ("prison break"). His pictures used a preset and a 5D tuner; here the **plain model** and
the C78 sampling are used, at 1024×1536. Script `experiments/te_punct2.py`, plan `data/te_punct2_plan.csv`: the
original text at the eight C78 seeds, 16 renders.

**Questions (yes / no / cannot tell), fixed now.** Errors = number of "no" per picture.

P3 totem: (1) l'orco è alla base della piramide? (2) la tiefling è nel mezzo, sulle spalle dell'orco? (3) l'elfa è in
cima? (4) il gatto è aggrappato all'elfa, in aria? (5) l'orco ha la pelle verde? (6) la tiefling ha la pelle rossa e
le corna? (7) l'elfa ha corna da cervo e la benda sull'occhio? (8) il guanto d'argento è dell'elfa? (9) scintille blu
escono solo dal guanto dell'elfa? (10) il gatto ha pelo fulvo e occhi gialli? (11) l'orco ha gli occhi chiusi e le
braccia incrociate? (12) nessun altro oltre alla tiefling ha pelle rossa o corna da ariete?

P4 prison: (1) l'elfa è al centro, in primo piano? (2) dal guanto dell'elfa escono fulmini blu? (3) fulmini blu
escono solo dall'elfa? (4) l'orco è in alto a sinistra? (5) l'orco ha pelle verde e zanne? (6) il gatto è in basso a
destra? (7) il gatto tiene un mazzo di chiavi? (8) la tiefling è dietro il gruppo con il martello alzato? (9) la
tiefling ha pelle rossa e corna? (10) c'è un'aura o un'onda dorata attorno alla tiefling o al martello? (11) c'è
un'esplosione arancione dietro il cancello? (12) nessun altro oltre alla tiefling ha pelle rossa o corna?

**Pilot rule.** A prompt goes on if its mean number of errors over the 8 pictures is between 1 and 6 (Claude, by eye).
Otherwise it stops. If it goes on, the versions (comma, period, semicolon, no punctuation, BREAK between characters,
and the same text without the "Character N (…):" labels and line breaks) and the paired test on the error count are a
further amendment, written before those renders.

## Amendment 4 — 2026-10-15, after the amendment-3 pilot, before any version render

**Pilot outcome (Claude, by eye, not blind).** On the 12 fixed questions both prompts average about 1 error per
picture, so both go on (rule: 1 to 6). The errors the questions catch are mostly omissions: the elf's blue sparks
missing in the totem, the tiefling's golden aura missing in the prison break, the catfolk's keys missing once or
twice. The pilot also showed leaks the questions do not cover: the elf's gauntleted fist turning green in the prison
break; the orc monk wearing metal pauldrons in all eight totems; the tiefling copying the orc's folded arms in most
totems.

**Versions** (`experiments/te_punct2.py`, plan `data/te_punct2_plan.csv`, block `versions`; words never change):
comma (sentence ends and line breaks become commas), period (every comma becomes a period), semicolon (every comma
becomes a semicolon), nopunct (as amendment 2: , . ; : and line breaks removed), break (each paragraph encoded alone
and joined with ConditioningConcat: style line, four characters, staging, environment = 7 parts), nolabels (the
"Character N (…):" labels and section headers removed, one paragraph). 6 versions × 2 prompts × 8 seeds = 96
renders, compared with the `original` pilot pictures at the same seed.

**Primary test (the 12 questions fixed in amendment 3).** For each version, d = mean over the 16 seed-pairs of
(errors of the version − errors of the original). **Helps** if d ≤ −1 and pairs with fewer errors ≥ pairs with more
errors + 3; **hurts** for the mirror image; **no difference** if |d| ≤ 0.25; otherwise inconclusive. Six versions
are tested, so a single "helps" or "hurts" is reported with that number in view (no correction applied).

**Secondary (questions chosen after seeing the original pictures).** (13) P4: il guanto dell'elfa è d'argento, mano
inclusa, senza verde? (14) P3: l'orco non ha armatura di metallo? (15) P3: la tiefling non ha le braccia incrociate?
(16) P3: il guanto dell'elfa è d'argento? Reported as counts by version. Because they were picked where the original
fails, any version will tend to look better on them by regression to the mean; they decide nothing.

**Labels:** Alessandro, blind to version, question-major page as in C75; 4 repeats per prompt; κ ≥ 0.60 gate.

## Labelling note — 2026-10-15, during labelling, before any analysis

Alessandro asked how to answer t16 ("Il guanto dell'elfa è d'argento?") when the elf wears two gauntlets. The
questions ask about colour and ownership, not number. Rule given: answer on colour only; two silver gauntlets → yes;
if either of them is not silver → no. The same reading applies to t08 and p13: a second gauntlet is not an error by
itself.

## Labelling note 2 and amendment 5 — 2026-10-15, during labelling, before any analysis

**Keys (p07).** The prompt asks for "a stolen iron keyring". Yes if the catfolk holds a ring or bunch with at least
one recognisable key (two bunches: yes); no if it holds nothing, or a bare ring with no key; "cannot tell" if a shape
on the ring may or may not be a key.

**Missing or changed characters.** Alessandro saw pictures where a character is missing or the catfolk is drawn as
an ordinary cat. For the primary questions: a question about a character that is not in the picture is answered
"no" (the prompt asks for it); questions about fur, eyes or colour are answered on what is drawn, whatever the
catfolk's anatomy.

**Amendment 5: six secondary questions, added during labelling** (Alessandro had seen part of the pictures; they
decide nothing and are reported as counts by version, like amendment 4's): s01/s04 all four characters present;
s02/s05 the catfolk is humanoid, not an animal; s03/s06 no extra characters (background guards in the prison do not
count). They are appended at the end of the labelling page (360 more answers, new schedule rows with RNG seed 7879);
answers already given are untouched.
