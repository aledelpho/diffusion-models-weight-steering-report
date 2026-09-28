# -*- coding: utf-8 -*-
"""
experiments/groove_or_hole.py
=============================
A groove or a hole? Targeted presets and the model's repertoire.

Governed by docs/prereg_groove_or_hole.md and its amendment 01. Committed before it was run.

Modes, in the order they must be used:

  python experiments/groove_or_hole.py --prepare   # extract features for benches K and D, cache, stop
  python experiments/groove_or_hole.py --guards    # G0a, G0b, G1, G1b, G2, G3, G4; writes the guard table, stop
  python experiments/groove_or_hole.py --run       # the study. Refuses while §7 reads PENDING,
                                                   # or while any guard has not passed.

Nothing in --prepare or --guards computes a Δout for a targeted unit. G0 recomputes two numbers
already published by the parent study, to prove the distance machinery is the parent's.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import os
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"
PREREG = DOCS / "prereg_groove_or_hole.md"

# Where renders may live. The first root that holds <bench>/renders/<file> wins.
RENDER_ROOTS = [
    Path(os.environ.get("GROOVE_RENDER_ROOT", os.path.expanduser("~/mnt"))),
    Path(os.path.expanduser("~/mnt/comfyui-pilot/output")),
    Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"),
    Path(r"C:\Users\aless\Desktop\comfyui-pilot\output"),
]

CLOUD_CSV = DATA / "mountain_base_features_style.csv"
CLOUD_ROWS_EXPECTED = 409
META = {"file", "prompt_id", "seed", "width_px", "height_px", "condition", "prompt_dir",
        "prompt_sha1", "rel_path", "source_manifest"}

OUT_GUARDS = DATA / "groove_guards.csv"
OUT_CELLS = DATA / "groove_cells.csv"
OUT_COND = DATA / "groove_by_condition.csv"
OUT_TESTS = DATA / "groove_tests.csv"
CACHE_K = DATA / "style_features_blk16_ladder.csv"
CACHE_D = DATA / "style_features_profondita.csv"

V_MIN = 1.0          # §3.2
L_MIN = 0.98         # §3.3
LINE_SCENES = {"S1", "S2", "S8"}   # §3.3, bench Q
MAPPA_DOSES = ["0.020", "0.035", "0.050", "0.080", "0.120", "0.200"]
TOL_G0 = 5e-5

RETRO_BENCH = {
    "M": "benchmark_mappa--renders",
    "K": "benchmark_blk16_ladder/renders",
    "D+": "benchmark_profondita/renders",
    "D-": "benchmark_profondita_neg/renders",
    "Q": "benchmark_qkvo_atlas--renders",
    "Qb": "benchmark_atlas_phase1--renders",
}


# ----------------------------------------------------------------------------- small helpers
def sha10(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


def dist(a, b) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def sign_flip(diffs: list[float]) -> tuple[float, float]:
    n = len(diffs)
    obs = abs(statistics.fmean(diffs))
    hits = sum(1 for s in itertools.product((1, -1), repeat=n)
               if abs(statistics.fmean(a * d for a, d in zip(s, diffs))) >= obs - 1e-12)
    return hits / 2 ** n, 2 / 2 ** n


def holm(ps: list[float]) -> list[float]:
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out, running = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, ps[i] * (len(ps) - rank)))
        out[i] = running
    return out


def spearman(x: list[float], y: list[float]) -> float:
    def ranks(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def read_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(p: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def find_render(bench: str, fn: str) -> Path | None:
    for r in RENDER_ROOTS:
        for c in (r / bench / "renders" / fn, r / bench / fn):
            if c.is_file():
                return c
    return None


# ----------------------------------------------------------------------------- PNG metadata
def png_graph(path: Path) -> dict | None:
    from PIL import Image
    with Image.open(path) as im:
        raw = im.info.get("prompt")
    return json.loads(raw) if raw else None


def _follow_text(g: dict, node_id: str, depth: int = 0) -> str | None:
    if depth > 10 or node_id not in g:
        return None
    inp = g[node_id].get("inputs", {})
    if isinstance(inp.get("text"), str):
        return inp["text"]
    for key in ("conditioning", "conditioning_1", "positive", "text"):
        v = inp.get(key)
        if isinstance(v, list) and v:
            t = _follow_text(g, str(v[0]), depth + 1)
            if t is not None:
                return t
    for v in inp.values():
        if isinstance(v, list) and v and isinstance(v[0], (str, int)):
            t = _follow_text(g, str(v[0]), depth + 1)
            if t is not None:
                return t
    return None


def png_record(path: Path) -> dict:
    """Positive prompt hash and sampler settings, read from the render's own graph."""
    from PIL import Image
    g = png_graph(path)
    with Image.open(path) as im:
        size = f"{im.width}x{im.height}"
    if not g:
        return {"ok": False, "why": "no graph", "size": size}
    samplers = [(k, v) for k, v in g.items() if "Sampler" in v.get("class_type", "")
                and isinstance(v.get("inputs", {}).get("positive"), list)]
    if len(samplers) != 1:
        return {"ok": False, "why": f"{len(samplers)} sampler nodes", "size": size}
    _, node = samplers[0]
    inp = node["inputs"]
    text = _follow_text(g, str(inp["positive"][0]))
    if text is None:
        return {"ok": False, "why": "positive text not found", "size": size}
    seed = inp.get("seed", inp.get("noise_seed"))
    return {"ok": True, "sha": sha10(text), "seed": seed, "steps": inp.get("steps"),
            "cfg": inp.get("cfg"), "sampler": inp.get("sampler_name"),
            "scheduler": inp.get("scheduler"), "denoise": inp.get("denoise"), "size": size}


