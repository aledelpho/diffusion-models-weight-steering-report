# MOSS-S2 result — the turbo at 10 steps with euler follows the reference; 25 steps does not

2026-10-25. Pre-registration `docs/prereg_moss_settings2.md`; renders and numbers by Antigravity
(`docs/RENDERS_2026-10-25_moss_settings2.md`, baaad7f): 72 of 72. Times per picture: T10 24 s, T10A 25 s, E25 86 s,
R50 178 s.

| rule | value | verdict |
|---|---|---|
| power | R50 median edit distance 0.046 (≥ 0.03) | informative |
| S2 E25 | Spearman 0.57, ratio 1.20 | **FAIL** |
| **S2 T10** (DMD2 LoRA, euler, 10 steps, CFG 1) | Spearman **0.86**, ratio 1.18 | **PASS** |
| S2 T10A (same, euler_ancestral) | Spearman 0.67, ratio 1.02 | FAIL |

**Decision, as pre-registered:** T10 is the working setting for MOSS; confirmations run on **R50** (E25 failed).

Read after the rules: the turbo ranks edits like the reference better than 25 steps does, plausibly because 25 steps
leave the 50-step trajectory unfinished while the distilled model is trained to reach the end in few steps. T10 is
weaker than R50 on the text-encoder edit of layer 6 on the dwarf (0.022 and 0.040 against 0.035 and 0.077); one seed,
two prompts, four edits: the confirmations stay necessary.
