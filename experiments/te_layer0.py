"""C77 - does switching off half of text-encoder layer 0 make Krea-2 write the prompt as text on other prompts?
Replication of the C64 pilot observation (one prompt, one seed). Written 2026-10-14, before any C77 render.
Renders authorised by Alessandro on 2026-10-14 ("prendi tre prompt ... solo quel seed con quel peso").

  python te_layer0.py --plan             # data/te_layer0_plan.csv
  python te_layer0.py --queue --first 1  # the gate: the C64 elf, layer 0 MLP x 0, re-rendered
  python te_layer0.py --gate             # must equal the C64 render pixel for pixel
  python te_layer0.py --queue
  python te_layer0.py --count

Rule, fixed now (pre-registration, short): a picture "writes the prompt" if it is mostly text and at least one
readable fragment of a word of its own prompt can be pointed to. Prediction: 6 of 6. Reported as k of 6; the claim
holds if at least 5 of 6, fails if 3 or fewer, open otherwise. Judged by Alessandro (not blind: the case is extreme).
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_layer0_plan.csv"
FOLDER = "benchmark_te_layer0"
SEED = "1618033"
CHARS = ["D1_dwarf_paladin", "R6_dragonborn_cleric", "D1W_dwarf_paladin_watercolor"]
EDITS = {
    "L00_mlp_m1.00": {"layers.0.mlp.gate_proj.weight": -1.0, "layers.0.mlp.up_proj.weight": -1.0,
                      "layers.0.mlp.down_proj.weight": -1.0},
    "L00_attn_m1.00": {"layers.0.self_attn.q_proj.weight": -1.0, "layers.0.self_attn.k_proj.weight": -1.0,
                       "layers.0.self_attn.v_proj.weight": -1.0, "layers.0.self_attn.o_proj.weight": -1.0},
}
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
       "width": "1024", "height": "1280"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def make_plan():
    tx = {}
    for r in rd(DATA / "te_characters_plan.csv"):
        tx.setdefault(r["char"], r["prompt_text"])
    pilot = [r for r in rd(DATA / "te_pilot_plan.csv") if r["cond"] == "L00_mlp_m1.00"][0]
    rows = []
    def add(block, ch, cond, text):
        prefix = f"{ch}_{cond}_krea2_seed{SEED}"
        rows.append({"row": len(rows), "block": block, "char": ch, "cond": cond,
                     "te_granular_json": json.dumps(EDITS[cond]), "prompt_text": text, "seed": SEED,
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    add("gate", "P1_elfbrawler", "L00_mlp_m1.00", pilot["prompt_text"])
    for ch in CHARS:
        for cond in EDITS:
            add("A", ch, cond, tx[ch])
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
    old = c47.IMG_ROOT / "benchmark_te_pilot" / "P1_elfbrawler_L00_mlp_m1.00_krea2_seed1618033_00001_.png"
    d = int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(old)).max())
    print("re-rendered C64 layer-0 picture vs existing: max abs diff", d)
    print("GATE", "PASS" if d == 0 else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "gate", "count"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.gate: gate()
    if a.count: count()
