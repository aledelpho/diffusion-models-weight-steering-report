"""MOSS-S2 - S2 again at doses that move the picture: do 25 steps and the turbo (10 steps, euler or euler_ancestral)
treat edits like 50 steps? (docs/prereg_moss_settings2.md). Written 2026-10-25 before any render. Authorised by
Alessandro ("Sono d'accordo, ma alziamo a 10 gli steps del turbo ... prova anche il turbo con euler a").

  python moss_settings2.py --plan      # data/moss_settings2_plan.csv (committed; do not re-run)
  python moss_settings2.py --queue     # ComfyUI running, MOSS tuner v4
  python moss_settings2.py --count     # expected 72 missing 0 []
  python moss_settings2.py --analyze   # data/moss_settings2_metrics.csv, data/moss_settings2_tests.csv
  python moss_settings2.py --sheet     # Text2Img/_moss_settings2_sheet.jpg
"""
import argparse, csv, json, statistics, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import moss_gate as G
import moss_settings as S

DATA = HERE.parent / "data"
PLAN, METRICS, TESTS = DATA / "moss_settings2_plan.csv", DATA / "moss_settings2_metrics.csv", DATA / "moss_settings2_tests.csv"
FOLDER = "benchmark_moss_settings2"
S.SETTINGS = {"R50": ("euler", 50, 3.0, False), "E25": ("euler", 25, 3.0, False),
              "T10": ("euler", 10, 1.0, True), "T10A": ("euler_ancestral", 10, 1.0, True)}
S.FOLDER = FOLDER
PROMPTS, SEED = ["D1_dwarf_paladin", "S1_rally"], "2645751"
DOSES = [1.0, 2.0]
ORDER = {"T10": 0, "T10A": 1, "E25": 2, "R50": 3}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def cond(e, d):
    return f"{e}_p{d:g}".replace(".", "p")


def make_plan():
    import te_shapes2 as TS2
    tx = TS2.texts(); rows = []
    for st in S.SETTINGS:
        for p in PROMPTS:
            rows.append({"setting": st, "prompt": p, "seed": SEED, "cond": "plain", "te_json": "{}", "dit_json": "{}", "prompt_text": tx[p]})
            for e, (half, key) in S.EDITS.items():
                for d in DOSES:
                    j = json.dumps({key: d})
                    rows.append({"setting": st, "prompt": p, "seed": SEED, "cond": cond(e, d), "te_json": j if half == "te" else "{}",
                                 "dit_json": j if half == "dit" else "{}", "prompt_text": tx[p]})
    for r in rows:
        r["name"] = f"{r['setting']}_{r['prompt']}_{r['cond']}_seed{r['seed']}"; r["expected_filename"] = r["name"] + "_00001_.png"
    rows.sort(key=lambda r: ORDER[r["setting"]])
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def queue():
    n = 0
    for r in rd(PLAN):
        if (G.IMG / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{G.URL}/prompt", data=json.dumps({"prompt": S.workflow(r)}).encode(),
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
    D = lambda a, b: 1 - float(V[a] @ V[b] / (np.linalg.norm(V[a]) * np.linalg.norm(V[b])))
    nm = lambda st, p, c: f"{st}_{p}_{c}_seed{SEED}"
    cells = [(p, cond(e, d)) for p in PROMPTS for e in S.EDITS for d in DOSES]
    eff = {st: [D(nm(st, p, c), nm(st, p, "plain")) for p, c in cells] for st in S.SETTINGS}
    met = [{"setting": st, "prompt": p, "cond": c, "D_to_own_plain": round(v, 5)} for st in S.SETTINGS for (p, c), v in zip(cells, eff[st])]
    out = [{"test": "power (reported)", "value": f"R50 median edit D {statistics.median(eff['R50']):.3f}; informative if >= 0.03", "verdict": "-"}]
    for st in ("E25", "T10", "T10A"):
        rho = S.spearman(eff[st], eff["R50"]); ratio = statistics.median([a / b for a, b in zip(eff[st], eff["R50"]) if b > 0])
        ok = rho >= 0.80 and 0.5 <= ratio <= 2.0
        out.append({"test": f"S2 {st} edits proportional to R50", "value": f"Spearman {rho:.2f} (bar 0.80), median ratio {ratio:.2f} (0.5-2)", "verdict": "PASS" if ok else "FAIL"})
    for path, rws in ((METRICS, met), (TESTS, out)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rws[0])); w.writeheader(); w.writerows(rws)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


def sheet():
    from PIL import Image
    R = G.IMG / FOLDER; W, H = 200, 250
    conds = ["plain"] + [cond(e, d) for e in S.EDITS for d in DOSES]
    sts = list(S.SETTINGS)
    Sh = Image.new("RGB", (W * len(conds), H * len(sts) * len(PROMPTS)), (26, 26, 25))
    for i, p in enumerate(PROMPTS):
        for j, st in enumerate(sts):
            for k, c in enumerate(conds):
                Sh.paste(Image.open(R / f"{nm_(st, p, c)}_00001_.png").convert("RGB").resize((W, H)), (k * W, (i * len(sts) + j) * H))
    Sh.save(G.IMG / "_moss_settings2_sheet.jpg", quality=86)
    print("sheet: rows dwarf R50/E25/T10/T10A then rally; columns plain then", conds[1:], "->", G.IMG / "_moss_settings2_sheet.jpg")


def nm_(st, p, c):
    return f"{st}_{p}_{c}_seed{SEED}"


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
