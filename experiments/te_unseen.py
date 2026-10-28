"""C114 - blind confirmation on unseen prompts of the dose windows found in C113 (docs/prereg_te_unseen.md).
Written 2026-10-28 with the pre-registration, before any encode or render. Prompts written by Claude on the structure of
Alessandro's examples (subject + colour + style), not shown to him before the blind page, at his request.
Pipeline: C112's (te_settings.py / te_tree.py), reused; only prompts, edits and doses change.

  python te_unseen.py --selftest
  python te_unseen.py --plan            # GPU -> data/te_unseen_plan.csv
  python te_unseen.py --queue --block gate | main
  python te_unseen.py --gate
  python te_unseen.py --count
  python te_unseen.py --analyze         # GPU -> data/te_unseen_dino.csv (applied with the labels)
  python te_unseen.py --page            # blind page Text2Img/occhio_C114.html
  python te_unseen.py --rules           # once data/te_unseen_labels.csv exists
"""
import argparse, csv, itertools, os, random, statistics, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_tree as TT
import te_depth_control as T
import te_settings as S

DATA = HERE.parent / "data"
PLAN, DINO = DATA / "te_unseen_plan.csv", DATA / "te_unseen_dino.csv"
KEY, LABELS, TESTS = DATA / "te_unseen_key.csv", DATA / "te_unseen_labels.csv", DATA / "te_unseen_tests.csv"
FOLDER = "benchmark_te_unseen"
PROMPTS = {"U1_redtree": "A twisted tree with long red leaves and a curled trunk, watercolor painting",
           "U2_dagger": "A ceremonial dagger in art deco style with golden geometric inlays",
           "U3_robot": "A small green robot with round copper eyes, clay figurine"}
SUBJECTS = list(PROMPTS)
DOSES = {"E06": 0.8, "E14": 0.8, "E28": 1.06066, "P01": 1.75}      # C113's windows; P01 inside its bracket
SEEDS = TT.TEST_SEEDS
for mod in (S, TT):
    mod.FOLDER = FOLDER
S.PROMPTS, S.SUBJECTS, S.DOSES, S.PLAN = PROMPTS, SUBJECTS, DOSES, PLAN
TT.TX, TT.SUBJECTS = PROMPTS, SUBJECTS
TT.PERTS = {"E06": ("edit", 6), "E14": ("edit", 14), "E28": ("edit", 28), "P01": ("preset", None)}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def plan():
    S.plan()


cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def dino_rows(V, C):
    out = []
    for p in SUBJECTS:
        plain = statistics.median(1 - cos(V[(p, a, "C0")], V[(p, b, "C0")]) for a, b in itertools.combinations(SEEDS, 2))
        for n in DOSES:
            c = C[(p, n)]
            U = {s: V[(p, s, c)] - V[(p, s, "C0")] for s in SEEDS}
            D = statistics.median(1 - cos(V[(p, s, c)], V[(p, s, "C0")]) for s in SEEDS)
            out.append({"prompt": p, "edit": n, "dose": DOSES[n], "median_D_from_plain": round(D, 4), "plain_seed_D": round(plain, 4),
                        "ratio_to_seed": round(D / plain, 3), "consistency": round(statistics.mean(cos(U[a], U[b]) for a, b in itertools.combinations(SEEDS, 2)), 4)})
    return out


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = T.img_root() / FOLDER; m = MV.Models(vqa=False)
    V = {(r["char"], r["seed"], r["cond"]): np.asarray(m.dino_vec(Image.open(R / r["expected_filename"]).convert("RGB")), dtype=np.float64)
         for r in rd(PLAN) if r["block"] == "main"}
    out = dino_rows(V, S.conds())
    with open(DINO, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("wrote", DINO, len(out), "rows (not printed: applied with the labels)")


# ---------------------------------------------------------------- blind
KEPT = [("tutte", "sì, in tutte"), ("molte", "nella maggior parte"), ("poche", "solo in poche"), ("nessuna", "in nessuna")]
KSC = {"tutte": 1.0, "molte": 0.67, "poche": 0.33, "nessuna": 0.0}
QS = [S.QS[0], S.QS[1],
      ("kept", "3. Il soggetto, il colore e lo stile scritti nel prompt (sopra) ci sono ancora nella riga DOPO?", KEPT)]
SC, MSC = TT.SC, TT.MSC


def unit_specs(rng):
    U, names = [], list(DOSES)
    for p in SUBJECTS:
        for n in names:
            U.append({"kind": "edit", "prompt": p, "pert": n, "pairs": [(s, "C0", s, n) for s in SEEDS]})
        for _ in range(2):
            ps = [names[i % 4] for i in range(8)]; rng.shuffle(ps)
            U.append({"kind": "null", "prompt": p, "pert": "mixed", "pairs": [(s, "C0", s, n) for s, n in zip(SEEDS, ps)]})
        U.append({"kind": "seed", "prompt": p, "pert": "seed", "pairs": [(s, "C0", SEEDS[(i + 4) % 8], "C0") for i, s in enumerate(SEEDS)]})
    return U


def page():
    from eye_grid_page import thumb, build
    R = T.img_root(); root = str(R); rng = random.Random(11414); C = S.conds()
    U = unit_specs(rng); rng.shuffle(U)
    reps = rng.sample([i for i, u in enumerate(U) if u["kind"] == "edit"], 3); order = list(range(len(U)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 6, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for k_, i in enumerate(order, 1):
        u = U[i]; uid = f"W{k_:02d}"
        key.append({"unit": uid, "kind": u["kind"], "prompt": u["prompt"], "pert": u["pert"],
                    "pairs": " ".join(":".join(x) for x in u["pairs"]), "repeat": int(i in seen)}); seen.add(i)
        cc = lambda n: "C0" if n == "C0" else C[(u["prompt"], n)]
        top, bot = [], []
        for s, n0, s2, n in u["pairs"]:
            a = thumb(str(R / FOLDER / TT.fname(u["prompt"], cc(n0), s)), root); b = thumb(str(R / FOLDER / TT.fname(u["prompt"], cc(n), s2)), root)
            top.append({"t": a[0], "f": a[1]}); bot.append({"t": b[0], "f": b[1]})
        units.append({"id": uid, "title": f"Scheda {k_:02d} — prompt: «{PROMPTS[u['prompt']]}»",
                      "groups": [{"id": "g", "name": "", "cols": [str(c) for c in range(1, 9)],
                                  "rows": [{"label": "PRIMA", "cells": top}, {"label": "DOPO", "cells": bot}]}]})
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_C114.html"), "C114 · la stessa modifica a ogni seed, su prompt nuovi?", units, QS, TT.OPTS, "c114_labels_v1", "te_unseen_labels.csv")
    print("cards", len(units), "->", os.path.join(root, "occhio_C114.html"))


def rules(labels, key, dino):
    first, reps = {}, []
    for r in labels:
        k = key.get(r["unit"])
        if not k:
            continue
        a = {q: (r.get(q) or "").strip() for q in ("amount", "same", "kept")}
        if not any(a.values()):
            continue
        t = (k["kind"], k["prompt"], k["pert"], k["pairs"])
        if str(k["repeat"]) == "1" or t in first:
            reps.append((first.get(t), a)); continue
        first[t] = a
    mean = lambda v: (sum(v) / len(v)) if v else None
    rnd = lambda x: "-" if x is None else f"{x:.2f}"
    sel = lambda kind, f: [f(a) for t, a in first.items() if t[0] == kind and f(a) is not None]
    same = lambda a: SC.get(a["same"]); amt = lambda a: MSC.get(a["amount"]); kept = lambda a: KSC.get(a["kept"])
    out = []
    sn = mean(sel("null", same)); ok = sn is not None and sn <= 0.35
    out.append({"test": "Rule 0 null cards called the same", "value": rnd(sn), "verdict": "ok" if ok else "too high: rule 1 not testable"})
    se = mean(sel("edit", same))
    v = "not testable" if not ok or se is None else ("the change repeats across seeds on unseen prompts" if se - sn >= 0.30 else ("does not repeat" if se - sn <= 0.10 else "partly"))
    out.append({"test": "Rule 1 same way: edit cards against null", "value": f"edits {rnd(se)} (n {len(sel('edit', same))}); null {rnd(sn)}", "verdict": v})
    cells = [(t, a) for t, a in first.items() if t[0] == "edit"]
    nk = sum(1 for t, a in cells if (kept(a) or 0) >= 0.67)
    out.append({"test": "Rule 2 subject, colour and style of the prompt kept (all or most) in edit cards", "value": f"{nk} of {len(cells)}",
                "verdict": "the window doses respect the prompt" if nk >= 9 else "the edits override the prompt"})
    nr = sum(1 for r in dino if float(r["ratio_to_seed"]) >= 1.0)
    out.append({"test": "Rule 3 DINOv2: edit moves the picture at least as much as a change of seed, cells", "value": f"{nr} of {len(dino)}",
                "verdict": "supported" if nr >= 9 else "not supported"})
    out.append({"test": "Reported amount: edit / null / seed", "value": " / ".join(rnd(mean(sel(k, amt))) for k in ("edit", "null", "seed")), "verdict": "-"})
    out.append({"test": "Reported kept: edit / null / seed", "value": " / ".join(rnd(mean(sel(k, kept))) for k in ("edit", "null", "seed")), "verdict": "-"})
    out.append({"test": "Reported seed cards same way", "value": rnd(mean(sel("seed", same))), "verdict": "-"})
    out.append({"test": "Reported per cell (same; amount; kept)", "value": "; ".join(f"{t[1]} {t[2]} {a['same']}/{a['amount']}/{a['kept']}" for t, a in sorted(cells)), "verdict": "-"})
    out.append({"test": "Reported DINOv2 per cell (ratio to seed; consistency)", "value": "; ".join(f"{r['prompt']} {r['edit']} {r['ratio_to_seed']}; {r['consistency']}" for r in dino), "verdict": "-"})
    rr = [(a, b) for a, b in reps if a]
    out.append({"test": "Reported test-retest", "value": ", ".join(f"{q} {sum(a[q] == b[q] for a, b in rr)}/{len(rr)}" for q in ("amount", "same", "kept")), "verdict": "-"})
    return out


def selftest():
    rng = random.Random(1); U = unit_specs(rng)
    assert len(U) == 3 * (4 + 2 + 1) and all(len(u["pairs"]) == 8 for u in U)
    assert all(len(set(n for *_, n in u["pairs"])) == 4 for u in U if u["kind"] == "null")
    assert TT.tag("P01", DOSES["P01"]) == "P01_1p75" and TT.tag("E06", DOSES["E06"]) == "E06_0p8"
    assert DOSES["P01"] * 0.3 <= 1.0
    key, lab = {}, []
    for i, u in enumerate(U):
        uid = f"W{i:02d}"; key[uid] = {"kind": u["kind"], "prompt": u["prompt"], "pert": u["pert"], "pairs": " ".join(":".join(x) for x in u["pairs"]), "repeat": "0"}
        e = u["kind"] == "edit"
        lab.append({"unit": uid, "amount": "molto" if e else "qualcosa", "same": "stesso" if e else "diversi", "kept": "tutte" if e else "molte"})
    dino = [{"prompt": p, "edit": n, "ratio_to_seed": 1.5, "consistency": 0.4} for p in SUBJECTS for n in DOSES]
    o = {r["test"]: r["verdict"] for r in rules(lab, key, dino)}
    assert o["Rule 1 same way: edit cards against null"] == "the change repeats across seeds on unseen prompts", o
    assert o["Rule 2 subject, colour and style of the prompt kept (all or most) in edit cards"] == "the window doses respect the prompt", o
    assert o["Rule 3 DINOv2: edit moves the picture at least as much as a change of seed, cells"] == "supported", o
    print("selftest ok;", len(U), "cards (+3 repeats)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "plan", "gate", "count", "analyze", "page", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--queue", action="store_true"); ap.add_argument("--block")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.plan: plan()
    if a.queue: S.queue(a.block)
    if a.gate: S.gate()
    if a.count: S.count()
    if a.analyze: analyze()
    if a.page: page()
    if a.rules:
        out = rules(rd(LABELS), {r["unit"]: r for r in rd(KEY)}, rd(DINO))
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
