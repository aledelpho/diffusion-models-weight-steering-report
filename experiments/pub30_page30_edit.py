"""PUB30: fold C77, C78, the 36-layer probe and C79 into results/30-the-text-encoder.md (2026-10-18)."""
import sys
from pathlib import Path
p = Path(sys.argv[1]); s = p.read_text(encoding="utf-8")

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)

rep("date: 2026-10-13\n", "date: 2026-10-18\n")
rep("pitfalls: [90]\n", "pitfalls: [90, 91]\n")
rep("  renders: 1649\n  prompts: 70\n", "  renders: 1917\n  prompts: 74\n")

NEW_CLAIMS = """  - id: te-separators-make-no-difference
    status: holds
    statement: >
      On prompts complex enough to produce errors, the separators between the parts of the prompt make no measurable
      difference: commas, periods, semicolons, no punctuation at all, or no "Character N" labels.
    evidence: >
      Pre-registered (C78), blind labels, two four-character prompts at eight seeds, twelve questions per prompt: every
      version lands within 0.25 errors of the original (1.50 errors per picture). Repeats kappa 0.954. On the encoder
      side, the separator changes how alike the tokens of one part are by less than 0.001.
    anchor: "#punctuation-break-and-labels"
  - id: te-break-breaks-the-scene
    status: holds
    statement: >
      Splitting the prompt with BREAK, so that each part is encoded on its own, makes the picture much worse: the scene
      falls apart.
    evidence: >
      Pre-registered (C78): +5.50 errors per picture against the original, worse in 16 of 16 pairs. All four characters
      are present in none of the 16 BREAK pictures, and the catfolk is never humanoid.
    anchor: "#punctuation-break-and-labels"
  - id: te-layer0-off-writes-text
    status: open
    statement: >
      With half of the first layer of the text encoder switched off, the image model writes fragments of the prompt as
      text instead of drawing it; with the whole layer off it draws coloured noise.
    evidence: >
      C77, rule fixed before the renders: text in 4 of 6 new pictures (holds at 5), so open. Counting the C64 elf,
      attention off writes text in 4 of 4 prompts, MLP off in 2 of 4, the whole layer off in 0 of 4 (exploratory). One
      seed, my readings, not blind. Encoder side: with half the layer off the conditioning keeps its scale (0.98x and
      0.84x) and the identity of the tokens; with the whole layer off its norm is 21.7x on average (62x at L05) and no
      token is recognisable.
    anchor: "#layer-0-switched-off"
  - id: te-l06-writes-the-stream
    status: open
    statement: >
      Inside the text encoder, one layer writes almost all of the internal signal: the MLP of layer 6 takes its size
      from about 400 to about 13,100, and every later layer up to 33 adds only 1 to 8 % of it.
    evidence: >
      Described, no pre-registration: a read-only probe of all 36 layers on 16 prompts. Layer 6's MLP writes 33.8 times
      the size of the signal it receives; layers 7-33 write 0.012-0.080 times; the last two reshape it (the norm falls
      to 12,768 and 6,606). L06 doubled is also the edit that turned seven portraits into realistic renders in 11 of 14 pictures (C73).
    anchor: "#inside-the-text-encoder"
  - id: te-damage-needs-many-taps
    status: holds
    statement: >
      The damage of the L06 and L14 edits does not travel through the readings taken right after the edited layer:
      restricted to them, the edit costs the character almost nothing.
    evidence: >
      Pre-registered (C79 rule 2), blind labels with C75's questions: trait loss with the push kept only on the next
      taps is 0.014 against 0.296 on all early and middle taps for L06 (ratio 0.05; rule at most 0.30), 0.000 against
      0.128 for L14 (one tap). Repeats kappa 1.00.
    anchor: "#which-taps-carry-the-damage"
  - id: te-damage-through-early-taps
    status: ambiguous
    statement: >
      The traits lost under L06 and L14 travel mostly through the early and middle readings of the text encoder (layers
      2-26) rather than the late ones (29-35).
    evidence: >
      Pre-registered (C79 rule 1): trait loss 0.212 with the push only on the early and middle taps, 0.066 only on the
      late ones; the difference, +0.146, misses the bar of +0.15, although the early taps cost more in 5 of 6
      character-edit pairs (bar 5). Inconclusive. Neither half alone reproduces the full edit, and together they fall
      short of it: on the same two seeds 0.37 against 0.46 (L06) and 0.16 against 0.38 (L14).
    anchor: "#which-taps-carry-the-damage"
---
"""
# the front matter ends at the first line that is exactly '---' after the opening one
head, sep, body = s.partition("\n---\n\n# The text encoder")
assert sep
s = head + "\n" + NEW_CLAIMS + "\n# The text encoder" + body

