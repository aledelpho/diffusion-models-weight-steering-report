"""C79 tally (docs/prereg_te_tap_isolation.md, section C and decision rules 1-3; amendment 1).
Written 2026-10-18 after Alessandro's labels were committed as downloaded (data/te_tap_alessandro.csv) and before
any count. Retention R is computed exactly as in C75 (experiments/te_traits_tally.py): for each picture, the share
of the traits present in the same-seed baseline that the picture still shows; "non so" answers are left out.

Inputs: data/te_tap_key.csv, data/te_tap_schedule.csv, data/te_tap_alessandro.csv, data/te_tap_isolation_cells.csv.
Outputs: data/te_tap_tests.csv, data/te_tap_by_picture.csv.

  python te_tap_isolation_tally.py
  python te_tap_isolation_tally.py --selftest
"""
import argparse, csv, statistics
from collections import Counter, defaultdict
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
VAL = {"sì": 1, "no": 0, "non so": None}
EDITS = ["L06_mlp_p1.00", "L14_mlp_p1.00"]
CONDS = ["taps_local", "taps_early_mid", "taps_late", "full"]


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


def kappa(pairs):
    if not pairs:
        return None
    po = sum(a == b for a, b in pairs) / len(pairs)
    c1, c2 = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(c1[k] * c2[k] for k in set(c1) | set(c2)) / len(pairs) ** 2
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def answers(labels):
    a1, a2 = {}, {}
    for r in labels:
        (a1 if str(r["showing"]) == "1" else a2)[(r["item"], r["question"])] = r["answer"]
    return a1, a2


def skin(a, item):
    s, l, d = a.get((item, "skin_same")), a.get((item, "skin_lighter")), a.get((item, "skin_darker"))
    if s == "sì": return "same"
    if s == "no" and l == "sì": return "lighter"
    if s == "no" and l == "no" and d == "sì": return "darker"
    if s == "no" and l == "no" and d == "no": return "other hue"
    return None


def mean(x):
    x = [v for v in x if v is not None]
    return statistics.mean(x) if x else None


def f2(x):
    return "n/a" if x is None else f"{x:.2f}"


