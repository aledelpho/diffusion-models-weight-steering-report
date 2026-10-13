"""C75 B2, exploratory (written 2026-10-13 after the pre-registered tally, decides nothing): B1 by dose and by edit x
dose; inter-rater agreement on the pictures shared with part A, per trait, without e_androgynous and person
(amendment 4); skin categories of both raters on shared pictures. Output: data/te_traits_B2_explore.csv."""
import csv, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import te_traits_tally as T
DATA = T.DATA
kB = T.rd(DATA / "te_traits_key_B2.csv"); kA = T.rd(DATA / "te_traits_key_A.csv")
b1, _ = T._answers(T.rd(DATA / "te_traits_B2_rater2.csv")); a1, _ = T._answers(T.rd(DATA / "te_traits_alessandro.csv"))
sched = T.rd(DATA / "te_traits_schedule_B2.csv")
per = defaultdict(set)
for s in sched:
    if s["kind"] == "trait": per[s["char"]].add(s["question"])
V = T.VAL
orig = {(k["char"], k["seed"]): k["item"] for k in kB if k["variant"] == "original"}
def R(it, c, s):
    o = orig[(c, s)]; p0 = [q for q in per[c] if V.get(b1.get((o, q))) == 1 and V.get(b1.get((it, q))) is not None]
    return sum(V[b1[(it, q)]] for q in p0) / len(p0) if p0 else None
cells = defaultdict(dict)
for k in kB:
    if k["edit"]: cells[(k["char"], k["seed"], k["edit"], k["dose"])][k["variant"]] = R(k["item"], k["char"], k["seed"])
out = []
for d in ("0.70", "0.85", "1.00"):
    for e in ("all", "L06_mlp", "L14_mlp", "L28_mlp"):
        v = [x for c, x in cells.items() if c[3] == d and (e == "all" or c[2] == e)]
        out.append({"what": f"B1 dose {d} {e}", "n_cells": len(v), "real": round(statistics.mean(x["real"] for x in v), 3),
                    "token": round(statistics.mean(x["token"] for x in v), 3), "permuted": round(statistics.mean(x["permuted"] for x in v), 3)})
fA = {k["file"]: k["item"] for k in kA}
agree = defaultdict(lambda: [0, 0]); pairs = []
for k in kB:
    if k["file"] not in fA: continue
    ia = fA[k["file"]]
    for q in per[k["char"]]:
        if q == "e_androgynous": continue
        x, y = a1.get((ia, q)), b1.get((k["item"], q))
        if x in ("sì", "no") and y in ("sì", "no"):
            agree[q][0] += x == y; agree[q][1] += 1; pairs.append((x, y))
out.append({"what": "inter-rater kappa, traits without e_androgynous", "n_cells": len(pairs), "real": round(T.kappa(pairs), 3), "token": "", "permuted": ""})
for q, (a, n) in sorted(agree.items(), key=lambda x: x[1][0] / x[1][1]):
    out.append({"what": f"inter-rater agreement {q}", "n_cells": n, "real": round(a / n, 3), "token": "", "permuted": ""})
sk = Counter((T._skin(a1, fA[k["file"]]), T._skin(b1, k["item"])) for k in kB if k["file"] in fA and k["edit"])
out.append({"what": "skin (Alessandro, rater 2) on shared edited pictures", "n_cells": sum(sk.values()), "real": str(dict(sk)), "token": "", "permuted": ""})
with open(DATA / "te_traits_B2_explore.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out: print(o)
