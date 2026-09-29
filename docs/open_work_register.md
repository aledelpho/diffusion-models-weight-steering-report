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
| ~~**A7**~~ | **DONE** — G_eye answered 2026-09-28: 9 of 12 resolved, 7 agreeing with `L`, threshold 8. The primary now carries *"L not validated by eye"*. | `centre_push_eye_veto_result.md` |
| **A8** | **what the primary of `centre_push` should now say.** The model-eye veto resolved only 5 of 12 pairs and `L` is wrong by eye on named units (`centre_push_eye_veto_result.md` §2). The analyst has changed nothing. | `centre_push_eye_veto_result.md` |
| **A9** | **whether the tool should be repaired.** If the rule is dimensionality, `ArthemyKrea2PresetLoader` silently drops every 1-D patch while reporting it applied — **165 of 430 tensors**, all of them gains, temperatures and modulation. Repairing it, or making it warn, is a change to the instrument and not the analyst's to make | `parameter_families_first_result.md` §3 |
| **A10** | **`krea2_architecture_decomposition.md` §3b names a tensor the checkpoint does not contain** — `txtfusion.projector.scale` [12] instead of `txtfusion.projector.weight` [1, 12]. It is the tensor on which `parameter_families_first_result.md` §3 turns, and the document says the opposite of the checkpoint. Repair or declare | verified against `krea2_turbo_bf16_details.json` |
| ~~**A11**~~ | **ANSWERED** — "Mi sembra l'unione di tutte insieme." Agrees with fine-grain composition (12/12 within 11 %), disagrees with the direction test (sum beats the best single slice in 7/36). `wo_depth_result.md` §8·0 | — |

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
| **B11** | **recompute structure coherence at 3×3 and 5×5 on the 24 crops of the eye veto** — now with a human answer to score against. `L` has the **sign wrong** on `Block_6 pos 0.080` and `Block_1 neg 0.500`, both scored above baseline and both called broken by Alessandro and by six blind observers. If the window is the cause, the smaller window flips exactly those two | decides whether coherence is repairable or must be retired |

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
| **C35** | **SPEC READY** — `RENDERS_2026-09-28_parameter_families.md`, `data/family_bench_plan.csv`, 36 presets generated from the checkpoint listing, predictions G1-G3 and P1-P5 frozen. **Isolate one parameter family at a time** — no bench has ever moved anything smaller than a block. Order of leverage per parameter: `qknorm` alone (8 192 params, an attention-temperature control that has ridden inside every `*_attn` atlas condition unexamined), then `first`/`last` (the 64-channel latent interface), then `mod.lin` at a large gain, then kind 1 with kinds 2-4 held fixed. `parameter_families.md` §5 | ~96 |
| **C36** | **FROZEN** in §2 of the same spec: the matched quantity is the relative gain delta and nothing else; displacement is recorded as an observed covariate and explicitly not controlled; families are compared by the shape of the delta-to-effect curve. Was: **a matching rule for families that displacement cannot compare.** Scaling every block norm gain by 10 % is a relative Frobenius displacement of 5.3e-4 against a standard edit's 0.05 — 100x smaller. Matched-displacement controls are impossible there, and the replacement rule must be frozen **before** the data (pitfall 68) | 0 |
| **C34** | **run the decisive test on the norm scales**, specified in `atlas_vs_tuner_generator.md` on 2026-09-26 and never queued: bake the patched model with the tuner's Saver and compare `blocks.0.prenorm.scale` against the checkpoint. Different → these 84 parameters are inert to rescaling, a real statement about the architecture. Identical → ComfyUI never materialises a scalar patch on a non-`.weight` parameter, and the tuner should refuse instead of reporting 84 patched layers | 0 renders |
| **C33** | **capture the tuner's logger output beside every bench's renders**, and add a decoded-pixel hash against the baseline to the provenance step. Either check would have caught the `normscales` hole in April; the warning is already written and already emitted, and goes nowhere | 0 |
| ~~**C37**~~ | **WITHDRAWN 2026-09-29** — premised on `Block_4 pos` / `Block_1 pos` at 0.500 "holding the line"; opened, both renders are destroyed (no subject; crumpled strokes and colour confetti). `centre_push_result.md` §4, retraction | — |
| **C38** | **run the eye veto owed by `prereg_centre_push.md`** — 12 centre/extreme pairs at matched V, 1:1 crops, blind. Until it runs the primary is not validated by eye, and `analyze_centre_push.py` does not implement it | 0 renders |
| **C39** | **the position grouping is wrong and should be replaced by a measured one.** `Block_1` (an "extreme") breaks the line in 9 % of visible units, `Block_6` in 93 %, `Block_5` behaves like `Block_6`. Any future contrast that splits by depth inherits this error | 0 renders |
| **C30** | **locate the knee.** Coherence is flat or rising to dose 0.120 and collapses at 0.200 for `Block_6 pos` (1.009 → 0.927), `Block_5 pos` (0.994 → 0.950) and, accelerating, `Block_6 neg` (0.926 → 0.794). The ladder has no point in between. Doses 0.140, 0.160, 0.180 on those three conditions locate it, and **0.200 is the dose almost every bench in this project uses** | ~54 |
| **C31** | pre-register **`Block_5 neg`** (coherence rises monotonically to 1.033, no knee, never singled out by anything) and **`blk27 pos`** (the largest line-preserving move of all 56 single-block conditions, 0.379 at coherence 1.023 — the same block whose negative arm is 75th of 80) | ~72 |
| **C32** | **the `Block_1` / `Block_6` contrast needs a quantity that is not spatial scale.** Both peak at 4–8 px and both cut a hole there on the opposite arm; page 08's distinction between them cannot be a difference of scale (`retro_mappa_reading_result.md` §3) | 0 |
| **C21** | **why is `blk16` super-linear above dose 0.120?** Style 0.045→0.066→0.095→0.138→0.194 is close to linear, then 0.447 at 0.200: factor 2.3 for a dose factor 1.67. Every step below is linear. Intermediate doses 0.140, 0.160, 0.180, both arms | ~72 |
| ~~**C22**~~ | **DONE, negative** — `leaf_collapse_predictors_result.md`: 0 of 12 baseline features survive Bonferroni, and an exact permutation test over all 167 960 splits gives p = 0.535. Baseline chroma, the obvious candidate, is 0.50326 against 0.50309. The collapse is not a property of the image the model was going to draw | 0 |
| **C28** | **pre-register `late_mlp`.** On the atlas re-read it moves the image as far as anything in the corpus while *raising* coherence, in six styles of eight (up to 1.24). It is `blk16`'s result on a second corpus at a different granularity, and it costs nothing to freeze before it is claimed | ~72 |
| **C29** | join the remaining 1 653 renders to their baselines and re-read their published claims on the two new axes — `qkvo_atlas`, `stage4_preset`, `stage5`, `stage7`, `stage9`, `pavimento_rumore`, `latenti_b6`. Handed over in `HANDOVER_2026-09-28_retro_axes.md`. **No renders** | 0 |
| **C26** | **pre-register the band-2 separation of mask against anti-mask.** On the positive arm the mask adds more energy at 4-8 px than its anti-mask in 12 of 12 cells, p = 0.0005 — the first statistic on which the mask bench separates the two cleanly. M5 asked this question and could not be read; this is a different statistic and a new question, and it must be frozen before it is claimed. Second prompt family, second dose | ~72 |
| **C27** | **the two damage modes of `Block_6` negative**: monotone stripping (hardest at 1-2 px, floor 0.36-0.39) against a mid-scale notch (2-8 px gutted, finest and coarsest kept). Which one appears is set by the relative sign of the two sub-blocks. Replicate on a second prompt family and check whether the notch tracks dose | ~48 |
| **C25** | **rerun arm C on ambiguous-prior subjects.** Screen candidates first with `experiments/prior_ambiguity.py`: render only the undeclared and prototypical-declared baselines, keep the subjects above ~30 deg apart (the leaf is 52.2; mushroom, tomato, pinecone and banana are 0.9-9.9 and were useless), then spend renders on the edit. A flower — the subject rejected when arm C was designed, for the very property that made it right — is the first candidate | ~24 screen + ~72 |
| **C23** | **dose ladder on the firing seeds.** The nine that fire and nine that do not, at doses 0.050, 0.080, 0.120, 0.200. If the switch has a per-seed dose threshold, that threshold is the bifurcation parameter and it is measurable. Follows directly from C22's negative | ~72 |
| **C24** | **decode the latent at intermediate steps** (3, 5, 7) for four firing and four quiet seeds. C22 rules out the endpoint, so the separation — if there is one — happens during denoising. Needs a workflow change, not just a queue | ~24 |
| **C14** | **measure the joint effect of a sub-block pair directly, at both relative signs**, instead of predicting it by composing singles. Forced by `rectified_mask_result.md`: M4 missed by 0.31 *and by direction*, so every mask designed on composed predictions is untestable until this exists. `Block_6` (`blk26`/`blk27`) first, where the failure is largest | ~48 |
| ~~**C15**~~ | **WITHDRAWN** — the ordering reverses on four new subjects (prototypical ≈ undeclared < unusual, 4/4), so it is a property of that leaf prompt, not of declared colour. Was: **pre-register `LG` < `LP` < `LN`** — prototypical declared colour is pinned, unusual declared colour is not, undeclared is free — on a **second object and a second colour pair**. Post hoc at present: 10/12 conditions, p = 0.039 on one arm only, one object (`colour_gate_and_chroma_audit.md` §5) | ~108 |
| ~~**C16**~~ | **DONE** — `leaf_collapse_and_blk16_result.md`: L1 and L2 confirmed (9/20 against 0/20), L3, L4 and L5 falsified. Reproducible, and confined to one prompt and one subject. Was: the achromatic singleton: one cell in 108 kept the object and lost 96 % of its chroma (`LN_Block_4neg_0.200`, seed 1337), and it replicates on neither of its own two sibling seeds. **Same condition, ~20 seeds**, to separate a seed × condition interaction from a one-off. Cheap and decisive | ~20 |
| **C17** | pre-register the **chroma antisymmetry** of `Block_3` (pos ×1.563 / neg ×0.931) and `Block_6` (pos ×0.726 / neg ×1.815), 18/18 cells each, p = 1e-5, on a second object and a second prompt family. Hue is pinned, chroma is not — and nothing pre-registered had looked at chroma (`colour_gate_and_chroma_audit.md` §6) | ~72 |
| ~~**C19**~~ | **DONE** — K1, K2 and K3 confirmed, K4 grey. Coherence rises with dose to x1.040 while style rises to 0.447; K3 reproduces an existing cell to four decimals across benches. Was: **`blk16`, dose ladder 0.020–0.200 both arms, second prompt family.** The single block that moves style most while *raising* the orientation of the drawing (style 0.447, coherence ×1.040, 6/6 cells, rank 1–2 of 80). It is a member of `Block_4`, the family Alessandro identified by eye. Supersedes the earlier `blk27` entry, which bought its style by dissolving the line (coherence ×0.802, rank 75/80) | ~72 |
| **C19b** | `blk27` keeps an entry, but as the **grain anomaly** — nominated by Punto 7 §3 on swing and by `internal_fights_by_group.md` as the member that reverses its own group — **not** as an operating point | ~72 |
| ~~**C20**~~ | **ANSWERED, at zero cost** — `retro_axes_atlas_result.md` §2: the atlas already carried eight style families. Coherence discriminates on photo, watercolour and charcoal (spread 0.09-0.10, a quarter of cells below 0.90) and is near-blind on lowpoly, claymation, ukiyo-e and pixel (spread 0.04, 1%). **Every structural claim of 2026-09-28 is now scoped to line-bearing styles.** Was: **validate structure coherence as a quality axis on a photographic prompt family.** Partly answered: `texture_anisotropy.py` separates exactly what the observer separated, and ranks this project's own recommendations last. But it is one number on one drawing style, and a comic-line baseline is the case where it should work best | ~0 renders |
| **C40** | **one preset separates “one-dimensional” from “ignored by the forward pass”.** `last.modulation.lin` is [2, 6144] and 2-D; `blocks.N.mod.lin` is [36864] and 1-D and proven dead. Both are modulation. If the 2-D one moves the image, the tool has a repairable defect; if it does not, the model ignores modulation. Tighter still inside one module: `first.weight` is live, `first.bias` [6144] is untried | **~12** |
| ~~**C41**~~ | **RUN** — composition **not supported** at ±0.100 (all four combinations), but the test was unpassable: at that dose a slice agrees with itself across seeds at cos 0.06–0.39 (pitfall 89). Exploratory: fine grain composes multiplicatively within 1–11 %, the union is more reproducible than its parts, the negative-arm grain profile is a U in depth. `wo_depth_result.md` | 254 |
| **C42** | **the composition test, done so it can pass**: the six-slice decomposition at a dose where the parts reproduce, **pre-registered with the reproducibility ceiling stated next to the threshold** (pitfall 89). **Not on the existing ±0.350 renders**: their composition numbers have already been seen, and scoring them under a new pre-registration would be pitfall 68. **Add as a pre-registered prediction: Δ(b1)+Δ(b6) is at least as close to the union as the full six-slice sum** — the hypothesis that reconciles the eye with the direction test (`wo_depth_result.md` §8·0). Three new seeds on `P01`/`P02` at ±0.350: 14 conditions × 2 prompts × 3 seeds + 6 baselines | **~90** |
| **C43** | **single blocks with seeds.** The atlas has one seed, so a middle block's failure to be recognised across pictures cannot be told apart from that seed's trajectory. Re-render the blocks that matter — 0, 1, 20, 23, 25, 26, 27 plus two middle controls (12, 16) — at ±0.350 and ±0.200, two more seeds, the same three prompts. Settles which of §5's "controls" are the block and which are the seed (`single_blocks_atlas_result.md`) | **~216** |
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
| **87** | a novelty check performed after publication is not a novelty check. Third re-derivation of an already-documented result in one day; the first grep returned the right document as its first hit, and it was run only when the user asked. **Rule: before writing any document that reports a finding, grep `docs/` and `notebook/` for its key terms in both languages and record what the search returned, including "nothing"** | drafted, `normscales_never_applied.md` §4 |
| ~~86~~ | *withdrawn with the finding — the phenomenon is real and was documented on 2026-09-26 in `atlas_vs_tuner_generator.md`* | — |
| **85** | a convolution that zero-pads at the frame edge, inside a statistic that reads the frame edge as content. On a constant image, whose true band energy is 0, `np.convolve(..., mode="same")` reports 4.0e-4 — a quarter of a real render's band-0 energy. Away from an 8 px frame the two conventions agree to 0.000% | drafted, `estimator_precision_defect.md` §3 |
| **84** | a summed-area table in float32. A cumulative sum over 1.3 million values of order 1e-4, then differenced, loses **0.9% per window** to catastrophic cancellation and 2.5% on the aggregate. It moved the headline condition of `style_damage_frontier.md` from 12th of 80 to 1st. Rule earned: **an estimator is cross-checked against an independent implementation before anything is published from it** | drafted, `estimator_precision_defect.md` §2 |
| **83** | measuring a claim about the surface in the space of the layout. The first test of "the combined condition looks like Block_6" used the 8x downsampled luminance and returned 1.09x and 0.91x, i.e. nothing; in the space of the band profile the same claim is 3.8x to 11.5x, four times out of four. The measurement was not wrong, it was aimed at the wrong quantity | drafted, `mask_damage_taxonomy_result.md` §3 |
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
2. **A1–A3** — twenty drafted pitfalls sitting outside the error log, which is the project's most
   transferable output.
3. **C1** — the only live experiment with a passed gate.
4. The **`permutation-adds-a-neglected-attribute` replication** — 19/20 against 1/20 is the largest
   effect in the project and it is stuck on a formality. It is also the existence proof that a
   *measured* rearrangement beats a *random* one at identical displacement, which is the premise of
   every stacking and masking design in **C11–C13**.
5. **C11** — the angle rule is load-bearing for three queued designs and was measured only in the
   degraded regime.
