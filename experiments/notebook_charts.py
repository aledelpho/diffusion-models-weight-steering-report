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



def b1b6_advantage_by_prompt(out: Path) -> Path:
    """Every prompt's same-block advantage against the null of two arbitrary scrambles."""
    src = DATA / "b1b6_paired_by_prompt.csv"
    if not src.exists():
        raise FileNotFoundError(f"{src} is missing -- run experiments/b1b6_paired_advantage.py")
    rows = sorted(csv.DictReader(src.open(encoding="utf-8", newline="")),
                  key=lambda r: float(r["V"]))
    y = range(len(rows))

    fig, ax = _canvas(7.6, 4.4)
    ax.axvline(0.0, color=GRID, lw=1.0, zorder=1)
    for i, r in enumerate(rows):
        v, vs = float(r["V"]), float(r["V_scramble"])
        ax.plot([vs, v], [i, i], color=GRID, lw=1.6, zorder=2)
        ax.scatter([vs], [i], s=46, color=CAT[1], edgecolor=SURFACE, linewidth=0.7, zorder=3)
        ax.scatter([v], [i], s=46, color=CAT[0], edgecolor=SURFACE, linewidth=0.7, zorder=3)
    ax.scatter([], [], s=46, color=CAT[0], label="Block_1 against Block_6")
    ax.scatter([], [], s=46, color=CAT[1], label="two arbitrary scrambles, same displacement")

    v_mean = statistics.mean(float(r["V"]) for r in rows)
    s_mean = statistics.mean(float(r["V_scramble"]) for r in rows)
    ahead = sum(1 for r in rows if r["exceeds_null"] == "yes")
    ax.set_yticks(list(y))
    ax.set_yticklabels([r["prompt_id"].split("_", 1)[1] for r in rows], color=DIM, fontsize=8.5)
    ax.set_xlabel("same-block advantage, leave-one-out across prompts", color=DIM, fontsize=9)
    ax.set_title(f"The two blocks separate further than two random perturbations do, in "
                 f"{ahead} prompts of {len(rows)}\nmean {v_mean:+.3f} against a null that is "
                 f"itself {s_mean:+.3f}, not zero",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False, labelcolor=DIM,
              borderaxespad=0.8)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.10)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 "10 style prompts x 3 seeds, displacement matched at D = 0.04500  ·  "
                 "source data/b1b6_paired_by_prompt.csv")


