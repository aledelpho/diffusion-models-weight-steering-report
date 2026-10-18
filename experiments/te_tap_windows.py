"""C87 - cumulative tap windows and single taps of the L06 edit (docs/prereg_te_tap_windows.md).
Written 2026-10-18 after the pre-registration (975e537) and before any C87 render.

Reuses the C79 workflow (te_tap_isolation.workflow: Krea2ConditioningPush, variant="taps").

  python te_tap_windows.py --selftest
  python te_tap_windows.py --plan               # data/te_tap_windows_plan.csv: 156 rows (18 gate + 138 main)
  python te_tap_windows.py --queue --block gate
  python te_tap_windows.py --gate               # 18 x "max abs diff 0" against C79, then GATE PASS
  python te_tap_windows.py --queue --block main
  python te_tap_windows.py --count              # expected 156 missing 0 []
  python te_tap_windows.py --analyze            # GPU: DINOv2 (primary), CSD, VQAScore -> data/te_tap_windows_metrics.csv
"""
import argparse, csv, json, sys, urllib.request
from collections import Counter
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_tap_isolation as TI

DATA = HERE.parent / "data"
PLAN = DATA / "te_tap_windows_plan.csv"
METRICS = DATA / "te_tap_windows_metrics.csv"
FOLDER = "benchmark_te_tap_windows"
CHARS = TI.CHARS
SEEDS = ["2645751", "3316624"]
LAYER, DOSE = 6, 1.00


def conditions():
    """26 conditions: forward F_k = taps 2..k (k 2-10), backward B_k = taps k..11 (k 3-11), single S_k (k 3-10)."""
    c = {}
    for k in range(2, 11):
        c[f"F{k:02d}"] = ",".join(str(t) for t in range(2, k + 1))
    for k in range(3, 12):
        c[f"B{k:02d}"] = ",".join(str(t) for t in range(k, 12))
    for k in range(3, 11):
        c[f"S{k:02d}"] = str(k)
    assert len(c) == 26
    return c


# conditions that coincide with C79 renders (same taps carrying a non-zero push, same seeds): the gate
GATE = {"F03": "taps_local", "F08": "taps_early_mid", "B09": "taps_late"}


def make_plan():
    tx = TI.texts(); rows = []
    for block in ("gate", "main"):
        for ch in CHARS:
            for s in SEEDS:
                for tag, taps in conditions().items():
                    if (tag in GATE) != (block == "gate"):
                        continue
                    cond = f"L{LAYER:02d}_mlp_p{DOSE:.2f}_{tag}"
                    prefix = f"{ch}_{cond}_krea2_seed{s}"
                    rows.append({"row": len(rows), "block": block, "char": ch, "seed": s, "layer": LAYER,
                                 "dose": f"{DOSE:.2f}", "cond_tag": tag, "variant": "taps", "taps": taps,
                                 "noise_seed": TI.NOISE_SEED, "te_granular_json": TI.gj(LAYER, DOSE), "cond": cond,
                                 "prompt_text": tx[ch], "output_prefix": prefix,
                                 "expected_filename": f"{prefix}_00001_.png", **TI.SET})
    assert len(rows) == 156, len(rows)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows), dict(Counter(r["block"] for r in rows)))


def workflow(r):
    wf = TI.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(block=None):
    rows = [r for r in TI.rd(PLAN) if not block or r["block"] == block]
    n = 0
    for r in rows:
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def c79_file(r):
    return c47.IMG_ROOT / TI.FOLDER / f"{r['char']}_L06_mlp_p1.00_{GATE[r['cond_tag']]}_krea2_seed{r['seed']}_00001_.png"


