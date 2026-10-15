"""C78 amendments 4-6 - tally of Alessandro's blind labels on the complex prompts (P3 totem, P4 prison break).
Rules: docs/prereg_te_punct.md, amendment 4 (primary test on the 12 questions fixed in amendment 3); secondary
questions (amendments 4-6) reported as counts. Written 2026-10-15 after the labels were committed (e973a23) and
before any count was looked at.

  python te_punct_tally.py            # data/te_punct_tests.csv, te_punct_by_picture.csv, te_punct_secondary.csv
  python te_punct_tally.py --selftest
"""
import argparse, csv, sys
from collections import defaultdict
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
VERSIONS = ["comma", "period", "semicolon", "nopunct", "break", "nolabels"]
NEG = {"t12", "p12", "t14", "t15", "s03", "s06", "x05b", "y05b"}   # written in the negative: "sì" = no defect


def rd(n):
    return list(csv.DictReader(open(DATA / n, encoding="utf-8-sig")))


def verdict(d, better, worse):
    if d <= -1 and better >= worse + 3:
        return "helps"
    if d >= 1 and worse >= better + 3:
        return "hurts"
    if abs(d) <= 0.25:
        return "no difference"
    return "inconclusive"


def kappa(pairs):
    pairs = [(a, b) for a, b in pairs if a in ("sì", "no") and b in ("sì", "no")]
    n = len(pairs)
    if not n:
        return float("nan"), 0
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a == "sì" for a, _ in pairs) / n; pb = sum(b == "sì" for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, n


def run():
    key = {r["item"]: r for r in rd("te_punct_key.csv")}
    qs = {q["id"]: q for q in rd("te_punct_questions.csv")}
    lab = rd("te_punct_alessandro.csv")
    first, second = {}, {}
    for r in lab:
        (first if r["showing"] == "1" else second)[(r["item"], r["question"])] = r["answer"]
    # reliability
    rep = [(first[k], second[k]) for k in second if k in first]
    rep_p = [(first[k], second[k]) for k in second if k in first and qs[k[1]]["primary"] == "1"]
    rep_neg = [(first[k], second[k]) for k in second if k in first and k[1] in NEG]
    rep_pos = [(first[k], second[k]) for k in second if k in first and k[1] not in NEG]
    k_p, n_p = kappa(rep_p); k_a, n_a = kappa(rep)
    agree = lambda P: (sum(a == b for a, b in P if a in ("sì", "no") and b in ("sì", "no")), sum(1 for a, b in P if a in ("sì", "no") and b in ("sì", "no")))
    # errors per picture (primary)
    prim = [q for q in qs if qs[q]["primary"] == "1"]
    err = {}; unk = {}
    for it, r in key.items():
        mine = [q for q in prim if qs[q]["prompt"] == r["prompt"]]
        ans = [first.get((it, q)) for q in mine]
        assert all(a is not None for a in ans), (it, mine)
        err[it] = sum(a == "no" for a in ans); unk[it] = sum(a == "non so" for a in ans)
    by = {(r["prompt"], r["version"], r["seed"]): it for it, r in key.items()}
    with open(DATA / "te_punct_by_picture.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["item", "prompt", "version", "seed", "errors", "cannot_tell"])
        for it, r in sorted(key.items(), key=lambda x: (x[1]["prompt"], x[1]["version"], x[1]["seed"])):
            w.writerow([it, r["prompt"], r["version"], r["seed"], err[it], unk[it]])
    rows = []
    mean = lambda xs: sum(xs) / len(xs)
    orig_all = [err[by[(p, "original", s)]] for (p, v, s) in by if v == "original"]
    rows.append({"test": "original", "version": "original", "mean_errors": round(mean(orig_all), 3), "d": "", "better": "", "worse": "",
                 "ties": "", "P3_d": "", "P4_d": "", "verdict": "", "note": f"{len(orig_all)} pictures"})
    for v in VERSIONS:
        diffs = {"P3_totem": [], "P4_prison": []}
        for (p, vv, s), it in by.items():
            if vv == v:
                diffs[p].append(err[it] - err[by[(p, "original", s)]])
        allx = diffs["P3_totem"] + diffs["P4_prison"]
        d = mean(allx); b = sum(x < 0 for x in allx); wv = sum(x > 0 for x in allx)
        rows.append({"test": "primary", "version": v, "mean_errors": round(mean([err[by[(p, v, s)]] for (p, vv, s) in by if vv == v]), 3),
                     "d": round(d, 3), "better": b, "worse": wv, "ties": len(allx) - b - wv,
                     "P3_d": round(mean(diffs["P3_totem"]), 3), "P4_d": round(mean(diffs["P4_prison"]), 3),
                     "verdict": verdict(d, b, wv), "note": "16 seed-pairs; 6 versions tested, no correction"})
    rows.append({"test": "reliability", "version": "", "mean_errors": "", "d": "", "better": "", "worse": "", "ties": "", "P3_d": "", "P4_d": "",
                 "verdict": "passed" if k_p >= 0.60 else "FAILED: no test may be stated as holding",
                 "note": f"kappa primary {k_p:.3f} on {n_p} pairs; all questions {k_a:.3f} on {n_a}; agreement negative-worded {agree(rep_neg)[0]}/{agree(rep_neg)[1]}, positive-worded {agree(rep_pos)[0]}/{agree(rep_pos)[1]}"})
    with open(DATA / "te_punct_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    # secondary and per-question counts: share of "sì" among sì/no, by version
    sec = []
    for q in qs:
        p = qs[q]["prompt"]
        row = {"question": q, "prompt": p, "primary": qs[q]["primary"], "negative_wording": int(q in NEG), "text": qs[q]["question_it"]}
        for v in ["original"] + VERSIONS:
            a = [first[(it, q)] for it, r in key.items() if r["prompt"] == p and r["version"] == v and (it, q) in first]
            y = sum(x == "sì" for x in a); n = sum(x in ("sì", "no") for x in a)
            row[v] = f"{y}/{n}"
        sec.append(row)
    with open(DATA / "te_punct_secondary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sec[0])); w.writeheader(); w.writerows(sec)
    for r in rows:
        print(r)


def selftest():
    assert verdict(-1.2, 8, 3) == "helps" and verdict(-1.2, 6, 4) == "inconclusive"
    assert verdict(1.0, 2, 5) == "hurts" and verdict(0.2, 4, 4) == "no difference" and verdict(-0.5, 7, 3) == "inconclusive"
    k, n = kappa([("sì", "sì"), ("no", "no"), ("sì", "no"), ("sì", "sì"), ("non so", "sì")]); assert n == 4 and abs(k - (0.75 - 0.5) / 0.5) < 1e-9, k
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    selftest() if a.selftest else run()
