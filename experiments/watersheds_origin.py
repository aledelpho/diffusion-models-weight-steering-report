"""C97 - fragile places: replication, starting noise vs content, prompt micro-changes (docs/prereg_watersheds_origin.md).
Written 2026-10-18 after the pre-registration, before any C97 render.

  python watersheds_origin.py --selftest
  python watersheds_origin.py --plan            # data/watersheds_origin_plan.csv (108 rows; already committed)
  python watersheds_origin.py --queue --block gate
  python watersheds_origin.py --gate            # 2 x "max abs diff 0", then GATE PASS
  python watersheds_origin.py --queue --block main
  python watersheds_origin.py --count           # expected 108 missing 0 []
  python watersheds_origin.py --noise           # GPU venv (torch): data/watersheds_origin_noise.npz
  python watersheds_origin.py --analyze         # numpy/scipy: data/watersheds_origin_*.csv
"""
import argparse, csv, itertools, json, statistics, sys, urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import micro_watersheds as MW

DATA = HERE.parent / "data"
PLAN = DATA / "watersheds_origin_plan.csv"
NOISE = DATA / "watersheds_origin_noise.npz"
FOLDER = "benchmark_watersheds_origin"
SEEDS = ["3141592", "2645751", "1618033", "2718281", "3316624", "4123105"]
W = {"W1": (27, 0.004), "W2": (27, -0.004), "W3": (0, -0.010), "W4": (10, -0.010), "W5": (23, 0.010)}
MICRO = {
    "P3_archerforest": [("M1", "reflect every detail", "reflect each detail"),
                        ("M2", "A sense of depth", "A feeling of depth"),
                        ("M3", "The lighting is dim and dappled", "The lighting is low and dappled")],
    "D1_dwarf_paladin": [("M1", "resolute stern expression", "resolute, stern expression"),
                         ("M2", "simple background", "plain background"),
                         ("M3", "close-up portrait", "closeup portrait")],
}
GATES = {("P3_archerforest", "3141592"): "benchmark_hood_threshold/P3_archerforest_baseline_krea2_seed3141592_00001_.png",
         ("D1_dwarf_paladin", "2645751"): "benchmark_portraits/phase_c/D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png"}
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
       "width": "1024", "height": "1280"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def texts():
    t = {}
    for r in rd(DATA / "hood_threshold_plan.csv"):
        t["P3_archerforest"] = r["prompt_text"]; break
    for r in rd(DATA / "portraits_preset_plan.csv"):
        if r["char"] == "D1_dwarf_paladin" and r["cond"] == "baseline":
            t["D1_dwarf_paladin"] = r["prompt_text"]; break
    for p, ms in MICRO.items():
        for _, a, _b in ms:
            assert t[p].count(a) == 1, (p, a)
    return t


def vec(b, d):
    v = ["0.0"] * 34; v[b] = repr(float(d)); return ",".join(v)