rep("> **Holds** · 1649 renders · 70 prompts · pre-registered 2026-10-12",
    "> **Holds** · 1917 renders · 74 prompts · pre-registered 2026-10-12")

rep("""> cost the character far more than random pushes of the same size, and turn dark skin lighter.
""", """> cost the character far more than random pushes of the same size, and turn dark skin lighter.
> Since then I've looked inside: one layer, L06, writes almost all of the encoder's internal signal; the damage does
> not travel through the readings right after the edited layer, and the two halves of the readings together fall
> short of the full edit. Switching off half of the very first layer makes the picture *write* the prompt. And on the
> prompt itself, the separators make no difference, while BREAK breaks the scene.
""")

TWO_MIN = """
Then I opened the text encoder itself. A probe that only reads, run on all 36 layers, shows one layer doing almost all
the writing: the MLP of layer 6 takes the internal signal from about 400 to about 13,100, and every layer after it, up
to 33, adds a few percent. And L06 doubled is the edit that turned my portraits into photographs. That is a coincidence
worth testing, not an explanation yet.

The image model doesn't read only the encoder's last layer: it takes **twelve readings** of every word, at layers 2, 5,
8 and so on up to 35, and mixes them. So I asked which readings carry the damage. I let the L06 and L14 edits reach
only some readings and kept the others at their original value. The readings right after the edited layer do
nothing. The early and middle ones cost more traits than the late ones, in five of six cases, but by a margin just
short of the bar I had fixed (0.146 against 0.15). And the strangest part: the two halves together don't add up to the
full edit. Under L14 they cost less than half of what the whole edit costs; the whole edit changes the person every
time, the halves never.

![The half-orc at four seeds under L06 MLP doubled: the original, the full edit (two seeds) turning her into a photograph of a generic woman, the push kept on the two readings right after the layer (unchanged), on the early and middle readings (a human woman with lighter skin, mostly still a comic) and on the late readings (a lighter, half-painted woman who keeps her ears).](../assets/30-the-text-encoder/F30.22_te_taps_L06_halforc.webp)

Then two curiosities. Switch off half of the encoder's **first** layer and the image model stops drawing: it
*writes*, filling the picture with fragments of the prompt ("realist: om wetern comips"). Switch off the whole layer
and you get coloured noise, no text at all. Measured on the encoder side, half a layer keeps the words recognisable at
a normal size; the whole layer gone loses both.

![Four prompts at one seed with layer 0 of the text encoder switched off: attention off fills the picture with fragments of the prompt as text, MLP off writes clean text for the elf and text over a face for the watercolour dwarf, the whole layer off gives tiled coloured noise every time.](../assets/30-the-text-encoder/F30.21_te_layer0_text.webp)

And people asked me about punctuation. On two complex prompts with four characters each, commas, periods,
semicolons, no punctuation at all, or no "Character 1 (…)" labels: no difference, within a quarter of an error. BREAK,
the old trick from CLIP-based models to stop concepts bleeding, does the opposite here: it breaks the scene in 16 of 16
pairs.
"""
rep("""
## The verdict
""", TWO_MIN + """
## The verdict
""")

rep("""that L28 costs traits without changing style.
""", """that L28 costs traits without changing style. **Holds** (C78): separators make no difference on complex prompts;
BREAK breaks the scene. **Open** (C77): half of layer 0 switched off makes the picture write the prompt (4 of 6, bar 5).
**Open**, described: L06's MLP writes almost all of the encoder's internal signal. **Holds** (C79): the damage does not
travel through the readings right after the edited layer. **Ambiguous** (C79): that it travels through the early and
middle readings rather than the late ones (+0.146 against a bar of +0.15).
""")

rep("""**The intensity scale mixed two things.**""", """**The newest results are thin.** C77 is one seed, four prompts and my own reading of the pictures. C78 rests on two
prompts that I wrote, and most questions sit near the ceiling, so a small effect of punctuation cannot be excluded.
In C79 I labelled alone, and contact sheets showing the conditions existed before I labelled: my perfect agreement
with myself on repeats (kappa 1.00) says I was consistent, not that I was not influenced. The probe of the 36 layers
is a description: no prediction was fixed before it.

**The intensity scale mixed two things.**""")

