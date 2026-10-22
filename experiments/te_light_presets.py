"""C109 - light text-encoder presets: four MLP layers at about +-0.30 each, calibrated per subject like C105
(docs/prereg_te_light_presets.md). Written 2026-10-22 with the pre-registration, before any encode or render.
Generated from te_light_presets.py (C105) with the perturbations replaced by 12 presets; the calibration, plan,
queue, gate, count and analyze steps are C105's unchanged. Renders authorised by Alessandro on 2026-10-22.

  python te_light_presets.py --selftest
  python te_light_presets.py --calibrate     # GPU + ComfyUI running: encodes, queues, waits, measures, decides (resumable)
  python te_light_presets.py --plan          # GPU: matched test conditionings -> data/te_light_presets_plan.csv
  python te_light_presets.py --queue --block gate | main
  python te_light_presets.py --gate
  python te_light_presets.py --count
  python te_light_presets.py --analyze       # GPU: DINOv2 of the test renders (match check)
  (blind page and rules: written after the renders, as pre-registered; do NOT run --page or --rules, they are still C105's)
"""
import argparse, csv, gc, json, math, os, random, statistics, sys, time, urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_depth_control as T

DATA = HERE.parent / "data"
STATE = DATA / "te_light_presets_cal_state.json"
CALPLAN = DATA / "te_light_presets_cal_plan.csv"
PLAN = DATA / "te_light_presets_plan.csv"
METRICS = DATA / "te_light_presets_metrics.csv"
KEY = DATA / "te_light_presets_key.csv"
LABELS = DATA / "te_light_presets_labels.csv"
TESTS = DATA / "te_light_presets_tests.csv"
FOLDER = "benchmark_te_light_presets"
COMICS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter", "G5_gnome_wizard"]
OTHER = ["S1_rally", "C4_stilllife", "P2_lotuscanoe", "LN"]
SUBJECTS = COMICS + OTHER
# 12 presets drawn with random.Random(10909): P01-P06 four distinct MLP layers in 7-24, P07-P12 in 1-34; sign random;
# nominal dose 0.30 per layer. Strength x multiplies all four doses (x = 1 is the nominal +-0.30).
PRESETS = {"P01": {"7": 0.3, "9": -0.3, "11": 0.3, "17": 0.3}, "P02": {"12": 0.3, "21": 0.3, "22": -0.3, "24": 0.3}, "P03": {"9": 0.3, "14": -0.3, "16": 0.3, "23": 0.3}, "P04": {"10": -0.3, "12": -0.3, "17": -0.3, "18": -0.3}, "P05": {"10": -0.3, "17": 0.3, "18": 0.3, "19": -0.3}, "P06": {"9": 0.3, "11": -0.3, "20": -0.3, "22": 0.3}, "P07": {"2": 0.3, "18": 0.3, "19": -0.3, "26": -0.3}, "P08": {"1": -0.3, "9": -0.3, "21": -0.3, "32": 0.3}, "P09": {"5": 0.3, "7": 0.3, "25": 0.3, "26": 0.3}, "P10": {"14": 0.3, "15": 0.3, "29": 0.3, "30": -0.3}, "P11": {"9": -0.3, "14": 0.3, "18": -0.3, "27": 0.3}, "P12": {"2": -0.3, "4": 0.3, "6": -0.3, "34": 0.3}}
PERTS = {n: ("preset", None) for n in PRESETS}
LADDER = {n: [0.5, 1.0, 2.0, 3.3] for n in PRESETS}   # x <= 3.3 keeps every dose above -1 (no sign flip)
LADDER["E14"] = [0.4, 0.8, 1.6, 3.2]   # used only by the calibration self-test
CAL_SEEDS = ["1618033", "2718281"]
TEST_SEEDS = ["2645751", "3316624"]
TARGET, LO, HI, ACC_LO, ACC_HI, ROUNDS = 0.25, 0.20, 0.32, 0.15, 0.40, 2
MATCH_LO, MATCH_HI, MIN_CELLS = 0.10, 0.45, 3        # amendment 1 (2026-10-20, before the blind pass)
SET = T.SET
SETS = {"WC": COMICS, "WO": OTHER, "X1": ["D1_dwarf_paladin", "E2_elf_rogue", "S1_rally", "C4_stilllife"],
        "X2": ["O4_halforc_fighter", "G5_gnome_wizard", "P2_lotuscanoe", "LN"]}
