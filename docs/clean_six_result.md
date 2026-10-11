# C63 — are the six "clean" middle-block edits really free? Result

2026-10-11. Pre-registration `docs/prereg_clean_six.md` (`91075a2`). Renders 109 of 109, check identical to the
pixel to the C60 file (`docs/RENDERS_2026-10-11_clean_six.md`). Key committed before the labels (`d8fa452`),
labels committed as downloaded (`375eb6d`). Tally: `data/clean_six_eye_tally_alessandro.csv`.

## Verdicts, as written

| rule | value | verdict |
|---|---|---|
| **Gate 1** CONTROL edited sides damaged more than their baselines (Fisher, 24 pairs) | 24/24 against 0/24, p = 3e-14 | **pass** |
| **Gate 2** self-agreement on damage ≥ medium, 10 repeats | 1.00 on both sides | **pass** |
| **H** CLEAN, 72 pairs: upper end of Newcombe 95% of (edit − baseline) < 0.10 | 4/72 = 0.056 against 0/72; [−0.005, +0.134] | **undecided** |

The six edits cannot be called free: the interval reaches 13%. Nor do they carry a demonstrated cost: it also
reaches below zero. 72 pairs were not enough to separate a cost of a few percent from none, as the
pre-registration warned.

## Per edit (descriptive)

| edit | damaged pairs (≥ medium) of 12 | mean damage, edit | mean damage, baseline | change (0-2) |
|---|---|---|---|---|
| block 2 whole − | 0 | 0.83 | 1.00 | 1.00 |
| block 8 MLP + | 0 | 0.75 | 0.92 | 1.58 |
| block 8 whole + | 1 | 0.92 | 1.00 | 2.00 |
| block 9 attention + | **3** | 1.25 | 1.00 | 1.33 |
| block 9 whole + | 0 | 0.75 | 1.00 | 1.83 |
| block 18 MLP − | 0 | 0.58 | 1.00 | 0.92 |
| *control:* block 22 MLP + | 12 | 2.00 | 1.00 | 0.92 |
| *control:* block 27 MLP + | 12 | 3.00 | 1.00 | 0.58 |

* Three of the four damaged pairs come from **block 9 attention +**, one from block 8 whole +; the other four
  edits are at 0 of 12 here as they were at 0 of 9 in C60. Looked at at 100%
  (`Text2Img/benchmark_clean_six/sheets/clean_damaged_100.jpg`): on the children's-book face the flat skin turns
  mottled; on the other three the damage is not obvious at that crop.
* **On these prompts the baselines themselves were labelled "slight" almost everywhere** (mean 1.00), unlike
  C60's (0 everywhere at medium and above, and mostly none). Five of the six clean edits were labelled *less*
  damaged than their baselines on average (0.58-0.92): they may smooth what the observer saw as slight grain in
  the originals. Only medium and above counts, so this does not enter the verdict; it is a lead.
* The edits still change the picture a lot (1.0-2.0 on the 0-2 scale), most of all block 8 whole + and block 9
  whole +.

## What this changes

No new claim. Page 29's claim `chosen-middle-edits-are-not-free` stands as it is; C63 is added to its evidence
as a test that could not decide the stronger statement. Practical reading, not a claim: block 2 whole −, block 8
MLP +, block 9 whole + and block 18 MLP − are 0 of 21 pairs damaged across C60 and C63 combined — the strongest
candidates for a comic preset; block 9 attention + is the one to drop.
