"""C103 - deep against early text-encoder edits, matched on the change in the picture (docs/prereg_te_depth_control2.md).
Written 2026-10-19 with the pre-registration, before any encode or render.

  python te_depth_control2.py --selftest
  python te_depth_control2.py --encode-cal        # GPU: ladder conditionings -> data/te_depth_control2_cal_plan.csv (100 rows)
  python te_depth_control2.py --queue --block cal
  python te_depth_control2.py --calibrate         # GPU: DINOv2 on the ladder, strengths, matched conditionings -> data/te_depth_control2_plan.csv
  python te_depth_control2.py --queue --block gate
  python te_depth_control2.py --gate              # 12 x "max abs diff 0" against C102's plain renders, GATE PASS
  python te_depth_control2.py --queue --block main
  python te_depth_control2.py --count
  python te_depth_control2.py --analyze           # GPU: DINOv2 -> data/te_depth_control2_metrics.csv, _dino.npz
  python te_depth_control2.py --page              # blind page Text2Img/occhio_C103.html and data/te_depth_control2_key.csv
  python te_depth_control2.py --rules
"""
import argparse, csv, itertools, json, math, os, random, statistics, sys, urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_depth_control as T

DATA = HERE.parent / "data"
CALPLAN = DATA / "te_depth_control2_cal_plan.csv"
CALM = DATA / "te_depth_control2_calibration.csv"
STRENGTH = DATA / "te_depth_control2_strengths.csv"
PLAN = DATA / "te_depth_control2_plan.csv"
METRICS = DATA / "te_depth_control2_metrics.csv"
VECS = DATA / "te_depth_control2_dino.npz"
KEY = DATA / "te_depth_control2_key.csv"
LABELS = DATA / "te_depth_control2_labels.csv"
TESTS = DATA / "te_depth_control2_tests.csv"
FOLDER = "benchmark_te_depth_control2"
PROMPTS, SEEDS = T.PROMPTS, T.SEEDS
CAL_SEED = "1618033"
LADDER = {"L04": [0.5, 0.75, 1.0, 1.25], "L09": [0.5, 0.75, 1.0, 1.25], "L26": [1.5, 3.0, 5.0, 8.0], "L30": [1.5, 3.0, 5.0, 8.0],
          "R09": [1.5, 2.25, 3.0, 4.0], "R26": [6.0, 12.0, 24.0, 48.0]}
LAYER = {"L04": 4, "L09": 9, "L26": 26, "L30": 30, "R09": 9, "R26": 26}
TARGETS = {"t1": 0.12, "t2": 0.30}
NAMES = ["L04", "L09", "L26", "L30", "R09", "R26"]
SET = T.SET


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def conds():
    return ["C0"] + [f"{n}_{lv}" for lv in TARGETS for n in NAMES]


def cpath(p, tag):
    import blk23_colorful as c47
    return c47.IMG_ROOT / FOLDER / "conds" / f"{p}_{tag}.pt"


def stag(x):
    return f"{x:g}".replace(".", "p")


# ---------------------------------------------------------------- encoder (GPU)
class Enc:
    def __init__(self):
        import torch
        import te_punct_encoder as TPE, te_layer0_encoder as TLE, te_shapes as TS
        self.torch, self.TLE = torch, TLE
        self.base = TPE.gate(); self.layers = TS._layers(self.base); self.tx = T.texts(); self.cap = {}

    def raw(self, clip, text):
        tokens = clip.tokenize(text)
        return clip.encode_from_tokens(tokens, return_pooled=False, return_dict=True)["cond"].detach().cpu().clone()

    def baseline_mlp(self, p):
        torch = self.torch; cap = {}
        def grab(L):
            def h(m, a, o):
                cap[L] = (o[0] if isinstance(o, tuple) else o).detach().float().clone()
            return h
        hs = [self.layers[L].mlp.register_forward_hook(grab(L)) for L in (9, 26)]
        self.raw(self.base, self.tx[p])
        for h in hs:
            h.remove()
        self.cap[p] = cap

    def cond(self, p, name, x):
        torch = self.torch; text = self.tx[p]; L = LAYER[name]
        if name.startswith("L"):
            return self.raw(self.TLE.apply_te_edit(self.base, T.gj(L, x)), text)
        if p not in self.cap:
            self.baseline_mlp(p)
        c = self.cap[p][L]
        g = torch.Generator(device="cpu").manual_seed(9393)
        R = torch.randn(c.shape, generator=g); R = R / torch.linalg.vector_norm(R, dim=-1, keepdim=True)
        add = R * torch.linalg.vector_norm(c, dim=-1, keepdim=True).cpu() * x
        h = self.layers[L].mlp.register_forward_hook(lambda m, a, o: o + add.to(o.device, o.dtype))
        try:
            return self.raw(self.base, text)
        finally:
            h.remove()


