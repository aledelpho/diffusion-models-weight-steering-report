# Pre-registration C71 — does an edit push the conditioning toward "anime" as the text itself would?

Written 2026-10-12, **before any C71 encode.** No images. Code: `experiments/te_direction.py`; plan
`data/te_direction_plan.csv` (16 encodes).

## Question

C70 found that when an edit changes the genre, the result is anime in 39 of 50 images. It also found that this is not
explained by less attention on the style words (C69, C70 G1/G1d). The remaining hypothesis is about content: the
edits that end in anime push the conditioning in the same direction as writing "anime" in the prompt would.

## Material

* **New encodes (15).** In each of the five word orders, the clause "realistic western comics style" is replaced by
  one of three alternatives; everything else is identical:
  * "anime style";
  * "cartoon style";
  * "oil painting style" (control: no image went to painting in C70).
* **Gate encode (1).** The V1 baseline is encoded again.
* **Encode settings.** Full conditioning, all 12 taps, with the same node as C67/C68.
* **Existing material.** The C67 baselines and the C68 edits (20 edits × 5 orders, full); the C70 genre labels
  (seed 3141592).

## Measures

* **Pooled conditioning** = mean over token positions, per tap. Pooling makes prompts of different length comparable;
  C67 found the edits' push to be mostly prompt-independent, which pooling keeps.
* **Push of an edit** = pooled(edit) − pooled(baseline).
* **Direction of a swap** = pooled(swap) − pooled(baseline).
* **Cosine** between the two, on the taps the edit reaches, averaged over the five orders.
* **Anime − painting.** Every swap also *removes* "western comics". Subtracting the painting direction from the anime
  direction cancels that shared removal and keeps what is specific to anime.

## Gate

The re-encoded V1 baseline must be **bit-identical** to the C67 baseline. Otherwise nothing is computed.

## Tests (thresholds fixed now)

| test | measure (20 edits) | rule |
|---|---|---|
| H1 | cos(push, anime direction) vs number of anime images (0–5, C70) | Spearman ρ ≥ 0.50 → supported |
| H2 | cos(push, anime − painting) vs number of anime images | ρ ≥ 0.40 → supported |

## Reported, deciding nothing

* **R1:** cos(push, cartoon − painting) vs number of cartoon images.
* **R2:** cos(push, painting direction) vs number of anime images (control).
* **R3:** the similarity of the three style directions to each other.
* **Per edit:** all cosines.

## Limits

* **Pooling.** Pooling over positions mixes the swapped clause with the rest of the prompt; an effect located on a
  few tokens can be diluted.
* **Small counts.** Many edits have 0 anime images, so ties are many.
* **Labels.** The anime counts come from one labeller and one seed.
* **One wording.** A single wording per style ("anime style"); other wordings could point elsewhere.
* **Similar does not mean causal.** A push similar to the text's anime direction does not show that this direction
  causes the anime look in the DiT.
