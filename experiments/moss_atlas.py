"""MOSS3 - an atlas of MOSS-Image: every DiT block and every text-encoder layer, attention and MLP, doubled and removed
(docs/prereg_moss_atlas.md). Written 2026-10-25 before any render. Authorised by Alessandro ("andiamo con il turbo ...
Facciamo un atlante del model e text encoder?").

  python moss_atlas.py --plan      # data/moss_atlas_plan.csv (committed; do not re-run)
  python moss_atlas.py --queue     # ComfyUI running, MOSS tuner v4, DMD2 LoRA
  python moss_atlas.py --count     # expected 904 missing 0 []
  python moss_atlas.py --analyze   # DINOv2 -> data/moss_atlas_metrics.csv, data/moss_atlas_tests.csv
  python moss_atlas.py --sheets    # Text2Img/_moss_atlas/<prompt>_<dit|te>.jpg

Units (148): DiT layers 0-41 x {attention = proj.o, MLP = proj.ffn_down}; TE layers 0-31 x {MLP = mlp.down_proj,
attention = self_attn.o_proj on the 8 full-attention layers (3, 7, ..., 31), linear_attn.out_proj on the other 24}.
Scaling the output projection scales the whole sublayer's contribution. Doses d = +1 (doubled) and d = -1 (removed).
Three prompts at seed 2718281 (those of the Krea-2 atlases: blacksmith, rally, close-up; amendment 1), T10 (MOSS2 bench settings). Confirmation cells at R50 named in the plan (block "confirm").
"""
import argparse, csv, json, random, statistics, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import moss_gate as G
import moss_bench as B

DATA = HERE.parent / "data"
PLAN, METRICS, TESTS = DATA / "moss_atlas_plan.csv", DATA / "moss_atlas_metrics.csv", DATA / "moss_atlas_tests.csv"
FOLDER = "benchmark_moss_atlas"
B.FOLDER = FOLDER
PROMPTS = ["P01_blacksmith", "S1_rally", "F4_closeup"]   # amendment 1: the prompts and seed of the Krea-2 atlases
SEED = "2718281"
DOSES = {"p": 1.0, "m": -1.0}
FULL_ATTN = set(range(3, 32, 4))