def row(block, p, s, tag, path):
    prefix = f"{p}_{tag}_krea2_seed{s}"
    return {"block": block, "char": p, "seed": s, "cond": tag, "variant": "file", "push_path": str(path), "noise_seed": 7,
            "taps": "", "te_granular_json": "{}", "prompt_text": T.texts()[p], "output_prefix": prefix,
            "expected_filename": f"{prefix}_00001_.png", **SET}


def write(path, rows):
    for i, r in enumerate(rows):
        r["row"] = i
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["row"] + [k for k in rows[0] if k != "row"]); w.writeheader(); w.writerows(rows)


def encode_cal():
    E = Enc(); torch = E.torch
    cpath("x", "x").parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in PROMPTS:
        torch.save(E.raw(E.base, E.tx[p]), cpath(p, "C0")); rows.append(row("cal", p, CAL_SEED, "C0", cpath(p, "C0")))
        for n in NAMES:
            for x in LADDER[n]:
                tag = f"cal_{n}_{stag(x)}"
                c = E.cond(p, n, x)
                if not bool(torch.isfinite(c.float()).all()):
                    print("NONFINITE", p, tag, flush=True); continue
                torch.save(c, cpath(p, tag)); rows.append(row("cal", p, CAL_SEED, tag, cpath(p, tag)))
        print("done", p, flush=True)
    write(CALPLAN, rows); print("wrote", CALPLAN, len(rows))


def interp(ladder, d, target):
    """ladder: strengths ascending, d: DINOv2 distances. Log-strength interpolation at the first crossing of target;
    (0, 0) is the lowest point (linear between 0 and the first rung). None if never reached."""
    xs, ys = [0.0] + list(ladder), [0.0] + list(d)
    for i in range(1, len(xs)):
        if ys[i] >= target:
            x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
            if y1 == y0:
                return x1
            f = (target - y0) / (y1 - y0)
            if x0 == 0:
                return x1 * f
            return math.exp(math.log(x0) + f * (math.log(x1) - math.log(x0)))
    return None


