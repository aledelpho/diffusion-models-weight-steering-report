"""C75 part A, exploratory (written 2026-10-13 after the pre-registered tally, decides nothing).
Per strip: sustained onset with the pre-registered criterion (R < 1) and with a stricter one (R <= 0.85, about two
traits of twelve), next to the C74 style onset; traits lost at d = 1.00; skin changes by character and edit.
Output: data/te_traits_explore.csv."""
import csv
from collections import Counter, defaultdict
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
D = ["0.10", "0.25", "0.40", "0.50", "0.60", "0.70", "0.75", "0.80", "0.85", "0.90", "0.95", "1.00"]
CH = {"D1": "D1_dwarf_paladin", "E2": "E2_elf_rogue", "O4": "O4_halforc_fighter"}


def onset(v, thr):
    best = "mai"
    for d in reversed(D):
        if v[d]["R"] == "":
            continue
        if float(v[d]["R"]) <= thr:
            best = d
        else:
            break
    return best


P = list(csv.DictReader(open(DATA / "te_traits_by_picture.csv", encoding="utf-8")))
st = defaultdict(dict)
for p in P:
    if p["edit"]:
        st[(p["char"], p["seed"], p["edit"])][p["dose"]] = p
style = {(r["grid"][-3:], r["row"]): r["cambia_da"] for r in csv.DictReader(open(DATA / "te_dose_alessandro.csv", encoding="utf-8-sig"))}
rows = []
for (c, s, e), v in sorted(st.items()):
    rows.append({"char": c, "seed": s, "edit": e, "onset_R_below_1": onset(v, 0.999), "onset_R_le_0.85": onset(v, 0.85),
                 "style_onset_C74": style.get((e[:3], f"{CH[c]} · {s}"), ""), "lost_at_1.00": v["1.00"]["lost"],
                 "skin_changes": dict(Counter(x["skin"] for x in v.values() if x["skin"] not in ("same", "")))})
with open(DATA / "te_traits_explore.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
O = {d: i for i, d in enumerate(D)}; O["mai"] = 99
m = [r for r in rows if r["edit"] in ("L06_mlp", "L14_mlp") and r["style_onset_C74"] not in ("", "mai")]
for k in ("onset_R_below_1", "onset_R_le_0.85"):
    a = sum(O[r[k]] < O[r["style_onset_C74"]] for r in m); b = sum(O[r[k]] > O[r["style_onset_C74"]] for r in m)
    print(f"{k}: traits first {a}, style first {b}, ties {len(m) - a - b}, of {len(m)}")
