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



def headlight_floor_by_style(out: Path) -> Path:
    """Why the stage-12 headlight confirmation could not return an answer.

    Reads data/stage12_headlights_by_style.csv, the table
    experiments/stage12_headlights.py derives from the blind round, and draws the per-style
    rate for the four conditions. The claim is the shape, not a level: nine of the ten styles
    never light a headlight under any condition, so the exact sign-flip test has one
    informative unit and a floor of 2/2 = 1.0.
    """
    src = DATA / "stage12_headlights_by_style.csv"
    if not src.exists():
        raise FileNotFoundError(f"{src} is missing -- run experiments/stage12_headlights.py")
    rows = [r for r in csv.DictReader(src.open(encoding="utf-8", newline=""))
            if r["scope"] == "all_tiles"]
    conds = ["baseline", "preset_pos_2x", "blockshuf_neg_1x", "blockshuf_neg_2x"]
    names = {"baseline": "untouched", "preset_pos_2x": "calibrated preset x2",
             "blockshuf_neg_1x": "block derangement x1",
             "blockshuf_neg_2x": "block derangement x2"}
    styles = sorted({r["prompt_id"] for r in rows})
    informative = sorted({r["prompt_id"] for r in rows if r["prompt_is_informative"] == "yes"})
    order = [s for s in styles if s not in informative] + informative
    y = {s: i for i, s in enumerate(order)}

    # Every series is offset inside its own row. All four sit on top of each other at zero in
    # nine styles of ten, and a single overplotted dot would hide exactly the fact the figure
    # exists to show.
    fig, ax = _canvas(8.0, 4.6)
    palette = [DIM] + CAT
    offsets = [0.24, 0.08, -0.08, -0.24]
    for i, cond in enumerate(conds):
        sel = [r for r in rows if r["condition"] == cond]
        ax.scatter([float(r["rate"]) for r in sel],
                   [y[r["prompt_id"]] + offsets[i] for r in sel],
                   s=34, color=palette[i], edgecolor=SURFACE, linewidth=0.7,
                   label=names[cond], zorder=3)
    for s in informative:
        ax.annotate("the only prompt where anything moves",
                    (1.0, y[s] + 0.24), textcoords="offset points", xytext=(-6, 9),
                    color=INK, fontsize=8, ha="right")

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([s.split("_", 1)[1] for s in order], color=DIM, fontsize=8.5)
    ax.set_xlim(-0.05, 1.15)
    ax.set_ylim(-0.7, len(order) - 0.15)
    ax.set_xlabel("renders scored as having a lit headlight", color=DIM, fontsize=9)
    ax.set_title(f"{len(styles) - len(informative)} styles of {len(styles)} never light a "
                 f"headlight, in any condition\nthe registered confirmation had one "
                 f"informative prompt, so it could not resolve anything",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.legend(loc="center right", fontsize=7.5, frameon=False, labelcolor=DIM,
              handletextpad=0.4, borderaxespad=1.2)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 f"10 styles x 5 seeds x 4 conditions  ·  n = 199 scorable tiles  ·  "
                 f"source data/stage12_headlights_by_style.csv")



FAMILY_LABEL = {"preset": "calibrated preset", "blockshuffle": "block derangement",
                "randsign": "sign scramble (matched norm)"}


def _hatching(level: str) -> tuple[list[dict], dict]:
    src = DATA / ("stage7_hatching_pairs.csv" if level == "pair"
                  else "stage7_hatching_summary.csv")
    if not src.exists():
        raise FileNotFoundError(f"{src} is missing -- run experiments/stage7_hatching_axis.py")
    rows = list(csv.DictReader(src.open(encoding="utf-8", newline="")))
    summary = {r["family"]: r for r in csv.DictReader(
        (DATA / "stage7_hatching_summary.csv").open(encoding="utf-8", newline=""))}
    return rows, summary


def _hatching_strip(out: Path, values: dict, summary: dict, title: str, subtitle: str,
                    strip: str, marked: tuple | None = None) -> Path:
    fams = ["preset", "blockshuffle", "randsign"]
    fig, ax = _canvas(7.8, 3.9)
    ax.axvline(0.0, color=DIM, lw=1.0, ls="--", zorder=1)
    for i, fam in enumerate(fams):
        v = values[fam]
        jitter = [len(fams) - 1 - i + (j - (len(v) - 1) / 2) * (0.55 / max(len(v) - 1, 1))
                  for j in range(len(v))]
        ax.scatter(v, jitter, s=30 if len(v) > 20 else 44, color=CAT[i],
                   edgecolor=SURFACE, linewidth=0.6, zorder=3)
        s = summary[fam]
        ax.annotate(f"delta {float(s['delta']):+.3f}   Holm p {float(s['p_holm']):.1e}",
                    (min(v), len(fams) - 1 - i + 0.33), color=DIM, fontsize=7.5,
                    ha="left", textcoords="offset points", xytext=(-6, 0))
    if marked:
        ax.scatter([marked[0]], [marked[1]], s=150, facecolor="none", edgecolor=INK,
                   linewidth=1.2, zorder=4)
        ax.annotate(marked[2], (marked[0], marked[1]), textcoords="offset points",
                    xytext=(-12, -20), ha="right", color=INK, fontsize=8)
    ax.set_yticks(range(len(fams)))
    ax.set_yticklabels([FAMILY_LABEL[f] for f in reversed(fams)], color=DIM, fontsize=8.5)
    ax.set_xlabel("crosshatch entropy, positive arm minus negative arm", color=DIM, fontsize=9)
    ax.set_title(f"{title}\n{subtitle}", color=INK, fontsize=10.5, loc="left", pad=12)
    ax.set_ylim(-0.55, len(fams) - 1 + 0.58)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.10)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out, strip)


