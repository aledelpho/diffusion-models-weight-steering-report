"""C111 - "Photo of a tree" (amendment 1, 2026-10-27, before any render: random pushes removed, seed cards and an
"amount" question added). Does the plain model draw nearly the same tree at every seed, and does a text-encoder edit
change the light or the setting in the same way at every seed? (docs/prereg_te_tree.md). Written 2026-10-27 with the
pre-registration, before any encode or render. Proposed by Alessandro; renders to be authorised by him with the directive.
Encoder, calibration (target DINOv2 D 0.25), queue and count are C109's code (te_light_presets.py) unchanged; plan, gate,
analyze, blind page and rules are new.

  python te_tree.py --selftest
  python te_tree.py --calibrate     # GPU + ComfyUI running: encodes, queues, waits, measures, decides (resumable)
  python te_tree.py --plan          # GPU: test conditionings -> data/te_tree_plan.csv
  python te_tree.py --queue --block gate | main
  python te_tree.py --gate          # plain render through the conditioning file = plain render through the text, pixel for pixel
  python te_tree.py --count
  python te_tree.py --analyze       # GPU: DINOv2 -> data/te_tree_metrics.csv, data/te_tree_dino_tests.csv
  python te_tree.py --page          # blind page Text2Img/occhio_C111.html (after --analyze)
  python te_tree.py --rules         # once data/te_tree_labels.csv exists
"""
import argparse, csv, gc, itertools, json, math, os, random, statistics, sys, time, urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_depth_control as T

DATA = HERE.parent / "data"
STATE = DATA / "te_tree_cal_state.json"
CALPLAN = DATA / "te_tree_cal_plan.csv"
PLAN = DATA / "te_tree_plan.csv"
STRENGTHS = DATA / "te_tree_strengths.csv"
METRICS = DATA / "te_tree_metrics.csv"
DTESTS = DATA / "te_tree_dino_tests.csv"
KEY = DATA / "te_tree_key.csv"
LABELS = DATA / "te_tree_labels.csv"
TESTS = DATA / "te_tree_tests.csv"
FOLDER = "benchmark_te_tree"
PROMPT = "Photo of a tree"
SUBJECTS = ["T1_tree"]
# C109's presets that visibly moved the rally (P01, P06, P10), the same four layers and signs.
PRESETS = {"P01": {"7": 0.3, "9": -0.3, "11": 0.3, "17": 0.3}, "P06": {"9": 0.3, "11": -0.3, "20": -0.3, "22": 0.3},
           "P10": {"14": 0.3, "15": 0.3, "29": 0.3, "30": -0.3}}
EDITS = ["E05", "E06", "E14", "E26", "E28"]          # MLP of one encoder layer (pages 30-31: L05, L06, L14, L26, L28)
REAL = EDITS + list(PRESETS)
RANDOM = []                                           # amendment 1: no random pushes (not part of the claim)
PERTS = {**{e: ("edit", int(e[1:])) for e in EDITS}, **{n: ("preset", None) for n in PRESETS}}
LADDER = {**{e: [0.4, 0.8, 1.6, 3.2] for e in ("E05", "E06", "E14")}, **{e: [0.75, 1.5, 3.0, 6.0] for e in ("E26", "E28")},
          **{n: [0.5, 1.0, 2.0, 3.3] for n in PRESETS}}
CAL_SEEDS = ["1618033", "2718281"]
TEST_SEEDS = ["2645751", "3316624", "1414213", "1732050", "2236067", "3141592", "1234567", "5772156"]
GROUPS = [TEST_SEEDS[:4], TEST_SEEDS[4:]]
TARGET, LO, HI, ACC_LO, ACC_HI, ROUNDS = 0.25, 0.20, 0.32, 0.15, 0.40, 2
PLAIN_MAX = 0.15                                      # rule 1: plain seeds closer than the smallest accepted edit change
SET = T.SET


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def texts():
    return {"T1_tree": PROMPT}


def tag(n, x):
    return f"{n}_{x:g}".replace(".", "p")


def cpath(p, t):
    return T.img_root() / FOLDER / "conds" / f"{p}_{t}.pt"


def fname(p, t, s):
    return f"{p}_{t}_krea2_seed{s}_00001_.png"