DATA = """
### Layer 0 switched off

C77 replicated a page of the C64 pilot notes: with the MLP of layer 0 switched off, the elf came out as text. I
switched off the attention or the MLP of layer 0 on three new prompts at the same seed, after re-rendering the C64 elf
(pixel-identical). The rule, fixed before the renders, asked for readable text in at least 5 of 6 pictures: it got 4.

| prompt (seed 1618033) | attention off | MLP off | whole layer off (exploratory) |
|---|---|---|---|
| elf, comic (C64) | text | text | noise |
| dwarf, comic | text | tiled pattern | noise |
| dragonborn, comic | text | tiled pattern | noise |
| dwarf, watercolour | text | text over a face | noise |

On the encoder side (`data/te_layer0_encoder_summary.csv`), with half the layer off the conditioning keeps a normal
size (0.98x and 0.84x on average over the twelve readings) and the identity of each token (a logit lens recovers it in
52 % and 62 % of positions, 51 % unedited). With the whole layer off its size is 21.7x on average, 62x at L05, and no
token is recovered. My reading, not tested: the picture writes the prompt when the conditioning keeps the words at a
normal size but has lost part of what layer 0 adds to them. No experiment varies the two separately.

### Punctuation, BREAK and labels

C78 asked whether the separators between the parts of a prompt matter, on two prompts with four characters each
(a prison break and a totem), eight seeds, seven versions. Before the pilot I fixed twelve yes/no questions per prompt;
I answered them blind to version and seed (`data/te_punct_alessandro.csv`, 2,640 answers, repeats kappa 0.954).

| version | errors per picture | against the original | better / worse / tied (16 pairs) | verdict |
|---|---|---|---|---|
| original | 1.50 | | | |
| commas | 1.44 | -0.06 | 5 / 4 / 7 | no difference |
| periods | 1.31 | -0.19 | 4 / 1 / 11 | no difference |
| semicolons | 1.31 | -0.19 | 6 / 3 / 7 | no difference |
| no punctuation | 1.75 | +0.25 | 2 / 6 / 8 | no difference |
| no "Character N" labels | 1.69 | +0.19 | 1 / 3 / 12 | no difference |
| BREAK | 7.00 | **+5.50** | 0 / **16** / 0 | **worse** |

With BREAK no picture has all four characters, and the catfolk is never humanoid. The errors left in the other
versions are omissions the model makes in every version (the elf's blue sparks: 0 of 8 everywhere). Questions chosen
after the pilot, which decide nothing, show one more thing: without the labels two leaks between characters disappear
(the orc's green on the elf's fist, the orc's folded arms on the tiefling), but the totem's catfolk becomes an
ordinary cat in 7 of 8. On the encoder side, the separator changes how alike the tokens of one part are by less than
0.001 (`data/te_punct_encoder_summary.csv`).

### Inside the text encoder

A probe that only reads (no picture), on 16 prompts, measures how much each of the 36 layers writes into the
encoder's internal signal, relative to the size of the signal it receives (`data/te_residual_probe_summary.csv`).

| layers | size of the signal after the layer | what the layer writes, relative to what it receives |
|---|---|---|
| 0 | 12.6 → 106.9 | 8.5 |
| 1-5 | 186 → 398 | 0.47-1.23 |
| **6** | **398 → 13,107** | **33.8** (almost all of it from the MLP) |
| 7-33 | 13,108 → 14,136 | 0.012-0.080 |
| 34-35 | 12,768, then 6,606 | 0.24, 0.65 |

Described, not tested. L06 doubled is the edit that turned the portraits into realistic renders (11 of 14 in C73) and
jumped from comic to photograph in the dose ladder (C74). Whether it is
destructive *because* it writes so much is the next question on the roadmap.

### Which taps carry the damage

The image model reads twelve **taps** of the text encoder: the internal signal entering layers 2, 5, 8, …, 35
(`txtfusion` normalises them and mixes them before the image model sees them). An edit to layer 6 changes taps 2-11;
an edit to layer 14 changes taps 5-11; L28, the edit that keeps the comic and the character, changes only taps 9-11.
So: does the damage of L06 and L14 travel through the early and middle taps (0-8), or through the late ones (9-11),
where L28 is harmless?

C79 computed the edit's push on the conditioning and let it through only on some taps: the next two (L06) or the
next one (L14), the early and middle ones, the late ones. Kept on all twelve, the push reproduces the full edit
pixel for pixel; the two halves add up to it exactly. Three characters, four seeds, 72 renders, 108 showings labelled
blind with C75's questions, one at a time (`data/te_tap_alessandro.csv`).

| test (pre-registered) | value | rule | verdict |
|---|---|---|---|
| 1 — early and middle taps cost more traits than late ones | 0.212 against 0.066, +0.146; 5 of 6 pairs | ≥ +0.15 and 5 of 6 | inconclusive |
| 2 — the taps right after the layer are enough, L06 | 0.014 / 0.296 = 0.05 | ≥ 0.70 enough, ≤ 0.30 not | not enough |
| 2 — the same, L14 (one tap) | 0.000 / 0.128 = 0.00 | same | not enough |
| 3 — automatic distances agree (DINOv2 / CSD) | 15 of 24 / 3 of 24 cells | ≥ 18 of 24 | no / opposite |
| reliability on repeats | kappa 1.00 | ≥ 0.60 | passed |

Trait loss on the two seeds where the full edit exists:

| edit | next taps | early and middle | late | the two halves summed | full edit |
|---|---|---|---|---|---|
| L06 | 0.01 | 0.31 | 0.07 | 0.37 | 0.46 |
| L14 | 0.00 | 0.12 | 0.03 | 0.16 | 0.38 |

![The half-orc at four seeds under L14 MLP doubled: the full edit (two seeds) turns her into a light-skinned human with brown braids; with the push on one tap, on the early and middle taps or on the late taps she stays a half-orc, with small changes to her hair and a tusk.](../assets/30-the-text-encoder/F30.23_te_taps_L14_halforc.webp)

Reported, not tested: under L14 the full edit lightens the skin in 4 of 6 pictures and changes the person in 6 of 6,
the half-tap pictures in 0 of 24. Under L06 the early and middle taps lighten it in 6 of 12 and change the person in
6 of 12, the late ones in 4 of 12 and 1 of 12. By CSD the late taps move the pictures more (21 of 24 cells); under L06,
DINOv2 and VQAScore move more with the early ones: a hint that the late taps carry rendering and the early ones
content, from a measure (CSD) that C66 did not validate for style.
"""
rep("""
### Reproducing this
""", DATA + """
### Reproducing this
""")

