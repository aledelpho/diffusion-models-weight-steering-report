"""C55 — is the tuner clean when it is active? (docs/prereg_null_patch.md). Written 2026-10-06.

  python null_patch.py --plan            # data/null_patch_plan.csv (5 rows)
  python null_patch.py --queue           # queue the 5 renders (skips files that exist)
  python null_patch.py --check           # N0 against the existing baseline, N1 against N0 (the decisive test)
  python null_patch.py --page            # blind hood labels for N2-N4 (C54 labels), no names

Renders: Text2Img/benchmark_null_patch/P3_archerforest_<id>_krea2_seed3141592_00001_.png
Workflow and prompt identical to C47 (blk23_colorful.workflow); only the tuner input changes.
"""
import argparse, csv, json, os, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "null_patch_plan.csv"
FOLDER = "benchmark_null_patch"
SEED = "3141592"
MATRICES = ["attn.gate", "attn.wq", "attn.wk", "attn.wv", "attn.wo", "mlp.gate", "mlp.up", "mlp.down"]
NULL_JSON = json.dumps({f"blocks.27.{m}.weight": 0.0001 for m in MATRICES})
ZERO = ",".join(["0.0"] * 34)


def vec27(d):
    v = ["0.0"] * 34
    v[27] = repr(float(d))           # full precision: c47.vector() would print 0.0001 as 0.000
    return ",".join(v)


ROWS = [  # id, vectors_override, granular_json, what changes
    ("N0_baseline", "", "", "nothing: no tuner node (re-render of the C47 baseline, same session)"),
    ("N1_null", ZERO, NULL_JSON, "nothing: the 8 bf16 matrices of block 27 x1.0001 round back to themselves"),
    ("N2_blk27_p0.0001", vec27(0.0001), "", "only the float32 scales and mod.lin of block 27, by 1e-4"),
    ("N3_blk27_p0.004", vec27(0.004), "", "every weight of block 27 by ~one bf16 step"),
    ("N4_blk27_m0.004", vec27(-0.004), "", "same, other sign"),
]


def make_plan():
    b = [r for r in csv.DictReader(open(c47.PLAN, encoding="utf-8"))
         if r["prompt_id"] == "P3_archerforest" and r["seed"] == SEED and r["cond"] == "baseline"][0]
    rows = []
    for i, (cid, vo, gj, what) in enumerate(ROWS):
        prefix = f"P3_archerforest_{cid}_krea2_seed{SEED}"
        rows.append({"row": i, "id": cid, "seed": SEED, "vectors_override": vo, "granular_json": gj, "changes": what,
                     "prompt_text": b["prompt_text"], "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png",
                     **{k: b[k] for k in ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")}})
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = c47.workflow(r)                       # node 50 (tuner) present iff vectors_override is non-empty
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["granular_json"]:
        wf["50"]["inputs"]["granular_json"] = r["granular_json"]
    return wf


def queue():
    for r in csv.DictReader(open(PLAN, encoding="utf-8")):
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        print("queued", r["output_prefix"])


def check():
    import numpy as np
    from PIL import Image
    load = lambda p: np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
    f = lambda cid: c47.IMG_ROOT / FOLDER / f"P3_archerforest_{cid}_krea2_seed{SEED}_00001_.png"
    old = c47.IMG_ROOT / "benchmark_blk23_colorful" / f"P3_archerforest_baseline_krea2_seed{SEED}_00001_.png"
    n0, n1 = load(f("N0_baseline")), load(f("N1_null"))
    d0 = int(np.abs(n0 - load(old)).max())
    print(f"N0 re-render vs C47 baseline: max abs diff {d0} -> {'REPRO PASS' if d0 == 0 else 'REPRO FAIL: stop, the session is not reproducible'}")
    d1 = np.abs(n1 - n0)
    print(f"N1 null patch vs N0: max abs diff {int(d1.max())}, pixels differing {100 * float((d1.max(-1) > 0).mean()):.3f}%")
    print("C55 VERDICT:", "CLEAN - the active node adds nothing beyond the multiplication" if d0 == 0 and d1.max() == 0
          else "NOT CLEAN - the active node or the patch path adds something" if d0 == 0 else "VOID (repro failed)")


def page():
    """N2-N4 for blind hood labels, mixed with N0 and N1, order shuffled, no names (C54 labels)."""
    import base64, io, numpy as np
    from PIL import Image
    import hood_watershed as hw
    rng = np.random.default_rng(55)
    ids = [r[0] for r in ROWS]
    names = {cid: f"n{k}" for k, cid in zip(rng.permutation(np.arange(100, 999))[:len(ids)], ids)}
    order = [names[c] for c in ids]; rng.shuffle(order)
    imgs = {}
    for cid in ids:
        im = Image.open(c47.IMG_ROOT / FOLDER / f"P3_archerforest_{cid}_krea2_seed{SEED}_00001_.png").convert("RGB")
        imgs[names[cid]] = [hw.jpg(im.resize((512, 640), Image.LANCZOS)), hw.jpg(im.crop((112, 0, 912, 800)).resize((640, 640), Image.LANCZOS))]
    with open(DATA / "null_patch_page_key.csv", "w", newline="") as fh:
        fh.write("item,id\n"); [fh.write(f"{names[c]},{c}\n") for c in ids]
    html = hw.PAGE.replace("__SLOTS__", json.dumps([f"{s}#{k}" for k, s in enumerate(order)])).replace(
        "__IMG__", json.dumps(imgs)).replace("__LABELS__", json.dumps(hw.LABELS)).replace("cappuccio_v1", "cappuccio_null").replace(
        "cappuccio_v2", "cappuccio_null").replace("hood_labels.csv", "null_patch_hood_labels.csv")
    out = c47.IMG_ROOT / FOLDER / "hood_test.html"
    out.write_text(html, encoding="utf-8"); print("page ->", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "check", "page"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue()
    if a.check: check()
    if a.page: page()
