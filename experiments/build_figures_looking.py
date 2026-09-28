#!/usr/bin/env python3
"""Figures for notebook/11-what-the-numbers-could-not-see.md.

Three sheets, each rebuilt from the renders and each REFUSING TO COMPOSE if the measurement file
does not say what its caption says. That guard is the point: every one of these figures exists
because a number and a picture disagreed, and a figure that outlived its data would be the same
mistake a third time.

The renders live outside the repository (ComfyUI's output tree), so a root is passed in; the
default is the mount used while the page was written.

    python experiments/build_figures_looking.py [--roots DIR ...]
"""
import argparse, csv, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "11-what-the-numbers-could-not-see")
DEFAULT_ROOTS = [os.path.expanduser("~/mnt")]
SEEDS3 = ["42", "777", "1337"]
SURFACE = (26, 26, 25)   # the notebook's dark surface; the validator checks it
MARGIN, GUTTER = 18, 8


def find(rel, roots):
    for r in roots:
        p = os.path.join(r, rel)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(rel)


def rows_of(path):
    return list(csv.DictReader(open(os.path.join(ROOT, path), encoding="utf-8")))


def compose(tiles, cols, tw, th, outfile, resample=Image.LANCZOS):
    rows = (len(tiles) + cols - 1) // cols
    fig = Image.new("RGB",
                    (2 * MARGIN + cols * tw + (cols - 1) * GUTTER,
                     2 * MARGIN + rows * th + (rows - 1) * GUTTER), SURFACE)
    for i, p in enumerate(tiles):
        if p is None:
            continue
        fig.paste(Image.open(p).resize((tw, th), resample),
                  (MARGIN + (i % cols) * (tw + GUTTER), MARGIN + (i // cols) * (th + GUTTER)))
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, outfile)
    fig.save(dst, "WEBP", quality=88, method=6)
    print(f"  {outfile}  {fig.size}")


def f11_1(roots):
    """The mushroom: told 'brown', told 'purple', told nothing."""
    amb = {r["subject"]: float(r["mean_deg"]) for r in rows_of("data/prior_ambiguity.csv")}
    if amb["mushroom"] >= 20 or amb["leaf"] <= 30:
        raise RuntimeError("REFUSING TO COMPOSE F11.1: prior_ambiguity says mushroom "
                           f"{amb['mushroom']:.1f} deg and leaf {amb['leaf']:.1f} deg; the figure "
                           "would claim the mushroom's prior is unambiguous and the leaf's is not.")
    R = "benchmark_leaf_collapse/renders"
    tiles = []
    for tag in ("P", "U", "N"):
        for s in SEEDS3:
            for kind in ("baseline", "B4neg_0.200"):
                tiles.append(find(f"{R}/MU{tag}_{kind}_krea2_seed{s}_00001_.png", roots))
    compose(tiles, 6, 250, 312, "F11.1_the_prior_leaves_nothing_to_infer.webp")


def f11_2(roots):
    """Arm A: twenty seeds, untouched above, edited below."""
    cells = [r for r in rows_of("data/leaf_collapse_cells.csv") if r["arm"] == "A_seeds"]
    hits = [r for r in cells if r["hit"] == "1"]
    ratios = sorted(float(r["chroma_ratio"]) for r in cells)
    gap = [x for x in ratios if 0.15 < x < 0.45]
    if len(hits) != 9 or gap:
        raise RuntimeError(f"REFUSING TO COMPOSE F11.2: {len(hits)} hits (caption says 9) and "
                           f"{len(gap)} cells inside the empty band (caption says none).")
    R = "benchmark_leaf_collapse/renders"
    seeds = sorted(r["seed"] for r in cells)
    tiles = [find(f"{R}/LN_baseline_krea2_seed{s}_00001_.png", roots) for s in seeds[:10]]
    tiles += [find(f"{R}/LN_B4neg_0.200_krea2_seed{s}_00001_.png", roots) for s in seeds[:10]]
    compose(tiles, 10, 210, 262, "F11.2_nine_of_twenty.webp")


def f11_3(roots):
    """B6_mask at 100 %: both arms, the same crop, no downscaling."""
    coh = {(r["condition"], r["arm"]): float(r["coherence_ratio"])
           for r in rows_of("data/texture_anisotropy.csv")}
    if coh[("B6_mask", "neg")] >= 0.75 or coh[("B4_mask", "pos")] <= 1.02:
        raise RuntimeError("REFUSING TO COMPOSE F11.3: coherence says B6_mask neg "
                           f"{coh[('B6_mask','neg')]:.3f} and B4_mask pos "
                           f"{coh[('B4_mask','pos')]:.3f}; the figure would claim the first is the "
                           "corpus's worst loss of line and the second its best.")
    R = "benchmark_rectified_masks/renders"
    box = (380, 120, 720, 460)
    parts = [find(f"{R}/P01_B4_mask_pos_seed777_00001_.png", roots),
             find(f"{R}/P01_B6_mask_pos_seed777_00001_.png", roots),
             find(f"{R}/P01_B6_mask_neg_seed777_00001_.png", roots)]
    fig = Image.new("RGB", (2 * MARGIN + 340 * 3 + 2 * GUTTER, 2 * MARGIN + 340), SURFACE)
    for i, p in enumerate(parts):
        fig.paste(Image.open(p).crop(box), (MARGIN + i * (340 + GUTTER), MARGIN))
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, "F11.3_the_curl_field.webp")
    fig.save(dst, "WEBP", quality=92, method=6)
    print(f"  F11.3_the_curl_field.webp  {fig.size}  (crops at 1:1, never downscaled)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="*", default=DEFAULT_ROOTS)
    a = ap.parse_args()
    for fn in (f11_1, f11_2, f11_3):
        fn(a.roots)


if __name__ == "__main__":
    main()
