# -*- coding: utf-8 -*-
"""
experiments/judge_style_gate.py
===============================
FIRST STEP of docs/prereg_capability_judge.md, as amended by amendment 01 section 3.
It measures THE JUDGE, never the presets. No preset image is shown by this script.

The probe: the eight baseline renders at seed 42 are eight declared styles. The judge is asked
the style question about ALL EIGHT styles for each baseline -> an 8x8 confusion matrix, 64 items,
each asked in BOTH polarities (128 calls).

PASS, fixed in the amendment before any call: for at least 6 of the 8 baselines, the judge says
yes to its own style and no to at least 6 of the other 7. Polarity agreement above 20% makes the
answers unusable.

Every row logs model, backend, url and timestamp. The 2026-09-15 run of vlm_gate.py did not, and
a week later nobody could say which model had failed it: see
data/vlm_gate_20260915.csv and docs/prereg_capability_judge_amendment_01.md section 1.

Images go in at NATIVE resolution. No resize, no centre crop.

Usage (on the machine that runs Ollama):
    python experiments/judge_style_gate.py ^
        --renders "C:\\StabilityMatrix-win-x64\\Data\\Images\\Text2Img\\benchmark_atlas_phase1\\renders" ^
        --model qwen3.8:27b
Then hand data/capability_judge_gate.csv back. Run it once per judge; the file is appended to.
"""

from __future__ import annotations

import argparse
import base64
import csv
import datetime
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "capability_judge_gate.csv"

# scene -> the style phrase used in the question, taken from each prompt's own text
STYLES = {
    "S1_photo": "realistic photography",
    "S2_watercolor": "watercolor painting",
    "S3_lowpoly": "lowpoly 3D, flat shaded polygons",
    "S4_claymation": "claymation, stop-motion plasticine",
    "S5_ukiyoe": "traditional Japanese ukiyo-e woodblock print",
    "S6_pixel": "8-bit pixel art",
    "S7_glass": "stained glass window mosaic",
    "S8_charcoal": "rough charcoal sketch",
}
SEED = "42"
POS = "Is this image in the style of {style}? Answer only yes or no."
NEG = "Is this image NOT in the style of {style}? Answer only yes or no."


def ask(url, model, prompt, b64, timeout=300):
    body = json.dumps({"model": model, "prompt": prompt, "images": [b64],
                       "stream": False, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode()).get("response", "")


def yesno(text):
    t = re.sub(r"[^a-z]", " ", (text or "").lower())
    words = t.split()
    for w in words:
        if w in ("yes", "si", "sì", "yeah"):
            return 1
        if w in ("no", "not", "nope"):
            return 0
    return -1                      # unparsable, counted and never guessed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:11434")
    ap.add_argument("--backend", default="ollama")
    a = ap.parse_args()

    imgs = {}
    for scene in STYLES:
        fn = f"{scene}_baseline_seed{SEED}_00001_.png"
        p = os.path.join(a.renders, fn)
        if not os.path.exists(p):
            sys.exit(f"ABORT: missing baseline {fn}")
        imgs[scene] = base64.b64encode(open(p, "rb").read()).decode()
    print(f"  8 baselines loaded, native resolution, judge {a.model}")

    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows, n = [], 0
    for scene in STYLES:
        for asked, phrase in STYLES.items():
            for polarity, tmpl in (("positive", POS), ("negative", NEG)):
                q = tmpl.format(style=phrase)
                raw = ask(a.url, a.model, q, imgs[scene])
                n += 1
                rows.append(dict(
                    judge_model=a.model, backend=a.backend, url=a.url, run_utc=stamp,
                    image_scene=scene, asked_about=asked,
                    is_own_style=int(scene == asked), polarity=polarity,
                    question=q, answer_raw=(raw or "").strip().replace("\n", " ")[:160],
                    answer=yesno(raw)))
                print(f"  [{n:3d}/128] {scene:15s} asked {asked:15s} {polarity:8s} -> {rows[-1]['answer']}")

    new = not OUT.exists()
    with OUT.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        if new:
            w.writeheader()
        w.writerows(rows)

    # the gate, applied here so the answer is known before anything else is run
    ok = 0
    for scene in STYLES:
        own = [r for r in rows if r["image_scene"] == scene and r["is_own_style"] == 1
               and r["polarity"] == "positive"]
        oth = [r for r in rows if r["image_scene"] == scene and r["is_own_style"] == 0
               and r["polarity"] == "positive"]
        if own and own[0]["answer"] == 1 and sum(1 for r in oth if r["answer"] == 0) >= 6:
            ok += 1
    pos = {(r["image_scene"], r["asked_about"]): r["answer"] for r in rows if r["polarity"] == "positive"}
    neg = {(r["image_scene"], r["asked_about"]): r["answer"] for r in rows if r["polarity"] == "negative"}
    pairs = [(k, pos[k], neg[k]) for k in pos if pos[k] in (0, 1) and neg.get(k) in (0, 1)]
    agree = sum(1 for _, p, q in pairs if p == q) / len(pairs) if pairs else float("nan")
    unpars = sum(1 for r in rows if r["answer"] == -1)
    yes_share = sum(1 for r in rows if r["polarity"] == "positive" and r["answer"] == 1) / 64

    print(f"\n  scenes passing (own yes, >=6 of 7 others no): {ok} / 8   [gate needs 6]")
    print(f"  polarity agreement (should be low): {agree:.3f}   [unusable above 0.20]")
    print(f"  share of yes on the positive polarity: {yes_share:.3f}")
    print(f"  unparsable answers: {unpars} / 128")
    print(f"  VERDICT: {'PASS' if (ok >= 6 and agree <= 0.20) else 'FAIL — the capability study stops here'}")
    print(f"  wrote {len(rows)} rows to data/capability_judge_gate.csv")


if __name__ == "__main__":
    main()
