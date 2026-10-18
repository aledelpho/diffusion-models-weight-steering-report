# Pre-registration C89 — does an edit's push on the conditioning keep its direction as the dose grows?

Written 2026-10-18 by Claude, **before any computation on these data for this question.** No renders: existing C64
encodes. Proposed by Alessandro (2026-10-18): the edits may cut the model along directions that are not straight
("organised in a spiral"); features organised on circles and helices are known in language models (Engels et al.
2024; Kantamneni and Tegmark 2025).

## 1. Question

If the push grows along one direction as the dose grows, the edit is a straight line in the conditioning; if its
direction turns, the edit follows a curve, and a curve that keeps turning the same way is the "spiral" reading.
C74 found the pictures moving almost straight toward the full-dose picture (10 of 11 strips); this tests the
conditioning, which the pictures do not show.

## 2. Data (fixed now)

The elf (P1), C64 encodes `Text2Img/benchmark_te_conditioning/elf/P1_elfbrawler_L<k>_<attn|mlp>_<p|m><dose>.npz`, for
every half of layers 0–34 with doses 0.10, 0.35 and 1.00 in both signs (70 halves × 2 signs = 140 trajectories). The
push p(d) is `dmean` (mean over tokens of edited minus original conditioning, 12 taps × 2560). Each tap of the push is
divided by the mean token norm of the unedited conditioning at that tap (`P1_elfbrawler_baseline.npz`), so that late
taps, which are larger, do not dominate; the 12 taps are then concatenated.

A trajectory is used only if its push at d = 0.10 is not identically zero (the encodes are stored in float16, so a
very small push can round to zero).

## 3. Measures

* **Bend:** c = cos(p(0.10), p(1.00)). 1 = the full-dose push points where the small one did.
* **Path:** a = angle(p(0.10), p(0.35)) + angle(p(0.35), p(1.00)) against b = angle(p(0.10), p(1.00)). a ≈ b means the
  direction turns steadily in one plane (an arc); a ≫ b means it turns back and forth.
* **Sign symmetry (reported):** cos(p(+0.10), −p(−0.10)); 1 in the linear regime.

## 4. Decision rules

Over the trajectories in use, and separately over the "strong" half (push norm at 1.00 above the median):

1. **Straight:** median c ≥ 0.90 among the strong trajectories.
2. **Curved:** median c ≤ 0.50 among the strong trajectories, **and** in ≥ 2/3 of those with c ≤ 0.50 the path is an
   arc (a ≤ 1.2 b).
3. Otherwise: bent but not consistently (reported as "in between").

Reported: c by layer and by half; the relation (Spearman) between 1 − c and C64's intensity of change seen by eye at
dose 1.00 (`data/te_pilot_eye_alessandro_phase1.csv`), as a lead only.

**Tool rule.** Straight: a dose is a position along one line, and intermediate doses interpolate the full edit (as C74
saw in the pictures); a knob can be calibrated by size alone. Curved arcs: the dose also chooses a direction, so a knob
needs a map of where each dose points; and the "spiral" reading becomes worth a dedicated test with more doses.

## 5. Limits known in advance

Three doses per sign; one prompt; the mean over tokens can hide per-token turns; float16 storage.

Script: `experiments/te_trajectories.py` (written after this file, committed with it).
