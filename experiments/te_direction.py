"""C71 - does each text-encoder edit push the conditioning along the "comics -> anime" direction of the text itself?
(docs/prereg_te_direction.md). Written 2026-10-12, before any C71 encode. No images.

  python te_direction.py --plan           # data/te_direction_plan.csv (5 orders x 3 style swaps + 1 gate encode)
  python te_direction.py --queue --first 1
  python te_direction.py --gate           # the re-encoded V1 baseline must equal the C67 baseline bit for bit
  python te_direction.py --queue
  python te_direction.py --count
  python te_direction.py --analyze        # Claude
  python te_direction.py --selftest

Style swap: the clause "realistic western comics style" of each word order replaced by "anime style", "cartoon style"
or "oil painting style"; everything else identical. Pooled conditioning = mean over token positions, per tap.
Direction of a swap = pooled(swap) - pooled(baseline); push of an edit = pooled(edit, C68) - pooled(baseline, C67).
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_conditioning as T
import te_regions as RG

DATA = HERE.parent / "data"
PLAN = DATA / "te_direction_plan.csv"
FOLDER = "benchmark_te_direction"
ORDERS = RG.ORDERS
CLAUSE = "realistic western comics style"
STYLES = {"anime": "anime style", "cartoon": "cartoon style", "painting": "oil painting style"}
SEED_LAB = "3141592"


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def out_path(pid, cond):
    return c47.IMG_ROOT / FOLDER / f"{pid}_{cond}.npz"


def make_plan():
    texts = {r["prompt_id"]: r["prompt_text"] for r in rd(DATA / "te_conditioning_plan.csv") if r["set"] == "order" and r["cond"] == "baseline"}
    rows = [{"row": 0, "prompt_id": ORDERS[0], "cond": "baseline_again", "prompt_text": texts[ORDERS[0]]}]
    for v in ORDERS:
        assert texts[v].count(CLAUSE) == 1, v
        for s, rep in STYLES.items():
            rows.append({"row": len(rows), "prompt_id": v, "cond": s, "prompt_text": texts[v].replace(CLAUSE, rep)})
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = T.workflow({"prompt_text": r["prompt_text"], "te_granular_json": "", "out": str(out_path(r["prompt_id"], r["cond"])),
                     "mode": "full", "baseline": ""})
    wf["90"]["inputs"]["taps"] = ""            # all 12 taps, as C67 baselines and C68 edits
    return wf


def queue(first):
    n = 0
    for r in rd(PLAN)[: first or None]:
        if out_path(r["prompt_id"], r["cond"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def count():
    rows = rd(PLAN)
    miss = [r["cond"] + "/" + r["prompt_id"] for r in rows if not out_path(r["prompt_id"], r["cond"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def gate():
    a = np.load(out_path(ORDERS[0], "baseline_again")); b = np.load(T.out_path("order", ORDERS[0], "baseline"))
    same = a["cond"].shape == b["cond"].shape and np.array_equal(a["cond"], b["cond"]) and np.array_equal(a["ids"], b["ids"])
    print("re-encoded V1 baseline vs C67 baseline:", "identical" if same else "DIFFERENT")
    print("GATE", "PASS" if same else "FAIL - stop")


# ---------------------------------------------------------------- analysis
def pooled(path):
    return np.load(path)["cond"].astype(np.float32).mean(0)        # (12 taps, 2560)


def cos(a, b):
    a = a.ravel(); b = b.ravel()
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def labels():
    lab = {r["row"]: [r[f"g{i}"] for i in range(1, 6)] for r in rd(DATA / "te_genre_alessandro.csv") if r["grid"] == f"te_genre_{SEED_LAB}"}
    lab.pop("originali")
    return lab


def analyze():
    from scipy.stats import spearmanr
    lab = labels()
    edits = list(lab)
    unit = {r["cond"]: r["unit"] for r in rd(DATA / "te_regions_plan.csv")}
    B = {v: pooled(T.out_path("order", v, "baseline")) for v in ORDERS}
    D = {(v, s): pooled(out_path(v, s)) - B[v] for v in ORDERS for s in STYLES}
    rows = []
    for e in edits:
        j = T.first_tap(unit[e])
        res = {"cond": e, "first_tap": j, "anime_n": lab[e].count("anime"), "cartoon_n": lab[e].count("cartoon"),
               "switch_n": sum(g != "fumetto" for g in lab[e])}
        for name, f in [("cos_anime", lambda v: D[(v, "anime")]), ("cos_cartoon", lambda v: D[(v, "cartoon")]),
                        ("cos_painting", lambda v: D[(v, "painting")]),
                        ("cos_anime_minus_painting", lambda v: D[(v, "anime")] - D[(v, "painting")]),
                        ("cos_cartoon_minus_painting", lambda v: D[(v, "cartoon")] - D[(v, "painting")])]:
            res[name] = round(float(np.mean([cos((pooled(RG.out_path("order", v, e)) - B[v])[j:], f(v)[j:]) for v in ORDERS])), 4)
        rows.append(res)
    with open(DATA / "te_direction_by_edit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    # style directions among themselves (reported)
    sim = {f"{a}~{b}": round(float(np.mean([cos(D[(v, a)], D[(v, b)]) for v in ORDERS])), 4)
           for a, b in [("anime", "cartoon"), ("anime", "painting"), ("cartoon", "painting")]}
    A = [r["anime_n"] for r in rows]
    out = []
    rho, p = spearmanr([r["cos_anime"] for r in rows], A)
    out.append({"test": "H1", "value": f"rho {rho:.3f} (p {p:.3f}, n {len(rows)}) cos(push, anime direction) vs anime count", "verdict": "supported" if rho >= 0.50 else "not supported"})
    rho, p = spearmanr([r["cos_anime_minus_painting"] for r in rows], A)
    out.append({"test": "H2", "value": f"rho {rho:.3f} (p {p:.3f}) cos(push, anime - painting) vs anime count", "verdict": "supported" if rho >= 0.40 else "not supported"})
    rho, p = spearmanr([r["cos_cartoon_minus_painting"] for r in rows], [r["cartoon_n"] for r in rows])
    out.append({"test": "R1 cartoon (reported)", "value": f"rho {rho:.3f} (p {p:.3f}) cos(push, cartoon - painting) vs cartoon count", "verdict": ""})
    rho, p = spearmanr([r["cos_painting"] for r in rows], A)
    out.append({"test": "R2 control (reported)", "value": f"rho {rho:.3f} (p {p:.3f}) cos(push, painting direction) vs anime count", "verdict": ""})
    out.append({"test": "R3 style directions (reported)", "value": json.dumps(sim), "verdict": ""})
    with open(DATA / "te_direction_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    for r in rows:
        print(f"  {r['cond']:16s} anime {r['anime_n']} cartoon {r['cartoon_n']}  cosA {r['cos_anime']:+.3f} cosC {r['cos_cartoon']:+.3f} "
              f"cosP {r['cos_painting']:+.3f}  A-P {r['cos_anime_minus_painting']:+.3f}  C-P {r['cos_cartoon_minus_painting']:+.3f}")
    for r in out:
        print(r)


def selftest():
    rng = np.random.default_rng(0)
    a = rng.normal(size=(12, 8))
    assert abs(cos(a, a) - 1) < 1e-6 and abs(cos(a, -a) + 1) < 1e-6
    assert T.first_tap("L06") == 2 and T.first_tap("L35") == 12 and T.first_tap("L02") == 1
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "gate", "count", "analyze", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.gate: gate()
    if a.count: count()
    if a.analyze: analyze()
    if a.selftest: selftest()
