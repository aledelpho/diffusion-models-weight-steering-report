"""C59 post-hoc: band measure, summary and additivity tables, contact sheets (docs/split_atlas_result.md).
Written 2026-10-07, after the renders and after split_atlas.py --measure. Not pre-registered.

  python split_atlas_posthoc.py --band        # data/split_atlas_band_posthoc.csv (blur 2 - blur 8, ratio to baseline)
  python split_atlas_posthoc.py --tables      # data/split_atlas_summary.csv, data/split_atlas_additivity.csv
  python split_atlas_posthoc.py --sheets SEED # Text2Img/benchmark_split_atlas/sheets/*.jpg
  --img-root PATH overrides the render root (default: blk23_colorful.IMG_ROOT)
"""
import argparse, csv, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
DATA = HERE.parent / "data"


def arms(s, pid, seed, blk):
    a = [("attn", lambda sg: s.f_split(pid, seed, f"blk{blk:02d}_attn_{sg}_d0.350")),
         ("mlp", lambda sg: s.f_split(pid, seed, f"blk{blk:02d}_mlp_{sg}_d0.350"))]
    if seed == "2718281":
        a.append(("whole", lambda sg: s.f_atlas(pid, f"blk{blk:02d}_{sg}_d0.350")))
    return a


def band(s):
    def f(p):
        g = Image.open(p).convert("L")
        return float((np.asarray(g.filter(ImageFilter.GaussianBlur(2)), float) - np.asarray(g.filter(ImageFilter.GaussianBlur(8)), float)).std())
    rows = []
    for seed in s.SEEDS:
        for pid in s.PROMPTS:
            bb = f(s.f_base(pid, seed))
            for blk in range(28):
                for part, fn in arms(s, pid, seed, blk):
                    for sg in ("pos", "neg"):
                        rows.append({"prompt": pid, "seed": seed, "block": blk, "part": part, "sign": sg, "band_ratio": round(f(fn(sg)) / bb, 4)})
    with open(DATA / "split_atlas_band_posthoc.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def tables():
    import pandas as pd
    b = pd.read_csv(DATA / "split_atlas_blocks.csv"); m = pd.read_csv(DATA / "split_atlas_measures.csv")
    d = pd.read_csv(DATA / "split_atlas_band_posthoc.csv")
    rows = []
    for (blk, part), g in m.groupby(["block", "part"]):
        r = {"block": blk, "part": part, "n_cells": g[["prompt", "seed"]].drop_duplicates().shape[0]}
        for sg in ("pos", "neg"):
            h = g[g.sign == sg]
            r[f"hf_{sg}"] = round(h.hf_ratio.median(), 3); r[f"chroma_{sg}"] = round(h.d_chroma.median(), 2)
            r[f"layout_{sg}"] = round(h.layout_r.median(), 2)
            r[f"band_{sg}"] = round(d[(d.block == blk) & (d.part == part) & (d.sign == sg)].band_ratio.median(), 3)
        bb = b[(b.block == blk) & (b.part == part)]
        r["hf_common_mode"] = round(bb.common_mode.median(), 3); r["hf_swing"] = round(bb.swing.median(), 3)
        rows.append(r)
    pd.DataFrame(rows).to_csv(DATA / "split_atlas_summary.csv", index=False)
    s = m[m.seed == 2718281].pivot_table(index=["block", "prompt", "sign"], columns="part", values=["hf_ratio", "d_chroma", "layout_r"])
    lh = np.log(s["hf_ratio"])
    e = pd.DataFrame({"hf_whole": s["hf_ratio"].whole, "hf_attn": s["hf_ratio"].attn, "hf_mlp": s["hf_ratio"].mlp,
                      "hf_product": np.exp(lh.attn + lh.mlp).round(4), "log_err": (lh.whole - lh.attn - lh.mlp).round(4),
                      "size": (lh.attn.abs() + lh.mlp.abs()).round(4), "dchroma_whole": s["d_chroma"].whole,
                      "dchroma_sum": (s["d_chroma"].attn + s["d_chroma"].mlp).round(4), "layout_whole": s["layout_r"].whole,
                      "layout_attn": s["layout_r"].attn, "layout_mlp": s["layout_r"].mlp}).reset_index()
    e.to_csv(DATA / "split_atlas_additivity.csv", index=False)


def sheets(s, seed):
    out = c47.IMG_ROOT / s.FOLDER / "sheets"; out.mkdir(exist_ok=True)
    W, H, LW, TH = 192, 240, 70, 24
    cols = ["base", "attn+", "attn-", "mlp+", "mlp-", "whole+", "whole-"]
    for pid in s.PROMPTS:
        base = Image.open(s.f_base(pid, seed)).convert("RGB").resize((W, H))
        for q in range(4):
            sh = Image.new("RGB", (LW + W * 7, TH + H * 7), "white"); dr = ImageDraw.Draw(sh)
            for j, lab in enumerate(cols): dr.text((LW + j * W + 4, 4), lab, fill="black")
            for i, blk in enumerate(range(q * 7, q * 7 + 7)):
                dr.text((4, TH + i * H + H // 2), f"blk{blk:02d}", fill="black")
                sh.paste(base, (LW, TH + i * H))
                paths = dict(arms(s, pid, seed, blk))
                for j, lab in enumerate(cols[1:], 1):
                    part, sg = lab[:-1], {"+": "pos", "-": "neg"}[lab[-1]]
                    if part in paths:
                        sh.paste(Image.open(paths[part](sg)).convert("RGB").resize((W, H)), (LW + j * W, TH + i * H))
            sh.save(out / f"{pid}_seed{seed}_blk{q*7:02d}-{q*7+6:02d}.jpg", quality=88)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--band", action="store_true"); ap.add_argument("--tables", action="store_true")
    ap.add_argument("--sheets"); ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    import split_atlas as s
    if a.band: band(s)
    if a.tables: tables()
    if a.sheets: sheets(s, a.sheets)