# ----------------------------------------------------------------------------- the cloud
def load_cloud() -> tuple[list[dict], list[str], list[float], list[float]]:
    rows = read_csv(CLOUD_CSV)
    if len(rows) != CLOUD_ROWS_EXPECTED:
        sys.exit(f"cloud has {len(rows)} rows, the pre-registration froze {CLOUD_ROWS_EXPECTED}")
    feats = [c for c in rows[0].keys() if c not in META]
    vecs = [[float(r[c]) for c in feats] for r in rows]
    mu = [statistics.fmean(v[i] for v in vecs) for i in range(len(feats))]
    sd = [statistics.stdev(v[i] for v in vecs) for i in range(len(feats))]
    cloud = []
    for r, v in zip(rows, vecs):
        cloud.append({"file": r["file"], "prompt_id": r["prompt_id"], "seed": int(r["seed"]),
                      "raw": v, "z": [(v[i] - mu[i]) / sd[i] for i in range(len(feats))]})
    return cloud, feats, mu, sd


def manifest_sha_index() -> dict[str, str]:
    idx: dict[str, str] = {}
    for m in sorted(DATA.glob("*.csv")):
        try:
            rows = read_csv(m)
        except Exception:
            continue
        if not rows:
            continue
        cols = rows[0].keys()
        fcol = next((c for c in ("file", "image_path", "rel_path", "expected_filename") if c in cols), None)
        if not fcol or not ({"prompt_sha1", "prompt_text"} & set(cols)):
            continue
        for r in rows:
            fn = os.path.basename((r.get(fcol) or "").replace("\\", "/"))
            if not fn or fn in idx:
                continue
            if r.get("prompt_text"):
                idx[fn] = sha10(r["prompt_text"])
            elif r.get("prompt_sha1"):
                idx[fn] = r["prompt_sha1"][:10]
    return idx


def resolve_cloud_sha(cloud: list[dict]) -> list[str]:
    idx = manifest_sha_index()
    missing = []
    for b in cloud:
        sha = idx.get(b["file"])
        if sha is None:
            for bench in ("benchmark_pavimento_rumore", "benchmark_latenti_b6"):
                p = find_render(bench, b["file"])
                if p:
                    rec = png_record(p)
                    if rec["ok"]:
                        sha = rec["sha"]
                    break
        b["sha"] = sha
        if sha is None:
            missing.append(b["file"])
    return missing


# ----------------------------------------------------------------------------- feature tables
def feat_table(path: Path, feats: list[str]) -> dict[str, list[float]]:
    return {r["file"]: [float(r[c]) for c in feats] for r in read_csv(path)}


def z_of(v, mu, sd):
    return [(v[i] - mu[i]) / sd[i] for i in range(len(v))]


def coherence_table() -> dict[tuple[str, str], float]:
    return {(r["bench"], r["file"]): float(r["coherence"]) for r in read_csv(DATA / "retro_texture_axes.csv")}


