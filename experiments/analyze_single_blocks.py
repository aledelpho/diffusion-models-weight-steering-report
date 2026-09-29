# -*- coding: utf-8 -*-
"""
experiments/analyze_single_blocks.py — tests docs/prereg_single_blocks_identifiability.md.

  --guards   all renders present; drive in each graph matches the plan; none identical to baseline
  --extract  23 features + coherence + 5 bands + saturation/hue, resumable, time-bounded
  --run      T1, T2, T3 and the descriptive map
No render.
"""
from __future__ import annotations
import argparse, csv, itertools, json, math, random, statistics, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G  # noqa: E402

BENCH = "benchmark_single_blocks_atlas"
PLAN = DATA / "single_blocks_atlas_plan.csv"
CACHE = DATA / "single_blocks_measures.csv"
OUT_G = DATA / "single_blocks_guards.csv"
PROMPTS = ["P01_blacksmith", "S1_rally", "F4_closeup"]
BLOCKS = list(range(28))
rp = lambda fn: G.find_render(BENCH, fn)


def guards():
    from PIL import Image
    arr = lambda p: np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
    plan = G.read_csv(PLAN); bad = []; dead = []
    base = {r["prompt_id"]: r["expected_filename"] for r in plan if r["arm"] == "baseline"}
    for r in plan:
        p = rp(r["expected_filename"])
        if not p:
            bad.append("missing " + r["expected_filename"]); continue
        g = G.png_graph(p) or {}
        tun = [n["inputs"] for n in g.values() if "Tuner" in n.get("class_type", "")]
        vo = str(tun[0].get("vectors_override", "")) if tun else ""
        want = r["vectors_override"]
        if r["arm"] == "baseline":
            if vo.strip() and any(abs(float(x)) > 0 for x in vo.split(",") if x.strip()):
                bad.append("drive in baseline " + r["expected_filename"])
        else:
            got = [float(x) for x in vo.split(",") if x.strip()]
            exp = [float(x) for x in want.split(",") if x.strip()]
            if len(got) != len(exp) or any(abs(a - b) > 1e-9 for a, b in zip(got, exp)):
                bad.append("drive " + r["expected_filename"])
            b = rp(base[r["prompt_id"]])
            if b and int(np.abs(arr(p) - arr(b)).max()) == 0:
                dead.append(r["expected_filename"])
    out = [{"guard": "G1_present_and_drive", "pass": not bad, "detail": " | ".join(bad[:6]) or f"{len(plan)}/{len(plan)}"},
           {"guard": "G3_not_identical", "pass": not dead, "detail": f"{len(dead)} identical: {dead[:6]}"}]
    G.write_csv(OUT_G, out)
    for x in out: print(f"  {x['guard']:22} {'PASS' if x['pass'] else 'FAIL'}  {x['detail']}")


def extract(budget=150.0):
    from style_features import extract_all_features
    from retro_texture_axes import measure
    t0 = time.time(); cloud, feats, mu, sd = G.load_cloud()
    rows = G.read_csv(CACHE) if CACHE.exists() else []; done = {r["file"] for r in rows}
    todo = [r["expected_filename"] for r in G.read_csv(PLAN) if r["expected_filename"] not in done]
    print(f"{len(done)} cached, {len(todo)} to measure", flush=True)
    for i, fn in enumerate(todo, 1):
        p = rp(fn); f = extract_all_features(str(p)); coh, bands, var, sat, hue = measure(str(p))
        rows.append({"file": fn, "coherence": coh, **{f"band{k}": bands[k] for k in range(5)},
                     "sat": sat, "hue": hue, **{c: f[c] for c in feats}})
        if i % 8 == 0 or i == len(todo) or time.time() - t0 > budget:
            G.write_csv(CACHE, rows); print(f"  {i}/{len(todo)}", flush=True)
        if time.time() - t0 > budget:
            print("  budget reached, re-run", flush=True); return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guards", action="store_true"); ap.add_argument("--extract", action="store_true")
    a = ap.parse_args()
    if a.guards: guards()
    if a.extract: extract()


if __name__ == "__main__":
    main()
