# Pre-registration C103 — random edits: does each have its own direction, or does the network impose one?

Written 2026-10-19 by Claude, **before any C103 encode or render.** First version (cabe766) replaced the same day, before
anything ran, after Alessandro's objection: *any fixed edit, random or not, should change the pictures the same way across
seeds* ("stiamo rompendo in modi diversi il modello e i risultati non possono che essere coerenti").

## 1. Why

C102 (`docs/te_depth_control_result.md`) compared each edit with **one** random push (seed 9393). A random push, once
drawn, is a fixed change of the function, so it may well change every seed the same way; C102's random push at layer 9
did (blind 0.71). Consistency across seeds therefore does not separate a meaningful edit from a random one. The open
question is another one:

* **(a) own direction** — every fixed perturbation, random or not, changes the pictures consistently, and different
  perturbations change them differently (Alessandro's hypothesis, in its strong form);
* **(b) network's direction** — different random perturbations at the same layer change the pictures *the same way*:
  the network funnels them into one outcome (what C101 suggests for the early layers, where an edit bends like a random
  push).

And: does the answer change with depth?

## 2. Design

* **Prompts and test seeds as C102:** `D1_dwarf_paladin`, `S1_rally`, `C4_stilllife`, `P5_comic_panels`; seeds 2645751,
  3316624, 2718281; file route for every render; sampler as C102.
* **Perturbations (8):** MLP edit ×(1+d) at **L09** and **L26**; three random pushes at each of those layers' MLP output
  (**R09a/b/c**, **R26a/b/c**: per-token random unit directions with seeds 9393, 9394, 9395, scaled by α × the per-token
  norm of the unedited MLP output).
* **Matched on the picture:** one target, DINOv2 distance **D = 0.30** to the same-seed plain render. Strengths from a
  calibration ladder on seed 1618033 (not used in the test): L09 d = 0.5, 0.75, 1.0, 1.25; L26 d = 1.5, 3, 5, 8; R09 α =
  1.5, 2.25, 3, 4; R26 α = 6, 12, 24, 48; interpolation in log strength at the first crossing; a target above the
  ladder is **unreachable** and that perturbation is dropped for that prompt. Calibration: 4 × (1 + 8 × 4) = 132 renders.
* **Test:** per prompt × seed, the plain render and the 8 perturbations: 108 renders (the 12 plain ones are the gate:
  pixel-identical to C102's).
* **Measures (DINOv2-large; Δ = v(X) − v(plain, same prompt and seed)):**
  * **κ (own consistency):** for one perturbation, mean pairwise cosine of Δ over the three seeds;
  * **ρ (cross agreement):** for one layer and one seed, mean pairwise cosine of Δ over the three random pushes;
  * **ε (edit like random):** for one layer and one seed, mean cosine between Δ of the edit and Δ of each random push.
* **Blind (Alessandro).** Two kinds of unit, mixed, conditions hidden, order random (seed 10303), 6 repeats:
  * **A** (32): one perturbation, the three seeds as plain → changed;
  * **B** (24): one layer and one seed, the three random pushes as plain → changed.

  Same question for both: **"Nelle tre coppie l'immagine cambia nello stesso modo?"** — *stesso modo* / *in modi
  diversi* / *non si vede*. Page written before any label.

## 3. Rules (fixed now)

0. **Match check:** a perturbation whose realized median D over its 12 test pictures (3 for one prompt's) is below 0.15
   is **not matched**. If all three random pushes of a layer are not matched, that layer's rules are *not testable*.
1. **Any fixed perturbation changes the seeds the same way (Alessandro), per layer, random pushes only.** Computed: κ ≥
   0.30 in ≥ 75% of prompt × random-push cells. Blind: share of *stesso modo* among A units of random pushes answered
   *stesso* or *diversi* ≥ 0.60 (needs ≥ 6 such units). Both → **supported**; neither → **not supported**; one →
   **disagreement**.
2. **Own direction or the network's, per layer.** Computed: r = median ρ / median κ (random pushes). r ≥ 0.50 → *the
   network imposes the direction*; r ≤ 0.25 → *each perturbation has its own direction*; otherwise *partly*. Blind: share
   of *stesso modo* among B units answered *stesso* or *diversi* (needs ≥ 4): ≥ 0.60 network, ≤ 0.30 own, otherwise
   partly. Agreement or disagreement reported as in rule 1.
3. **Depth:** whether rules 1–2 give different answers at L09 and L26 (reported).
4. **Reported:** κ of the two edits against their layer's random pushes; ε per layer; *non si vede* counts; strengths and
   unreachable targets; blind test–retest.

**Tool rule.** (a) at a layer: every edit is its own knob, and random search over edits is a legitimate way to find
styles. (b) at a layer: edits there all fall into the same outcome, and only the strength matters. Different answers at
L09 and L26: depth decides which kind of knob a layer offers.

## 4. Limits

One calibration seed per prompt; three random directions per layer; DINOv2 directions not validated (hence the blind
co-primary); two layers.

Script: `experiments/te_depth_control2.py`. Directive: `docs/directives_antigravity_te_depth_control2.md`.
