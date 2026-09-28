# Render spec — the achromatic leaf, and the `blk16` ladder

- **For:** Alessandro, who launches every render. **The analyst generates none.**
- **Two independent benches, two different drive mechanisms.** They must not be mixed; §4 says why.
- **214 renders total**: 142 + 72. Either can be queued alone.

---

# Bench 1 — `benchmark_leaf_collapse`, 142 renders

## 1. What is being chased

One cell in 108 kept its object and lost 96 % of its colour: `LN_Block_4neg_0.200`, seed 1337
(`colour_gate_and_chroma_audit.md` §3–4). It replicates on neither of its two sibling seeds
(×1.652 on 42, ×0.898 on 777) and seed 1337 is not fragile in general (mean chroma ratio 1.135
against 1.308 and 1.195). With n = 1, a seed × condition interaction cannot be told from a one-off.

Alessandro's two questions, plus the control that can kill both:

| arm | question | renders |
|---|---|--:|
| **A — seeds** | does it come back on 20 fresh seeds, same prompt, same preset? | 40 |
| **B — wording** | does it come back on five other ways of asking for the same thing? | 30 |
| **C — subject** | does it come back on four other subjects with a strong colour prior? | 72 |

Every perturbed cell has its own unperturbed baseline at the same prompt and seed, because the
statistic is a ratio to that baseline. **Arm A's 20 baselines are the killer control**: an
unperturbed render that collapses means the edit is not the cause and the whole thing is noise in
the sampler.

## 2. The design

**Drive, for every perturbed row:** tuner named input **`Block_4 = -0.2`**, every other named
input 0.0, **`vectors_override` empty, `granular_json` empty**, mode `Real Value`. Baseline rows
bypass the tuner entirely. Settings as every bench: `euler_ancestral`, `simple`, 9 steps, CFG 1.0,
1024 × 1280.

**Arm A** — the exact original prompt, `LN`:
> *a single leaf centred on a plain light grey background, macro photograph, sharp focus, even
> studio lighting, no other objects*

Seeds **2001–2020**, fresh, chosen before any of them was rendered.

**Arm B** — same subject, still no colour declared, five other wordings (`W1`–`W5`); `W5` changes
only the background from light grey to white. Seeds 42, 777, 1337.

**Arm C** — four subjects with a strong colour prior, each in three colour conditions, same
sentence frame as the leaf. The unusual colour is held at **purple** for all four — the same
unusual colour the original experiment used, so it is not a new free variable.

| code | subject | prototypical | unusual | undeclared |
|---|---|---|---|---|
| `MU` | mushroom | brown | purple | — |
| `TO` | tomato | red | purple | — |
| `PC` | pinecone | brown | purple | — |
| `BA` | banana | yellow | purple | — |

Seeds 42, 777, 1337.

## 3. Predictions, frozen before the renders

**A hit is:** chroma ratio **< 0.20** against its own baseline **and** IoU **≥ 0.70** with it, on
the low-passed value foreground of `experiments/colour_chroma_audit.py`. The threshold is wide on
purpose: the event measured 0.040 and the next lowest of 108 cells was 0.648, so nothing sits near
0.20. The corpus rate so far is **1/108 = 0.93 %**.

| # | arm | confirmed if | falsified if |
|---|---|---|---|
| **L1** | A, perturbed | **≥ 2 of 20** hits — reproducible mode (binomial against 0.93 %, p = 0.014) | **0 of 20** — a one-off |
| **L2** | A, baselines | **0 of 20** hits | **≥ 1** — the edit is not the cause and L1 means nothing |
| **L3** | B | hits on **≥ 2 of the 5** wordings — preset-driven | hits on none — wording-specific |
| **L4** | C | hits on **≥ 2 of the 4** new subjects — subject-general | hits on none — leaf-specific |
| **L5** | C | mean hue shift ordered **prototypical < unusual < undeclared** in **≥ 3 of 4** subjects | the order fails in ≥ 3 of 4 |

**L2 is read first.** If any unperturbed baseline collapses, stop: L1, L3 and L4 are unreadable and
the finding was sampler noise all along.

**L5 is the second object `C15` asked for** — the `LG` < `LP` < `LN` ordering, currently resting on
one object and p = 0.039 on one of two arms. It is obtained here for free, but on a single block,
so it is a partial answer and will be reported as one.

Plan: `data/leaf_collapse_plan.csv`, built by `experiments/make_leaf_collapse_plan.py`.
**142 rows**, 71 perturbed and 71 baseline. Folder `benchmark_leaf_collapse\renders`.

---

# Bench 2 — `benchmark_blk16_ladder`, 72 renders

## 4. Why `blk16`, and why the drive is different here

`style_damage_frontier.md` §9: `blk16 pos` is the single block that moves style most while
**raising** the orientation of the drawing — style 0.447, structure coherence ×1.040, 6/6 cells
above 1 — against a corpus in which the five conditions this project had previously recommended
are its five largest losses of drawn line. It sits inside `Block_4`, the family Alessandro
identified by eye before any statistic did. It replaces `blk27` as the single-block candidate.

**`benchmark_profondita` drove single blocks with a 34-slot `vectors_override` in `Real Value`
mode, every named group input at 0.0.** Bench 1 above drives a *named group input* with
`vectors_override` empty, because that is what the colour sweep did. Both are correct for their own
bench and **a row from one must never be run with the other's mechanism** — the comparison to the
existing corpus is what makes either bench worth rendering.

## 5. The design

Slot **16** at ±dose, the other 33 slots `0.000`. Doses **0.020, 0.035, 0.050, 0.080, 0.120,
0.200**, both arms, prompts `P01` and `P02`, seeds 42, 777, 1337. Baselines already exist in
`benchmark_mappa` — **do not re-render them**. Prompt text is carried from the baseline renders'
own metadata so it cannot drift.

## 6. Predictions, frozen

Measured with `experiments/style_damage_frontier.py` and `experiments/texture_anisotropy.py`
against the `benchmark_mappa` baselines.

| # | prediction | confirmed if | falsified if |
|---|---|---|---|
| **K1** | coherence stays at or above baseline across the whole positive ladder | ratio ≥ 0.98 at **every** positive dose | < 0.95 at any dose ≤ 0.120 |
| **K2** | style grows monotonically with dose on the positive arm | 6 doses in rank order | any inversion greater than 0.03 |
| **K3** | `blk16 pos` at 0.200 reproduces its measured point | style 0.447 ± 0.08, coherence 1.040 ± 0.03 | outside those bands |
| **K4** | the negative arm behaves like the rest of the corpus: style bought by losing line | coherence < 0.98 at 0.200 | ≥ 1.00 |

**K3 is the one that matters**, because the 0.200 cell already exists in `benchmark_profondita`
and is being re-rendered here from a different plan file: it is a determinism and provenance check
on the whole pipeline, not just on `blk16`. If K3 fails, nothing else in this bench is readable.

Plan: `data/blk16_ladder_plan.csv`, built by `experiments/make_blk16_ladder_plan.py`. **72 rows.**
Folder `benchmark_blk16_ladder\renders`.

---

## 7. Standing constraints

- The analyst generates no render and requests none beyond this document.
- Nothing written under `notebook/`. No claim status changes.
- Validator at 0 errors before every commit; commit messages in Italian; repository content in
  English; **do not push**.
- **Nothing in this project may shut down or close the machine.**
