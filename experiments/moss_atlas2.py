"""MOSS3b - confirmations at 50 steps and follow-ups of the MOSS atlas (docs/prereg_moss_atlas2.md). Written 2026-10-26
before any render. Authorised by Alessandro ("Abbiamo tre ore di render che possiamo spendere").

  python moss_atlas2.py --plan      # data/moss_atlas2_plan.csv (committed; do not re-run)
  python moss_atlas2.py --queue     # ComfyUI running, MOSS tuner v4, DMD2 LoRA
  python moss_atlas2.py --count     # expected 160 missing 0 []
  python moss_atlas2.py --analyze   # data/moss_atlas2_metrics.csv, data/moss_atlas2_tests.csv
  (the blind confirmation page is written by Claude after the renders, as in MOSS2)

Blocks:
  A  confirm   R50, blacksmith at 2718281: plain + the 12 cells drawn in MOSS3 (seed 31337)              13
  A' targeted  R50, blacksmith: te00_attn_pp, dit24_mlp_pp, dit32_attn_m (findings named after looking)   3
  B  stacks    T10, 3 prompts: all TE layers 1-31 at once - MLP +1, MLP +0.5, MLP -0.5, attention +1      12
  C  embedder  T10, 3 prompts: DiT text_embedder blocks 0, 1 x {attention proj, ffn_down} x {+1, +2, -1}    36
  D  seed2     T10, blacksmith at 3141592: plain, DiT MLP +2 all 42 layers, TE attention removed all 32  75
  E  seed2 bis T10, blacksmith at 3141592: DiT MLP removed, blocks 0, 4, ..., 24 and 28-41                21
"""
import argparse, csv, json, statistics, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import moss_gate as G
import moss_bench as B
import moss_atlas as A

DATA = HERE.parent / "data"
PLAN, METRICS, TESTS = DATA / "moss_atlas2_plan.csv", DATA / "moss_atlas2_metrics.csv", DATA / "moss_atlas2_tests.csv"
KEY, LAB = DATA / "moss_atlas2_confirm_key.csv", DATA / "moss_atlas2_confirm_labels.csv"
FOLDER = "benchmark_moss_atlas2"
B.FOLDER = FOLDER
CONFIRM = ['te22_attn_p', 'dit21_mlp_m', 'dit38_mlp_p', 'dit07_attn_p', 'dit26_attn_p', 'dit23_attn_p', 'dit40_attn_m',
           'dit13_mlp_p', 'te29_mlp_p', 'te12_mlp_m', 'te00_mlp_p', 'te00_attn_m']
TARGETED = ['te00_attn_pp', 'dit24_mlp_pp', 'dit32_attn_m']
SEED, SEED2 = "2718281", "3141592"
DOSE = {"p": 1.0, "m": -1.0, "pp": 2.0}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def texts():
    tx = {}
    for r in rd(DATA / "single_blocks_atlas_plan.csv"):
        tx.setdefault(r["prompt_id"], r["prompt_text"])
    return tx


def cell(c):
    un, sg = c.rsplit("_", 1); half, key = A.units()[un]
    return half, {key: DOSE[sg]}


