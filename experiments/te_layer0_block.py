"""C77 exploration — whole-block ablation of text-encoder Layer 0 (both Attention and MLP x 0).
Requested by Alessandro on 2026-10-14.

  python te_layer0_block.py --plan
  python te_layer0_block.py --queue
  python te_layer0_block.py --count
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_layer0_block_plan.csv"
FOLDER = "benchmark_te_layer0_block"
SEED = "1618033"
CHARS = ["P1_elfbrawler", "D1_dwarf_paladin", "R6_dragonborn_cleric", "D1W_dwarf_paladin_watercolor"]

EDIT_L00_BLOCK = {
    "layers.0.self_attn.q_proj.weight": -1.0,
    "layers.0.self_attn.k_proj.weight": -1.0,
    "layers.0.self_attn.v_proj.weight": -1.0,
    "layers.0.self_attn.o_proj.weight": -1.0,
    "layers.0.mlp.gate_proj.weight": -1.0,
    "layers.0.mlp.up_proj.weight": -1.0,
    "layers.0.mlp.down_proj.weight": -1.0,
}

SET = {
    "sampler": "euler_ancestral",
    "scheduler": "simple",
    "steps": "9",
    "cfg": "1.0",
    "denoise": "1.0",
    "width": "1024",
    "height": "1280",
}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def make_plan():
    tx = {}
    for r in rd(DATA / "te_characters_plan.csv"):
        tx.setdefault(r["char"], r["prompt_text"])
    pilot = [r for r in rd(DATA / "te_pilot_plan.csv") if r["cond"] == "L00_mlp_m1.00"][0]
    tx["P1_elfbrawler"] = pilot["prompt_text"]

    rows = []
    for ch in CHARS:
        prefix = f"{ch}_L00_block_m1.00_krea2_seed{SEED}"
        rows.append({
            "row": len(rows),
            "char": ch,
            "cond": "L00_block_m1.00",
            "te_granular_json": json.dumps(EDIT_L00_BLOCK),
            "prompt_text": tx[ch],
            "seed": SEED,
            "output_prefix": prefix,
            "expected_filename": f"{prefix}_00001_.png",
            **SET,
        })
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = TP.workflow({**r, "vectors_override": ""})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue():
    n = 0
    for r in rd(PLAN):
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(
            f"{c47.COMFY}/prompt",
            data=json.dumps({"prompt": workflow(r)}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "count"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.plan:
        make_plan()
    if a.queue:
        queue()
    if a.count:
        count()