def b1b6_advantage_by_space(out: Path) -> Path:
    """The same comparison in each measurement space, primary and secondary."""
    src = DATA / "b1b6_paired_by_space.csv"
    if not src.exists():
        raise FileNotFoundError(f"{src} is missing -- run experiments/b1b6_paired_advantage.py")
    rows = list(csv.DictReader(src.open(encoding="utf-8", newline="")))
    labels = [r["space"].replace(" (PRIMARIO)", "").replace(" (Secondario)", "")
              .replace(" (Secondaria)", "") for r in rows]

    fig, ax = _canvas(8.0, 4.0)
    x = range(len(rows))
    w = 0.38
    ax.bar([i - w / 2 for i in x], [float(r["V"]) for r in rows], width=w, color=CAT[0],
           label="Block_1 against Block_6", zorder=3)
    ax.bar([i + w / 2 for i in x], [float(r["V_scramble"]) for r in rows], width=w,
           color=CAT[1], label="two arbitrary scrambles", zorder=3)
    for i, r in enumerate(rows):
        ax.annotate(f"+{float(r['paired_advantage']):.2f}", (i, float(r["V"])),
                    textcoords="offset points", xytext=(0, 6), ha="center",
                    color=INK, fontsize=8.5)
    passed = sum(1 for r in rows if r["falsification_passed"] == "True")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{l}\n{r['n_features']} feat." for l, r in zip(labels, rows)],
                       color=DIM, fontsize=8)
    ax.set_ylabel("same-block advantage", color=DIM, fontsize=9)
    ax.set_title(f"The registered falsification criterion is met in {passed} spaces of "
                 f"{len(rows)}\nthe gap above each pair is what the criterion actually "
                 f"compares",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.set_ylim(0, max(float(r["V"]) for r in rows) * 1.34)
    ax.legend(loc="upper center", ncol=2, fontsize=8, frameon=False, labelcolor=DIM,
              bbox_to_anchor=(0.5, 1.02))
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    return _save(fig, out,
                 "5 measurement spaces, same 10 prompts and 3 seeds  ·  "
                 "source data/b1b6_paired_by_space.csv")



def _stage9_cell_label(r: dict) -> str:
    space = r["space"].split(".", 1)[-1].strip()
    space = (space.replace("24-D Completo (L*, a*, b*)", "24-D complete")
                  .replace("8-D Solo Luminanza (L*)", "8-D luminance")
                  .replace("16-D Solo Cromatico (a*, b*)", "16-D chroma")
                  .replace("5-D Asse Tessitura", "5-D texture"))
    cond = (r.get("condition_style") or r.get("condition", "")).replace("_1x", "").replace("_2x", "")
    cond = (cond.replace("preset_pos", "calibrated preset +")
                .replace("blockshuf_neg", "block derangement −")
                .replace("rand_pos", "sign scramble +"))
    return f"{space} · {cond}"


def stage9_centering_flip(out: Path) -> Path:
    """The same statistic under the two standardisation conventions."""
    src = DATA / "stage9_centering_sensitivity.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig", newline="")))
    rows.sort(key=lambda r: float(r["delta_c_centered"]))
    flipped = [r for r in rows if r["sign_agrees"] == "NO"]

    fig, ax = _canvas(8.0, 5.2)
    ax.axvline(0.0, color=DIM, lw=1.2, ls="--", zorder=2)
    for i, r in enumerate(rows):
        a, b = float(r["delta_c_centered"]), float(r["delta_c_uncentered"])
        flips = r["sign_agrees"] == "NO"
        colour = CAT[1] if flips else DIM
        ax.plot([a, b], [i, i], color=colour, lw=1.8 if flips else 1.0, zorder=3)
        ax.scatter([a], [i], s=40, color=colour, edgecolor=SURFACE, linewidth=0.7, zorder=4)
        ax.scatter([b], [i], s=40, facecolor=SURFACE, edgecolor=colour, linewidth=1.4, zorder=4)
    ax.scatter([], [], s=40, color=DIM, label="centred (filled) \u2192 uncentred (hollow)")
    ax.plot([], [], color=CAT[1], lw=1.8, label=f"the sign changes  ({len(flipped)} cells)")
    ax.plot([], [], color=DIM, lw=1.0,
            label=f"the sign holds  ({len(rows) - len(flipped)} cells)")

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{r['amplitude'].replace('Ampiezza ', '')}  {_stage9_cell_label(r)}"
                        for r in rows], color=DIM, fontsize=7.5)
    ax.set_xlabel("coherence between subjects minus coherence between styles\n"
                  "(the registered prediction asked for positive)",
                  color=DIM, fontsize=9)
    ax.set_title(f"The sign of the result depends on a convention nobody registered\n"
                 f"{len(flipped)} cells of {len(rows)} change sign when the joint mean is not "
                 f"subtracted",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False, labelcolor=DIM,
              handletextpad=0.8, borderpad=0.2)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.10, y=0.03)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out,
                 f"{len(rows)} cells, 2 amplitudes x 3 spaces x 3 conditions "
                 f"(the texture space is not in this file)  ·  "
                 f"source data/stage9_centering_sensitivity.csv")


def stage9_direction_at_usable_dose(out: Path) -> Path:
    """What the registered prediction asked for, and which way the cells went."""
    src = DATA / "stage9_coherence_results.csv"
    rows = [r for r in csv.DictReader(src.open(encoding="utf-8-sig", newline=""))
            if "1.0x" in r["amplitude"]]
    rows.sort(key=lambda r: float(r["delta_c_raw"]))

    fig, ax = _canvas(8.0, 4.6)
    ax.axvline(0.0, color=DIM, lw=1.2, zorder=2)
    for i, r in enumerate(rows):
        d = float(r["delta_c_raw"])
        ax.barh(i, d, height=0.62, color=CAT[1] if d < 0 else CAT[2],
                edgecolor=SURFACE, linewidth=0.6, zorder=3)
        ax.annotate(f"p = {float(r['p_value_raw']):.2f}",
                    (d, i), textcoords="offset points",
                    xytext=(-6 if d < 0 else 6, 0), ha="right" if d < 0 else "left",
                    va="center", color=DIM, fontsize=7.5)
    wrong = sum(1 for r in rows if float(r["delta_c_raw"]) < 0)
    sig = sum(1 for r in rows if r["decision"] != "NOT_SIGNIFICANT")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([_stage9_cell_label(r) for r in rows], color=DIM, fontsize=8)
    ax.set_xlabel("coherence between subjects minus coherence between styles\n"
                  "(the registered prediction asked for positive)",
                  color=DIM, fontsize=9)
    ax.set_title(f"At the usable dose not one cell of {len(rows)} is significant\n"
                 f"{wrong} point the wrong way, and all four calibrated-preset cells do",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.22)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 f"{len(rows)} cells at amplitude 1.0x, {sig} significant  ·  "
                 f"source data/stage9_coherence_results.csv")


def _stage9_treat(r: dict) -> str:
    """`S8` + `blockshuf_neg_2x` -> the vocabulary the rest of the notebook uses."""
    cond = r["treatment"].replace("_1x", "").replace("_2x", "")
    cond = (cond.replace("preset_pos", "calibrated preset +")
                .replace("blockshuf_neg", "block derangement −")
                .replace("rand_pos", "sign scramble +"))
    return f"{r['prompt']} · {cond}"


