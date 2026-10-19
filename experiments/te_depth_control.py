"""C102 - is a deep text-encoder edit more controllable than an early one, at the same push? (docs/prereg_te_depth_control.md)
Written 2026-10-19 with the pre-registration, before any encode or render.

  python te_depth_control.py --selftest
  python te_depth_control.py --encode          # GPU, ComfyUI venv: matched-push conditionings -> Text2Img/benchmark_te_depth_control/conds/*.pt,
                                               # data/te_depth_control_encoder.csv, data/te_depth_control_plan.csv
  python te_depth_control.py --queue --block gate
  python te_depth_control.py --gate            # 3 x "max abs diff 0", then GATE PASS
  python te_depth_control.py --queue --block main
  python te_depth_control.py --count           # expected 156 missing 0 []
  python te_depth_control.py --analyze         # GPU: DINOv2 -> data/te_depth_control_metrics.csv, data/te_depth_control_dino.npz
  python te_depth_control.py --rules           # numpy: data/te_depth_control_tests.csv (blind rule once the labels exist)
"""
import argparse, csv, itertools, json, statistics, sys, urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
DATA = HERE.parent / "data"
PLAN = DATA / "te_depth_control_plan.csv"
ENC = DATA / "te_depth_control_encoder.csv"
METRICS = DATA / "te_depth_control_metrics.csv"
VECS = DATA / "te_depth_control_dino.npz"
LABELS = DATA / "te_depth_control_labels.csv"
KEY = DATA / "te_depth_control_key.csv"
TESTS = DATA / "te_depth_control_tests.csv"
FOLDER = "benchmark_te_depth_control"
PROMPTS = ["D1_dwarf_paladin", "S1_rally", "C4_stilllife", "P5_comic_panels"]
SEEDS = ["2645751", "3316624", "2718281"]
EDITS = {"L04": 4, "L09": 9, "L26": 26, "L30": 30}
CTRLS = {"R09": 9, "R26": 26}
LEVELS = {"t1": 0.5, "t2": 1.0}                    # anchors: tau of L06 MLP at these doses
ANCHOR = 6
D_MAX, A_MAX, TOL = 6.0, 20.0, 0.01
GATES = {("D1_dwarf_paladin", "2645751"): "benchmark_portraits/phase_c/D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png",
         ("S1_rally", "2718281"): "benchmark_single_blocks_atlas/renders/S1_rally_baseline_krea2_seed2718281_00001_.png",
         ("C4_stilllife", "2718281"): "benchmark_single_blocks_styles/renders/C4_stilllife_baseline_krea2_seed2718281_00001_.png"}
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
       "width": "1024", "height": "1280"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def img_root():
    import blk23_colorful as c47
    return c47.IMG_ROOT if c47.IMG_ROOT.exists() else Path.home() / "mnt" / "Text2Img"


def conds():
    out = ["C0"]
    for lv in LEVELS:
        out += [f"{e}_{lv}" for e in EDITS] + [f"{c}_{lv}" for c in CTRLS]
    return out


def texts():
    import te_shapes2 as TS2
    t = TS2.texts()
    return {p: t[p] for p in PROMPTS}


def gj(L, d):
    return {f"layers.{L}.mlp.{m}_proj.weight": d for m in ("gate", "up", "down")}


def cond_path(p, c):
    import blk23_colorful as c47
    return c47.IMG_ROOT / FOLDER / "conds" / f"{p}_{c}.pt"


def bisect(f, target, hi):
    """Smallest-bracket bisection for f(x) = target on [0, hi]; returns (x, f(x), iterations) or None if f(hi) < target."""
    fh = f(hi)
    if fh < target:
        return None
    lo, n = 0.0, 1
    x, fx = hi, fh
    while abs(fx - target) / target > TOL and n < 40:
        x = (lo + hi) / 2; fx = f(x); n += 1
        if fx < target:
            lo = x
        else:
            hi = x
    return x, fx, n


