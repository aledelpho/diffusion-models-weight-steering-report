# -*- coding: utf-8 -*-
"""
experiments/results_figures.py

Figure builders for the results notebook (results/*.md), under the same contract as the
exploratory notebook (notebook/AUTHORING.md section 4): numbers come from one file under
data/, captions are derived from the rows drawn, whole frames only, dark surface, provenance
strip under every figure.

    python experiments/results_figures.py            # build every results figure
"""
from __future__ import annotations

import csv
import os
import statistics
from pathlib import Path

from PIL import Image, ImageDraw

from notebook_charts import _canvas, _save, CAT, INK, DIM, GRID, SURFACE
from notebook_figures import font, SURFACE as SURF_RGB, INK as INK_RGB, DIM as DIM_RGB, POS, NEG, ACC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
IMG = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img")
if not IMG.exists():
    IMG = Path(os.path.expanduser("~/mnt"))

C47_COLS = [("baseline", "base"), ("txtpos", "\"colorful\""), ("b23_m0.450", "blk23 -0.45"),
            ("b23_m0.300", "blk23 -0.30"), ("b23_m0.150", "blk23 -0.15"), ("b23_p0.150", "blk23 +0.15"),
            ("b23_p0.300", "blk23 +0.30"), ("txtneg", "\"muted\"")]
C47_SEED_A = {"E1_cartoon": "2718281", "E3_oil": "2718281", "E7_sepiaphoto": "2718281", "C2_rally": "2718281",
              "C3_fox": "2718281", "C4_stilllife": "2718281", "P3_archerforest": "3141592", "P4_selfie": "1618033"}


def _measures_c47() -> dict:
    return {(r["prompt"], r["seed"], r["cond"]): r for r in csv.DictReader(open(DATA / "blk23_colorful_measures.csv"))}


def saturation_ladder_sheet(out: Path) -> Path:
    """F22.1 — every prompt at its original seed, whole frames, one column per condition.
    Caption under each panel: chroma change against the baseline, read from the measurement file."""
    m = _measures_c47()
    W, H, GAP, CAP, LAB, HEAD = 150, 188, 2, 18, 132, 26
    rows = list(C47_SEED_A.items())
    cw = LAB + len(C47_COLS) * (W + GAP)
    chh = HEAD + len(rows) * (H + CAP + GAP) + 22
    S = Image.new("RGB", (cw, chh), SURF_RGB); d = ImageDraw.Draw(S)
    for j, (_, lab) in enumerate(C47_COLS):
        d.text((LAB + j * (W + GAP) + 4, 6), lab, fill=INK_RGB, font=font(12, True))
    for i, (pid, seed) in enumerate(rows):
        y = HEAD + i * (H + CAP + GAP)
        d.text((6, y + H // 2 - 8), pid.replace("_", " "), fill=INK_RGB, font=font(12))
        for j, (cond, _) in enumerate(C47_COLS):
            p = IMG / "benchmark_blk23_colorful" / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"
            if not p.exists():
                raise FileNotFoundError(p)
            x = LAB + j * (W + GAP)
            S.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y))
            if cond != "baseline":
                dc = float(m[(pid, seed, cond)]["d_chroma"])
                col = POS if dc > 0 else NEG
                d.text((x + 4, y + H + 2), f"chroma {dc:+.1f}", fill=col, font=font(11))
    d.text((6, chh - 18), "8 prompts · original seed of each · whole frames · chroma = mean CIELAB chroma change "
                          "vs the baseline · source data/blk23_colorful_measures.csv", fill=DIM_RGB, font=font(10))
    out.parent.mkdir(parents=True, exist_ok=True)
    S.save(out, "WEBP", quality=86, method=6)
    return out


