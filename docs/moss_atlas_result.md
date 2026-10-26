# MOSS3 result — the MOSS atlas (turbo, not yet confirmed): the image model acts from its last third, the text encoder almost only at layer 0

2026-10-26. Pre-registration `docs/prereg_moss_atlas.md` (amendments 1-3). 1,335 renders by Antigravity at T10 (148
units × d = +1, +2, −1 × blacksmith, rally, close-up at 2718281). Values `data/moss_atlas_tests.csv`,
`data/moss_atlas_metrics.csv`; sheets `Text2Img/_moss_atlas/`. **Turbo only: every statement below is provisional until
the 12 pre-drawn cells are confirmed at R50.**

## Verdicts (DINOv2 distance to the plain picture, median over the three prompts)

| rule | result |
|---|---|
| **H1 depth, DiT** | ordered for MLP at +1 (ρ +0.74), −1 (+0.56), +2 (+0.76) and attention removed (+0.66): **deeper blocks change the picture more**; attention ×2 and ×3 not ordered (+0.43, +0.40) |
| **H1 depth, text encoder** | **not ordered** except attention removed (ρ −0.54: earlier layers matter more) |
| **H2 MLP > attention** | **does not hold** in the DiT (19, 16, 23 of 42); in the text encoder only for removal (25 of 32; 21 and 19 of 32 otherwise) |
| H3 full vs linear attention (TE) | median 0.030 vs 0.026: no difference |
| strongest (reported) | DiT 32 attention removed 0.99, DiT 0 attention removed 0.97, DiT 33 attention and MLP removed 0.86 and 0.85, TE 0 attention removed 0.81, DiT 31 MLP ×3 0.81, DiT 34 MLP removed 0.75, TE 0 attention ×3 0.71 |

## What the sheets show (blacksmith; Claude, conditions known, not blind)

* **DiT 1–20:** at ×2, ×3 and removed, the woman, the forge and the workbench stay; the fire and background shift a little.
* **DiT 21–27, MLP ×3:** **who** is drawn changes (an older woman, another face, other clothes), the scene stays.
* **DiT 28–41:** removing a sublayer breaks the picture into texture or noise (31–34); ×3 on the MLP washes it, lightens it
  or overlays sketch lines (36–41); DiT 0 attention removed gives a flat brown texture.
* **Text encoder:** layers 1–31 change almost nothing visible at any dose. **Layer 0** is the exception: attention ×3
  turns the scene into a grid of comic covers, attention removed into a sci-fi interface poster.
* **Style:** the blacksmith prompt starts with "Western comics style", but MOSS turbo draws it as a cinematic, almost
  photographic render (the dwarf, by contrast, is illustrated at both T10 and R50). Comparisons of style with the Krea
  atlas need this in mind.

## Reading

* MOSS's image model is quiet for two thirds of its depth and does most of its work, and most of its damage, in the last
  third. On Krea the middle blocks redrew content and the last ones changed colour and grain (page 21); on MOSS content
  changes around 21–27 and the last 14 blocks are fragile.
* The text encoder of MOSS is very robust: doubling, tripling or removing any sublayer of layers 1–31 barely moves the
  picture. On Krea single text-encoder layers changed genre and identity (page 30). Possible reasons, not tested: MOSS
  reads only the last layer; a 9B encoder is more redundant; the 2-block text embedder in the DiT absorbs changes.
* "MLP moves more than attention" (Krea page 29) is not a rule on MOSS.

## Next

Confirm at R50 the 12 cells drawn in advance (13 renders, about 37 min, blind page with controls). Then, if Alessandro
wants, a blind map of DiT 21–41 and TE 0 as on Krea's page 21.
