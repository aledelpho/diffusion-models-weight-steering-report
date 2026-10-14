"""C76 tally (docs/prereg_te_bind.md). Written 2026-10-14, before any C76 label.
Inputs: data/te_bind_key.csv, data/te_bind_schedule.csv, data/te_bind_questions.csv, data/te_bind_rater.csv
(committed as downloaded; block,pos,item,showing,question,answer); for the reported overlap, data/te_traits_key_A.csv
and data/te_traits_alessandro.csv. Output: data/te_bind_tests.csv.

  python te_bind_tally.py
  python te_bind_tally.py --selftest
"""
import argparse, csv
from collections import defaultdict
from pathlib import Path
from te_traits_tally import kappa, rd, _answers
DATA = Path(__file__).resolve().parent.parent / "data"
OVERLAP = {"copper": "d_copper", "amber": "e_amber", "green": "e_cowl", "burgundy": "o_jack"}


def band(d):
    d = float(d)
    return "<=0.50" if d <= 0.50 else ("0.60-0.80" if d <= 0.80 else ">=0.85")


def rate(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs), len(xs)) if xs else (None, 0)


def tally(key, questions, labels, keyA=None, labA=None):
    a1, a2 = _answers(labels)
    words = defaultdict(str)
    for q in questions:
        words[q["word"]] = q["char"]
    yn = lambda v: {"sì": 1, "no": 0}.get(v)
    orig = {(k["char"], k["seed"]): k["item"] for k in key if k["variant"] == "original"}
    cases = []   # one row per picture x word
    for k in key:
        for w, c in words.items():
            if k["char"] != c:
                continue
            on, off = yn(a1.get((k["item"], f"{w}_on"))), yn(a1.get((k["item"], f"{w}_off")))
            o = orig.get((c, k["seed"]))
            o_on = yn(a1.get((o, f"{w}_on"))) if o else None
            state = ""
            if k["variant"] == "real" and o_on == 1 and on is not None:
                state = "lost" if on == 0 else "kept"
            cases.append({**k, "word": w, "on": on, "off": off, "state": state})
    out = []
    lost = [c["off"] for c in cases if c["state"] == "lost"]
    kept = [c["off"] for c in cases if c["state"] == "kept"]
    plain = [c["off"] for c in cases if c["variant"] in ("original", "plain_B0")]
    (Ll, nl), (Lk, nk), (L0, n0) = rate(lost), rate(kept), rate(plain)
    if nl < 10 or Ll is None:
        v1 = "inconclusive (fewer than 10 lost cases)"
    else:
        ref = max(x for x in (Lk, L0) if x is not None)
        v1 = ("the colour moves (links break)" if Ll >= 0.30 and Ll - ref >= 0.20 else
              ("the colour vanishes (defaults win)" if Ll <= ref + 0.05 else "inconclusive"))
    f = lambda x: "" if x is None else f"{x:.2f}"
    out.append({"test": "M1 off-target rate when the colour is lost (real edits)",
                "value": f"L_lost {f(Ll)} (n {nl}); L_kept {f(Lk)} (n {nk}); L_0 {f(L0)} (n {n0})", "verdict": v1})
    rand_cells = {(c["char"], c["seed"], c["edit"], c["dose"]) for c in cases if c["variant"] in ("token", "permuted")}
    real_m = [c["off"] for c in cases if c["variant"] == "real" and (c["char"], c["seed"], c["edit"], c["dose"]) in rand_cells]
    rand_m = [c["off"] for c in cases if c["variant"] in ("token", "permuted")]
    (Rr, nr), (Rn, nn) = rate(real_m), rate(rand_m)
    if Rr is None or Rn is None:
        v2 = "inconclusive (no labels)"
    else:
        d = Rr - Rn
        v2 = ("edits misplace more" if d >= 0.15 else ("no difference" if abs(d) <= 0.05 else ("random pushes misplace more" if d <= -0.15 else "inconclusive")))
    out.append({"test": "M2 off-target rate, real edits minus random pushes, matched cells",
                "value": f"real {f(Rr)} (n {nr}); random {f(Rn)} (n {nn})", "verdict": v2})
    pairs = [(a1[(i, q)], a2[(i, q)]) for (i, q) in a2 if (i, q) in a1 and a1[(i, q)] in ("sì", "no") and a2[(i, q)] in ("sì", "no")]
    kp = kappa(pairs)
    out.append({"test": "Reliability gate (kappa on repeats)", "value": f"kappa {kp:.2f} on {len(pairs)} pairs" if kp is not None else "no pairs",
                "verdict": "" if kp is None else ("passed" if kp >= 0.60 else "failed: no claim from C76 may be stated as holds")})
    # reported
    for e in ("L06_mlp", "L14_mlp", "L28_mlp"):
        l = rate([c["off"] for c in cases if c["state"] == "lost" and c["edit"] == e]); k_ = rate([c["off"] for c in cases if c["state"] == "kept" and c["edit"] == e])
        out.append({"test": f"M1 by edit {e} (reported)", "value": f"L_lost {f(l[0])} (n {l[1]}); L_kept {f(k_[0])} (n {k_[1]})", "verdict": ""})
    for w in words:
        l = rate([c["off"] for c in cases if c["state"] == "lost" and c["word"] == w]); k_ = rate([c["off"] for c in cases if c["state"] == "kept" and c["word"] == w])
        z = rate([c["off"] for c in cases if c["word"] == w and c["variant"] in ("original", "plain_B0")])
        out.append({"test": f"M1 by word {w} (reported)", "value": f"L_lost {f(l[0])} (n {l[1]}); L_kept {f(k_[0])} (n {k_[1]}); L_0 {f(z[0])} (n {z[1]})", "verdict": ""})
    for b in ("<=0.50", "0.60-0.80", ">=0.85"):
        l = rate([c["off"] for c in cases if c["state"] == "lost" and band(c["dose"]) == b]); k_ = rate([c["off"] for c in cases if c["state"] == "kept" and band(c["dose"]) == b])
        out.append({"test": f"M1 by dose band {b} (reported)", "value": f"L_lost {f(l[0])} (n {l[1]}); L_kept {f(k_[0])} (n {k_[1]})", "verdict": ""})
    g = [c for c in cases if c["word"] == "green" and c["edit"] == "L28_mlp" and c["char"] == "E2"]
    out.append({"test": "L28, elf, green off-target by dose (reported)",
                "value": " ".join(f"{c['seed'][:2]}/{c['dose']}:{c['off']}" for c in sorted(g, key=lambda c: (c["seed"], float(c["dose"])))), "verdict": ""})
    if keyA and labA:
        A1, _ = _answers(labA); fA = {k["file"]: k["item"] for k in keyA}
        agree = []
        for c in cases:
            if c["word"] in OVERLAP and c["file"] in fA and c["on"] is not None:
                x = {"sì": 1, "no": 0}.get(A1.get((fA[c["file"]], OVERLAP[c["word"]])))
                if x is not None:
                    agree.append((x, c["on"]))
        out.append({"test": "on-answers here against C75 part A traits, same pictures (reported)",
                    "value": f"agree {sum(a == b for a, b in agree)} of {len(agree)}; kappa {kappa(agree):.2f}" if agree else "no pairs", "verdict": ""})
    return out, cases


