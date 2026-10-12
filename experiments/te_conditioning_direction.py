"""C67 amendment 2 (exploratory): direction of the conditioning change across prompts.

  python te_conditioning_direction.py [--img-root PATH]
      -> data/te_conditioning_direction.csv (per edit: agreement across orders, across characters, watercolour vs comic D1)
         data/te_conditioning_direction_tests.csv (D1-D3)
"""
import argparse, csv, itertools, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_conditioning as T

DATA = HERE.parent / "data"
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter", "G5_gnome_wizard", "H3_halfling_druid",
         "R6_dragonborn_cleric", "T7_tiefling_bard"]
SHORT = ["D1", "E2", "O4", "G5", "H3", "R6", "T7"]
ORDERS = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
WC = "D1W_dwarf_paladin_watercolor"


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def vec(set_, pid, cond, unit):
    z = np.load(T.out_path(set_, pid, cond))
    return z["dmean"].astype(np.float32)[T.first_tap(unit):].ravel()


def main():
    rows = T.rd(T.PLAN)
    edits = []
    for r in rows:
        if r["set"] == "order" and r["mode"] == "diff" and (r["cond"], r["unit"]) not in edits:
            edits.append((r["cond"], r["unit"]))
    V = {}
    out = []
    for k, u in edits:
        o = {v: vec("order", v, k, u) for v in ORDERS}
        c = {ch: vec("chars", ch, k, u) for ch in CHARS + [WC]}
        V[k] = (o, c)
        out.append({"cond": k, "agree_orders": round(np.mean([cos(o[a], o[b]) for a, b in itertools.combinations(ORDERS, 2)]), 4),
                    "agree_chars": round(np.mean([cos(c[a], c[b]) for a, b in itertools.combinations(CHARS, 2)]), 4),
                    "watercolor_vs_comicD1": round(cos(c[WC], c["D1_dwarf_paladin"]), 4),
                    "comicD1_vs_other_chars": round(np.mean([cos(c["D1_dwarf_paladin"], c[x]) for x in CHARS[1:]]), 4)})
    # floor: agreement between different edits on the same prompt (V1 order; chars D1)
    cross = []
    for (k1, _), (k2, _) in itertools.combinations(edits, 2):
        a, b = V[k1][0]["V1_Original"], V[k2][0]["V1_Original"]
        n = min(len(a), len(b))
        cross.append(cos(a[-n:], b[-n:]))       # common taps (the later ones)
    with open(DATA / "te_conditioning_direction.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    agree = {x["cond"]: x for x in out}
    res = []
    # D1 orders
    sc = {r["row"]: int(r["score_1_5"]) for r in T.rd(DATA / "te_order_grid_notes_alessandro.csv") if r["grid"] == "te_order_3141592" and r["score_1_5"]}
    ks = [k for k in sc if k in agree]
    rho, p = T.spearman([1 - agree[k]["agree_orders"] for k in ks], [sc[k] for k in ks])
    res.append({"test": "D1 orders: direction disagreement vs 1-5 scores", "n": len(ks), "rho": round(rho, 3), "p": round(p, 4), "rule": "rho >= 0.50",
                "verdict": "holds" if rho >= 0.50 else "does not hold"})
    # D2 characters
    eye = [x for x in T.rd(DATA / "te_characters_eye_joined.csv") if x["first"] == "1" and x["stessa"]]
    m = {"si": 2, "parte": 1, "no": 0}
    xs = [(agree[x["cond"]]["agree_chars"], m[x["stessa"]]) for x in eye if x["cond"] in agree]
    rho2, p2 = T.spearman([a for a, _ in xs], [b for _, b in xs])
    res.append({"test": "D2 characters: direction agreement vs 'same direction'", "n": len(xs), "rho": round(rho2, 3), "p": round(p2, 4), "rule": "rho >= 0.40",
                "verdict": "holds" if rho2 >= 0.40 else "does not hold"})
    # D3 exceptions
    pos, neg = [], []
    for x in eye:
        if x["cond"] not in V:
            continue
        c = V[x["cond"]][1]
        for ch, s in zip(CHARS, SHORT):
            v = cos(c[ch], np.mean([c[o] for o in CHARS if o != ch], axis=0))
            lab = x[f"c_{s}"]
            (neg if lab == "diverso" else pos if lab == "segue" else []).append(v)
    a = T.auc(pos, neg)
    res.append({"test": "D3 exceptions: cosine with the other six, follows vs another way", "n": f"{len(pos)}+{len(neg)}", "auc": round(a, 3),
                "rule": "AUC >= 0.70", "verdict": "holds" if a >= 0.70 else "does not hold"})
    res.append({"test": "floor: agreement between different edits (V1, common taps)", "n": len(cross), "median": round(float(np.median(cross)), 3),
                "rule": "reported", "verdict": "reported"})
    with open(DATA / "te_conditioning_direction_tests.csv", "w", newline="", encoding="utf-8") as f:
        cols = sorted({k for r in res for k in r}, key=lambda k: ["test", "n", "verdict", "rule"].index(k) if k in ("test", "n", "verdict", "rule") else 9)
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(res)
    for r in res:
        print(r)
    print()
    for x in sorted(out, key=lambda x: x["agree_chars"]):
        print(f"{x['cond']:16s} orders {x['agree_orders']:.3f}  chars {x['agree_chars']:.3f}  wc-vs-D1 {x['watercolor_vs_comicD1']:.3f}  D1-vs-others {x['comicD1_vs_other_chars']:.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--img-root"); a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    main()