# ---------------------------------------------------------------- encodes (GPU)
def encode():
    import torch
    import te_punct_encoder as TPE
    import te_layer0_encoder as TLE
    import te_shapes as TS
    base = TPE.gate()
    layers = TS._layers(base)
    def raw(clip, text):
        tokens = clip.tokenize(text)
        return clip.encode_from_tokens(tokens, return_pooled=False, return_dict=True)["cond"].detach().cpu().clone()
    (cond_path("x", "x").parent).mkdir(parents=True, exist_ok=True)
    rows = []
    for p, text in texts().items():
        c0 = raw(base, text); c0f = c0.float()
        tau = lambda c: float(torch.linalg.vector_norm(c.float() - c0f) / torch.linalg.vector_norm(c0f))
        torch.save(c0, cond_path(p, "C0"))
        targets = {lv: tau(raw(TLE.apply_te_edit(base, gj(ANCHOR, d)), text)) for lv, d in LEVELS.items()}
        cap = {}
        def grab(L):
            def h(m, a, o):
                cap[L] = (o[0] if isinstance(o, tuple) else o).detach().float().clone()
            return h
        hs = [layers[L].mlp.register_forward_hook(grab(L)) for L in CTRLS.values()]
        raw(base, text)
        for h in hs:
            h.remove()
        for lv, tg in targets.items():
            for name, L in EDITS.items():
                last = {}
                def f(d):
                    c = raw(TLE.apply_te_edit(base, gj(L, d)), text); last["c"] = c; return tau(c)
                res = bisect(f, tg, D_MAX)
                rows.append(save(p, f"{name}_{lv}", "edit", L, lv, tg, res, last, torch))
            for name, L in CTRLS.items():
                g = torch.Generator(device="cpu").manual_seed(9393)
                R = torch.randn(cap[L].shape, generator=g); R = R / torch.linalg.vector_norm(R, dim=-1, keepdim=True)
                n = torch.linalg.vector_norm(cap[L], dim=-1, keepdim=True).cpu()
                last = {}
                def f(a, L=L, R=R, n=n):
                    add = R * n * a
                    h = layers[L].mlp.register_forward_hook(lambda m, ar, o: o + add.to(o.device, o.dtype))
                    try:
                        c = raw(base, text)
                    finally:
                        h.remove()
                    last["c"] = c; return tau(c)
                res = bisect(f, tg, A_MAX)
                rows.append(save(p, f"{name}_{lv}", "control", L, lv, tg, res, last, torch))
        print("done", p, {k: round(v, 4) for k, v in targets.items()}, flush=True)
    with open(ENC, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("wrote", ENC, len(rows))
    make_plan(rows)


def save(p, c, kind, L, lv, tg, res, last, torch):
    row = {"prompt": p, "cond": c, "kind": kind, "layer": L, "level": lv, "target_tau": round(tg, 6)}
    if res is None:
        print("UNREACHABLE", p, c, flush=True)
        return {**row, "tau": "", "dose_or_scale": "", "iterations": "", "reached": 0}
    x, fx, n = res
    torch.save(last["c"], cond_path(p, c))
    return {**row, "tau": round(fx, 6), "dose_or_scale": round(x, 5), "iterations": n, "reached": 1}


# ---------------------------------------------------------------- renders
def make_plan(enc_rows):
    tx = texts()
    ok = {(r["prompt"], r["cond"]) for r in enc_rows if int(r["reached"])}
    rows = []
    def add(block, p, s, c):
        prefix = f"{p}_{c}_krea2_seed{s}"
        rows.append({"row": len(rows), "block": block, "char": p, "seed": s, "cond": c, "variant": "file",
                     "push_path": str(cond_path(p, c)), "noise_seed": 7, "taps": "", "te_granular_json": "{}",
                     "prompt_text": tx[p], "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    for (p, s) in GATES:
        add("gate", p, s, "C0")
    for p in PROMPTS:
        for s in SEEDS:
            for c in conds():
                if (p, s) in GATES and c == "C0":
                    continue
                if c == "C0" or (p, c) in ok:
                    add("main", p, s, c)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows), "(156 if every target was reached)")


def workflow(r):
    import te_massive as TM
    wf = TM.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(block=None):
    import blk23_colorful as c47
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


def gate():
    from PIL import Image
    R = img_root(); ok = True
    for (p, s), ref in GATES.items():
        a = R / FOLDER / f"{p}_C0_krea2_seed{s}_00001_.png"
        if not a.exists():
            print("missing", a.name); ok = False; continue
        A = np.asarray(Image.open(a).convert("RGB"), dtype=np.int16); B = np.asarray(Image.open(R / ref).convert("RGB"), dtype=np.int16)
        d = int(np.abs(A - B).max()); print(f"{a.name} vs {Path(ref).name}: max abs diff {d}"); ok &= d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    R = img_root(); rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (R / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = img_root(); m = MV.Models(vqa=False)
    keys, vecs, out = [], [], []
    for r in rd(PLAN):
        v = np.asarray(m.dino_vec(Image.open(R / FOLDER / r["expected_filename"]).convert("RGB")), dtype=np.float32)
        keys.append(f"{r['char']}|{r['seed']}|{r['cond']}"); vecs.append(v)
    V = dict(zip(keys, vecs))
    for k, v in V.items():
        p, s, c = k.split("|"); b = V[f"{p}|{s}|C0"]
        out.append({"prompt": p, "seed": s, "cond": c, "dinov2_dist_to_base": round(1 - float(v @ b / (np.linalg.norm(v) * np.linalg.norm(b))), 6)})
    np.savez_compressed(VECS, keys=np.array(keys), vecs=np.stack(vecs))
    with open(METRICS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("wrote", METRICS, len(out), "and", VECS)


# ---------------------------------------------------------------- rules (numpy)
def _cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def kappa(V, p, c):
    D = [V[(p, s, c)] - V[(p, s, "C0")] for s in SEEDS if (p, s, c) in V]
    if len(D) < 2:
        return None
    return statistics.mean(_cos(a, b) for a, b in itertools.combinations(D, 2))


def kappa_seeds(V, p, c, seeds):
    D = [V[(p, s, c)] - V[(p, s, "C0")] for s in seeds if (p, s, c) in V]
    if len(D) < 2:
        return None
    return statistics.mean(_cos(a, b) for a, b in itertools.combinations(D, 2))


def rules(V, labels=None, key=None):
    out = []
    K = {(p, c): kappa(V, p, c) for p in PROMPTS for c in conds()[1:]}
    cells = [(p, lv) for p in PROMPTS for lv in LEVELS]
    d09 = {c: (K[(c[0], f"L09_{c[1]}")] - K[(c[0], f"R09_{c[1]}")]) for c in cells if K.get((c[0], f"L09_{c[1]}")) is not None and K.get((c[0], f"R09_{c[1]}")) is not None}
    d26 = {c: (K[(c[0], f"L26_{c[1]}")] - K[(c[0], f"R26_{c[1]}")]) for c in cells if K.get((c[0], f"L26_{c[1]}")) is not None and K.get((c[0], f"R26_{c[1]}")) is not None}
    n26 = sum(v >= 0.10 for v in d26.values()); n09hi = sum(v >= 0.10 for v in d09.values())
    n09lo = sum(v < 0.10 for v in d09.values()); n26lo = sum(v < 0.10 for v in d26.values())
    if n26 >= 6 and n09lo >= 6: v1 = "depth gives the edit a direction in the picture"
    elif n26 >= 6 and n09hi >= 6: v1 = "both have a direction"
    elif n26lo >= 6 and n09lo >= 6: v1 = "neither"
    else: v1 = "mixed"
    out.append({"test": "Rule 1 dkappa (edit - its random control), L26 and L09, 8 cells",
                "value": f"L26 >= 0.10 in {n26}/{len(d26)}; L09 < 0.10 in {n09lo}/{len(d09)}; "
                         f"L26 {' '.join(f'{v:+.2f}' for v in d26.values())}; L09 {' '.join(f'{v:+.2f}' for v in d09.values())}",
                "verdict": v1})
    for e, ctrl in (("L04", "R09"), ("L30", "R26")):
        vals = [K[(p, f"{e}_{lv}")] - K[(p, f"{ctrl}_{lv}")] for p, lv in cells
                if K.get((p, f"{e}_{lv}")) is not None and K.get((p, f"{ctrl}_{lv}")) is not None]
        if vals:
            out.append({"test": f"Rule 3 dkappa {e} against {ctrl} (reported)", "value": f"median {statistics.median(vals):+.3f}; >= 0.10 in {sum(x >= 0.10 for x in vals)}/{len(vals)}", "verdict": ""})
    dist = lambda p, s, c: 1 - _cos(V[(p, s, c)], V[(p, s, "C0")])
    less, tot = 0, 0
    for p, lv in cells:
        for s in SEEDS:
            dp = [dist(p, s, f"{e}_{lv}") for e in ("L26", "L30") if (p, s, f"{e}_{lv}") in V]
            ea = [dist(p, s, f"{e}_{lv}") for e in ("L04", "L09") if (p, s, f"{e}_{lv}") in V]
            if dp and ea:
                tot += 1; less += statistics.mean(dp) < statistics.mean(ea)
    out.append({"test": "Rule 3 at equal push the deep edits move the picture less than the early ones (reported)", "value": f"{less} of {tot}", "verdict": ""})
    out.append({"test": "Rule 3 kappa per prompt x condition (reported)",
                "value": " | ".join(f"{p[:2]}/{c}:{K[(p, c)]:.2f}" for p in PROMPTS for c in conds()[1:] if K.get((p, c)) is not None), "verdict": ""})
    if labels and key:
        sc = {"si": 1.0, "sì": 1.0, "in parte": 0.5, "inparte": 0.5, "no": 0.0}
        labels = [{"unit": r["unit"], "answer": r.get("answer") or r.get("same") or ""} for r in labels]
        labels = [r for r in labels if r["answer"].strip()]
        S = {}
        first = {}
        reps = []
        for r in labels:
            k = key[r["unit"]]; val = sc[r["answer"].strip().lower()]
            tag = (k["prompt"], k["cond"])
            if tag in first:
                reps.append((first[tag], val))
            else:
                first[tag] = val; S.setdefault(k["cond"].rsplit("_", 1)[0], []).append(val)
        m = {c: statistics.mean(v) for c, v in S.items()}
        diff = (m["L26"] - m["R26"]) - (m["L09"] - m["R09"])
        v2 = "the eye agrees" if diff >= 0.25 else "the eye does not separate them"
        out.append({"test": "Rule 2 blind: (s(L26) - s(R26)) - (s(L09) - s(R09))",
                    "value": f"{diff:+.2f}; means {' '.join(f'{c} {x:.2f}' for c, x in sorted(m.items()))}", "verdict": v2})
        if reps:
            out.append({"test": "Rule 3 blind test-retest (reported)", "value": f"{sum(a == b for a, b in reps)} of {len(reps)} identical", "verdict": ""})
        both = "supported" if v1.startswith("depth") and v2 == "the eye agrees" else ("disagreement" if v1.startswith("depth") != (v2 == "the eye agrees") else "not supported")
        out.append({"test": "Combined verdict (rules 1 and 2)", "value": "", "verdict": both})
    return out


def load_vecs():
    z = np.load(VECS)
    return {tuple(k.split("|")): v.astype(np.float64) for k, v in zip(z["keys"], z["vecs"])}


def selftest():
    assert len(conds()) == 13 and len(PROMPTS) * len(SEEDS) * len(conds()) == 156
    assert len(gj(26, 1.0)) == 3
    r = bisect(lambda x: x ** 2, 4.0, 6.0); assert r and abs(r[1] - 4) / 4 <= TOL
    assert bisect(lambda x: x, 10.0, 6.0) is None
    assert set(texts()) == set(PROMPTS)
    rng = np.random.default_rng(0)
    def synth(directed):
        V = {}
        for p in PROMPTS:
            dirs = {c: rng.standard_normal(64) for c in conds()}
            for s in SEEDS:
                b = rng.standard_normal(64); V[(p, s, "C0")] = b
                for c in conds()[1:]:
                    own = c.split("_")[0] in directed
                    V[(p, s, c)] = b + (2.0 * dirs[c] if own else 0) + rng.standard_normal(64)
        return V
    v = rules(synth({"L26", "L30"}))[0]["verdict"]; assert v == "depth gives the edit a direction in the picture", v
    v = rules(synth(set()))[0]["verdict"]; assert v == "neither", v
    v = rules(synth({"L26", "L30", "L04", "L09"}))[0]["verdict"]; assert v == "both have a direction", v
    key = {f"U{i}": {"prompt": "D1_dwarf_paladin", "cond": c} for i, c in enumerate(["L26_t1", "R26_t1", "L09_t1", "R09_t1", "L26_t1"])}
    lab = [{"unit": "U0", "answer": "sì"}, {"unit": "U1", "answer": "no"}, {"unit": "U2", "answer": "in parte"}, {"unit": "U3", "answer": "in parte"}, {"unit": "U4", "answer": "sì"}]
    o = rules(synth({"L26", "L30"}), lab, key)
    assert [x for x in o if x["test"].startswith("Rule 2")][0]["verdict"] == "the eye agrees"
    assert [x for x in o if x["test"].startswith("Combined")][0]["verdict"] == "supported"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "encode", "gate", "count", "analyze", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--queue", action="store_true"); ap.add_argument("--block")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.encode: encode()
    if a.queue: queue(a.block)
    if a.gate: gate()
    if a.count: count()
    if a.analyze: analyze()
    if a.rules:
        V = load_vecs()
        lab = rd(LABELS) if LABELS.exists() else None
        key = {r["unit"]: r for r in rd(KEY)} if KEY.exists() else None
        out = rules(V, lab, key)
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