# ----------------------------------------------------------------------------- the four benches
RX_M = re.compile(r"^(P0[12])_Block_(\d)(pos|neg)_([0-9.]+)_krea2_seed(\d+)_00001_\.png$")
RX_K = re.compile(r"^(P0[12])_blk16(pos|neg)_([0-9.]+)_krea2_seed(\d+)_00001_\.png$")
RX_D = re.compile(r"^(P0[12])_blk(\d\d)(pos|neg)_0\.200_krea2_seed(\d+)_00001_\.png$")
RX_Q = re.compile(r"^(S\d)_([a-z]+)_Arthemy_QKVO_(w[qkvo])_(b[16])_(pos|neg)_seed(\d+)_00001_\.png$")


def mappa_base(p: str, s: str) -> str:
    return f"{p}_baseline_krea2_seed{s}_00001_.png"


def atlas_base(scene: str, style: str, s: str) -> str:
    return f"{scene}_{style}_baseline_seed{s}_00001_.png"


def list_cells(feats) -> list[dict]:
    """Every perturbed cell of the four benches, with its baseline. No distance is computed here."""
    cells = []
    for r in read_csv(DATA / "style_features_mappa.csv"):
        m = RX_M.match(r["file"])
        if m:
            p, g, sign, dose, s = m.groups()
            cells.append({"bench": "M", "unit": f"Block_{g}", "sign": sign, "dose": dose, "prompt": p,
                          "seed": s, "file": r["file"], "render_bench": "benchmark_mappa",
                          "base_file": mappa_base(p, s), "base_bench": "benchmark_mappa",
                          "retro": RETRO_BENCH["M"], "base_retro": RETRO_BENCH["M"]})
    for sub, key in (("benchmark_blk16_ladder", "K"),):
        for p in sorted(find_bench_files(sub)):
            m = RX_K.match(p)
            if m:
                pr, sign, dose, s = m.groups()
                cells.append({"bench": "K", "unit": "blk16", "sign": sign, "dose": dose, "prompt": pr,
                              "seed": s, "file": p, "render_bench": sub, "base_file": mappa_base(pr, s),
                              "base_bench": "benchmark_mappa", "retro": RETRO_BENCH["K"],
                              "base_retro": RETRO_BENCH["M"]})
    for sub, rkey in (("benchmark_profondita", "D+"), ("benchmark_profondita_neg", "D-")):
        for p in sorted(find_bench_files(sub)):
            m = RX_D.match(p)
            if m:
                pr, b, sign, s = m.groups()
                cells.append({"bench": "D", "unit": f"blk{b}", "sign": sign, "dose": "0.200", "prompt": pr,
                              "seed": s, "file": p, "render_bench": sub, "base_file": mappa_base(pr, s),
                              "base_bench": "benchmark_mappa", "retro": RETRO_BENCH[rkey],
                              "base_retro": RETRO_BENCH["M"]})
    for r in read_csv(DATA / "style_features_qkvo.csv"):
        m = RX_Q.match(r["file"])
        if m:
            scene, style, proj, band, sign, s = m.groups()
            cells.append({"bench": "Q", "unit": f"{proj}_{band}", "sign": sign, "dose": "-", "prompt": scene,
                          "style": style, "seed": s, "file": r["file"], "render_bench": "benchmark_qkvo_atlas",
                          "base_file": atlas_base(scene, style, s), "base_bench": "benchmark_atlas_phase1",
                          "retro": RETRO_BENCH["Q"], "base_retro": RETRO_BENCH["Qb"]})
    return cells


def find_bench_files(bench: str) -> list[str]:
    for r in RENDER_ROOTS:
        d = r / bench / "renders"
        if d.is_dir():
            return [p.name for p in d.glob("*.png")]
    return []


# ----------------------------------------------------------------------------- --prepare
def prepare(feats) -> None:
    sys.path.insert(0, str(ROOT / "experiments"))
    from style_features import extract_all_features
    for cache, benches, rx in ((CACHE_K, ["benchmark_blk16_ladder"], RX_K),
                               (CACHE_D, ["benchmark_profondita", "benchmark_profondita_neg"], RX_D)):
        done = {r["file"] for r in read_csv(cache)} if cache.exists() else set()
        rows = read_csv(cache) if cache.exists() else []
        todo = [(b, f) for b in benches for f in sorted(find_bench_files(b)) if rx.match(f) and f not in done]
        print(f"{cache.name}: {len(done)} cached, {len(todo)} to extract", flush=True)
        for i, (b, f) in enumerate(todo, 1):
            d = extract_all_features(str(find_render(b, f)))
            rows.append({"file": f, "bench": b, **{c: d[c] for c in feats}})
            if i % 12 == 0 or i == len(todo):
                write_csv(cache, rows)
                print(f"  {i}/{len(todo)}", flush=True)


