"""One table for the results page on blk23: for each C47 cell, the words' chroma gain and the
layout r / LPIPS / DINOv2 cosine of the words and of blk23 interpolated at that same gain.
Same interpolation as analyze_blk23_vs_colorful.py (T1) and analyze_standard_metrics.py (M1).
Reads data/blk23_colorful_measures.csv and data/standard_metrics_c47.csv;
writes data/blk23_matched_chroma.csv.
"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data")
LADDER = ["b23_m0.450", "b23_m0.300", "b23_m0.150", "baseline", "b23_p0.150", "b23_p0.300"]


def main():
    ms = {(r["prompt"], r["seed"], r["cond"]): r for r in csv.DictReader(open(os.path.join(DATA, "blk23_colorful_measures.csv")))}
    sm = {(r["prompt_id"], r["seed"], r["cond"]): r for r in csv.DictReader(open(os.path.join(DATA, "standard_metrics_c47.csv")))}
    cells = sorted({(p, s) for p, s, _ in ms})
    out = []
    for p, s in cells:
        ch = lambda c: 0.0 if c == "baseline" else float(ms[(p, s, c)]["d_chroma"])
        val = {"layout_r": lambda c: 1.0 if c == "baseline" else float(ms[(p, s, c)]["layout_r"]),
               "lpips": lambda c: 0.0 if c == "baseline" else float(sm[(p, s, c)]["lpips"]),
               "dino_cos": lambda c: 1.0 if c == "baseline" else float(sm[(p, s, c)]["dino_cos"])}
        tc = ch("txtpos"); row = {"prompt": p, "seed": s, "text_d_chroma": round(tc, 3),
                                  "blk23_max_d_chroma": round(ch("b23_m0.450"), 3)}
        hit = None
        for c0, c1 in zip(LADDER, LADDER[1:]):
            a, b = ch(c0), ch(c1)
            if min(a, b) <= tc <= max(a, b) and a != b:
                hit = (c0, c1, (tc - a) / (b - a)); break
        row["scorable"] = int(hit is not None)
        for k, f in val.items():
            row[f"text_{k}"] = round(f("txtpos"), 4)
            row[f"blk23_{k}"] = "" if hit is None else round(f(hit[0]) + hit[2] * (f(hit[1]) - f(hit[0])), 4)
        out.append(row)
    with open(os.path.join(DATA, "blk23_matched_chroma.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(sum(r["scorable"] for r in out), "scorable of", len(out))


if __name__ == "__main__":
    main()
