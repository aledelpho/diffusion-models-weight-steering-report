# C89 result — does an edit's push keep its direction as the dose grows?

2026-10-18. Pre-registration `docs/prereg_te_trajectories.md`; script `experiments/te_trajectories.py` (committed in
86a205d before the run; afterwards two bugs that stopped the script were fixed — the render-root path on the Linux
mount and a dictionary key swallowed by a comment — with the selftest re-run; the measures are unchanged).
Outputs `data/te_trajectories.csv`, `data/te_trajectories_tests.csv`. No renders: C64 encodes of the elf, 70 layer
halves × 2 signs at doses 0.10, 0.35, 1.00; all 140 trajectories usable.

## Verdict

| measure | value | rule | verdict |
|---|---|---|---|
| median bend c = cos(p(0.10), p(1.00)), strong half | **0.665** (70 trajectories; all 140: 0.835) | ≥ 0.90 straight; ≤ 0.50 + arcs curved | **in between** |
| arcs among strong trajectories with c ≤ 0.50 | 2 of 20 | ≥ 2/3 for "curved, in arcs" | not arcs |

* **Small doses are linear.** At 0.10 the push of +d and −d are opposite: cos(p(+0.10), −p(−0.10)) median 0.977.
* **Large doses turn.** From 0.10 to 1.00 the direction of the strong pushes turns by about 50° on the median, and up
  to 90° or more. MLP doubled turns most (median c 0.548), attention zeroed least (0.965).
* **Not a steady arc.** Where the turn is large, the intermediate dose is off the shortest path (path 1.2–1.5 times
  the direct angle): the direction does not rotate smoothly in one plane. With three doses this cannot tell a spiral
  from any other non-linear path; it says only that the path is not a clean arc.
* **The edits that change the character bend.** L06 MLP doubled: c 0.46; L14: 0.48; L05: 0.50; L28, the edit that keeps
  the character: 0.71. The most bent trajectories sit in layers 0–3.
* **Lead (reported, not tested):** across all 138 halves with an eye label, the bend correlates with C64's intensity
  of change seen at dose 1.00, Spearman +0.57.

## Reading

An edit is a straight line only at small doses. At full dose the push points in a direction partly different from
where it started: part of what a doubled MLP does is not "more of the small edit". This fits C74, where nothing
changes style below 0.70 and L06 then jumps: the full-dose effect may be a different direction, not a larger step.
For a tool: a knob calibrated at small doses does not extrapolate to large ones. The "spiral" reading needs more
doses (C74's twelve) and per-token pushes to be tested; that needs new encodes on the GPU, no renders.

## Limits

One prompt; three doses per sign; the mean over tokens; float16 storage; the eye intensity is one labeller's.
