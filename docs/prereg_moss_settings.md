# Pre-registration MOSS-S — which sampling settings can stand in for the slow reference?

Written 2026-10-25 by Claude, **before any render.** Asked by Alessandro: at 50 steps MOSS takes about 150 s per picture;
calibrate first, then spend hours on renders, and try the turbo LoRA already. Comes before MOSS2, which will use the
setting chosen here (MOSS2 amendment 2 will say which).

## Design (84 renders, about 2 h)

* **Settings:** R50 euler, 50 steps, CFG 3 (reference); E25 euler, 25 steps, CFG 3; T8 the lodestones 8-step DMD2 LoRA
  (`Moss\lodestones-8-steps-dmd2-lora.safetensors`, strength 1.0, distilled from MOSS-Image Base), euler, 8 steps, CFG 1.
  All: simple scheduler, MOSS's default shift 5, 1024 × 1280, SFT bf16, both MOSS tuners in the graph.
* **Plain:** six prompts (dwarf, rally, still life, comic page, lotus canoe, leaf) × seeds 2645751, 3316624, per setting.
* **Edits:** dwarf and rally at 2645751; DiT MLP down of layers 6 and 20, TE MLP down of layers 6 and 27; d = 0.10 and
  0.30; per setting (16 cells).
* **Tuner v4:** with the LoRA, an edit multiplies the patched weight, (W + LoRA) × (1 + d); without it, unchanged.

## Rules (fixed now)

* **S1 fidelity:** median DINOv2 distance between a setting's plain picture and R50's (same prompt and seed) ≤ half of
  R50's median distance between the two seeds.
* **S2 edits proportional:** over the 16 edit cells, the distance of each edited picture to its own plain picture;
  Spearman with R50's ≥ 0.80 **and** median ratio to R50 between 0.5 and 2.
* **Decision:** E25 replaces R50 for the experiments if it passes S1 and S2. T8 is used for large sweeps if it passes
  S2 and Alessandro judges its pictures acceptable on the sheet (S1 reported: the LoRA is expected to change the look);
  every result found with T8 is then confirmed on R50. Neither passes: R50 stays, and the experiments are made smaller.
* **Reported:** the seed floor per setting (distillation may shrink it); the pairwise table.

## Limits

One seed for the edits, 16 cells; DINOv2 distance only (no eye pass on the edits). The LoRA is a community distillation
of the Base checkpoint used on SFT.
