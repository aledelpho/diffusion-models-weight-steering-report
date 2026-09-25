# Amendment 03 to `docs/prereg_family_coherence.md` — the run confound is withdrawn

- **Written:** 2026-09-25, after amendment 02.
- **Nature:** this amendment withdraws an **objection**, not a result. Amendment 02 refused to
  treat the cross-domain observation as usable because family C is one render run and every
  other family is another. That objection rested on an assumption that the project's own data
  contradict.

---

## 1. The evidence that the render run is inert

Three records, none of them produced for this study:

1. `data/bench_checks.csv`, row `determinism_across_sessions`: P01 seed 42, benchmark
   `determinismo` against benchmark `mappa`, **across a ComfyUI restart**, max channel
   difference **0** on a 0–255 scale. Verdict PASS. The note on that row already states that
   every measurement pairing those two benches rests on it.
2. `data/perturbation_atlas_draw_check.csv`, gate `gate_environment_determinism`: **S1
   baseline seed 42**, a render belonging to the stage9 run of 2026-09-18, re-rendered on
   2026-09-25 and compared in raw RGB. **Max pixel difference 0, byte-for-byte match**,
   SHA256 `9cc570d778582db3abaf938b1634091bceee58be6e94833cd564a38c317f294f`. Seven days and
   an unknown number of restarts apart.
3. Generation parameters are identical in all eight manifests: `euler_ancestral`, 9 steps,
   cfg 1.0, 1024×1280. Families **B and C additionally share the same harness version**
   (`suite_git_sha = ba28b12532175220`); A1 and A2 carry `ff680ad0a33ee142`.

## 2. What follows, and what does not

**Follows.** "Different render run" does not by itself put any difference into the pixels.
A cosine that falls from +0.42 (B against A1) to +0.077 (B against C) cannot be attributed to
the calendar when the same prompt, seed and condition reproduce byte-for-byte across a week.
The objection raised in amendment 02 §3 and §5 is therefore withdrawn for the **B versus C**
contrast, where the harness version is also identical.

**Does not follow.** Nothing here revives the verdict withdrawn in amendment 02. The family
partition is still misspecified, within-family still equals between-family among A1, A2 and B,
and the restricted gap still favours the random control. Amendment 02 stands in full.

**Does not follow either.** Determinism proves that a repetition reproduces. It does not prove
that two runs used identical weights on disk; it makes the contrary implausible, not
impossible. A1/A2 carry a different `suite_git_sha` from B/C, so any contrast that crosses
that boundary keeps the caveat.

## 3. Consequence

The cross-domain observation released as description in amendment 02 §5 — preset cosine ≈ 0.02
against the random control's ≈ 0.19 across the comics/stage9 boundary — becomes a question that
existing data can answer. It is not answered here. It is pre-registered separately, restricted
to B and C so that the harness version is held constant, in
`docs/prereg_domain_specificity.md`, which states in its own first section that the pattern was
seen before the test was written.
