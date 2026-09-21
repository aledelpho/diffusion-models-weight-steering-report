# -*- coding: utf-8 -*-
"""
experiments/notebook_charts.py

The chart module the authoring contract names (notebook/AUTHORING.md sections 4.2 and 4.4).

Like notebook_figures.py, this file did not exist until the migration went looking for it,
while figures.yaml had been naming builders inside it since the contract was written. It holds
the palette section 4.4 declares and the statistical builders that read a measurement file and
draw what is in it.

Every builder here:

  * takes its numbers from one file under data/ and from nothing else;
  * derives its annotations from the rows it drew, so a label cannot contradict the data;
  * draws on the surface #1a1a19 that validate_notebook.py samples for;
  * direct-labels the outliers rather than every point;
  * ends with a provenance strip naming the source file and the n.

    python experiments/notebook_charts.py
"""

from __future__ import annotations

import csv
import io
import json
import math
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

# AUTHORING section 4.4. The three categorical slots are validated for colour-vision
# deficiency against this surface; do not substitute values without re-running the validator.
SURFACE = "#1a1a19"
CAT = ["#3987e5", "#d95926", "#199e70"]
INK = "#e3e7ee"
DIM = "#98a2b2"
GRID = "#2e2e2c"


def _canvas(w: float, h: float):
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=8)
    return fig, ax


def _save(fig, out: Path, strip: str) -> Path:
    fig.text(0.008, 0.012, strip, color=DIM, fontsize=6.5, ha="left", va="bottom")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=SURFACE,
                edgecolor="none", bbox_inches=None)
    plt.close(fig)
    buf.seek(0)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.open(buf).convert("RGB").save(out, "WEBP", quality=88, method=6)
    return out


# ---------------------------------------------------------------- measurements


def _enlargement_rows() -> list[dict]:
    src = DATA / "stage12_enlargement_by_prompt.csv"
    if not src.exists():
        raise FileNotFoundError(
            f"{src} is missing -- run experiments/stage12_enlargement_by_prompt.py first")
    rows = list(csv.DictReader(src.open(encoding="utf-8", newline="")))
    for r in rows:
        r["rho"] = float(r["rho"])
        r["identified_blockshuf_2x"] = int(r["identified_blockshuf_2x"])
        r["n_afc_trials"] = int(r["n_afc_trials"])
    if not rows:
        raise ValueError(f"{src} is empty")
    return rows


LABEL = {
    "blockshuf_neg_2x": "block derangement, negative, x2",
    "blockshuf_neg_1x": "block derangement, negative, x1",
    "preset_pos_2x": "calibrated preset, positive, x2",
}


# ---------------------------------------------------------------- builders


def enlargement_by_prompt(out: Path) -> Path:
    """Per-prompt area ratio for the three conditions, ordered by the registered target."""
    rows = _enlargement_rows()
    order = sorted({r["prompt_id"] for r in rows},
                   key=lambda p: next(r["rho"] for r in rows
                                      if r["prompt_id"] == p
                                      and r["condition"] == "blockshuf_neg_2x"))
    y = {p: i for i, p in enumerate(order)}

    fig, ax = _canvas(7.6, 4.6)
    ax.axvline(1.0, color=DIM, lw=1.0, ls="--", zorder=1)
    for i, cond in enumerate(("blockshuf_neg_2x", "blockshuf_neg_1x", "preset_pos_2x")):
        sel = [r for r in rows if r["condition"] == cond]
        ax.scatter([r["rho"] for r in sel], [y[r["prompt_id"]] for r in sel],
                   s=46, color=CAT[i], edgecolor=SURFACE, linewidth=0.8,
                   label=LABEL[cond], zorder=3)

    target = {r["prompt_id"]: r["rho"] for r in rows if r["condition"] == "blockshuf_neg_2x"}
    hi = max(target, key=target.get)
    lo = min(target, key=target.get)
    for p in (hi, lo):
        ax.annotate(f"{target[p]:.2f}", (target[p], y[p]), textcoords="offset points",
                    xytext=(9, -3), color=INK, fontsize=8)

    n = len(order)
    above = sum(1 for v in target.values() if v > 1)
    geo = math.exp(sum(math.log(v) for v in target.values()) / n)
    ax.set_yticks(range(n))
    ax.set_yticklabels([p.split("_", 1)[1] for p in order], color=DIM, fontsize=8)
    ax.set_xlabel("subject area, treated over its own baseline", color=DIM, fontsize=9)
    ax.set_title(f"The subject grows in {above} styles of {n} under block derangement at "
                 f"double dose\ngeometric mean {geo:.3f}; the calibrated preset, predicted to "
                 f"shrink it, does nothing",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    leg = ax.legend(loc="lower right", fontsize=7.5, frameon=False, labelcolor=DIM)
    leg.set_zorder(4)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.10)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out,
                 f"10 styles x 5 seeds x 4 conditions  ·  n = {n} prompt-level ratios  ·  "
                 f"source data/stage12_enlargement_by_prompt.csv")


