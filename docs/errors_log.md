# Measurement Protocol & Error Log: Replication Checklist

> **Purpose of this document**: This log records the 28 real-world measurement pitfalls encountered during benchmark development on Krea-2 DiT and the 8 derived methodological rules.  
> **None of these 28 errors produced absurd values or obvious runtime exceptions**: all produced seemingly plausible numbers, quietly distorting the scientific conclusions. This document serves as a **mandatory pre-flight checklist** before launching any new benchmark run (including testing on circlestone-labs/Anima (Cosmos-Predict2-2B + Qwen3 0.6B) or future diffusion architectures).

---

## The 8 Non-Negotiable Methodological Rules

Before analyzing data or drawing conclusions on any diffusion architecture:

1. **The null distribution is never zero; establish it before inspecting the treatment effect.**  
   Always construct at least two null baselines: the seed floor (purely stochastic dispersion across distinct seeds given the identical prompt) and the sign/label permutation null on prompt directions (the directional agreement expected purely by chance).
2. **If a metric is formulated as an unsigned distance, it cannot observe a trade-off: signed projection is required.**  
   Unsigned distances (Euclidean, unsigned cosine distance, absolute differences) are blind to direction. If an intervention shifts one feature positively and another negatively, an unsigned metric collapses everything into a generic scalar "change". The signed projection decomposition ($A = \frac{d^+ - d^-}{2}$, $S = \frac{d^+ + d^-}{2}$) is essential.
3. **Always separate direction from magnitude.**  
   Never conflate the displacement amplitude of a vector with angular alignment across distinct prompts.
4. **A control that cannot fail noisily is not a control.**  
   A sentinel test must have a threshold such that, if the pipeline is inert or corrupted, it fails unambiguously and loudly.
5. **A gate that tallies misses and proceeds is a gate that stays silent.**  
   If an audit procedure (e.g., verifying text encoder tensor keys) detects missing layers, it must raise a blocking exception, rather than printing a benign warning and outputting "PASSED".
6. **The unit of statistical analysis is the unit you wish to generalize over.**  
   In our setting, the independent statistical unit is the **prompt** (the subject), not the individual cell or seed. Treating repeated seeds as independent observations artificially inflates degrees of freedom ($t$-scores inflated by $\sim 2\times$ due to high Intraclass Correlation Coefficients, ICC 0.66–0.95).
7. **Every table printed to the terminal must be persisted to disk, always.**  
   Intermediate computations must never exist solely in transient stdout buffers.
8. **Always report the test resolution floor ($P_{\min}$).**  
   With $n$ prompts, the minimum achievable two-tailed $p$-value for an exact sign-permutation test is $2 / 2^n$. With $n = 6$ prompts, $P_{\min} = 0.03125$: no effect can achieve statistical significance after multiplicity correction (Holm/FDR), regardless of effect magnitude. With $n = 10$, $P_{\min} = 0.00195$, restoring statistical resolving power.

---

## The 32 Documented Measurement Pitfalls