# ----------------------------------------------------------------------------- --guards
def guard_g0(cloud, feats, mu, sd) -> list[dict]:
    out = []
    # G0a — stage 9, preset_pos_1x, cloud standardisation, prompt-id matching (parent §2)
    by_key = {(b["prompt_id"], b["seed"]): b for b in cloud}
    s9 = read_csv(DATA / "style_features_stage9.csv")
    per_prompt: dict[str, list[float]] = {}
    for r in s9:
        if r.get("condition") != "preset_pos_1x":
            continue
        p = (r.get("prompt_dir") or "").split("_")[0]
        base = by_key.get((p, int(r["seed"])))
        if not base:
            continue
        ze = z_of([float(r[c]) for c in feats], mu, sd)
        d_e = min(dist(ze, b["z"]) for b in cloud if b["prompt_id"] != p)
        d_b = min(dist(base["z"], b["z"]) for b in cloud if b["prompt_id"] != p)
        per_prompt.setdefault(p, []).append(d_e - d_b)
    means = [statistics.fmean(v) for v in per_prompt.values()]
    g0a = statistics.fmean(means) if means else float("nan")
    out.append({"guard": "G0a", "target": 0.530427, "observed": round(g0a, 6),
                "n_prompts": len(means), "pass": abs(g0a - 0.530427) < TOL_G0})
    # G0b — stage 7, preset_pos, standardised on the stage-7 baselines (parent amendment 01 §7)
    s7 = read_csv(DATA / "style_features_stage7.csv")
    s7b = [r for r in s7 if r.get("condition") == "baseline"]
    mu7 = [statistics.fmean(float(r[c]) for r in s7b) for c in feats]
    sd7 = [statistics.stdev(float(r[c]) for r in s7b) for c in feats]
    c7 = [{"prompt_id": b["prompt_id"], "seed": b["seed"], "file": b["file"], "z": z_of(b["raw"], mu7, sd7)}
          for b in cloud]
    s7b_files = {r["file"] for r in s7b}
    base7 = {}
    for b in c7:
        if b["file"] in s7b_files:
            base7[(b["prompt_id"], b["seed"])] = min(dist(b["z"], o["z"]) for o in c7
                                                     if o["prompt_id"] != b["prompt_id"])
    prompts7 = ["I01", "I02", "I05", "I06", "I07", "I09", "I10", "I11",
                "I12", "I16", "I17", "I18", "I20", "I21", "I23", "I24"]
    pvals, stats7 = [], {}
    for arm in ("preset_pos", "blockshuf_neg", "rand_pos"):
        pp: dict[str, list[float]] = {}
        for r in s7:
            if (r.get("condition") or r.get("arm")) != arm:
                continue
            p = r.get("prompt_dir") or r.get("prompt_id")
            if p not in prompts7 or (p, int(r["seed"])) not in base7:
                continue
            ze = z_of([float(r[c]) for c in feats], mu7, sd7)
            d_e = min(dist(ze, o["z"]) for o in c7 if o["prompt_id"] != p)
            pp.setdefault(p, []).append(d_e - base7[(p, int(r["seed"]))])
        pm = [statistics.fmean(pp[p]) for p in prompts7 if p in pp]
        pv, _ = sign_flip(pm)
        stats7[arm] = statistics.fmean(pm)
        pvals.append(pv)
    ph = holm(pvals)
    out.append({"guard": "G0b", "target": "0.501902 / holm 0.002441",
                "observed": f"{stats7['preset_pos']:.6f} / holm {ph[0]:.6f}", "n_prompts": 16,
                "pass": abs(stats7["preset_pos"] - 0.501902) < TOL_G0 and abs(ph[0] - 0.002441) < TOL_G0})
    return out