def gate():
    ok = True
    for r in [r for r in TI.rd(PLAN) if r["block"] == "gate"]:
        p, q = c47.IMG_ROOT / FOLDER / r["expected_filename"], c79_file(r)
        if not p.exists() or not q.exists():
            print(r["expected_filename"], "MISSING", p if not p.exists() else q); ok = False; continue
        d = int(np.abs(TI._im(p) - TI._im(q)).max())
        print(f"{r['char']} {r['seed']} {r['cond_tag']} vs C79 {GATE[r['cond_tag']]}: max abs diff {d}")
        ok &= d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = TI.rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def analyze():
    """DINOv2-large (primary), CSD-ViT-L and VQAScore distances to the same-seed baseline, for the 156 renders and the
    six full edits; checks rule 4 (gate renders reproduce C79's DINOv2 distances to the third decimal)."""
    from PIL import Image
    import metric_validation as MV
    rows = TI.rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    if miss:
        raise RuntimeError(f"missing {len(miss)} C87 renders: {miss[:3]}")
    m = MV.Models(vqa=True); cache = {}
    def ev(path, ch):
        if str(path) not in cache:
            im = Image.open(path).convert("RGB")
            cache[str(path)] = {"dino": m.dino_vec(im), "csd": m.csd_vec(im),
                                "vqa": float(np.mean(m.vqa_scores(path, [p for _, p in TI.VQA_TRAITS[ch]])))}
        return cache[str(path)]
    base = lambda ch, s: c47.IMG_ROOT / "benchmark_portraits" / "phase_c" / f"{ch}_baseline_krea2_seed{s}_00001_.png"
    full = lambda ch, s: c47.IMG_ROOT / "benchmark_te_characters" / f"{ch}_L06_mlp_p1.00_krea2_seed{s}_00001_.png"
    todo = [(r["char"], r["seed"], r["cond_tag"], r["taps"], c47.IMG_ROOT / FOLDER / r["expected_filename"]) for r in rows]
    todo += [(ch, s, "FULL", "2,3,4,5,6,7,8,9,10,11", full(ch, s)) for ch in CHARS for s in SEEDS]
    out = []
    for i, (ch, s, tag, taps, p) in enumerate(todo):
        b, c = ev(base(ch, s), ch), ev(p, ch)
        out.append({"char": ch, "seed": s, "cond_tag": tag, "taps": taps,
                    "dinov2_dist_to_base": round(1 - MV.cos(c["dino"], b["dino"]), 6),
                    "csd_dist_to_base": round(1 - MV.cos(c["csd"], b["csd"]), 6),
                    "vqa_loss_vs_base": round(b["vqa"] - c["vqa"], 6), "file": str(p.relative_to(c47.IMG_ROOT))})
        if (i + 1) % 18 == 0:
            print(f"analyzed {i + 1}/{len(todo)}")
    with open(METRICS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    c79 = {(r["char"], r["seed"], r["cond_tag"]): float(r["dinov2_dist_to_base"])
           for r in TI.rd(DATA / "te_tap_isolation_metrics.csv") if r["layer"] == "6"}
    bad = [(o["char"], o["seed"], o["cond_tag"]) for o in out if o["cond_tag"] in GATE
           and abs(o["dinov2_dist_to_base"] - c79[(o["char"], o["seed"], GATE[o["cond_tag"]])]) >= 0.0005]
    print("wrote", METRICS, "rows", len(out))
    print("RULE 4", "PASS" if not bad else f"FAIL {bad}")


def selftest():
    c = conditions()
    assert c["F02"] == "2" and c["F10"] == "2,3,4,5,6,7,8,9,10" and c["B03"] == "3,4,5,6,7,8,9,10,11"
    assert c["B11"] == "11" and c["S07"] == "7" and "S02" not in c and "S11" not in c
    assert c["F03"] == TI.TAP_CONDS[6]["taps_local"] and c["B09"] == TI.TAP_CONDS[6]["taps_late"]
    # F08 vs C79 early_mid: same taps once 0 and 1 (no push from a layer-6 edit) are dropped
    assert set(c["F08"].split(",")) == set(TI.TAP_CONDS[6]["taps_early_mid"].split(",")) - {"0", "1"}
    n = len(CHARS) * len(SEEDS)
    assert n * len(c) == 156 and n * len(GATE) == 18
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