rep("""  - name: C74 dose ladder, MLP of L06, L14, L28 at d = 0.10, 0.25, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00
    dose: 0.10-1.00
    measured_D: not measured; the dose is a per-matrix gain, not a calibrated displacement
""", """  - name: C74 dose ladder, MLP of L06, L14, L28 at d = 0.10, 0.25, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00
    dose: 0.10-1.00
    measured_D: not measured; the dose is a per-matrix gain, not a calibrated displacement
  - name: C77 layer 0 attention, MLP or all seven matrices x 0
    dose: -1.00
    measured_D: not measured
  - name: C79 push of L06 or L14 MLP doubled, restricted to taps (2,3 or 4,5), 0-8 or 9-11 (Krea2ConditioningPush, variant taps)
    dose: 1.000
    measured_D: per-tap push norms in data/te_tap_isolation_encoder_by_tap.csv
""")
rep("""  files: [data/te_pilot_plan.csv, data/te_characters_plan.csv, data/te_bridge_plan.csv, data/te_default_plan.csv, data/te_fallback_plan.csv, data/te_dose_plan.csv, data/te_traits_plan.csv]
  ids:""", """  files: [data/te_pilot_plan.csv, data/te_characters_plan.csv, data/te_bridge_plan.csv, data/te_default_plan.csv, data/te_fallback_plan.csv, data/te_dose_plan.csv, data/te_traits_plan.csv, data/te_layer0_plan.csv, data/te_punct_plan.csv, data/te_punct2_plan.csv, data/te_punct_nopunct_plan.csv, data/te_tap_isolation_plan.csv]
  ids:""")