def guards(cloud, feats, mu, sd) -> list[dict]:
    rows = guard_g0(cloud, feats, mu, sd)
    if not all(r["pass"] for r in rows):
        return rows  # the machinery is not the parent's: nothing else is worth checking

    # G2 — every cloud row must resolve to a prompt text
    missing = resolve_cloud_sha(cloud)
    rows.append({"guard": "G2-cloud", "target": "409 resolved", "observed": f"{409 - len(missing)} resolved",
                 "n_prompts": len({b['sha'] for b in cloud if b['sha']}), "pass": not missing,
                 "detail": ";".join(missing[:10])})

    cells = list_cells(feats)
    recs: dict[tuple[str, str], dict] = {}

    def rec(bench, fn):
        k = (bench, fn)
        if k not in recs:
            p = find_render(bench, fn)
            recs[k] = png_record(p) if p else {"ok": False, "why": "not on disk"}
        return recs[k]

    # G1 — baseline identity; G2 — one text per tested prompt; G3 — dead edits
    import numpy as np
    from PIL import Image
    g1_fail: dict[str, list[str]] = {}
    texts: dict[tuple[str, str], set] = {}
    dead_by_cond: dict[tuple, list[bool]] = {}
    for c in cells:
        re_, rb = rec(c["render_bench"], c["file"]), rec(c["base_bench"], c["base_file"])
        bad = None
        if not re_.get("ok") or not rb.get("ok"):
            bad = f"{c['file']}: {re_.get('why') or rb.get('why')}"
        else:
            for k in ("sha", "seed", "steps", "cfg", "sampler", "scheduler", "denoise", "size"):
                if re_.get(k) != rb.get(k):
                    bad = f"{c['file']}: {k} {re_.get(k)} != {rb.get(k)}"
                    break
        if bad:
            g1_fail.setdefault(c["bench"], []).append(bad)
        else:
            texts.setdefault((c["bench"], c["prompt"]), set()).add(re_["sha"])
            c["sha"] = re_["sha"]
        pe, pb = find_render(c["render_bench"], c["file"]), find_render(c["base_bench"], c["base_file"])
        dead = False
        if pe and pb:
            a = np.asarray(Image.open(pe).convert("RGB"), dtype=np.int16)
            b = np.asarray(Image.open(pb).convert("RGB"), dtype=np.int16)
            dead = a.shape == b.shape and int(np.abs(a - b).max()) == 0
        c["dead"] = dead
        dead_by_cond.setdefault((c["bench"], c["unit"], c["sign"], c["dose"]), []).append(dead)
    for bench in ("M", "K", "D", "Q"):
        n = sum(1 for c in cells if c["bench"] == bench)
        f = g1_fail.get(bench, [])
        rows.append({"guard": f"G1-{bench}", "target": "0 mismatches", "observed": f"{len(f)} of {n}",
                     "n_prompts": len({c['prompt'] for c in cells if c['bench'] == bench}),
                     "pass": n > 0 and not f, "detail": " | ".join(f[:5])})
    multi = {k: v for k, v in texts.items() if len(v) > 1}
    rows.append({"guard": "G2-tested", "target": "one text per tested prompt",
                 "observed": f"{len(multi)} prompts with >1 text", "n_prompts": len(texts),
                 "pass": not multi, "detail": str(sorted(multi))[:300]})
    excluded = [k for k, v in dead_by_cond.items() if sum(v) > 0.10 * len(v)]
    rows.append({"guard": "G3", "target": "dead cells flagged, conditions >10% dead excluded",
                 "observed": f"{sum(c['dead'] for c in cells)} dead cells, {len(excluded)} conditions excluded",
                 "n_prompts": "", "pass": True, "detail": str(excluded)[:300]})

    # G4 — cloud coverage per tested prompt text
    cloud_shas = {b["sha"] for b in cloud if b["sha"]}
    low = []
    for sha in {c.get("sha") for c in cells if c.get("sha")}:
        n_other = len(cloud_shas - {sha})
        if n_other < 40:
            low.append((sha, n_other))
    rows.append({"guard": "G4", "target": ">= 40 other prompts in B", "observed": f"{len(low)} prompts below",
                 "n_prompts": len(cloud_shas), "pass": not low, "detail": str(low)})

    # G1b — the same extractor on both sides (amendment 01 §3)
    sys.path.insert(0, str(ROOT / "experiments"))
    from style_features import extract_all_features
    cached = feat_table(DATA / "style_features_mappa.csv", feats)
    worst, fails = 0.0, []
    for p in ("P01", "P02"):
        for s in ("42", "777", "1337"):
            fn = mappa_base(p, s)
            fresh = extract_all_features(str(find_render("benchmark_mappa", fn)))
            for i, col in enumerate(feats):
                tol = 0.05 if col.startswith("color_") else 0.01
                dev = abs(float(fresh[col]) - cached[fn][i]) / sd[i]
                worst = max(worst, dev)
                if dev > tol:
                    fails.append(f"{fn}:{col}:{dev:.3f}sd")
    rows.append({"guard": "G1b", "target": "fresh vs cached baseline features within tolerance",
                 "observed": f"worst {worst:.4f} sd, {len(fails)} over tolerance", "n_prompts": 2,
                 "pass": True, "detail": ("K and D will use FRESH baselines: " + ";".join(fails[:8])) if fails
                 else "cached baselines used"})
    return rows


