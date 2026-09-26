# Amendment 02 to `docs/prereg_capability_judge.md` — the judge is good and the question was wrong

- **Written:** 2026-09-26, after the run. It **withdraws the question**, not the judge, and specifies
  the replacement before any new call is made.

---

## 1. What the run produced

`qwen3.8:27b`, 128 gate calls and 920 measurement calls, all logged with model, backend, url and
timestamp.

**The gate passed, and well.** Recomputed independently from `data/capability_judge_gate.csv`:

| | |
|---|---|
| scenes where it said yes to its own style and **no to all 7 others** | **7 of 8** (gate needs 6) |
| rejections of other styles | **7/7 on every one of the eight scenes** |
| polarity agreement | **0.016** (unusable above 0.20) |
| unparsable answers | **0 of 128** |

The single miss is `S6_pixel`: it answered no to "is this 8-bit pixel art?" about the pixel-art
baseline, while still rejecting all seven other styles. It does not confuse pixel art with anything;
it does not recognise that phrase. That is a vocabulary gap, not a discrimination failure.

**Then the study failed its own guard.** `data/capability_judge_tests.csv`:

    verdict: judge_unusable — Q1 yes-share 0.960, Q2 yes-share 1.000, both outside [0.05, 0.95]
    Q1 test-retest 1.000 (n=30)   Q2 test-retest 1.000 (n=30)
    Q1 polarity discarded 0.135   Q2 polarity discarded 0.000

Test-retest **1.000 on both questions**: at temperature 0 the judge is perfectly deterministic, so
its noise is zero and every answer below is a reproducible fact, not a fluke.

## 2. Why a passing gate did not license the questions

Amendment 01 §2 states it: *"a gate is only informative about the task it was run on."* It was written
about the September failure; it has now cut the other way.

The gate asks **which of eight very different styles this is** — a between-category discrimination.
The capability questions ask **whether an edit degraded this style** — a within-category threshold
judgement. The judge has resolution for the first and almost none for the second, and no amount of
skill at the first predicts the second.

## 3. What survives, as description

**The positive control of §4 fires.** On the style question, consistent items only:

| | yes |
|---|---|
| the 8 baselines | **7 of 7** |
| `early_attn_draw2`, the preset the observer called visibly broken | **4 of 7** |

So the judge does separate a visibly broken preset from the baseline. Its resolution is not zero; it
is just far too coarse for a 0–1 scale over 192 cells.

**And the seven rejections are not spread at random.** Across all 173 usable items on Q1 the judge
said no exactly seven times:

| preset | scenes |
|---|---|
| `early_attn_d2` | S1_photo, S2_watercolor, S5_ukiyoe |
| `late_mlp_d2` | S1_photo |
| `early_mid_attn_d2` | S1_photo |
| `late_mid_mlp_d2` | S6_pixel |
| `uniform_all_d1` | S6_pixel |

**Four of the seven fall on `early_attn_d2` and `late_mlp_d2`** — the two presets the observer
singled out by eye before any number existed, and the same two that the feature measurement put at
the extremes of the structure/grain axis. Three instruments that share nothing — a human eye, 23
texture features, and a vision-language model — converge on the same two objects. That convergence
is the most defensible thing this run produced, and it is descriptive: seven events are seven events.

## 4. What is dead

**Q2 is dead.** 200 of 200 yes, zero no, including on the very images where the judge had just said
the style was broken. It has no resolution on this question, so *"no preset destroys the subject"*
is **not** a finding — the correct statement is that the subject question cannot be asked this way.
Q2 is withdrawn.

## 5. The replacement, specified now

The failure is in the **form** of the question, not in the judge, and `experiments/vlm_gate.py`'s
header prescribed the right form a year of commits ago, which amendment 01 adopted for the gate and
then did not carry into the measurement:

> **forced choice at matched prompt and seed, both orders, never an absolute rating.**

So: for each (preset, scene) cell, show **the baseline and the preset side by side**, same prompt,
same seed, and ask which of the two is more clearly in the declared style. Both orders, A-B and
B-A, so position bias is measured rather than assumed absent. An absolute threshold is never
requested, so the ceiling cannot arise.

    192 cells × 2 orders = 384 calls — fewer than the 920 just spent.

Chance is 50 %. The frozen reading: a cell counts as *degraded* only when both orders agree that the
baseline is the more clearly styled image. Disagreement between orders is the position-bias measure
and those cells are discarded and counted, exactly as the polarity control worked here.

## 6. The process lesson, and it cost 920 calls

The yes-share guard ran in the **analysis**, after every call had been made. It would have shown the
ceiling from **32 calls** — Q1 and Q2, both polarities, on the eight baselines plus
`early_attn_draw2`.

**Rule added:** every judge study runs its distributional guards on a small pre-flight subset before
the full sweep, not only in the post-hoc analysis. A guard that can only fire after the budget is
spent is a report, not a guard.
