"""C56 — how small a push completes the archer's hood, block by block (docs/prereg_hood_threshold.md).
Written 2026-10-06.

  python hood_threshold.py --plan              # data/hood_threshold_plan.csv (41 rows)
  python hood_threshold.py --queue --first 1   # the baseline re-render only
  python hood_threshold.py --repro             # it must equal the C47 baseline pixel for pixel
  python hood_threshold.py --queue             # the other 40
  python hood_threshold.py --count             # expected 41 missing 0
  python hood_threshold.py --page              # blind page for Alessandro + data/hood_threshold_page_key.csv
  python hood_threshold.py --tally --answers data/hood_threshold_labels_alessandro.csv
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "hood_threshold_plan.csv"
PKEY = DATA / "hood_threshold_page_key.csv"
FOLDER = "benchmark_hood_threshold"
SEED = "3141592"
BLOCKS = [0, 10, 20, 23]
DOSES = [0.01, 0.02, 0.04, 0.08, 0.16]


def vec(b, d):
    v = ["0.0"] * 34
    v[b] = repr(float(d))
    return ",".join(v)


def make_plan():
    b = [r for r in csv.DictReader(open(c47.PLAN, encoding="utf-8"))
         if r["prompt_id"] == "P3_archerforest" and r["seed"] == SEED and r["cond"] == "baseline"][0]
    conds = [("baseline", "", "", "", "")]
    for blk in BLOCKS:
        for sign in (-1, 1):
            for d in DOSES:
                conds.append((f"blk{blk:02d}_{'neg' if sign < 0 else 'pos'}_d{d:.3f}", vec(blk, sign * d), f"blk{blk:02d}",
                              "-" if sign < 0 else "+", f"{d:.3f}"))
    rows = []
    for i, (cid, vo, blk, sg, d) in enumerate(conds):
        prefix = f"P3_archerforest_{cid}_krea2_seed{SEED}"
        rows.append({"row": i, "cond": cid, "block": blk, "sign": sg, "dose": d, "seed": SEED, "vectors_override": vo,
                     "prompt_text": b["prompt_text"], "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png",
                     **{k: b[k] for k in ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")}})
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(first):
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    if first:
        rows = rows[:first]
    n = 0
    for r in rows:
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1; print("queued", r["output_prefix"])
    print("queued", n, "of", len(rows))


def repro():
    import numpy as np
    from PIL import Image
    L = lambda p: np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
    new = c47.IMG_ROOT / FOLDER / f"P3_archerforest_baseline_krea2_seed{SEED}_00001_.png"
    old = c47.IMG_ROOT / "benchmark_blk23_colorful" / f"P3_archerforest_baseline_krea2_seed{SEED}_00001_.png"
    d = int(np.abs(L(new) - L(old)).max())
    print("REPRO", "PASS" if d == 0 else "FAIL", f"max abs diff {d}")


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5])


def page():
    import numpy as np
    from PIL import Image
    import hood_watershed as hw
    rng = np.random.default_rng(56)
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    names = {r["cond"]: f"t{k}" for r, k in zip(rows, rng.permutation(np.arange(100, 999))[:len(rows)])}
    order = [names[r["cond"]] for r in rows]; rng.shuffle(order)
    rep = list(rng.choice(order, 8, replace=False))
    show = list(order)
    for x in rep:
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), x)
    with open(PKEY, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["item", "cond", "block", "sign", "dose", "repeated"])
        for r in rows:
            w.writerow([names[r["cond"]], r["cond"], r["block"], r["sign"], r["dose"], int(names[r["cond"]] in rep)])
    imgs = {}
    for r in rows:
        im = Image.open(c47.IMG_ROOT / FOLDER / r["expected_filename"]).convert("RGB")
        imgs[names[r["cond"]]] = [hw.jpg(im.resize((512, 640), Image.LANCZOS)),
                                  hw.jpg(im.crop((112, 0, 912, 800)).resize((640, 640), Image.LANCZOS))]
    html = hw.PAGE.replace("__SLOTS__", json.dumps([f"{s}#{k}" for k, s in enumerate(show)])).replace(
        "__IMG__", json.dumps(imgs)).replace("__LABELS__", json.dumps(hw.LABELS)).replace(
        "cappuccio_v1", "cappuccio_soglia").replace("hood_labels.csv", "hood_threshold_labels.csv")
    out = c47.IMG_ROOT / FOLDER / "hood_test.html"
    out.write_text(html, encoding="utf-8"); print(len(rows), "images,", len(show), "showings ->", out)


def tally(answers):
    key = {r["item"]: r for r in csv.DictReader(open(PKEY))}
    by = {}
    for r in csv.DictReader(open(answers, encoding="utf-8")):
        by.setdefault(r["item"], []).append(r["label"])
    rep = [v for it, v in by.items() if key[it]["repeated"] == "1" and len(v) == 2]
    agree = sum(a == b for a, b in rep)
    print(f"self-agreement {agree}/{len(rep)} ->", "reliable" if agree >= 7 else "UNRELIABLE: no table")
    base = next(by[it][0] for it in key if key[it]["cond"] == "baseline")
    print("baseline:", base)
    content = {(r["block"], s): float(r[c]) for r in csv.DictReader(open(DATA / "atlas_equal_dose_content_change.csv"))
               for s, c in (("-", "neg_1_minus_layout_r"), ("+", "pos_1_minus_layout_r"))}
    out, thr = [], {}
    for blk in [f"blk{b:02d}" for b in BLOCKS]:
        for sg in ("-", "+"):
            labs = []
            for d in [f"{x:.3f}" for x in DOSES]:
                it = next(i for i, k in key.items() if k["block"] == blk and k["sign"] == sg and k["dose"] == d)
                labs.append(by[it][0]); out.append({"block": blk, "sign": sg, "dose": d, "label": by[it][0]})
            t = next((DOSES[i] for i, l in enumerate(labs) if l != "a metà"), None)
            step = t is not None and all(l != "a metà" for l in labs[DOSES.index(t):])
            thr[(blk, sg)] = t
            print(f"{blk} {sg}: " + " | ".join(f"{d}:{l}" for d, l in zip(DOSES, labs)) + f"  -> threshold {t} {'step' if step else ('not a step' if t else '')}")
    with open(DATA / "hood_threshold_tally.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    import numpy as np
    ks = list(thr)
    t = np.array([thr[k] if thr[k] is not None else 1.0 for k in ks]); c = np.array([content[k] for k in ks])
    rk = lambda x: np.argsort(np.argsort(x)).astype(float)
    rho = float(np.corrcoef(rk(t), rk(c))[0, 1])
    print(f"Spearman(threshold, content change) = {rho:+.2f}  (expectation: negative)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "repro", "count", "page", "tally"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0); ap.add_argument("--answers")
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.repro: repro()
    if a.count: count()
    if a.page: page()
    if a.tally: tally(a.answers)
