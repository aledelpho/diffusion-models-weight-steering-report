"""C112 - a subject fixed by the prompt, the setting left free: does the plain model fall back on one picture at every
seed, and does a text-encoder edit choose another version and keep it at every seed? (docs/prereg_te_settings.md)
Written 2026-10-28 with the pre-registration, before any encode or render. Prompts written by Alessandro, never rendered.
Hypothesis from C111's exploratory run (Benchmark_te_tree_2): E28 at 1.06 moved the twisted tree to a park lawn at 8 of 8
seeds, P01 at 0.71 to an ivy-covered trunk at about 6 of 8. Doses fixed to that run's (no calibration).
Encoder and workflow are C111's (te_tree.py), reused unchanged.

  python te_settings.py --selftest
  python te_settings.py --plan            # GPU: conditionings -> data/te_settings_plan.csv
  python te_settings.py --queue --block gate | main
  python te_settings.py --gate            # plain through the conditioning file = plain through the text, 4 prompts
  python te_settings.py --count
  python te_settings.py --analyze         # GPU: DINOv2 -> data/te_settings_metrics.csv, data/te_settings_dino_tests.csv
  python te_settings.py --page            # blind page Text2Img/occhio_C112.html (after --analyze)
  python te_settings.py --rules           # once data/te_settings_labels.csv exists
"""
import argparse, csv, itertools, json, os, random, statistics, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_tree as TT
import te_depth_control as T

DATA = HERE.parent / "data"
PLAN, METRICS, DTESTS = DATA / "te_settings_plan.csv", DATA / "te_settings_metrics.csv", DATA / "te_settings_dino_tests.csv"
KEY, LABELS, TESTS = DATA / "te_settings_key.csv", DATA / "te_settings_labels.csv", DATA / "te_settings_tests.csv"
FOLDER = "benchmark_te_settings"
PROMPTS = {"S1_bluetree": "A curved tree with large blue leaves",
           "S2_alienaxe": "A short alien axe with a weird shaped blade",
           "S3_evilhelmet": "Cartoon evil helmet with black metal and a big red gemstone",
           "S4_flyingcar": "A concept yellow flying car"}
SUBJECTS = list(PROMPTS)
DOSES = {"E05": 0.28285, "E06": 0.4, "E14": 0.4, "E26": 0.53033, "E28": 1.06066, "P01": 0.7071, "P06": 0.8409, "P10": 1.0}
PRIMARY = ["E28", "P01"]
SEEDS = TT.TEST_SEEDS
PLAIN_MAX = 0.15

TT.FOLDER, TT.TX, TT.SUBJECTS = FOLDER, PROMPTS, SUBJECTS
assert set(DOSES) == set(TT.PERTS)


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def plan():
    (T.img_root() / FOLDER / "conds").mkdir(parents=True, exist_ok=True)
    E = TT.Enc(); rows = []
    for p in SUBJECTS:
        E.save(p, "C0", 0)
        rows.append(TT.row("gate", p, SEEDS[0], "TEXT", variant="text"))
    for p in SUBJECTS:
        for s in SEEDS:
            rows.append(TT.row("main", p, s, "C0"))
            for n, x in DOSES.items():
                t = E.save(p, n, x)
                if t is None:
                    print("NONFINITE", p, n, x); continue
                rows.append(TT.row("main", p, s, t))
    TT.write(PLAN, rows); print("plan rows:", len(rows), "(292 expected)")


def queue(block):
    n = 0
    for r in rd(PLAN):
        if r["block"] != block or (T.img_root() / FOLDER / r["expected_filename"]).exists():
            continue
        TT.post(r); n += 1
    print("queued", n)


