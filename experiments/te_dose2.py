"""C113 - does a stronger push let the edit's direction dominate the seed? Dose ladders of four text-encoder edits on two
C112 prompts (docs/prereg_te_dose2.md). Written 2026-10-28 with the pre-registration, before any encode or render.
Level 1 of every ladder is C112's dose: those renders and the plain pictures are reused from benchmark_te_settings
(same seeds, same pipeline; a gate checks the plain picture is reproduced pixel for pixel).

  python te_dose2.py --selftest
  python te_dose2.py --plan            # GPU: conditionings -> data/te_dose2_plan.csv
  python te_dose2.py --queue --block gate | main
  python te_dose2.py --gate            # the plain picture re-rendered here = C112's, 2 prompts
  python te_dose2.py --count
  python te_dose2.py --analyze         # GPU: DINOv2 -> data/te_dose2_dino.csv
  python te_dose2.py --page            # blind page Text2Img/occhio_C113.html (after --analyze)
  python te_dose2.py --rules           # once data/te_dose2_labels.csv exists
"""
import argparse, csv, itertools, os, random, statistics, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_tree as TT
import te_depth_control as T

DATA = HERE.parent / "data"
PLAN, DINO = DATA / "te_dose2_plan.csv", DATA / "te_dose2_dino.csv"
KEY, LABELS, TESTS = DATA / "te_dose2_key.csv", DATA / "te_dose2_labels.csv", DATA / "te_dose2_tests.csv"
FOLDER, PREV = "benchmark_te_dose2", "benchmark_te_settings"
PROMPTS = {"S1_bluetree": "A curved tree with large blue leaves",
           "S3_evilhelmet": "Cartoon evil helmet with black metal and a big red gemstone"}
SUBJECTS = list(PROMPTS)
LADDERS = {"E06": [0.4, 0.8, 1.2, 1.6], "E14": [0.4, 0.8, 1.2, 1.6],
           "E28": [1.06066, 1.59099, 2.12132, 2.65165], "P01": [0.7071, 1.41421, 2.12132, 2.82843]}
SEEDS = TT.TEST_SEEDS
TT.FOLDER, TT.TX, TT.SUBJECTS = FOLDER, PROMPTS, SUBJECTS
TT.PERTS = {"E06": ("edit", 6), "E14": ("edit", 14), "E28": ("edit", 28), "P01": ("preset", None)}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def tag(n, lvl):
    return TT.tag(n, LADDERS[n][lvl])


def path(p, cond, s):
    """Level 1 and plain come from C112's folder; levels 2-4 and the gate from this one."""
    new = cond == "GATE" or any(cond == tag(n, l) for n in LADDERS for l in (1, 2, 3))
    return T.img_root() / (FOLDER if new else PREV) / TT.fname(p, "C0" if cond == "GATE" else cond, s)


def plan():
    (T.img_root() / FOLDER / "conds").mkdir(parents=True, exist_ok=True)
    E = TT.Enc(); rows = []
    for p in SUBJECTS:
        E.save(p, "C0", 0); rows.append(TT.row("gate", p, SEEDS[0], "C0"))
    for p in SUBJECTS:
        for n, xs in LADDERS.items():
            for x in xs[1:]:
                t = E.save(p, n, x)
                if t is None:
                    print("NONFINITE", p, n, x); continue
                for s in SEEDS:
                    rows.append(TT.row("main", p, s, t))
    TT.write(PLAN, rows); print("plan rows:", len(rows), "(194 expected)")


def queue(block):
    n = 0
    for r in rd(PLAN):
        if r["block"] != block or (T.img_root() / FOLDER / r["expected_filename"]).exists():
            continue
        TT.post(r); n += 1
    print("queued", n)