def row(block, p, s, t, variant="file"):
    prefix = f"{p}_{t}_krea2_seed{s}"
    return {"block": block, "char": p, "seed": s, "cond": t, "variant": variant, "push_path": str(cpath(p, t)) if variant == "file" else "",
            "noise_seed": 7, "taps": "", "te_granular_json": "{}", "prompt_text": TX[p], "output_prefix": prefix,
            "expected_filename": f"{prefix}_00001_.png", **SET}


TX = None


def write(path, rows):
    for i, r in enumerate(rows):
        r["row"] = i
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["row"] + [k for k in rows[0] if k != "row"]); w.writeheader(); w.writerows(rows)


# ---------------------------------------------------------------- encoder (GPU)
class Enc:
    def __init__(self):
        import torch
        import te_punct_encoder as TPE, te_layer0_encoder as TLE, te_shapes as TS
        self.torch, self.TLE = torch, TLE
        self.base = TPE.gate(); self.layers = TS._layers(self.base); self.cap = {}

    def raw(self, clip, text):
        tokens = clip.tokenize(text)
        return clip.encode_from_tokens(tokens, return_pooled=False, return_dict=True)["cond"].detach().cpu().clone()

    def cond(self, p, n, x):
        torch = self.torch; kind, L = PERTS[n] if n in PERTS else (None, None); text = TX[p]
        if n == "C0":
            return self.raw(self.base, text)
        if kind == "edit":
            return self.raw(self.TLE.apply_te_edit(self.base, T.gj(L, x)), text)
        if kind == "preset":
            g = {}
            for Ls, d in PRESETS[n].items():
                g.update(T.gj(int(Ls), d * x))
            return self.raw(self.TLE.apply_te_edit(self.base, g), text)
        if (p, L) not in self.cap:
            box = {}
            h = self.layers[L].mlp.register_forward_hook(lambda m, a, o: box.__setitem__("o", (o[0] if isinstance(o, tuple) else o).detach().float().clone()))
            self.raw(self.base, text); h.remove(); self.cap[(p, L)] = box["o"]
        c = self.cap[(p, L)]
        g = torch.Generator(device="cpu").manual_seed(9393)
        R = torch.randn(c.shape, generator=g); R = R / torch.linalg.vector_norm(R, dim=-1, keepdim=True)
        add = R * torch.linalg.vector_norm(c, dim=-1, keepdim=True).cpu() * x
        h = self.layers[L].mlp.register_forward_hook(lambda m, a, o: o + add.to(o.device, o.dtype))
        try:
            return self.raw(self.base, text)
        finally:
            h.remove()

    def save(self, p, n, x):
        t = "C0" if n == "C0" else tag(n, x)
        if not cpath(p, t).exists():
            c = self.cond(p, n, x)
            if not bool(self.torch.isfinite(c.float()).all()):
                return None
            self.torch.save(c, cpath(p, t))
        return t


def free():
    gc.collect()
    try:
        import torch; torch.cuda.empty_cache()
    except Exception:
        pass


# ---------------------------------------------------------------- calibration (state machine)
def med(state, p, n, x):
    ds = state["D"].get(f"{p}|{tag(n, x)}")
    return statistics.median(ds) if ds else None


def next_strengths(state, p, n):
    """None if done; otherwise the strengths still to render for this pair."""
    st = state["pairs"][f"{p}|{n}"]
    if st["status"] != "open":
        return []
    xs = sorted(float(x) for x in st["tested"])
    ms = [med(state, p, n, x) for x in xs]
    if any(m is None for m in ms):
        return [x for x, m in zip(xs, ms) if m is None]
    if any(LO <= m <= HI for m in ms):
        st["status"] = "done"; return []
    if st["round"] >= ROUNDS or all(m < TARGET for m in ms):
        st["status"] = "done"; return []
    above = [x for x, m in zip(xs, ms) if m > TARGET]; x_hi = min(above)
    below = [x for x, m in zip(xs, ms) if m < TARGET and x < x_hi]; x_lo = max(below) if below else 0.0
    x_new = math.sqrt(x_lo * x_hi) if x_lo > 0 else x_hi / 2
    st["round"] += 1; st["tested"].append(x_new)
    return [x_new]


def choose(state, p, n):
    st = state["pairs"][f"{p}|{n}"]
    cand = [(abs(med(state, p, n, float(x)) - TARGET), float(x)) for x in st["tested"] if med(state, p, n, float(x)) is not None]
    if not cand:
        return None, None
    d, x = min(cand); m = med(state, p, n, x)
    return (x, m) if ACC_LO <= m <= ACC_HI else (None, m)


