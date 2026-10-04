"""Does a block's effect depend more on the STYLE or on the SUBJECT of the prompt?

Exploratory (2026-10-04, Alessandro's question about "presets per prompt style").
benchmark_single_blocks_styles, seed 2718281, Alessandro's per-block doses:
  same style, different subject : E1_cartoon, C1_blacksmith, C2_rally, C3_fox, C4_stilllife (all cartoon) -> 10 pairs
  same subject, different style : E1..E7 (the elf in cartoon, watercolour, oil, colour pencil,
                                  children's book, claymation, sepia photo)                       -> 21 pairs
  same subject and style, words moved: E1 vs E8                                                 -> 1 pair
Per arm: dF = 23 style features (data/single_blocks_styles_style_features.csv) of the arm minus
its baseline, each feature divided by its SD over the 12 baselines; mean cosine within each group.
Writes data/style_vs_subject_consistency.csv.
"""
import csv, itertools, os, re
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
PAT = re.compile(r"^(.+?)_(blk\d\d_(?:pos|neg)_d[\d.]+|baseline)_krea2_seed")
STYLE = ["E1_cartoon", "C1_blacksmith", "C2_rally", "C3_fox", "C4_stilllife"]
SUBJ = ["E1_cartoon", "E2_watercolor", "E3_oil", "E4_colorpencil", "E5_childrensbook", "E6_claymation", "E7_sepiaphoto"]


def main():
    rows = list(csv.DictReader(open(os.path.join(DATA, "single_blocks_styles_style_features.csv"))))
    keys = [k for k in rows[0] if k not in ("file", "width_px", "height_px")]
    F = {}
    for r in rows:
        m = PAT.match(r["file"]); F[(m[1], m[2])] = np.array([float(r[k]) for k in keys])
    prompts = sorted({p for p, _ in F})
    B = np.array([F[(p, "baseline")] for p in prompts]); sd = B.std(axis=0, ddof=1); sd[sd == 0] = 1
    arms = sorted({c for _, c in F if c != "baseline"})
    d = lambda p, c: (F[(p, c)] - F[(p, "baseline")]) / sd
    cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    out = []
    for c in arms:
        st = np.mean([cos(d(a, c), d(b, c)) for a, b in itertools.combinations(STYLE, 2)])
        su = np.mean([cos(d(a, c), d(b, c)) for a, b in itertools.combinations(SUBJ, 2)])
        wo = cos(d("E1_cartoon", c), d("E8_cartoon_styleend", c))
        size = np.mean([np.abs(d(p, c)).mean() for p in prompts])
        out.append([c, round(size, 3), round(st, 3), round(su, 3), round(wo, 3)])
    with open(os.path.join(DATA, "style_vs_subject_consistency.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "size", "same_style_diff_subject", "same_subject_diff_style", "E1_vs_E8_word_order"])
        w.writerows(out)
    big = [o for o in out if o[1] > 1.0]
    for name, sel in (("all", out), ("size>1", big)):
        a = np.array([o[2] for o in sel]); b = np.array([o[3] for o in sel]); e = np.array([o[4] for o in sel])
        print(f"{name:7s} n={len(sel):2d}  same style/diff subject {np.median(a):.3f}   same subject/diff style {np.median(b):.3f}"
              f"   style-consistency higher in {int((a > b).sum())}/{len(sel)}   word order (E1-E8) {np.median(e):.3f}")


if __name__ == "__main__":
    main()