def gate():
    from PIL import Image
    ok = True
    for p in SUBJECTS:
        a, b = path(p, "GATE", SEEDS[0]), path(p, "C0", SEEDS[0])
        if not (a.exists() and b.exists()):
            print("missing", p); ok = False; continue
        d = int(np.abs(np.asarray(Image.open(a).convert("RGB"), dtype=np.int16) - np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)).max())
        print(f"{p}: re-rendered plain vs C112 plain, max abs diff {d}"); ok &= d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN); miss = [r["expected_filename"] for r in rows if not (T.img_root() / FOLDER / r["expected_filename"]).exists()]
    lvl1 = [path(p, tag(n, 0), s) for p in SUBJECTS for n in LADDERS for s in SEEDS] + [path(p, "C0", s) for p in SUBJECTS for s in SEEDS]
    print("expected", len(rows), "missing", len(miss), miss[:3], "| reused from C112:", len(lvl1), "missing", sum(not f.exists() for f in lvl1))


cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def dino_rows(V):
    out = []
    for p in SUBJECTS:
        plain = statistics.median(1 - cos(V[(p, a, "C0")], V[(p, b, "C0")]) for a, b in itertools.combinations(SEEDS, 2))
        for n in LADDERS:
            for l in range(4):
                c = tag(n, l)
                U = {s: V[(p, s, c)] - V[(p, s, "C0")] for s in SEEDS}
                D = statistics.median(1 - cos(V[(p, s, c)], V[(p, s, "C0")]) for s in SEEDS)
                out.append({"prompt": p, "edit": n, "level": l + 1, "dose": LADDERS[n][l], "median_D_from_plain": round(D, 4),
                            "plain_seed_D": round(plain, 4), "ratio_to_seed": round(D / plain, 3),
                            "consistency": round(statistics.mean(cos(U[a], U[b]) for a, b in itertools.combinations(SEEDS, 2)), 4)})
    return out