GATE_HARD = {(p, s): f"benchmark_portraits/phase_c/{p}_baseline_krea2_seed{s}_00001_.png" for p in ["D1_dwarf_paladin"] for s in TEST_SEEDS}
GATE_HARD.update({(p, s): f"benchmark_te_depth_control/{p}_C0_krea2_seed{s}_00001_.png" for p in ["S1_rally", "C4_stilllife"] for s in TEST_SEEDS})
GATE_SOFT = {(p, s): f"benchmark_portraits/phase_c/{p}_baseline_krea2_seed{s}_00001_.png" for p in COMICS[1:] for s in TEST_SEEDS}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def texts():
    import te_shapes2 as TS2
    t = {k: v for k, v in TS2.texts().items() if k in SUBJECTS}
    for r in rd(DATA / "te_characters_plan.csv"):
        if r["char"] in SUBJECTS:
            t.setdefault(r["char"], r["prompt_text"])
    assert set(t) == set(SUBJECTS), set(SUBJECTS) - set(t)
    return t


def tag(n, x):
    return f"{n}_{x:g}".replace(".", "p")


def cpath(p, t):
    return T.img_root() / FOLDER / "conds" / f"{p}_{t}.pt"


def fname(p, t, s):
    return f"{p}_{t}_krea2_seed{s}_00001_.png"


