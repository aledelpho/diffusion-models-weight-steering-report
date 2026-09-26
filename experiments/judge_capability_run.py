# -*- coding: utf-8 -*-
"""
experiments/judge_capability_run.py
===================================
STEP 2 of docs/prereg_capability_judge.md (+ amendments). Asks the judge the two frozen
capability questions about the 200 images of the corpus, in both polarities, and appends every
answer with the judge's identity and the timestamp.

DO NOT RUN THIS BEFORE experiments/judge_style_gate.py HAS PRINTED "PASS".
The gate decides whether the judge is an instrument at all. This script refuses to start unless
data/capability_judge_gate.csv contains a passing run for the same --model.

Corpus: seed 42 only. 24 live presets x 8 scenes = 192, plus the 8 baselines = 200 images.
`modulation_norm` is excluded: its renders are the baseline, pixel for pixel
(docs/prereg_style_capacity_amendment_02.md).

Questions, verbatim and frozen:
  Q1  Is this image in the style of {style}? Answer only yes or no.
  Q2  Does this image show a yellow and blue rally car in a jungle? Answer only yes or no.
Each is also asked in the negated form; the two must disagree, and an item where they agree is
discarded by the analysis and counted (polarity bias).
Question 3 of the parent document, the 1-5 quality rating, was withdrawn by amendment 01 section 5.

Test-retest: 30 images drawn with random.Random(1337) are asked a second time, tagged rep=1.
Resumable: rows already present in the output for the same model are skipped, so an interrupted
run continues where it stopped.

Usage:
    python experiments/judge_capability_run.py --renders "<...>\\renders" --model qwen3.8:27b
"""

from __future__ import annotations

import argparse
import base64
import csv
import datetime
import json
import os
import random
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
GATE = DATA / "capability_judge_gate.csv"
OUT = DATA / "capability_judge_raw.csv"
PLANS = ["perturbation_atlas_phase1_plan.csv", "perturbation_atlas_phase2_plan.csv"]
SEED = "42"
INERT = {("modulation_norm", "1"), ("modulation_norm", "2")}

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
Q1P = "Is this image in the style of {style}? Answer only yes or no."
Q1N = "Is this image NOT in the style of {style}? Answer only yes or no."
Q2P = "Does this image show a yellow and blue rally car in a jungle? Answer only yes or no."
Q2N = "Is it false that this image shows a yellow and blue rally car in a jungle? Answer only yes or no."


def yesno(text):
    for w in re.sub(r"[^a-z]", " ", (text or "").lower()).split():
        if w in ("yes", "si", "yeah", "true"):
            return 1
        if w in ("no", "not", "nope", "false"):
            return 0
    return -1


