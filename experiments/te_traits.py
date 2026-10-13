"""C75 part B - renders for the trait test (docs/prereg_te_traits.md, amendment 1). Written 2026-10-13, before any
C75 render or label. Renders authorised by Alessandro on 2026-10-13.

  python te_traits.py --plan              # data/te_traits_plan.csv
  python te_traits.py --queue --first 2   # the two gate renders
  python te_traits.py --gate
  python te_traits.py --queue
  python te_traits.py --count
  python te_traits.py --selftest

B0: the three portraits, plain, at the four corpus seeds not yet rendered for them (12 renders; seeds 2645751,
3316624, 3605551 and 4123105 already exist in benchmark_portraits/phase_c).
B1: random pushes of the conditioning (tools/comfyui_krea2_condpush, v2), matched tap by tap to the real push of the
MLP of layer 6, 14 or 28 at d = 0.70, 0.85, 1.00; variants token and permuted; three characters, two seeds
(108 renders). No weight of the image model is edited; the text encoder is edited only to measure the push.
Gate: variant zero must equal the plain portrait, variant real must equal the C74 render, pixel for pixel.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_traits_plan.csv"
FOLDER = "benchmark_te_traits"
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter"]
SEEDS = ["2645751", "3316624"]
SEEDS_B0 = ["1618033", "1234567", "3141592", "2718281"]
LAYERS = [6, 14, 28]
DOSES = [0.70, 0.85, 1.00]
VARIANTS = ["token", "permuted"]
NOISE_SEED = 7
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0", "width": "1024", "height": "1280"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def gj(layer, d):
    return json.dumps({f"layers.{layer}.mlp.{m}_proj.weight": d for m in ("gate", "up", "down")})


def texts():
    t = {}
    for r in rd(DATA / "te_characters_plan.csv"):
        if r["char"] in CHARS and r["char"] not in t:
            t[r["char"]] = r["prompt_text"]
    return t


def make_plan():
    tx = texts(); rows = []
    def add(block, ch, seed, layer="", d=None, variant=""):
        cond = "baseline" if not variant else f"L{layer:02d}_mlp_p{d:.2f}_{variant}"
        prefix = f"{ch}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "block": block, "char": ch, "seed": seed, "layer": layer,
                     "dose": "" if d is None else f"{d:.2f}", "variant": variant, "noise_seed": NOISE_SEED if variant else "",
                     "te_granular_json": gj(layer, d) if variant else "", "cond": cond, "prompt_text": tx[ch],
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    add("gate", CHARS[0], SEEDS[0], 6, 0.85, "zero")
    add("gate", CHARS[0], SEEDS[0], 6, 0.85, "real")
    for ch in CHARS:
        for s in SEEDS_B0:
            add("B0", ch, s)
    for layer in LAYERS:
        for ch in CHARS:
            for s in SEEDS:
                for d in DOSES:
                    for v in VARIANTS:
                        add("B1", ch, s, layer, d, v)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("plan rows:", len(rows), dict(Counter(r["block"] for r in rows)))


def workflow(r):
    wf = TP.workflow({**r, "te_granular_json": "", "vectors_override": ""})     # plain CLIP on node 40
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["variant"]:
        wf["51"] = {"class_type": "ArthemyKrea2CLIPTuner", "inputs": {
            "clip": ["37", 1], "mode": "Real Value", "vectors_override": "", "granular_json": r["te_granular_json"],
            "Embedding": 0.0, "Layer_1": 0.0, "Layer_2": 0.0, "Layer_3": 0.0, "Layer_4": 0.0, "Layer_5": 0.0,
            "Layer_6": 0.0, "Layer_7": 0.0}}
        wf["94"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": ["51", 0], "text": r["prompt_text"]}}
        wf["93"] = {"class_type": "Krea2ConditioningPush", "inputs": {
            "conditioning": ["40", 0], "conditioning_edit": ["94", 0], "variant": r["variant"],
            "noise_seed": int(r["noise_seed"])}}
        wf["42"]["inputs"]["positive"] = ["93", 0]
    return wf


def queue(first):
    n = 0
    for r in rd(PLAN)[: first or None]:
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def _im(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def gate():
    g = [r for r in rd(PLAN) if r["block"] == "gate"]
    ch, s = g[0]["char"], g[0]["seed"]
    base = _im(c47.IMG_ROOT / "benchmark_portraits" / "phase_c" / f"{ch}_baseline_krea2_seed{s}_00001_.png")
    edit = _im(c47.IMG_ROOT / "benchmark_te_dose" / f"{ch}_L06_mlp_p0.85_krea2_seed{s}_00001_.png")
    dz = int(np.abs(_im(c47.IMG_ROOT / FOLDER / g[0]["expected_filename"]) - base).max())
    dr = int(np.abs(_im(c47.IMG_ROOT / FOLDER / g[1]["expected_filename"]) - edit).max())
    print("zero push vs plain portrait: max abs diff", dz)
    print("real push L06 d=0.85 vs C74 render: max abs diff", dr)
    print("GATE", "PASS" if dz == 0 and dr == 0 else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def selftest():
    assert len(texts()) == 3
    assert json.loads(gj(28, 0.85))["layers.28.mlp.down_proj.weight"] == 0.85
    r = {"row": 0, "block": "B1", "char": CHARS[0], "seed": SEEDS[0], "layer": 6, "dose": "0.70", "variant": "token",
         "noise_seed": 7, "te_granular_json": gj(6, 0.70), "cond": "x", "prompt_text": texts()[CHARS[0]],
         "output_prefix": "x", "expected_filename": "x_00001_.png", **SET}
    wf = workflow(r)
    assert wf["42"]["inputs"]["positive"] == ["93", 0] and wf["93"]["inputs"]["variant"] == "token"
    assert wf["40"]["inputs"]["clip"] != ["51", 0]
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "gate", "count", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.gate: gate()
    if a.count: count()
    if a.selftest: selftest()