def tally(key, sched, labels, cells):
    a1, a2 = answers(labels)
    per_char = defaultdict(set)
    for s in sched:
        if s["kind"] == "trait":
            per_char[s["char"]].add(s["question"])
    base = {(k["char"], k["seed"]): k["item"] for k in key if k["cond"] == "baseline"}
    def pres(it, q, a=a1):
        v = a.get((it, q)); return VAL.get(v) if v is not None else None
    pic = []
    for k in key:
        it, c = k["item"], k["char"]; o = base[(c, k["seed"])]
        p0 = [q for q in per_char[c] if pres(o, q) == 1]
        j = [q for q in p0 if pres(it, q) is not None]
        R = sum(pres(it, q) for q in j) / len(j) if j else None
        lost = [q for q in j if pres(it, q) == 0]
        added = [q for q in per_char[c] if pres(o, q) == 0 and pres(it, q) == 1]
        pic.append({**{x: k[x] for x in ("item", "char", "seed", "edit", "cond")}, "R": R, "n_base_traits": len(j),
                    "lost": ";".join(sorted(lost)), "added": ";".join(sorted(added)),
                    "skin": skin(a1, it) if k["cond"] != "baseline" else "", "person": a1.get((it, "person"), "")})
    out = []
    def dR(cond, edit=None, char=None):
        m = mean([p["R"] for p in pic if p["cond"] == cond and (edit is None or p["edit"] == edit) and (char is None or p["char"] == char)])
        return None if m is None else 1 - m
    # rule 1 (primary)
    em, la = dR("taps_early_mid"), dR("taps_late")
    pairs = [(c, e) for c in sorted(per_char) for e in EDITS]
    em_more = sum(dR("taps_early_mid", e, c) > dR("taps_late", e, c) for c, e in pairs)
    la_more = sum(dR("taps_late", e, c) > dR("taps_early_mid", e, c) for c, e in pairs)
    d = em - la
    if d >= 0.15 and em_more >= 5: v1 = "H2 supported (early/mid taps drive the trait loss)"
    elif -d >= 0.15 and la_more >= 5: v1 = "H1 supported (late-tap cascade drives the trait loss)"
    elif abs(d) < 0.15 and ((em >= 0.10 and la >= 0.10) or (em < 0.15 and la < 0.15)): v1 = "joint / distributed"
    else: v1 = "inconclusive (no branch of rule 1 met)"
    out.append({"test": "Rule 1 primary: trait loss, early/mid taps vs late taps",
                "value": f"dR early_mid {em:.2f}, dR late {la:.2f}, difference {d:+.2f}; early_mid loses more in {em_more}/6 pairs, late in {la_more}/6",
                "verdict": v1})
    out.append({"test": "Rule 1 pairs (reported)", "value": " | ".join(
        f"{c}/{e[:3]}: em {dR('taps_early_mid', e, c):.2f} late {dR('taps_late', e, c):.2f} local {dR('taps_local', e, c):.2f}" for c, e in pairs), "verdict": ""})
    # rule 2 (secondary), per edit (amendment 1)
    for e in EDITS:
        lo, emx = dR("taps_local", e), dR("taps_early_mid", e)
        if emx is None or emx <= 0:
            out.append({"test": f"Rule 2 local sufficiency, {e[:3]}", "value": f"dR local {f2(lo)}, dR early_mid {f2(emx)}", "verdict": "not defined (early_mid causes no loss)"}); continue
        r = lo / emx
        v = "local taps sufficient" if r >= 0.70 else ("needs accumulation across intermediate taps" if r <= 0.30 else "in between")
        out.append({"test": f"Rule 2 local sufficiency, {e[:3]}" + (" (local = one tap, amendment 1)" if e.startswith("L14") else ""),
                    "value": f"dR local {lo:.2f} / dR early_mid {emx:.2f} = {r:.2f}", "verdict": v})
    # rule 3, automatic distances
    for m in ("dinov2", "csd"):
        dl = [float(c[f"delta_early_late_{m}"]) for c in cells if c[f"delta_early_late_{m}"] != ""]
        pi = [float(c[f"pi_early_late_{m}"]) for c in cells if c.get(f"pi_early_late_{m}", "") not in ("", "nan")]
        pos, neg = sum(x > 0 for x in dl), sum(x < 0 for x in dl)
        ppos, pneg = sum(x > 0 for x in pi), sum(x < 0 for x in pi)
        v = ("early/mid farther from baseline" if pos >= 18 else ("late farther from baseline" if neg >= 18 else "no unidirectional verdict"))
        out.append({"test": f"Rule 3 automatic, {m}", "value": f"Delta early-late > 0 in {pos}/{len(dl)} cells (< 0 in {neg}); Pi > 0 in {ppos}/{len(pi)} cells (< 0 in {pneg})", "verdict": v})
    # reported: mean R by condition and edit, skin, person
    for e in EDITS:
        out.append({"test": f"mean R by condition, {e[:3]} (reported)", "value": " ".join(f"{c}:{f2(mean([p['R'] for p in pic if p['cond'] == c and p['edit'] == e]))}" for c in CONDS), "verdict": ""})
    for e in EDITS:
        sk = {c: Counter(p["skin"] for p in pic if p["cond"] == c and p["edit"] == e) for c in CONDS}
        out.append({"test": f"skin vs same-seed baseline, {e[:3]} (reported)", "value": " | ".join(
            f"{c}: lighter {sk[c]['lighter']} darker {sk[c]['darker']} other {sk[c]['other hue']} same {sk[c]['same']}" for c in CONDS), "verdict": ""})
        pn = {c: Counter(p["person"] for p in pic if p["cond"] == c and p["edit"] == e) for c in CONDS}
        out.append({"test": f"same person = no, {e[:3]} (reported)", "value": " ".join(f"{c}:{pn[c]['no']}/{sum(pn[c].values())}" for c in CONDS), "verdict": ""})
    out.append({"test": "baseline vs itself, person and skin (sanity, reported)", "value":
                f"person sì {sum(p['person'] == 'sì' for p in pic if p['cond'] == 'baseline')}/{sum(p['cond'] == 'baseline' for p in pic)}; skin same "
                f"{sum(skin(a1, p['item']) == 'same' for p in pic if p['cond'] == 'baseline')}", "verdict": ""})
    # reliability (C75 gate: kappa >= 0.60)
    traits = set().union(*per_char.values())
    rp = [(a1[k], a2[k]) for k in a2 if k[1] in traits and k in a1 and a1[k] in ("sì", "no") and a2[k] in ("sì", "no")]
    kp = kappa(rp)
    out.append({"test": "Reliability gate (Cohen kappa on repeats, traits; C75 threshold 0.60)",
                "value": f"kappa {kp:.2f} on {len(rp)} pairs, raw agreement {sum(a == b for a, b in rp)}/{len(rp)}" if kp is not None else "no pairs",
                "verdict": "" if kp is None else ("passed" if kp >= 0.60 else "failed: no claim from C79 labels may be stated as holds")})
    rep = {k[0] for k in a2}
    sp = [(skin(a1, it), skin(a2, it)) for it in rep if skin(a1, it) and skin(a2, it)]
    pp = [(a1.get((it, "person")), a2.get((it, "person"))) for it in rep if (it, "person") in a2]
    out.append({"test": "Repeat agreement, skin and person (reported)", "value": f"skin {sum(a == b for a, b in sp)} of {len(sp)}; person {sum(a == b for a, b in pp)} of {len(pp)}", "verdict": ""})
    lost = Counter(q for p in pic if p["cond"] in ("taps_early_mid", "taps_late") for q in p["lost"].split(";") if q)
    out.append({"test": "traits lost most often in early_mid + late (reported)", "value": " ".join(f"{q}:{n}" for q, n in lost.most_common(8)), "verdict": ""})
    return out, pic


