#!/usr/bin/env python3
"""Rebuilds every contact sheet of the 2026-09-28 benches, so looking is repeatable.

These sheets are not notebook figures -- those are in experiments/build_figures_looking.py and
carry data guards. These are the working sheets: every render of a bench laid out so a person can
scan it before trusting a statistic. Three findings on 2026-09-28 came from them and from nothing
else, which is why they are a script and a kept folder rather than stray files.

Output: <bench root>/benchmark_leaf_collapse/_contact_sheets, beside the renders, with an INDEX.txt.
No render.

    python experiments/build_contact_sheets.py [--root DIR]
"""
import argparse, os
from PIL import Image

SURFACE = (26, 26, 25)
MARGIN, GUTTER = 16, 6
SEEDS3 = ["42", "777", "1337"]
ARM_A = [str(s) for s in range(2001, 2021)]
FIRE = {"2001", "2003", "2005", "2006", "2008", "2011", "2013", "2014", "2017"}


def sheet(paths, cols, out, tw=250, th=312):
    rows = (len(paths) + cols - 1) // cols
    fig = Image.new("RGB", (2*MARGIN + cols*tw + (cols-1)*GUTTER,
                            2*MARGIN + rows*th + (rows-1)*GUTTER), SURFACE)
    n = 0
    for i, p in enumerate(paths):
        if p and os.path.exists(p):
            fig.paste(Image.open(p).resize((tw, th), Image.LANCZOS),
                      (MARGIN + (i % cols)*(tw+GUTTER), MARGIN + (i // cols)*(th+GUTTER)))
            n += 1
    fig.save(out)
    return n, fig.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser("~/mnt"))
    a = ap.parse_args()
    LEAF = os.path.join(a.root, "benchmark_leaf_collapse", "renders")
    MASK = os.path.join(a.root, "benchmark_rectified_masks", "renders")
    OUT = os.path.join(a.root, "benchmark_leaf_collapse", "_contact_sheets")
    os.makedirs(OUT, exist_ok=True)
    index = []

    # arm A -- twenty seeds, untouched row over edited row, ten per sheet
    for k, seeds in enumerate([ARM_A[:10], ARM_A[10:]], start=1):
        paths = [os.path.join(LEAF, f"LN_baseline_krea2_seed{s}_00001_.png") for s in seeds] + \
                [os.path.join(LEAF, f"LN_B4neg_0.200_krea2_seed{s}_00001_.png") for s in seeds]
        n, sz = sheet(paths, 10, os.path.join(OUT, f"armA_{k}.png"), 210, 262)
        index.append(f"armA_{k}.png     {n:3d} renders {sz}  untouched above, edited below; "
                     f"seeds {seeds[0]}-{seeds[-1]}; collapsing seeds: "
                     + ", ".join(s for s in seeds if s in FIRE))

    # arm B -- five rewordings x three seeds, untouched beside edited
    paths = [os.path.join(LEAF, f"W{w}_{k}_krea2_seed{s}_00001_.png")
             for w in range(1, 6) for s in SEEDS3 for k in ("baseline", "B4neg_0.200")]
    n, sz = sheet(paths, 6, os.path.join(OUT, "armB.png"))
    index.append(f"armB.png        {n:3d} renders {sz}  rows W1-W5 (rewordings); "
                 "columns seed x (untouched | edited)")

    # arm C -- one sheet per subject, rows prototypical / purple / undeclared
    for sub, name in (("MU", "mushroom"), ("TO", "tomato"), ("PC", "pinecone"), ("BA", "banana")):
        paths = [os.path.join(LEAF, f"{sub}{t}_{k}_krea2_seed{s}_00001_.png")
                 for t in ("P", "U", "N") for s in SEEDS3 for k in ("baseline", "B4neg_0.200")]
        n, sz = sheet(paths, 6, os.path.join(OUT, f"armC_{sub}.png"))
        index.append(f"armC_{sub}.png     {n:3d} renders {sz}  {name}: rows prototypical / purple / "
                     "undeclared; columns seed x (untouched | edited)")

    # the rectified masks, both prompts
    for p in ("P01", "P02"):
        conds = ["B4_mask", "B4_anti", "B6_mask", "B6_anti", "B4B6_mask", "B4B6_anti"]
        paths = [os.path.join(MASK, f"{p}_{c}_{arm}_seed{s}_00001_.png")
                 for c in conds for s in SEEDS3 for arm in ("pos", "neg")]
        n, sz = sheet(paths, 6, os.path.join(OUT, f"masks_{p}.png"))
        index.append(f"masks_{p}.png   {n:3d} renders {sz}  rows {', '.join(conds)}; "
                     "columns seed x (pos | neg)")

    with open(os.path.join(OUT, "INDEX.txt"), "w", encoding="utf-8") as fh:
        fh.write("Contact sheets, rebuilt by experiments/build_contact_sheets.py\n")
        fh.write("Working sheets for scanning a bench by eye. The notebook figures are separate\n"
                 "and carry data guards: experiments/build_figures_looking.py.\n\n")
        for line in index:
            fh.write(line + "\n")
    for line in index:
        print("  " + line)
    print(f"\n  INDEX.txt -> {OUT}")


if __name__ == "__main__":
    main()