def analyze():
    from PIL import Image
    import metric_validation as MV
    m = MV.Models(vqa=False); V = {}
    for p in SUBJECTS:
        for s in SEEDS:
            for c in ["C0"] + [tag(n, l) for n in LADDERS for l in range(4)]:
                V[(p, s, c)] = np.asarray(m.dino_vec(Image.open(path(p, c, s)).convert("RGB")), dtype=np.float64)
    out = dino_rows(V)
    with open(DINO, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    for o in out:
        print(o)


# ---------------------------------------------------------------- blind
# amendment 1 (2026-10-28, before any label): how far the pictures went, instead of how many are broken
DRIFT = [("niente", "per niente: è ancora ciò che il prompt chiede"), ("poco", "poco: qualche dettaglio fuori posto"),
         ("tanto", "molto: si riconosce a fatica"), ("tutto", "del tutto: non è più ciò che il prompt chiede, o è rotta")]
QS = [("amount", "1. Confronta la riga DOPO con la riga PRIMA: quanto sono cambiate le immagini?",
       [("molto", "molto"), ("qualcosa", "un po'"), ("poco", "quasi niente"), ("niente", "niente")]),
      ("same", "2. Le immagini della riga DOPO sono cambiate tutte nello stesso modo? (negli appunti: che cosa è cambiato)",
       [("stesso", "sì, tutte"), ("simile", "la maggior parte"), ("diversi", "no, ognuna a modo suo"), ("nonsivede", "non è cambiato nulla")]),
      ("drift", "3. Quanto si sono allontanate dal prompt le immagini DOPO, nell'insieme?", DRIFT)]
SC, MSC = TT.SC, TT.MSC
OKB = ("niente", "poco")


def unit_specs(rng):
    U, conds = [], [(n, l) for n in LADDERS for l in range(4)]
    for p in SUBJECTS:
        for n, l in conds:
            U.append({"kind": "edit", "prompt": p, "edit": n, "level": l + 1, "pairs": [(s, "C0", s, tag(n, l)) for s in SEEDS]})
        for _ in range(2):
            pick = rng.sample(conds, 8)
            U.append({"kind": "null", "prompt": p, "edit": "mixed", "level": 0, "pairs": [(s, "C0", s, tag(n, l)) for s, (n, l) in zip(SEEDS, pick)]})
        for sh in (4, 3):
            U.append({"kind": "seed", "prompt": p, "edit": "seed", "level": 0, "pairs": [(s, "C0", SEEDS[(i + sh) % 8], "C0") for i, s in enumerate(SEEDS)]})
    return U


def page():
    from eye_grid_page import thumb, build
    root = str(T.img_root()); rng = random.Random(11313)
    U = unit_specs(rng); rng.shuffle(U)
    reps = rng.sample([i for i, u in enumerate(U) if u["kind"] == "edit"], 4); order = list(range(len(U)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 10, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for k_, i in enumerate(order, 1):
        u = U[i]; uid = f"V{k_:02d}"
        key.append({"unit": uid, "kind": u["kind"], "prompt": u["prompt"], "edit": u["edit"], "level": u["level"],
                    "pairs": " ".join(":".join(x) for x in u["pairs"]), "repeat": int(i in seen)}); seen.add(i)
        top, bot = [], []
        for s, c0, s2, c in u["pairs"]:
            a = thumb(str(path(u["prompt"], c0, s)), root); b = thumb(str(path(u["prompt"], c, s2)), root)
            top.append({"t": a[0], "f": a[1]}); bot.append({"t": b[0], "f": b[1]})
        units.append({"id": uid, "title": f"Scheda {k_:02d}", "groups": [{"id": "g", "name": "", "cols": [str(c) for c in range(1, 9)],
                      "rows": [{"label": "PRIMA", "cells": top}, {"label": "DOPO", "cells": bot}]}]})
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_C113.html"), "C113 · più dose, più coerenza?", units, QS, QS[1][2], "c113_labels_v2", "te_dose2_labels.csv")
    print("cards", len(units), "->", os.path.join(root, "occhio_C113.html"))


def rules(labels, key, dino=None):
    first, reps = {}, []
    for r in labels:
        k = key.get(r["unit"])
        if not k:
            continue
        a = {q: (r.get(q) or "").strip() for q in ("amount", "same", "drift")}
        if not any(a.values()):
            continue
        t = (k["kind"], k["prompt"], k["edit"], str(k["level"]), k["pairs"])
        if str(k["repeat"]) == "1" or t in first:
            reps.append((first.get(t), a)); continue
        first[t] = a
    get = lambda p, n, l: next((a for t, a in first.items() if t[0] == "edit" and t[1] == p and t[2] == n and t[3] == str(l)), None)
    mean = lambda v: (sum(v) / len(v)) if v else None
    rnd = lambda x: "-" if x is None else f"{x:.2f}"
    out = []
    sn = mean([SC[a["same"]] for t, a in first.items() if t[0] == "null" and a["same"] in SC]); ok = sn is not None and sn <= 0.35
    out.append({"test": "Rule 0 null cards called the same", "value": rnd(sn), "verdict": "ok" if ok else "too high: pass not valid"})
    seed_amt = {p: mean([MSC[a["amount"]] for t, a in first.items() if t[0] == "seed" and t[1] == p and a["amount"] in MSC]) for p in SUBJECTS}
    D = {(r["prompt"], r["edit"], int(r["level"])): float(r["consistency"]) for r in (dino or [])}
    rise = dom = drise = cells = 0; detail = []
    for p in SUBJECTS:
        for n in LADDERS:
            labs = [get(p, n, l) for l in range(1, 5)]
            okl = [l for l in range(2, 5) if labs[l - 1] and labs[l - 1]["drift"] in OKB]
            top = max(okl) if okl else None
            cells += 1
            s1 = SC.get((labs[0] or {}).get("same"), 0.0) if labs[0] else None
            st = SC.get(labs[top - 1]["same"], 0.0) if top else None
            r1 = top is not None and s1 is not None and st - s1 >= 0.5
            at = MSC.get(labs[top - 1]["amount"]) if top else None
            r2 = top is not None and at is not None and seed_amt[p] is not None and at >= seed_amt[p]
            r3 = top is not None and (p, n, top) in D and D[(p, n, top)] - D[(p, n, 1)] >= 0.10
            rise += r1; dom += r2; drise += r3
            brk = next((l for l in range(1, 5) if labs[l - 1] and labs[l - 1]["drift"] not in OKB), None)
            detail.append(f"{p} {n}: top unbroken level {top or '-'}, same {rnd(s1)} -> {rnd(st)}, amount {rnd(at)} vs seed {rnd(seed_amt[p])}, first drifted level {brk or '-'}, drift by level " + "/".join((l or {}).get("drift", "-") or "-" for l in labs))
    ver = lambda k: "supported" if k >= 5 else "not supported"
    out.append({"test": "Rule 1 same way rises from level 1 to the highest unbroken level (>= 0.5), cells", "value": f"{rise} of {cells}", "verdict": ver(rise) if ok else "not testable"})
    out.append({"test": "Rule 2 at the highest unbroken level the edit changes as much as a change of seed, cells", "value": f"{dom} of {cells}", "verdict": ver(dom)})
    out.append({"test": "Rule 3 DINOv2 consistency rises by >= 0.10 to the highest unbroken level, cells", "value": f"{drise} of {cells}", "verdict": ver(drise) if dino else "not computed"})
    out.append({"test": "Reported per cell", "value": "; ".join(detail), "verdict": "-"})
    rr = [(a, b) for a, b in reps if a]
    out.append({"test": "Reported test-retest", "value": ", ".join(f"{q} {sum(a[q] == b[q] for a, b in rr)}/{len(rr)}" for q in ("amount", "same", "drift")), "verdict": "-"})
    return out


def selftest():
    rng = random.Random(1); U = unit_specs(rng)
    assert len(U) == 2 * (16 + 2 + 2) and all(len(u["pairs"]) == 8 for u in U)
    assert tag("E28", 0) == "E28_1p06066" and tag("P01", 0) == "P01_0p7071" and tag("E06", 0) == "E06_0p4"
    assert all(x * 0.3 <= 1.0 for x in LADDERS["P01"])
    key, lab, dino = {}, [], []
    for i, u in enumerate(U):
        uid = f"V{i:02d}"; key[uid] = {"kind": u["kind"], "prompt": u["prompt"], "edit": u["edit"], "level": u["level"], "pairs": " ".join(":".join(x) for x in u["pairs"]), "repeat": "0"}
        if u["kind"] == "edit":
            l = u["level"]
            lab.append({"unit": uid, "amount": ["poco", "qualcosa", "molto", "molto"][l - 1], "same": ["diversi", "simile", "stesso", "stesso"][l - 1], "drift": "tutto" if l == 4 else "niente"})
        else:
            lab.append({"unit": uid, "amount": "molto" if u["kind"] == "seed" else "qualcosa", "same": "diversi", "drift": "niente"})
    for p in SUBJECTS:
        for n in LADDERS:
            for l in range(1, 5):
                dino.append({"prompt": p, "edit": n, "level": l, "consistency": 0.05 * l})
    o = {r["test"]: r for r in rules(lab, key, dino)}
    assert o["Rule 1 same way rises from level 1 to the highest unbroken level (>= 0.5), cells"]["value"] == "8 of 8", o
    assert o["Rule 2 at the highest unbroken level the edit changes as much as a change of seed, cells"]["value"] == "8 of 8", o
    assert o["Rule 3 DINOv2 consistency rises by >= 0.10 to the highest unbroken level, cells"]["value"] == "8 of 8", o
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
        out = rules(rd(LABELS), {r["unit"]: r for r in rd(KEY)}, rd(DINO) if DINO.exists() else None)
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
