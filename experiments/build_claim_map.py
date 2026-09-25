# -*- coding: utf-8 -*-
"""
experiments/build_claim_map.py
==============================
Writes data/claim_map.csv: one row per notebook claim, assigning it to a chapter of the
instrument report and recording whether it can move as it stands or has to be re-derived.

The page and the status are READ FROM notebook/*.md, never typed here, so the map cannot
drift from the notebook. The chapter and the disposition are the editorial judgement and
live in CLASSIFICATION below. The script aborts if a claim exists in the notebook and not in
CLASSIFICATION, or the reverse: the map is never allowed to be silently incomplete.

It reads notebook/ and writes only data/. It never edits a notebook page.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "notebook"
DATA = ROOT / "data"
SKIP = {"AUTHORING.md", "STORY.md", "_template.md"}

CHAPTERS = {
    "C1": "What the instrument does",
    "C2": "What is safe to touch",
    "C3": "What the instrument can produce",
    "M": "Method, belongs in the appendix",
}

# claim id -> (chapter, disposition, why)
# disposition: moves_as_is | re_derive | not_needed
CLASSIFICATION = {
    # --- 00 the bench -------------------------------------------------------
    "node-is-identity-at-zero": ("C1", "moves_as_is",
        "Without it the tuner is not an instrument. This is the first sentence of the report."),
    "deterministic-across-sessions": ("C1", "moves_as_is",
        "Reinforcement available: gate_environment_determinism re-rendered a stage9 image seven days later byte-for-byte."),
    "roundtrip-does-not-return": ("C1", "moves_as_is",
        "An operating limit of the tool, not a curiosity: the edit has no image-level undo."),
    "cliplult-is-a-dead-arm": ("C1", "moves_as_is",
        "A defect of the instrument. A report about the tool must list its inert controls."),
    "noise-floor-measured": ("C1", "moves_as_is",
        "The measurement floor every threshold rests on."),
    "two-arms-undiagnosed": ("C1", "re_derive",
        "In a preset-centred notebook this is a footnote; in an instrument report it is an open defect. One run that prints the patch count closes it."),
    "an-edit-is-a-direction": ("C1", "moves_as_is",
        "Behaviour of the tool at fixed seed. The statement already concedes the random control does it too."),

    # --- 01 mark style ------------------------------------------------------
    "tiny-payload-shifts-mark-style": ("C3", "re_derive",
        "States 53 KB; the file is 50026 bytes and 1059 scalars. Built as preset-versus-controls; the instrument version is a statement about the payload."),
    "direction-not-distance": ("C3", "moves_as_is",
        "The load-bearing property of the whole system, measured at fixed displacement."),
    "mark-style-generalises": ("C3", "re_derive",
        "No generalisation criterion was ever frozen, and the 2026-09-25 numbers restrict it: transfer 0.38-0.47 inside a style domain, 0.05 across."),
    "colour-does-not-generalise": ("C3", "moves_as_is",
        "A specification of the tool, not a failure: colour follows the prompt."),
    "preset-is-a-sharp-operator": ("C3", "re_derive",
        "The most preset-centred claim in the notebook. The instrument version is about what a preset of the tuner does, not about this preset."),
    "operative-structural-property-unknown": ("C3", "moves_as_is",
        "The declared gap that the observer has put in the future: why it works."),

    # --- 02 attribute emergence --------------------------------------------
    "permutation-adds-a-neglected-attribute": ("C3", "re_derive",
        "Exploratory, no threshold fixed in advance. This is the trait-combination claim and it is the weakest one in the notebook."),
    "edit-adds-and-removes-unasked-traits": ("C3", "re_derive",
        "The confirmation could not resolve: 9 of its 10 prompts never light a headlight in any condition. The corpus, not the effect, failed."),
    "attribute-emergence-generality-untested": ("C3", "re_derive",
        "The pre-registered stage-7 attribute table was never filled. The test exists on paper only."),

    # --- 03 what ends up in the picture -------------------------------------
    "subject-enlargement-replicates": ("C3", "moves_as_is",
        "A useful effect, pre-registered, replicated on ten styles that did not exist when the prediction was frozen. A starting point for the hunt for resonances."),
    "blinding-is-a-measurement-and-it-failed": ("C3", "re_derive",
        "Same 17/20, two different claims. The frozen threshold was built to detect a blinding failure, not to establish perceptibility. The product claim needs its own statement and its own bar."),
    "enlargement-structure-or-magnitude": ("C3", "re_derive",
        "The sign-scrambled arm at the same displacement was never rendered, so no point on the magnitude axis exists."),

    # --- 04 where in the model ----------------------------------------------
    "position-beats-displacement": ("C2", "re_derive",
        "Exploratory, one seed per cell, one unsigned metric. The atlas redoes this properly and at matched displacement."),
    "blocks-point-in-different-directions": ("C2", "re_derive",
        "The family of comparisons was never declared and the result sits on the boundary the declaration would have decided."),
    "position-function-or-proximity": ("C2", "re_derive",
        "The atlas separates them by construction: early/late crossed with attention/mlp puts two functions at one depth."),

    # --- 05 knob or cost ----------------------------------------------------
    "cost-grows-with-depth": ("C2", "moves_as_is",
        "Literally what is dangerous to touch. Pre-registered, 23 of 28 blocks, r = -0.659."),
    "first-block-is-an-inverted-knob": ("C2", "moves_as_is",
        "An operating instruction: this control runs backwards."),
    "tail-is-rectified": ("C2", "moves_as_is",
        "An operating instruction: on the tail the negative direction is the safe side, 9.1x asymmetry on block 26."),
    "mirror-response-is-the-rule": ("C2", "moves_as_is",
        "Moves as a falsification. For a tool, knowing that 17 of 28 blocks are symmetric is operating information, not a defeat."),
    "extremes-are-violent-both-ways": ("C2", "moves_as_is",
        "Same: a prediction about the ends of the network that did not survive, and the map is better for it."),

    # --- 06 the hatching axis -----------------------------------------------
    "hatching-axis-holds-under-derangement": ("C3", "moves_as_is",
        "Pre-registered sign, confirmed on 16 fresh prompts at the permutation floor. The clearest candidate resonance on disk."),
    "hatching-axis-preset-runs-the-other-way": ("C3", "re_derive",
        "The pre-registration made this row conditional on a visual check that was never recorded. The missing piece is one visual check, not a new corpus."),
    "randsign-hatching-did-not-replicate": ("C3", "moves_as_is",
        "Moves as a negative result."),

    # --- 07 chromatic signatures --------------------------------------------
    "edits-move-colour-in-different-directions": ("C3", "moves_as_is",
        "The direct precursor of the atlas capacity number: different edits, different directions, twice on its Monte Carlo floor."),
    "chromatic-signature-per-edit-is-ambiguous": ("C3", "moves_as_is",
        "Three of six against a bar of four, declared in advance and not to be rounded up."),
    "colour-and-texture-are-not-one-signature": ("C3", "moves_as_is",
        "A constraint on any account of the mechanism."),

    # --- 08 block 1 vs block 6 ----------------------------------------------
    "blocks-separate-by-direction-not-distance": ("C2", "moves_as_is",
        "The prototype of the capacity claim: two groups at one distance, told apart, above a scramble null."),
    "block1-coheres-at-matched-displacement": ("C2", "moves_as_is",
        "Coherence 0.942 and 0.977 on ten prompts sharing no text with the pilot."),
    "block1-does-not-replicate": ("C2", "moves_as_is",
        "Moves as unresolved. The two families disagree and the pilot was not displacement-matched."),

    # --- 09 style direction --------------------------------------------------
    "style-does-not-steer-direction": ("C3", "moves_as_is",
        "Moves as a negative. WARNING: it is NOT the 2026-09-25 domain-specificity result. That one says the direction fails to transfer between domains; this one says the declared style does not steer it. Merging them is the relabelling error."),
    "double-dose-arm-is-degraded": ("C2", "moves_as_is",
        "Reclassified: this is the first measured ceiling on how hard the tool can be pushed. 18 cells of 24 outside the frozen quality gate at double amplitude."),
    "shared-scene-is-not-separated-from-style": ("C3", "moves_as_is",
        "A declared exchangeability limit. A crossed design settles it; the 160-render request of prereg_domain_specificity section 8 is that design."),

    # --- 10 all blocks clean -------------------------------------------------
    "response-grows-monotonically-with-angle": ("C2", "moves_as_is",
        "Dose-response per block group: the backbone of a calibration curve."),
    "specialization-disagrees-with-separability": ("C2", "moves_as_is",
        "Two instruments disagree about which blocks are close. For a calibration map this contradiction is the finding."),
    "output-lead-survives-dose-normalisation": ("C2", "moves_as_is",
        "Response per unit of displacement is the correct unit for calibration, and the lead widens under it."),

    # --- method ---------------------------------------------------------------
    "clip-224-is-blind-to-it": ("M", "not_needed",
        "A question about CLIP as a measuring device, not about the tool. Belongs in the measurement appendix."),
}


def read_claims():
    out = []
    for p in sorted(NOTEBOOK.glob("*.md")):
        if p.name in SKIP:
            continue
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"^---\n(.*?)\n---", txt, re.S)
        body = m.group(1) if m else txt
        for block in re.split(r"\n\s*- id:\s*", body)[1:]:
            cid = block.split("\n")[0].strip()
            st = re.search(r"status:\s*(\S+)", block)
            out.append((cid, p.name, st.group(1) if st else "?"))
    return out


def main():
    claims = read_claims()
    ids = [c[0] for c in claims]
    if len(ids) != len(set(ids)):
        sys.exit("ABORT: duplicate claim id in the notebook")
    missing = [i for i in ids if i not in CLASSIFICATION]
    extra = [i for i in CLASSIFICATION if i not in ids]
    if missing or extra:
        sys.exit(f"ABORT: unclassified {missing}; classified but absent from the notebook {extra}")

    rows = []
    for cid, page, status in claims:
        ch, disp, why = CLASSIFICATION[cid]
        rows.append(dict(claim_id=cid, page=page, status_now=status, chapter=ch,
                         chapter_name=CHAPTERS[ch], disposition=disp, rationale=why))
    with (DATA / "claim_map.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    from collections import Counter
    print(f"  {len(rows)} claims mapped")
    print("  by chapter:   ", dict(Counter(r["chapter"] for r in rows)))
    print("  by status:    ", dict(Counter(r["status_now"] for r in rows)))
    print("  by disposition:", dict(Counter(r["disposition"] for r in rows)))
    for ch in ("C1", "C2", "C3", "M"):
        sub = [r for r in rows if r["chapter"] == ch]
        h = sum(1 for r in sub if r["status_now"] == "holds")
        mv = sum(1 for r in sub if r["disposition"] == "moves_as_is")
        print(f"   {ch} {CHAPTERS[ch]:38s} n={len(sub):2d}  holds={h:2d}  moves_as_is={mv:2d}")


if __name__ == "__main__":
    main()