def run():
    out, pic = tally(rd(DATA / "te_tap_key.csv"), rd(DATA / "te_tap_schedule.csv"), rd(DATA / "te_tap_alessandro.csv"),
                     rd(DATA / "te_tap_isolation_cells.csv"))
    with open(DATA / "te_tap_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    with open(DATA / "te_tap_by_picture.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pic[0])); w.writeheader(); w.writerows(pic)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


def selftest():
    """Synthetic labeller: early_mid and full lose the first three traits, late and local lose none; skin lighter
    where traits are lost; repeats identical. Expected: rule 1 H2, rule 2 'needs accumulation', kappa passed."""
    key, sched = rd(DATA / "te_tap_key.csv"), rd(DATA / "te_tap_schedule.csv")
    K = {k["item"]: k for k in key}
    traits = defaultdict(list)
    for s in sched:
        if s["kind"] == "trait" and s["question"] not in traits[s["char"]]:
            traits[s["char"]].append(s["question"])
    labels = []
    for s in sched:
        k = K[s["item"]]; lost = k["cond"] in ("taps_early_mid", "full")
        b = dict(block=s["block"], pos=s["pos"], item=s["item"], showing=s["showing"])
        if s["kind"] == "trait":
            labels.append({**b, "question": s["question"], "answer": "no" if lost and s["question"] in sorted(traits[k["char"]])[:3] else "sì"})
        elif s["kind"] == "skin":
            labels.append({**b, "question": "skin_same", "answer": "no" if lost else "sì"})
            if lost: labels.append({**b, "question": "skin_lighter", "answer": "sì"})
        else:
            labels.append({**b, "question": "person", "answer": "no" if lost else "sì"})
    out, _ = tally(key, sched, labels, rd(DATA / "te_tap_isolation_cells.csv"))
    d = {o["test"]: o for o in out}
    assert d["Rule 1 primary: trait loss, early/mid taps vs late taps"]["verdict"].startswith("H2"), d
    assert d["Rule 2 local sufficiency, L06"]["verdict"].startswith("needs"), d
    assert next(o for o in out if o["test"].startswith("Reliability"))["verdict"] == "passed"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    selftest() if ap.parse_args().selftest else run()