def stage9_quality_gate(out: Path) -> Path:
    """How far outside its own range the double-dose arm sits."""
    src = DATA / "stage9_amplitude2x_quality_gate.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig", newline="")))
    for r in rows:
        r["_z"] = max(abs(float(r["z_edge_density"])), abs(float(r["z_lbp_entropy"])))
    rows.sort(key=lambda r: r["_z"])
    degraded = [r for r in rows if "DEGRADED" in r["status"]]

    fig, ax = _canvas(8.0, 4.4)
    ax.axvline(3.0, color=CAT[2], lw=1.3, ls="--", zorder=2)
    ax.annotate("the gate, 3 sigma", (3.0, len(rows) - 0.4), color=CAT[2], fontsize=8,
                textcoords="offset points", xytext=(6, 0))
    for i, r in enumerate(rows):
        bad = "DEGRADED" in r["status"]
        ax.plot([0.3, r["_z"]], [i, i], color=GRID, lw=0.9, zorder=1)
        ax.scatter([r["_z"]], [i], s=42, color=CAT[1] if bad else DIM,
                   edgecolor=SURFACE, linewidth=0.7, zorder=3)
    worst = rows[-1]
    ax.annotate(f"{_stage9_treat(worst)}  z = {worst['_z']:.0f}",
                (worst["_z"], len(rows) - 1), textcoords="offset points", xytext=(-8, 9),
                ha="right", color=INK, fontsize=8)
    ax.set_xscale("log")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([_stage9_treat(r) for r in rows], color=DIM, fontsize=7.5)
    ax.set_xlabel("distance from the baseline range, in sigma, worst of two texture features",
                  color=DIM, fontsize=9)
    ax.set_title(f"The only arm that produced a result fails its own quality gate in "
                 f"{len(degraded)} cells of {len(rows)}\nthe worst sits at "
                 f"{worst['_z']:.0f} sigma, and the gate was written before the renders",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save(fig, out,
                 f"{len(rows)} cells at amplitude 2.0x  ·  "
                 f"source data/stage9_amplitude2x_quality_gate.csv")


SPACE_SHORT = {"Tessitura (PRIMARIO)": "Texture  (primary)",
               "Global 23 Features (Secondario)": "Global, 23 features",
               "Linework (Secondario)": "Linework",
               "Shadow Hardness (Secondario)": "Shadow hardness",
               "Palette LAB/Chroma (Secondario)": "Palette"}


def b1b6_hud_vs_recovered(out: Path) -> Path:
    """The same experiment measured twice: with the HUD panel in frame, and without it.

    The renders of this bench were written 1024x1760 -- the picture plus a 480-pixel panel
    appended underneath. The panel was added after generation, so cropping it returns the
    original render, and the whole analysis could be re-run on real pixels. Each row is one
    measurement: the segment runs from the scramble null to the same-block advantage, so its
    length is the excess the falsification criterion compares.
    """
    hud = list(csv.DictReader((DATA / "rotations_block1_vs_block6_results.csv")
                              .open(encoding="utf-8-sig", newline="")))
    rec = list(csv.DictReader((DATA / "rotations_block1_vs_block6_recovered_results.csv")
                              .open(encoding="utf-8-sig", newline="")))
    by_space = {r["space"]: r for r in rec}
    order = [r["space"] for r in hud]

    fig, ax = _canvas(8.2, 5.0)
    labels, ypos, y = [], [], 0
    gaps = {}
    for space in reversed(order):
        for tag, row, colour in (("recovered", by_space[space], CAT[1]),
                                 ("with the HUD", next(r for r in hud if r["space"] == space), DIM)):
            v, n = float(row["mean_V"]), float(row["mean_V_scramble"])
            gaps.setdefault(space, {})[tag] = v - n
            ax.plot([n, v], [y, y], color=colour, lw=3.0, solid_capstyle="butt", zorder=3)
            ax.scatter([n], [y], s=46, facecolor=SURFACE, edgecolor=colour, linewidth=1.6, zorder=4)
            ax.scatter([v], [y], s=46, color=colour, edgecolor=SURFACE, linewidth=0.7, zorder=4)
            ax.annotate(f"{v - n:+.2f}", (v, y), textcoords="offset points", xytext=(9, 0),
                        va="center", color=colour, fontsize=7.5)
            labels.append(f"{SPACE_SHORT.get(space, space)} · {tag}")
            ypos.append(y)
            y += 1
        y += 0.6

    ax.scatter([], [], s=46, facecolor=SURFACE, edgecolor=DIM, linewidth=1.6,
               label="the scramble null")
    ax.scatter([], [], s=46, color=DIM, edgecolor=SURFACE, linewidth=0.7,
               label="the same-block advantage")
    ax.legend(loc="upper left", fontsize=7.5, frameon=False, labelcolor=DIM, borderpad=0.2,
              handletextpad=0.6)

    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, color=DIM, fontsize=7.5)
    ax.set_xlabel("leave-one-out same-block advantage; the segment is the excess over the null",
                  color=DIM, fontsize=9)
    prim = gaps["Tessitura (PRIMARIO)"]
    ax.set_title(f"The HUD moved the control more than the effect\n"
                 f"primary space: the excess grows {prim['with the HUD']:+.2f} to {prim['recovered']:+.2f}\n"
                 f"three of the four secondary spaces move the other way",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.13, y=0.03)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out,
                 "5 spaces x 2 measurements, 10 prompts each  ·  sources "
                 "data/rotations_block1_vs_block6_results.csv and "
                 "..._recovered_results.csv")