def make_plan():
    tx = texts(); rows = []
    def add(block, setting, p, seed, cond, te, dit):
        name = f"{setting}_{p}_{cond}_seed{seed}"
        rows.append({"block": block, "prompt": p, "seed": seed, "cond": cond, "setting": setting,
                     "te_json": json.dumps(te) if te else "{}", "dit_json": json.dumps(dit) if dit else "{}",
                     "name": name, "expected_filename": name + "_00001_.png", "prompt_text": tx[p]})
    bs = "P01_blacksmith"
    # A, A': R50 confirmations
    add("confirm", "R50", bs, SEED, "plain", None, None)
    for blk, cells in (("confirm", CONFIRM), ("targeted", TARGETED)):
        for c in cells:
            half, j = cell(c); add(blk, "R50", bs, SEED, c, j if half == "te" else None, j if half == "dit" else None)
    # B: text-encoder stacks
    stacks = {"te_all_mlp_p": {f"layers.{L}.mlp.down_proj.weight": 1.0 for L in range(1, 32)},
              "te_all_mlp_p0.5": {f"layers.{L}.mlp.down_proj.weight": 0.5 for L in range(1, 32)},
              "te_all_mlp_m0.5": {f"layers.{L}.mlp.down_proj.weight": -0.5 for L in range(1, 32)},
              "te_all_attn_p": {A.units()[f"te{L:02d}_attn"][1]: 1.0 for L in range(1, 32)}}
    for p in A.PROMPTS:
        for n, j in stacks.items():
            add("stacks", "T10", p, SEED, n.replace(".", "p"), j, None)
    # C: the DiT's text embedder
    for p in A.PROMPTS:
        for b in (0, 1):
            for part, key in (("attn", f"text_embedder.blocks.{b}.proj.weight"), ("mlp", f"text_embedder.blocks.{b}.ffn_down.weight")):
                for sg, d in DOSE.items():
                    add("embedder", "T10", p, SEED, f"temb{b}_{part}_{sg}", None, {key: d})
    # D: second seed, the two ordered columns
    add("seed2", "T10", bs, SEED2, "plain", None, None)
    for L in range(42):
        add("seed2", "T10", bs, SEED2, f"dit{L:02d}_mlp_pp", None, {f"layers.{L}.proj.ffn_down.weight": 2.0})
    for L in range(32):
        add("seed2", "T10", bs, SEED2, f"te{L:02d}_attn_m", {A.units()[f"te{L:02d}_attn"][1]: -1.0}, None)
    # E: second seed, DiT MLP removed (the other ordered column), last 14 blocks and every 4th earlier block
    for L in sorted(set(range(0, 28, 4)) | set(range(28, 42))):
        add("seed2", "T10", bs, SEED2, f"dit{L:02d}_mlp_m", None, {f"layers.{L}.proj.ffn_down.weight": -1.0})
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def queue():
    n = 0
    for r in rd(PLAN):
        if (G.IMG / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{G.URL}/prompt", data=json.dumps({"prompt": B.workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10).read(); n += 1
    print("queued", n)


def count():
    rows = rd(PLAN); miss = [r["expected_filename"] for r in rows if not (G.IMG / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = G.IMG / FOLDER; rows = rd(PLAN); m = MV.Models(vqa=False)
    V = {r["name"]: np.asarray(m.dino_vec(Image.open(R / r["expected_filename"]).convert("RGB")), dtype=np.float64) for r in rows}
    atlas = {}                                                       # MOSS3 T10 pictures for the comparisons
    Ra = G.IMG / A.FOLDER
    for r in rd(A.PLAN):
        atlas[r["name"]] = Ra / r["expected_filename"]
    def vec(name):
        if name not in V:
            V[name] = np.asarray(m.dino_vec(Image.open(atlas[name]).convert("RGB")), dtype=np.float64)
        return V[name]
    D = lambda a, b: 1 - float(vec(a) @ vec(b) / (np.linalg.norm(vec(a)) * np.linalg.norm(vec(b))))
    met = [{"block": r["block"], "setting": r["setting"], "prompt": r["prompt"], "seed": r["seed"], "cond": r["cond"],
            "D": round(D(r["name"], f"{r['setting']}_{r['prompt']}_plain_seed{r['seed']}"), 5)} for r in rows if r["cond"] != "plain"]
    out = []
    # A: T10 against R50 distances for the confirmation cells (the blind check is the rule)
    for c in CONFIRM + TARGETED:
        out.append({"test": f"A {c} (reported)", "value": f"D R50 {D(f'R50_P01_blacksmith_{c}_seed{SEED}', f'R50_P01_blacksmith_plain_seed{SEED}'):.3f} / T10 {D(f'T10_P01_blacksmith_{c}_seed{SEED}', f'T10_P01_blacksmith_plain_seed{SEED}'):.3f}", "verdict": "-"})
    out.append({"test": "A style: R50 plain against T10 plain, blacksmith (reported)", "value": f"D {D(f'R50_P01_blacksmith_plain_seed{SEED}', f'T10_P01_blacksmith_plain_seed{SEED}'):.3f}", "verdict": "-"})
    # B: stacks against single TE layers
    single = statistics.median(D(f"T10_{p}_te{L:02d}_mlp_p_seed{SEED}", f"T10_{p}_plain_seed{SEED}") for p in A.PROMPTS for L in range(1, 32))
    for n in ("te_all_mlp_p", "te_all_mlp_p0p5", "te_all_mlp_m0p5", "te_all_attn_p"):
        v = statistics.median(x["D"] for x in met if x["cond"] == n)
        out.append({"test": f"B {n}", "value": f"median D {v:.3f} vs single TE MLP +1 {single:.3f}", "verdict": "additive (>= 3x)" if v >= 3 * single else "not additive"})
    # C: embedder against DiT blocks
    dit = statistics.median(D(f"T10_{p}_dit{L:02d}_{h}_{s}_seed{SEED}", f"T10_{p}_plain_seed{SEED}") for p in A.PROMPTS for L in range(42) for h in ("attn", "mlp") for s in ("p", "m", "pp"))
    emb = [x["D"] for x in met if x["block"] == "embedder"]
    out.append({"test": "C text embedder vs DiT blocks (reported)", "value": f"median D {statistics.median(emb):.3f} vs {dit:.3f}; max {max(emb):.3f}", "verdict": "-"})
    # D, E: second seed
    for col, n in (("mlp_pp", 42), ("attn_m", 32)):
        part = "dit" if col == "mlp_pp" else "te"
        a = [D(f"T10_P01_blacksmith_{part}{L:02d}_{col}_seed{SEED2}", f"T10_P01_blacksmith_plain_seed{SEED2}") for L in range(n)]
        b = [D(f"T10_P01_blacksmith_{part}{L:02d}_{col}_seed{SEED}", f"T10_P01_blacksmith_plain_seed{SEED}") for L in range(n)]
        rho_d = A.spearman(list(range(n)), a); rho_s = A.spearman(a, b)
        out.append({"test": f"D {part} {col} at seed {SEED2}", "value": f"Spearman with depth {rho_d:+.2f}; with seed {SEED} per layer {rho_s:+.2f}",
                    "verdict": "replicated" if abs(rho_d) >= 0.5 and rho_s >= 0.5 else "not replicated"})
    for path, rws in ((METRICS, met), (TESTS, out)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rws[0])); w.writeheader(); w.writerows(rws)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "count", "analyze"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue()
    if a.count: count()
    if a.analyze: analyze()
