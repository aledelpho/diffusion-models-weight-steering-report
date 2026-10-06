"""C59 — the split atlas: every block's attention and MLP, apart, both signs (docs/plan_split_atlas.md).
Written 2026-10-06. Exploratory.

  python split_atlas.py --plan              # data/split_atlas_plan.csv (2 checks + 6 baselines + 1008)
  python split_atlas.py --queue --checks    # the 2 check renders only
  python split_atlas.py --check             # REPRO and SPLIT = WHOLE, pixel for pixel
  python split_atlas.py --queue             # everything else, seed 2718281 first
  python split_atlas.py --count             # expected 1016 missing 0
  python split_atlas.py --measure           # data/split_atlas_measures.csv, data/split_atlas_blocks.csv

The three prompts and seed 2718281 of the equal-dose atlas (benchmark_single_blocks_atlas: every whole
block at +-0.35), plus seeds 3141592 and 4669201. Dose +-0.35, Real Value, through granular_json:
  attn = blocks.B.attn.{wq,wk,wv,gate,wo}.weight     mlp = blocks.B.mlp.{gate,up,down}.weight
Renders: Text2Img/benchmark_split_atlas/{prompt}_{cond}_krea2_seed{seed}_00001_.png
  cond: baseline | blkBB_{attn|mlp}_{pos|neg}_d0.350 | CHK_repro_baseline | CHK_all8_blk09_pos_d0.350
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "split_atlas_plan.csv"
ATLAS_PLAN = DATA / "single_blocks_atlas_plan.csv"
ATLAS = "benchmark_single_blocks_atlas/renders"
FOLDER = "benchmark_split_atlas"
PROMPTS = ["P01_blacksmith", "F4_closeup", "S1_rally"]
SEEDS = ["2718281", "3141592", "4669201"]          # 2718281 = the equal-dose atlas seed
DOSE = 0.35
PARTS = {"attn": ["attn.wq", "attn.wk", "attn.wv", "attn.gate", "attn.wo"], "mlp": ["mlp.gate", "mlp.up", "mlp.down"]}
ZERO = ",".join(["0.0"] * 34)


def gj(block, mats, d):
    return json.dumps({f"blocks.{block}.{m}.weight": d for m in mats})


def base_rows():
    rows = {r["prompt_id"]: r for r in csv.DictReader(open(ATLAS_PLAN, encoding="utf-8")) if r["condition"] == "baseline"}
    assert set(PROMPTS) <= set(rows), rows.keys()
    return rows


def make_plan():
    B = base_rows()
    rows = []
    def add(pid, seed, cond, vo, g, phase):
        b = B[pid]; prefix = f"{pid}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "phase": phase, "prompt_id": pid, "seed": seed, "cond": cond, "vectors_override": vo,
                     "granular_json": g, "prompt_text": b["prompt_text"], "output_prefix": prefix,
                     "expected_filename": f"{prefix}_00001_.png",
                     **{k: b[k] for k in ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")}})
    add("P01_blacksmith", "2718281", "CHK_repro_baseline", "", "", "check")
    add("F4_closeup", "2718281", "CHK_all8_blk09_pos_d0.350", ZERO, gj(9, PARTS["attn"] + PARTS["mlp"], DOSE), "check")
    for seed in SEEDS:                                  # seed 2718281 first: usable alone if the night is short
        for pid in PROMPTS:
            if seed != "2718281":
                add(pid, seed, "baseline", "", "", "main")
            for blk in range(28):
                for part, mats in PARTS.items():
                    for sign, d in (("pos", DOSE), ("neg", -DOSE)):
                        add(pid, seed, f"blk{blk:02d}_{part}_{sign}_d{DOSE:.3f}", ZERO, gj(blk, mats, d), "main")
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["granular_json"]:
        wf["50"]["inputs"]["granular_json"] = r["granular_json"]
    return wf


def queue(checks_only):
    n = 0
    for r in csv.DictReader(open(PLAN, encoding="utf-8")):
        if (checks_only and r["phase"] != "check") or (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def _img(p):
    import numpy as np
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def f_split(pid, seed, cond):
    return c47.IMG_ROOT / FOLDER / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"


def f_atlas(pid, cond):
    return c47.IMG_ROOT / ATLAS / f"{pid}_{cond}_krea2_seed2718281_00001_.png"


def f_base(pid, seed):
    return f_atlas(pid, "baseline") if seed == "2718281" else f_split(pid, seed, "baseline")


def check():
    import numpy as np
    a = int(np.abs(_img(f_split("P01_blacksmith", "2718281", "CHK_repro_baseline")) - _img(f_atlas("P01_blacksmith", "baseline"))).max())
    b = int(np.abs(_img(f_split("F4_closeup", "2718281", "CHK_all8_blk09_pos_d0.350")) - _img(f_atlas("F4_closeup", "blk09_pos_d0.350"))).max())
    print(f"REPRO baseline vs equal-dose atlas: max abs diff {a}")
    print(f"SPLIT=WHOLE blk09 +0.35 (eight matrices, granular) vs atlas whole block: max abs diff {b}")
    print("CHECK", "PASS" if a == 0 and b == 0 else "FAIL - stop")


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5])


def measure():
    """Per render against its baseline: fine texture HF (page 05), chroma change and layout r (C47).
    Per block, part and cell: r+, r-, common mode sqrt(r+ r-) and swing r+/r- of HF."""
    import numpy as np
    from PIL import Image, ImageFilter
    from blk23_vs_postproc import lab_small
    def feats(p):
        im = Image.open(p).convert("RGB"); g = im.convert("L")
        hf = float((np.asarray(g, float) - np.asarray(g.filter(ImageFilter.GaussianBlur(1.5)), float)).std())
        L = lab_small(im)
        return hf, float(np.hypot(L[..., 1], L[..., 2]).mean()), L[..., 0].ravel()
    rows, blocks = [], []
    for seed in SEEDS:
        for pid in PROMPTS:
            bp = f_base(pid, seed)
            if not bp.exists():
                continue
            hb, cb, lb = feats(bp)
            for blk in range(28):
                arms = [("attn", lambda s, b=blk: f_split(pid, seed, f"blk{b:02d}_attn_{s}_d0.350")),
                        ("mlp", lambda s, b=blk: f_split(pid, seed, f"blk{b:02d}_mlp_{s}_d0.350"))]
                if seed == "2718281":
                    arms.append(("whole", lambda s, b=blk: f_atlas(pid, f"blk{b:02d}_{s}_d0.350")))
                for part, fn in arms:
                    r = {}
                    for s in ("pos", "neg"):
                        p = fn(s)
                        if not p.exists():
                            break
                        hf, c, l = feats(p)
                        r[s] = hf / hb
                        rows.append({"prompt": pid, "seed": seed, "block": blk, "part": part, "sign": s, "hf_ratio": round(hf / hb, 4),
                                     "d_chroma": round(c - cb, 4), "layout_r": round(float(np.corrcoef(l, lb)[0, 1]), 4)})
                    if len(r) == 2:
                        blocks.append({"prompt": pid, "seed": seed, "block": blk, "part": part, "r_pos": round(r["pos"], 4),
                                       "r_neg": round(r["neg"], 4), "common_mode": round(float(np.sqrt(r["pos"] * r["neg"])), 4),
                                       "swing": round(r["pos"] / r["neg"], 4)})
    for name, data in (("split_atlas_measures.csv", rows), ("split_atlas_blocks.csv", blocks)):
        with open(DATA / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    print(len(rows), "renders measured,", len(blocks), "block-part-cell pairs")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "checks", "check", "count", "measure"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue(a.checks)
    if a.check: check()
    if a.count: count()
    if a.measure: measure()