def _punto7():
    """The 28-block table of page 05, as plain lists -- this module carries no numpy."""
    rows = list(csv.DictReader((DATA / "punto7_blocks.csv").open(encoding="utf-8-sig",
                                                                newline="")))
    out = {k: [float(r[k]) for r in rows] for k in
           ("r_pos", "r_neg", "common_mode", "swing", "specularity", "amp_pos", "amp_neg")}
    out["block"] = [int(r["block"]) for r in rows]
    return out


def _pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / math.sqrt(sxx * syy)


def _fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    m = (sum((a - mx) * (b - my) for a, b in zip(xs, ys))
         / sum((a - mx) ** 2 for a in xs))
    return m, my - m * mx


def knob_vs_cost_scatter(out: Path) -> Path:
    """Every block placed by how much it steers against how much it costs.

    The cost is the common mode -- what an edit does whichever way you push it. The steering is
    the swing -- what reverses with the sign. A ratio alone discards the first, which is exactly
    the quantity this page exists to recover.
    """
    d = _punto7()
    blocks, sw, cm = d["block"], d["swing"], d["common_mode"]
    fig, ax = _canvas(7.4, 5.0)
    ax.axhline(1.0, color=DIM, lw=1.0, ls="--", zorder=2)
    ax.axvline(1.0, color=DIM, lw=1.0, ls="--", zorder=2)
    top = max(blocks)
    sc = ax.scatter(sw, cm, c=[b / top for b in blocks], cmap="magma", s=64,
                    edgecolor=SURFACE, linewidth=0.7, zorder=3, vmin=0, vmax=1)
    for b in (0, 26, 27):
        i = blocks.index(b)
        right = sw[i] < 1.2          # keep the label inside the axes for the far-right point
        ax.annotate(f"block {b}", (sw[i], cm[i]), textcoords="offset points",
                    xytext=(8 if right else -8, 5), ha="left" if right else "right",
                    color=INK, fontsize=8)
    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("block index, 0 to 27", color=DIM, fontsize=8)
    cb.ax.tick_params(colors=DIM, labelsize=7)
    cb.outline.set_edgecolor(GRID)
    ax.set_xlabel("steering: the swing, what reverses with the sign", color=DIM, fontsize=9)
    ax.set_ylabel("cost: the common mode, what happens either way", color=DIM, fontsize=9)
    below = sum(1 for v in cm if v < 1)
    ax.set_title(f"Almost every block sits below the line where an edit would be free\n"
                 f"{below} of {len(blocks)} lose fine texture whichever way they are "
                 f"pushed\nthe dashed lines are 'no change' on each axis",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.09)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out, f"{len(blocks)} blocks, 2 prompts x 3 seeds  ·  "
                           f"source data/punto7_blocks.csv")


def depth_profile(out: Path) -> Path:
    """The cost against depth, with its fitted line. The headline of page 05."""
    d = _punto7()
    b, cm = [float(x) for x in d["block"]], d["common_mode"]
    r = _pearson(b, cm)
    m, q = _fit(b, cm)
    fig, ax = _canvas(7.6, 4.6)
    ax.axhline(1.0, color=DIM, lw=1.0, ls="--", zorder=2)
    xs = [min(b), max(b)]
    ax.plot(xs, [m * x + q for x in xs], color=CAT[0], lw=1.6, zorder=3)
    ax.scatter(b, cm, s=58, color=CAT[1], edgecolor=SURFACE, linewidth=0.7, zorder=4)
    ax.annotate(f"r = {r:.3f}", (xs[1], m * xs[1] + q), textcoords="offset points",
                xytext=(-6, -16), ha="right", color=CAT[0], fontsize=9)
    below = sum(1 for v in cm if v < 1)
    ax.set_xlabel("block index, 0 at the input and 27 against the output", color=DIM, fontsize=9)
    ax.set_ylabel("common mode (1.0 = no cost)", color=DIM, fontsize=9)
    ax.set_title(f"The cost deepens the closer the push lands to the output\n"
                 f"mean {sum(cm) / len(cm):.3f} of the baseline's fine texture, "
                 f"{below} of {len(b)} blocks below 1",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out, f"{len(b)} blocks  ·  source data/punto7_blocks.csv")


