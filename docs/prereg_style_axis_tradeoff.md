# Pre-registration — Does an edit push a scene into its own style, or out of it?

- **Written:** 2026-09-25, before the statistic exists. No cosine against a style axis has been
  computed on this corpus by anyone.
- **Corpus:** atlas Phase 1 enlarged, already measured. **No new render.**
- **Relates to:** `docs/prereg_style_capacity.md` and its amendments 01–02, notebook claim
  `cost-grows-with-depth`.

---

## 0. The question, and the distinction it rests on

The observer asked whether moving weights creates a **trade-off**: the model becomes better at
one thing and worse at another because the same mass cannot serve both.

Nothing measured so far can answer that, because every number in
`data/style_capacity_tests.csv` measures how **detectable** an edit is, not how **capable** the
model remains. A systematic defect is easier to recognise than an improvement, so a high
identification recall is as compatible with damage as with skill.

This study measures something different: whether an edit moves a scene **along the direction
that defines that scene's style**, and whether the sign of that movement differs from scene to
scene within one preset.

## 1. Definitions — frozen

Displacement, scale and features exactly as in `docs/prereg_style_capacity_amendment_01.md` §2:
24 live presets, 8 prompts, 3 seeds, the 23 numeric style features, per-feature scale = pooled
within-(preset, prompt) standard deviation of Δ across seeds. `modulation_norm` stays excluded
under amendment 02.

**Style axis of scene s**, in the same scaled space:

    u_s = z(baseline of s) − mean over the eight scenes of z(baseline)

That is: what makes pixel art pixel art relative to the average of the eight renderings.

**Matched projection:** c(p, s) = cos( Δ(p, s), u_s ).
Positive = the edit pushes that scene **further into** its own style. Negative = **out of it**,
toward the average render.

## 2. The artefact that would fake the result, and the control that removes it

Δ(p, s) is anchored on the baseline of s, and u_s is **built from that same baseline**. The
estimation noise of the baseline therefore enters both with opposite signs, which biases the
matched cosine **downward** — a mechanical push toward "every edit leaves its own style" that
has nothing to do with the edit.

**Primary is therefore the split-seed version.** With three seeds, for each choice of one seed
*a*:

- u_s is estimated from seed *a* alone;
- Δ(p, s) is averaged over the other two seeds;

and the three choices are averaged. Axis and displacement then share no image.

The naive version, axis and displacement from all three seeds, is reported as a **cross-check**.
If the two disagree in sign, the study is inconclusive.

## 3. The null — exact, by enumeration

Under the null the pairing between a scene and its axis carries no information. Permute the
eight axes among the eight scenes and recompute. **All 8! = 40 320 permutations are enumerated**,
the identity included as the observed value, giving an exact floor of 1/40 320 = 2.48e-05.

Two statistics, both judged against this null:

- **M** — the mean of c(p, s) over the 24 × 8 cells. Two-sided: the claim predicts no sign.
- **T** — the mean over presets of min(k, 8 − k), where k is the number of scenes with
  c(p, s) > 0. T = 0 when an edit does the same thing to every scene; T = 4 when it is maximally
  split. This is the trade-off statistic proper.

## 4. Decision rules — frozen before the first cosine

1. **No signal** if M is inside the null and T is inside the null. The edit's direction has no
   relation to the style of the scene it acts on, the trade-off question is answered *no*, and
   the localisation study the observer asked about does not proceed.
2. **Contractive, not selective** if M < 0 outside the null. Wording fixed now: *every edit makes
   every scene less like itself and more like the average render.* This is a uniform cost, not a
   trade-off, and it would extend `cost-grows-with-depth` from texture to style.
3. **Trade-off** if T is outside the null, whatever M does. Wording fixed now: *the same edit
   pushes some scenes further into their style and others out of theirs.* Only this outcome
   supports the observer's hypothesis.
4. **Selective gain** if M > 0 outside the null. This would say edits sharpen the style already
   present. It is the least expected outcome and **no claim is published on it without a
   replication on a corpus not used here.**

Reported alongside, as description only: the mean matched cosine **per scene** (which styles
gain, which lose) and k per preset.

## 5. What would kill this study

- The eight scenes share one subject, a rally car. u_s mixes "style" with anything else that
  distinguishes that render from the average, and nothing here separates the two.
- Three seeds. The split-seed control costs a third of the data for the axis and two thirds for
  the displacement; the axis rests on a single image per scene per fold.
- The scaled space is the 23 style features. A trade-off invisible to those features is invisible
  here, and a claim of absence carries that limit.
- `modulation_norm` is excluded as inert; if the patch-count run of
  `docs/prereg_style_capacity_amendment_02.md` §4 ever shows other regions partly inert, the
  displacement of every preset here is partly nominal.

## 6. Outputs

- `data/style_axis_projection.csv` — one row per (preset, scene): matched cosine, split-seed and
  naive, and the sign.
- `data/style_axis_tests.csv` — M, T, their exact p-values, the per-scene means, and the verdict
  from §4.