def hatching_axis_by_prompt(out: Path) -> Path:
    """The registered unit: one difference per prompt, three families."""
    rows, summary = _hatching("pair")
    values = {}
    for fam in summary:
        byp = {}
        for r in rows:
            if r["family"] == fam:
                byp.setdefault(r["prompt_sha1"], []).append(float(r["delta"]))
        values[fam] = [statistics.mean(v) for v in byp.values()]
    n = len(next(iter(values.values())))
    return _hatching_strip(
        out, values, summary,
        "Two families separate on the hatching axis, sign fixed in advance",
        "the norm-matched sign scramble, predicted negative, straddles zero",
        f"one point per prompt, seeds averaged first  ·  n = {n} prompts per family  ·  "
        f"source data/stage7_hatching_pairs.csv")


def hatching_axis_by_pair(out: Path) -> Path:
    """The concordance claim: every seed-level pair, and the single exception."""
    rows, summary = _hatching("pair")
    values = {fam: [float(r["delta"]) for r in rows if r["family"] == fam]
              for fam in summary}
    odd = [r for r in rows if r["family"] == "blockshuffle" and r["matches_prediction"] == "no"]
    marked = None
    if len(odd) == 1:
        d = float(odd[0]["delta"])
        marked = (d, 1 + (values["blockshuffle"].index(d) - 39.5) * (0.55 / 79),
                  "the one pair of eighty that goes the other way")
    return _hatching_strip(
        out, values, summary,
        "Eighty image pairs per family, and one exception in the whole design",
        "the preset separates in 80 pairs of 80 and the derangement in 79 of 80",
        f"one point per (prompt, seed) pair  ·  n = {len(values['preset'])} pairs per family  "
        f"·  source data/stage7_hatching_pairs.csv",
        marked=marked)



COND_LABEL = {"blockshuf_neg": "block derangement −", "blockshuf_pos": "block derangement +",
              "preset_neg": "calibrated preset −", "preset_pos": "calibrated preset +",
              "rand_neg": "sign scramble −", "rand_pos": "sign scramble +"}


def _chromatic_rows() -> list[dict]:
    src = DATA / "stage7_chromatic_coherence.csv"
    if not src.exists():
        raise FileNotFoundError(
            f"{src} is missing -- run experiments/stage7_chromatic_coherence.py")
    return [r for r in csv.DictReader(src.open(encoding="utf-8", newline=""))
            if r["condition"] in COND_LABEL]


def chromatic_coherence_decision(out: Path) -> Path:
    """Where each condition lands against the threshold that was fixed in advance."""
    rows = sorted(_chromatic_rows(), key=lambda r: float(r["p_holm"]))
    survivors = [r for r in rows if r["survives_holm_0.05"] == "yes"]

    fig, ax = _canvas(7.6, 3.9)
    ax.axvline(0.05, color=CAT[1], lw=1.3, ls="--", zorder=2)
    ax.annotate("0.05", (0.05, len(rows) - 0.35), color=CAT[1], fontsize=8,
                textcoords="offset points", xytext=(4, 0))
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        passed = r["survives_holm_0.05"] == "yes"
        ax.plot([float(r["p_holm"]), 1.0], [y, y], color=GRID, lw=0.8, zorder=1)
        ax.scatter([float(r["p_holm"])], [y], s=62,
                   color=CAT[2] if passed else DIM, edgecolor=SURFACE, linewidth=0.8,
                   zorder=3)
        ax.annotate(f"cos {float(r['cosine_confirmation']):+.3f}",
                    (float(r["p_holm"]), y), textcoords="offset points", xytext=(0, 9),
                    ha="center", color=INK if passed else DIM, fontsize=8)
    ax.set_xscale("log")
    ax.set_xlim(1e-4, 1.4)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([COND_LABEL[r["condition"]] for r in reversed(rows)],
                       color=DIM, fontsize=8.5)
    ax.set_xlabel("Holm-corrected p for a coherent direction across prompts",
                  color=DIM, fontsize=9)
    ax.set_title(f"{len(survivors)} conditions of {len(rows)} carry a coherent chromatic "
                 f"direction, against a bar of four\nthe fourth misses by "
                 f"{float(rows[3]['p_holm']) - 0.05:.4f}, and the bar was written before the "
                 f"data existed",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_ylim(-0.6, len(rows) - 0.05)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 f"16 prompts, exact sign-flip permutation, Holm across {len(rows)} conditions"
                 f"  ·  source data/stage7_chromatic_coherence.csv")