| # | Pitfall Encountered | Failure Mechanism | Silent Consequence | How to Prevent in Replication |
|---|---|---|---|---|
| **1** | Subtracting $\mu_{\text{floor}}$ in z-score calculation | $\mu_{\text{floor}}$ measures distance between *different* seeds; $\mu_{\text{cell}}$ measures distance from the *same* seed | Real effects falsely appeared negative relative to the baseline seed floor | Always normalize against seed-paired baselines |
| **2** | All metrics formulated as unsigned distances | Unsigned distances cannot distinguish $\pm \theta$ from isotropic degradation | Antisymmetry was undetectable by construction; signed projection subsequently revealed $p = 3 \times 10^{-8}$ | Implement symmetric/antisymmetric ($S$ and $A$) decomposition |
| **3** | Mixed common/differential ratio | Conflated vector magnitude with angular alignment | Penalized the very phenomenon being measured; pure directional cosine increased effect signal from 1.23× to 7.6× | Compute cosine similarity purely on direction vectors |
| **4** | Sentinel perturbation set to $\epsilon = 10^{-3}$ in bfloat16 | Relative precision in bf16 has step size $2^{-8} \sim 2^{-7}$ ($0.0039 \sim 0.0078$) | Multipliers like $1.0001$ or $1.001$ flip zero bits: the sentinel was mathematically inert | Use perturbations $\ge 0.01$ or verify bitwise tensor alterations |
| **5** | Sentinel audit testing $\|z\| > 2$ | A minimal sentinel perturbation should remain within noise variance | Flagged properly functioning sentinels as catastrophic failures | Define acceptance criteria matched to the perturbation scale |
| **6** | Sentinels included inside Holm correction family | Treating internal diagnostic checks as research hypotheses | Inflated hypothesis family $m$ (from 240 to 280), needlessly eroding statistical power | Strictly separate integrity diagnostics from scientific hypotheses |
| **7** | Mismatched CSV column lookups | Silent discrepancy between Python dict keys and CSV header strings | Two out of five metrics silently failed to reach the results matrix | Validate tabular schemas with strict pre-flight assertions |
| **8** | Computing CLIP adherence against `prompt_tag` instead of full text | Script matched against short internal tags (e.g., `"tiefling_detective"`) | Measured embedding similarity against an arbitrary label string rather than the generative prompt | Pass the complete, verbatim prompt text |
| **9** | Grouping cells solely by `condition_id` | A single `condition_id` spanned across 3 distinct prompts | Erroneous denominator in cell-mean calculations | Group strictly by `(prompt_sha1, condition, seed)` |
| **10** | Round-trip sentinel $\pm\theta$ composition | ComfyUI patch application is additive against the base matrix: $U(R + R^T - I)\Sigma V^T$ | Produced $(2\cos\theta - 1)W$, representing a $-3.9\%$ scaling artifact rather than identity | Verify patcher linear algebra before chaining inverse transformations |
| **11** | Faceless prompt tagged with `has_face: True` | Manual metadata error on a specific prompt | Facial attribute axis collapsed silently for that prompt | Use automated attribute detectors or audited prompt manifests |
| **12** | Mismatched parameter names between engine dials and UI widgets | Discrepancy between internal tuner names and ComfyUI widget identifiers | **The only error that failed noisily with a runtime `ValueError`** | Maintain automated regression tests across node interfaces |
| **13** | Bisection returning best candidate on target convergence failure | When root-finding failed to converge within tolerance, it returned the nearest approximation | A cell labeled $D = 0.50$ actually contained $D = 0.43$ | Raise an explicit error if convergence tolerance is violated |
| **14** | `measured_delta` unadjusted in HALF amplitude condition | Half-amplitude rotations $\theta/2$ do not scale linearly in Frobenius space | Effective deltas drifted by the factor $\sin(\epsilon\theta/2) / \sin(\theta/2)$ | Analytically calculate or directly re-measure $D$ at each $\epsilon$ |
| **15** | Text encoder gate searching for mismatched prefix | Looked for `model.language_model.*` on a checkpoint formatted as `model.layers.*` | **288 out of 629 tensors counted as missing and ignored**: gate printed "PASSED" | Assert `len(missing) == 0` with no silent fallbacks |
| **16** | BLOCKSHUFFLE calibration factor $\alpha$ applied to unpermuted tensors | Global Frobenius recalibration inadvertently scaled frozen weights as well | Vision tower drifted to $-0.0273$ instead of $-0.0250$, unbalancing the control | Apply $\alpha$ scaling *strictly* to the permuted parameter subset |
| **17** | Treating 30 cells (6 prompts $\times$ 5 seeds) as independent observations | Seeds sharing a prompt have high Intraclass Correlation (ICC 0.66–0.95) | Fictitious degrees of freedom ($df = 29$ instead of $df = 5$), inflating $t$-scores by $\sim 2.1\times$ | Aggregate first at the prompt level ($n = 10$, $df = 9$) |
| **18** | Labeling contrast $P^+ + P^- - 2\cdot\text{Base}$ as "Asymmetry" | The calculated quantity is $2 \cdot S$, representing the **symmetric** component | The descriptive label stated the exact opposite of the underlying mathematics | Formally define mathematical terms prior to code implementation |
| **19** | Computing PCA directly on raw image feature matrices | Inter-subject variance (characters with distinct color palettes) dominated the space | PC1 at 49.7% explained "which character is depicted" rather than intervention effect | Always compute PCA on **paired differences relative to baseline** |
| **20** | Computing ICC on absolute feature scores | ICC measured $0.92$ even on the unperturbed Baseline condition | Merely confirmed that the metric reflected prompt subject identity | Compute ICC on intervention deltas |
| **21** | Image harvesting depending on missing `renders_root` column | Column was absent in `stage4_images.csv` | 4 prompts silently lost; resulting 6-prompt sample had resolution floor $P_{\min} = 0.031$ | Resolve images by unique `basename` via collision-checked hash map |
| **22** | Sampling combinatorial subsets in lexicographic order | Iterator pulled subsets heavily biased toward initial indices | Empirical scaling exponent distorted from $0.5$ to $0.9$ | Sample uniformly at random with fixed pseudorandom seeds |
| **23** | Transferring identity $\|A\|/\|S\| = \sqrt{\frac{1-c}{1+c}}$ from CLIP to Stroke space | Coincided within $0.3\%$ in CLIP; drifted by $-4.1\%$ in stroke space | Not a software bug, but the result of cell-amplitude weighting under heterogeneity | Never assume identities proven in one feature space hold identically in another |
| **24** | `EXPLAINED_VARIANCE_RATIO` written as a data row inside the PCA loadings table | Its value sits in the `PC1`…`PC4` columns like any feature loading | Any reader — or script — that ingests the file as a loadings matrix silently treats explained variance as a 24th feature, contaminating every cosine computed between axes | Keep metadata out of the matrix: separate file, or a column that marks the row type |
| **25** | A hand-kept tally disagreeing with its own per-item list | The header of a scoring set read `19 / 20` while all twenty seeds were marked positive; another read `1 / 10` against two positives | The headline number of the experiment, and every paired test built on it, came from the summary line rather than from the data | Never read the total; recompute it from the item list, and make the two disagreeing an error rather than a preference |
| **26** | Fisher's exact test on paired binary outcomes | The same seeds appear in every condition, so the two columns are repeated measures on one unit, not two independent samples | Fisher returned $p = 3 \times 10^{-10}$ where the correct paired McNemar test returns $7.6 \times 10^{-6}$ — four orders of magnitude of borrowed confidence, in the direction that flatters the result | With shared seeds, use McNemar on the discordant pairs; the binary twin of pitfall 17 |
| **27** | Assuming a base checkpoint and a ComfyUI-saved copy of it share tensor names | Anima Base v1.0 prefixes every key with `net.`; the same model saved out of ComfyUI uses `model.diffusion_model.` | The two spellings have **zero keys in common**, so an offline script reading the file directly matches nothing — and reports a clean run unless it was written to assert coverage | Resolve prefixes from the file actually being read, and make an integrity gate fail when a single expected tensor is unaccounted for |
| **28** | One sub-tensor map for blocks that are not shaped alike | In Anima, `blocks.N` has 20 tensors with `self_attn.output_proj` and `mlp.layer1`/`layer2`; `llm_adapter.blocks.N` has 19, with `self_attn.o_proj`, `mlp.0`/`mlp.2`, three extra norms and biases the main blocks do not have | A surgeon built on the main-block map silently touches nothing in the adapter blocks, while the node still reports the patches it attempted | One map per block family, and count the tensors each map actually matched against the tensors that exist |
| **29** | Estimating the paper white from a border ring of the frame | The prompts ask for a `white background`, so a ring of pixels at the edge looked like a safe sample of it — but the same prompts also ask for an `extreme close-up on the head only, tight framing`, and the head fills the border | The estimator returned `paper_L` = 65.7 ± 23.5 (bimodal: sometimes paper, sometimes cheek) and a subject fraction of 0.89–0.95, so every paper- and ink-derived feature was measuring skin. Replacing it with extreme-lightness k-means clusters carrying at least 3% of the mass gives `paper_L` = 99.0 ± 0.5 | Read the whole prompt before deciding where a quantity lives in the frame, and treat a bimodal distribution with a σ of 23 units as a failed estimator rather than a noisy one |
| **30** | Two experiments writing into the same output folder, with same-named manifests | A 228-render pilot and the 560-render confirmation both wrote into `benchmark_stage7\renders`, and both manifests were called `stage7_images.csv` | The existing harvester, pointed at that filename, measures the wrong 228 images and **prints a clean run** — no missing files, no error, just the wrong experiment. It had already been committed to the repository next to the right manifests, where a reader would inherit the collision | Resolve every image through its manifest, never through the directory; assert the manifest's seed against the seed in the filename and stop on mismatch; and never let two runs share an output root |
| **31** | A pre-registered stratification criterion that can only be checked after rendering | The design required four prompts in each of four 90° hue arcs, but hue is a property of the render, not of the prompt text | Either the criterion is unenforceable, or it is enforced by looking at images and then choosing — an unspecified selection step inside a pre-registered design. Worse, the lever did not work: the brief asked for cool subjects and got 14 of 16 prompts in a single arc, because on close-up portraits the measured swatches are skin and paper whatever the scene says | Split the corpus into a baseline-only stage and a deterministic selection rule that reads only baselines; and check that the quantity you intend to stratify on is actually controllable by the thing you are varying |
| **32** | Editing a script after freezing it by hash in a pre-registration | A reporting bug was fixed in the frozen analysis script — it printed the exact permutation floor while running Monte Carlo — hours after the document naming its hash was written | The published hash no longer matched the file that would run the confirmation, which by the document's own terms voids it. The edit happened to be inert (at *n* = 16 the exact branch runs and the patch touched only the Monte Carlo branch), but that was luck, established afterwards rather than guaranteed | Freeze by hash *and* by copy: keep the exact bytes alongside the pre-registration. If an edit is unavoidable, invert it to reconstruct the frozen file, verify the hash, run **that**, and publish both outputs |

---

## Replication Checklist for New Model Families (e.g., circlestone-labs/Anima (Cosmos-Predict2-2B + Qwen3 0.6B))

Before generation:
- [ ] Map all parameter tensors of the target model and verify numerical precision (bf16/fp8).
- [ ] Calculate baseline Frobenius norms and document target displacements $D_{\text{model}}$ and $D_{\text{encoder}}$.
- [ ] Construct the **RANDSIGN** control (random signs across identical tensors, $D$ invariant by construction).
- [ ] Construct the **BLOCKSHUFFLE** control via block derangement and apply $\alpha$ strictly to the permuted subset.
- [ ] Define a family of at least 10 subject prompts with identical syntactic structure and orthogonal color dominants.

During measurement:
- [ ] Harvest images by unique basename (no hardcoded relative paths).
- [ ] Verify integrity gates fail loudly if a single tensor key is unaccounted for.
- [ ] Establish the zero-intervention seed floor across all prompts.
- [ ] Perform seed-paired $S$ and $A$ decomposition.
- [ ] Measure across stroke/luminance morphological space, not solely on downsampled CLIP 224×224.
- [ ] Perform PCA and hypothesis testing aggregated at the prompt level ($df = n_{\text{prompt}} - 1$).