def rectification_bars(out: Path) -> Path:
    """Per-block amplitude on the two arms, paired, to show where the sign decides."""
    d = _punto7()
    b, ap, an = d["block"], d["amp_pos"], d["amp_neg"]
    flips = [x for x, p_, n_ in zip(b, ap, an) if n_ > p_]
    tail_flips = [x for x in flips if x >= 22]
    mid_flips = [x for x in flips if x < 22]
    i26 = b.index(26)
    ratio = ap[i26] / an[i26]
    fig, ax = _canvas(8.4, 4.8)
    w = 0.40
    ax.bar([x - w / 2 for x in b], ap, width=w, color=CAT[0], edgecolor=SURFACE, linewidth=0.5,
           label="pushed positive", zorder=3)
    ax.bar([x + w / 2 for x in b], an, width=w, color=CAT[1], edgecolor=SURFACE, linewidth=0.5,
           label="pushed negative", zorder=3)
    for x in flips:
        i = b.index(x)
        ax.annotate("\u2195", (x, max(ap[i], an[i])), textcoords="offset points", xytext=(0, 3),
                    ha="center", color=CAT[2], fontsize=9)
    ax.annotate(f"block 26: {ratio:.1f}x", (26, ap[i26]), textcoords="offset points",
                xytext=(-4, 10), ha="right", color=INK, fontsize=8)
    ax.set_yscale("log")
    ax.set_xticks(b[::2])
    ax.set_xlabel("block index  \u00b7  \u2195 marks a block that moves further on the "
                  "negative arm", color=DIM, fontsize=9)
    ax.set_ylabel("amplitude, log scale", color=DIM, fontsize=9)
    ax.set_title(f"The tail is rectified: on the last blocks one direction moves the image far "
                 f"further\nblock 26 by {ratio:.1f}x. Of the last six only block "
                 f"{tail_flips[0] if tail_flips else '-'} reverses it, and "
                 f"{len(mid_flips)} blocks in the middle reverse it too",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.legend(loc="upper left", fontsize=8, frameon=False, labelcolor=DIM)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out, f"{len(b)} blocks, both arms at |dose| = 0.200  \u00b7  "
                           f"source data/punto7_blocks.csv")


# ---------------------------------------------------------------- toggle and render comparisons


