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



# ---------------------------------------------------------------- shared helpers

def _sheet(rows, cols, path_fn, caption_fn, out: Path, footer: str, W=150, H=188, LAB=132) -> Path:
    """Whole-frame contact sheet. rows: [(row_key, row_label)], cols: [(col_key, col_label)].
    path_fn(row_key, col_key) -> Path; caption_fn(row_key, col_key) -> (text, rgb) or None."""
    GAP, CAP, HEAD = 2, 18, 26
    cw = LAB + len(cols) * (W + GAP)
    chh = HEAD + len(rows) * (H + CAP + GAP) + 22
    S = Image.new("RGB", (cw, chh), SURF_RGB); d = ImageDraw.Draw(S)
    for j, (_, lab) in enumerate(cols):
        d.text((LAB + j * (W + GAP) + 4, 6), lab, fill=INK_RGB, font=font(12, True))
    for i, (rk, rl) in enumerate(rows):
        y = HEAD + i * (H + CAP + GAP)
        d.text((6, y + H // 2 - 8), rl, fill=INK_RGB, font=font(12))
        for j, (ck, _) in enumerate(cols):
            p = path_fn(rk, ck)
            if not p.exists():
                raise FileNotFoundError(p)
            x = LAB + j * (W + GAP)
            S.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y))
            cap = caption_fn(rk, ck)
            if cap:
                d.text((x + 4, y + H + 2), cap[0], fill=cap[1], font=font(11))
    d.text((6, chh - 18), footer, fill=DIM_RGB, font=font(10))
    out.parent.mkdir(parents=True, exist_ok=True)
    S.save(out, "WEBP", quality=86, method=6)
    return out


def _axes(fig, n, k):
    ax = fig.add_subplot(1, n, k); ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=7)
    return ax


def _ramp(i: int, n: int) -> str:
    """Sequential blue ramp for ordered depth (AUTHORING 4.4)."""
    t = i / max(n - 1, 1)
    r, g, b = int(0xb8 - t * (0xb8 - 0x1d)), int(0xd4 - t * (0xd4 - 0x4f)), int(0xf5 - t * (0xf5 - 0x91))
    return f"#{r:02x}{g:02x}{b:02x}"


# ---------------------------------------------------------------- 20-method

def edit_schema(out: Path) -> Path:
    """F20.1 — schema, no measured number: 28 blocks, one expanded, the multiplier."""
    S = Image.new("RGB", (1200, 420), SURF_RGB); d = ImageDraw.Draw(S)
    d.text((20, 14), "SCHEMA — how a single-block edit is built (no measured values)", fill=DIM_RGB, font=font(13, True))
    x0, y0, w, h = 40, 70, 36, 60
    bands = [(0, 1, "Base"), (2, 18, "Style"), (19, 22, "Details"), (23, 27, "Correction")]
    for b in range(28):
        x = x0 + b * (w + 4)
        col = (0x39, 0x87, 0xE5) if b == 23 else (0x3a, 0x3a, 0x38)
        d.rectangle([x, y0, x + w, y0 + h], fill=col)
        d.text((x + 8, y0 + h + 6), f"{b:02d}", fill=INK_RGB, font=font(11))
    for a, z, name in bands:
        xa, xz = x0 + a * (w + 4), x0 + z * (w + 4) + w
        d.line([xa, y0 - 12, xz, y0 - 12], fill=DIM_RGB, width=2)
        d.text((xa, y0 - 32), name, fill=DIM_RGB, font=font(11))
    d.text((40, 170), "block 23, expanded: 13 tensors, 8 of them 2-D and reachable by the tuner", fill=INK_RGB, font=font(13))
    tens = ["attn.wq", "attn.wk", "attn.wv", "attn.wo", "attn.gate", "mlp.up", "mlp.gate", "mlp.down"]
    for k, t in enumerate(tens):
        x = 40 + k * 140
        d.rectangle([x, 200, x + 128, 240], outline=(0x39, 0x87, 0xE5), width=2)
        d.text((x + 10, 212), t, fill=INK_RGB, font=font(12))
    d.text((40, 262), "every one of them is multiplied by the same factor:   W  ->  (1 + d) · W", fill=INK_RGB, font=font(15, True))
    d.text((40, 296), "d < 0 weakens the block's contribution, d > 0 strengthens it; d is the 'dose'.", fill=INK_RGB, font=font(12))
    d.text((40, 322), "The 1-D tensors (norm scales, modulation) are not reachable this way and stay as they are.", fill=INK_RGB, font=font(12))
    d.text((40, 348), "A preset is a vector of 34 such factors (28 blocks + 6 other sections); a single-block edit sets one.", fill=INK_RGB, font=font(12))
    d.text((40, 384), "Band names are Alessandro's labels from looking at the renders, not measurements.", fill=DIM_RGB, font=font(11))
    out.parent.mkdir(parents=True, exist_ok=True)
    S.save(out, "WEBP", quality=90, method=6)
    return out