# ----------------------------------------------------------------------------- --run
def prediction_filled() -> bool:
    txt = PREREG.read_text(encoding="utf-8")
    sec = txt.split("## 7.")[1].split("**Analyst.**")[0]
    return "PENDING" not in sec


def run(cloud, feats, mu, sd) -> None:
    if not prediction_filled():
        sys.exit("§7 of the pre-registration still reads PENDING. Alessandro's prediction comes first.")
    if not OUT_GUARDS.exists():
        sys.exit("run --guards first")
    g = read_csv(OUT_GUARDS)
    if not all(r["pass"] == "True" for r in g):
        sys.exit("at least one guard has not passed; see data/groove_guards.csv")
    fresh_base = any(r["guard"] == "G1b" and r["detail"].startswith("K and D will use FRESH") for r in g)

    resolve_cloud_sha(cloud)
    cells = list_cells(feats)
    coh = coherence_table()
    fm = feat_table(DATA / "style_features_mappa.csv", feats)
    fq = feat_table(DATA / "style_features_qkvo.csv", feats)
    fa = feat_table(DATA / "style_features_atlas_phase1.csv", feats)
    fk = feat_table(CACHE_K, feats)
    fd = feat_table(CACHE_D, feats)
    if fresh_base:
        sys.path.insert(0, str(ROOT / "experiments"))
        from style_features import extract_all_features
        fresh = {}
        for p in ("P01", "P02"):
            for s in ("42", "777", "1337"):
                fn = mappa_base(p, s)
                d = extract_all_features(str(find_render("benchmark_mappa", fn)))
                fresh[fn] = [float(d[c]) for c in feats]
    src = {"M": fm, "K": fk, "D": fd, "Q": fq}

    # prompt text of each tested prompt, from its baseline render
    shas: dict[tuple[str, str], str] = {}
    dead_cond: dict[tuple, list[bool]] = {}
    from PIL import Image
    import numpy as np
    out_cells = []
    for c in cells:
        key = (c["bench"], c["prompt"])
        if key not in shas:
            shas[key] = png_record(find_render(c["base_bench"], c["base_file"]))["sha"]
        sha = shas[key]
        pe, pb = find_render(c["render_bench"], c["file"]), find_render(c["base_bench"], c["base_file"])
        a = np.asarray(Image.open(pe).convert("RGB"), dtype=np.int16)
        b = np.asarray(Image.open(pb).convert("RGB"), dtype=np.int16)
        dead = a.shape == b.shape and int(np.abs(a - b).max()) == 0
        dead_cond.setdefault((c["bench"], c["unit"], c["sign"], c["dose"]), []).append(dead)
        if c["bench"] == "Q":
            base_raw = fa[c["base_file"]]
        elif c["bench"] in ("K", "D") and fresh_base:
            base_raw = fresh[c["base_file"]]
        else:
            base_raw = fm[c["base_file"]]
        ze, zb = z_of(src[c["bench"]][c["file"]], mu, sd), z_of(base_raw, mu, sd)
        others = [o["z"] for o in cloud if o["sha"] != sha]
        d_e, d_b = min(dist(ze, o) for o in others), min(dist(zb, o) for o in others)
        ce, cb = coh.get((c["retro"], c["file"])), coh.get((c["base_retro"], c["base_file"]))
        out_cells.append({**{k: c.get(k, "") for k in ("bench", "unit", "sign", "dose", "prompt", "seed", "file")},
                          "prompt_sha": sha, "dead": dead, "d_out_edit": round(d_e, 6), "d_out_base": round(d_b, 6),
                          "delta_out": round(d_e - d_b, 6), "coherence_ratio": round(ce / cb, 6) if ce and cb else "",
                          "_ze": ze, "_zb": zb})
    excluded = {k for k, v in dead_cond.items() if sum(v) > 0.10 * len(v)}
    live = [c for c in out_cells if not c["dead"]
            and (c["bench"], c["unit"], c["sign"], c["dose"]) not in excluded]

    # N(p): seed-noise unit (§3.2, amendment 01 §2b)
    def noise_unit(bench, prompt, sha):
        zs = [o["z"] for o in cloud if o["sha"] == sha]
        source = "cloud"
        if len(zs) < 3:
            source = "bench"
            zs = []
            for s in ("42", "777", "1337"):
                ex = next(c for c in cells if c["bench"] == bench and c["prompt"] == prompt)
                raw = fa[ex["base_file"].replace(f"seed{ex['seed']}", f"seed{s}")] if bench == "Q" \
                    else fm[mappa_base(prompt, s)]
                zs.append(z_of(raw, mu, sd))
        return statistics.median(dist(a, b) for a, b in itertools.combinations(zs, 2)), source

    # per (bench, unit, sign, dose, prompt)
    units: dict[tuple, list[dict]] = {}
    for c in live:
        units.setdefault((c["bench"], c["unit"], c["sign"], c["dose"], c["prompt"]), []).append(c)
    by_prompt = []
    for (bench, unit, sign, dose, prompt), cs in sorted(units.items()):
        nfac, nsrc = noise_unit(bench, prompt, cs[0]["prompt_sha"])
        mean_diff = [statistics.fmean(c["_ze"][i] - c["_zb"][i] for c in cs) for i in range(len(feats))]
        V = math.sqrt(sum(x * x for x in mean_diff)) / nfac
        crs = [c["coherence_ratio"] for c in cs if c["coherence_ratio"] != ""]
        by_prompt.append({"bench": bench, "unit": unit, "sign": sign, "dose": dose, "prompt": prompt,
                          "n_seeds": len(cs), "mean_delta_out": round(statistics.fmean(c["delta_out"] for c in cs), 6),
                          "cells_negative": sum(c["delta_out"] < 0 for c in cs),
                          "V": round(V, 4), "n_source": nsrc, "noise_unit": round(nfac, 4),
                          "L": round(statistics.fmean(crs), 4) if crs else ""})

    # verdicts
    tests = []
    conds: dict[tuple, list[dict]] = {}
    for r in by_prompt:
        conds.setdefault((r["bench"], r["unit"], r["sign"], r["dose"]), []).append(r)
    q_rows = []
    for (bench, unit, sign, dose), rs in sorted(conds.items()):
        cells_c = [c for c in live if (c["bench"], c["unit"], c["sign"], c["dose"]) == (bench, unit, sign, dose)]
        if bench in ("M", "K", "D"):
            both_visible = len(rs) == 2 and all(r["V"] >= V_MIN for r in rs)
            both_line = len(rs) == 2 and all(r["L"] != "" and r["L"] >= L_MIN for r in rs)
            neg = sum(c["delta_out"] < 0 for c in cells_c)
            pos = sum(c["delta_out"] > 0 for c in cells_c)
            each_neg = all(r["mean_delta_out"] < 0 for r in rs)
            if not both_visible:
                verdict = "invisible"
            elif both_line and neg == 6 and each_neg:
                verdict = "groove_candidate"
            elif pos == 6:
                verdict = "hole"
            else:
                verdict = "undecided"
            tests.append({"stage": "screen", "bench": bench, "unit": unit, "sign": sign, "dose": dose,
                          "cells_negative": neg, "cells_positive": pos, "n_cells": len(cells_c),
                          "p_sign_test": round(2 * 0.5 ** 6, 4) if neg in (0, 6) and len(cells_c) == 6 else "",
                          "V_min": min(r["V"] for r in rs), "L_min": min((r["L"] for r in rs if r["L"] != ""), default=""),
                          "mean_delta_out": round(statistics.fmean(r["mean_delta_out"] for r in rs), 6),
                          "verdict": verdict})
        else:
            pm = [r["mean_delta_out"] for r in rs]
            p, floor = sign_flip(pm) if len(pm) >= 2 else (float("nan"), float("nan"))
            lr = [r["L"] for r in rs if r["prompt"] in LINE_SCENES and r["L"] != ""]
            q_rows.append({"stage": "confirmatory", "bench": bench, "unit": unit, "sign": sign, "dose": dose,
                           "n_scenes": len(pm), "scenes_negative": sum(x < 0 for x in pm),
                           "mean_delta_out": round(statistics.fmean(pm), 6), "p_sign_flip": round(p, 6),
                           "p_floor": round(floor, 6), "V_median": round(statistics.median(r["V"] for r in rs), 4),
                           "L_line_scenes": round(statistics.fmean(lr), 4) if lr else ""})
    for r, ph in zip(q_rows, holm([r["p_sign_flip"] for r in q_rows])):
        r["p_holm"] = round(ph, 6)
        vis = r["V_median"] >= V_MIN
        line = r["L_line_scenes"] != "" and r["L_line_scenes"] >= L_MIN
        if ph < 0.05 and r["mean_delta_out"] < 0 and vis and line:
            r["verdict"] = "confirmed_groove"
        elif ph < 0.05 and r["mean_delta_out"] > 0 and vis:
            r["verdict"] = "confirmed_hole"
        else:
            r["verdict"] = "invisible" if not vis else "undecided"
        tests.append(r)

    # dose curves (M, K), descriptive
    for bench in ("M", "K"):
        for unit, sign in sorted({(r["unit"], r["sign"]) for r in by_prompt if r["bench"] == bench}):
            pts = sorted((float(r["dose"]), r["mean_delta_out"]) for r in by_prompt
                         if r["bench"] == bench and r["unit"] == unit and r["sign"] == sign)
            doses = sorted({d for d, _ in pts})
            curve = [statistics.fmean(v for d2, v in pts if d2 == d) for d in doses]
            tests.append({"stage": "dose_curve", "bench": bench, "unit": unit, "sign": sign,
                          "dose": "all", "spearman_dose_delta": round(spearman(doses, curve), 4),
                          "top_dose_delta": round(curve[-1], 6),
                          "verdict": "hole_signature" if spearman(doses, curve) > 0 and curve[-1] > 0 else "no_hole_signature"})

    # pooled count (§4.3, amendment 01 §2c)
    visible = [r for r in by_prompt if r["V"] >= V_MIN]
    holes = sum(r["mean_delta_out"] > 0 for r in visible)
    cands = [t for t in tests if t.get("verdict") == "groove_candidate"]
    confirmed = [t for t in tests if t.get("verdict") == "confirmed_groove"]
    if confirmed:
        claim = "supported (pending G_eye)"
    elif cands:
        claim = "screen only (Stage B licensed, pending G_eye)"
    elif visible and holes >= len(visible) / 2:
        claim = "not supported"
    else:
        claim = "undecided"
    tests.append({"stage": "verdict", "bench": "all", "unit": "-", "sign": "-", "dose": "-",
                  "visible_units": len(visible), "visible_holes": holes, "groove_candidates": len(cands),
                  "confirmed_grooves": len(confirmed), "dead_conditions_excluded": len(excluded), "verdict": claim})

    write_csv(OUT_CELLS, [{k: v for k, v in c.items() if not k.startswith("_")} for c in out_cells])
    write_csv(OUT_COND, by_prompt)
    write_csv(OUT_TESTS, tests)
    print(f"verdict: {claim}; visible units {len(visible)}, of which holes {holes}; "
          f"candidates {len(cands)}; confirmed {len(confirmed)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--guards", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = ap.parse_args()
    cloud, feats, mu, sd = load_cloud()
    if args.prepare:
        prepare(feats)
    elif args.guards:
        rows = guards(cloud, feats, mu, sd)
        write_csv(OUT_GUARDS, rows)
        for r in rows:
            print(f"{r['guard']:<10} {'PASS' if r['pass'] else 'FAIL'}  {r['observed']}  {r.get('detail', '')[:120]}")
        sys.exit(0 if all(r["pass"] for r in rows) else 1)
    else:
        run(cloud, feats, mu, sd)


if __name__ == "__main__":
    main()
