# Amendment 01 to `docs/prereg_capability_judge.md` — the candidate judge has already failed a gate

- **Written:** 2026-09-26, before any image has been shown to any judge.
- **Nature:** tightens the study and changes its first step. It relaxes nothing.

---

## 1. What already exists, and what it says

`experiments/vlm_gate.py` — present in both repositories, written 2026-09-15 — is a design for
calibrating a VLM judge **before** using it. Its header already states the three design choices
the parent pre-registration got wrong, and the three probes it runs. It was **executed**, and its
output is now carried here as `data/vlm_gate_20260915.csv` (provenance: `comfyui-pilot/vlm_gate.csv`,
2026-09-15 09:42; 12 rows, 6 pairs).

The observer states that the model used was **Gemma4** — the same model proposed as judge for this
study. **The CSV does not record the model name, the date or the backend**, because the script takes
`--model` as a required argument and never writes it to the output. The identification therefore
rests on recollection, not on the file. That is a reproducibility defect in the script and is
recorded as such; the script must log model, backend, URL and timestamp before it is run again.

What the run shows, on the two **easiest** pairs, where the measured difference in median stroke
width is **37.76 px** and **35.41 px**:

| pair | order AB | order BA | choice |
|---|---|---|---|
| `preset_pos` vs `preset_neg` | wrong | right | **B** |
| `blockshuf_pos` vs `blockshuf_neg` | wrong | right | **B** |

Four answers, all "B". On the **negative control** — two baselines, same prompt, different seeds,
no preset applied — one pair returned "SAME" in both orders, and the other declared a visible
difference in line weight in both orders, naming **the opposite image each time**. Every one of the
twelve rows carries `confidenza = 5`.

Position bias on the easy pairs, confabulation on a pair where nothing was edited, maximum
confidence throughout.

## 2. What that does and does not disqualify

**It disqualifies a VLM for fine-grained texture comparison.** "Which of these two crops has
thicker contour lines" is a low-level perceptual measurement, and on that task this judge is worse
than useless, because it is confident.

**It does not automatically disqualify it for this study's questions**, and saying otherwise would
be as sloppy as ignoring it. "Is this image pixel art" and "does it show a rally car" are coarse
semantic judgements, a different capability from "is this line 3 px thicker". A model can be
hopeless at the second and adequate at the first. The 2026-09-15 run is therefore evidence about
**the wrong task**, and the parent pre-registration cannot simply inherit its verdict either way.

**The rule this leaves:** a gate is only informative about the task it was run on. The capability
study needs its own gate, matched to its own questions, and that gate comes first.

## 3. The first step, replacing §4 of the parent document

**Style confusion matrix on the baselines alone.** The 8 baseline renders at seed 42 are eight
declared styles. For each baseline, the judge is asked the style question about **all eight**
styles, not only its own: 8 × 8 = **64 calls**.

- **Pass** requires the judge to answer yes to a baseline's own style and no to at least 6 of the 7
  others, for at least **6 of the 8** styles. The thresholds are fixed here.
- **Fail** ends the study on the spot, at a cost of 64 calls and about two minutes. No image of any
  preset is ever shown.
- Whatever it returns, the full 8 × 8 matrix is reported: it is the judge's measured resolution and
  tells us which styles it cannot tell apart, which bounds every later reading.

This probe is strictly stronger than the positive control of the parent §4, because it tests
discrimination **between** styles rather than between a baseline and a visibly broken render, and a
model that answers "yes" to everything fails it by construction.

## 4. Two guards added, both taken from `vlm_gate.py`'s reasoning

**Polarity bias.** Yes/no questions have no position, but they have a polarity. Each style question
is asked in both forms — `Is this image in the style of X?` and `Is this image NOT in the style of
X?` — and the two must disagree. The share of pairs where they **agree** is the polarity-bias
measure, and above 20 % the judge's yes/no answers are not usable.

**Native resolution.** No image is resized or centre-cropped to feed the judge. The renders are
1024 × 1280 and go in whole, at their own pixel size. Resizing is the failure `vlm_gate.py`'s
header names, and it is what makes a CLIP-style 224 px pipeline blind to exactly the properties
this project measures.

## 5. What is dropped from the parent document

Question 3, `Rate the technical quality of this image from 1 to 5`, is **withdrawn**. Two reasons,
both already on the record:

- `vlm_gate.py`'s header: absolute 1–5 ratings are dominated by the subject, not by the
  intervention. Every one of its twelve answers came back at confidence 5, which is the same
  pathology in the confidence field.
- `claude/stage9-esito-e-verifica-2026-09-18.md`: the automatic quality gate marked
  `blockshuf_neg_2x` DEGRADED in 6 styles of 8 — precisely the six where the observer judged it the
  **best and most respectful of the declared style**. The count "18 of 24 degraded" was **retracted**
  for that reason. An instrument that cannot separate damage from strong correct re-stylisation
  must not be asked for a quality score, and a VLM inherits the same confusion with less
  transparency.

Q1 and Q2 stand. §5 and §6 of the parent document are otherwise unchanged.
