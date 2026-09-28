# -*- coding: utf-8 -*-
"""
experiments/analyze_centre_push.py
==================================
Can the centre be pushed further without breaking the drawing?
Governed by docs/prereg_centre_push.md. Committed before any render of the bench existed.

  python experiments/analyze_centre_push.py --extract   # features, coherence, content; resumable cache
  python experiments/analyze_centre_push.py --guards    # G_det, G1, G3, G_range, G_content
  python experiments/analyze_centre_push.py --run       # primary, S1-S4; writes the tables

Reuses unchanged: the base cloud, the z-scoring and d_out of experiments/groove_or_hole.py, the 23
features of experiments/style_features.py, and structure coherence from
experiments/retro_texture_axes.py (measure()).
"""
from __future__ import annotations

import argparse
import csv
import itertools
import math
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))

import groove_or_hole as G  # noqa: E402

BENCH = "benchmark_centre_push"
PLAN = DATA / "centre_push_plan.csv"
CACHE = DATA / "centre_push_measures.csv"
OUT_GUARDS = DATA / "centre_push_guards.csv"
OUT_UNITS = DATA / "centre_push_units.csv"
OUT_TESTS = DATA / "centre_push_tests.csv"

ENDS = {"Block_1", "Block_6"}
CENTRE = {"Block_2", "Block_3", "Block_4", "Block_5"}
V_RANGE, V_HI, L_MIN = 2.0, 1.5, 0.98
DINO_NAME = "vit_small_patch14_dinov2.lvd142m"


def render_path(fn: str) -> Path | None:
    return G.find_render(BENCH, fn)


# ----------------------------------------------------------------------------- content embedding
_dino = None


def dino_embed(path: Path):
    """CLS embedding of DINOv2 ViT-S/14 (timm), image resized so the short side is 518, centre crop."""
    global _dino
    import numpy as np
    import torch
    import timm
    from PIL import Image
    if _dino is None:
        m = timm.create_model(DINO_NAME, pretrained=True, num_classes=0).eval()
        cfg = timm.data.resolve_data_config({}, model=m)
        _dino = (m, timm.data.create_transform(**cfg))
    m, tf = _dino
    with torch.no_grad():
        v = m(tf(Image.open(path).convert("RGB")).unsqueeze(0))[0].numpy()
    return v / (np.linalg.norm(v) + 1e-12)


# ----------------------------------------------------------------------------- --extract
def extract(with_content: bool) -> None:
    from style_features import extract_all_features
    from retro_texture_axes import measure
    plan = G.read_csv(PLAN)
    rows = G.read_csv(CACHE) if CACHE.exists() else []
    done = {r["file"] for r in rows}
    cloud, feats, mu, sd = G.load_cloud()
    todo = [r for r in plan if r["expected_filename"] not in done and render_path(r["expected_filename"])]
    print(f"{len(done)} cached, {len(todo)} to measure, "
          f"{sum(1 for r in plan if not render_path(r['expected_filename']))} not on disk", flush=True)
    for i, r in enumerate(todo, 1):
        p = render_path(r["expected_filename"])
        f = extract_all_features(str(p))
        coh = measure(str(p))[0]
        row = {"file": r["expected_filename"], "coherence": coh, **{c: f[c] for c in feats}}
        if with_content:
            row["dino"] = " ".join(f"{x:.6f}" for x in dino_embed(p))
        rows.append(row)
        if i % 10 == 0 or i == len(todo):
            G.write_csv(CACHE, rows)
            print(f"  {i}/{len(todo)}", flush=True)


