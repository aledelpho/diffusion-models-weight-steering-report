"""C75 part A tally (docs/prereg_te_traits.md, amendment 1). Written 2026-10-13, before any C75 label.
Inputs: data/te_traits_key_A.csv, data/te_traits_schedule_A.csv, data/te_traits_questions.csv,
data/te_traits_alessandro.csv (committed as downloaded; block,pos,item,showing,question,answer),
data/te_dose_alessandro.csv (C74 style onsets, as downloaded).
Outputs: data/te_traits_tests.csv, data/te_traits_by_picture.csv.

  python te_traits_tally.py
  python te_traits_tally.py --selftest
  python te_traits_tally.py --part B            # added 2026-10-13 after the part B renders, before its labels:
  python te_traits_tally.py --part B --selftest # B0, B1, B1-skin, repeats; T1-T2 again without fragile traits.
Part B inputs: data/te_traits_key_B.csv, data/te_traits_schedule_B.csv, data/te_traits_B_alessandro.csv, plus the
part A files. Output: data/te_traits_B_tests.csv.
"""
import argparse, csv, statistics
from collections import Counter, defaultdict
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
DOSES = ["0.10", "0.25", "0.40", "0.50", "0.60", "0.70", "0.75", "0.80", "0.85", "0.90", "0.95", "1.00"]
ORDER = {d: i for i, d in enumerate(DOSES, 1)}; ORDER["mai"] = 99
CH = {"D1": "D1_dwarf_paladin", "E2": "E2_elf_rogue", "O4": "O4_halforc_fighter"}
VAL = {"sì": 1, "no": 0, "non so": None}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