# ---------------------------------------------------------------- 21-block-map

def layout_stability_by_block(out: Path) -> Path:
    """F21.1 — layout r with the baseline per block, both signs, 23 prompts."""
    rows = list(csv.DictReader(open(DATA / "block_colour_layout.csv")))
    by = {}
    for r in rows:
        b = int(r["block"][3:]); s = "pos" if float(r["dose"]) > 0 else "neg"
        by.setdefault((b, s), []).append(float(r["layout_r"]))
    fig, ax = _canvas(7.2, 3.2)
    for b in range(28):
        for k, s in enumerate(("neg", "pos")):
            v = statistics.mean(by[(b, s)])
            ax.bar(b + (k - 0.5) * 0.38, v, width=0.36, color=_ramp(b, 28), alpha=0.55 if s == "neg" else 1.0)
    ax.set_ylim(0.4, 1.0); ax.set_xticks(range(0, 28, 3))
    ax.set_xlabel("block (left bar negative dose, right bar positive)", color=DIM, fontsize=8)
    ax.set_ylabel("layout r with the baseline", color=DIM, fontsize=8)
    lo = min(range(28), key=lambda b: statistics.mean(by[(b, "pos")]))
    ax.annotate(f"blk{lo:02d} +", (lo + 0.2, statistics.mean(by[(lo, "pos")])), textcoords="offset points",
                xytext=(4, -12), color=INK, fontsize=7.5)
    ax.set_title("The ends keep the layout; the middle rewrites it", color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(left=0.1, right=0.98, top=0.88, bottom=0.18)
    n = len({r["prompt"] for r in rows})
    return _save(fig, out, f"{n} prompts (styles, v3, v4) · calibrated doses · L-channel correlation at 64x80 · "
                           f"source data/block_colour_layout.csv")


def residual_overlap_matrix(out: Path) -> Path:
    """F21.2 — residual signed correlation between positive arms (common mode removed)."""
    rows = list(csv.DictReader(open(DATA / "block_effect_overlap_mean.csv")))
    import numpy as np
    M = np.full((28, 28), np.nan)
    for r in rows:
        if r["arm_a"].endswith("_pos") and r["arm_b"].endswith("_pos"):
            a, b = int(r["arm_a"][3:5]), int(r["arm_b"][3:5]); v = float(r["resid_mean"])
            M[a, b] = M[b, a] = v
    fig, ax = _canvas(4.6, 4.2)
    im = ax.imshow(M, cmap="RdBu_r", vmin=-0.4, vmax=0.4)
    ax.set_xticks(range(0, 28, 3)); ax.set_yticks(range(0, 28, 3))
    ax.set_title("Positive arms that push the same way\n(after removing the shared part)", color=INK, fontsize=8.5, loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.04); cb.ax.tick_params(colors=DIM, labelsize=7)
    fig.subplots_adjust(left=0.1, right=0.92, top=0.86, bottom=0.08)
    return _save(fig, out, "styles bench, 12 prompts · data/block_effect_overlap_mean.csv")


def weights_vs_stability(out: Path) -> Path:
    """F21.3 — largest singular value of mlp.gate per block against layout stability."""
    W = {int(r["block"]): float(r["mlp.gate.sigma1"]) for r in csv.DictReader(open(DATA / "block_weight_structure.csv"))}
    lay = {}
    for r in csv.DictReader(open(DATA / "block_colour_layout.csv")):
        lay.setdefault(int(r["block"][3:]), []).append(float(r["layout_r"]))
    fig, ax = _canvas(5.4, 3.4)
    for b in range(28):
        y = statistics.mean(lay[b]); ax.scatter(W[b], y, color=_ramp(b, 28), s=22, zorder=3)
        if b in (8, 9, 23, 26, 27, 0):
            ax.annotate(f"{b:02d}", (W[b], y), textcoords="offset points", xytext=(4, 3), color=INK, fontsize=7)
    ax.set_xlabel("largest singular value of mlp.gate", color=DIM, fontsize=8)
    ax.set_ylabel("layout r with the baseline", color=DIM, fontsize=8)
    ax.set_title("The blocks that rewrite the picture have the strongest MLP-gate direction", color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(left=0.13, right=0.97, top=0.88, bottom=0.17)
    return _save(fig, out, "28 blocks · light = early, dark = late · data/block_weight_structure.csv")


# ---------------------------------------------------------------- 23-prompt-family

FAMS = [("F1cartoon", "cartoon"), ("F2oil", "oil"), ("F3photo", "photo")]
SUBJS = ["blacksmith", "rally", "fox", "stilllife", "fisherman", "lighthouse"]


def _family_sheet(arm: str, out: Path, seed: str = "5772156") -> Path:
    rows = [(s, s) for s in SUBJS]
    cols = []
    for f, fl in FAMS:
        cols += [((f, "baseline"), f"{fl} · base"), ((f, arm), f"{fl} · preset")]
    p = lambda s, c: IMG / "benchmark_prompt_family" / f"{c[0]}_{s}_{c[1]}_krea2_seed{seed}_00001_.png"
    return _sheet(rows, cols, p, lambda s, c: None, out,
                  f"arm {arm} · 6 subjects x 3 families · seed {seed} · whole frames · "
                  f"source data/prompt_family_plan.csv", W=130, H=163, LAB=92)


def family_sheet_combo(out: Path) -> Path:
    """F23.1 — the combo preset across six subjects and three families."""
    return _family_sheet("combo", out)


def family_sheet_blk09(out: Path) -> Path:
    """F23.2 — blk09 + across six subjects and three families."""
    return _family_sheet("blk09_pos_d0.450", out)


def family_coherence_by_family(out: Path) -> Path:
    """F23.3 — within-family coherence W per arm, split by family."""
    rows = list(csv.DictReader(open(DATA / "prompt_family_within_by_family.csv")))
    fig, ax = _canvas(7.2, 3.3)
    n = len(rows); w = 0.26
    for k, (col, lab) in enumerate((("W_F1cartoon", "cartoon"), ("W_F2oil", "oil"), ("W_F3photo", "photo"))):
        ax.bar([i + (k - 1) * w for i in range(n)], [float(r[col]) for r in rows], width=w * 0.95, color=CAT[k], label=lab)
    ax.set_xticks(range(n)); ax.set_xticklabels([r["arm"].replace("_d0.", " .").replace("_pos", " +").replace("_neg", " -") for r in rows],
                                                 rotation=35, ha="right", fontsize=6.5, color=DIM)
    ax.axhline(0, color=GRID, lw=0.8)
    ax.set_ylabel("within-family coherence W", color=DIM, fontsize=8)
    leg = ax.legend(frameon=False, fontsize=7, labelcolor=INK, loc="upper right")
    ax.set_title("Late blocks are coherent inside a family — most on cartoon, least on photographs",
                 color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(left=0.08, right=0.99, top=0.88, bottom=0.3)
    return _save(fig, out, "6 subjects x 2 seeds per family · cosine of 23-feature change vectors · "
                           "source data/prompt_family_within_by_family.csv")


def family_w_b_s(out: Path) -> Path:
    """F23.4 — W (within family), B (between families), S (seed floor) per arm."""
    rows = list(csv.DictReader(open(DATA / "prompt_family_arms.csv")))
    fig, ax = _canvas(7.2, 3.1)
    for i, r in enumerate(rows):
        W, B, S = float(r["W_within_family"]), float(r["B_between_families"]), float(r["S_seed"])
        ax.plot([i, i], [B, W], color=GRID, lw=2, zorder=1)
        ax.scatter([i], [S], marker="_", s=160, color=DIM, zorder=2)
        ax.scatter([i], [B], color=CAT[1], s=18, zorder=3)
        ax.scatter([i], [W], color=CAT[0], s=18, zorder=3)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([r["arm"].replace("_d0.", " .").replace("_pos", " +").replace("_neg", " -") for r in rows],
                       rotation=35, ha="right", fontsize=6.5, color=DIM)
    ax.set_ylabel("mean cosine", color=DIM, fontsize=8)
    ax.set_title("blue = within family (W), orange = between families (B), grey tick = across seeds (S)",
                 color=INK, fontsize=8.5, loc="left")
    fig.subplots_adjust(left=0.08, right=0.99, top=0.88, bottom=0.3)
    return _save(fig, out, "18 prompts x 2 seeds · 23 style features · source data/prompt_family_arms.csv")


# ---------------------------------------------------------------- 24-wording

def wording_sheet(out: Path) -> Path:
    """F24.1 — blk19 + on the elf, four writings and the content change, two seeds."""
    import analyze_prompt_writing as A
    arm = "blk19_pos_d0.350"
    labels = ["original", "reordered", "tags", "synonyms", "content changed"]
    rows = [(pid, lab) for pid, lab in zip(A.WRIT["S1"] + [A.CONTENT["S1"]], labels)]
    cols = [(("baseline", A.SEEDS[0]), f"base {A.SEEDS[0]}"), ((arm, A.SEEDS[0]), "blk19 +0.35"),
            (("baseline", A.SEEDS[1]), f"base {A.SEEDS[1]}"), ((arm, A.SEEDS[1]), "blk19 +0.35")]
    return _sheet(rows, cols, lambda pid, c: Path(A.path(pid, c[0], c[1])), lambda r, c: None, out,
                  "subject S1 (elf brawler) · whole frames · source data/prompt_writing_plan.csv")


def wording_consistency(out: Path) -> Path:
    """F24.2 — per scored arm: consistency across writings, seeds, content change, subjects."""
    rows = [r for r in csv.DictReader(open(DATA / "prompt_writing_arms.csv"))]
    size_w = 1.1547
    rows = [r for r in rows if float(r["size"]) > size_w]
    fig, ax = _canvas(7.2, 3.2)
    keys = [("A_content_small", "one object changed", CAT[2]), ("A_seed", "other seed", DIM),
            ("A_writing", "other writing", CAT[0]), ("A_subject", "other subject", CAT[1])]
    for k, (key, lab, col) in enumerate(keys):
        ax.scatter([i + (k - 1.5) * 0.12 for i in range(len(rows))], [float(r[key]) for r in rows], s=16, color=col, label=lab)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([r["arm"].replace("_d0.", " .").replace("_pos", " +").replace("_neg", " -") for r in rows],
                       rotation=35, ha="right", fontsize=6.5, color=DIM)
    ax.axhline(0, color=GRID, lw=0.8)
    ax.set_ylabel("cosine of the block's change", color=DIM, fontsize=8)
    ax.legend(frameon=False, fontsize=7, labelcolor=INK, ncol=4, loc="lower left")
    ax.set_title("A block does the same thing whatever the wording; the subject changes it", color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(left=0.08, right=0.99, top=0.88, bottom=0.3)
    return _save(fig, out, f"{len(rows)} arms larger than the writing-only change · 2 subjects x 2 seeds · "
                           f"source data/prompt_writing_arms.csv")


# ---------------------------------------------------------------- 25-standard-metrics

def depth_vs_cost(out: Path) -> Path:
    """F25.1 — per C49 arm: content kept (DINOv2 cosine) against quality cost (delta BRISQUE)."""
    rows = list(csv.DictReader(open(DATA / "standard_metrics_summary.csv")))
    dino, bris = {}, {}
    for r in rows:
        q = r["quantity"]
        if r["bench"] == "c49" and q.startswith("Q median dino_cos "):
            dino[q.split()[-1]] = float(r["value"])
        if r["bench"] == "c49" and q.startswith("Q median delta brisque "):
            bris[q.split()[-1]] = float(r["value"])
    fig, ax = _canvas(5.6, 3.6)
    for a in dino:
        late = a.startswith(("blk16", "blk20", "blk23", "blk26", "blk27")) or a == "combo"
        ax.scatter(dino[a], bris[a], color=CAT[0] if late else CAT[1], s=24, zorder=3)
        ax.annotate(a.replace("_d0.", " .").replace("_pos", " +").replace("_neg", " -"), (dino[a], bris[a]),
                    textcoords="offset points", xytext=(4, -10) if a.startswith("blk09") else (4, 3),
                    color=INK, fontsize=6.5)
    ax.set_xlim(min(dino.values()) - 0.006, max(dino.values()) + 0.02)
    ax.axhline(0, color=GRID, lw=0.8)
    ax.set_xlabel("DINOv2 cosine with the baseline (lower = content changed more)", color=DIM, fontsize=8)
    ax.set_ylabel("change in BRISQUE (higher = worse)", color=DIM, fontsize=8)
    ax.set_title("blue = late blocks and combo, orange = middle blocks", color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.17)
    return _save(fig, out, "medians over 18 prompts x 2 seeds · source data/standard_metrics_summary.csv")


# ---------------------------------------------------------------- 26-what-did-not-work

def destroyed_by_the_statistic(out: Path) -> Path:
    """F26.1 — the doses a statistic recommended, opened: Block_4 + and Block_1 + on P01, seed 2718281."""
    units = {(r["group"], r["sign"], r["dose"], r["prompt"]): r for r in csv.DictReader(open(DATA / "centre_push_units.csv"))}
    doses = ["0.080", "0.200", "0.350", "0.500"]
    rows = [("Block_4", "Block_4 +"), ("Block_1", "Block_1 +")]
    cols = [("baseline", "base")] + [(d, f"dose {d}") for d in doses]
    root = IMG / "benchmark_centre_push" / "renders"
    def p(g, c):
        return root / ("P01_baseline_krea2_seed2718281_00001_.png" if c == "baseline"
                       else f"P01_{g}pos_{c}_krea2_seed2718281_00001_.png")
    def cap(g, c):
        if c == "baseline":
            return None
        u = units[(g, "pos", c, "P01")]
        return (f"V {float(u['V']):.2f}  L {float(u['L']):.2f}", INK_RGB)
    return _sheet(rows, cols, p, cap, out, "P01 · seed 2718281 · V, L = the unit means (3 seeds) the retracted "
                                           "analysis ranked · data/centre_push_units.csv")



# ---------------------------------------------------------------- story figures (2026-10-05)

def three_knobs(out: Path) -> Path:
    """F20.2 — one picture, three single-block edits: saturation, realism, softness."""
    seed = "5772156"
    cols = [("baseline", "base"), ("blk23_neg_d0.300", "blk23 -0.30"), ("blk09_pos_d0.450", "blk09 +0.45"),
            ("blk27_neg_d0.250", "blk27 -0.25")]
    rows = [("F1cartoon_fox", "cartoon fox"), ("F2oil_lighthouse", "oil lighthouse")]
    p = lambda r, c: IMG / "benchmark_prompt_family" / f"{r}_{c}_krea2_seed{seed}_00001_.png"
    return _sheet(rows, cols, p, lambda r, c: None, out,
                  f"seed {seed} · whole frames · one block changed per column · source data/prompt_family_plan.csv",
                  W=230, H=288, LAB=110)


V4_EYE = ["OK", "VWA", "WA", "SA", "VSA", "BROKEN"]


def sensitivity_map(out: Path) -> Path:
    """F21.4 — artefact onset by eye at dose +-0.350, every block and sign."""
    rows = list(csv.DictReader(open(DATA / "single_blocks_eye_artifacts_alessandro.csv")))
    lab = {(int(r["block"]), r["sign"]): r["label_verbatim"].split(" ")[0] for r in rows}
    import matplotlib.colors as mcolors
    cmap = ["#2a3b2e", "#3f5a3a", "#8a7a2c", "#b0602a", "#b8402c", "#c42a2a"]
    fig, ax = _canvas(7.4, 2.2)
    for b in range(28):
        for k, sgn in enumerate(("neg", "pos")):
            L = lab[(b, sgn)]
            ax.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle(
                (b - 0.46, 1 - k - 0.42), 0.92, 0.84, color=cmap[V4_EYE.index(L)]))
            ax.text(b, 1 - k, "" if L == "OK" else ("BRK" if L == "BROKEN" else L), ha="center", va="center",
                    color=INK, fontsize=5.6)
    ax.set_xlim(-0.6, 27.6); ax.set_ylim(-0.6, 1.6)
    ax.set_yticks([1, 0]); ax.set_yticklabels(["negative", "positive"], color=DIM, fontsize=7.5)
    ax.set_xticks(range(0, 28, 3)); ax.set_xlabel("block", color=DIM, fontsize=8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("At the same dose the middle of the stack shows no artefact; the output end breaks first",
                 color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(left=0.1, right=0.99, top=0.82, bottom=0.25)
    return _save(fig, out, "dose 0.350 · 3 prompts · 1 seed · eye labels, blank = OK, then VWA, WA, SA, BRK = BROKEN · "
                           "source data/single_blocks_eye_artifacts_alessandro.csv")


def _v4_dose(block: int, sign: str) -> str:
    for r in csv.DictReader(open(DATA / "single_blocks_v4_plan.csv", encoding="utf-8-sig")):
        if r["block_idx"] and int(r["block_idx"]) == block and r["sign"] == sign:
            return f"{abs(float(r['dose'])):.3f}"
    raise KeyError((block, sign))


def _guide(prompt: str, out: Path) -> Path:
    W, H, GAP, CAP = 104, 130, 2, 16
    PAIR = 2 * W + GAP + 14
    per_row, LAB = 7, 8
    seed = "1234567"
    root = IMG / "benchmark_single_blocks_v4" / "renders"
    nrows = 1 + 28 // per_row
    cw = LAB + per_row * PAIR
    chh = 26 + nrows * (H + CAP + 20) + 22
    S = Image.new("RGB", (cw, chh), SURF_RGB); d = ImageDraw.Draw(S)
    d.text((LAB, 6), f"{prompt.replace('_', ' ')} · each pair: block pushed negative | positive", fill=INK_RGB,
           font=font(12, True))
    y0 = 26
    S.paste(Image.open(root / f"{prompt}_baseline_krea2_seed{seed}_00001_.png").convert("RGB").resize((W, H), Image.LANCZOS),
            (LAB, y0 + 16))
    d.text((LAB, y0), "baseline", fill=INK_RGB, font=font(11, True))
    bands = [(0, 1, "Base"), (2, 18, "Style"), (19, 22, "Details"), (23, 27, "Correction")]
    for b in range(28):
        r, c = 1 + b // per_row, b % per_row
        x = LAB + c * PAIR; y = y0 + r * (H + CAP + 20)
        band = next(n for a, z, n in bands if a <= b <= z)
        dn, dp = _v4_dose(b, "neg"), _v4_dose(b, "pos")
        d.text((x, y), f"blk{b:02d} · {band}", fill=INK_RGB, font=font(11, True))
        for k, (sgn, dose) in enumerate((("neg", dn), ("pos", dp))):
            f = root / f"{prompt}_blk{b:02d}_{sgn}_d{dose}_krea2_seed{seed}_00001_.png"
            if not f.exists():
                raise FileNotFoundError(f)
            S.paste(Image.open(f).convert("RGB").resize((W, H), Image.LANCZOS), (x + k * (W + GAP), y + 16))
            d.text((x + k * (W + GAP) + 3, y + 16 + H + 1), ("-" if sgn == "neg" else "+") + dose.rstrip("0"),
                   fill=NEG if sgn == "neg" else POS, font=font(10))
    d.text((6, chh - 18), f"benchmark_single_blocks_v4 · seed {seed} · doses of the v4 plan · whole frames · "
                          f"source data/single_blocks_v4_plan.csv", fill=DIM_RGB, font=font(10))
    out.parent.mkdir(parents=True, exist_ok=True)
    S.save(out, "WEBP", quality=86, method=6)
    return out


def guide_comic(out: Path) -> Path:
    """F21.5 — every block, both signs, on the comic page of v4."""
    return _guide("P5_comic_panels", out)


def guide_crown(out: Path) -> Path:
    """F21.6 — every block, both signs, on the crown seen from above."""
    return _guide("P1_crown_topdown", out)


def blk23_everywhere(out: Path) -> Path:
    """F22.4 — blk23 at its two strongest doses on all eight prompts."""
    rows = [("b23_m0.450", "blk23 -0.45"), ("baseline", "base"), ("b23_p0.300", "blk23 +0.30")]
    cols = [(pid, pid.split("_", 1)[1]) for pid in C47_SEED_A]
    m = _measures_c47()
    p = lambda r, c: IMG / "benchmark_blk23_colorful" / f"{c}_{r}_krea2_seed{C47_SEED_A[c]}_00001_.png"
    def cap(r, c):
        if r == "baseline":
            return None
        dc = float(m[(c, C47_SEED_A[c], r)]["d_chroma"])
        return (f"chroma {dc:+.1f}", POS if dc > 0 else NEG)
    return _sheet(rows, cols, p, cap, out, "8 prompts · original seed of each · whole frames · "
                                           "source data/blk23_colorful_measures.csv", W=128, H=160, LAB=96)


def blacksmith_identity(out: Path) -> Path:
    """F23.5 — the blacksmith under blk09 +0.45, both seeds, three families."""
    rows = [("5772156", "seed 5772156"), ("1414213", "seed 1414213")]
    cols = []
    for f, fl in FAMS:
        cols += [((f, "baseline"), f"{fl} · base"), ((f, "blk09_pos_d0.450"), f"{fl} · blk09 +")]
    p = lambda s, c: IMG / "benchmark_prompt_family" / f"{c[0]}_blacksmith_{c[1]}_krea2_seed{s}_00001_.png"
    _sheet(rows, cols, p, lambda s, c: None, out,
           "blacksmith prompt · blk09 +0.45 · rows 1-2 whole frames, row 3 the face at seed 1414213 enlarged · "
           "source data/prompt_family_plan.csv", W=150, H=188, LAB=100)
    S = Image.open(out).convert("RGB")
    W, GAP, LAB = 150, 2, 100
    band = Image.new("RGB", (S.width, W + 30), SURF_RGB); d = ImageDraw.Draw(band)
    d.text((6, W // 2), "face, 1414213", fill=INK_RGB, font=font(12))
    for j, c in enumerate(cols):
        im = Image.open(p("1414213", c[0])).convert("RGB").crop((250, 150, 800, 700)).resize((W, W), Image.LANCZOS)
        band.paste(im, (LAB + j * (W + GAP), 4))
    top = S.crop((0, 0, S.width, S.height - 22)); foot = S.crop((0, S.height - 22, S.width, S.height))
    T = Image.new("RGB", (S.width, top.height + band.height + foot.height), SURF_RGB)
    T.paste(top, (0, 0)); T.paste(band, (0, top.height)); T.paste(foot, (0, top.height + band.height))
    T.save(out, "WEBP", quality=86, method=6)
    return out


def atlas_ends_and_middle(out: Path) -> Path:
    """F12.1 — the equal-dose atlas: three prompts, the two ends against two middle blocks."""
    rows = [("P01_blacksmith", "blacksmith"), ("S1_rally", "rally"), ("F4_closeup", "close-up")]
    cols = [("baseline", "base"), ("blk00_pos", "blk00 +"), ("blk09_pos", "blk09 +"), ("blk13_pos", "blk13 +"),
            ("blk25_pos", "blk25 +"), ("blk27_pos", "blk27 +")]
    root = IMG / "benchmark_single_blocks_atlas" / "renders"
    p = lambda r, c: root / (f"{r}_baseline_krea2_seed2718281_00001_.png" if c == "baseline"
                             else f"{r}_{c}_d0.350_krea2_seed2718281_00001_.png")
    return _sheet(rows, cols, p, lambda r, c: None, out,
                  "benchmark_single_blocks_atlas · dose 0.350 for every block · seed 2718281 · whole frames · "
                  "source data/single_blocks_atlas_plan.csv", W=150, H=188, LAB=90)

# ---------------------------------------------------------------- 28-portrait-preset

PORTRAIT_CHARS = [("H3_halfling_druid", "halfling · new"), ("R6_dragonborn_cleric", "dragonborn · new"),
                  ("T7_tiefling_bard", "tiefling · new"), ("D1_dwarf_paladin", "dwarf"),
                  ("E2_elf_rogue", "elf"), ("O4_halforc_fighter", "half-orc"), ("G5_gnome_wizard", "gnome")]


def _phase_c(char: str, cond: str, seed: str) -> Path:
    return IMG / "benchmark_portraits" / "phase_c" / f"{char}_{cond}_krea2_seed{seed}_00001_.png"


def portrait_preset_sheet(out: Path) -> Path:
    """F28.1 — the frozen portrait preset on all seven characters at one seed; the first three never seen."""
    rows = [("baseline", "base"), ("preset", "preset")]
    return _sheet(rows, PORTRAIT_CHARS, lambda r, c: _phase_c(c, r, "2645751"), lambda r, c: None, out,
                  "benchmark_portraits/phase_c · seed 2645751 · preset presets/portrait_preset_alessandro.json · "
                  "'new' = held out, never seen while the preset was tuned · whole frames · "
                  "source data/portraits_preset_plan.csv", W=176, H=220, LAB=62)


def portrait_blind_and_faces(out: Path) -> Path:
    """F28.2 — left: the blind observer's choices; right: ArcFace similarity by kind of pair."""
    import itertools
    import numpy as np
    key = {r["sheet"]: r for r in csv.DictReader(open(DATA / "portrait_preset_blind_key.csv"))}
    ans = list(csv.DictReader(open(DATA / "portrait_preset_blind_answers_human.csv")))
    cells = {}
    for a in ans:
        k = key[a["sheet"]]
        c = cells.setdefault((k["group"], k["set"]), [0, 0])
        c[0] += a["q1"] == k["preset_side"]; c[1] += 1
    faces = [r for r in csv.DictReader(open(DATA / "portrait_preset_faces.csv")) if r["detected"] == "1"]
    emb = {(r["char"], r["cond"], r["seed"]): np.array([float(x) for x in r["emb"].split()]) for r in faces}
    cos = lambda u, v: float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v)))
    base = [k for k in emb if k[1] == "baseline"]
    same, other = [], []
    for a, b in itertools.combinations(base, 2):
        (same if a[0] == b[0] else other).append(cos(emb[a], emb[b]))
    edit = [cos(emb[k], emb[(k[0], "preset", k[2])]) for k in base if (k[0], "preset", k[2]) in emb]
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.4, 3.5), dpi=150); fig.patch.set_facecolor(SURFACE)
    ax = _axes(fig, 2, 1)
    order = [("held_out", "original"), ("held_out", "mirrored"), ("calibration", "original"), ("calibration", "mirrored")]
    labs = ["held out\noriginal", "held out\nmirrored", "calibration\noriginal", "calibration\nmirrored"]
    for i, o in enumerate(order):
        hit, n = cells[o]
        ax.bar(i, hit / n, color=CAT[0] if o[0] == "held_out" else CAT[2], width=0.62)
        ax.text(i, hit / n + 0.03, f"{hit}/{n}", ha="center", color=INK, fontsize=8)
    ax.axhline(0.5, color=DIM, lw=0.8, ls="--"); ax.text(3.45, 0.52, "chance", color=DIM, fontsize=7, ha="right")
    ax.set_xticks(range(4)); ax.set_xticklabels(labs, color=DIM, fontsize=7); ax.set_ylim(0, 1.15)
    ax.set_ylabel("share of sheets where the preset was chosen", color=DIM, fontsize=7.5)
    ax.set_title("blind observer: which looks more American comic / animation?", color=INK, fontsize=8.5, loc="left")
    ax = _axes(fig, 2, 2)
    groups = [(same, "same character,\nanother seed"), (edit, "base vs preset,\nsame seed"),
              (other, "different\ncharacters")]
    rng = np.random.default_rng(0)
    for i, (v, lab) in enumerate(groups):
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=6, color=[CAT[0], CAT[1], DIM][i], alpha=0.7, lw=0)
        m = statistics.mean(v)
        ax.plot([i - 0.28, i + 0.28], [m, m], color=INK, lw=1.4)
        ax.text(i + 0.31, m, f"{m:.2f}\n(n={len(v)})", color=INK, fontsize=7, va="center")
    ax.set_xticks(range(3)); ax.set_xticklabels([g[1] for g in groups], color=DIM, fontsize=7)
    ax.set_xlim(-0.5, 2.9); ax.set_ylim(-0.1, 1.0)
    ax.set_ylabel("ArcFace cosine similarity of the face", color=DIM, fontsize=7.5)
    ax.set_title("the preset moves the face a little more than a seed does", color=INK, fontsize=8.5, loc="left")
    fig.subplots_adjust(left=0.07, right=0.98, top=0.88, bottom=0.2, wspace=0.28)
    return _save(fig, out, "left: 56 sheets, one observer blind to condition · right: faces ArcFace detected, lines = means · "
                           "source data/portrait_preset_blind_answers_human.csv, data/portrait_preset_faces.csv")


def portrait_blind_sheet(out: Path) -> Path:
    """F28.3 — one blind sheet exactly as the observer saw it (held-out halfling), with the key below."""
    sheet = "sheet_8250"
    k = {r["sheet"]: r for r in csv.DictReader(open(DATA / "portrait_preset_blind_key.csv"))}[sheet]
    a = {r["sheet"]: r for r in csv.DictReader(open(DATA / "portrait_preset_blind_answers_human.csv"))}[sheet]
    im = Image.open(IMG / "benchmark_portraits" / "blind" / f"{sheet}.png").convert("RGB")
    im = im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS)
    M = 12                                   # dark margin: the sheet's own grey header stays inside
    S = Image.new("RGB", (im.width + 2 * M, im.height + 46 + M), SURF_RGB); S.paste(im, (M, M))
    d = ImageDraw.Draw(S); im_h = im.height + M
    d.text((6, im_h + 6), f"key, revealed after all answers: preset on the {k['preset_side']} · "
           f"{k['char']} · seed {k['seed']} · {k['set']} set · her answer: {a['q1']}, same character: {a['q2']}",
           fill=INK_RGB, font=font(11))
    d.text((6, im_h + 26), f"{sheet} as shown · source data/portrait_preset_blind_key.csv, "
           "data/portrait_preset_blind_answers_human.csv", fill=DIM_RGB, font=font(10))
    out.parent.mkdir(parents=True, exist_ok=True)
    S.save(out, "WEBP", quality=88, method=6)
    return out