def units():
    u = {}
    for L in range(42):
        u[f"dit{L:02d}_attn"] = ("dit", f"layers.{L}.proj.o.weight")
        u[f"dit{L:02d}_mlp"] = ("dit", f"layers.{L}.proj.ffn_down.weight")
    for L in range(32):
        u[f"te{L:02d}_mlp"] = ("te", f"layers.{L}.mlp.down_proj.weight")
        u[f"te{L:02d}_attn"] = ("te", f"layers.{L}.self_attn.o_proj.weight" if L in FULL_ATTN else f"layers.{L}.linear_attn.out_proj.weight")
    return u


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def make_plan():
    tx = {}
    for r in rd(DATA / "single_blocks_atlas_plan.csv"):
        tx.setdefault(r["prompt_id"], r["prompt_text"])
    U = units(); rows = []
    def add(block, setting, p, cond, te, dit):
        name = f"{setting}_{p}_{cond}_seed{SEED}"
        rows.append({"block": block, "prompt": p, "seed": SEED, "cond": cond, "setting": setting, "te_json": te or "{}",
                     "dit_json": dit or "{}", "name": name, "expected_filename": name + "_00001_.png", "prompt_text": tx[p]})
    for p in PROMPTS:
        add("atlas", "T10", p, "plain", "", "")
        for un, (half, key) in U.items():
            for sg, d in DOSES.items():
                j = json.dumps({key: d})
                add("atlas", "T10", p, f"{un}_{sg}", j if half == "te" else "", j if half == "dit" else "")
    rng = random.Random(31337)                                  # confirmation cells, named before any render
    picks = rng.sample([(un, sg) for un in U for sg in DOSES], 12)
    add("confirm", "R50", "P01_blacksmith", "plain", "", "")
    for un, sg in picks:
        half, key = U[un]; j = json.dumps({key: DOSES[sg]})
        add("confirm", "R50", "P01_blacksmith", f"{un}_{sg}", j if half == "te" else "", j if half == "dit" else "")
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows), "confirm:", [f"{a}_{b}" for a, b in picks])


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


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = G.IMG / FOLDER; rows = rd(PLAN); m = MV.Models(vqa=False)
    V = {r["name"]: np.asarray(m.dino_vec(Image.open(R / r["expected_filename"]).convert("RGB")), dtype=np.float64) for r in rows}
    D = lambda a, b: 1 - float(V[a] @ V[b] / (np.linalg.norm(V[a]) * np.linalg.norm(V[b])))
    met = [{"setting": r["setting"], "prompt": r["prompt"], "cond": r["cond"], "D": round(D(r["name"], f"{r['setting']}_{r['prompt']}_plain_seed{SEED}"), 5)}
           for r in rows if r["cond"] != "plain"]
    Dm = {(x["prompt"], x["cond"]): x["D"] for x in met if x["setting"] == "T10"}
    med = lambda un, sg: statistics.median(Dm[(p, f"{un}_{sg}")] for p in PROMPTS)
    out = []
    for half in ("mlp", "attn"):
        for sg in DOSES:
            ds = [med(f"dit{L:02d}_{half}", sg) for L in range(42)]
            out.append({"test": f"H1 DiT {half} {sg}: depth orders the change (reported if |rho| < 0.5)", "value": f"Spearman layer vs median D {spearman(list(range(42)), ds):+.2f}", "verdict": "ordered" if abs(spearman(list(range(42)), ds)) >= 0.5 else "not ordered"})
            ts = [med(f"te{L:02d}_{half}", sg) for L in range(32)]
            out.append({"test": f"H1 TE {half} {sg}", "value": f"Spearman layer vs median D {spearman(list(range(32)), ts):+.2f}", "verdict": "ordered" if abs(spearman(list(range(32)), ts)) >= 0.5 else "not ordered"})
    for part, n in (("dit", 42), ("te", 32)):
        for sg in DOSES:
            wins = sum(med(f"{part}{L:02d}_mlp", sg) > med(f"{part}{L:02d}_attn", sg) for L in range(n))
            out.append({"test": f"H2 {part} {sg}: MLP moves the picture more than attention", "value": f"{wins} of {n} layers (bar 2/3)", "verdict": "holds" if wins >= 2 * n / 3 else "does not hold"})
    fa = [med(f"te{L:02d}_attn", sg) for L in FULL_ATTN for sg in DOSES]; la = [med(f"te{L:02d}_attn", sg) for L in range(32) if L not in FULL_ATTN for sg in DOSES]
    out.append({"test": "H3 TE full-attention vs linear-attention layers (reported)", "value": f"median D {statistics.median(fa):.3f} vs {statistics.median(la):.3f}", "verdict": "-"})
    top = sorted(((statistics.median(Dm[(p, c)] for p in PROMPTS), c) for c in {c for _, c in Dm}), reverse=True)[:10]
    out.append({"test": "strongest ten units x sign (reported)", "value": "; ".join(f"{c} {v:.3f}" for v, c in top), "verdict": "-"})
    for path, rws in ((METRICS, met), (TESTS, out)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rws[0])); w.writeheader(); w.writerows(rws)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


def sheets():
    from PIL import Image, ImageDraw
    R = G.IMG / FOLDER; out = G.IMG / "_moss_atlas"; out.mkdir(exist_ok=True); W, H, LAB = 128, 160, 70
    cols = [("attn", "p"), ("attn", "m"), ("mlp", "p"), ("mlp", "m")]
    for p in PROMPTS:
        for part, n in (("dit", 42), ("te", 32)):
            S = Image.new("RGB", (LAB + W * 5, H * n), (26, 26, 25)); d = ImageDraw.Draw(S)
            plain = Image.open(R / f"T10_{p}_plain_seed{SEED}_00001_.png").convert("RGB").resize((W, H))
            for L in range(n):
                d.text((4, L * H + H // 2), f"{part} {L}", fill=(230, 230, 230))
                S.paste(plain, (LAB, L * H))
                for k, (h, sg) in enumerate(cols, 1):
                    S.paste(Image.open(R / f"T10_{p}_{part}{L:02d}_{h}_{sg}_seed{SEED}_00001_.png").convert("RGB").resize((W, H)), (LAB + k * W, L * H))
            S.save(out / f"{p}_{part}.jpg", quality=84)
    print("sheets in", out, "- columns: plain, attention x2, attention removed, MLP x2, MLP removed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "count", "analyze", "sheets"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue()
    if a.count: count()
    if a.analyze: analyze()
    if a.sheets: sheets()
