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
| **B9** | **re-run the sign-stability pre-check on a Frobenius-matched bench.** It failed on the q/k/v/o cells (7/184 unanimous against 1.4 by chance), but those cells span a factor **2.77** in displacement, so "below noise" and "given less dose" are the same observation there | decides whether a sign-correction mask is buildable at all — `assessment_sign_correction_mask.md` §5 |
| **B10** | rewrite `blk00` as a **contrast** knob. The variance ratios for all 28 blocks and both arms are already in `data/texture_audit_profondita.csv` | a replacement claim with a better estimator than the one just discredited |

## C. Costs renders — Alessandro launches

| # | work | size |
|---|---|--:|
| **C1** | **Stage 2 of the colour-binding study** — the gate passed, this is live | **78** (117 with `LN`) |
| **C2** | replicate q/k vs v/o on a **middle band never used to find it**, prediction frozen first | 192 |
| **C3** | the **downward dose probe** below 0.020 — our own data predicts nothing, which is why it is a small batch | ~96 |
| **C4** | `mod.lin` alone, to finish the dead-arm decomposition | 24 |
| **C5** | a bench where **one block group and a scramble carry the same D** — the comparison `structured_vs_scattered.md` §4 could not make | ~72 |
| **C6** | the crossed-domain replication of `prereg_domain_specificity` §8 | 160 |
| **C11** | **replicate the angle rule at low dose.** ρ = 0.939 − 0.278·cos rests entirely on nine pairs at dose 0.200, a degraded regime whose cosines correlate only r = +0.42 with those at 0.050. Every stacking design depends on this law | ~72 |
| **C12** | one more pair between cos −0.2 and 0.0, to test whether **super-additivity** (`B1+B4`, ρ = 1.167, 2.9 SE above 1) is systematic. If it is, the line is the chord of a curve and the optimal stack is not the linear one | 12 |
| **C13** | the **signed map** at q/k/v/o granularity, at matched displacement, against `RANDSIGN` at the same D — only after **B9** and **C11** | 288 |
| **C21** | **why is `blk16` super-linear above dose 0.120?** Style 0.045→0.066→0.095→0.138→0.194 is close to linear, then 0.447 at 0.200: factor 2.3 for a dose factor 1.67. Every step below is linear. Intermediate doses 0.140, 0.160, 0.180, both arms | ~72 |
| ~~**C22**~~ | **DONE, negative** — `leaf_collapse_predictors_result.md`: 0 of 12 baseline features survive Bonferroni, and an exact permutation test over all 167 960 splits gives p = 0.535. Baseline chroma, the obvious candidate, is 0.50326 against 0.50309. The collapse is not a property of the image the model was going to draw | 0 |
| **C25** | **rerun arm C on ambiguous-prior subjects.** Screen candidates first with `experiments/prior_ambiguity.py`: render only the undeclared and prototypical-declared baselines, keep the subjects above ~30 deg apart (the leaf is 52.2; mushroom, tomato, pinecone and banana are 0.9-9.9 and were useless), then spend renders on the edit. A flower — the subject rejected when arm C was designed, for the very property that made it right — is the first candidate | ~24 screen + ~72 |
| **C23** | **dose ladder on the firing seeds.** The nine that fire and nine that do not, at doses 0.050, 0.080, 0.120, 0.200. If the switch has a per-seed dose threshold, that threshold is the bifurcation parameter and it is measurable. Follows directly from C22's negative | ~72 |
| **C24** | **decode the latent at intermediate steps** (3, 5, 7) for four firing and four quiet seeds. C22 rules out the endpoint, so the separation — if there is one — happens during denoising. Needs a workflow change, not just a queue | ~24 |
| **C14** | **measure the joint effect of a sub-block pair directly, at both relative signs**, instead of predicting it by composing singles. Forced by `rectified_mask_result.md`: M4 missed by 0.31 *and by direction*, so every mask designed on composed predictions is untestable until this exists. `Block_6` (`blk26`/`blk27`) first, where the failure is largest | ~48 |
| ~~**C15**~~ | **WITHDRAWN** — the ordering reverses on four new subjects (prototypical ≈ undeclared < unusual, 4/4), so it is a property of that leaf prompt, not of declared colour. Was: **pre-register `LG` < `LP` < `LN`** — prototypical declared colour is pinned, unusual declared colour is not, undeclared is free — on a **second object and a second colour pair**. Post hoc at present: 10/12 conditions, p = 0.039 on one arm only, one object (`colour_gate_and_chroma_audit.md` §5) | ~108 |
| ~~**C16**~~ | **DONE** — `leaf_collapse_and_blk16_result.md`: L1 and L2 confirmed (9/20 against 0/20), L3, L4 and L5 falsified. Reproducible, and confined to one prompt and one subject. Was: the achromatic singleton: one cell in 108 kept the object and lost 96 % of its chroma (`LN_Block_4neg_0.200`, seed 1337), and it replicates on neither of its own two sibling seeds. **Same condition, ~20 seeds**, to separate a seed × condition interaction from a one-off. Cheap and decisive | ~20 |
| **C17** | pre-register the **chroma antisymmetry** of `Block_3` (pos ×1.563 / neg ×0.931) and `Block_6` (pos ×0.726 / neg ×1.815), 18/18 cells each, p = 1e-5, on a second object and a second prompt family. Hue is pinned, chroma is not — and nothing pre-registered had looked at chroma (`colour_gate_and_chroma_audit.md` §6) | ~72 |
| ~~**C19**~~ | **DONE** — K1, K2 and K3 confirmed, K4 grey. Coherence rises with dose to x1.040 while style rises to 0.447; K3 reproduces an existing cell to four decimals across benches. Was: **`blk16`, dose ladder 0.020–0.200 both arms, second prompt family.** The single block that moves style most while *raising* the orientation of the drawing (style 0.447, coherence ×1.040, 6/6 cells, rank 1–2 of 80). It is a member of `Block_4`, the family Alessandro identified by eye. Supersedes the earlier `blk27` entry, which bought its style by dissolving the line (coherence ×0.802, rank 75/80) | ~72 |
| **C19b** | `blk27` keeps an entry, but as the **grain anomaly** — nominated by Punto 7 §3 on swing and by `internal_fights_by_group.md` as the member that reverses its own group — **not** as an operating point | ~72 |
| **C20** | **validate structure coherence as a quality axis on a photographic prompt family.** Partly answered: `texture_anisotropy.py` separates exactly what the observer separated, and ranks this project's own recommendations last. But it is one number on one drawing style, and a comic-line baseline is the case where it should work best | ~0 renders |
| **C18** | **colour binding at q/k/v/o granularity, key projection first.** Forced by §8: no whole block, in either arm, releases a declared unusual colour toward its prior (6/36 cells). ColorWave (arXiv 2503.09864) localises attribute binding at the key projection, and `benchmark_qkvo_atlas` has never been pointed at colour | ~192 |
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
| **80** | an isotropic texture summary reports a decrease while the texture is being wholly replaced: \|ln(grain ratio)\| against band-0 difference energy over 140 conditions gives **r = −0.054**, and `blk27 neg` reads grain 0.841 with band-0 difference energy 1.53x the baseline's | drafted, `style_damage_frontier.md` §8a |
| **79** | two axes declared independent because they were *built* differently, without measuring it: `layout_cost_z` (8x downsample) against band-0 fine detail is **r = +0.798**, so a Pareto frontier between them is largely one quantity against itself | drafted, `style_damage_frontier.md` §8b |
| **82** | choosing the test population by the property that makes the effect impossible. Four subjects were picked for a **strong** colour prior in order to test a mechanism that requires a **weak** one, and the resulting null was published as a falsification ("leaf-specific"). The screening measurement that would have caught it costs two baselines per candidate | drafted, `looking_at_the_leaf_corpus.md` §1 |
| **81** | taking the base rate from the whole corpus when the event is conditional on one cell of it. The achromatic leaf was filed as "a singleton, 1 in 108" and demoted to a lead; only 3 of those 108 cells were the condition, so the rate was 1/3, and a 20-seed replication returned 9/20. Understated by the number of cells divided by | drafted, `leaf_collapse_and_blk16_result.md` §2 |
| **78** | judging a pixel-level property (grain, texture, artefacts) from a whole frame rendered down to fit, then reporting the judgement as evidence. Withdrawn claim: "no artefacts" on the two conditions the observer then identified as the most damaged in the corpus. **Remedy, stated by Alessandro and adopted as procedure: whenever grain or texture is the question, cut a section and look at it at 100 %.** A statement about detail requires a view that contains the detail — for a 1024x1280 render that means a crop of a few hundred pixels shown unscaled, not the frame. The same applies to any estimator: state the spatial scale it samples before reading it | drafted, `style_damage_frontier.md` §7 |
| **77** | a value-threshold foreground with no low-pass measures texture, not shape: on the grain block it tripled the foreground to 0.30 of the frame and reported a 60 % chroma collapse and a destroyed object, both artefacts. Committed in `9eef1ad` inside a document criticising a detector for exactly this | drafted, `colour_gate_and_chroma_audit.md` §7 |
| **76** | an "object intact" criterion built from the same quantity the experiment is trying to move cannot see the experiment succeed — the sweep's foreground is `sat > 0.15`, so an object that loses its colour is filed as a destroyed object, and `mean_sat` is censored by the same mask | drafted, `colour_gate_and_chroma_audit.md` §2 |
| — | `evaluate_colour_object_sweep.py` / `_gate.py`: foreground must become value-based before either gates anything again | **open**, replacement in `experiments/colour_chroma_audit.py` |
| — | `stroke_width_median_px` is quantised to 5 values; still present in every feature table | flagged, not removed |
| — | the eight q/k/v/o cells are **not** Frobenius-matched (23.50 … 65.06) | flagged; `F` survives it, magnitudes do not |

## F. What would change the most

1. **B1** — if the grain statistic has been reporting the wrong sign, several published numbers move.
2. **A1–A3** — sixteen drafted pitfalls sitting outside the error log, which is the project's most
   transferable output.
3. **C1** — the only live experiment with a passed gate.
4. The **`permutation-adds-a-neglected-attribute` replication** — 19/20 against 1/20 is the largest
   effect in the project and it is stuck on a formality. It is also the existence proof that a
   *measured* rearrangement beats a *random* one at identical displacement, which is the premise of
   every stacking and masking design in **C11–C13**.
5. **C11** — the angle rule is load-bearing for three queued designs and was measured only in the
   degraded regime.
