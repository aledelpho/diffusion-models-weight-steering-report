# Open work register — 2026-09-27

Supersedes nothing: [`backlog_2026-09-23.md`](backlog_2026-09-23.md) remains the notebook-completion
list and its items are carried here by reference, **their status unverified since 23/09**. This
register is the wider one — everything the project still owes an answer to.

**Counted from the files**: 43 claims (15 hold, 6 ambiguous, 18 open, 4 overturned), 69 pitfalls
logged, 6 drafted and not inserted.

---

## A. Decisions only Alessandro can make

Nothing below is blocked on work. It is blocked on a choice.

| # | decision | prepared |
|---|---|---|
| **A1** | insert pitfalls **70, 71, 72** into `errors_log.md` | `_pitfalls_70_72_da_inserire.md`, `pitfall_70_candidate.md`, `pitfall_71_candidate.md` |
| **A2** | insert pitfalls **73, 74, 75** (drafted today, not yet written up as rows) | §E below |
| **A3** | insert the older drafted rows **44–47, 48–50, 64–67**, still sitting in `_pitfalls_*_da_inserire.md` | drafted |
| **A4** | the 20 mismatched `prompt_sha1` rows in `data/stage9_images.csv` — repair or declare | not repaired |
| **A5** | whether `LN` (the no-colour-named arm) joins Stage 2 of the colour-binding study: +36 renders, 78 → 117 | `colour_binding_pilot_gate.md` §2 |
| **A6** | whether any claim status changes on this week's results. **The analyst has changed none.** | — |

## B. Costs no renders — the data is already on disk

| # | work | why it matters |
|---|---|---|
| **B1** | **Re-run every texture statistic in the project restricted to flat regions** (pitfall 75). The global measure called `Block_6` "both signs smooth" while it adds 32 % grain and removes 27 %. Every grain number in the notebook is suspect until checked. | the largest known measurement defect |
| **B2** | replicate the **q/k vs v/o split** analysis on a middle band — *analysis only*; the renders are the B-list item below | the only surviving new result of 26/09 |
| **B3** | `Block_3` is the cleanest bidirectional grain knob measured (**6/6** cells one way, **0/6** the other) and no document says so | a finding sitting in a table |
| **B4** | the **glitch belongs to the draw, not the region** (`early_attn_draw1` 0.0139 vs `draw2` 0.0485, same region, same D). Extend the detector to every bench | `looking_at_block1_and_block6.md` §5 |
| **B5** | `Block_2` transfers **below chance on stroke** (0.274). Unexplained | `signature_robustness_result.md` |
| **B6** | the **augmentation-robustness** test used one strength per operation. Harsher settings would find the edge this one did not | cheap, bounded |
| **B7** | backlog 23/09 items **A1–A6** — status unverified, need a pass | carried over |
| **B8** | apply the **23 traits and the judge** to `benchmark_mappa`, which has never been scored by either | the damage-or-style question on the block corpus |

## C. Costs renders — Alessandro launches

| # | work | size |
|---|---|--:|
| **C1** | **Stage 2 of the colour-binding study** — the gate passed, this is live | **78** (117 with `LN`) |
| **C2** | replicate q/k vs v/o on a **middle band never used to find it**, prediction frozen first | 192 |
| **C3** | the **downward dose probe** below 0.020 — our own data predicts nothing, which is why it is a small batch | ~96 |
| **C4** | `mod.lin` alone, to finish the dead-arm decomposition | 24 |
| **C5** | a bench where **one block group and a scramble carry the same D** — the comparison `structured_vs_scattered.md` §4 could not make | ~72 |
| **C6** | the crossed-domain replication of `prereg_domain_specificity` §8 | 160 |
| **C7** | Block K — trait combinations; page 02 is 0/4 | — |
| **C8** | blind 4-AFC at 1× without the baseline in the lineup | — |
| **C9** | the **"corrector"** objective: minimise noise at constant detail, beating "push block 0 positive" | — |
| **C10** | backlog 23/09 items **B1–B4** — status unverified | carried over |

## D. Claims that owe an answer

**Six ambiguous.** Each is a real effect stuck for a nameable reason:

| claim | why it is stuck | what would unstick it |
|---|---|---|
| `permutation-adds-a-neglected-attribute` | exploratory, no threshold fixed in advance — **19/20 against 1/20** | a pre-registered replication; this is the project's strongest unclaimed result |
| `edit-adds-and-removes-unasked-traits` | its confirmation corpus had the attribute at floor in 9/10 prompts | a corpus chosen with the attribute verified present first |
| `position-beats-displacement` | D not matched across blocks | **C5** |
| `hatching-axis-preset-runs-the-other-way` | never checked whether the measure tracks hatching orientation in that family | one measurement |
| `chromatic-signature-per-edit-is-ambiguous` | 3 of 6 conditions cleared a threshold of 4 | today's transfer result bears on it — colour does **not** survive a change of subject (0.514, p = 0.23) |
| `block1-does-not-replicate` | instability against position, unresolved | **C5** |

**Eighteen open.** Three got evidence this week and should be revisited first:

* `colour-does-not-generalise` — states the colour effect is *"present only where the prompt pins the
  palette"*. **Tested today on six matched pairs: 3/3, p = 1.000.** Null at low power, but it is now
  a measured claim rather than an untested one.
* `colour-and-texture-are-not-one-signature` — *"no account here explains it"*. There is one now:
  colour transfers across subjects at chance (0.514), texture at 0.778, p = 0.0097.
* `specialization-disagrees-with-separability` — the audit of 23/09 showed the specialisation
  classifier certifies a structureless scramble. The disagreement may be the classifier.

The other fifteen are listed in the notebook front matter and are not repeated here.

## E. Instrument defects found and not yet repaired

| # | defect | status |
|---|---|---|
| **73** | in a bilingual repository, a novelty check run in one language is not a novelty check | drafted, `sign_decomposition_retraction.md` §4 |
| **74** | a distributional guard averaged over heterogeneous questions can be satisfied by opposite pathologies cancelling | drafted, `prereg_damage_or_style.md` Am. 02 §C |
| **75** | a texture statistic not normalised for contrast reports the sum of two effects and can report the wrong sign | drafted, `looking_at_block1_and_block6.md` §3 |
| — | `evaluate_colour_object_gate.py` reports 15 files missing while all 15 are present and readable | **must be fixed before it gates anything** |
| — | `stroke_width_median_px` is quantised to 5 values; still present in every feature table | flagged, not removed |
| — | the eight q/k/v/o cells are **not** Frobenius-matched (23.50 … 65.06) | flagged; `F` survives it, magnitudes do not |

## F. What would change the most

1. **B1** — if the grain statistic has been reporting the wrong sign, several published numbers move.
2. **A1–A3** — nine drafted pitfalls sitting outside the error log, which is the project's most
   transferable output.
3. **C1** — the only live experiment with a passed gate.
4. The **`permutation-adds-a-neglected-attribute` replication** — 19/20 against 1/20 is the largest
   effect in the project and it is stuck on a formality.
