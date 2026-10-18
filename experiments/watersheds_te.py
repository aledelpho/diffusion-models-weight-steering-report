"""C99 - minimal text-encoder perturbations against C97's fragile places (docs/prereg_watersheds_te.md).
Written 2026-10-18 after the pre-registration, before any C99 render.

  python watersheds_te.py --selftest
  python watersheds_te.py --plan            # data/watersheds_te_plan.csv (50 rows; already committed)
  python watersheds_te.py --queue --block gate
  python watersheds_te.py --gate            # 2 x "max abs diff 0" against the C97 bases, then GATE PASS
  python watersheds_te.py --queue --block main
  python watersheds_te.py --count           # expected 50 missing 0 []
  python watersheds_te.py --analyze         # numpy/scipy: data/watersheds_te_tests.csv
"""
import argparse, csv, itertools, json, statistics, sys, urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_tap_isolation as TI
import micro_watersheds as MW
import watersheds_origin as WO

DATA = HERE.parent / "data"
PLAN = DATA / "watersheds_te_plan.csv"
FOLDER = "benchmark_watersheds_te"
T = {"T1": (6, 0.004, "real"), "T2": (14, 0.01, "real"), "T3": (28, -0.01, "real"), "T4": (6, 0.004, "token")}
GATES = [("P3_archerforest", "3141592"), ("D1_dwarf_paladin", "2645751")]


def make_plan():
    tx = {(r["prompt_id"], r["seed"]): r["prompt_text"] for r in WO.rd(WO.PLAN) if r["cond"] == "base"}
    rows = []
    def add(block, p, s, cond, layer, d, variant):
        prefix = f"{p}_{cond}_krea2_seed{s}"
        rows.append({"row": len(rows), "block": block, "prompt_id": p, "seed": s, "cond": cond, "layer": layer,
                     "dose": f"{d:.3f}", "variant": variant, "taps": "", "noise_seed": 99, "te_granular_json": TI.gj(layer, d),
                     "prompt_text": tx[(p, s)], "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **WO.SET})
    for p, s in GATES:
        add("gate", p, s, "zero", 6, 0.004, "zero")
    for p in WO.MICRO:
        for s in WO.SEEDS:
            for k, (L, d, v) in T.items():
                add("main", p, s, k, L, d, v)
    assert len(rows) == 50
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = TI.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(block=None):
    n = 0
    for r in WO.rd(PLAN):
        if block and r["block"] != block:
            continue
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def gate():
    ok = True
    for p, s in GATES:
        a = MW.img_root() / FOLDER / f"{p}_zero_krea2_seed{s}_00001_.png"
        b = MW.img_root() / WO.FOLDER / f"{p}_base_krea2_seed{s}_00001_.png"
        if not a.exists():
            print("MISSING", a); ok = False; continue
        d = int(np.abs(MW.load(a) - MW.load(b)).max()); print(f"{p} seed {s} zero vs C97 base: max abs diff {d}"); ok &= d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = WO.rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def analyze_cells(cells):
    """cells: {(p, s): {"base", "W1".."W5", "T1".."T4": img}}"""
    q1, q1j, q1t4, q2, q2j, mag = [], [], [], {}, {}, {"W": [], "T": []}
    for key, ims in sorted(cells.items()):
        base = ims["base"]; t = np.log1p(MW.texture(base).ravel()); j = WO.jitter(base)
        E = {}
        for k in [*WO.W, *T]:
            E[k], m = WO.logE(base, ims[k]); mag[k[0]].append(m)
        Wm = np.mean([E[k] for k in WO.W], axis=0)
        for k in T:
            v = WO.pcorr(E[k], Wm, t); q1.append(v); q1j.append(WO.pcorr(E[k], Wm, t, j))
            if k == "T4":
                q1t4.append(v)
        q2[key] = statistics.median(WO.pcorr(E[a], E[b], t) for a, b in itertools.combinations(list(T), 2))
        q2j[key] = statistics.median(WO.pcorr(E[a], E[b], t, j) for a, b in itertools.combinations(list(T), 2))
    m1 = statistics.median(q1); n2 = sum(v >= 0.30 for v in q2.values())
    return [
        {"test": "Q1 text-encoder perturbations hit the image-model fragile places (median partial r over 48)", "value": f"{m1:.3f}",
         "verdict": "supported" if m1 >= 0.30 else ("refuted" if m1 <= 0.10 else "inconclusive")},
        {"test": "Q2 text-encoder perturbations agree among themselves (cells with median >= 0.30)", "value": f"{n2} of {len(q2)}",
         "verdict": "agree" if n2 >= 0.75 * len(q2) else "do not agree"},
        {"test": "Q1 for T4 alone, random push of the conditioning (reported)", "value": f"median {statistics.median(q1t4):.3f} (n {len(q1t4)})", "verdict": ""},
        {"test": "size of changes, median mean delta W / T (reported)", "value": f"{statistics.median(mag['W']):.2f} / {statistics.median(mag['T']):.2f}", "verdict": ""},
        {"test": "Q1 / Q2 with the one-pixel jitter covariate (reported)", "value": f"{statistics.median(q1j):.3f} / {sum(v >= 0.30 for v in q2j.values())} of {len(q2j)}", "verdict": ""},
    ]


def analyze():
    R = MW.img_root(); cells = {}
    for p in WO.MICRO:
        for s in WO.SEEDS:
            ims = {"base": MW.load(R / WO.FOLDER / f"{p}_base_krea2_seed{s}_00001_.png")}
            for k in WO.W:
                ims[k] = MW.load(R / WO.FOLDER / f"{p}_{k}_krea2_seed{s}_00001_.png")
            for k in T:
                ims[k] = MW.load(R / FOLDER / f"{p}_{k}_krea2_seed{s}_00001_.png")
            cells[(p, s)] = ims
    out = analyze_cells(cells)
    with open(DATA / "watersheds_te_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


def selftest():
    rng = np.random.default_rng(5)
    def cell(spots_w, spots_t):
        base = np.full((256, 256, 3), 90, np.int16); base[:, :64] += rng.integers(0, 50, (256, 64, 3)).astype(np.int16)
        ims = {"base": base}
        for k, spots in [(k, spots_w) for k in WO.W] + [(k, spots_t) for k in T]:
            im = base.copy()
            for (y, x) in spots:
                if rng.random() < 0.7:
                    im[y:y + 16, x:x + 16] = 200
            im += rng.integers(-2, 3, im.shape).astype(np.int16); ims[k] = im
        return ims
    spots = lambda: [(int(rng.integers(0, 15)) * 16, int(rng.integers(5, 15)) * 16) for _ in range(8)]
    same = {(p, s): (lambda sp: cell(sp, sp))(spots()) for p in ("A", "B") for s in ("1", "2", "3")}
    assert analyze_cells(same)[0]["verdict"] == "supported"
    diff = {(p, s): cell(spots(), spots()) for p in ("A", "B") for s in ("1", "2", "3")}
    assert analyze_cells(diff)[0]["verdict"] != "supported"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a in ("plan", "queue", "gate", "count", "analyze", "selftest"):
        ap.add_argument(f"--{a}", action="store_true")
    ap.add_argument("--block", default=None)
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.plan: make_plan()
    if a.queue: queue(a.block)
    if a.gate: gate()
    if a.count: count()
    if a.analyze: analyze()
