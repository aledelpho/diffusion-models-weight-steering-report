"""MOSS2 - the MOSS bench: reproducibility, a clean active tuner, the seed floor and a first sensitivity ladder
(docs/prereg_moss_bench.md). Written 2026-10-25 before any MOSS2 render. Renders authorised by Alessandro ("Procediamo").

  python moss_bench.py --plan       # data/moss_bench_plan.csv (committed; do not re-run)
  python moss_bench.py --queue      # ComfyUI running, MOSS tuner v3 installed
  python moss_bench.py --count      # expected 84 missing 0 []
  python moss_bench.py --analyze    # V1, V2 pixel checks; DINOv2 -> data/moss_bench_metrics.csv; data/moss_bench_tests.csv

Amendment 2 (2026-10-25, before any render): working setting T10 (DMD2 LoRA, euler, 10 steps, CFG 1), chosen by
MOSS-S2 (S2 pass, Spearman 0.86); ladder doses 0.10, 0.30, 1.00, 2.00; the euler_ancestral block dropped (MOSS-S2 tested
it); seven confirmation renders at R50 named now. Amendment 1 (2026-10-25, before any render was kept): sampling euler, simple, 50 steps, CFG 3 (the official setting and
Alessandro's best pictures), 1024 x 1280, no SLG, no prompt enhancer; plus euler_ancestral (Krea-2's sampler) on the
floor prompts at two seeds, to see whether one sampler can serve both models. V1 is now two identical renders in one
session (plain_repro against the floor render). Every render goes through both MOSS tuners (non-dynamic route), "{}" when unedited, so
plain and edited pictures share one route.
"""
import argparse, csv, json, statistics, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import moss_gate as G

DATA = HERE.parent / "data"
PLAN, METRICS, TESTS = DATA / "moss_bench_plan.csv", DATA / "moss_bench_metrics.csv", DATA / "moss_bench_tests.csv"
FOLDER = "benchmark_moss_bench"
PROMPTS = ["D1_dwarf_paladin", "S1_rally", "C4_stilllife", "P5_comic_panels", "P2_lotuscanoe", "LN"]
SEEDS = ["2645751", "3316624", "2718281", "1618033"]
LADDER_PROMPTS = ["D1_dwarf_paladin", "S1_rally"]
DOSES = [0.10, 0.30, 1.00, 2.00]          # amendment 2: MOSS-S2 showed d <= 0.30 barely moves MOSS
LORA = "Moss\\lodestones-8-steps-dmd2-lora.safetensors"
SETTINGS = {"T10": ("euler", 10, 1.0, True), "R50": ("euler", 50, 3.0, False)}   # amendment 2
EDITS = {"dit06": ("dit", "layers.6.proj.ffn_down.weight"), "dit20": ("dit", "layers.20.proj.ffn_down.weight"),
         "dit35": ("dit", "layers.35.proj.ffn_down.weight"), "te06": ("te", "layers.6.mlp.down_proj.weight"),
         "te15": ("te", "layers.15.mlp.down_proj.weight"), "te27": ("te", "layers.27.mlp.down_proj.weight")}
NULL_DIT = {f"layers.41.proj.{m}.weight": 0.0001 for m in ("qkv", "o", "ffn_up_gate", "ffn_down")}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def texts():
    import te_shapes2 as TS2
    return TS2.texts()


