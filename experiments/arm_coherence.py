# -*- coding: utf-8 -*-
"""
experiments/arm_coherence.py  --  how far each arm moves the batch, and how much it agrees

The animations on page 02 raise a question they cannot answer. Five seeds of one prompt, one
edit, and all five move the same way: the lamps come on in all of them, the frame darkens in
all of them. A reader watching that will ask whether an edit is a perturbation that happens to
land similarly, or a direction the whole batch is pushed along. This measures it.

For every arm of the stage-9 bench, in the 23-dimensional style-feature space:

  magnitude    ||D||, the length of the paired difference from the baseline of the same
               (prompt, seed), in units of the baseline spread
  coherence    the mean cosine between those difference vectors, split two ways --
               across the five SEEDS of one prompt, and across different PROMPTS
  agreement    the cosine between the mean direction of each pair of arms
  per prompt   the same coherence one scene at a time, because the average over prompts
               hides that the styles are not alike
  the test     whether a structured arm agrees with itself MORE than the norm-matched sign
               scramble does, prompt by prompt, exact sign-flip, Holm across the family.
               Without this the coherence numbers say nothing about structure: holding the
               seed fixed is itself enough to make a RANDOM perturbation look like a
               direction, and the control is there to show how much

and, as the scale all three are read against, the same statistics on pairs of BASELINES at
different seeds. A change of seed is a large move in this space and it has no shared
direction; if an arm's coherence were of that order, "direction" would be the wrong word.

STANDARDISATION happens once, on the baselines of the corpus being analysed, and is then
applied to every image (pitfall 33: a separate standardisation per condition manufactures
agreement). The corpus is named per arm rather than pooled, because `chaos_edges_v2` was
rendered on four subject prompts while the other six arms ran on the eight style prompts;
pooling them would compare arms across different scenes.

WHAT THIS DOES NOT SHOW. The arms are not at matched displacement on this bench -- page 09
records that the double-amplitude figure is twice the single-dose value rather than a second
measurement -- so the magnitude column ranks how hard each arm was pushed as much as how much
it moves the image. The coherence columns do not depend on that: a direction is a direction
whatever its length. Read the magnitudes as descriptive and the cosines as the result.

Cosines here are not disattenuated. Each difference vector is measured with error, which pulls
every cosine toward zero, so the coherences below are lower bounds (pitfall 36).

Exploratory: no threshold was frozen before these were computed.

Nothing is rendered. Reads data/style_features_stage9.csv, writes data/arm_coherence.csv and
data/arm_coherence_pairs.csv, data/arm_coherence_by_prompt.csv and
data/arm_coherence_tests.csv.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SRC = DATA / "style_features_stage9.csv"

NOT_FEATURES = {"file", "width_px", "height_px", "condition", "prompt_dir",
                "prompt_sha1", "seed", "rel_path", "source_manifest"}
BASELINE = "baseline"


def load() -> tuple[list[str], dict[tuple[str, str, str], list[float]]]:
    if not SRC.exists():
        sys.exit(f"{SRC} is missing")
    with SRC.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    feats = [c for c in rows[0] if c not in NOT_FEATURES]
    cells: dict[tuple[str, str, str], list[float]] = {}
    for r in rows:
        try:
            cells[(r["prompt_dir"], r["condition"], r["seed"])] = [float(r[c]) for c in feats]
        except (ValueError, TypeError):
            continue
    return feats, cells


def cosine(a: list[float], b: list[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if not na or not nb:
        raise ValueError("a zero-length difference vector has no direction")
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def length(a: list[float]) -> float:
    return math.sqrt(sum(x * x for x in a))


def coherence(d: dict[tuple[str, str], list[float]]) -> tuple[float, float, int, int]:
    """Mean cosine within one prompt across seeds, and between different prompts."""
    same, other = [], []
    for k1, k2 in itertools.combinations(sorted(d), 2):
        (same if k1[0] == k2[0] else other).append(cosine(d[k1], d[k2]))
    return (statistics.fmean(same) if same else float("nan"),
            statistics.fmean(other) if other else float("nan"),
            len(same), len(other))



def sign_flip(diffs: list[float]) -> tuple[float, float]:
    """Exact two-tailed sign-flip p on paired differences, and its floor."""
    n = len(diffs)
    if n > 20:
        raise SystemExit(f"{n} pairs is too many to enumerate exactly")
    obs = abs(statistics.fmean(diffs))
    hits = sum(1 for s in itertools.product((1, -1), repeat=n)
               if abs(statistics.fmean(a * d for a, d in zip(s, diffs))) >= obs - 1e-12)
    return hits / 2 ** n, 2 / 2 ** n


def holm(ps: list[float]) -> list[float]:
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, ps[i] * (len(ps) - rank)))
        out[i] = running
    return out


# The comparison that decides what the coherence means. An arm agreeing with itself across
# seeds is only interesting if a norm-matched RANDOM perturbation does not do the same, so
# every structured arm is tested against the sign scramble at its own amplitude, prompt by
# prompt, and both are tested against the seed null.
CONTRASTS = [
    ("preset_pos_1x", "rand_pos_1x"),
    ("preset_pos_2x", "rand_pos_2x"),
    ("blockshuf_neg_1x", "rand_pos_1x"),
    ("blockshuf_neg_2x", "rand_pos_2x"),
    ("preset_pos_1x", "__seed_null__"),
    ("rand_pos_1x", "__seed_null__"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DATA / "arm_coherence.csv"))
    ap.add_argument("--out-pairs", default=str(DATA / "arm_coherence_pairs.csv"))
    ap.add_argument("--out-by-prompt", default=str(DATA / "arm_coherence_by_prompt.csv"))
    ap.add_argument("--out-tests", default=str(DATA / "arm_coherence_tests.csv"))
    a = ap.parse_args()

    a_out_tests = a.out_tests
    feats, cells = load()
    arms = sorted({c for _, c, _ in cells} - {BASELINE})

    rows, means, corpora, per_prompt = [], {}, {}, []
    for arm in arms:
        prompts = sorted({p for p, c, _ in cells if c == arm})
        base = {(p, s): v for (p, c, s), v in cells.items()
                if c == BASELINE and p in prompts}
        if not base:
            sys.exit(f"{arm}: no baseline for its prompts")
        # one standardisation, on this corpus's baselines, applied to everything below
        mu = [statistics.fmean(v[i] for v in base.values()) for i in range(len(feats))]
        sd = [statistics.stdev(v[i] for v in base.values()) for i in range(len(feats))]
        if any(s == 0 for s in sd):
            dead = [feats[i] for i, s in enumerate(sd) if s == 0]
            sys.exit(f"{arm}: these features do not vary across baselines and cannot be "
                     f"standardised: {dead}")

        def z(v): return [(v[i] - mu[i]) / sd[i] for i in range(len(feats))]

        delta = {(p, s): [x - y for x, y in zip(z(v), z(base[(p, s)]))]
                 for (p, c, s), v in cells.items() if c == arm and (p, s) in base}
        if not delta:
            sys.exit(f"{arm}: no cell pairs with a baseline at the same prompt and seed")

        # the scale: baselines against each other, same prompt, different seed
        null = {}
        for p in prompts:
            seeds = sorted(s for (pp, s) in base if pp == p)
            for s1, s2 in itertools.combinations(seeds, 2):
                null[(p, f"{s1}-{s2}")] = [x - y for x, y in
                                           zip(z(base[(p, s1)]), z(base[(p, s2)]))]
        n_same, n_other, _, _ = coherence(null)
        mags = [length(v) for v in delta.values()]
        null_mags = [length(v) for v in null.values()]
        same, other, n_pairs_same, n_pairs_other = coherence(delta)

        # The same question one prompt at a time. The average above hides that the styles are
        # not alike: an arm can be one direction on one scene and five accidents on another,
        # and only this table says which.
        for p in prompts:
            cells_here = {k: v for k, v in delta.items() if k[0] == p}
            if len(cells_here) < 2:
                continue
            cos_here = [cosine(a, b) for a, b in itertools.combinations(
                [cells_here[k] for k in sorted(cells_here)], 2)]
            null_here = [cosine(a, b) for a, b in itertools.combinations(
                [v for k, v in null.items() if k[0] == p], 2)]
            mags_here = [length(v) for v in cells_here.values()]
            null_mags_here = [length(v) for k, v in null.items() if k[0] == p]
            per_prompt.append({
                "arm": arm,
                "prompt": p,
                "n_seeds": len(cells_here),
                "n_pairs": len(cos_here),
                "mean_displacement": round(statistics.fmean(mags_here), 4),
                "seed_null_displacement": round(statistics.fmean(null_mags_here), 4),
                "times_the_seed_null": round(
                    statistics.fmean(mags_here) / statistics.fmean(null_mags_here), 3),
                "coherence_across_seeds": round(statistics.fmean(cos_here), 4),
                "seed_null_coherence": round(statistics.fmean(null_here), 4)
                                       if len(null_here) > 1 else "",
                "min_pairwise_cosine": round(min(cos_here), 4),
                "max_pairwise_cosine": round(max(cos_here), 4),
            })

        means[arm] = [statistics.fmean(v[i] for v in delta.values()) for i in range(len(feats))]
        corpora[arm] = " ".join(prompts)
        rows.append({
            "arm": arm,
            "n_cells": len(delta),
            "n_prompts": len(prompts),
            "corpus": " ".join(prompts),
            "mean_displacement_in_feature_space": round(statistics.fmean(mags), 4),
            "sd_displacement": round(statistics.stdev(mags), 4),
            "seed_null_displacement": round(statistics.fmean(null_mags), 4),
            "times_the_seed_null": round(statistics.fmean(mags) / statistics.fmean(null_mags), 3),
            "coherence_across_seeds": round(same, 4),
            "coherence_across_prompts": round(other, 4),
            "seed_null_coherence": round(n_same, 4),
            "n_pairs_same_prompt": n_pairs_same,
            "n_pairs_other_prompt": n_pairs_other,
            "space": f"{len(feats)}-D style features, standardised on this corpus's baselines",
        })
        print(f"{arm:18s} n={len(delta):3d}  |D| {statistics.fmean(mags):5.2f} "
              f"({statistics.fmean(mags) / statistics.fmean(null_mags):4.2f}x the seed null)  "
              f"coherence: seeds {same:+.3f}  prompts {other:+.3f}  "
              f"(null {n_same:+.3f})")

    pairs = []
    for x, y in itertools.combinations(arms, 2):
        shared = set(corpora[x].split()) & set(corpora[y].split())
        pairs.append({
            "arm_a": x, "arm_b": y,
            "cosine_between_mean_directions": round(cosine(means[x], means[y]), 4),
            "shared_prompts": len(shared),
            "comparable": "yes" if shared else
                          "NO -- the two arms ran on different prompts, so this cosine mixes "
                          "the edit with the scene",
        })

    per_prompt.sort(key=lambda r: (r["prompt"], r["arm"]))
    for path, data in ((Path(a.out), rows), (Path(a.out_pairs), pairs),
                       (Path(a.out_by_prompt), per_prompt)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
        print(f"wrote {path}  ({len(data)} rows)")

    look = {(r["arm"], r["prompt"]): r for r in per_prompt}
    shared = sorted({r["prompt"] for r in per_prompt
                     if all((a, r["prompt"]) in look for a, _ in CONTRASTS)})
    tests = []
    raw = []
    for a, b in CONTRASTS:
        if not all((a, p) in look for p in shared):
            continue
        x = [float(look[(a, p)]["coherence_across_seeds"]) for p in shared]
        y = ([float(look[(a, p)]["seed_null_coherence"]) for p in shared]
             if b == "__seed_null__"
             else [float(look[(b, p)]["coherence_across_seeds"]) for p in shared])
        d = [i - j for i, j in zip(x, y)]
        pv, floor = sign_flip(d)
        raw.append(pv)
        tests.append({
            "arm": a, "against": b, "n_prompts": len(shared),
            "mean_difference_in_coherence": round(statistics.fmean(d), 4),
            "prompts_in_favour": sum(1 for v in d if v > 0),
            "p_sign_flip": round(pv, 6), "p_floor": round(floor, 6),
        })
    for t, h in zip(tests, holm(raw)):
        t["p_holm"] = round(h, 6)
        t["verdict"] = ("separates" if h < 0.05 else
                        "does NOT separate -- the control matches it")
    Path(a_out_tests).parent.mkdir(parents=True, exist_ok=True)
    with open(a_out_tests, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tests[0].keys()))
        w.writeheader()
        w.writerows(tests)
    print(f"wrote {a_out_tests}  ({len(tests)} rows)")
    print("\ndoes the arm agree with itself MORE than the norm-matched random control does?")
    for t in tests:
        print(f"  {t['arm']:18s} vs {t['against']:14s} "
              f"{t['mean_difference_in_coherence']:+.3f}  "
              f"{t['prompts_in_favour']}/{t['n_prompts']} prompts  "
              f"p {t['p_sign_flip']:.5f}  Holm {t['p_holm']:.4f}  -> {t['verdict']}")

    print("\nwithin one prompt, across its seeds -- the spread the average above hides:")
    arms_seen = sorted({r["arm"] for r in per_prompt})
    prompts_seen = sorted({r["prompt"] for r in per_prompt})
    look = {(r["arm"], r["prompt"]): r for r in per_prompt}
    print(f"  {'prompt':10s}" + "".join(f"{x[:13]:>14s}" for x in arms_seen))
    for p in prompts_seen:
        line = f"  {p:10s}"
        for x in arms_seen:
            r = look.get((x, p))
            line += f"{float(r['coherence_across_seeds']):+14.3f}" if r else f"{'':>14s}"
        print(line)

    print("\ncosine between the mean direction of each pair of arms:")
    for p in pairs:
        flag = "" if p["comparable"] == "yes" else "   [different prompts]"
        print(f"  {p['arm_a']:18s} vs {p['arm_b']:18s} "
              f"{p['cosine_between_mean_directions']:+.3f}{flag}")


if __name__ == "__main__":
    main()
