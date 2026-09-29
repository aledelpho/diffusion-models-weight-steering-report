# Pitfall 89 — drafted 2026-09-29, not yet inserted in `errors_log.md`

## 89 — a threshold on agreement between two measured things, set without measuring how well each agrees with itself

**What happened.** `prereg_wo_depth.md` called composition supported only if cos(union, sum of
parts) ≥ 0.95. After the renders, the union's own displacement agreed with itself across seeds at
cos **0.13–0.88**, and a slice with itself at **0.06–0.39**. No comparison involving those vectors
could reach 0.95. The criterion was unpassable before a single render existed, and the "not
supported" it returned carries no information about composition.

**The rule.** Before fixing a threshold on the agreement between two measured quantities, obtain the
agreement of each with **its own replicate** under the same conditions — from a pilot, or from
existing data at the nearest dose. A threshold above that ceiling cannot be passed; a threshold far
below it cannot fail. State the ceiling in the pre-registration next to the threshold.

**Whose error.** Mine, as author of the pre-registration. The data to estimate the ceiling existed:
`benchmark_parameter_families` had rendered `Family_wo_d±0.100` at three seeds the day before.