def make_plan():
    tx = texts(); rows = []
    def add(block, p, s, cond, te, dit, setting="T10"):
        name = f"{setting}_{p}_{cond}_seed{s}"
        rows.append({"block": block, "prompt": p, "seed": s, "cond": cond, "setting": setting, "te_json": te or "{}", "dit_json": dit or "{}",
                     "name": name, "expected_filename": f"{name}_00001_.png", "prompt_text": tx[p]})
    # = the floor render of the dwarf at 2645751; a zero-dose JSON (parsed to no edit) makes the graph differ, so ComfyUI
    # cannot serve it from its cache and the picture is really computed twice
    add("V1", "D1_dwarf_paladin", "2645751", "plain_repro", "", json.dumps({"layers.0.proj.o.weight": 0.0}))
    for p in PROMPTS:
        for s in SEEDS:
            add("floor", p, s, "plain", "", "")
    for p in ("D1_dwarf_paladin", "S1_rally"):
        add("V2", p, "2645751", "null_dit41_x1.0001", "", json.dumps(NULL_DIT))
        add("V2r", p, "2645751", "te31_x1.0001", json.dumps({"layers.31.mlp.down_proj.weight": 0.0001}), "")
    for p in LADDER_PROMPTS:
        for e, (half, key) in EDITS.items():
            for d in DOSES:
                j = json.dumps({key: d})
                add("ladder", p, "2645751", f"{e}_p{d:g}".replace(".", "p"), j if half == "te" else "", j if half == "dit" else "")
    # confirmation cells named now (amendment 2): the dwarf plain and its six edits at d = 1.0, at R50
    add("confirm", "D1_dwarf_paladin", "2645751", "plain", "", "", "R50")
    for e, (half, key) in EDITS.items():
        j = json.dumps({key: 1.0})
        add("confirm", "D1_dwarf_paladin", "2645751", f"{e}_p1", j if half == "te" else "", j if half == "dit" else "", "R50")
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    G.PROMPT = r["prompt_text"]; G.SEED = int(r["seed"]); G.FOLDER = FOLDER
    sampler, steps, cfg, lora = SETTINGS[r["setting"]]
    G.SAMPLER, G.STEPS, G.CFG = sampler, steps, cfg
    wf = G.workflow(r["name"], r["te_json"], r["dit_json"])
    if lora:
        wf["12"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": LORA, "strength_model": 1.0}}
        wf["11"]["inputs"]["model"] = ["12", 0]
    return wf


def queue():
    n = 0
    for r in rd(PLAN):
        if (G.IMG / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{G.URL}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10).read(); n += 1
    print("queued", n)


def count():
    rows = rd(PLAN); miss = [r["expected_filename"] for r in rows if not (G.IMG / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = G.IMG / FOLDER; rows = rd(PLAN)
    px = lambda f: np.asarray(Image.open(f).convert("RGB"), dtype=np.int16)
    out = []
    a = px(R / "T10_D1_dwarf_paladin_plain_repro_seed2645751_00001_.png"); b = px(R / "T10_D1_dwarf_paladin_plain_seed2645751_00001_.png")
    v1 = int(np.abs(a - b).max()); out.append({"test": "V1 the dwarf rendered twice in one session", "value": f"max {v1}", "verdict": "PASS" if v1 == 0 else "FAIL"})
    for p in ("D1_dwarf_paladin", "S1_rally"):
        base = px(R / f"T10_{p}_plain_seed2645751_00001_.png")
        n = int(np.abs(px(R / f"T10_{p}_null_dit41_x1.0001_seed2645751_00001_.png") - base).max())
        t = np.abs(px(R / f"T10_{p}_te31_x1.0001_seed2645751_00001_.png") - base)
        out.append({"test": f"V2 DiT layer 41 x 1.0001 ({p})", "value": f"max {n}", "verdict": "PASS" if n == 0 else "reported: bf16 rounding moved"})
        out.append({"test": f"V2r TE layer 31 MLP down x 1.0001 ({p}), reported", "value": f"max {int(t.max())}, changed pixels {float((t.max(-1) > 0).mean()):.3f}", "verdict": "-"})
    m = MV.Models(vqa=False); V = {}
    vec = lambda f: np.asarray(m.dino_vec(Image.open(f).convert("RGB")), dtype=np.float64)
    cos = lambda u, v: float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v)))
    for r in rows:
        V[r["name"]] = vec(R / r["expected_filename"])
    met = []
    for p in PROMPTS:
        ds = []
        for i, s in enumerate(SEEDS):
            for t in SEEDS[i + 1:]:
                d = 1 - cos(V[f"T10_{p}_plain_seed{s}"], V[f"T10_{p}_plain_seed{t}"]); ds.append(d)
                met.append({"block": "floor", "prompt": p, "cond": f"seed{s}_vs_seed{t}", "D": round(d, 5)})
        out.append({"test": f"floor {p}", "value": f"median D between seeds {statistics.median(ds):.3f} (min {min(ds):.3f}, n {len(ds)})", "verdict": "-"})
    for e in EDITS:
        a_ = 1 - cos(V[f"T10_D1_dwarf_paladin_{e}_p1_seed2645751"], V["T10_D1_dwarf_paladin_plain_seed2645751"])
        b_ = 1 - cos(V[f"R50_D1_dwarf_paladin_{e}_p1_seed2645751"], V["R50_D1_dwarf_paladin_plain_seed2645751"])
        met.append({"block": "confirm", "prompt": "D1_dwarf_paladin", "cond": f"{e}_p1 T10 {a_:.4f} R50", "D": round(b_, 5)})
    for r in rows:
        if r["block"] in ("ladder", "V2", "V2r") and r["setting"] == "T10":
            d = 1 - cos(V[r["name"]], V[f"{r['setting']}_{r['prompt']}_plain_seed2645751"])
            met.append({"block": r["block"], "prompt": r["prompt"], "cond": r["cond"], "D": round(d, 5)})
    for p in LADDER_PROMPTS:
        for e in EDITS:
            ds = [next(x["D"] for x in met if x["prompt"] == p and x["cond"] == f"{e}_p{d:g}".replace(".", "p")) for d in DOSES]
            out.append({"test": f"ladder {p} {e}, reported", "value": " ".join(f"{d:g}:{v:.3f}" for d, v in zip(DOSES, ds)), "verdict": "-"})
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
