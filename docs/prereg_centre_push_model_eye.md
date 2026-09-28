# Amendment — the model-eye veto of `benchmark_centre_push`

**Deposited 2026-09-28, before any crop was judged and before any answer was read.**

## 0. Why this document exists, and what it is not

`docs/prereg_centre_push.md` §6 names **Alessandro** as the observer of G_eye. That veto is built
(`experiments/centre_push_eye_veto.py --build`) and still owed; **nothing here replaces it or
counts toward its 8-of-12 threshold.**

Alessandro asked, in addition, for the analyst's own eye on the same crops. The analyst cannot
supply a blind one: while reporting the build, **the analyst printed ΔL and the side L calls more
broken for all twelve pairs**. Its judgement on this set is contaminated and is worth nothing as a
test. So the request is split in two, and the two are never added together:

- **M1 — the blind model eye.** Three observers who have never seen the key, the units table, the
  measurements or this repository judge the twelve pairs from the images alone.
- **M2 — the sighted forensic reading.** The analyst, knowing the key, describes at 1:1 what
  actually differs in each pair. This is **not a test**: it is an audit of what `L` is measuring,
  and it can only ever produce hypotheses, never a verdict.

## 1. M1 — procedure, fixed now

1. Three independent observers, each a fresh agent with **no access to this repository**, to
   `data/centre_push_veto_key.csv`, to `data/centre_push_units.csv`, or to any part of the
   conversation in which the key was printed. Each sees only the twelve pair sheets and their
   1:1 zoom tiles, and the two unperturbed baseline crops.
2. Each observer answers, per pair, exactly one of **A**, **B**, **neither** to the same question
   put to Alessandro: on which side is the **drawing** more broken — the line, the stroke, the
   structure — not which is further from a prompt they cannot read, not which they prefer.
3. **The vote is the majority of the three.** Two or three agreeing fixes the answer; three
   different answers, or a majority for **neither**, is recorded as **neither** and excluded as a
   tie, exactly as the parent pre-registration excludes ties.
4. Scoring is `experiments/centre_push_eye_veto.py --score` against the sealed key, unchanged, plus
   an exact two-sided sign test on the judged pairs.

## 2. What M1 can and cannot conclude

M1 **cannot** satisfy G_eye. Three instances of the same model family are not three observers:
their errors are correlated by construction, so the sign test on their majority is anticonservative
by an unknown amount and is reported as descriptive. And the whole point of G_eye is a *human*
check on a statistic, because the statistic and the model share the same blind spots.

M1 **can** do one useful thing: if a blind observer, with no numbers at all, cannot recover the
ordering of `L` above chance, then `L` is ordering something not visible in the picture — which is
the failure mode G_eye exists to catch. A pass tells us much less than a failure does.

## 3. Predictions — deposited now

- **Analyst:** M1 agrees with `L` in **7 of 12** pairs. Reasoning: 8 of the 12 pairs are
  cross-prompt, and two (01 and 07) are numerical ties for `L` at ΔL < 0.012; a blind observer
  should be near chance on those ten and right on the two large-ΔL pairs.
- **Analyst:** the observers will disagree with each other on **at least 4** of the 12 pairs.
- **Analyst:** M2 will find that where `L` is large and negative, the visible difference is
  **grain**, not line — the confusion already logged against `L` in `STORY.md` §VII.

## 4. Stopping rule

M1 runs once. Three observers, one pass each, no re-reads, no fourth observer if the vote is
uncomfortable. The answers are written to `data/centre_push_model_eye_answers.csv` before the key
is opened against them.

---

## 5. M1b — the mirror control, deposited before it runs

**Added 2026-09-28, after seeing the M1 answers and before cutting a single mirrored sheet.**
This is a **post-hoc control**, not a second attempt at the primary, and it is labelled as such.

M1 resolved only 5 of 12 pairs, and **all five answers were `B`, the right-hand image**. Under a
coin flip that is p = 0.0625 two-sided. Side was assigned at random, so a right-hand preference and
a real perception of damage produce the same table here, and the two cannot be separated by any
amount of re-reading of the same sheets.

So the same twelve pairs are cut again with **the two halves swapped**, and three fresh observers,
who have seen nothing of this, judge them with the identical instruction.

**Interpretation, fixed now:**

- The mirrored majority names the **same image** (its answer flips side on the pairs M1 resolved):
  position bias is ruled out and M1's five answers stand as observations.
- The mirrored majority names the **same side** (`B` again): M1 is a position artefact. Its answers
  are **discarded in full**, and nothing in this amendment is reported as an observation about the
  drawings.
- Anything in between: M1 is reported as **not interpretable**, and neither table is used.

The scoring against `L` is not repeated or pooled. M1b decides only whether M1 exists.