def make_plan():
    tx = texts(); rows = []
    for p in MICRO:
        for s in SEEDS:
            conds = [("base", "", tx[p])] + [(k, vec(b, d), tx[p]) for k, (b, d) in W.items()] + \
                    [(m, "", tx[p].replace(a, b)) for m, a, b in MICRO[p]]
            for cid, vo, text in conds:
                prefix = f"{p}_{cid}_krea2_seed{s}"
                block = "gate" if cid == "base" and (p, s) in GATES else "main"
                rows.append({"row": len(rows), "block": block, "prompt_id": p, "seed": s, "cond": cid, "vectors_override": vo,
                             "prompt_text": text, "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    assert len(rows) == 108
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("plan rows:", len(rows), dict(Counter(r["block"] for r in rows)))


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(block=None):
    n = 0
    for r in rd(PLAN):
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


def root():
    return MW.img_root()


REPRO = {"W1": "benchmark_null_patch/P3_archerforest_N3_blk27_p0.004_krea2_seed3141592_00001_.png",
         "W2": "benchmark_null_patch/P3_archerforest_N4_blk27_m0.004_krea2_seed3141592_00001_.png",
         "W3": "benchmark_hood_threshold/P3_archerforest_blk00_neg_d0.010_krea2_seed3141592_00001_.png",
         "W4": "benchmark_hood_threshold/P3_archerforest_blk10_neg_d0.010_krea2_seed3141592_00001_.png",
         "W5": "benchmark_hood_threshold/P3_archerforest_blk23_pos_d0.010_krea2_seed3141592_00001_.png"}


def gate():
    """Bases against earlier renders; after the main block, also the archer's five weight edits at 3141592 against
    C55/C56 (checked when present)."""
    ok = True
    for k, ref in REPRO.items():
        a = root() / FOLDER / f"P3_archerforest_{k}_krea2_seed3141592_00001_.png"
        if a.exists():
            d = int(np.abs(MW.load(a) - MW.load(root() / ref)).max())
            print(f"P3_archerforest seed 3141592 {k} vs {ref}: max abs diff {d}"); ok &= d == 0
    for (p, s), ref in GATES.items():
        a, b = root() / FOLDER / f"{p}_base_krea2_seed{s}_00001_.png", root() / ref
        if not a.exists():
            print(p, s, "MISSING", a); ok = False; continue
        d = int(np.abs(MW.load(a) - MW.load(b)).max())
        print(f"{p} seed {s} base vs {ref}: max abs diff {d}"); ok &= d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def noise():
    """Initial latent noise as ComfyUI's prepare_noise draws it: torch.manual_seed(seed), randn of the latent shape on
    CPU. Krea-2 uses the Qwen-Image VAE (16 channels, 8x downsampling)."""
    import torch
    out = {}
    for s in SEEDS:
        g = torch.manual_seed(int(s))
        out[f"s{s}"] = torch.randn((1, 16, 1280 // 8, 1024 // 8), generator=g, device="cpu").numpy()[0]
    np.savez_compressed(NOISE, **out); print("wrote", NOISE, {k: v.shape for k, v in out.items()})


def logE(base, im):
    d = np.abs(im - base).max(axis=2).astype(np.float32)
    return np.log1p(MW.patches(d ** 2).ravel()), float(d.mean())


def resid(y, *zs):
    A = np.vstack([*zs, np.ones_like(y)]).T
    return y - A @ np.linalg.lstsq(A, y, rcond=None)[0]


def pcorr(a, b, *zs):
    return float(np.corrcoef(resid(a, *zs), resid(b, *zs))[0, 1])


def analyze_cells(cells):
    """cells: {(prompt, seed): {"base": img, "W1".. "W5": img, "M1".."M3": img}} -> rows, tests, F maps."""
    R, out, F, T = [], [], {}, {}
    r1 = {}; r2 = []; mag = {"W": [], "M": []}
    for (p, s), ims in sorted(cells.items()):
        base = ims["base"]; t = np.log1p(MW.texture(base).ravel()); T[(p, s)] = t
        E = {}
        for k in [*W, "M1", "M2", "M3"]:
            E[k], m = logE(base, ims[k]); mag[k[0]].append(m)
        pr = [pcorr(E[a], E[b], t) for a, b in itertools.combinations(list(W), 2)]
        r1[(p, s)] = statistics.median(pr)
        Wm = np.mean([E[k] for k in W], axis=0)
        F[(p, s)] = resid(Wm, t)
        for m in ("M1", "M2", "M3"):
            v = pcorr(E[m], Wm, t); r2.append(v)
            R.append({"prompt": p, "seed": s, "what": f"{m} vs mean W", "value": round(v, 4)})
        R.append({"prompt": p, "seed": s, "what": "R1 median pairwise W", "value": round(r1[(p, s)], 4)})
    n_ok = sum(v >= 0.30 for v in r1.values()); n = len(r1)
    v1 = "replicated" if n_ok >= 0.75 * n else ("not replicated" if n_ok <= n / 3 else "mixed")
    out.append({"test": "R1 replication: cells with median pairwise W partial r >= 0.30", "value": f"{n_ok} of {n}; " + " ".join(f"{p[:2]}/{s}:{v:.2f}" for (p, s), v in sorted(r1.items())), "verdict": v1})
    for p in sorted({p for p, _ in r1}):
        out.append({"test": f"R1 {p} (reported)", "value": f"{sum(v >= 0.30 for (q, _), v in r1.items() if q == p)} of {sum(q == p for q, _ in r1)}", "verdict": ""})
    m2 = statistics.median(r2)
    out.append({"test": "R2 prompt micro-changes hit the same places (median partial r, M vs mean W)", "value": f"{m2:.3f} over {len(r2)}",
                "verdict": "supported" if m2 >= 0.30 else ("refuted" if m2 <= 0.10 else "inconclusive")})
    out.append({"test": "R2 size of changes (reported)", "value": f"mean delta W {statistics.median(mag['W']):.2f}, M {statistics.median(mag['M']):.2f} (medians)", "verdict": ""})
    prompts = sorted({p for p, _ in F})
    if len(prompts) == 2:
        a, b = prompts; seeds = sorted({s for _, s in F})
        same = [pcorr(F[(a, s)], F[(b, s)], T[(a, s)], T[(b, s)]) for s in seeds]
        diff = [pcorr(F[(a, s)], F[(b, u)], T[(a, s)], T[(b, u)]) for s in seeds for u in seeds if u != s]
        from scipy.stats import mannwhitneyu
        p = float(mannwhitneyu(same, diff, alternative="greater").pvalue)
        dlt = statistics.mean(same) - statistics.mean(diff)
        v3 = "noise sets the places" if dlt >= 0.15 and p < 0.05 else ("not the noise" if dlt < 0.05 else "inconclusive")
        out.append({"test": "R3 same-seed vs different-seed similarity of fragility maps across prompts", "value": f"same {statistics.mean(same):+.3f} (n {len(same)}), different {statistics.mean(diff):+.3f} (n {len(diff)}), difference {dlt:+.3f}, Mann-Whitney p {p:.4f}", "verdict": v3})
    return R, out, F


def noise_stats(F, nz):
    """Reported: per-patch Spearman between F and the starting noise under the patch (16 px = 2x2 latent cells)."""
    from scipy.stats import spearmanr
    from scipy.ndimage import uniform_filter
    rows = []
    for name, fn in (("mean", lambda z: z.mean(0)), ("mean_abs", lambda z: np.abs(z).mean(0)),
                     ("lowfreq_energy", lambda z: (uniform_filter(z, size=(1, 8, 8)) ** 2).mean(0))):
        xs, ys = [], []
        for (p, s), f in F.items():
            z = nz[f"s{s}"]; m = fn(z)                                # (160, 128) latent cells
            m = m.reshape(80, 2, 64, 2).mean(axis=(1, 3)).ravel()       # 16-px patches
            xs.append(m[: len(f)]); ys.append(f)
        rows.append({"test": f"R4 Spearman(F, noise {name}) pooled (reported)", "value": f"{spearmanr(np.concatenate(xs), np.concatenate(ys)).correlation:+.3f}", "verdict": ""})
    return rows


def analyze():
    rows = rd(PLAN); cells = {}
    for r in rows:
        p = root() / FOLDER / r["expected_filename"]
        if not p.exists():
            sys.exit(f"missing {p}")
        cells.setdefault((r["prompt_id"], r["seed"]), {})[r["cond"]] = MW.load(p)
    R, out, F = analyze_cells(cells)
    if NOISE.exists():
        out += noise_stats(F, np.load(NOISE))
    for fn, data in (("watersheds_origin_cells.csv", R), ("watersheds_origin_tests.csv", out)):
        with open(DATA / fn, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


def _synth(rng, fragile, h=256, w=256, texture=None):
    base = np.full((h, w, 3), 90, np.int16)
    if texture is not None:
        base[texture] += rng.integers(0, 50, base[texture].shape).astype(np.int16)
    ims = {"base": base}
    for k in [*W, "M1", "M2", "M3"]:
        im = base.copy()
        for (y, x) in fragile:
            if rng.random() < 0.7:
                im[y:y + 16, x:x + 16] = 200
        im += rng.integers(-2, 3, im.shape).astype(np.int16); ims[k] = im
    return ims


def selftest():
    rng = np.random.default_rng(3)
    t = np.zeros((256, 256), bool); t[:, :64] = True
    seed_spots = {s: [(int(rng.integers(0, 15)) * 16, int(rng.integers(5, 15)) * 16) for _ in range(8)] for s in SEEDS[:4]}
    # noise world: the same places at a seed for both prompts
    cells = {(p, s): _synth(rng, seed_spots[s], texture=(slice(None), slice(0, 64))) for p in MICRO for s in SEEDS[:4]}
    _, out, _ = analyze_cells(cells)
    d = {o["test"].split(" ")[0]: o for o in out if not o["test"].endswith("(reported)")}
    assert d["R1"]["verdict"] == "replicated", d["R1"]
    assert d["R2"]["verdict"] == "supported", d["R2"]
    assert d["R3"]["verdict"] == "noise sets the places", d["R3"]
    # content world: places differ by prompt, not by seed
    cells = {(p, s): _synth(rng, [(int(rng.integers(0, 15)) * 16, int(rng.integers(5, 15)) * 16) for _ in range(8)],
                            texture=(slice(None), slice(0, 64))) for p in MICRO for s in SEEDS[:4]}
    _, out, _ = analyze_cells(cells)
    d = {o["test"].split(" ")[0]: o for o in out if not o["test"].endswith("(reported)")}
    assert d["R3"]["verdict"] == "not the noise", d["R3"]
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a in ("plan", "queue", "gate", "count", "noise", "analyze", "selftest"):
        ap.add_argument(f"--{a}", action="store_true")
    ap.add_argument("--block", default=None)
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.plan: make_plan()
    if a.queue: queue(a.block)
    if a.gate: gate()
    if a.count: count()
    if a.noise: noise()
    if a.analyze: analyze()