rep("""  folders: [benchmark_te_pilot, benchmark_te_characters, benchmark_te_bridge, benchmark_te_default, benchmark_te_fallback, benchmark_te_dose, benchmark_te_traits]
  manifests: [data/te_pilot_plan.csv, data/te_characters_plan.csv, data/te_bridge_plan.csv, data/te_default_plan.csv, data/te_fallback_plan.csv, data/te_dose_plan.csv, data/te_traits_plan.csv]""",
"""  folders: [benchmark_te_pilot, benchmark_te_characters, benchmark_te_bridge, benchmark_te_default, benchmark_te_fallback, benchmark_te_dose, benchmark_te_traits, benchmark_te_layer0, benchmark_te_layer0_block, benchmark_te_punct, benchmark_te_tap_isolation]
  manifests: [data/te_pilot_plan.csv, data/te_characters_plan.csv, data/te_bridge_plan.csv, data/te_default_plan.csv, data/te_fallback_plan.csv, data/te_dose_plan.csv, data/te_traits_plan.csv, data/te_layer0_plan.csv, data/te_punct_plan.csv, data/te_punct2_plan.csv, data/te_punct_nopunct_plan.csv, data/te_tap_isolation_plan.csv]""")
rep("""experiments/te_traits_explore.py, experiments/te_traits_explore_B2.py]""",
    """experiments/te_traits_explore.py, experiments/te_traits_explore_B2.py, experiments/te_layer0.py, experiments/te_layer0_block.py, experiments/te_layer0_encoder.py, experiments/te_punct.py, experiments/te_punct2.py, experiments/te_punct_page.py, experiments/te_punct_tally.py, experiments/te_punct_encoder.py, experiments/te_residual_probe.py, experiments/te_tap_isolation.py, experiments/te_tap_isolation_page.py, experiments/te_tap_isolation_tally.py]""")
rep("""data/te_traits_tests.csv, data/te_traits_B2_tests.csv
```""", """data/te_traits_tests.csv, data/te_traits_B2_tests.csv, data/te_layer0_encoder_summary.csv, data/te_punct_tests.csv, data/te_punct_encoder_summary.csv, data/te_residual_probe_summary.csv, data/te_tap_tests.csv, data/te_tap_isolation_metrics.csv
```""")
rep("""C75 random pushes and plain portraits (122, gate included).""",
    """C75 random pushes and plain portraits (122, gate included), C77 layer 0 (7, gate included, plus 4 with the whole layer off), C78 punctuation (181, gates and pilots included), C79 taps (76, four gates included).""")
rep("""* Encodes without images: C67 (721), C68 (241), C71 (16).""",
    """* Encodes without images: C67 (721), C68 (241), C71 (16); the 36-layer probe (16 prompts, read only).""")
rep("""`docs/prereg_te_traits.md` (+ amendments 1-4); the pilot plan""",
    """`docs/prereg_te_traits.md` (+ amendments 1-4), `docs/prereg_te_punct.md` (+ amendments 1-6), `docs/prereg_te_tap_isolation.md` (+ amendment 1; not committed before the renders, file times only); C77's rule is in the docstring of `experiments/te_layer0.py`, committed before its renders; the pilot plan""")
rep("""`docs/te_dose_result.md`, `docs/te_traits_result.md`.""",
    """`docs/te_dose_result.md`, `docs/te_traits_result.md`, `docs/te_layer0_result.md`, `docs/te_punct_result.md`, `docs/te_tap_isolation_result.md`.""")
rep("""`data/te_traits_B2_explore.csv`.""",
    """`data/te_traits_B2_explore.csv`, `data/te_layer0_encoder_by_tap.csv`, `data/te_punct_questions.csv`, `data/te_punct_key.csv`, `data/te_punct_alessandro.csv`, `data/te_punct_by_picture.csv`, `data/te_punct_secondary.csv`, `data/te_residual_probe_by_prompt.csv`, `data/te_tap_isolation_encoder_by_tap.csv`, `data/te_tap_isolation_txtfusion_weights.csv`, `data/te_tap_key.csv`, `data/te_tap_schedule.csv`, `data/te_tap_alessandro.csv`, `data/te_tap_by_picture.csv`, `data/te_tap_isolation_cells.csv`.""")
rep("""gate
  pixel-identical).""", """gate
  pixel-identical; its `taps` variant, used in C79, reproduces the full edit pixel for pixel when all twelve taps are
  kept).""")
p.write_text(s, encoding="utf-8")
print("ok")
