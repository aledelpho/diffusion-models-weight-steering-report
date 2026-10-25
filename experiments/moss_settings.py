"""MOSS-S - which sampling settings can stand in for the slow reference? (docs/prereg_moss_settings.md)
Written 2026-10-25 before any render. Renders authorised by Alessandro ("facciamo prepara la direttiva ... proverei già
anche il LoRA. Meglio prima partire con la calibrazione").

  python moss_settings.py --plan      # data/moss_settings_plan.csv (committed; do not re-run)
  python moss_settings.py --queue     # ComfyUI running, MOSS tuner v4 installed
  python moss_settings.py --count     # expected 84 missing 0 []
  python moss_settings.py --analyze   # DINOv2 -> data/moss_settings_metrics.csv, data/moss_settings_tests.csv
  python moss_settings.py --sheet     # Text2Img/_moss_settings_sheet.jpg (plain pictures, three settings side by side)

Settings: R50 euler, 50 steps, CFG 3 (the reference); E25 euler, 25 steps, CFG 3; T8 the lodestones 8-step DMD2 LoRA
(strength 1.0) with euler, 8 steps, CFG 1. All: simple scheduler, MOSS default shift 5, 1024 x 1280, MOSS-Image SFT bf16,
both MOSS tuners in the graph ("{}" when unedited).
"""
import argparse, csv, json, statistics, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import moss_gate as G

DATA = HERE.parent / "data"
PLAN, METRICS, TESTS = DATA / "moss_settings_plan.csv", DATA / "moss_settings_metrics.csv", DATA / "moss_settings_tests.csv"
FOLDER = "benchmark_moss_settings"
LORA = "Moss\\lodestones-8-steps-dmd2-lora.safetensors"
SETTINGS = {"R50": ("euler", 50, 3.0, False), "E25": ("euler", 25, 3.0, False), "T8": ("euler", 8, 1.0, True)}
PROMPTS = ["D1_dwarf_paladin", "S1_rally", "C4_stilllife", "P5_comic_panels", "P2_lotuscanoe", "LN"]
SEEDS = ["2645751", "3316624"]
EDIT_PROMPTS, EDIT_SEED = ["D1_dwarf_paladin", "S1_rally"], "2645751"
EDITS = {"dit06": ("dit", "layers.6.proj.ffn_down.weight"), "dit20": ("dit", "layers.20.proj.ffn_down.weight"),
         "te06": ("te", "layers.6.mlp.down_proj.weight"), "te27": ("te", "layers.27.mlp.down_proj.weight")}
DOSES = [0.10, 0.30]


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def make_plan():
    import te_shapes2 as TS2
    tx = TS2.texts(); rows = []
    for st in SETTINGS:
        for p in PROMPTS:
            for s in SEEDS:
                rows.append({"setting": st, "prompt": p, "seed": s, "cond": "plain", "te_json": "{}", "dit_json": "{}", "prompt_text": tx[p]})
        for p in EDIT_PROMPTS:
            for e, (half, key) in EDITS.items():
                for d in DOSES:
                    j = json.dumps({key: d})
                    rows.append({"setting": st, "prompt": p, "seed": EDIT_SEED, "cond": f"{e}_p{d:g}".replace(".", "p"),
                                 "te_json": j if half == "te" else "{}", "dit_json": j if half == "dit" else "{}", "prompt_text": tx[p]})
    for r in rows:
        r["name"] = f"{r['setting']}_{r['prompt']}_{r['cond']}_seed{r['seed']}"; r["expected_filename"] = r["name"] + "_00001_.png"
    order = {"T8": 0, "E25": 1, "R50": 2}                      # fast settings first: early results while the slow ones run
    rows.sort(key=lambda r: order[r["setting"]])
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    sampler, steps, cfg, lora = SETTINGS[r["setting"]]
    G.PROMPT, G.SEED, G.FOLDER = r["prompt_text"], int(r["seed"]), FOLDER
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


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = G.IMG / FOLDER; rows = rd(PLAN); m = MV.Models(vqa=False)
    V = {r["name"]: np.asarray(m.dino_vec(Image.open(R / r["expected_filename"]).convert("RGB")), dtype=np.float64) for r in rows}
    D = lambda a, b: 1 - float(V[a] @ V[b] / (np.linalg.norm(V[a]) * np.linalg.norm(V[b])))
    nm = lambda st, p, c, s: f"{st}_{p}_{c}_seed{s}"
    met, out = [], []
    floor = {st: [D(nm(st, p, "plain", SEEDS[0]), nm(st, p, "plain", SEEDS[1])) for p in PROMPTS] for st in SETTINGS}
    for st in SETTINGS:
        out.append({"test": f"seed floor {st}", "value": f"median D between the two seeds {statistics.median(floor[st]):.3f}", "verdict": "-"})
    ref_floor = statistics.median(floor["R50"])
    cells = [(p, f"{e}_p{d:g}".replace(".", "p")) for p in EDIT_PROMPTS for e in EDITS for d in DOSES]
    eff = {st: [D(nm(st, p, c, EDIT_SEED), nm(st, p, "plain", EDIT_SEED)) for p, c in cells] for st in SETTINGS}
    for st in SETTINGS:
        for (p, c), v in zip(cells, eff[st]):
            met.append({"setting": st, "prompt": p, "cond": c, "D_to_own_plain": round(v, 5)})
    for st in ("E25", "T8"):
        fid = [D(nm(st, p, "plain", s), nm("R50", p, "plain", s)) for p in PROMPTS for s in SEEDS]
        s1 = statistics.median(fid) <= 0.5 * ref_floor
        rho = spearman(eff[st], eff["R50"]); ratio = statistics.median([a / b for a, b in zip(eff[st], eff["R50"]) if b > 0])
        s2 = rho >= 0.80 and 0.5 <= ratio <= 2.0
        out.append({"test": f"S1 {st} plain close to R50", "value": f"median D {statistics.median(fid):.3f} vs half the R50 floor {0.5 * ref_floor:.3f}", "verdict": "PASS" if s1 else "FAIL"})
        out.append({"test": f"S2 {st} edits proportional to R50", "value": f"Spearman {rho:.2f} (bar 0.80), median ratio {ratio:.2f} (0.5-2)", "verdict": "PASS" if s2 else "FAIL"})
    for path, rws in ((METRICS, met), (TESTS, out)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rws[0])); w.writeheader(); w.writerows(rws)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


def sheet():
    from PIL import Image
    R = G.IMG / FOLDER; W, H = 256, 320
    S = Image.new("RGB", (W * 3 * len(SEEDS), H * len(PROMPTS)), (26, 26, 25))
    for i, p in enumerate(PROMPTS):
        for j, s in enumerate(SEEDS):
            for k, st in enumerate(SETTINGS):
                S.paste(Image.open(R / f"{st}_{p}_plain_seed{s}_00001_.png").convert("RGB").resize((W, H)), ((j * 3 + k) * W, i * H))
    S.save(G.IMG / "_moss_settings_sheet.jpg", quality=88)
    print("sheet: columns per seed R50 | E25 | T8 ->", G.IMG / "_moss_settings_sheet.jpg")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "count", "analyze", "sheet"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue()
    if a.count: count()
    if a.analyze: analyze()
    if a.sheet: sheet()