BUILDERS = {
    "F20.1": ("20-method", "edit_schema", edit_schema),
    "F21.1": ("21-block-map", "layout_stability_by_block", layout_stability_by_block),
    "F21.2": ("21-block-map", "residual_overlap_matrix", residual_overlap_matrix),
    "F21.3": ("21-block-map", "weights_vs_stability", weights_vs_stability),
    "F23.1": ("23-prompt-family-presets", "family_sheet_combo", family_sheet_combo),
    "F23.2": ("23-prompt-family-presets", "family_sheet_blk09", family_sheet_blk09),
    "F23.3": ("23-prompt-family-presets", "family_coherence_by_family", family_coherence_by_family),
    "F23.4": ("23-prompt-family-presets", "family_w_b_s", family_w_b_s),
    "F24.1": ("24-wording", "wording_sheet", wording_sheet),
    "F24.2": ("24-wording", "wording_consistency", wording_consistency),
    "F25.1": ("25-standard-metrics", "depth_vs_cost", depth_vs_cost),
    "F26.1": ("26-what-did-not-work", "destroyed_by_the_statistic", destroyed_by_the_statistic),
    "F22.1": ("22-saturation-knob", "saturation_ladder_sheet", saturation_ladder_sheet),
    "F22.2": ("22-saturation-knob", "saturation_dose_response", saturation_dose_response),
    "F22.3": ("22-saturation-knob", "matched_chroma_pairs", matched_chroma_pairs),
    "F20.2": ("20-method", "three_knobs", three_knobs),
    "F21.4": ("21-block-map", "sensitivity_map", sensitivity_map),
    "F21.5": ("21-block-map", "guide_comic", guide_comic),
    "F21.6": ("21-block-map", "guide_crown", guide_crown),
    "F22.4": ("22-saturation-knob", "blk23_everywhere", blk23_everywhere),
    "F23.5": ("23-prompt-family-presets", "blacksmith_identity", blacksmith_identity),
    "F12.1": ("12-single-blocks", "atlas_ends_and_middle", atlas_ends_and_middle),
    "F12.2": ("12-single-blocks", "sensitivity_map", sensitivity_map),
    "F13.1": ("13-pushing-harder", "destroyed_by_the_statistic", destroyed_by_the_statistic),
    "F28.1": ("28-portrait-preset", "portrait_preset_sheet", portrait_preset_sheet),
    "F28.2": ("28-portrait-preset", "portrait_blind_and_faces", portrait_blind_and_faces),
    "F28.3": ("28-portrait-preset", "portrait_blind_sheet", portrait_blind_sheet),
}


def main() -> int:
    import sys
    only = set(sys.argv[1:])
    for fid, (page, name, fn) in BUILDERS.items():
        if only and fid not in only:
            continue
        out = ASSETS / page / f"{fid}_{name}.webp"
        fn(out)
        print("built", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
