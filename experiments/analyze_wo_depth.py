# -*- coding: utf-8 -*-
"""
experiments/analyze_wo_depth.py
===============================
C41 — `wo` cut by depth, and the whole against the sum of its parts.
Governed by docs/prereg_wo_depth.md, deposited (642f361) before any render of this bench existed.

  python experiments/analyze_wo_depth.py --extract   # features, coherence, bands; resumable
  python experiments/analyze_wo_depth.py --guards    # G_det, G1, G3, G_applied, G_union
  python experiments/analyze_wo_depth.py --run       # primary at +-0.100, secondaries, exploratory doses

**Confirmatory vs exploratory.** The pre-registration covers +-0.100 only, and its §9 says: "A second
dose is a new pre-registration." Doses +-0.200 and +-0.350 were added to the plan afterwards (commit
f9834af, rendered 08:11-09:47, committed 10:04), with no pre-registration of their own. They are
therefore analysed with the SAME statistics, but every row they produce carries `status=exploratory`
and none of them can change the verdict.

Reuses unchanged: the base cloud, z-scoring and dist of groove_or_hole.py, the 23 features of
style_features.py, and measure() of retro_texture_axes.py. The six baselines are borrowed from
benchmark_centre_push and are only used if G_det passes.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import re
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))

import groove_or_hole as G  # noqa: E402

BENCH = "benchmark_wo_depth"
PLAN = DATA / "wo_depth_plan.csv"
CP_PLAN = DATA / "centre_push_plan.csv"
CACHE = DATA / "wo_depth_measures.csv"
OUT_GUARDS = DATA / "wo_depth_guards.csv"
OUT_CELLS = DATA / "wo_depth_composition_cells.csv"
OUT_SUMMARY = DATA / "wo_depth_composition_summary.csv"
OUT_PROFILE = DATA / "wo_depth_profile.csv"
GROUPS = ["b1", "b2", "b3", "b4", "b5", "b6"]
EXPECTED = {"b1": 5, "b2": 5, "b3": 5, "b4": 5, "b5": 4, "b6": 4, "union": 28}
CONFIRMATORY = 0.100
COS_MIN, RHO_LO, RHO_HI = 0.95, 0.90, 1.10


def rp(fn):
    return G.find_render(BENCH, fn)


def borrowed():
    """(prompt, seed) -> borrowed baseline path in benchmark_centre_push."""
    out = {}
    for r in G.read_csv(CP_PLAN):
        if r["arm"] == "baseline":
            out[(r["prompt_id"], r["seed"])] = G.find_render("benchmark_centre_push", r["expected_filename"])
    return out


def parse(cond: str):
    """condition -> (group, signed dose) ; e.g. slice_b3_pos -> (b3, +0.1), union_d-0.350 -> (union, -0.35)"""
    m = re.match(r"^(slice_(b\d)|union)_(pos|neg|d[+-][\d.]+)$", cond)
    if not m:
        return None
    g = m.group(2) or "union"
    t = m.group(3)
    d = CONFIRMATORY if t == "pos" else -CONFIRMATORY if t == "neg" else float(t[1:])
    return g, round(d, 3)


# ----------------------------------------------------------------------------- --extract
def extract(budget_s: float = 150.0) -> None:
    from style_features import extract_all_features
    from retro_texture_axes import measure
    t0 = time.time()
    cloud, feats, mu, sd = G.load_cloud()
    rows = G.read_csv(CACHE) if CACHE.exists() else []
    done = {r["file"] for r in rows}
    targets = [(r["expected_filename"], rp(r["expected_filename"])) for r in G.read_csv(PLAN)]
    targets += [(p.name, p) for p in borrowed().values() if p]
    todo = [(fn, p) for fn, p in targets if p and fn not in done]
    print(f"{len(done)} cached, {len(todo)} to measure", flush=True)
    for i, (fn, p) in enumerate(todo, 1):
        f = extract_all_features(str(p))
        coh, bands, *_ = measure(str(p))
        rows.append({"file": fn, "coherence": coh, **{f"band{k}": bands[k] for k in range(5)},
                     **{c: f[c] for c in feats}})
        if i % 8 == 0 or i == len(todo) or time.time() - t0 > budget_s:
            G.write_csv(CACHE, rows)
            print(f"  {i}/{len(todo)}", flush=True)
        if time.time() - t0 > budget_s:
            print("  budget reached, re-run to continue", flush=True)
            return


# ----------------------------------------------------------------------------- --guards
def guards() -> list[dict]:
    import numpy as np
    from PIL import Image
    arr = lambda p: np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
    plan = G.read_csv(PLAN)
    bor = borrowed()
    out = []

    # G_det — re-rendered baselines reproduce the borrowed ones pixel for pixel
    det = [r for r in plan if r["arm"] == "determinism"]
    det_ok, det_d = True, []
    for r in det:
        a, b = rp(r["expected_filename"]), bor.get((r["prompt_id"], r["seed"]))
        mx = int(np.abs(arr(a) - arr(b)).max()) if a and b else -1
        det_ok &= mx == 0
        det_d.append(f"{r['prompt_id']}:max|d|={mx}")
    out.append({"guard": "G_det", "pass": det_ok, "detail": " ".join(det_d)})

    # G1 — every render present, graph matches plan (prompt, seed, steps, size, preset)
    bad = []
    for r in plan:
        p = rp(r["expected_filename"])
        if not p:
            bad.append(f"missing {r['expected_filename']}"); continue
        rec, g = G.png_record(p), G.png_graph(p) or {}
        if not rec.get("ok") or rec["sha"] != r["prompt_sha1"] or int(rec["seed"]) != int(r["seed"]) \
                or rec["steps"] != int(r["steps"]) or rec["size"] != f"{r['width']}x{r['height']}":
            bad.append(f"graph {r['expected_filename']}")
        loaders = [n["inputs"].get("preset", "") for n in g.values()
                   if n.get("class_type") == "ArthemyKrea2PresetLoader"]
        want = r["preset_file"]
        if want and want not in loaders:
            bad.append(f"preset {r['expected_filename']} -> {loaders}")
        if not want and any(loaders):
            bad.append(f"preset in baseline row {r['expected_filename']} -> {loaders}")
    out.append({"guard": "G1", "pass": not bad, "detail": " | ".join(bad[:8]) or f"{len(plan)}/{len(plan)}"})

    # G3 — no perturbed render identical to its baseline
    dead = []
    for r in plan:
        if r["arm"] != "push":
            continue
        a, b = rp(r["expected_filename"]), bor.get((r["prompt_id"], r["seed"]))
        if a and b and int(np.abs(arr(a) - arr(b)).max()) == 0:
            dead.append(r["expected_filename"])
    out.append({"guard": "G3", "pass": not dead, "detail": f"{len(dead)} identical to baseline {dead[:4]}"})

    # G_applied — the loader reported the expected matched count for every preset used
    log = (Path(rp(plan[0]["expected_filename"])).parent / "tuner_logger_capture.log").read_text(
        encoding="utf-8", errors="replace")
    seen = {m.group(1): int(m.group(2)) for m in
            re.finditer(r"Loaded Preset '([^']+)' by [^|]*\| Model: (\d+) scalar", log)}
    wrong = []
    for r in plan:
        if r["arm"] != "push":
            continue
        g, _ = parse(r["condition"])
        name = r["preset_file"].rsplit(".", 1)[0]
        got = seen.get(name)
        if got != EXPECTED[g]:
            wrong.append(f"{name}:{got}")
    wrong = sorted(set(wrong))
    out.append({"guard": "G_applied", "pass": not wrong and not dead,
                "detail": (" | ".join(wrong[:8]) or "all presets reported the expected count")
                          + "; effect side covered by G3"})

    # G_union — recomputed from the preset files at analysis time
    u_bad = []
    by = {}
    for r in plan:
        if r["arm"] == "push":
            by.setdefault(parse(r["condition"])[1], {})[parse(r["condition"])[0]] = r["preset_file"]
    for d, m in sorted(by.items()):
        keys = {g: set(json.load(open(ROOT / "presets" / m[g], encoding="utf-8"))["model_patches"]) for g in m}
        flat = [k for g in GROUPS for k in keys[g]]
        if len(flat) != len(set(flat)) or set(flat) != keys["union"]:
            u_bad.append(f"{d:+.3f}")
    out.append({"guard": "G_union", "pass": not u_bad, "detail": ("bad at " + ",".join(u_bad)) if u_bad
                else f"6 disjoint slices == union at {len(by)} signed doses"})

    G.write_csv(OUT_GUARDS, out)
    for g in out:
        print(f"  {g['guard']:10} {'PASS' if g['pass'] else 'FAIL'}  {g['detail']}")
    return out


# ----------------------------------------------------------------------------- --run
def run() -> None:
    import numpy as np
    g = G.read_csv(OUT_GUARDS) if OUT_GUARDS.exists() else []
    if not g or not all(r["pass"] == "True" for r in g):
        sys.exit("guards missing or failed: run --guards first")
    plan = G.read_csv(PLAN)
    meas = {r["file"]: r for r in G.read_csv(CACHE)}
    cloud, feats, mu, sd = G.load_cloud()
    G.resolve_cloud_sha(cloud)
    sha = {r["prompt_id"]: r["prompt_sha1"] for r in plan}
    noise = {}
    for p in sha:
        zs = [o["z"] for o in cloud if o["sha"] == sha[p]]
        noise[p] = statistics.median(G.dist(a, b) for a, b in itertools.combinations(zs, 2))
    bor = {k: v.name for k, v in borrowed().items()}

    Z = lambda fn: np.array(G.z_of([float(meas[fn][c]) for c in feats], mu, sd))
    B = lambda fn, k: float(meas[fn][f"band{k}"])
    C = lambda fn: float(meas[fn]["coherence"])

    delta, prof = {}, []
    for r in plan:
        if r["arm"] != "push":
            continue
        grp, d = parse(r["condition"])
        fn, bf = r["expected_filename"], bor[(r["prompt_id"], r["seed"])]
        delta[(grp, d, r["prompt_id"], r["seed"])] = Z(fn) - Z(bf)
        prof.append({"group": grp, "dose": f"{d:+.3f}", "prompt": r["prompt_id"], "seed": r["seed"],
                     "status": "confirmatory" if abs(d) == CONFIRMATORY else "exploratory",
                     "dz_over_N": float(np.linalg.norm(Z(fn) - Z(bf)) / noise[r["prompt_id"]]),
                     **{f"band{k}_ratio": B(fn, k) / B(bf, k) for k in range(5)},
                     "L_column_only": C(fn) / C(bf)})
    G.write_csv(OUT_PROFILE, prof)

    cells, summ = [], []
    doses = sorted({d for (_, d, _, _) in delta})
    for d in doses:
        for p in sorted(sha):
            per = []
            for s in sorted({k[3] for k in delta}):
                parts = [delta[(gg, d, p, s)] for gg in GROUPS]
                S, U = sum(parts), delta[("union", d, p, s)]
                rho = float(np.linalg.norm(U) / np.linalg.norm(S))
                cos = float(U @ S / (np.linalg.norm(U) * np.linalg.norm(S)))
                R = float(np.linalg.norm(U - S) / noise[p])
                sumabs = sum(float(np.linalg.norm(x)) for x in parts)
                c = {"dose": f"{d:+.3f}", "prompt": p, "seed": s,
                     "status": "confirmatory" if abs(d) == CONFIRMATORY else "exploratory",
                     "rho": rho, "cos": cos, "R_over_N": R,
                     "U_over_N": float(np.linalg.norm(U) / noise[p]),
                     "Sigma_over_N": float(np.linalg.norm(S) / noise[p]),
                     "sum_of_part_norms_over_N": sumabs / noise[p]}
                cells.append(c); per.append(c)
            mean = lambda k: statistics.fmean(x[k] for x in per)
            rng = lambda k: f"{min(x[k] for x in per):.3f}..{max(x[k] for x in per):.3f}"
            ok = mean("cos") >= COS_MIN and RHO_LO <= mean("rho") <= RHO_HI
            summ.append({"dose": f"{d:+.3f}", "prompt": p, "status": per[0]["status"],
                         "rho_mean": mean("rho"), "rho_range": rng("rho"),
                         "cos_mean": mean("cos"), "cos_range": rng("cos"),
                         "R_over_N_mean": mean("R_over_N"), "U_over_N_mean": mean("U_over_N"),
                         "Sigma_over_N_mean": mean("Sigma_over_N"),
                         "meets_criterion": ok})
    G.write_csv(OUT_CELLS, cells)
    G.write_csv(OUT_SUMMARY, summ)

    print("\n=== PRIMARY (confirmatory, +-0.100) — composition supported only if all four meet the criterion")
    conf = [x for x in summ if x["status"] == "confirmatory"]
    for x in conf:
        print(f"  {x['dose']} {x['prompt']}  rho={x['rho_mean']:.3f} [{x['rho_range']}]  "
              f"cos={x['cos_mean']:.3f} [{x['cos_range']}]  R/N={x['R_over_N_mean']:.2f}  "
              f"|U|/N={x['U_over_N_mean']:.2f}  |Sigma|/N={x['Sigma_over_N_mean']:.2f}  "
              f"{'meets' if x['meets_criterion'] else 'FAILS'}")
    verdict = all(x["meets_criterion"] for x in conf) and len(conf) == 4
    print(f"  VERDICT: composition {'SUPPORTED' if verdict else 'NOT SUPPORTED'}")
    print("\n=== EXPLORATORY doses (not pre-registered; cannot change the verdict)")
    for x in summ:
        if x["status"] == "exploratory":
            print(f"  {x['dose']} {x['prompt']}  rho={x['rho_mean']:.3f} [{x['rho_range']}]  "
                  f"cos={x['cos_mean']:.3f} [{x['cos_range']}]  R/N={x['R_over_N_mean']:.2f}  "
                  f"{'meets' if x['meets_criterion'] else 'fails'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--guards", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.extract: extract()
    if a.guards: guards()
    if a.run: run()
    if not (a.extract or a.guards or a.run): ap.error("--extract, --guards or --run")


if __name__ == "__main__":
    main()