def run():
    out, cases = tally(rd(DATA / "te_bind_key.csv"), rd(DATA / "te_bind_questions.csv"), rd(DATA / "te_bind_rater.csv"),
                       rd(DATA / "te_traits_key_A.csv"), rd(DATA / "te_traits_alessandro.csv"))
    with open(DATA / "te_bind_tests.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    with open(DATA / "te_bind_cases.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cases[0])); w.writeheader(); w.writerows(cases)
    for o in out: print(o)


def selftest():
    """Two synthetic labellers on the real schedule. 'moves': colours lost under L06/L14 at d >= 0.6 and then seen on
    the body. 'vanishes': the same losses, never seen on the body. Random pushes: nothing lost, nothing misplaced."""
    key, sched, qs = rd(DATA / "te_bind_key.csv"), rd(DATA / "te_bind_schedule.csv"), rd(DATA / "te_bind_questions.csv")
    K = {k["item"]: k for k in key}
    for mode, expect1, expect2 in (("moves", "the colour moves (links break)", "edits misplace more"),
                                   ("vanishes", "the colour vanishes (defaults win)", "no difference")):
        lab = []
        for s in sched:
            k = K[s["item"]]; hit = k["variant"] == "real" and k["edit"] in ("L06_mlp", "L14_mlp") and float(k["dose"]) >= 0.6
            if s["question"].endswith("_on"):
                a = "no" if hit else "sì"
            else:
                a = "sì" if (hit and mode == "moves") else "no"
            lab.append({"block": s["block"], "pos": s["pos"], "item": s["item"], "showing": s["showing"], "question": s["question"], "answer": a})
        out, _ = tally(key, qs, lab)
        d = {o["test"].split(" ")[0]: o for o in out[:3]}
        assert d["M1"]["verdict"] == expect1, (mode, d["M1"])
        assert d["M2"]["verdict"] == expect2, (mode, d["M2"])
        assert d["Reliability"]["verdict"] == "passed"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    selftest() if a.selftest else run()