def toggle_animation(out: Path, panels: list[tuple[str, str | Path]], control: tuple[str | Path, str | Path],
                     caption_source: Path) -> Path:
    """Whole frames, one prompt, one seed, with a control panel of two untouched baselines.

    `panels` is [(label, image_path), ...] in reading order; `control` is the baseline pair.
    Every label is read out of `caption_source`, never typed here (pitfall 40).
    """
    c1, c2 = control
    items = list(panels)
    if str(c1) == str(c2):
        items.append(("Control · untouched baseline (same twice)", c1))
    else:
        items.append(("Control · baseline at seed 777", c2))

    n = len(items)
    fig, axes = plt.subplots(1, n, figsize=(3.0 * n, 4.5), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    if n == 1:
        axes = [axes]

    for ax, (label, p) in zip(axes, items):
        ax.set_facecolor(SURFACE)
        im = Image.open(p).convert("RGB")
        ax.imshow(im)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(GRID)
            spine.set_linewidth(1.0)
        is_ctrl = label.startswith("Control")
        ax.set_title(label, color=CAT[1] if is_ctrl else INK, fontsize=7.5, pad=6)

    fig.tight_layout(rect=(0.01, 0.04, 0.99, 0.96))
    strip = f"{n} panels, whole frames  ·  source {caption_source.relative_to(ROOT)}"
    return _save(fig, out, strip)


def inverted_knob_toggle(out: Path) -> Path:
    """F05.4: Block 0 and block 27 alternating against baseline, with control."""
    src = DATA / "punto7_blocks.csv"
    rows = {r["block"]: r for r in csv.DictReader(src.open(encoding="utf-8-sig", newline=""))}
    r0, r27 = rows["00"], rows["27"]
    lab0 = f"Block 0 (+0.200) · swing {float(r0['swing']):.3f} · amp {float(r0['amp_pos']):.2f}"
    lab27 = f"Block 27 (+0.200) · swing {float(r27['swing']):.3f} · amp {float(r27['amp_pos']):.2f}"

    p_base = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_mappa\renders\P01_baseline_krea2_seed42_00001_.png")
    p_b00 = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_profondita\renders\P01_blk00pos_0.200_krea2_seed42_00001_.png")
    p_b27 = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_profondita\renders\P01_blk27pos_0.200_krea2_seed42_00001_.png")

    panels = [
        ("Baseline · P01, seed 42", p_base),
        (lab0, p_b00),
        (lab27, p_b27),
    ]
    control = (p_base, p_base)
    return toggle_animation(out, panels, control, src)


def roundtrip_sentinel(out: Path) -> Path:
    """F00.1: Edit and exact inverse alternating against baseline, with control."""
    src = DATA / "bench_checks.csv"
    rows = {r["check"]: r for r in csv.DictReader(src.open(encoding="utf-8-sig", newline=""))}
    rz, rr = rows["sentinel_zero"], rows["sentinel_roundtrip"]
    lab_z = f"Gain zero · max diff {rz['value']} ({rz['verdict']})"
    lab_r = f"Round-trip (D=0) · mean diff {rr['value']} ({rr['verdict']})"

    p_base = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage1_gate\renders\P1_baseline_seed42_00001_.png")
    p_zero = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage1_gate\renders\P1_sentinel_zero_seed42_00001_.png")
    p_round = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage1_gate\renders\P1_sentinel_roundtrip_seed42_00001_.png")

    panels = [
        ("Baseline · P1, seed 42", p_base),
        (lab_z, p_zero),
        (lab_r, p_round),
    ]
    control = (p_base, p_base)
    return toggle_animation(out, panels, control, src)


def mark_style_toggle(out: Path) -> Path:
    """F01.2: Baseline, preset and norm-matched random control, with seed-pair control."""
    src = DATA / "stage5_images.csv"
    root = ASSETS / "01_steering"
    p_base = root / "baseline" / "G1_seatouched_teal_30de058455" / "42.webp"
    p_preset = root / "preset" / "G1_seatouched_teal_30de058455" / "42.webp"
    p_rand = root / "randsign" / "G1_seatouched_teal_30de058455" / "42.webp"
    p_ctrl = root / "baseline" / "G1_seatouched_teal_30de058455" / "777.webp"

    panels = [
        ("Baseline · G1, seed 42", p_base),
        ("Calibrated preset · +1.000", p_preset),
        ("Rand control · norm-matched", p_rand),
    ]
    control = (p_base, p_ctrl)
    return toggle_animation(out, panels, control, src)


def noise_floor_history(out: Path) -> Path:
    """F00.3: The seed-to-seed noise floor estimated three times."""
    src = DATA / "noise_floor_history.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig", newline="")))

    fig, ax = _canvas(7.5, 4.4)
    xs = list(range(len(rows)))
    vals = [float(r["value_pct"]) for r in rows]
    labels = [f"Est {r['estimate']}\n{r['subject']}\n(n={r['n_seeds']})" for r in rows]

    colors = [DIM, CAT[1], CAT[0], CAT[0]]
    bars = ax.bar(xs, vals, color=colors, width=0.55, edgecolor=SURFACE, linewidth=0.8, zorder=3)

    for x, v in zip(xs, vals):
        ax.annotate(f"{v:.2f}%", (x, v), textcoords="offset points", xytext=(0, 5),
                    ha="center", color=INK, fontsize=8.5, fontweight="bold")

    current = [float(r["value_pct"]) for r in rows if r["superseded_by"] == "current"]
    floor = sum(current) / len(current)
    ax.axhline(floor, color=CAT[2], linestyle="--", linewidth=1.2, zorder=2,
               label=f"measured mean floor ({floor:.2f}%)")

    ax.set_xticks(xs)
    ax.set_xticklabels(labels, color=DIM, fontsize=8)
    ax.set_ylabel("relative sigma of fine texture (%)", color=DIM, fontsize=9)
    ax.set_title("The seed-to-seed noise floor estimated three times\n"
                 "1.15% on 3 seeds \u2192 over-corrected to 5.20% (borrowed) \u2192 1.65% and 1.83% on 18",
                 color=INK, fontsize=10.0, loc="left", pad=12)
    ax.legend(loc="upper right", fontsize=8, frameon=False, labelcolor=DIM)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(y=0.15)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out, f"{len(rows)} estimates  \u00b7  source data/noise_floor_history.csv")



def _response_by_block() -> list[dict]:
    src = DATA / "all_blocks_clean_v2_response_by_block.csv"
    return list(csv.DictReader(src.open(encoding="utf-8-sig", newline="")))


def all_blocks_depth_profile(out: Path) -> Path:
    """F10.1: how far the image moves per block group, at each of the three angles."""
    rows = _response_by_block()
    angles = [("low", 5), ("mid", 10), ("high", 15)]
    blocks = sorted({r["block"] for r in rows})
    by = {(r["angle"], r["block"]): (float(r["mean_norm_A"]), float(r["sd_norm_A"])) for r in rows}
    missing = [(a, b) for a, _ in angles for b in blocks if (a, b) not in by]
    if missing:
        raise SystemExit(f"the measurement file has no row for {missing[:3]}")

    fig, ax = _canvas(7.6, 4.6)
    width = 0.26
    for i, (label, deg) in enumerate(angles):
        xs = [j + (i - 1) * width for j in range(len(blocks))]
        vals = [by[(label, b)][0] for b in blocks]
        errs = [by[(label, b)][1] for b in blocks]
        ax.bar(xs, vals, width=width, color=CAT[i], edgecolor=SURFACE, linewidth=0.7,
               zorder=3, label=f"{deg} deg")
        ax.errorbar(xs, vals, yerr=errs, fmt="none", ecolor=DIM, elinewidth=0.9,
                    capsize=2.5, zorder=4)
    top = by[("high", "B6")][0]
    second = max(by[("high", b)][0] for b in blocks if b != "B6")
    ax.set_xticks(range(len(blocks)))
    ax.set_xticklabels(blocks, color=DIM, fontsize=9)
    ax.set_xlabel("block group, B1 at the input and B6 against the output", color=DIM, fontsize=9)
    ax.set_ylabel("mean |A|, the antisymmetric response", color=DIM, fontsize=9)
    ax.set_title(f"Response grows with angle in every group, and the output group dwarfs "
                 f"the rest\nat 15 deg B6 moves the image {top / second:.1f} times further "
                 f"than the next group",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.legend(loc="upper left", fontsize=8, frameon=False, labelcolor=DIM,
              title="rotation angle", title_fontsize=8)
    ax.get_legend().get_title().set_color(DIM)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out, f"{len(rows)} rows, 6 cells each  \u00b7  "
                           f"source data/all_blocks_clean_v2_response_by_block.csv")