def row(block, p, s, t):
    prefix = f"{p}_{t}_krea2_seed{s}"
    return {"block": block, "char": p, "seed": s, "cond": t, "variant": "file", "push_path": str(cpath(p, t)), "noise_seed": 7,
            "taps": "", "te_granular_json": "{}", "prompt_text": TX[p], "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET}


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
    with open(DATA / "te_light_presets_strengths.csv", "w", newline="", encoding="utf-8") as f:
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
    S = {(r["prompt"], r["pert"]): r for r in rd(DATA / "te_light_presets_strengths.csv")}
    for p in SUBJECTS:
        E.save(p, "C0", 0)
    for (p, s) in GATE_HARD:
        rows.append(row("gate", p, s, "C0"))
    for p in SUBJECTS:
        for s in TEST_SEEDS:
            if (p, s) not in GATE_HARD:
                rows.append(row("main", p, s, "C0"))
            for n in PERTS:
                r = S[(p, n)]
                if int(r["reached"]):
                    t = E.save(p, n, float(r["strength"]))
                    rows.append(row("main", p, s, t))
    write(PLAN, rows); print("plan rows:", len(rows), "(208 if every pair was reached)")


def post(r):
    import blk23_colorful as c47
    wf = T.workflow({**r}); wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
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
    R = T.img_root(); ok = True
    for hard, G in ((True, GATE_HARD), (False, GATE_SOFT)):
        for (p, s), ref in G.items():
            a = R / FOLDER / fname(p, "C0", s)
            if not a.exists():
                print("missing", a.name); ok &= not hard; continue
            d = int(np.abs(np.asarray(Image.open(a).convert("RGB"), dtype=np.int16) - np.asarray(Image.open(R / ref).convert("RGB"), dtype=np.int16)).max())
            print(f"{'' if hard else '(reported) '}{a.name}: max abs diff {d}"); ok &= (d == 0) or not hard
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN); miss = [r["expected_filename"] for r in rows if not (T.img_root() / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = T.img_root() / FOLDER; m = MV.Models(vqa=False); V = {}; out = []
    rows = rd(PLAN)
    for r in rows:
        V[(r["char"], r["seed"], r["cond"])] = np.asarray(m.dino_vec(Image.open(R / r["expected_filename"]).convert("RGB")), dtype=np.float64)
    for (p, s, c), v in V.items():
        if c != "C0":
            b = V[(p, s, "C0")]
            out.append({"prompt": p, "seed": s, "cond": c, "pert": c.split("_")[0], "dinov2_dist_to_base": round(1 - float(v @ b / (np.linalg.norm(v) * np.linalg.norm(b))), 6)})
    with open(METRICS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("wrote", METRICS, len(out))


# ---------------------------------------------------------------- blind
OPTS = [("stesso", "stesso modo"), ("simile", "qualcosa di simile"), ("diversi", "in modi diversi"), ("nonsivede", "non si vede")]  # "simile": amendment 2


def matched_cells():
    M = {}
    for r in rd(METRICS):
        M.setdefault((r["prompt"], r["pert"]), []).append(float(r["dinov2_dist_to_base"]))
    return {k for k, v in M.items() if MATCH_LO <= statistics.median(v) <= MATCH_HI}, M


def unit_specs(ok):
    """Amendment 1: a unit keeps the subjects whose cell is matched, if at least MIN_CELLS remain; a control unit takes the
    first rotation (by seed) that leaves at least MIN_CELLS matched cells."""
    U = []
    for n in PERTS:
        for s in TEST_SEEDS:
            for k, subj in SETS.items():
                cells = [(p, n) for p in subj if (p, n) in ok]
                if len(cells) >= MIN_CELLS:
                    U.append({"kind": k, "pert": n, "seed": s, "cells": cells})
    names = list(PERTS)
    for i, s in enumerate(TEST_SEEDS):
        for k, subj in SETS.items():
            for r in range(4):
                cells = [c for c in ((p, names[(j + i + r) % 4]) for j, p in enumerate(subj)) if c in ok]
                if len(cells) >= MIN_CELLS:
                    U.append({"kind": "N" + k, "pert": "mixed", "seed": s, "cells": cells}); break
    return U


def page():
    from eye_grid_page import thumb, build
    R = T.img_root(); root = str(R); rng = random.Random(10505)
    ok, _ = matched_cells(); strengths = {(r["prompt"], r["pert"]): r for r in rd(DATA / "te_light_presets_strengths.csv")}
    U = unit_specs(ok); rng.shuffle(U)
    reps = rng.sample(range(len(U)), 6); order = list(range(len(U)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 10, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for n_, i in enumerate(order, 1):
        u = U[i]; uid = f"Z{n_:02d}"
        key.append({"unit": uid, "kind": u["kind"], "pert": u["pert"], "seed": u["seed"], "cells": " ".join(f"{p}:{n}" for p, n in u["cells"]), "repeat": int(i in seen)}); seen.add(i)
        rows = []
        for k, (p, n) in enumerate(u["cells"], 1):
            t = tag(n, float(strengths[(p, n)]["strength"]))
            a, b = thumb(str(R / FOLDER / fname(p, "C0", u["seed"])), root), thumb(str(R / FOLDER / fname(p, t, u["seed"])), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n_:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    qs = [("content", "Il tipo di cambiamento del contenuto (soggetti, forme, oggetti, età, materiali) è lo stesso in tutte le coppie?", OPTS),
          ("style", "Il tipo di cambiamento dello stile (resa, tecnica, colori, tratto) è lo stesso in tutte le coppie?", OPTS)]
    build(os.path.join(root, "occhio_C105.html"), "C105 · lo stesso cambiamento su soggetti diversi?", units, qs, OPTS, "c105_labels_v2", "te_light_presets_labels.csv")
    print("units", len(units), "->", os.path.join(root, "occhio_C105.html"))


def rules(labels, key, match_report=None):
    out = []
    if match_report:
        out.append({"test": "Rule 0 matched subject x perturbation (reported)", "value": match_report, "verdict": ""})
    first, reps = {}, []
    for r in labels:
        k = key[r["unit"]]; tagk = (k["kind"], k["pert"], k["seed"], k["cells"])
        a = {q: (r.get(q) or "").strip() for q in ("content", "style")}
        if not any(a.values()):
            continue
        if tagk in first:
            reps.append((first[tagk], a)); continue
        first[tagk] = a
    SC = {"stesso": 1.0, "simile": 0.5, "diversi": 0.0}               # amendment 2: s = mean score
    def share(sel, q, binary=False):
        keep = ("stesso", "diversi") if binary else tuple(SC)
        v = [SC[a[q]] for t, a in first.items() if sel(t) and a[q] in keep]
        return (sum(v) / len(v) if v else None), len(v)
    for q in ("content", "style"):
        sn, nn = share(lambda t: t[0].startswith("N"), q)
        null_ok = sn is not None and sn <= 0.35
        out.append({"test": f"Rule 1 [{q}] null: different perturbations called the same", "value": f"s(N) {sn if sn is None else round(sn, 2)} (n {nn})",
                    "verdict": ("ok" if null_ok else "too high: rule 2 not testable") if q == "content" else ""})
        for typ, ps in (("edits", ("E14", "E26")), ("random", ("R09", "R26"))):
            sw, nw = share(lambda t: t[1] in ps and t[0] in ("WC", "WO"), q)
            sm, nm = share(lambda t: t[1] in ps and t[0] in ("X1", "X2"), q)
            if q == "content" and not null_ok:
                v = "not testable"
            elif sw is None or sm is None or nw < 6 or nm < 6 or sn is None:
                v = "not testable (too few units)"
            elif sw - sn < 0.30:
                v = "no transfer"
            elif sw - sm >= 0.30:
                v = "domain-specific"
            elif sm - sn >= 0.30:
                v = "transfers across domains"
            else:
                v = "partly"
            out.append({"test": f"Rule 2 [{q}] {typ}", "value": f"within {sw if sw is None else round(sw, 2)} (n {nw}); mixed {sm if sm is None else round(sm, 2)} (n {nm}); null {sn if sn is None else round(sn, 2)}",
                        "verdict": v if q == "content" else f"(reported) {v}"})
        per = []
        for n in PERTS:
            sw, nw = share(lambda t: t[1] == n and t[0] in ("WC", "WO"), q); sm, nm = share(lambda t: t[1] == n and t[0] in ("X1", "X2"), q)
            per.append(f"{n} within {sw if sw is None else round(sw, 2)} (n {nw}) mixed {sm if sm is None else round(sm, 2)} (n {nm})")
        out.append({"test": f"Rule 3 [{q}] per perturbation (reported)", "value": "; ".join(per), "verdict": ""})
    for q in ("content", "style"):                                   # amendment 2: sensitivity without "simile"
        vals = []
        for lab_, sel in (("null", lambda t: t[0].startswith("N")), ("edits within", lambda t: t[1] in ("E14", "E26") and t[0] in ("WC", "WO")),
                          ("edits mixed", lambda t: t[1] in ("E14", "E26") and t[0] in ("X1", "X2")), ("random within", lambda t: t[1] in ("R09", "R26") and t[0] in ("WC", "WO")),
                          ("random mixed", lambda t: t[1] in ("R09", "R26") and t[0] in ("X1", "X2"))):
            v, n_ = share(sel, q, binary=True); vals.append(f"{lab_} {v if v is None else round(v, 2)} (n {n_})")
        out.append({"test": f"Rule 3 [{q}] binary, 'simile' left out (reported)", "value": "; ".join(vals), "verdict": ""})
        out.append({"test": f"Rule 3 [{q}] 'simile' answers (reported)", "value": str(sum(a[q] == "simile" for a in first.values())), "verdict": ""})
    ns = {q: sum(a[q] == "nonsivede" for a in first.values()) for q in ("content", "style")}
    out.append({"test": "Rule 3 'non si vede' (reported)", "value": f"content {ns['content']}, style {ns['style']}", "verdict": ""})
    if reps:
        out.append({"test": "Rule 3 test-retest (reported)", "value": f"content {sum(a['content'] == b['content'] for a, b in reps)}/{len(reps)}, style {sum(a['style'] == b['style'] for a, b in reps)}/{len(reps)}", "verdict": ""})
    return out


def selftest():
    # calibration state machine
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
    st2 = {"pairs": {"P|E14": {"status": "open", "round": 0, "tested": [0.4, 0.8]}}, "D": {"P|E14_0p4": [0.01, 0.01], "P|E14_0p8": [0.02, 0.02]}}
    assert next_strengths(st2, "P", "E14") == [] and choose(st2, "P", "E14")[0] is None
    g = {}
    for Ls, d in PRESETS["P01"].items():
        g.update(T.gj(int(Ls), d * 2.0))
    assert len(PRESETS) == 12 and all(len(v) == 4 for v in PRESETS.values()) and len(g) == 12, g
    assert all(abs(abs(v) - 0.60) < 1e-9 for v in g.values()), g
    global TX
    TX = texts(); assert len(TX) == 8
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "calibrate", "plan", "gate", "count", "analyze", "page", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--queue", action="store_true"); ap.add_argument("--block")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.calibrate: calibrate()
    if a.plan: plan()
    if a.queue: TX = texts(); queue(a.block)
    if a.gate: gate()
    if a.count: count()
    if a.analyze: analyze()
    if a.page: page()
    if a.rules:
        ok, M = matched_cells()
        rep = f"{len(ok)} of {len(M)} within {MATCH_LO}-{MATCH_HI}; not matched: " + ", ".join(f"{p}:{n} {statistics.median(v):.2f}" for (p, n), v in sorted(M.items()) if (p, n) not in ok)
        out = rules(rd(LABELS), {r["unit"]: r for r in rd(KEY)}, rep)
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
