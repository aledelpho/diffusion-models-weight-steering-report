# Observer predictions on the atlas, recorded before the numbers existed

- **Recorded:** 2026-09-25, 21:0x UTC.
- **State of the data at the moment of writing:** feature extraction was at **326 of 649
  images**. `data/style_capacity_tests.csv` did not exist. No distance, no K, no tau, no
  identification accuracy had been computed by anyone.
- **What the observer had seen:** only the renders of the **first prompt family**, `S1_photo`.
  Seven of the eight prompts were unseen by him at the time of writing.

This document exists because the observer's eye is the only instrument in this project that can
say whether a measured difference is a *style*. Written down after the numbers it would be
worthless; written down before, it becomes a variable that can be scored.

---

## 1. The six statements, verbatim

| id | preset | seed | statement (as given, in Italian) |
|----|--------|------|----------------------------------|
| **A** | `early_attn_draw2` | 42 | "Questo preset è visibilmente rotto." |
| **B** | `late_mlp_draw2` | 42 | "Questo preset sembra rotto, in un modo diverso dal precedente" |
| **C** | `model_only_draw2` | 42 | "Questo preset sembra avere i contrasti e la saturazione più elevati (ma sembra anche un po' bruciata)" |
| **D** | `late_attn_draw1` | 777 | "Questo preset presenta una grana visibile, c'è qualcosa che è spinto un po' troppo. Sembra rosso più nel modo di B." |
| **E** | `txtfusion_draw2` | 42 | "Questo preset sembra avere una predilezione per lo sfondo (riduce il soggetto)" |
| **F** | `uniform_all_draw2` | 1337 | "Questo preset sembra bruciare leggermente la messa a fuoco, mettendo una filigrana granulosa sullo sfocato." |

All six on `S1_photo`.

## 2. Operationalisation, fixed here and not negotiable afterwards

**The damage gate.** A preset is *out of range* on a prompt when `edge_density` or
`lbp_entropy` lies more than 3σ from that prompt's baseline, σ being the seed-to-seed spread of
the baseline on that prompt. With three baseline seeds σ carries 2 degrees of freedom: this gate
is blunt, and that is stated now rather than discovered later.

| id | prediction, in the measured space | testable with the 23 style features? |
|----|-----------------------------------|--------------------------------------|
| **A** | `early_attn_draw2` is out of range on S1, and its ‖Δ‖ is in the upper half of the 26 | yes |
| **B** | `late_mlp_draw2` is out of range on S1, **and** cos(Δ_A, Δ_B) is below the median of all 325 pairs — "broken in a different way" is a claim about direction, not about amount | yes |
| **C** | `model_only_draw2` on S1: `colorfulness_hs` **and** `glcm_contrast` both above the baseline, and its `colorfulness_hs` is in the top 5 of the 26 | yes |
| **D** | `late_attn_draw1` on S1: `fft_high_freq_share` above baseline and in the top 8 of the 26; **and** cos(Δ_D, Δ_B) > cos(Δ_D, Δ_A) — the "more like B than like A" claim | yes |
| **E** | `txtfusion_draw2` on S1 reduces the subject's share of the frame against the baseline | **no** — needs `experiments/measure_body_area.py`, a separate instrument |
| **F** | `uniform_all_draw2` on S1 raises high-frequency energy **in the low-detail regions specifically**, not globally | **no** — needs a regional frequency measure that does not exist yet |

A, B, C and D are scored against the features being extracted now. E and F are recorded as
predictions that this corpus cannot yet test; whoever builds those two instruments must not read
this file first.

## 3. The scoring rule, frozen

Each of A, B, C, D scores **hit** or **miss** on its stated criterion, with no partial credit
and no rewording. Four predictions, chance of a hit around one half each if the observer were
guessing, so the whole set is a small sample and is reported as such: the number is 0 to 4 and
carries no p-value worth printing.

**The part that does carry weight** is the second question, and it is free:

> Do A–D hold on the **seven prompts the observer never saw**?

Each prediction is re-scored on `S2_watercolor` … `S8_charcoal`. A claim made from one
photographic scene that survives ukiyo-e, pixel art and charcoal is evidence that the observer
is reading a property of the **preset**, not of one picture. A claim that holds only on S1 is
evidence that he is reading the picture.

Reported as two counts: hits on S1 (out of 4) and hits per unseen prompt (out of 4 × 7 = 28).
No threshold is set for "the observer is reliable": with four predictions there is no honest
threshold, and inventing one now would be worse than reporting the raw counts.

## 4. Why this is worth the trouble

`docs/errors_log.md` entry 34 records that in a four-way forced choice this observer identified
`preset_pos` ×2 in 17 trials of 20 and `blockshuf_neg` ×2 in 12 of 20, with the images mirrored,
flipped, hue-rotated, re-saturated, re-brightened and noised. His eye is a measured instrument
with a known, good score — at double amplitude, on a lineup that contained the baseline.

This is the first time it is being used **predictively**, on named presets, at single amplitude,
before the measurement. Whatever comes out is on the record.

---

## 5. Addendum, same session, extraction at 436 of 649, still no statistic computed

**Prediction G — the observer.** *"Ah, e ci sono due preset uguali, direi. A occhio."*

The pair was **not named** at the time of writing. As it stands the claim is only that **K < 26**,
which is weak. It becomes a sharp prediction the moment a pair is named, and a named pair will be
scored on one criterion, fixed here: that pair is **not distinguishable** in the consensus graph
of `docs/prereg_style_capacity_amendment_01.md` §3, i.e. it is joined by an edge and falls inside
one component.

Procedure, to keep the test alive: no pair-level number from this corpus is shown to the observer
until he names the pair. The naming is timestamped in this file when it happens.

**Prediction H — the analyst, sealed at the same moment and for the same scoring.** My own guess,
written before any distance exists and before the observer names his pair, so that it is
falsifiable on the same terms: the collapsing pair is **`model_only` and `uniform_all`**.

Reasoning, recorded so the guess cannot be re-explained afterwards: the two conditions differ
only in whether the CLIP tensors are included — 430 model tensors against 430 + 629. And the CLIP
side of `Arthemy_Bench_Base.json` carries only **6 distinct values** across its 629 tensors, with
343 of them at −0.025, against 345 distinct values on the model side. A block of near-constant
multipliers on the text encoder is the part of the payload most likely to contribute little to
the rendered image, in which case adding it changes the picture hardly at all.

If H is right, it is also a finding about the instrument and not only about two presets: it would
say the CLIP half of every preset in this project is close to inert, which bears on
`cliplult-is-a-dead-arm` and on how the tuner's payload should be described.