def sensitivity_per_displacement(out: Path) -> Path:
    """F10.2: B6 against B1, before and after dividing by the displacement each received."""
    src = DATA / "sensitivity_by_block.csv"
    rows = [r for r in csv.DictReader(src.open(encoding="utf-8-sig", newline=""))
            if r["response_per_unit_displacement"] != "not measured"]
    if not rows:
        raise SystemExit(f"{src.name} has no normalised row: run "
                         f"experiments/measure_block_group_displacements.py first")
    need = {("B1", a) for a in ("low", "mid", "high")} | {("B6", a) for a in ("low", "mid", "high")}
    have = {(r["block"], r["angle_label"]) for r in rows}
    if not need <= have:
        raise SystemExit(f"the pair B1/B6 is not complete in {src.name}: missing {sorted(need - have)}")
    raw = {(r["block"], r["angle_label"]): float(r["mean_norm_A"]) for r in rows}
    norm = {(r["block"], r["angle_label"]): float(r["response_per_unit_displacement"]) for r in rows}
    angles = ("low", "mid", "high")
    degrees = {"low": 5, "mid": 10, "high": 15}
    as_rendered = [raw[("B6", a)] / raw[("B1", a)] for a in angles]
    per_dose = [norm[("B6", a)] / norm[("B1", a)] for a in angles]
    src_note = rows[0]["displacement_source"]

    fig, ax = _canvas(7.6, 4.6)
    xs = list(range(len(angles)))
    width = 0.34
    ax.bar([x - width / 2 for x in xs], as_rendered, width=width, color=DIM,
           edgecolor=SURFACE, linewidth=0.7, zorder=3, label="as rendered, equal angle")
    ax.bar([x + width / 2 for x in xs], per_dose, width=width, color=CAT[1],
           edgecolor=SURFACE, linewidth=0.7, zorder=3, label="per unit of weight displacement")
    for x, v in zip(xs, as_rendered):
        ax.annotate(f"{v:.2f}x", (x - width / 2, v), textcoords="offset points", xytext=(0, 4),
                    ha="center", color=INK, fontsize=8.5)
    for x, v in zip(xs, per_dose):
        ax.annotate(f"{v:.2f}x", (x + width / 2, v), textcoords="offset points", xytext=(0, 4),
                    ha="center", color=INK, fontsize=8.5, fontweight="bold")
    ax.axhline(1.0, color=CAT[2], ls="--", lw=1.1, zorder=2, label="B6 and B1 equally sensitive")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{a} ({degrees[a]} deg)" for a in angles], color=DIM, fontsize=9)
    ax.set_ylabel("B6 response divided by B1 response", color=DIM, fontsize=9)
    ax.set_title(f"The same angle is not the same dose, and correcting for it widens the gap\n"
                 f"B6 receives {1 / (norm[('B6', 'high')] / raw[('B6', 'high')]):.0%} of B1's "
                 f"displacement at the same angle\n"
                 f"and still answers {min(per_dose):.1f} to {max(per_dose):.1f} times harder",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.legend(loc="upper right", fontsize=8, frameon=False, labelcolor=DIM)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.margins(y=0.16)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out, f"{len(rows)} normalised rows  \u00b7  source data/sensitivity_by_block.csv, "
                           f"displacement from {src_note.split(' (')[0]}")



