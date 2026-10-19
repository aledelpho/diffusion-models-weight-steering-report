"""C103 - random edits: own direction or the network's? (docs/prereg_te_depth_control2.md). Rewritten 2026-10-19 with the
new pre-registration, before any encode or render.

  python te_depth_control2.py --selftest
  python te_depth_control2.py --encode-cal        # GPU: ladder conditionings -> data/te_depth_control2_cal_plan.csv (132 rows)
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
LADDER = {"L09": [0.5, 0.75, 1.0, 1.25], "L26": [1.5, 3.0, 5.0, 8.0]}
LADDER.update({f"R09{x}": [1.5, 2.25, 3.0, 4.0] for x in "abc"})
LADDER.update({f"R26{x}": [6.0, 12.0, 24.0, 48.0] for x in "abc"})
LAYER = {n: int(n[1:3]) for n in LADDER}
RSEED = {"a": 9393, "b": 9394, "c": 9395}
TARGETS = {"t": 0.30}
NAMES = ["L09", "L26", "R09a", "R09b", "R09c", "R26a", "R26b", "R26c"]
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
        g = torch.Generator(device="cpu").manual_seed(RSEED[name[-1]])
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
    write(PLAN, rows); print("wrote", CALM, STRENGTH, "and", PLAN, len(rows), "(108 if every target was reached)")


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


def units_spec(have):
    """A: one perturbation, three seeds. B: one layer, one seed, three random pushes."""
    A = [("A", p, c, "") for p in PROMPTS for c in conds()[1:] if all((p, s, c) in have for s in SEEDS)]
    B = [("B", p, f"R{L}", s) for p in PROMPTS for L in ("09", "26") for s in SEEDS
         if all((p, s, f"R{L}{x}_t") in have for x in "abc")]
    return A, B


def page():
    from eye_grid_page import thumb, build
    R = T.img_root(); root = str(R); rng = random.Random(10303)
    have = {(r["char"], r["seed"], r["cond"]) for r in rd(PLAN) if r["block"] == "main"}
    A, B = units_spec(have); base = A + B; rng.shuffle(base)
    reps = rng.sample(base, 6); order = list(base)
    for r in reps:
        i = order.index(r); order.insert(rng.randint(min(i + 10, len(order)), len(order)), r)
    f = lambda p, c, s: thumb(str(R / FOLDER / f"{p}_{c}_krea2_seed{s}_00001_.png"), root)
    key, units, seen = [], [], set()
    for n, u in enumerate(order, 1):
        kind, p, c, s0 = u; uid = f"V{n:02d}"
        key.append({"unit": uid, "kind": kind, "prompt": p, "cond": c, "seed": s0, "repeat": int(u in seen)}); seen.add(u)
        pairs = [(s, c) for s in SEEDS] if kind == "A" else [(s0, f"{c}{x}_t") for x in "abc"]
        rows = []
        for k, (s, cc) in enumerate(pairs, 1):
            a, b = f(p, "C0", s), f(p, cc, s)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=["unit", "kind", "prompt", "cond", "seed", "repeat"]); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_C103.html"), "C103 · lo stesso cambiamento?", units,
          [("same", "Nelle tre coppie l'immagine cambia nello stesso modo?", OPTS)], OPTS, "c103_labels_v2", "te_depth_control2_labels.csv")
    print("units", len(units), "(A", len(A), "B", len(B), "+ 6 repeats) ->", os.path.join(root, "occhio_C103.html"))


# ---------------------------------------------------------------- rules (numpy)
def rules(V, labels=None, key=None):
    out = []
    cos = T._cos
    dl = lambda p, s, c: V[(p, s, c)] - V[(p, s, "C0")]
    dist = lambda p, s, c: 1 - cos(V[(p, s, c)], V[(p, s, "C0")])
    matched = {}
    for n in NAMES:
        c = f"{n}_t"; ds = [dist(p, s, c) for p in PROMPTS for s in SEEDS if (p, s, c) in V]
        md = statistics.median(ds) if ds else 0.0; matched[n] = bool(ds) and md >= 0.15
        out.append({"test": f"Rule 0 realized median D, {n} (target 0.30)", "value": f"{md:.3f} over {len(ds)}", "verdict": "matched" if matched[n] else "not matched"})
    kap = lambda p, c: T.kappa_seeds(V, p, c, SEEDS)
    blind = {}
    if labels and key:
        seen, reps = {}, []
        for r in labels:
            a = (r.get("same") or "").strip()
            if not a:
                continue
            k = key[r["unit"]]; tag = (k["kind"], k["prompt"], k["cond"], k["seed"])
            if tag in seen:
                reps.append((seen[tag], a)); continue
            seen[tag] = a
        blind = seen
        ns = {}
        for (kind, p, c, s), a in seen.items():
            ns[c if kind == "A" else f"B:{c}"] = ns.get(c if kind == "A" else f"B:{c}", 0) + (a == "nonsivede")
        out.append({"test": "Rule 4 'non si vede' per condition (reported)", "value": " ".join(f"{k} {v}" for k, v in sorted(ns.items())), "verdict": ""})
        if reps:
            out.append({"test": "Rule 4 blind test-retest (reported)", "value": f"{sum(a == b for a, b in reps)} of {len(reps)} identical", "verdict": ""})
    def share(items):
        vis = [a for a in items if a in ("stesso", "diversi")]
        return (sum(a == "stesso" for a in vis) / len(vis) if vis else None), len(vis)
    def combine(c, b):
        if c is None or b is None:
            return "not testable"
        return "supported" if c and b else ("not supported" if not c and not b else "disagreement")
    res = {}
    for L in ("09", "26"):
        rnd = [f"R{L}{x}" for x in "abc"]
        if not any(matched[n] for n in rnd):
            out.append({"test": f"Rules 1-2 layer {L}", "value": "no random push matched", "verdict": "not testable"}); continue
        K = [kap(p, f"{n}_t") for p in PROMPTS for n in rnd if matched[n]]; K = [k for k in K if k is not None]
        c1 = (sum(k >= 0.30 for k in K) / len(K) >= 0.75) if K else None
        bA = [a for (kind, p, c, s), a in blind.items() if kind == "A" and c[:-2] in rnd]
        sh, nv = share(bA); b1 = None if (not blind or nv < 6) else sh >= 0.60
        v1 = combine(c1, b1) if blind else ("computed only: " + ("yes" if c1 else "no"))
        out.append({"test": f"Rule 1 layer {L}: any fixed random push changes the seeds the same way",
                    "value": f"kappa >= 0.30 in {sum(k >= 0.30 for k in K)}/{len(K)} (median {statistics.median(K):.2f}); blind stesso {('%.2f' % sh) if sh is not None else '-'} (n {nv})", "verdict": v1})
        rho = []
        for p in PROMPTS:
            for s in SEEDS:
                D = [dl(p, s, f"{n}_t") for n in rnd if matched[n] and (p, s, f"{n}_t") in V]
                if len(D) >= 2:
                    rho.append(statistics.mean(cos(a, b) for a, b in itertools.combinations(D, 2)))
        r = statistics.median(rho) / statistics.median(K) if rho and K and statistics.median(K) > 0 else None
        c2 = None if r is None else ("network" if r >= 0.50 else ("own" if r <= 0.25 else "partly"))
        bB = [a for (kind, p, c, s), a in blind.items() if kind == "B" and c == f"R{L}"]
        sb, nb = share(bB); b2 = None if (not blind or nb < 4) else ("network" if sb >= 0.60 else ("own" if sb <= 0.30 else "partly"))
        if c2 is None: v2 = "not testable"
        elif not blind: v2 = "computed only: " + c2
        elif b2 is None: v2 = f"computed {c2}; blind not testable"
        else: v2 = f"agree: {c2}" if c2 == b2 else f"disagreement: computed {c2}, blind {b2}"
        lab = {"network": "the network imposes the direction", "own": "each perturbation has its own direction", "partly": "partly"}
        out.append({"test": f"Rule 2 layer {L}: own direction or the network's",
                    "value": f"median rho {statistics.median(rho):.2f} / median kappa {statistics.median(K):.2f} = r {r:.2f}; blind B stesso {('%.2f' % sb) if sb is not None else '-'} (n {nb})" if r is not None else "",
                    "verdict": v2 + (f" ({lab[c2]})" if c2 else "")})
        e = f"L{L}"
        if matched[e]:
            ke = [kap(p, f"{e}_t") for p in PROMPTS]; ke = [k for k in ke if k is not None]
            eps = [statistics.mean(cos(dl(p, s, f"{e}_t"), dl(p, s, f"{n}_t")) for n in rnd if matched[n] and (p, s, f"{n}_t") in V)
                   for p in PROMPTS for s in SEEDS if (p, s, f"{e}_t") in V]
            out.append({"test": f"Rule 4 edit {e}: kappa and epsilon (edit like its layer's random pushes) (reported)",
                        "value": f"kappa median {statistics.median(ke):.2f} (random {statistics.median(K):.2f}); epsilon median {statistics.median(eps):.2f} (rho {statistics.median(rho):.2f})", "verdict": ""})
        res[L] = (v1, v2)
    if len(res) == 2:
        out.append({"test": "Rule 3 depth: answers at L09 and L26 (reported)", "value": f"L09 {res['09']} | L26 {res['26']}", "verdict": "differ" if res["09"] != res["26"] else "same"})
    return out


def load_vecs():
    z = np.load(VECS)
    return {tuple(k.split("|")): v.astype(np.float64) for k, v in zip(z["keys"], z["vecs"])}


def selftest():
    assert len(conds()) == 9 and conds()[1] == "L09_t" and LAYER["R26c"] == 26
    assert abs(interp([1, 2], [0.24, 0.5], 0.12) - 0.5) < 1e-9 and interp([1, 2], [0.1, 0.2], 0.3) is None
    rng = np.random.default_rng(0)
    def synth(shared09, shared26):
        V = {}
        for p in PROMPTS:
            net = {L: rng.standard_normal(64) for L in ("09", "26")}
            own = {c: rng.standard_normal(64) for c in conds()}
            for s in SEEDS:
                b = rng.standard_normal(64); V[(p, s, "C0")] = b
                for c in conds()[1:]:
                    L = c[1:3]; shared = shared09 if L == "09" else shared26
                    d = (net[L] if shared else own[c]) * 1.5 + 0.4 * rng.standard_normal(64)
                    V[(p, s, c)] = b + d
        return V
    o = {x["test"].split(":")[0]: x["verdict"] for x in rules(synth(True, False))}
    assert o["Rule 2 layer 09"].startswith("computed only: network"), o
    assert o["Rule 2 layer 26"].startswith("computed only: own"), o
    assert o["Rule 1 layer 09"] == "computed only: yes", o
    V = synth(True, False)
    have = {k for k in V}
    A, B = units_spec(have); assert len(A) == 32 and len(B) == 24
    key, lab = {}, []
    for i, (kind, p, c, s) in enumerate(A + B):
        key[f"V{i}"] = {"kind": kind, "prompt": p, "cond": c, "seed": s}
        a = "stesso" if (kind == "A" or c == "R09") else "diversi"
        lab.append({"unit": f"V{i}", "same": a})
    o = {x["test"].split(":")[0]: x["verdict"] for x in rules(V, lab, key)}
    assert o["Rule 1 layer 09"] == "supported" and o["Rule 2 layer 09"].startswith("agree: network"), o
    assert o["Rule 2 layer 26"].startswith("agree: own"), o
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