def calibrate():
    global TX
    TX = texts()
    state = json.loads(STATE.read_text()) if STATE.exists() else {
        "pairs": {f"{p}|{n}": {"status": "open", "round": 0, "tested": list(LADDER[n])} for p in SUBJECTS for n in PERTS}, "D": {}}
    import blk23_colorful as c47
    while True:
        todo = {}
        for p in SUBJECTS:
            for n in PERTS:
                for x in next_strengths(state, p, n):
                    todo[(p, n, x)] = 1
        STATE.write_text(json.dumps(state, indent=1))
        need_c0 = [p for p in SUBJECTS if f"{p}|C0" not in state["D"]]
        if not todo and not need_c0:
            break
        print(f"round: {len(todo)} strengths to render x {len(CAL_SEEDS)} seeds", flush=True)
        (T.img_root() / FOLDER / "conds").mkdir(parents=True, exist_ok=True)
        E = Enc(); rows = rd(CALPLAN) if CALPLAN.exists() else []; have = {r["expected_filename"] for r in rows}; new = []
        for p in need_c0:
            E.save(p, "C0", 0)
            for s in CAL_SEEDS:
                r = row("cal", p, s, "C0")
                if r["expected_filename"] not in have: new.append(r)
        for (p, n, x) in todo:
            t = E.save(p, n, x)
            if t is None:
                print("NONFINITE", p, n, x, flush=True); state["D"][f"{p}|{tag(n, x)}"] = [9.9, 9.9]; continue
            for s in CAL_SEEDS:
                r = row("cal", p, s, t)
                if r["expected_filename"] not in have: new.append(r)
        E = None; free()
        if new:
            write(CALPLAN, rows + new)
            for r in new:
                post(r)
            print("queued", len(new), flush=True)
            t0 = time.time()
            while True:
                miss = [r for r in new if not (T.img_root() / FOLDER / r["expected_filename"]).exists()]
                if not miss:
                    break
                if time.time() - t0 > 4 * 3600:
                    sys.exit(f"TIMEOUT waiting for {len(miss)} renders - stop")
                time.sleep(30)
            time.sleep(10)
        measure(state); STATE.write_text(json.dumps(state, indent=1))
    out = []
    for p in SUBJECTS:
        for n in PERTS:
            x, m = choose(state, p, n)
            st = state["pairs"][f"{p}|{n}"]
            out.append({"prompt": p, "pert": n, "strength": "" if x is None else round(x, 5), "median_D": "" if m is None else round(m, 4),
                        "in_window": int(m is not None and LO <= m <= HI), "rounds": st["round"], "reached": int(x is not None)})
            if x is None:
                print("UNREACHABLE", p, n, "closest D", m, flush=True)
    with open(STRENGTHS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("calibration done:", sum(o["reached"] for o in out), "of", len(out), "pairs reached;", sum(o["in_window"] for o in out), "in the window")


def measure(state):
    from PIL import Image
    import metric_validation as MV
    R = T.img_root() / FOLDER; m = MV.Models(vqa=False); V = {}
    vec = lambda f: np.asarray(m.dino_vec(Image.open(R / f).convert("RGB")), dtype=np.float64)
    for r in rd(CALPLAN):
        key = f"{r['char']}|{r['cond']}"
        if key in state["D"] and len(state["D"][key]) == len(CAL_SEEDS):
            continue
        V[(r["char"], r["seed"], r["cond"])] = vec(r["expected_filename"])
    for (p, s, t), v in list(V.items()):
        if t == "C0":
            continue
        b = V.get((p, s, "C0"))
        if b is None:
            b = vec(fname(p, "C0", s)); V[(p, s, "C0")] = b
        state["D"].setdefault(f"{p}|{t}", [])
        state["D"][f"{p}|{t}"].append(1 - float(v @ b / (np.linalg.norm(v) * np.linalg.norm(b))))
    for p in SUBJECTS:
        state["D"].setdefault(f"{p}|C0", [0.0])
    m = None; free()


# ---------------------------------------------------------------- test
def plan():
    global TX
    TX = texts(); E = Enc(); rows = []
    S = {(r["prompt"], r["pert"]): r for r in rd(STRENGTHS)}
    p = SUBJECTS[0]; E.save(p, "C0", 0)
    rows.append(row("gate", p, TEST_SEEDS[0], "TEXT", variant="text"))
    for s in TEST_SEEDS:
        rows.append(row("main", p, s, "C0"))
        for n in PERTS:
            r = S[(p, n)]
            if int(r["reached"]):
                rows.append(row("main", p, s, E.save(p, n, float(r["strength"]))))
    write(PLAN, rows); print("plan rows:", len(rows), f"({1 + 8 * (1 + len(PERTS))} if every perturbation was reached)")


def post(r):
    import blk23_colorful as c47
    if r.get("variant") == "text":
        wf = c47.workflow({**r, "vectors_override": ""})
    else:
        wf = T.workflow({**r})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        json.loads(resp.read())


def queue(block):
    n = 0
    for r in rd(PLAN):
        if r["block"] != block or (T.img_root() / FOLDER / r["expected_filename"]).exists():
            continue
        post(r); n += 1
    print("queued", n)


def gate():
    from PIL import Image
    R = T.img_root() / FOLDER; p, s = SUBJECTS[0], TEST_SEEDS[0]
    a, b = R / fname(p, "C0", s), R / fname(p, "TEXT", s)
    if not (a.exists() and b.exists()):
        print("missing", [x.name for x in (a, b) if not x.exists()]); print("GATE FAIL - stop"); return
    d = int(np.abs(np.asarray(Image.open(a).convert("RGB"), dtype=np.int16) - np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)).max())
    print(f"{a.name} vs {b.name}: max abs diff {d}"); print("GATE", "PASS" if d == 0 else "FAIL - stop")


