# Pre-registration C104 — random edits: is the content of the change shared and the style the perturbation's own?

Written 2026-10-19 by Claude, **before the new blind pass and before any CSD vector was computed.** Asked by Alessandro
after C103 ("mi stavi facendo le domande sbagliate e possiamo ritararle"). **No new renders**: the 96 test renders of
C103 are reused.

## 1. Why

C103 (`docs/te_depth_control2_result.md`) ended in disagreement: DINOv2 said that different random pushes at the same
layer change the pictures the same way; Alessandro's blind pass said they change them in different ways. The pictures
and his notes suggested a reason: the random pushes share **what** changes (content: realism, age, a vintage kettle) and
differ in **how it is rendered** (colour, photo or painted). One question was asking two things. C104 asks them
separately, by eye and by two embeddings: DINOv2 for content, CSD (a style embedding, already in
`experiments/metric_validation.py`) for style.

## 2. Design

* **Material:** C103's units, unchanged: A (one perturbation, three seeds; 28) and B (one layer, one seed, three random
  pushes; 21), 6 repeats; new random order (seed 10404), new unit names, conditions hidden.
* **Two questions per unit**, same three answers (*stesso modo* / *in modi diversi* / *non si vede*):
  * **Contenuto:** "Il contenuto (soggetti, forme, oggetti, composizione) cambia nello stesso modo nelle tre coppie?"
  * **Stile:** "Lo stile (resa, tecnica, colori, tratto) cambia nello stesso modo nelle tre coppie?"
* **Computed:** κ, ρ, ε as C103, once with DINOv2 (content) and once with CSD-ViT-L (style), on C103's matched
  perturbations (R09a excluded as not matched, as in C103).
* **Known limit, stated now:** Alessandro has seen these pictures in C103 and knows the hypothesis. Conditions stay hidden
  and the order is new, but the pass is not naive. The computed CSD side is untouched by this.

## 3. Rules (fixed now), per layer (9 and 26)

Share s = share of *stesso modo* among answers *stesso* or *diversi* (first showings; needs ≥ 4 B units).

1. **Content is the network's.** Blind: s(content, B) ≥ 0.60. Computed (DINOv2, already known from C103): r_DINO =
   median ρ / median κ ≥ 0.50. Both → **supported**.
2. **Style is the perturbation's own.** Blind: s(style, B) ≤ 0.30. Computed: r_CSD ≤ 0.25. Both → **supported**;
   neither → **not supported**; one → **disagreement**.
3. **Combined reading — "content from the network, rendering from the perturbation":** supported at a layer if rules 1
   and 2 are both supported there.
4. **Reported:** A units (random pushes): s(content) and s(style), and κ with DINOv2 and CSD (Alessandro's hypothesis,
   split); the edits' κ and ε with both embeddings; *non si vede* counts; test–retest; agreement between this pass and
   C103's single question.

**Tool rule.** Supported: at a layer, what changes is set by the network and how it is rendered by the particular
edit; a style tool can pick its rendering by trying edits, while the content shift comes with the layer. Not supported:
random edits differ in content as well, or share their style.

## 4. Limits

Not a naive blind pass (above); three random directions per layer; CSD validated in this project only as a style
distance (C60 onward), not for directions; 21 B units.

Script: `experiments/te_content_style.py`. Directive: `docs/directives_antigravity_te_content_style.md`.
