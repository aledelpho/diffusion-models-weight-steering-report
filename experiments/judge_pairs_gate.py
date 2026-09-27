#!/usr/bin/env python3
"""Multi-image gate -- can this judge address two images as two?

Pre-registration: docs/prereg_damage_or_style.md section 4, frozen before any call.
Every prior judge call in this project sent ONE image. This gate uses manipulations with
CERTAIN ground truth, applied to copies of the baselines. Image processing, never rendering.

PASS criteria, frozen: per probe, >= 14/16 correct AND >= 12/16 order agreement;
overall first-position share inside [0.30, 0.70].

    python experiments/judge_pairs_gate.py --renders "<...>\\benchmark_mappa\\renders" --model qwen3.8:27b
"""
import argparse, csv, datetime, math, os, pathlib, sys, tempfile
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from judge_multi_image import ask, ab, b64

OUT = pathlib.Path("data/damage_style_gate.csv")
PROBES = {
    "saturation": ("Which of these two images is more colourful? Answer only A or B.", "more"),
    "sharpness":  ("Which of these two images is sharper and better in focus? Answer only A or B.", "more"),
    "degradation":("Which of these two images has more visible defects, noise or artefacts? "
                   "Answer only A or B.", "more"),
}

def variants(src, probe, tmp):
    im = Image.open(src).convert("RGB")
    if probe == "saturation":
        hi, lo = im, ImageEnhance.Color(im).enhance(0.5)
    elif probe == "sharpness":
        hi, lo = im, im.filter(ImageFilter.GaussianBlur(2.0))
    else:
        rng = np.random.default_rng(0)
        a = np.asarray(im, dtype=np.float32)
        lo = Image.fromarray(np.clip(a + rng.normal(0, 4, a.shape), 0, 255).astype(np.uint8))
        hi = Image.fromarray(np.clip(a + rng.normal(0, 16, a.shape), 0, 255).astype(np.uint8))
    p1 = os.path.join(tmp, f"{probe}_hi.png"); p2 = os.path.join(tmp, f"{probe}_lo.png")
    hi.save(p1); lo.save(p2)
    return p1, p2          # p1 is ALWAYS the image the question's answer points to

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:11434")
    a = ap.parse_args()
    # Amendment 01: ALL baselines, never a silent slice. A dropped image is an
    # unjustified exclusion, and there is no reason to give the gate less power.
    bases = sorted(f for f in os.listdir(a.renders) if "_baseline_" in f)
    if len(bases) != 9:
        print(f"NOTE: expected 9 baselines, found {len(bases)} -- thresholds scale with n")
    n = len(bases)
    OUT.parent.mkdir(exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    fields = ["judge_model", "url", "run_utc", "probe", "baseline", "order",
              "correct_letter", "question", "answer_raw", "choice", "correct"]
    new = not OUT.exists()
    rows = []
    with tempfile.TemporaryDirectory() as tmp, OUT.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        if new:
            w.writeheader()
        for bn in bases:
            for probe, (q, _) in PROBES.items():
                p_hi, p_lo = variants(os.path.join(a.renders, bn), probe, tmp)
                for order in ("hi_first", "lo_first"):
                    imgs = [b64(p_hi), b64(p_lo)] if order == "hi_first" else [b64(p_lo), b64(p_hi)]
                    correct = "A" if order == "hi_first" else "B"
                    raw = ask(a.url, a.model, q, imgs)
                    ch = ab(raw)
                    r = dict(judge_model=a.model, url=a.url, run_utc=stamp, probe=probe,
                             baseline=bn, order=order, correct_letter=correct, question=q,
                             answer_raw=(raw or "").replace("\n", " ")[:300], choice=ch,
                             correct=int(ch == correct) if ch else -1)
                    w.writerow(r); fh.flush(); rows.append(r)
                    print(f"  {probe:12s} {bn[:28]:28s} {order:9s} -> {ch or '?':1s} "
                          f"{'OK' if r['correct']==1 else 'x'}")
    print("\n" + "=" * 62)
    allok = True
    for probe in PROBES:
        sub = [r for r in rows if r["probe"] == probe]
        ok = sum(1 for r in sub if r["correct"] == 1)
        # order agreement: both orders of the same (baseline, probe) answered correctly,
        # i.e. the judge tracked the image and not the position. 6 pairs of 8 = 12 of 16.
        agree = sum(1 for i in range(0, len(sub), 2)
                    if sub[i]["correct"] == 1 and sub[i + 1]["correct"] == 1) * 2
        # Amendment 01: thresholds as proportions of n, >= 0.889 correct and >= 0.778
        # order-agreeing -- both stricter than the 14/16 and 12/16 first deposited.
        p = ok >= math.ceil(0.889 * 2 * n) and agree >= math.ceil(0.778 * 2 * n)
        allok &= p
        print(f"  {probe:12s} correct {ok:2d}/{2*n}  order-agreeing {agree:2d}/{2*n}"
              f"  (need {math.ceil(0.889*2*n)} and {math.ceil(0.778*2*n)})"
              f"  -> {'PASS' if p else 'FAIL'}")
    good = [r for r in rows if r["choice"]]
    share = sum(1 for r in good if r["choice"] == "A") / len(good) if good else 0
    ps = 0.30 <= share <= 0.70
    allok &= ps
    print(f"  first-position share {share:.3f} in [0.30,0.70] -> {'PASS' if ps else 'FAIL'}")
    print("=" * 62)
    print("GATE PASSED" if allok else "GATE FAILED -- this is the result. Write it up and stop.")
    sys.exit(0 if allok else 2)

if __name__ == "__main__":
    main()