def calibrate():
    from PIL import Image
    import metric_validation as MV
    R = T.img_root(); m = MV.Models(vqa=False)
    vec = lambda r: np.asarray(m.dino_vec(Image.open(R / FOLDER / r["expected_filename"]).convert("RGB")), dtype=np.float64)
    cal = rd(CALPLAN); dist = {}; out = []
    for p in PROMPTS:
        b = vec([r for r in cal if r["char"] == p and r["cond"] == "C0"][0])
        for r in cal:
            if r["char"] == p and r["cond"] != "C0":
                v = vec(r); d = 1 - float(v @ b / (np.linalg.norm(v) * np.linalg.norm(b)))
                _, n, xs = r["cond"].split("_"); x = float(xs.replace("p", "."))
                dist[(p, n, x)] = d; out.append({"prompt": p, "cond": n, "strength": x, "dinov2_dist": round(d, 6)})
    with open(CALM, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    E = Enc(); torch = E.torch; st, rows = [], []
    for p in PROMPTS:
        for n in NAMES:
            lad = [x for x in LADDER[n] if (p, n, x) in dist]
            for lv, tg in TARGETS.items():
                x = interp(lad, [dist[(p, n, y)] for y in lad], tg)
                st.append({"prompt": p, "cond": f"{n}_{lv}", "target": tg, "strength": "" if x is None else round(x, 5), "reached": int(x is not None)})
                if x is None:
                    print("UNREACHABLE", p, n, lv, flush=True); continue
                torch.save(E.cond(p, n, x), cpath(p, f"{n}_{lv}"))
        print("calibrated", p, flush=True)
    with open(STRENGTH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(st[0])); w.writeheader(); w.writerows(st)
    ok = {(s["prompt"], s["cond"]) for s in st if s["reached"]}
    for p in PROMPTS:
        for s in SEEDS:
            rows.append(row("gate", p, s, "C0", cpath(p, "C0")))
    for p in PROMPTS:
        for s in SEEDS:
            for c in conds()[1:]:
                if (p, c) in ok:
                    rows.append(row("main", p, s, c, cpath(p, c)))
    write(PLAN, rows); print("wrote", CALM, STRENGTH, "and", PLAN, len(rows), "(156 if every target was reached)")


# ---------------------------------------------------------------- renders
def workflow(r):
    import te_massive as TM
    wf = TM.workflow(r); wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(block):
    import blk23_colorful as c47
    plan = CALPLAN if block == "cal" else PLAN
    n = 0
    for r in rd(plan):
        if r["block"] != block or (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def gate():
    from PIL import Image
    R = T.img_root(); ok = True
    for p in PROMPTS:
        for s in SEEDS:
            a, b = R / FOLDER / f"{p}_C0_krea2_seed{s}_00001_.png", R / T.FOLDER / f"{p}_C0_krea2_seed{s}_00001_.png"
            if not a.exists():
                print("missing", a.name); ok = False; continue
            d = int(np.abs(np.asarray(Image.open(a).convert("RGB"), dtype=np.int16) - np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)).max())
            print(f"{a.name}: max abs diff {d}"); ok &= d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    R = T.img_root()
    for plan in (CALPLAN, PLAN):
        rows = rd(plan); miss = [r["expected_filename"] for r in rows if not (R / FOLDER / r["expected_filename"]).exists()]
        print(plan.name, "expected", len(rows), "missing", len(miss), miss[:3])


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = T.img_root(); m = MV.Models(vqa=False); keys, vecs = [], []
    for r in rd(PLAN):
        keys.append(f"{r['char']}|{r['seed']}|{r['cond']}")
        vecs.append(np.asarray(m.dino_vec(Image.open(R / FOLDER / r["expected_filename"]).convert("RGB")), dtype=np.float32))
    V = dict(zip(keys, vecs)); out = []
    for k, v in V.items():
        p, s, c = k.split("|"); b = V[f"{p}|{s}|C0"]
        out.append({"prompt": p, "seed": s, "cond": c, "dinov2_dist_to_base": round(1 - float(v @ b / (np.linalg.norm(v) * np.linalg.norm(b))), 6)})
    np.savez_compressed(VECS, keys=np.array(keys), vecs=np.stack(vecs))
    with open(METRICS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("wrote", METRICS, len(out), "and", VECS)


# ---------------------------------------------------------------- blind page
OPTS = [("stesso", "stesso modo"), ("diversi", "in modi diversi"), ("nonsivede", "non si vede")]


def page():
    from eye_grid_page import thumb, build
    R = T.img_root(); root = str(R); rng = random.Random(10303)
    have = {(r["char"], r["cond"]) for r in rd(PLAN) if r["block"] == "main"}
    base = sorted({(p, c) for p, c in have}); rng.shuffle(base)
    reps = rng.sample(base, 6); order = list(base)
    for r in reps:
        i = order.index(r); order.insert(rng.randint(min(i + 10, len(order)), len(order)), r)
    key, units, seen = [], [], set()
    for n, (p, c) in enumerate(order, 1):
        uid = f"V{n:02d}"; key.append({"unit": uid, "prompt": p, "cond": c, "repeat": int((p, c) in seen)}); seen.add((p, c))
        rows = []
        for k, s in enumerate(SEEDS, 1):
            a = thumb(str(R / FOLDER / f"{p}_C0_krea2_seed{s}_00001_.png"), root); b = thumb(str(R / FOLDER / f"{p}_{c}_krea2_seed{s}_00001_.png"), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["unit", "prompt", "cond", "repeat"]); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_C103.html"), "C103 · lo stesso cambiamento?", units,
          [("same", "Nelle tre coppie l'immagine cambia nello stesso modo?", OPTS)], OPTS, "c103_labels_v1", "te_depth_control2_labels.csv")
    print("units", len(units), "->", os.path.join(root, "occhio_C103.html"))


# ---------------------------------------------------------------- rules (numpy)
def rules(V, labels=None, key=None):
    out = []
    cos = T._cos
    dist = lambda p, s, c: 1 - cos(V[(p, s, c)], V[(p, s, "C0")])
    matched = {}
    for lv, tg in TARGETS.items():
        for n in NAMES:
            c = f"{n}_{lv}"; ds = [dist(p, s, c) for p in PROMPTS for s in SEEDS if (p, s, c) in V]
            md = statistics.median(ds) if ds else 0.0
            matched[c] = bool(ds) and md >= 0.5 * tg
            out.append({"test": f"Rule 0 realized median D, {c} (target {tg})", "value": f"{md:.3f} over {len(ds)}", "verdict": "matched" if matched[c] else "not matched"})
    testable = any(matched[f"L26_{lv}"] and matched[f"R26_{lv}"] for lv in TARGETS)
    K = {(p, c): T.kappa_seeds(V, p, c, SEEDS) for p in PROMPTS for c in conds()[1:]}
    cells = [(p, lv) for p in PROMPTS for lv in TARGETS]
    def dk(e, r):
        return {c: K[(c[0], f"{e}_{c[1]}")] - K[(c[0], f"{r}_{c[1]}")] for c in cells
                if K[(c[0], f"{e}_{c[1]}")] is not None and K[(c[0], f"{r}_{c[1]}")] is not None}
    d26, d09 = dk("L26", "R26"), dk("L09", "R09")
    if not testable or not d26 or not d09:
        v1 = "not testable"
    else:
        q = lambda d, f: sum(f(x) for x in d.values()) / len(d)
        a26, l09 = q(d26, lambda x: x >= 0.10), q(d09, lambda x: x < 0.10)
        if a26 >= 0.75 and l09 >= 0.75: v1 = "depth gives the edit a direction in the picture"
        elif a26 >= 0.75 and q(d09, lambda x: x >= 0.10) >= 0.75: v1 = "both have a direction"
        elif q(d26, lambda x: x < 0.10) >= 0.75 and l09 >= 0.75: v1 = "neither"
        else: v1 = "mixed"
    out.append({"test": "Rule 1 dkappa L26-R26 and L09-R09",
                "value": f"L26 {' '.join(f'{x:+.2f}' for x in d26.values())}; L09 {' '.join(f'{x:+.2f}' for x in d09.values())}", "verdict": v1})
    for e, r in (("L04", "R09"), ("L30", "R26")):
        d = dk(e, r)
        if d:
            out.append({"test": f"Rule 3 dkappa {e} against {r} (reported)", "value": f"median {statistics.median(d.values()):+.3f}; >= 0.10 in {sum(x >= 0.10 for x in d.values())}/{len(d)}", "verdict": ""})
    if labels and key:
        seen, S, NS, reps = {}, {}, {}, []
        for r in labels:
            a = (r.get("same") or "").strip()
            if not a:
                continue
            k = key[r["unit"]]; tag = (k["prompt"], k["cond"]); n = k["cond"].rsplit("_", 1)[0]
            if tag in seen:
                reps.append((seen[tag], a)); continue
            seen[tag] = a; NS[n] = NS.get(n, 0) + (a == "nonsivede")
            if a in ("stesso", "diversi"):
                S.setdefault(n, []).append(1.0 if a == "stesso" else 0.0)
        out.append({"test": "Rule 3 'non si vede' per condition (reported)", "value": " ".join(f"{n} {NS.get(n, 0)}" for n in NAMES), "verdict": ""})
        if all(len(S.get(n, [])) >= 4 for n in ("L09", "R09", "L26", "R26")):
            s = {n: statistics.mean(v) for n, v in S.items()}
            diff = (s["L26"] - s["R26"]) - (s["L09"] - s["R09"])
            v2 = "the eye agrees" if diff >= 0.25 else "the eye does not separate them"
            val = f"{diff:+.2f}; " + " ".join(f"{n} {s[n]:.2f} (n {len(S[n])})" for n in NAMES if n in s)
        else:
            v2, val = "not testable", " ".join(f"{n} n {len(S.get(n, []))}" for n in NAMES)
        out.append({"test": "Rule 2 blind (s(L26) - s(R26)) - (s(L09) - s(R09))", "value": val, "verdict": v2})
        if reps:
            out.append({"test": "Rule 3 blind test-retest (reported)", "value": f"{sum(a == b for a, b in reps)} of {len(reps)} identical", "verdict": ""})
        if "not testable" in (v1, v2):
            comb = "not testable"
        else:
            y1, y2 = v1.startswith("depth"), v2 == "the eye agrees"
            comb = "supported" if y1 and y2 else ("disagreement" if y1 != y2 else "not supported")
        out.append({"test": "Combined verdict (rules 1 and 2)", "value": "", "verdict": comb})
    return out


def load_vecs():
    z = np.load(VECS)
    return {tuple(k.split("|")): v.astype(np.float64) for k, v in zip(z["keys"], z["vecs"])}


def selftest():
    assert len(conds()) == 13
    assert abs(interp([1, 2, 4], [0.05, 0.2, 0.5], 0.12) - math.exp(math.log(1) + (0.07 / 0.15) * math.log(2))) < 1e-9
    assert abs(interp([1, 2], [0.24, 0.5], 0.12) - 0.5) < 1e-9 and interp([1, 2], [0.1, 0.2], 0.3) is None
    rng = np.random.default_rng(0)
    def synth(directed, deep_scale=1.0):
        V = {}
        for p in PROMPTS:
            dirs = {c: rng.standard_normal(64) for c in conds()}
            for s in SEEDS:
                b = rng.standard_normal(64); V[(p, s, "C0")] = b
                for c in conds()[1:]:
                    sc = deep_scale if c[:3] in ("L26", "L30", "R26") else 1.0
                    V[(p, s, c)] = b + sc * ((2.0 * dirs[c] if c.split("_")[0] in directed else 0) + rng.standard_normal(64))
        return V
    v = [o for o in rules(synth({"L26", "L30"})) if o["test"].startswith("Rule 1")][0]["verdict"]
    assert v == "depth gives the edit a direction in the picture", v
    v = [o for o in rules(synth(set())) if o["test"].startswith("Rule 1")][0]["verdict"]; assert v == "neither", v
    v = [o for o in rules(synth({"L26"}, deep_scale=0.001)) if o["test"].startswith("Rule 1")][0]["verdict"]; assert v == "not testable", v
    key = {}; lab = []; i = 0
    for n, a in (("L26", "stesso"), ("R26", "diversi"), ("L09", "stesso"), ("R09", "stesso")):
        for p in PROMPTS:
            key[f"V{i}"] = {"prompt": p, "cond": f"{n}_t1"}; lab.append({"unit": f"V{i}", "same": a}); i += 1
    o = rules(synth({"L26", "L30"}), lab, key)
    assert [x for x in o if x["test"].startswith("Rule 2")][0]["verdict"] == "the eye agrees", o
    assert [x for x in o if x["test"].startswith("Combined")][0]["verdict"] == "supported"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "encode-cal", "calibrate", "gate", "count", "analyze", "page", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--queue", action="store_true"); ap.add_argument("--block")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.encode_cal: encode_cal()
    if a.queue: queue(a.block)
    if a.calibrate: calibrate()
    if a.gate: gate()
    if a.count: count()
    if a.analyze: analyze()
    if a.page: page()
    if a.rules:
        V = load_vecs(); lab = rd(LABELS) if LABELS.exists() else None
        key = {r["unit"]: r for r in rd(KEY)} if KEY.exists() else None
        out = rules(V, lab, key)
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
