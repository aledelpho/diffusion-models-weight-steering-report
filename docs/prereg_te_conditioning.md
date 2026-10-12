# Pre-registration C67 — what a text-encoder edit does to the conditioning, token by token

Written 2026-10-12, **before any conditioning is computed.** No images. Code: `experiments/te_conditioning.py`
(plan, queue, gate, reduce, logit lens, rules, self-test) and the ComfyUI node `tools/comfyui_krea2_probe`
(`Krea2ConditioningProbe`), committed with this document.

## Question (Alessandro, 2026-10-12)

Instead of judging pictures, read *what came out* of the text encoder after it read the prompt: which words does an
edit move, and does that explain what the eye saw — the size of the change (C64), the word-order dependence (C65 B),
the characters that follow or break the common direction (C65 A)?

## What is measured

Krea-2's DiT receives, for each prompt, a tensor (seq, 12, 2560): the hidden states of Qwen3-VL-4B at the 12 taps
(layers 2, 5, …, 35; tap k is the input of layer k; final norm applied), the template prefix stripped
(`comfy/text_encoders/krea2.py`). The node encodes the prompt with the CLIP it receives — so the
ArthemyKrea2CLIPTuner patch applies exactly as for CLIPTextEncode — and writes that tensor (baselines, and the 20
C65 edits on the elf) or, for every other edit, its difference from the baseline of the same prompt: per position
and tap the relative change |c − b| / |b| and the cosine. An edit to layer L can only reach the taps after L; every
summary averages over those taps only.

**Material (721 encodes, seed-independent):** the elf prompt of C64 with every text-encoder edit of C64 (426, all
doses, checks included); the five word orders of C65 B and the eight prompts of C65 A/C (seven characters,
watercolour D1) with the 20 C65 edits; the elf with the 20 C65 edits in full for the logit lens; the baselines (the
elf twice, for determinism).

## Gate (before anything is read)

* the elf baseline encoded twice is **identical** (bit for bit);
* layer 35 at +1.00 gives relative change **0** at every position (it is never read); the visual-tower edit too;
* L02 MLP at +1.00 gives a change **> 0**.

If the gate fails, nothing below is computed.

## Rules (thresholds fixed now; labels already committed, by Alessandro)

| test | measure | rule |
|---|---|---|
| E1 | elf, ±1.00 edits: mean relative change over positions and reached taps vs C64 phase-1 "how much it changed" (none … strong, text) | Spearman ρ ≥ 0.50 → supported |
| E2 | word order: per edit, the per-word change profile in each of the five orders; disagreement = 1 − mean Spearman between orders, vs the 1–5 scores (seed 3141592) | ρ ≥ 0.50 → supported |
| E3 | characters: share of the change that falls on the words shared by all seven prompts (Western comics style, close-up portrait, frontal view, white / simple background) vs "same direction" (yes 2 / partly 1 / no 0) | ρ ≥ 0.40 → supported |

Reported, deciding nothing: AUC of the E1 measure for style *changed* vs *unchanged*; for each edit the eight words
it moves most; the q+k-only checks against whole-attention edits of the same layers (QK-norm predicts a small
change); the logit lens — each tap projected through the encoder's own token embedding (Qwen3-4B ties input and
output embeddings), top-3 tokens per position — and, in particular, what L00 attention / MLP at −1.00 (the edits
that render the prompt as text) do to it.

## Limits

The conditioning is what the DiT *receives*, not what it *does* with it; a large change the DiT ignores, or a
small one it amplifies, would break E1–E3 without the measurement being wrong. Relative change per position mixes
direction and size; the cosine is stored for later. One prompt per family; the word grouping of tokens is a fixed
rule (`words()` in the code). The logit lens on intermediate layers of a model with tied embeddings is a known but
rough reading (Belrose et al. 2023 propose tuned lenses for this reason).