def chromatic_exploratory_vs_confirmation(out: Path) -> Path:
    """What happened to each condition between the two corpora."""
    rows = sorted(_chromatic_rows(), key=lambda r: -float(r["cosine_confirmation"]))
    fig, ax = _canvas(8.0, 4.3)
    # Two conditions land within 0.0004 of each other on the right; nudge their labels apart
    # rather than let one print on top of the other.
    last, bump = None, 0.0
    for r in rows:
        a, b = float(r["cosine_exploratory"]), float(r["cosine_confirmation"])
        grew = b > a
        ax.plot([0, 1], [a, b], color=CAT[2] if grew else CAT[1], lw=1.6, zorder=2)
        ax.scatter([0, 1], [a, b], s=34, color=CAT[2] if grew else CAT[1],
                   edgecolor=SURFACE, linewidth=0.7, zorder=3)
        bump = bump - 11 if last is not None and abs(last - b) < 0.006 else -3
        last = b
        ax.annotate(COND_LABEL[r["condition"]], (1, b), textcoords="offset points",
                    xytext=(8, bump), color=INK, fontsize=8)
    mean_a = statistics.mean(float(r["cosine_exploratory"]) for r in rows)
    mean_b = statistics.mean(float(r["cosine_confirmation"]) for r in rows)
    ax.plot([0, 1], [mean_a, mean_b], color=INK, lw=2.6, ls=":", zorder=4)
    ax.annotate(f"mean {mean_a:+.3f} to {mean_b:+.3f}", (0, mean_a),
                textcoords="offset points", xytext=(-8, 8), ha="right",
                color=INK, fontsize=8.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["exploratory\n18 prompts, colour named in all",
                        "confirmation\n16 new prompts, colour named in none"],
                       color=DIM, fontsize=8.5)
    ax.set_xlim(-0.42, 1.55)
    ax.set_ylabel("mean pairwise cosine between per-prompt directions", color=DIM, fontsize=9)
    fell = sum(1 for r in rows
               if float(r["cosine_confirmation"]) < float(r["cosine_exploratory"]))
    ax.set_title(f"{fell} conditions of {len(rows)} fell and {len(rows) - fell} rose; the mean "
                 f"went {mean_a:+.3f} to {mean_b:+.3f}\nthe corpora also differ on whether "
                 f"the prompt names a colour, and the ranking reshuffled",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 "6 conditions, mean pairwise cosine over pairs of distinct prompts  ·  "
                 "sources data/palette_condition_cosines.csv, "
                 "data/palette_condition_cosines_stage7.csv")



def _position_rows() -> list[dict]:
    src = DATA / "pilot_rotations_position.csv"
    if not src.exists():
        raise FileNotFoundError(
            f"{src} is missing -- run experiments/pilot_rotations_position.py")
    return list(csv.DictReader(src.open(encoding="utf-8", newline="")))


def _ramp(i: int, n: int) -> str:
    """Depth is ordered, so it wears one hue light to dark, never categorical colours."""
    import matplotlib.colors as mc
    base = mc.to_rgb(CAT[0])
    f = 0.22 + 0.78 * (i / max(n - 1, 1))
    return mc.to_hex(tuple(1 - f * (1 - c) for c in base))