def gate():
    from PIL import Image
    R = T.img_root() / FOLDER; ok = True
    for p in SUBJECTS:
        a, b = R / TT.fname(p, "C0", SEEDS[0]), R / TT.fname(p, "TEXT", SEEDS[0])
        if not (a.exists() and b.exists()):
            print("missing", p); ok = False; continue
        d = int(np.abs(np.asarray(Image.open(a).convert("RGB"), dtype=np.int16) - np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)).max())
        print(f"{a.name} vs {b.name}: max abs diff {d}"); ok &= d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN); miss = [r["expected_filename"] for r in rows if not (T.img_root() / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def conds():
    """(subject, pert) -> condition tag."""
    return {(r["char"], r["cond"].split("_")[0]): r["cond"] for r in rd(PLAN) if r["block"] == "main" and r["cond"] != "C0"}


cosd = TT.cosd
cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def dino_tests(V, C):
    out, n_coll = [], 0
    for p in SUBJECTS:
        d = statistics.median(cosd(V[(p, a, "C0")], V[(p, b, "C0")]) for a, b in itertools.combinations(SEEDS, 2))
        n_coll += d <= PLAIN_MAX
        out.append({"test": f"Rule 1 {p}: median pairwise D of the 8 plain pictures", "value": f"{d:.3f} (bar {PLAIN_MAX})",
                    "verdict": "same picture at every seed" if d <= PLAIN_MAX else "the seeds vary"})
    out.append({"test": "Rule 1 prompts whose plain pictures are the same at every seed", "value": f"{n_coll} of {len(SUBJECTS)}",
                "verdict": "supported (>= 3 of 4)" if n_coll >= 3 else "not supported"})
    for p in SUBJECTS:
        mv = {n: statistics.median(cosd(V[(p, s, C[(p, n)])], V[(p, s, "C0")]) for s in SEEDS) for n in DOSES if (p, n) in C}
        U = {n: {s: V[(p, s, C[(p, n)])] - V[(p, s, "C0")] for s in SEEDS} for n in DOSES if (p, n) in C}
        w = {n: statistics.mean(cos(U[n][a], U[n][b]) for a, b in itertools.combinations(SEEDS, 2)) for n in U}
        null = statistics.mean(cos(U[m][a], U[n][b]) for m, n in itertools.permutations(U, 2) for a, b in itertools.permutations(SEEDS, 2))
        out.append({"test": f"Reported {p}: median D from plain per edit", "value": "; ".join(f"{n} {v:.3f}" for n, v in mv.items()), "verdict": "-"})
        out.append({"test": f"Reported {p}: mean cosine of the displacements across seeds per edit (null: different edits, different seeds)",
                    "value": "; ".join(f"{n} {v:.2f}" for n, v in w.items()) + f"; null {null:.2f}", "verdict": "-"})
    return out


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = T.img_root() / FOLDER; m = MV.Models(vqa=False)
    V = {(r["char"], r["seed"], r["cond"]): np.asarray(m.dino_vec(Image.open(R / r["expected_filename"]).convert("RGB")), dtype=np.float64)
         for r in rd(PLAN) if r["block"] == "main"}
    met = [{"prompt": p, "seed": s, "cond": c, "pert": c.split("_")[0], "dinov2_dist_to_base": round(cosd(v, V[(p, s, "C0")]), 6)}
           for (p, s, c), v in V.items() if c != "C0"]
    with open(METRICS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(met[0])); w.writeheader(); w.writerows(met)
    out = dino_tests(V, conds())
    with open(DTESTS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


# ---------------------------------------------------------------- blind
QS, SC, MSC = TT.QS, TT.SC, TT.MSC


def unit_specs(names, rng):
    """Cards of 8 pairs (every seed). Edit: plain -> one edit. Null: plain -> a different edit at each seed.
    Seed: plain at a seed -> plain at another seed."""
    U = []
    for p in SUBJECTS:
        for n in names:
            U.append({"kind": "edit", "prompt": p, "pert": n, "pairs": [(s, "C0", s, n) for s in SEEDS]})
        for _ in range(2):
            ps = [rng.choice(names) for _ in SEEDS]
            while len(set(ps)) < 6:
                ps = [rng.choice(names) for _ in SEEDS]
            U.append({"kind": "null", "prompt": p, "pert": "mixed", "pairs": [(s, "C0", s, n) for s, n in zip(SEEDS, ps)]})
        U.append({"kind": "seed", "prompt": p, "pert": "seed", "pairs": [(s, "C0", SEEDS[(i + 4) % 8], "C0") for i, s in enumerate(SEEDS)]})
    return U


def page():
    from eye_grid_page import thumb, build
    R = T.img_root(); root = str(R); rng = random.Random(11212); C = conds()
    U = unit_specs(list(DOSES), rng); rng.shuffle(U)
    reps = rng.sample([i for i, u in enumerate(U) if u["kind"] == "edit"], 4); order = list(range(len(U)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 10, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for k_, i in enumerate(order, 1):
        u = U[i]; uid = f"U{k_:02d}"
        key.append({"unit": uid, "kind": u["kind"], "prompt": u["prompt"], "pert": u["pert"],
                    "pairs": " ".join(":".join(x) for x in u["pairs"]), "repeat": int(i in seen)}); seen.add(i)
        cc = lambda n: "C0" if n == "C0" else C[(u["prompt"], n)]
        rows = []
        for k, (s, n0, s2, n) in enumerate(u["pairs"], 1):
            a = thumb(str(R / FOLDER / TT.fname(u["prompt"], cc(n0), s)), root); b = thumb(str(R / FOLDER / TT.fname(u["prompt"], cc(n), s2)), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {k_:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_C112.html"), "C112 · lo stesso cambiamento a ogni seed?", units, QS, TT.OPTS, "c112_labels_v1", "te_settings_labels.csv")
    print("cards", len(units), "->", os.path.join(root, "occhio_C112.html"))


def rules(labels, key):
    out, first, reps = [], {}, []
    for r in labels:
        k = key.get(r["unit"])
        if not k:
            continue
        a = {q: (r.get(q) or "").strip() for q in ("amount", "light", "scene")}
        if not any(a.values()):
            continue
        t = (k["kind"], k["prompt"], k["pert"], k["pairs"])
        if k["repeat"] == "1" or t in first:
            reps.append((first.get(t), a)); continue
        first[t] = a
    same = TT.card_score; amt = lambda a: MSC.get(a.get("amount"))
    def mean(sel, f=same):
        v = [f(a) for t, a in first.items() if sel(t) and f(a) is not None]
        return (sum(v) / len(v) if v else None), len(v)
    rnd = lambda x: "-" if x is None else f"{x:.2f}"
    prim = lambda t: t[0] == "edit" and t[2] in PRIMARY
    sn, nn = mean(lambda t: t[0] == "null"); ok = sn is not None and sn <= 0.35
    out.append({"test": "Rule 0 null cards called the same", "value": f"{rnd(sn)} (n {nn})", "verdict": "ok" if ok else "too high: pass not valid"})
    ap, nap = mean(prim, amt); asd, nas = mean(lambda t: t[0] == "seed", amt)
    if ap is None or asd is None or nap < 4 or nas < 3:
        v = "not testable"
    else:
        v = "the edits change the content more than a change of seed" if ap - asd >= 0.30 else ("no more than a change of seed" if ap - asd <= 0.10 else "partly")
    out.append({"test": "Rule 1b amount: E28 and P01 cards against seed cards", "value": f"edits {rnd(ap)} (n {nap}); seed {rnd(asd)} (n {nas})", "verdict": v})
    sp, nsp = mean(prim)
    if not ok or sp is None or nsp < 4:
        v = "not testable"
    else:
        v = "the change repeats across seeds" if sp - sn >= 0.30 else ("the change does not repeat" if sp - sn <= 0.10 else "partly")
    out.append({"test": "Rule 2 E28 and P01 cards against null (same kind)", "value": f"edits {rnd(sp)} (n {nsp}); null {rnd(sn)}", "verdict": v})
    sa, nsa = mean(lambda t: t[0] == "edit"); ss, nss = mean(lambda t: t[0] == "seed")
    out.append({"test": "Reported: all eight edits against null; seed cards", "value": f"all edits {rnd(sa)} (n {nsa}); seed {rnd(ss)} (n {nss})", "verdict": "-"})
    for q in ("light", "scene"):
        f = lambda a, q=q: SC.get(a.get(q))
        out.append({"test": f"Reported [{q}] alone: E28+P01 / null / seed", "value": " / ".join(rnd(mean(sel, f)[0]) for sel in (prim, lambda t: t[0] == "null", lambda t: t[0] == "seed")), "verdict": "-"})
    for p in SUBJECTS:
        out.append({"test": f"Reported {p}: same kind (amount) per edit", "value": "; ".join(f"{n} {rnd(mean(lambda t, n=n, p=p: t[0] == 'edit' and t[1] == p and t[2] == n)[0])} ({rnd(mean(lambda t, n=n, p=p: t[0] == 'edit' and t[1] == p and t[2] == n, amt)[0])})" for n in DOSES), "verdict": "-"})
    rr = [(a, b) for a, b in reps if a]
    out.append({"test": "Reported test-retest", "value": ", ".join(f"{q} {sum(a[q] == b[q] for a, b in rr)}/{len(rr)}" for q in ("amount", "light", "scene")), "verdict": "-"})
    return out


def selftest():
    rng = random.Random(1); U = unit_specs(list(DOSES), rng)
    assert len(U) == 4 * (8 + 2 + 1) and all(len(u["pairs"]) == 8 for u in U)
    assert all(a != b for u in U if u["kind"] == "seed" for a, _, b, _ in u["pairs"])
    key, lab = {}, []
    for i, u in enumerate(U):
        uid = f"U{i:02d}"; key[uid] = {"kind": u["kind"], "prompt": u["prompt"], "pert": u["pert"], "pairs": " ".join(":".join(x) for x in u["pairs"]), "repeat": "0"}
        hit = u["kind"] == "edit" and u["pert"] in PRIMARY
        lab.append({"unit": uid, "amount": "molto" if hit else "poco", "light": "nonsivede", "scene": "stesso" if hit else "diversi"})
    o = {r["test"]: r["verdict"] for r in rules(lab, key)}
    assert o["Rule 2 E28 and P01 cards against null (same kind)"] == "the change repeats across seeds", o
    assert o["Rule 1b amount: E28 and P01 cards against seed cards"] == "the edits change the content more than a change of seed", o
    rs = np.random.default_rng(0); V = {}; C = {(p, n): f"{n}_x" for p in SUBJECTS for n in DOSES}
    for p in SUBJECTS:
        base = rs.normal(size=16) + 5
        for s in SEEDS:
            V[(p, s, "C0")] = base + (0.01 if p != "S4_flyingcar" else 3) * rs.normal(size=16)
            for n in DOSES:
                V[(p, s, f"{n}_x")] = V[(p, s, "C0")] + rs.normal(size=16)
    o = {r["test"]: r["verdict"] for r in dino_tests(V, C)}
    assert o["Rule 1 prompts whose plain pictures are the same at every seed"] == "supported (>= 3 of 4)", o
    assert TT.tag("P01", DOSES["P01"]) == "P01_0p7071" and TT.tag("E28", DOSES["E28"]) == "E28_1p06066"
    print("selftest ok;", len(U), "cards (+4 repeats)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "plan", "gate", "count", "analyze", "page", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--queue", action="store_true"); ap.add_argument("--block")
    a = ap.parse_args()
    if a.selftest: selftest()
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