# ----------------------------------------------------------------------------- --guards
def guards() -> list[dict]:
    import numpy as np
    from PIL import Image
    plan = G.read_csv(PLAN)
    out = []
    # G_det — the determinism row reproduces benchmark_mappa pixel for pixel
    det = next(r for r in plan if r["arm"] == "determinism")
    a, b = render_path(det["expected_filename"]), G.find_render("benchmark_mappa", det["expected_filename"])
    same = bool(a and b) and int(np.abs(np.asarray(Image.open(a).convert("RGB"), dtype=np.int16)
                                       - np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)).max()) == 0
    out.append({"guard": "G_det", "pass": same, "detail": det["expected_filename"]})
    # G1 — every render present, its graph matches its plan row, baselines carry no tuner
    bad, dead = [], 0
    base = {(r["prompt_id"], r["seed"]): r["expected_filename"] for r in plan if r["arm"] == "baseline"}
    for r in plan:
        p = render_path(r["expected_filename"])
        if not p:
            bad.append(f"missing {r['expected_filename']}")
            continue
        rec = G.png_record(p)
        g = G.png_graph(p)
        tuner = g.get("50")
        exp_seed = int(r["seed"])
        if not rec.get("ok") or rec["sha"] != r["prompt_sha1"] or int(rec["seed"]) != exp_seed \
                or rec["steps"] != int(r["steps"]) or rec["size"] != f"{r['width']}x{r['height']}":
            bad.append(f"graph {r['expected_filename']}")
        if r["arm"] == "baseline" and tuner is not None:
            bad.append(f"tuner present in baseline {r['expected_filename']}")
        if r["arm"] in ("push", "determinism"):
            ti = (tuner or {}).get("inputs", {})
            if abs(float(ti.get(r["block_input"], 0.0)) - float(r["gain"])) > 1e-9 or ti.get("vectors_override", ""):
                bad.append(f"drive {r['expected_filename']}")
            if r["arm"] == "push":
                bp = render_path(base[(r["prompt_id"], r["seed"])])
                if bp and int(np.abs(np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
                                     - np.asarray(Image.open(bp).convert("RGB"), dtype=np.int16)).max()) == 0:
                    dead += 1
    out.append({"guard": "G1", "pass": not bad, "detail": " | ".join(bad[:8]) or "295/295"})
    out.append({"guard": "G3", "pass": dead == 0, "detail": f"{dead} perturbed renders identical to baseline"})
    return out


# ----------------------------------------------------------------------------- --run
def ols_slope(x, y):
    mx, my = statistics.fmean(x), statistics.fmean(y)
    den = sum((a - mx) ** 2 for a in x)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / den if den else float("nan")


