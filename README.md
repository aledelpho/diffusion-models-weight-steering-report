# Weight-Space Steering in Diffusion Models: A Public Lab Notebook

<!-- CLAIMS:BEGIN -->

| | What | What it rests on |
|---|---|---|
| **Holds** | [One of the text-encoder arms is exactly inert: it changes nothing at any dose, while a sibling arm in the same run changes the image at every dose.](notebook/00-the-bench.md#four-arms-that-do-nothing-and-one-that-proves-the-test-works) | RMS difference exactly 0.0 at five doses; the sibling arm runs 23.5 to 34.0. |
| **Holds** | [The pipeline reproduces a render exactly across a restart, so measurements taken weeks apart can be compared to each other.](notebook/00-the-bench.md#the-same-render-twice-weeks-apart) | Maximum channel difference 0, P01 at seed 42, across a ComfyUI restart. |
| **Holds** | [With the tuner in the graph and every gain at zero, the render is bit-for-bit identical to the render with no tuner at all.](notebook/00-the-bench.md#the-node-adds-nothing-of-its-own) | Maximum channel difference 0 across 15 cells on 3 prompts. |
| **Holds** | [The seed-to-seed noise floor of fine texture is under 2% on the two prompts that every threshold in this notebook is calibrated against.](notebook/00-the-bench.md#the-floor-that-moved-twice-before-it-was-measured) | 1.65% on P01 and 1.84% on P02, measured across 18 baseline seeds each. |
| **Holds** | [An edit and its exact inverse put the weights back where they were and do not put the image back, which sets a floor stricter than the seed floor.](notebook/00-the-bench.md#the-edit-that-undoes-itself-and-does-not) | Weights at D = 0; image differs by a mean of 16 of 255 across 15 cells. |
| **Holds** | [Pushing any block costs fine texture, in either direction, and the cost grows the closer the block sits to the output.](notebook/05-knob-or-cost.md#the-common-mode-is-friction-not-a-knob) | Pre-registered. Mean common mode 0.978, 23 of 28 blocks below 1, r = -0.659 against block index, 11-14σ. |
| **Holds** | [The first block is a knob that runs the opposite way to the tail: pushed positive it smooths, pushed negative it etches.](notebook/05-knob-or-cost.md#the-first-block-runs-backwards) | Pre-registered as P3. r+ = 0.841, r- = 1.100, swing 0.764. |
| **Holds** | [On the last blocks the negative direction is the safe side: positive pushes wreck the image, negative pushes barely move it.](notebook/05-knob-or-cost.md#the-tail-is-rectified) | Amplitude ratio 9.1x on block 26, both arms on one scale. All six blocks from 22 onward asymmetric. |
| **Overturned** | [Blocks at either end of the network respond violently in both directions.](notebook/05-knob-or-cost.md#what-i-got-wrong) | Falsified. Predicted for the first block and at least three of five tail blocks; found in one of the five. |
| **Overturned** | [A bidirectional, mirror-image response is the exception rather than the rule.](notebook/05-knob-or-cost.md#what-i-got-wrong) | Falsified. 17 of 28 blocks are mirror-symmetric within 3σ. The prediction expected fewer than 10. |
| **Open** | [Two more arms produce no change at all and nobody yet knows whether that is the architecture or a bug in delivery.](notebook/00-the-bench.md#what-is-still-unknown) | Not verified here. The diagnosis is one run that prints the patch count. |

<!-- CLAIMS:END -->