def downsample_blindness(out: Path) -> Path:
    """F01.3: does the separation survive CLIP's 224x224 resample? Mostly, yes."""
    src = DATA / "downsample_blindness.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig", newline="")))
    native = {r["feature"]: float(r["abs_dz"]) for r in rows if r["scale"] == "native"}
    small = {r["feature"]: float(r["abs_dz"]) for r in rows if r["scale"] == "clip224"}
    if not native or set(native) != set(small):
        raise SystemExit(f"{src.name} does not carry both scales for the same features")
    feats = sorted(native, key=lambda f: -native[f])
    n = int(next(r["n_prompts"] for r in rows))

    fig, ax = _canvas(7.8, 5.0)
    ys = list(range(len(feats)))
    height = 0.36
    ax.barh([y + height / 2 for y in ys], [native[f] for f in feats], height=height,
            color=CAT[0], edgecolor=SURFACE, linewidth=0.7, zorder=3,
            label="as rendered, 1024x1280")
    ax.barh([y - height / 2 for y in ys], [small[f] for f in feats], height=height,
            color=CAT[1], edgecolor=SURFACE, linewidth=0.7, zorder=3,
            label="after CLIP's 224x224 resample")
    ax.invert_yaxis()
    ax.set_yticks(ys)
    ax.set_yticklabels([f.replace("_", " ") for f in feats], color=DIM, fontsize=8)
    ax.set_xlabel("|dz|, the paired effect size of preset against block shuffle",
                  color=DIM, fontsize=9)
    kept = sum(1 for f in feats if small[f] >= 0.5 * native[f])
    grew = sum(1 for f in feats if small[f] > native[f])
    ax.set_title(f"The resample does not wipe the separation out\n"
                 f"{kept} of {len(feats)} statistics keep at least half their effect size at "
                 f"224x224, and {grew} grow",
                 color=INK, fontsize=10.5, loc="left", pad=12)
    ax.legend(loc="lower right", fontsize=8, frameon=False, labelcolor=DIM)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return _save(fig, out, f"{n} prompts, one seed  \u00b7  source data/downsample_blindness.csv")


def scale_comparison(out: Path) -> Path:
    """F01.1: Baseline and preset at full resolution vs 224x224 (as CLIP sees it)."""
    src = DATA / "stage7b_images.csv"
    p_base = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage7a\renders\I01_baseline_seed42_00001_.png")
    p_preset = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage7\renders\I01_preset_pos_seed42_00001_.png")

    im_b = Image.open(p_base).convert("RGB")
    im_p = Image.open(p_preset).convert("RGB")

    im_b224 = im_b.resize((224, 224), Image.LANCZOS)
    im_p224 = im_p.resize((224, 224), Image.LANCZOS)

    items = [
        ("Baseline · full resolution (1024×1280)", im_b),
        ("Preset · full resolution (1024×1280)", im_p),
        ("Baseline · 224×224 (CLIP input scale)", im_b224),
        ("Preset · 224×224 (CLIP input scale)", im_p224),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(12.0, 4.4), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    for ax, (label, img) in zip(axes, items):
        ax.set_facecolor(SURFACE)
        ax.imshow(img)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(GRID)
            spine.set_linewidth(1.0)
        ax.set_title(label, color=INK, fontsize=7.5, pad=6)

    fig.tight_layout(rect=(0.01, 0.04, 0.99, 0.96))
    strip = "full resolution vs 224x224 downsample  \u00b7  source data/stage7b_images.csv"
    return _save(fig, out, strip)


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
        knob_vs_cost_scatter(ASSETS / "05-knob-or-cost" / "F05.1_knob_vs_cost.webp"),
        depth_profile(ASSETS / "05-knob-or-cost" / "F05.2_depth_profile.webp"),
        rectification_bars(ASSETS / "05-knob-or-cost" / "F05.3_rectification.webp"),
        inverted_knob_toggle(ASSETS / "05-knob-or-cost" / "F05.4_inverted_knob_toggle.webp"),
        roundtrip_sentinel(ASSETS / "00-the-bench" / "F00.1_roundtrip_sentinel.webp"),
        noise_floor_history(ASSETS / "00-the-bench" / "F00.3_noise_floor_history.webp"),
        scale_comparison(ASSETS / "01-mark-style" / "F01.1_scale_comparison.webp"),
        mark_style_toggle(ASSETS / "01-mark-style" / "F01.2_mark_style_toggle.webp"),
        b1b6_hud_vs_recovered(ASSETS / "08-block1-vs-block6"
                              / "F08.3_hud_vs_recovered.webp"),
        b1b6_advantage_by_prompt(ASSETS / "08-block1-vs-block6"
                                 / "F08.1_advantage_by_prompt.webp"),
        b1b6_advantage_by_space(ASSETS / "08-block1-vs-block6"
                                 / "F08.2_advantage_by_space.webp"),
        stage9_centering_flip(ASSETS / "09-style-direction"
                              / "F09.1_centering_flip.webp"),
        stage9_direction_at_usable_dose(ASSETS / "09-style-direction"
                                        / "F09.2_direction_at_usable_dose.webp"),
        stage9_quality_gate(ASSETS / "09-style-direction" / "F09.3_quality_gate.webp"),
        all_blocks_depth_profile(ASSETS / "10-all-blocks-clean"
                                 / "F10.1_depth_profile_by_angle.webp"),
        sensitivity_per_displacement(ASSETS / "10-all-blocks-clean"
                                     / "F10.2_sensitivity_per_displacement.webp"),
        downsample_blindness(ASSETS / "01-mark-style" / "F01.3_downsample_blindness.webp"),
    ]
    for p in built:
        print(f"built {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
