# C64 — first look while the renders run (2026-10-11)

Exploratory notes on the first 15 renders of the text-encoder pilot (`docs/plan_te_pilot.md`); nothing here is
a claim, and the pilot is one prompt at one seed.

* **Controls.** Baseline reproduces to the pixel. Layer 35 doubled and a visual-tower block doubled are identical
  to the pixel to the baseline: E1 holds — the tap reading (layer 35 never read, visual tower inert) is right.
  Layer 2 MLP doubled changes the image (mean |Δ| 53/255): the patch reaches the encoder.
* **q and k alone doubled (E2, QK-norm) do not leave the image unchanged:** mean |Δ| 10.5-11.5/255, about a quarter of
  the pixels moved by more than 10, at layers 5, 17 and 29. By eye the elf is the same picture with small changes
  (the lightning on the gauntlet). The norm should remove a uniform scale of q and k exactly in exact arithmetic;
  whether the residual is numerical (a patched weight taking another compute path) or real is not known. Until a
  near-null patch is rendered (×(1+ε) that changes no bf16 weight), **a change of this size (~10/255 mean) must be
  treated as the floor** of what a text-encoder edit can be told apart from.
* **Layer 0 knocked out draws the prompt as text.** With the attention of layer 0 zeroed (×0) the picture becomes
  rows of black words on a pale ground, many readable fragments of the prompt ("western", "style", "from", "with").
  With the MLP of layer 0 zeroed it is clearer still: a page of text set in two quoted paragraphs, beginning
  "realist; om wetern comips gih: syile, battcm hutten..." — *realistic western comics style, bold ink outlines* —
  and a second paragraph opening "liyiting:", the prompt's own "Lighting:" section. The elf is gone.
  Reading, not yet tested: without layer 0 the encoder's states keep the identity of the tokens but lose what they
  mean together, and the DiT, trained to render text it is asked to write, renders the words themselves. This fits
  the interpretability literature on language models, where the first layers "detokenise" — turn tokens into
  word- and phrase-level features — and ablating them is the most damaging single ablation (Lad, Gurnee, Tegmark
  2024; Gurnee et al. 2023). To check on more prompts and seeds before saying more.
* **Layer 0 attention doubled** drops attributes the prompt names — the antlers, the eyepatch, the fur collar — and
  changes the pose, with a clean surface. **Layer 0 attention −0.35** keeps the picture and loses the lightning.
  So far E4 (the encoder changes what is drawn, not the surface) holds on every render looked at.
