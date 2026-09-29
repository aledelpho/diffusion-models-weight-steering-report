# Pitfall 90 — drafted 2026-09-29, not yet inserted in `errors_log.md`

## 90 — a recommendation about what an image looks like, made without opening the image

**What happened.** `centre_push_result.md` §4 (2026-09-28) recommended `Block_4 pos` and `Block_1 pos`
at dose 0.500 as the project's best operating points — "more movement *and* a stronger line" — from
two statistics, `V` (distance from baseline) and `L` (structure coherence). A render-bench (`C37`)
was registered to push them further. Opened a day later, at Alessandro's prompting: both are
destroyed, one into crumpled strokes, one into colour confetti, and `Block_4 pos` is already broken
at 0.350. Alessandro had been saying the images were breaking; the analyst had been answering with
numbers.

**Why the numbers said the opposite.** `V` measures *how far*, not *what*: a ruined image is far from
its baseline, so destruction scores as a large effect. `L` rewards regular oriented texture, which is
what both collapses are made of. Two blind statistics agreed with each other and with nothing in the
picture.

**The rule.**
1. **No sentence about how a render looks — holds, breaks, keeps the line, is cleaner — without the
   analyst having opened that render**, at the dose the sentence is about, and named it in the text.
2. **No operating recommendation from a statistic alone.** A dose, a preset, an arm is recommended
   only after its renders have been looked at, by Alessandro or by the analyst, at 1:1 where grain
   matters.
3. When the eye and a statistic disagree, **the statistic is the suspect** until shown otherwise —
   this project's statistics have been wrong about images (defects 77, 78, 84, 85, the eye veto,
   this one) far more often than its observer has.

**Whose error.** The analyst's. Pitfall 78 (judge at 1:1) and the eye veto's result (`L` inverts on
named units) were both already on record when §4 was written.
