"""C74 - dose ladder for three text-encoder edits with a clear destination (docs/prereg_te_dose.md). Written
2026-10-13, before any C74 render. Renders authorised by Alessandro on 2026-10-13.

  python te_dose.py --plan              # data/te_dose_plan.csv
  python te_dose.py --queue --first 1   # gate: L06 at d = 1.00 re-rendered, must equal the C65 render
  python te_dose.py --gate
  python te_dose.py --queue
  python te_dose.py --count
  python te_dose.py --selftest

Edits: the MLP of layer 6, 14 or 28 of the text encoder, every matrix (gate, up, down) scaled by (1 + d),
d in {0.10, 0.25, 0.50, 0.75} and, after amendment 1, {0.40, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95}; d = 1.00 is the existing C65 render. Three characters, two seeds.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_dose_plan.csv"
FOLDER = "benchmark_te_dose"
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter"]
SEEDS = ["2645751", "3316624"]
LAYERS = [6, 14, 28]
DOSES = [0.10, 0.25, 0.50, 0.75]
DOSES_A1 = [0.40, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]   # amendment 1 (2026-10-13): finer steps, mostly at high doses
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


def c65_path(ch, layer, seed):
    return c47.IMG_ROOT / "benchmark_te_characters" / f"{ch}_L{layer:02d}_mlp_p1.00_krea2_seed{seed}_00001_.png"


def make_plan():
    tx = texts(); rows = []
    ref = [r for r in rd(DATA / "te_characters_plan.csv") if r["char"] == CHARS[0] and r["cond"] == "L06_mlp_p1.00"][0]
    assert json.loads(ref["te_granular_json"]) == json.loads(gj(6, 1.0))
    def add(block, ch, layer, d, seed):
        cond = f"L{layer:02d}_mlp_p{d:.2f}"
        prefix = f"{ch}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "block": block, "char": ch, "layer": layer, "dose": f"{d:.2f}", "cond": cond,
                     "te_granular_json": gj(layer, d), "prompt_text": tx[ch], "seed": seed,
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    add("gate", CHARS[0], 6, 1.0, SEEDS[0])
    for layer in LAYERS:
        for ch in CHARS:
            for s in SEEDS:
                for d in DOSES:
                    add("ladder", ch, layer, d, s)
    for layer in LAYERS:                      # amendment 1: appended, so the original rows keep their order
        for ch in CHARS:
            for s in SEEDS:
                for d in DOSES_A1:
                    add("ladder_a1", ch, layer, d, s)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = TP.workflow({**r, "vectors_override": ""})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
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
    r = rd(PLAN)[0]
    d = int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(c65_path(r["char"], int(r["layer"]), r["seed"]))).max())
    print("L06 MLP d=1.00 re-rendered vs C65 render: max abs diff", d)
    print("GATE", "PASS" if d == 0 else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def selftest():
    assert json.loads(gj(14, 0.25)) == {"layers.14.mlp.gate_proj.weight": 0.25, "layers.14.mlp.up_proj.weight": 0.25, "layers.14.mlp.down_proj.weight": 0.25}
    assert len(texts()) == 3
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
