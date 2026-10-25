# Pre-registration MOSS3 — an atlas of MOSS-Image: every DiT block and every text-encoder layer

Written 2026-10-25 by Claude, **before any render.** Asked by Alessandro ("andiamo con il turbo ... facciamo un atlante del
model e text encoder"). Working setting T10 (MOSS2), with confirmation cells at R50 named now.

## Design (1,201 renders: 1,188 at T10, about 7 h 15 min; 13 at R50, about 37 min)

* **Units (148):** DiT layers 0–41, attention (`proj.o`) and MLP (`proj.ffn_down`); text-encoder layers 0–31, MLP
  (`mlp.down_proj`) and attention (`self_attn.o_proj` on the full-attention layers 3, 7, …, 31; `linear_attn.out_proj`
  on the other 24). Editing the output projection scales the whole sublayer's contribution to the stream.
* **Doses:** d = +1 (contribution doubled) and d = −1 (contribution removed). MOSS2: d ≤ 0.30 barely moves MOSS.
* **Prompts:** dwarf, rally, still life, comic page, at seed 2645751, plus their plain pictures.
* **Confirmation (R50, dwarf):** the plain picture and 12 unit × sign cells drawn now with `random.Random(31337)`:
  te22 attn +, dit21 mlp −, dit38 mlp +, dit07 attn +, dit26 attn +, dit23 attn +, dit40 attn −, dit13 mlp +, te29 mlp +,
  te12 mlp −, te00 mlp +, te00 attn −. Their blind check (same kind of change, T10 against R50) follows the MOSS2 protocol
  with controls, page written after the renders.

## Questions and rules (fixed now), DINOv2 distance to the plain picture, median over the four prompts

* **H1 depth (from Krea pages 21 and 29: the effect of an edit depends on depth):** per half and sign, Spearman between
  layer index and distance; |ρ| ≥ 0.5 → *depth orders the change*.
* **H2 MLP against attention (Krea page 29: most of the noise lives in the MLP):** the MLP moves the picture more than the
  attention in at least 2/3 of the layers → *holds*, per model part and sign.
* **H3, reported:** text-encoder attention, full-attention layers against linear-attention layers.
* **Reported:** the ten strongest unit × sign; contact sheets per prompt and part for Alessandro's eye (what each layer
  does), the basis of a later blind map as on Krea's page 21.

## Limits

One seed; DINOv2 distance says how much, not what; doses not calibrated per layer; turbo results are provisional until
confirmed (MOSS2: 4 of 6 edits confirmed).