def run() -> None:
    import numpy as np
    g = G.read_csv(OUT_GUARDS) if OUT_GUARDS.exists() else []
    if not g or not all(r["pass"] == "True" for r in g):
        sys.exit("guards missing or failed: run --guards first")
    plan = G.read_csv(PLAN)
    meas = {r["file"]: r for r in G.read_csv(CACHE)}
    cloud, feats, mu, sd = G.load_cloud()
    G.resolve_cloud_sha(cloud)

    def z(fn):
        return G.z_of([float(meas[fn][c]) for c in feats], mu, sd)

    base = {(r["prompt_id"], r["seed"]): r["expected_filename"] for r in plan if r["arm"] == "baseline"}
    sha = {r["prompt_id"]: r["prompt_sha1"] for r in plan}
    # N(p): seed-noise unit from the cloud baselines of the same text (as in groove_or_hole §3.2)
    noise = {}
    for p in sha:
        zs = [o["z"] for o in cloud if o["sha"] == sha[p]]
        noise[p] = statistics.median(G.dist(a, b) for a, b in itertools.combinations(zs, 2))
    # content noise: DINO distance between this bench's own baselines of the same prompt
    has_dino = all("dino" in meas[fn] and meas[fn]["dino"] for fn in base.values())

    def emb(fn):
        return np.array([float(x) for x in meas[fn]["dino"].split()])
    cnoise = {}
    if has_dino:
        for p in sha:
            es = [emb(base[(p, s)]) for (pp, s) in base if pp == p]
            cnoise[p] = statistics.median(1 - float(a @ b) for a, b in itertools.combinations(es, 2))

    cells = []
    for r in plan:
        if r["arm"] != "push":
            continue
        fn, bfn = r["expected_filename"], base[(r["prompt_id"], r["seed"])]
        ze, zb = z(fn), z(bfn)
        others = [o["z"] for o in cloud if o["sha"] != sha[r["prompt_id"]]]
        c = {"group": r["block_input"], "sign": "pos" if float(r["gain"]) > 0 else "neg",
             "dose": f"{abs(float(r['gain'])):.3f}", "prompt": r["prompt_id"], "seed": r["seed"], "file": fn,
             "ze": ze, "zb": zb,
             "delta_out": min(G.dist(ze, o) for o in others) - min(G.dist(zb, o) for o in others),
             "L": float(meas[fn]["coherence"]) / float(meas[bfn]["coherence"])}
        if has_dino:
            c["content"] = (1 - float(emb(fn) @ emb(bfn))) / cnoise[r["prompt_id"]]
        cells.append(c)

    units = {}
    for c in cells:
        units.setdefault((c["group"], c["sign"], c["dose"], c["prompt"]), []).append(c)
    urows = []
    for (grp, sign, dose, p), cs in sorted(units.items()):
        md = [statistics.fmean(c["ze"][i] - c["zb"][i] for c in cs) for i in range(len(feats))]
        urows.append({"group": grp, "position": "end" if grp in ENDS else "centre", "sign": sign, "dose": dose,
                      "prompt": p, "V": math.sqrt(sum(x * x for x in md)) / noise[p],
                      "L": statistics.fmean(c["L"] for c in cs),
                      "delta_out": statistics.fmean(c["delta_out"] for c in cs),
                      "content": statistics.fmean(c["content"] for c in cs) if has_dino else ""})

    # primary: slope of L on ln V per group-arm; T = mean(centre) - mean(ends); exact permutation over 495
    arms = sorted({(u["group"], u["sign"]) for u in urows})
    beta = {}
    for a in arms:
        us = [u for u in urows if (u["group"], u["sign"]) == a]
        beta[a] = ols_slope([math.log(u["V"]) for u in us], [u["L"] for u in us])
    is_end = {a: a[0] in ENDS for a in arms}

    def T(ends):
        return statistics.fmean(beta[a] for a in arms if a not in ends) - statistics.fmean(beta[a] for a in ends)
    t_obs = T({a for a in arms if is_end[a]})
    perms = [T(set(c)) for c in itertools.combinations(arms, 4)]
    p_one = sum(t >= t_obs - 1e-12 for t in perms) / len(perms)

    # range guard (G_range): >= 3 of 8 central group-arms reach V >= 2 (mean over prompts) at some dose
    reach = 0
    for a in arms:
        if is_end[a]:
            continue
        by_dose = {}
        for u in urows:
            if (u["group"], u["sign"]) == a:
                by_dose.setdefault(u["dose"], []).append(u["V"])
        reach += any(statistics.fmean(v) >= V_RANGE for v in by_dose.values())
    range_ok = reach >= 3
    if not range_ok:
        verdict = "inconclusive: the centre was not pushed far enough"
    elif t_obs > 0 and p_one <= 0.05:
        verdict = "supported"
    else:
        verdict = "not supported"

    tests = [{"test": "primary", "T": round(t_obs, 5), "p_one_sided": round(p_one, 5), "n_perm": len(perms),
              "central_arms_reaching_V2": reach, "verdict": verdict,
              "betas": "; ".join(f"{a[0]} {a[1]} {beta[a]:+.4f}" for a in arms)}]
    hi = [u for u in urows if u["V"] >= V_HI]
    for pos in ("end", "centre"):
        hs = [u for u in hi if u["position"] == pos]
        tests.append({"test": f"S1_{pos}", "n_units_V>=1.5": len(hs),
                      "share_L<0.98": round(sum(u["L"] < L_MIN for u in hs) / len(hs), 4) if hs else ""})
    vis = [u for u in urows if u["V"] >= 1.0]
    for pos in ("end", "centre"):
        vs = [u for u in vis if u["position"] == pos]
        tests.append({"test": f"S4_{pos}", "n_visible": len(vs),
                      "share_holes": round(sum(u["delta_out"] > 0 for u in vs) / len(vs), 4) if vs else ""})
    if has_dino:
        for lo, hi_ in ((1.0, 1.5), (1.5, 2.5), (2.5, 1e9)):
            for pos in ("end", "centre"):
                us = [u for u in urows if u["position"] == pos and lo <= u["V"] < hi_]
                tests.append({"test": f"S2_{pos}_V{lo}-{hi_ if hi_ < 1e9 else 'inf'}", "n": len(us),
                              "median_content": round(statistics.median(u["content"] for u in us), 4) if us else ""})
    else:
        tests.append({"test": "S2", "verdict": "dropped: content embedding not available (§5 G_content)"})

    G.write_csv(OUT_UNITS, [{k: (round(v, 6) if isinstance(v, float) else v) for k, v in u.items()} for u in urows])
    G.write_csv(OUT_TESTS, tests)
    for t in tests:
        print(t)


def main() -> None:
    ap = argparse.ArgumentParser()
    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument("--extract", action="store_true")
    m.add_argument("--guards", action="store_true")
    m.add_argument("--run", action="store_true")
    ap.add_argument("--no-content", action="store_true", help="skip the DINOv2 embedding (S2 is then dropped)")
    a = ap.parse_args()
    if a.extract:
        extract(with_content=not a.no_content)
    elif a.guards:
        rows = guards()
        G.write_csv(OUT_GUARDS, rows)
        for r in rows:
            print(r)
        sys.exit(0 if all(r["pass"] for r in rows) else 1)
    else:
        run()


if __name__ == "__main__":
    main()