def saturation_dose_response(out: Path) -> Path:
    """F22.2 — chroma change against blk23 dose, one line per prompt x seed (16), median bold."""
    m = _measures_c47()
    doses = [(-0.45, "b23_m0.450"), (-0.30, "b23_m0.300"), (-0.15, "b23_m0.150"), (0.0, "baseline"),
             (0.15, "b23_p0.150"), (0.30, "b23_p0.300")]
    cells = sorted({(p, s) for p, s, _ in m})
    fig, ax = _canvas(6.4, 3.6)
    ys_all = []
    for p, s in cells:
        ys = [0.0 if c == "baseline" else float(m[(p, s, c)]["d_chroma"]) for _, c in doses]
        ys_all.append(ys)
        ax.plot([x for x, _ in doses], ys, color=DIM, lw=0.8, alpha=0.6)
    med = [statistics.median(col) for col in zip(*ys_all)]
    ax.plot([x for x, _ in doses], med, color=CAT[0], lw=2.4, marker="o", ms=4)
    for x, y in zip([x for x, _ in doses], med):
        ax.annotate(f"{y:+.1f}", (x, y), textcoords="offset points", xytext=(4, 6), color=INK, fontsize=7.5)
    ax.axhline(0, color=GRID, lw=0.8); ax.axvline(0, color=GRID, lw=0.8)
    ax.set_xlabel("blk23 dose (negative = more saturated)", color=DIM, fontsize=8)
    ax.set_ylabel("chroma change vs baseline", color=DIM, fontsize=8)
    mono = sum(all(a > b for a, b in zip(ys, ys[1:])) for ys in ys_all)
    ax.set_title(f"Chroma falls monotonically along the ladder in {mono} of {len(cells)} cells",
                 color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(left=0.11, right=0.98, top=0.88, bottom=0.2)
    return _save(fig, out, f"16 cells = 8 prompts x 2 seeds · thin = one cell, bold = median · "
                           f"source data/blk23_colorful_measures.csv")


def matched_chroma_pairs(out: Path) -> Path:
    """F22.3 — at the words' chroma gain: layout r, LPIPS and DINOv2 cosine of the words and of blk23
    interpolated at the same gain, for the scorable cells."""
    rows = [r for r in csv.DictReader(open(DATA / "blk23_matched_chroma.csv")) if r["scorable"] == "1"]
    fig, axes = _canvas(7.2, 3.0)
    fig.clf()
    specs = [("layout_r", "layout r (higher = closer)"), ("lpips", "LPIPS (lower = closer)"),
             ("dino_cos", "DINOv2 cosine (higher = closer)")]
    for k, (key, lab) in enumerate(specs):
        ax = fig.add_subplot(1, 3, k + 1); ax.set_facecolor(SURFACE)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=DIM, labelsize=7)
        win = 0
        for r in rows:
            t, b = float(r[f"text_{key}"]), float(r[f"blk23_{key}"])
            better = b < t if key == "lpips" else b > t
            win += better
            ax.plot([0, 1], [t, b], color=CAT[2] if better else CAT[1], lw=1.2, marker="o", ms=3)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["\"colorful\"", "blk23"], color=DIM, fontsize=7.5)
        ax.set_xlim(-0.3, 1.3)
        ax.set_title(f"{lab}\nblk23 closer in {win} of {len(rows)}", color=INK, fontsize=8, loc="left")
    fig.subplots_adjust(left=0.07, right=0.99, top=0.78, bottom=0.18, wspace=0.45)
    return _save(fig, out, f"{len(rows)} of 16 cells where blk23 reaches the words' chroma gain · "
                           f"green = blk23 closer to the baseline · source data/blk23_matched_chroma.csv")


BUILDERS = {
    "F22.1": ("22-saturation-knob", "saturation_ladder_sheet", saturation_ladder_sheet),
    "F22.2": ("22-saturation-knob", "saturation_dose_response", saturation_dose_response),
    "F22.3": ("22-saturation-knob", "matched_chroma_pairs", matched_chroma_pairs),
}


def main() -> int:
    for fid, (page, name, fn) in BUILDERS.items():
        out = ASSETS / page / f"{fid}_{name}.webp"
        fn(out)
        print("built", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
