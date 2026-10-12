"""C67, exploratory: direction of the change by prompt region, on the elf (the 20 C65 edits kept in full).
Regions = the sentences of the elf prompt: style, framing, subject, clothes, action, background, lighting.

  python te_conditioning_regions.py [--img-root PATH] [--vocab PATH]
      -> data/te_conditioning_regions_elf.csv  per edit: agreement between regions (reached taps), size per region
         data/te_conditioning_regions_summary.csv  same region across edits vs different regions within an edit (last 3 taps)
"""
import argparse, csv, itertools, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_conditioning as T

DATA = HERE.parent / "data"
MARKS = [("style", None), ("framing", "smug grin"), ("subject", "female antlered"), ("clothes", "fur-collared"),
         ("action", "looking to her left"), ("background", "Background:"), ("lighting", "Lighting:"), ("template", "<|im_end|>")]


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def regions(ids, inv):
    pieces = [inv.get(int(i), "") for i in ids]
    starts = np.cumsum([0] + [len(p) for p in pieces[:-1]]); text = "".join(pieces)
    offs = [0 if m is None else text.index(m) for _, m in MARKS]
    return np.array([max(i for i, o in enumerate(offs) if o <= s) for s in starts]), [n for n, _ in MARKS]


def main():
    inv = T.vocab()
    b = np.load(T.out_path("elf", "P1_elfbrawler", "baseline")); B = b["cond"].astype(np.float32)
    reg, names = regions(b["ids"], inv); names = names[:-1]
    rows, last3 = [], {}
    for r in T.rd(T.PLAN):
        if r["set"] != "elf_full":
            continue
        E = np.load(T.out_path("elf_full", "P1_elfbrawler", r["cond"]))["cond"].astype(np.float32)
        j0 = T.first_tap(r["unit"]); D = (E - B)
        V = {n: D[reg == i][:, j0:].mean(0).ravel() for i, n in enumerate(names)}
        size = {n: float(np.linalg.norm(D[reg == i][:, j0:], axis=-1).mean() / np.linalg.norm(B[reg == i][:, j0:], axis=-1).mean()) for i, n in enumerate(names)}
        rows.append({"cond": r["cond"], "agree_between_regions": round(float(np.mean([cos(V[a], V[c]) for a, c in itertools.combinations(names, 2)])), 4),
                     **{f"size_{n}": round(v, 4) for n, v in size.items()}})
        last3[r["cond"]] = {n: D[reg == i][:, -3:].mean(0).ravel() for i, n in enumerate(names)}
    with open(DATA / "te_conditioning_regions_elf.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    conds = list(last3); summ = []
    for n in names:
        summ.append({"what": f"same region ({n}), different edits", "median_cos": round(float(np.median([cos(last3[a][n], last3[c][n]) for a, c in itertools.combinations(conds, 2)])), 4)})
    summ.append({"what": "different regions, same edit", "median_cos": round(float(np.median([np.mean([cos(last3[c][a], last3[c][d]) for a, d in itertools.combinations(names, 2)]) for c in conds])), 4)})
    with open(DATA / "te_conditioning_regions_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0])); w.writeheader(); w.writerows(summ)
    for r in rows: print(r["cond"], r["agree_between_regions"])
    for s in summ: print(s)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--img-root"); ap.add_argument("--vocab"); a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.vocab: T.VOCAB = Path(a.vocab)
    main()