def ask(url, model, prompt, b64, timeout=300):
    body = json.dumps({"model": model, "prompt": prompt, "images": [b64],
                       "stream": False, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode()).get("response", "")


def gate_passed(model):
    if not GATE.exists():
        return False, "data/capability_judge_gate.csv does not exist"
    rows = [r for r in csv.DictReader(GATE.open(encoding="utf-8")) if r["judge_model"] == model]
    if not rows:
        return False, f"no gate rows for model {model}"
    ok = 0
    scenes = sorted({r["image_scene"] for r in rows})
    for sc in scenes:
        own = [r for r in rows if r["image_scene"] == sc and r["is_own_style"] == "1"
               and r["polarity"] == "positive"]
        oth = [r for r in rows if r["image_scene"] == sc and r["is_own_style"] == "0"
               and r["polarity"] == "positive"]
        if own and own[0]["answer"] == "1" and sum(1 for r in oth if r["answer"] == "0") >= 6:
            ok += 1
    pos = {(r["image_scene"], r["asked_about"]): r["answer"] for r in rows if r["polarity"] == "positive"}
    neg = {(r["image_scene"], r["asked_about"]): r["answer"] for r in rows if r["polarity"] == "negative"}
    pr = [(pos[k], neg[k]) for k in pos if pos[k] in ("0", "1") and neg.get(k) in ("0", "1")]
    agree = sum(1 for p, q in pr if p == q) / len(pr) if pr else 1.0
    if ok >= 6 and agree <= 0.20:
        return True, f"gate passed: {ok}/8 scenes, polarity agreement {agree:.3f}"
    return False, f"gate FAILED: {ok}/8 scenes, polarity agreement {agree:.3f}"


def corpus(renders):
    items = []
    seen = set()
    for pl in PLANS:
        for r in csv.DictReader((DATA / pl).open(encoding="utf-8")):
            if r["type"] == "determinism_check" or r["seed"] != SEED:
                continue
            key = (r["condition"], r.get("draw", ""))
            if r["type"] != "baseline" and key in INERT:
                continue
            fn = os.path.basename(r["expected_filename"])
            if fn in seen:
                continue
            seen.add(fn)
            items.append(dict(file=fn, scene=r["prompt_id"], kind=r["type"],
                              condition=r["condition"], draw=r.get("draw", "")))
    missing = [i["file"] for i in items if not os.path.exists(os.path.join(renders, i["file"]))]
    if missing:
        sys.exit(f"ABORT: {len(missing)} images missing, e.g. {missing[:3]}")
    return sorted(items, key=lambda i: i["file"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:11434")
    ap.add_argument("--backend", default="ollama")
    a = ap.parse_args()

    ok, why = gate_passed(a.model)
    print(f"  {why}")
    if not ok:
        sys.exit("ABORT (pre-registration): the judge has not passed the style gate. "
                 "Run experiments/judge_style_gate.py first. No preset image is shown until it passes.")

    items = corpus(a.renders)
    print(f"  corpus: {len(items)} images at seed {SEED} "
          f"({sum(1 for i in items if i['kind']=='baseline')} baselines)")
    if len(items) != 200:
        print(f"  WARNING: expected 200 images, found {len(items)} — reported, not repaired")

    rng = random.Random(1337)
    retest = set(rng.sample([i["file"] for i in items], min(30, len(items))))

    done = set()
    if OUT.exists():
        for r in csv.DictReader(OUT.open(encoding="utf-8")):
            if r["judge_model"] == a.model:
                done.add((r["file"], r["question"], r["polarity"], r["repetition"]))
        print(f"  already answered for this model: {len(done)} rows — they are skipped")

    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    todo = []
    for it in items:
        reps = [0, 1] if it["file"] in retest else [0]
        for rep in reps:
            for q, pol, tmpl in (("Q1", "positive", Q1P), ("Q1", "negative", Q1N),
                                 ("Q2", "positive", Q2P), ("Q2", "negative", Q2N)):
                if (it["file"], q, pol, str(rep)) in done:
                    continue
                todo.append((it, rep, q, pol, tmpl.format(style=STYLES[it["scene"]])
                             if q == "Q1" else tmpl))
    print(f"  calls to make: {len(todo)}")

    new = not OUT.exists()
    fields = ["judge_model", "backend", "url", "run_utc", "file", "scene", "kind", "condition",
              "draw", "question", "polarity", "repetition", "prompt", "answer_raw", "answer"]
    with OUT.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        if new:
            w.writeheader()
        cache = {}
        for n, (it, rep, q, pol, prompt) in enumerate(todo, 1):
            if it["file"] not in cache:
                cache.clear()
                cache[it["file"]] = base64.b64encode(
                    open(os.path.join(a.renders, it["file"]), "rb").read()).decode()
            raw = ask(a.url, a.model, prompt, cache[it["file"]])
            w.writerow(dict(judge_model=a.model, backend=a.backend, url=a.url, run_utc=stamp,
                            file=it["file"], scene=it["scene"], kind=it["kind"],
                            condition=it["condition"], draw=it["draw"], question=q,
                            polarity=pol, repetition=rep, prompt=prompt,
                            answer_raw=(raw or "").strip().replace("\n", " ")[:160],
                            answer=yesno(raw)))
            fh.flush()
            if n % 20 == 0 or n == len(todo):
                print(f"  [{n}/{len(todo)}]")
    print(f"  done. data/capability_judge_raw.csv")


if __name__ == "__main__":
    main()