def ranks(x):
    s = sorted(range(len(x)), key=lambda i: x[i]); r = [0.0] * len(x); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and x[s[j + 1]] == x[s[i]]:
            j += 1
        for k in range(i, j + 1):
            r[s[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    """Constant y (no loss or no change) -> 0.0: no relation (amendment 1)."""
    if len(x) < 3 or len(set(y)) < 2:
        return 0.0
    rx, ry = ranks(x), ranks(y); mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def kappa(pairs):
    if not pairs:
        return None
    po = sum(a == b for a, b in pairs) / len(pairs)
    c1, c2 = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(c1[k] * c2[k] for k in set(c1) | set(c2)) / len(pairs) ** 2
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def tally(key, sched, questions, labels, c74, exclude=frozenset()):
    traits = {q["id"] for q in questions if q["kind"] in ("asked", "common")}
    ans1, ans2 = {}, {}
    for r in labels:
        (ans1 if str(r["showing"]) == "1" else ans2)[(r["item"], r["question"])] = r["answer"]
    K = {k["item"]: k for k in key}
    per_char = defaultdict(set)
    for s in sched:
        if s["kind"] == "trait" and s["question"] not in exclude:
            per_char[s["char"]].add(s["question"])
    orig = {(k["char"], k["seed"]): k["item"] for k in key if k["dose"] == "0.00"}
    def pres(item, q, a=ans1):
        v = a.get((item, q)); return VAL.get(v) if v is not None else None
    def skin(item, a=ans1):
        s, l, d = a.get((item, "skin_same")), a.get((item, "skin_lighter")), a.get((item, "skin_darker"))
        if s == "sì": return "same"
        if s == "no" and l == "sì": return "lighter"
        if s == "no" and l == "no" and d == "sì": return "darker"
        if s == "no" and l == "no" and d == "no": return "other hue"
        return None
    pic = []
    for k in key:
        it, c = k["item"], k["char"]; o = orig[(c, k["seed"])]
        p0 = [q for q in per_char[c] if pres(o, q) == 1]
        judge0 = [q for q in p0 if pres(it, q) is not None]
        R = sum(pres(it, q) for q in judge0) / len(judge0) if judge0 else None
        jud = [q for q in per_char[c] if pres(it, q) is not None]
        F = sum(pres(it, q) for q in jud) / len(jud) if jud else None
        lost = [q for q in judge0 if pres(it, q) == 0]
        added = [q for q in per_char[c] if pres(o, q) == 0 and pres(it, q) == 1]
        pic.append({**{x: k[x] for x in ("item", "char", "seed", "edit", "dose")}, "R": R, "F": F,
                    "lost": ";".join(sorted(lost)), "added": ";".join(sorted(added)), "skin": skin(it), "person": ans1.get((it, "person"), "")})
    out = []
    strips = defaultdict(dict)
    for p in pic:
        if p["edit"]:
            strips[(p["char"], p["seed"], p["edit"])][p["dose"]] = p["R"]
    # T1
    rhos = {s: spearman([float(d) for d in DOSES if v.get(d) is not None], [v[d] for d in DOSES if v.get(d) is not None]) for s, v in strips.items()}
    med = statistics.median(rhos.values()) if rhos else None
    v1 = "inconclusive (no labels)" if med is None else ("supported" if med <= -0.50 else ("not supported" if med >= -0.20 else "inconclusive"))
    out.append({"test": "T1 retention falls with dose", "value": f"median Spearman over {len(rhos)} strips = {med:.2f}" if med is not None else "", "verdict": v1})
    # T2
    def onset(v):
        best = "mai"
        for d in reversed(DOSES):
            if v.get(d) is None: continue
            if v[d] < 1: best = d
            else: break
        return best
    def t2(slip_fix):
        n = first = later = 0; rows = []
        for r in c74:
            if r["grid"] not in ("dose_L06", "dose_L14"): continue
            ch, s = r["row"].split(" · "); c = [k for k, v in CH.items() if v == ch][0]
            st = r["cambia_da"]
            if slip_fix and r["grid"] == "dose_L06" and ch == CH["O4"] and s == "3316624" and st == "mai": st = "0.80"
            if not st or st == "mai": continue
            on = onset(strips[(c, s, "L" + r["grid"][-2:] + "_mlp")])
            n += 1; first += ORDER[on] < ORDER[st]; later += ORDER[on] > ORDER[st]; rows.append(f"{c}/{s}/{r['grid'][-3:]}: traits {on}, style {st}")
        return n, first, later, rows
    n, a, b, rows = t2(False)
    v2 = ("inconclusive (no labels)" if not n else ("traits go first" if a >= 2 * n / 3 else ("style goes first" if b >= 2 * n / 3 else "inconclusive")))
    out.append({"test": "T2 traits lost before the style changes (L06, L14)", "value": f"traits first {a}, style first {b}, ties or never {n - a - b}, of {n}", "verdict": v2})
    n2, a2, b2, _ = t2(True)
    out.append({"test": "T2 with the C74 slip read as 0.80 (reported)", "value": f"traits first {a2}, style first {b2}, of {n2}", "verdict": ""})
    out.append({"test": "T2 strips (reported)", "value": " | ".join(rows), "verdict": ""})
    # T3
    l28 = [v for (c, s, e), v in strips.items() if e == "L28_mlp"]
    hi = [v["1.00"] for v in l28 if v.get("1.00") is not None]; lo = [v["0.10"] for v in l28 if v.get("0.10") is not None]
    if hi and lo:
        diff = statistics.mean(hi) - statistics.mean(lo)
        v3 = "supported" if diff <= -0.15 else ("not supported" if diff >= -0.05 else "inconclusive")
        out.append({"test": "T3 L28 costs traits without changing style", "value": f"mean R at 1.00 minus at 0.10 = {diff:+.2f}", "verdict": v3})
    else:
        out.append({"test": "T3 L28 costs traits without changing style", "value": "", "verdict": "inconclusive (no labels)"})
    # T4
    ed = [p for p in pic if p["edit"] and p["skin"] in ("lighter", "darker")]
    nl = sum(p["skin"] == "lighter" for p in ed)
    byc = {c: Counter(p["skin"] for p in pic if p["edit"] and p["char"] == c) for c in CH}
    cmaj = sum(byc[c]["lighter"] > byc[c]["darker"] for c in CH)
    if len(ed) < 10:
        v4 = "inconclusive (fewer than 10 changed)"; sh = None
    else:
        sh = nl / len(ed)
        v4 = "toward lighter skin: supported" if sh >= 0.80 and cmaj >= 2 else ("not supported" if sh <= 0.60 else "inconclusive")
    out.append({"test": "T4 unnamed drift toward lighter skin", "value": f"lighter {nl} of {len(ed)} lighter+darker" + (f" = {sh:.2f}" if sh is not None else "") + f"; characters with lighter majority {cmaj}; other hue {sum(p['skin'] == 'other hue' for p in pic if p['edit'])}", "verdict": v4})
    # reliability
    pairs = [(ans1[(it, q)], ans2[(it, q)]) for (it, q) in ans2 if q in traits and (it, q) in ans1 and ans1[(it, q)] in ("sì", "no") and ans2[(it, q)] in ("sì", "no")]
    kp = kappa(pairs)
    out.append({"test": "Reliability gate (Cohen kappa on repeats, traits)", "value": f"kappa {kp:.2f} on {len(pairs)} pairs" if kp is not None else "no pairs",
                "verdict": "" if kp is None else ("passed" if kp >= 0.60 else "failed: no claim from C75 may be stated as holds")})
    sp = [(skin(it), skin(it, ans2)) for it in {i for (i, q) in ans2 if q.startswith("skin")} if skin(it) and skin(it, ans2)]
    pp = [(ans1[(it, "person")], ans2[(it, "person")]) for (it, q) in ans2 if q == "person" and (it, "person") in ans1]
    out.append({"test": "Repeat agreement, skin and person (reported)", "value": f"skin {sum(a == b for a, b in sp)} of {len(sp)}; person {sum(a == b for a, b in pp)} of {len(pp)}", "verdict": ""})
    # reported
    for e in ("L06_mlp", "L14_mlp", "L28_mlp"):
        m = [f"{d}:{statistics.mean([v[d] for (c, s, ee), v in strips.items() if ee == e and v.get(d) is not None]):.2f}" for d in DOSES
             if [v[d] for (c, s, ee), v in strips.items() if ee == e and v.get(d) is not None]]
        out.append({"test": f"mean R by dose, {e} (reported)", "value": " ".join(m), "verdict": ""})
    first_loss = defaultdict(list)
    for (c, s, e), v in strips.items():
        for q in per_char[c]:
            for d in DOSES:
                p = next((x for x in pic if x["char"] == c and x["seed"] == s and x["edit"] == e and x["dose"] == d), None)
                if p and q in p["lost"].split(";"):
                    first_loss[q].append(float(d)); break
    out.append({"test": "lowest dose at which each trait is lost, median over strips (reported)",
                "value": " ".join(f"{q}:{statistics.median(v):.2f}(n{len(v)})" for q, v in sorted(first_loss.items(), key=lambda x: statistics.median(x[1]))), "verdict": ""})
    of = [f"{p['char']}/{p['seed']}:{p['F']:.2f}" for p in pic if p["dose"] == "0.00" and p["F"] is not None]
    out.append({"test": "fidelity of the originals F (reported)", "value": " ".join(of), "verdict": ""})
    pn = Counter((p["edit"], p["person"]) for p in pic if p["edit"])
    out.append({"test": "person = no, by edit (reported)", "value": " ".join(f"{e}:{pn[(e, 'no')]}/{sum(v for (ee, _), v in pn.items() if ee == e)}" for e in ("L06_mlp", "L14_mlp", "L28_mlp")), "verdict": ""})
    return out, pic


def run():
    out, pic = tally(rd(DATA / "te_traits_key_A.csv"), rd(DATA / "te_traits_schedule_A.csv"), rd(DATA / "te_traits_questions.csv"),
                     rd(DATA / "te_traits_alessandro.csv"), rd(DATA / "te_dose_alessandro.csv"))
    with open(DATA / "te_traits_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    with open(DATA / "te_traits_by_picture.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pic[0])); w.writeheader(); w.writerows(pic)
    for o in out: print(o)


def selftest():
    """Synthetic labeller: every trait present up to a strip-specific dose, then the first four traits lost; skin
    lighter after the loss; repeats answered identically. Expected: T1 supported, T2 traits first, T3 supported,
    T4 supported, kappa 1."""
    key, sched, qs = rd(DATA / "te_traits_key_A.csv"), rd(DATA / "te_traits_schedule_A.csv"), rd(DATA / "te_traits_questions.csv")
    K = {k["item"]: k for k in key}
    traits = defaultdict(list)
    for s in sched:
        if s["kind"] == "trait" and s["question"] not in traits[s["char"]]:
            traits[s["char"]].append(s["question"])
    lose_from = {"L06_mlp": 0.60, "L14_mlp": 0.60, "L28_mlp": 0.80}
    labels = []
    for s in sched:
        k = K[s["item"]]; d = float(k["dose"]); lost = bool(k["edit"]) and d >= lose_from[k["edit"]]
        base = dict(block=s["block"], pos=s["pos"], item=s["item"], showing=s["showing"])
        if s["kind"] == "trait":
            a = "no" if lost and s["question"] in sorted(traits[k["char"]])[:4] else "sì"
            labels.append({**base, "question": s["question"], "answer": a})
        elif s["kind"] == "skin":
            labels.append({**base, "question": "skin_same", "answer": "no" if lost else "sì"})
            if lost: labels.append({**base, "question": "skin_lighter", "answer": "sì"})
        else:
            labels.append({**base, "question": "person", "answer": "no" if lost else "sì"})
    c74 = [{"grid": f"dose_L{L}", "row": f"{CH[c]} · {s}", "cambia_da": "0.85"} for L in ("06", "14") for c in CH for s in ("2645751", "3316624")]
    out, _ = tally(key, sched, qs, labels, c74)
    d = {}
    for o in out:
        d.setdefault(o["test"].split(" ")[0], o)
    assert d["T1"]["verdict"] == "supported", d["T1"]
    assert d["T2"]["verdict"] == "traits go first", d["T2"]
    assert d["T3"]["verdict"] == "supported", d["T3"]
    assert d["T4"]["verdict"].startswith("toward lighter"), d["T4"]
    assert d["Reliability"]["verdict"] == "passed", d["Reliability"]
    print("selftest ok")


def _answers(labels):
    a1, a2 = {}, {}
    for r in labels:
        (a1 if str(r["showing"]) == "1" else a2)[(r["item"], r["question"])] = r["answer"]
    return a1, a2


def _skin(a, item):
    s, l, d = a.get((item, "skin_same")), a.get((item, "skin_lighter")), a.get((item, "skin_darker"))
    if s == "sì": return "same"
    if s == "no" and l == "sì": return "lighter"
    if s == "no" and l == "no" and d == "sì": return "darker"
    if s == "no" and l == "no" and d == "no": return "other hue"
    return None


def band(x):
    return "more" if x >= 0.15 else ("size" if -0.05 <= x <= 0.05 else ("less" if x <= -0.15 else "mid"))


def tally_B(keyB, schedB, questions, labB, keyA, schedA, labA, c74):
    out = []
    a1, a2 = _answers(labB); A1, _ = _answers(labA)
    traits = {q["id"] for q in questions if q["kind"] in ("asked", "common")}
    per_char = defaultdict(set)
    for s in schedB:
        if s["kind"] == "trait":
            per_char[s["char"]].add(s["question"])
    def pres(a, it, q):
        v = a.get((it, q)); return VAL.get(v) if v is not None else None
    # B0: presence over 8 seeds (2 originals from part B session + 6 plain; part A originals reported apart)
    rate = {}
    for c in CH:
        plain = [k["item"] for k in keyB if k["char"] == c and k["variant"] in ("original", "plain_B0")]
        for q in sorted(per_char[c]):
            v = [pres(a1, it, q) for it in plain if pres(a1, it, q) is not None]
            rate[q] = (sum(v) / len(v), len(v)) if v else (None, 0)
    fragile = {q for q, (r, n) in rate.items() if r is not None and r < 0.5}
    out.append({"test": "B0 presence of each trait in the unedited model, 8 seeds (reported)",
                "value": " ".join(f"{q}:{r:.2f}(n{n})" for q, (r, n) in sorted(rate.items(), key=lambda x: (x[1][0] is None, x[1][0])) if r is not None),
                "verdict": ""})
    out.append({"test": "B0 fragile at baseline (presence < 0.5)", "value": " ".join(sorted(fragile)) or "none", "verdict": ""})
    # B1: retention against the part B original of the same character and seed
    orig = {(k["char"], k["seed"]): k["item"] for k in keyB if k["variant"] == "original"}
    def R(it, c, s):
        o = orig[(c, s)]
        p0 = [q for q in per_char[c] if pres(a1, o, q) == 1 and pres(a1, it, q) is not None]
        return sum(pres(a1, it, q) for q in p0) / len(p0) if p0 else None
    cells = defaultdict(dict)
    for k in keyB:
        if k["edit"]:
            cells[(k["char"], k["seed"], k["edit"], k["dose"])][k["variant"]] = R(k["item"], k["char"], k["seed"])
    full = {c: v for c, v in cells.items() if all(v.get(x) is not None for x in ("real", "token", "permuted"))}
    if full:
        dp = statistics.mean((v["token"] + v["permuted"]) / 2 - v["real"] for v in full.values())
        dt = statistics.mean(v["token"] - v["real"] for v in full.values())
        dm = statistics.mean(v["permuted"] - v["real"] for v in full.values())
        bt, bm = band(dt), band(dm)
        if bt != bm and "mid" not in (bt, bm):
            vb = "depends on the form of the push"
        else:
            vb = {"more": "the edit costs more traits than its size: supported", "size": "size alone",
                  "less": "random pushes cost more", "mid": "inconclusive"}[band(dp)]
        out.append({"test": "B1 random minus real retention, matched cells", "value": f"pooled {dp:+.2f}; token {dt:+.2f}; permuted {dm:+.2f}; cells {len(full)} of {len(cells)}", "verdict": vb})
        for e in ("L06_mlp", "L14_mlp", "L28_mlp"):
            ve = [v for c, v in full.items() if c[2] == e]
            if ve:
                out.append({"test": f"B1 by edit, {e} (reported)", "value": f"real {statistics.mean(v['real'] for v in ve):.2f}; token {statistics.mean(v['token'] for v in ve):.2f}; permuted {statistics.mean(v['permuted'] for v in ve):.2f}", "verdict": ""})
    else:
        out.append({"test": "B1 random minus real retention, matched cells", "value": "", "verdict": "inconclusive (no labels)"})
    sk = Counter((k["variant"], _skin(a1, k["item"])) for k in keyB if k["edit"])
    out.append({"test": "B1-skin share lighter among lighter + darker (reported)",
                "value": " ".join(f"{v}: {sk[(v, 'lighter')]}/{sk[(v, 'lighter')] + sk[(v, 'darker')]} (other hue {sk[(v, 'other hue')]})" for v in ("real", "token", "permuted")), "verdict": ""})
    pairs = [(a1[(it, q)], a2[(it, q)]) for (it, q) in a2 if q in traits and (it, q) in a1 and a1[(it, q)] in ("sì", "no") and a2[(it, q)] in ("sì", "no")]
    kp = kappa(pairs)
    out.append({"test": "Reliability, part B repeats (Cohen kappa, traits)", "value": f"kappa {kp:.2f} on {len(pairs)} pairs" if kp is not None else "no pairs",
                "verdict": "" if kp is None else ("passed" if kp >= 0.60 else "failed: no claim from B may be stated as holds")})
    # same pictures labelled in both sessions (originals, real edits at 0.70 / 0.85 / 1.00): cross-session agreement
    fileA = {k["file"]: k["item"] for k in keyA}
    cross = [(A1[(fileA[k["file"]], q)], a1[(k["item"], q)]) for k in keyB if k["file"] in fileA for q in per_char[k["char"]]
             if (fileA[k["file"]], q) in A1 and (k["item"], q) in a1 and A1[(fileA[k["file"]], q)] in ("sì", "no") and a1[(k["item"], q)] in ("sì", "no")]
    kc = kappa(cross)
    out.append({"test": "Agreement across sessions, same pictures (reported)", "value": f"kappa {kc:.2f} on {len(cross)} pairs" if kc is not None else "no pairs", "verdict": ""})
    # T1, T2 of part A without the fragile traits
    if labA and fragile:
        o2, _ = tally(keyA, schedA, questions, labA, c74, exclude=frozenset(fragile))
        for o in o2:
            if o["test"].startswith(("T1", "T2 traits")):
                out.append({"test": o["test"] + " - without fragile traits (reported)", "value": o["value"], "verdict": o["verdict"]})
    return out


def run_B():
    labA = rd(DATA / "te_traits_alessandro.csv") if (DATA / "te_traits_alessandro.csv").exists() else []
    out = tally_B(rd(DATA / "te_traits_key_B.csv"), rd(DATA / "te_traits_schedule_B.csv"), rd(DATA / "te_traits_questions.csv"),
                  rd(DATA / "te_traits_B_alessandro.csv"), rd(DATA / "te_traits_key_A.csv"), rd(DATA / "te_traits_schedule_A.csv"),
                  labA, rd(DATA / "te_dose_alessandro.csv"))
    with open(DATA / "te_traits_B_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    for o in out: print(o)


def selftest_B():
    """Synthetic labeller for part B: the real edit loses the first four traits at every dose, random pushes lose
    none; o_tusks absent in every plain picture. Expected: B1 'edit costs more', o_tusks fragile, kappa 1."""
    keyB, schedB, qs = rd(DATA / "te_traits_key_B.csv"), rd(DATA / "te_traits_schedule_B.csv"), rd(DATA / "te_traits_questions.csv")
    K = {k["item"]: k for k in keyB}
    traits = defaultdict(list)
    for s in schedB:
        if s["kind"] == "trait" and s["question"] not in traits[s["char"]]:
            traits[s["char"]].append(s["question"])
    lab = []
    for s in schedB:
        k = K[s["item"]]; base = dict(block=s["block"], pos=s["pos"], item=s["item"], showing=s["showing"])
        if s["kind"] == "trait":
            a = "no" if (k["variant"] == "real" and s["question"] in sorted(traits[k["char"]])[:4]) or (s["question"] == "o_tusks" and not k["edit"]) else "sì"
            lab.append({**base, "question": s["question"], "answer": a})
        elif s["kind"] == "skin":
            lab.append({**base, "question": "skin_same", "answer": "no" if k["variant"] == "real" else "sì"})
            if k["variant"] == "real": lab.append({**base, "question": "skin_lighter", "answer": "sì"})
        else:
            lab.append({**base, "question": "person", "answer": "sì"})
    out = tally_B(keyB, schedB, qs, lab, rd(DATA / "te_traits_key_A.csv"), rd(DATA / "te_traits_schedule_A.csv"), [], [])
    d = {}
    for o in out:
        d.setdefault(o["test"].split(",")[0], o)
    assert d["B1 random minus real retention"]["verdict"].startswith("the edit costs more"), d["B1 random minus real retention"]
    assert "o_tusks" in d["B0 fragile at baseline (presence < 0.5)"]["value"]
    assert d["Reliability"]["verdict"] == "passed"
    print("selftest B ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--part", default="A")
    a = ap.parse_args()
    if a.part == "B":
        selftest_B() if a.selftest else run_B()
    else:
        selftest() if a.selftest else run()