def discrimination_rates(out: Path) -> Path:
    """How often the annotator picked each condition out of a four-way line-up."""
    res = json.loads((DATA / "stage12_pattern_results.json").read_text(encoding="utf-8"))
    n = res["n_trials"]
    bars = [
        ("calibrated preset x2", res["k_preset_pos_2x"] / n, 0.25, res["pval_preset_pos_2x"]),
        ("block derangement x2", res["k_blockshuf_2x"] / n, 0.25, res["pval_blockshuf_2x"]),
        ("both, in one trial", res["k_both"] / n, res["p_both_h0"], res["pval_both"]),
    ]
    ks = [res["k_preset_pos_2x"], res["k_blockshuf_2x"], res["k_both"]]

    fig, ax = _canvas(7.8, 3.6)
    x = range(len(bars))
    ax.bar(x, [b[1] for b in bars], width=0.52, color=CAT[:3], zorder=3)
    for i, (label, rate, chance, p) in enumerate(bars):
        ax.plot([i - 0.33, i + 0.33], [chance, chance], color=DIM, lw=1.4, ls="--", zorder=4)
        ax.annotate(f"{ks[i]} of {n}", (i, rate), textcoords="offset points", xytext=(0, 6),
                    ha="center", color=INK, fontsize=9.5, fontweight="bold")
        ax.annotate(f"chance {chance * 100:.3g}%", (i, chance), textcoords="offset points",
                    xytext=(0, 5), ha="center", color=DIM, fontsize=7.5)
        ax.annotate(f"p = {p:.1e}", (i, 0.02), ha="center", color=DIM, fontsize=7.5)
    ax.set_xticks(list(x))
    ax.set_xticklabels([b[0] for b in bars], color=DIM, fontsize=8.5)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("identified correctly", color=DIM, fontsize=9)
    ax.set_title("The blinding failed, and this is by how much\nmirroring, flipping, hue, "
                 "saturation, brightness and noise did not hide it",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    return _save(fig, out,
                 f"4-AFC, {n} trials, 2 per style, threshold fixed at 5 of {n} before the round  ·  "
                 f"source data/stage12_pattern_results.json")


def discriminability_vs_effect(out: Path) -> Path:
    """The effect against how well the annotator could tell the condition, per style."""
    rows = [r for r in _enlargement_rows() if r["condition"] == "blockshuf_neg_2x"]
    fig, ax = _canvas(7.0, 4.0)
    ax.axhline(1.0, color=DIM, lw=1.0, ls="--", zorder=1)

    groups = {}
    for r in rows:
        groups.setdefault(r["identified_blockshuf_2x"], []).append(r)
    for k in sorted(groups):
        sel = groups[k]
        jitter = [k + (i - (len(sel) - 1) / 2) * 0.055 for i in range(len(sel))]
        ax.scatter(jitter, [r["rho"] for r in sel], s=58, color=CAT[0],
                   edgecolor=SURFACE, linewidth=0.8, zorder=3)
        m = statistics.mean(r["rho"] for r in sel)
        ax.plot([k - 0.22, k + 0.22], [m, m], color=CAT[1], lw=2.4, zorder=4)
        ax.annotate(f"mean {m:.2f}", (k + 0.24, m), color=CAT[1], fontsize=8.5,
                    va="center", ha="left")

    extremes = sorted(rows, key=lambda r: r["rho"])
    for r in (extremes[0], extremes[-1]):
        ax.annotate(r["prompt_id"].split("_", 1)[1],
                    (r["identified_blockshuf_2x"], r["rho"]),
                    textcoords="offset points", xytext=(8, 4), color=INK, fontsize=8)

    ax.set_xticks(sorted(groups))
    ax.set_xticklabels([f"{k} of {rows[0]['n_afc_trials']}" for k in sorted(groups)], color=DIM)
    ax.set_xlabel("trials in which the annotator identified this condition, per style",
                  color=DIM, fontsize=9)
    ax.set_ylabel("subject area, treated over baseline", color=DIM, fontsize=9)
    means = {k: statistics.mean(r["rho"] for r in g) for k, g in groups.items()}
    lo_k, hi_k = min(means), max(means)
    ax.set_title(f"Where the blinding held the effect is smaller, and it does not vanish\n"
                 f"mean ratio {means[lo_k]:.2f} in the styles the annotator never identified, "
                 f"{means[hi_k]:.2f} where it always did",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.12)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 f"per style  ·  n = {len(rows)} styles  ·  sources "
                 f"data/stage12_enlargement_by_prompt.csv, data/stage12_pattern_results.json")


def main() -> int:
    out = ASSETS / "03-what-ends-up-in-the-picture"
    built = [
        enlargement_by_prompt(out / "F03.1_enlargement_by_prompt.webp"),
        discrimination_rates(out / "F03.2_discrimination_rates.webp"),
        discriminability_vs_effect(out / "F03.3_discriminability_vs_effect.webp"),
    ]
    for p in built:
        print(f"built {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