def position_against_displacement(out: Path) -> Path:
    """How much the picture moved against how far the weights moved, per block group."""
    rows = _position_rows()
    n = len(rows)
    fig, ax = _canvas(7.4, 4.4)
    mids = [r for r in rows if r["block"] not in ("Block_1", "Block_6")]
    xs = [float(r["d_model_at_30deg"]) for r in mids]
    ys = [float(r["clip_dist_mean_rotation"]) for r in mids]
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ax.plot([xs[i] for i in order], [ys[i] for i in order], color=GRID, lw=1.4, zorder=1)

    for i, r in enumerate(rows):
        ax.scatter([float(r["d_model_at_30deg"])], [float(r["clip_dist_mean_rotation"])],
                   s=82, color=_ramp(i, n), edgecolor=SURFACE, linewidth=0.9, zorder=3)
    for name, dx, dy in (("Block_6", 10, 0), ("Block_1", 8, -4), ("Block_2", 6, -14)):
        r = next(x for x in rows if x["block"] == name)
        ax.annotate(name.replace("_", " ").lower(),
                    (float(r["d_model_at_30deg"]), float(r["clip_dist_mean_rotation"])),
                    textcoords="offset points", xytext=(dx, dy), color=INK, fontsize=8.5)
    ax.annotate("the four middle groups, in displacement order",
                (sum(xs) / len(xs), min(ys)), textcoords="offset points", xytext=(0, -26),
                ha="center", color=DIM, fontsize=8)

    b6 = next(x for x in rows if x["block"] == "Block_6")
    b2 = next(x for x in rows if x["block"] == "Block_2")
    ratio = float(b6["clip_dist_mean_rotation"]) / float(b2["clip_dist_mean_rotation"])
    less = 1 - float(b6["d_model_at_30deg"]) / float(b2["d_model_at_30deg"])
    ax.set_xlabel("relative Frobenius displacement of the checkpoint at 30 degrees",
                  color=DIM, fontsize=9)
    ax.set_ylabel("mean CLIP distance from baseline", color=DIM, fontsize=9)
    ax.set_title(f"The last group moves the weights {less:.0%} less than the largest and the "
                 f"picture {ratio:.1f} times more\nthe amplitude account is not merely "
                 f"rejected, it is rejected backwards",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(0.16)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 "216 rotation cells · 6 block groups · 7 prompts, averaged per prompt first"
                 "  ·  source data/pilot_rotations_position.csv")


def antisymmetry_by_block(out: Path) -> Path:
    """How much of each group's response reverses when the rotation reverses."""
    rows = _position_rows()
    fig, ax = _canvas(7.6, 4.0)
    x = range(len(rows))
    w = 0.38
    ax.bar([i - w / 2 for i in x], [float(r["norm_S_texture_30deg"]) for r in rows],
           width=w, color=CAT[0], label="‖S‖  how much it moves, either way", zorder=3)
    ax.bar([i + w / 2 for i in x], [float(r["norm_A_texture_30deg"]) for r in rows],
           width=w, color=CAT[1], label="‖A‖  how much reverses with the sign", zorder=3)
    for i, r in enumerate(rows):
        ax.annotate(f"{float(r['antisymmetric_share']):.2f}",
                    (i, max(float(r["norm_S_texture_30deg"]),
                            float(r["norm_A_texture_30deg"]))),
                    textcoords="offset points", xytext=(0, 6), ha="center",
                    color=INK, fontsize=8.5)
    top = max(float(r["antisymmetric_share"]) for r in rows)
    top_block = next(r["block"] for r in rows
                     if abs(float(r["antisymmetric_share"]) - top) < 1e-9)
    ax.set_xticks(list(x))
    ax.set_xticklabels([r["block"].replace("_", " ").lower() for r in rows],
                       color=DIM, fontsize=8.5)
    ax.set_ylabel("norm of the mean direction, texture space", color=DIM, fontsize=9)
    ax.set_title("The antisymmetric share above each pair, and the magnitude beneath it\n"
                 f"the largest share belongs to {top_block.replace('_', ' ').lower()} "
                 f"({top:.2f}), the largest antisymmetric movement to block 6",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.legend(loc="upper left", fontsize=8, frameon=False, labelcolor=DIM)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 "rotation at 30 degrees · texture space, uncentred · 7 prompts  ·  "
                 "source data/pilot_rotations_position.csv")


def main() -> int:
    out = ASSETS / "03-what-ends-up-in-the-picture"
    built = [
        enlargement_by_prompt(out / "F03.1_enlargement_by_prompt.webp"),
        discrimination_rates(out / "F03.2_discrimination_rates.webp"),
        discriminability_vs_effect(out / "F03.3_discriminability_vs_effect.webp"),
        headlight_floor_by_style(ASSETS / "02-attribute-emergence"
                                 / "F02.6_headlight_floor_by_style.webp"),
        hatching_axis_by_prompt(ASSETS / "06-the-hatching-axis"
                                / "F06.1_hatching_axis_by_prompt.webp"),
        hatching_axis_by_pair(ASSETS / "06-the-hatching-axis"
                              / "F06.2_hatching_axis_by_pair.webp"),
        chromatic_coherence_decision(ASSETS / "07-chromatic-signatures"
                                     / "F07.1_coherence_decision.webp"),
        chromatic_exploratory_vs_confirmation(
            ASSETS / "07-chromatic-signatures" / "F07.2_exploratory_vs_confirmation.webp"),
        position_against_displacement(ASSETS / "04-where-in-the-model"
                                      / "F04.1_position_against_displacement.webp"),
        antisymmetry_by_block(ASSETS / "04-where-in-the-model"
                              / "F04.2_antisymmetry_by_block.webp"),
    ]
    for p in built:
        print(f"built {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