def count():
    rows = rd(PLAN); miss = [r["expected_filename"] for r in rows if not (T.img_root() / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def conds_by_pert():
    """pert -> test condition tag (only perturbations whose calibration was reached)."""
    out = {}
    for r in rd(PLAN):
        if r["block"] == "main" and r["cond"] != "C0":
            out[r["cond"].split("_")[0]] = r["cond"]
    return out


def cosd(a, b):
    return 1 - float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def dino_tests(V, ref):
    """V: (seed, cond) -> vector for the tree; ref: subject -> [vectors of C0 at 4 seeds] (C109, reported)."""
    out, C = [], conds_by_pert()
    plain = [cosd(V[(a, "C0")], V[(b, "C0")]) for a, b in itertools.combinations(TEST_SEEDS, 2)]
    moved = {n: [cosd(V[(s, t)], V[(s, "C0")]) for s in TEST_SEEDS] for n, t in C.items()}
    real = [x for n in REAL if n in moved for x in moved[n]]
    mp, mr = statistics.median(plain), (statistics.median(real) if real else float("nan"))
    v = "nearly the same picture at every seed" if mp <= PLAIN_MAX and mp < mr else "the seeds already vary"
    out.append({"test": "Rule 1 plain seeds: median pairwise D of the 8 plain trees", "value": f"{mp:.3f} (bar {PLAIN_MAX}); median D of the real edits from the plain tree {mr:.3f}", "verdict": v})
    for p, vs in ref.items():
        d = [cosd(a, b) for a, b in itertools.combinations(vs, 2)]
        out.append({"test": f"Rule 1 reference: {p} plain, pairwise D over its 4 C109 seeds (reported)", "value": f"median {statistics.median(d):.3f}", "verdict": "-"})
    U = {n: {s: V[(s, t)] - V[(s, "C0")] for s in TEST_SEEDS} for n, t in C.items()}
    cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    within = {n: statistics.mean(cos(U[n][a], U[n][b]) for a, b in itertools.combinations(TEST_SEEDS, 2)) for n in U}
    null = [cos(U[m][a], U[n][b]) for m, n in itertools.permutations(U, 2) for a, b in itertools.permutations(TEST_SEEDS, 2)]
    nm = statistics.mean(null) if null else float("nan")
    w = [within[n] for n in REAL if n in within]
    sd = [cos(V[(a2, "C0")] - V[(a, "C0")], V[(b2, "C0")] - V[(b, "C0")]) for (a, a2), (b, b2) in itertools.combinations(list(zip(GROUPS[0], GROUPS[1])), 2)]
    out.append({"test": "Reported: direction of the change shared across seeds (mean cosine of the DINOv2 displacements)",
                "value": (f"edits {statistics.mean(w):.3f}; different perturbations at different seeds {nm:.3f}; "
                          f"seed changes of the plain tree {statistics.mean(sd):.3f}") if w else "none reached", "verdict": "-"})
    out.append({"test": "Reported: per perturbation, mean cosine across seeds", "value": "; ".join(f"{n} {within[n]:.2f}" for n in PERTS if n in within), "verdict": "-"})
    disp = {n: statistics.median(cosd(V[(a, t)], V[(b, t)]) for a, b in itertools.combinations(TEST_SEEDS, 2)) for n, t in C.items()}
    out.append({"test": "Reported: median pairwise D across seeds after each perturbation (plain above)", "value": "; ".join(f"{n} {disp[n]:.3f}" for n in PERTS if n in disp), "verdict": "-"})
    unreached = [n for n in PERTS if n not in C]
    out.append({"test": "Reported: perturbations that did not reach the calibration window", "value": ", ".join(unreached) or "none", "verdict": "-"})
    return out


def analyze():
    from PIL import Image
    import metric_validation as MV
    import te_light_presets as LP
    R = T.img_root() / FOLDER; m = MV.Models(vqa=False)
    vec = lambda f: np.asarray(m.dino_vec(Image.open(f).convert("RGB")), dtype=np.float64)
    V = {(r["seed"], r["cond"]): vec(R / r["expected_filename"]) for r in rd(PLAN) if r["block"] == "main"}
    met = [{"prompt": SUBJECTS[0], "seed": s, "cond": c, "pert": c.split("_")[0], "dinov2_dist_to_base": round(cosd(v, V[(s, "C0")]), 6)}
           for (s, c), v in V.items() if c != "C0"]
    with open(METRICS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(met[0])); w.writeheader(); w.writerows(met)
    ref = {}
    Rl = T.img_root() / LP.FOLDER
    for p in LP.SUBJECTS:
        fs = [Rl / LP.fname(p, "C0", s) for s in LP.CAL_SEEDS + LP.TEST_SEEDS]
        if all(f.exists() for f in fs):
            ref[p] = [vec(f) for f in fs]
    out = dino_tests(V, ref)
    with open(DTESTS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


# ---------------------------------------------------------------- blind
OPTS = [("stesso", "stesso tipo"), ("simile", "qualcosa di simile"), ("diversi", "in modi diversi"), ("nonsivede", "non si vede")]
MAG = [("molto", "cambia molto"), ("qualcosa", "cambia qualcosa"), ("poco", "quasi niente"), ("niente", "niente")]
MSC = {"molto": 1.0, "qualcosa": 2 / 3, "poco": 1 / 3, "niente": 0.0}
QS = [("amount", "Quanto cambia il contenuto (albero, ambiente, luce) da prima a dopo, nell'insieme delle coppie?", MAG),
      ("light", "Il cambiamento di luce, cielo o ora del giorno è dello stesso tipo in tutte le coppie?", OPTS),
      ("scene", "Il cambiamento dell'albero o dell'ambiente (specie, forma, stagione, paesaggio) è dello stesso tipo in tutte le coppie?", OPTS)]
SC = {"stesso": 1.0, "simile": 0.5, "diversi": 0.0}


def unit_specs(C, rng):
    """Pairs are (seed before, cond before, seed after, cond after); cond "C0" is the plain tree.
    Matched: one perturbation, four seeds of a group. Null: four different perturbations, one per seed of a group.
    Seed (amendment 1): plain tree at one seed -> plain tree at a seed of the other group (no perturbation)."""
    U, names = [], [n for n in PERTS if n in C]
    for n in names:
        for g, seeds in enumerate(GROUPS):
            U.append({"kind": "real", "pert": n, "group": g, "pairs": [(s, "C0", s, n) for s in seeds]})
    for g, seeds in enumerate(GROUPS):
        for _ in range(4):
            ps = rng.sample(names, 4)
            U.append({"kind": "null", "pert": "mixed", "group": g, "pairs": [(s, "C0", s, n) for s, n in zip(seeds, ps)]})
    for g, seeds in enumerate(GROUPS):
        other = GROUPS[1 - g]
        for sh in (0, 1):
            U.append({"kind": "seed", "pert": "seed", "group": g, "pairs": [(s, "C0", other[(i + sh) % 4], "C0") for i, s in enumerate(seeds)]})
    return U


def page():
    from eye_grid_page import thumb, build
    R = T.img_root(); root = str(R); rng = random.Random(11010); C = conds_by_pert()
    U = unit_specs(C, rng); rng.shuffle(U)
    reps = rng.sample([i for i, u in enumerate(U) if u["kind"] == "real"], 4); order = list(range(len(U)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 8, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for k_, i in enumerate(order, 1):
        u = U[i]; uid = f"T{k_:02d}"
        key.append({"unit": uid, "kind": u["kind"], "pert": u["pert"], "group": u["group"],
                    "pairs": " ".join(":".join(x) for x in u["pairs"]), "repeat": int(i in seen)}); seen.add(i)
        rows = []
        cc = lambda n: "C0" if n == "C0" else C[n]
        for k, (s, n0, s2, n) in enumerate(u["pairs"], 1):
            a = thumb(str(R / FOLDER / fname(SUBJECTS[0], cc(n0), s)), root); b = thumb(str(R / FOLDER / fname(SUBJECTS[0], cc(n), s2)), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {k_:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_C111.html"), "C111 · lo stesso cambiamento a ogni seed?", units, QS, OPTS, "c111_labels_v1", "te_tree_labels.csv")
    print("cards", len(units), "->", os.path.join(root, "occhio_C111.html"))


def card_score(a):
    v = [SC[a[q]] for q in ("light", "scene") if a.get(q) in SC]
    return max(v) if v else None


def rules(labels, key):
    out, first, reps = [], {}, []
    for r in labels:
        k = key.get(r["unit"])
        if not k:
            continue
        a = {q: (r.get(q) or "").strip() for q in ("amount", "light", "scene")}
        if not any(a.values()):
            continue
        t = (k["kind"], k["pert"], k["group"], k["pairs"])
        if k["repeat"] == "1" or t in first:
            reps.append((first.get(t), a)); continue
        first[t] = a
    def mean(sel, f=card_score):
        v = [f(a) for t, a in first.items() if sel(t) and f(a) is not None]
        return (sum(v) / len(v) if v else None), len(v)
    rnd = lambda x: "-" if x is None else f"{x:.2f}"
    sn, nn = mean(lambda t: t[0] == "null"); sr, nr = mean(lambda t: t[0] == "real"); ss, ns_ = mean(lambda t: t[0] == "seed")
    amt = lambda a: MSC.get(a.get("amount"))
    ar, nar = mean(lambda t: t[0] == "real", amt); asd, nas = mean(lambda t: t[0] == "seed", amt)
    if ar is None or asd is None or nar < 6 or nas < 2:
        v1 = "not testable"
    elif ar - asd >= 0.30:
        v1 = "the edits change the content more than a change of seed"
    elif ar - asd <= 0.10:
        v1 = "no more than a change of seed"
    else:
        v1 = "partly"
    out.append({"test": "Rule 1b how much the content changes: edit cards against seed cards", "value": f"edits {rnd(ar)} (n {nar}); seed {rnd(asd)} (n {nas})", "verdict": v1})
    ok = sn is not None and sn <= 0.35
    out.append({"test": "Rule 0 null cards (different perturbations) called the same", "value": f"{rnd(sn)} (n {nn})", "verdict": "ok" if ok else "too high: pass not valid"})
    if not ok or sr is None or nr < 6:
        v = "not testable"
    elif sr - sn >= 0.30:
        v = "the change repeats across seeds"
    elif sr - sn <= 0.10:
        v = "the change does not repeat"
    else:
        v = "partly"
    out.append({"test": "Rule 2 real edits and presets against null", "value": f"real {rnd(sr)} (n {nr}); null {rnd(sn)}", "verdict": v})
    out.append({"test": "Reported: seed cards, the same kind of change in every pair", "value": f"{rnd(ss)} (n {ns_})", "verdict": "-"})
    for q in ("light", "scene"):
        f = lambda a, q=q: SC.get(a.get(q))
        out.append({"test": f"Reported [{q}] alone", "value": "; ".join(f"{k} {rnd(mean(lambda t, k=k: t[0] == k, f)[0])} (n {mean(lambda t, k=k: t[0] == k, f)[1]})" for k in ("real", "null", "seed")), "verdict": "-"})
        out.append({"test": f"Reported [{q}] 'non si vede'", "value": str(sum(a[q] == "nonsivede" for a in first.values())), "verdict": "-"})
    out.append({"test": "Reported per perturbation (same kind; amount)", "value": "; ".join(f"{n} {rnd(mean(lambda t, n=n: t[1] == n)[0])}; {rnd(mean(lambda t, n=n: t[1] == n, amt)[0])}" for n in PERTS), "verdict": "-"})
    rr = [(a, b) for a, b in reps if a]
    out.append({"test": "Reported test-retest", "value": f"amount {sum(a['amount'] == b['amount'] for a, b in rr)}/{len(rr)}, light {sum(a['light'] == b['light'] for a, b in rr)}/{len(rr)}, scene {sum(a['scene'] == b['scene'] for a, b in rr)}/{len(rr)}", "verdict": "-"})
    return out


def selftest():
    st = {"pairs": {"P|E14": {"status": "open", "round": 0, "tested": [0.4, 0.8, 1.6, 3.2]}}, "D": {}}
    curve = lambda x: min(1.0, 0.02 * x ** 3)
    for x in (0.4, 0.8, 1.6, 3.2):
        st["D"][f"P|{tag('E14', x)}"] = [curve(x), curve(x)]
    nx = next_strengths(st, "P", "E14"); assert len(nx) == 1 and 1.6 < nx[0] < 3.2, nx
    st["D"][f"P|{tag('E14', nx[0])}"] = [curve(nx[0])] * 2
    nx2 = next_strengths(st, "P", "E14")
    if nx2:
        st["D"][f"P|{tag('E14', nx2[0])}"] = [curve(nx2[0])] * 2; next_strengths(st, "P", "E14")
    x, m = choose(st, "P", "E14"); assert x is not None and abs(m - TARGET) < 0.08, (x, m)
    assert set(PERTS) == set(LADDER) and len(PERTS) == 8 and len(set(TEST_SEEDS + CAL_SEEDS)) == 10
    assert all(x * 0.3 <= 1.0 for x in LADDER["P01"])
    g = {}
    for Ls, d in PRESETS["P06"].items():
        g.update(T.gj(int(Ls), d))
    assert len(g) == 12
    # rules on synthetic labels: real cards "stesso" and "molto", null "diversi", seed "diversi" and "poco"
    rng = random.Random(1); C = {n: f"{n}_1" for n in PERTS}; U = unit_specs(C, rng)
    key, lab = {}, []
    for i, u in enumerate(U):
        uid = f"T{i:02d}"; key[uid] = {"kind": u["kind"], "pert": u["pert"], "group": str(u["group"]), "pairs": " ".join(":".join(x) for x in u["pairs"]), "repeat": "0"}
        a = {"real": "stesso", "seed": "diversi", "null": "diversi"}[u["kind"]]
        lab.append({"unit": uid, "amount": "poco" if u["kind"] == "seed" else "molto", "light": a, "scene": "nonsivede"})
    o = {r["test"]: r["verdict"] for r in rules(lab, key)}
    assert o["Rule 2 real edits and presets against null"] == "the change repeats across seeds", o
    assert o["Rule 1b how much the content changes: edit cards against seed cards"] == "the edits change the content more than a change of seed", o
    assert sum(u["kind"] == "seed" for u in U) == 4 and sum(u["kind"] == "null" for u in U) == 8
    # dino tests on synthetic vectors: identical plain trees, a fixed shift per perturbation
    rs = np.random.default_rng(0); base = rs.normal(size=16) + 5; V = {}
    for s in TEST_SEEDS:
        V[(s, "C0")] = base + 0.01 * rs.normal(size=16)
    shift = {n: rs.normal(size=16) * 3 for n in PERTS}
    global conds_by_pert
    keep = conds_by_pert; conds_by_pert = lambda: {n: f"{n}_1" for n in PERTS}
    try:
        for s in TEST_SEEDS:
            for n in PERTS:
                V[(s, f"{n}_1")] = V[(s, "C0")] + shift[n]
        o = {r["test"]: r for r in dino_tests(V, {})}
        assert o["Rule 1 plain seeds: median pairwise D of the 8 plain trees"]["verdict"] == "nearly the same picture at every seed", o
    finally:
        conds_by_pert = keep
    print("selftest ok;", len(U), "cards with every perturbation reached (+4 repeats)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "calibrate", "plan", "gate", "count", "analyze", "page", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--queue", action="store_true"); ap.add_argument("--block")
    a = ap.parse_args()
    TX = texts()
    if a.selftest: selftest()
    if a.calibrate: calibrate()
    if a.plan: plan()
    if a.queue: queue(a.block)
    if a.gate: gate()
    if a.count: count()
    if a.analyze: analyze()
    if a.page: page()
    if a.rules:
        out = rules(rd(LABELS), {r["unit"]: r for r in rd(KEY)})
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
