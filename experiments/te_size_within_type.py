"""Exploratory (2026-10-12, after C70, not pre-registered): does the size of the conditioning change predict the
change seen by eye *within* one type of edit? Answers a review remark that C67 E1 and C70 G3d may mostly separate
edit types. Writes data/te_size_within_type.csv."""
import csv, statistics as st
from pathlib import Path
from scipy.stats import spearmanr
DATA = Path(__file__).resolve().parent.parent / "data"
rd = lambda n: list(csv.DictReader(open(DATA / n, encoding="utf-8")))
out = []
# C67 E1 material: 140 elf edits at +-1.00, eye label "how much it changed" (C64 phase 1)
sz = {r["cond"]: float(r["mean_rel"]) for r in rd("te_conditioning_edits.csv") if r["set"] == "elf"}
lv = {"nessuna": 0, "lieve": 1, "media": 2, "forte": 3, "testo": 4}
J = [r for r in rd("te_pilot_phase1_joined.csv") if r["phase"] != "check" and r["cond"] in sz and r["entita"] in lv]
def add(src, group, xs, ys):
    rho, p = spearmanr(xs, ys)
    out.append({"source": src, "group": group, "n": len(xs), "spearman": round(float(rho), 3), "p": round(float(p), 4)})
add("C67 E1 (size vs C64 change label)", "all", [sz[r["cond"]] for r in J], [lv[r["entita"]] for r in J])
for part in ("mlp", "attn"):
    for sign, name in (("+", "doubled"), ("-", "zeroed")):
        rs = [r for r in J if r["part"] == part and r["sign"] == sign]
        add("C67 E1 (size vs C64 change label)", f"{part} {name}", [sz[r["cond"]] for r in rs], [lv[r["entita"]] for r in rs])
n_strong = sum(1 for r in J if r["part"] == "mlp" and r["sign"] == "+" and r["entita"] == "forte")
# C70 G3d material: 20 edits, size (te_order_tests) vs mean intensity over five orders
size = {r["cond"]: float(r["size"]) for r in rd("te_order_tests.csv")}
dose = {r["row"]: [int(r[f"d{i}"]) for i in range(1, 6)] for r in rd("te_genre_dose_alessandro.csv") if r["row"] != "originali"}
add("C70 G3d (size vs mean intensity)", "all", [size[k] for k in size], [st.mean(dose[k]) for k in size])
for name, f in (("mlp doubled", lambda k: "mlp_p" in k), ("attn doubled", lambda k: "attn_p" in k)):
    ks = [k for k in size if f(k)]
    add("C70 G3d (size vs mean intensity)", name, [size[k] for k in ks], [st.mean(dose[k]) for k in ks])
with open(DATA / "te_size_within_type.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in out:
    print(r)
print("C64 MLP doubled labelled strong:", n_strong, "of 35")
