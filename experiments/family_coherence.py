# -*- coding: utf-8 -*-
"""
experiments/family_coherence.py
===============================
Does the displacement produced by a weight edit keep its direction better between two
prompts of the SAME family than between two prompts of DIFFERENT families?

Governed by docs/prereg_family_coherence.md (2026-09-25) and
docs/prereg_family_coherence_amendment_01.md.

Constraints carried from the pre-registration:
  - The prompt is the unit. Pairs are never treated as independent observations.
  - Null = permutation of family labels over prompts, sizes fixed, 10000 draws,
    random.Random(1337). Bootstrap for W = resample of prompts, 2000 draws, same seed.
  - One standardisation for the whole study, computed from BASELINE rows only.
  - Prompt identity is (feature file, prompt id): S7_01..S7_06 and S7_glass are different
    prompts (amendment 01 section 1).
  - Run label is read per (prompt, arm) from the manifests (amendment 01 section 2).
  - No render is generated. No existing claim changes status here.
"""

from __future__ import annotations

import csv
import itertools
import math
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SEEDS_5 = ["42", "777", "1337", "9999", "4242145"]

FEATURES_23 = [
    "stroke_width_median_px", "stroke_width_std_px", "stroke_width_cv", "edge_density",
    "contour_mean_length_px", "contour_n_components", "crosshatch_entropy_mean",
    "crosshatch_entropy_p90", "color_top4_cluster_share", "color_cluster_entropy_norm",
    "color_n_effective", "colorfulness_hs", "luminance_hist_n_peaks",
    "shadow_edge_transition_width_px", "shadow_edge_transition_width_std", "glcm_contrast",
    "glcm_homogeneity", "glcm_energy", "glcm_correlation", "lbp_entropy",
    "lbp_uniform_share", "fft_radial_slope", "fft_high_freq_share",
]
COLOUR_FEATURES = ["color_top4_cluster_share", "color_cluster_entropy_norm",
                   "color_n_effective", "colorfulness_hs"]
FEATURES_19 = [f for f in FEATURES_23 if f not in COLOUR_FEATURES]

ARMS_PRIMARY = ["preset_pos", "rand_pos", "blockshuf_neg"]
ARMS_SECONDARY = ["preset_neg", "rand_neg", "blockshuf_pos"]
ARMS_ALL = ARMS_PRIMARY + ARMS_SECONDARY

FAM_A1 = ["F1", "F2", "F3", "F4", "G1", "G2", "G3", "G4", "G5", "G6",
          "H01", "H02", "H03", "H04", "H05", "H06", "H07", "H08"]
FAM_A2 = ["S7_01", "S7_02", "S7_03", "S7_04", "S7_05", "S7_06"]
FAM_B = ["I01", "I02", "I05", "I06", "I07", "I09", "I10", "I11",
         "I12", "I16", "I17", "I18", "I20", "I21", "I23", "I24"]
FAM_C = ["ST1", "ST2", "ST3", "ST4", "ST5", "ST6", "ST7", "ST8"]
FAMILY_OF = {}
for _p in FAM_A1: FAMILY_OF[_p] = "A1"
for _p in FAM_A2: FAMILY_OF[_p] = "A2"
for _p in FAM_B: FAMILY_OF[_p] = "B"
for _p in FAM_C: FAMILY_OF[_p] = "C"

# stage9 condition label -> canonical arm name (same preset file, strength 1.0)
STAGE9_ARM = {"preset_pos_1x": "preset_pos", "rand_pos_1x": "rand_pos",
              "blockshuf_neg_1x": "blockshuf_neg", "baseline": "baseline"}
# stage9 prompt_dir -> internal id (amendment 01 section 1)
STAGE9_PROMPT = {f"S{i}": f"ST{i}" for i in range(1, 9)}

MANIFESTS = ["stage2_images.csv", "stage4_images.csv", "stage5_images.csv",
             "stage6_images.csv", "stage6b_pilot_images.csv", "stage7a_images.csv",
             "stage7b_images.csv", "stage9_images.csv"]

N_PERM = 10000
N_BOOT = 2000
PERM_SEED = 1337


def die(msg):
    sys.exit(f"ABORT (pre-registration): {msg}")


def load_runs():
    """basename(image_path) -> run_id, from every manifest."""
    runs = {}
    for m in MANIFESTS:
        path = DATA / m
        if not path.exists():
            die(f"missing manifest {m}")
        with path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                runs[os.path.basename(r["image_path"])] = r["run_id"]
    return runs


def load_rows(runs):
    """One record per image: prompt uid, family, arm, seed, run, feature vector."""
    rows = []

    # --- families A1 and A2: data/style_features.csv, metadata parsed from the file name
    with (DATA / "style_features.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            fname = r["file"]
            stem = fname.split("_seed")
            if len(stem) != 2:
                die(f"unparsable file name {fname}")
            seed = stem[1].split("_")[0]
            head = stem[0]
            if head.startswith("S7_"):
                prompt = head[:5]          # S7_01 .. S7_06
                arm = head[6:]
            else:
                prompt = head.split("_")[0]
                arm = head[len(prompt) + 1:]
            if prompt not in FAMILY_OF:
                continue
            if seed not in SEEDS_5 or arm not in ARMS_ALL + ["baseline"]:
                continue
            rows.append(dict(prompt=prompt, family=FAMILY_OF[prompt], arm=arm, seed=seed,
                             run=runs.get(fname, ""), file=fname, src="style_features.csv",
                             vec=[float(r[f]) for f in FEATURES_23]))

    # --- family B: data/style_features_stage7.csv, metadata in columns
    with (DATA / "style_features_stage7.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            prompt, arm, seed = r["prompt_dir"], r["condition"], r["seed"]
            if prompt not in FAM_B or seed not in SEEDS_5:
                continue
            if arm not in ARMS_ALL + ["baseline"]:
                continue
            rows.append(dict(prompt=prompt, family="B", arm=arm, seed=seed,
                             run=runs.get(r["file"], ""), file=r["file"],
                             src="style_features_stage7.csv",
                             vec=[float(r[f]) for f in FEATURES_23]))

    # --- family C: data/style_features_stage9.csv, 1x conditions only
    with (DATA / "style_features_stage9.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["prompt_dir"] not in STAGE9_PROMPT:
                continue                      # the I* baselines carried in this file
            arm = STAGE9_ARM.get(r["condition"])
            if arm is None or r["seed"] not in SEEDS_5:
                continue
            prompt = STAGE9_PROMPT[r["prompt_dir"]]
            rows.append(dict(prompt=prompt, family="C", arm=arm, seed=r["seed"],
                             run=runs.get(r["file"], ""), file=r["file"],
                             src="style_features_stage9.csv",
                             vec=[float(r[f]) for f in FEATURES_23]))
    return rows


def standardise(rows):
    """One standardisation, from baseline rows only (pre-registration section 3)."""
    base = np.array([r["vec"] for r in rows if r["arm"] == "baseline"], dtype=float)
    if base.shape[0] == 0:
        die("no baseline rows")
    mu, sd = base.mean(axis=0), base.std(axis=0, ddof=1)
    dropped = [FEATURES_23[i] for i in range(len(FEATURES_23)) if not sd[i] > 0]
    sd_safe = np.where(sd > 0, sd, 1.0)
    for r in rows:
        r["z"] = (np.array(r["vec"], dtype=float) - mu) / sd_safe
    return mu, sd, dropped, base.shape[0]


def build_deltas(rows, cols):
    """Delta(prompt, arm) = mean over the 5 seeds of z(arm) - z(baseline), restricted to cols."""
    idx = [FEATURES_23.index(c) for c in cols]
    by = {(r["prompt"], r["arm"], r["seed"]): r for r in rows}
    deltas, meta, missing = {}, {}, []
    prompts = sorted({r["prompt"] for r in rows})
    for p in prompts:
        for a in ARMS_ALL:
            have = [s for s in SEEDS_5 if (p, a, s) in by and (p, "baseline", s) in by]
            if len(have) != 5:
                if any((p, a, s) in by for s in SEEDS_5):
                    missing.append((p, a, len(have)))
                continue
            d = np.mean([by[(p, a, s)]["z"][idx] - by[(p, "baseline", s)]["z"][idx]
                         for s in have], axis=0)
            deltas[(p, a)] = d
            meta[(p, a)] = dict(run_arm=by[(p, a, SEEDS_5[0])]["run"],
                                run_base=by[(p, "baseline", SEEDS_5[0])]["run"])
    return deltas, meta, missing


def reliability(rows, cols, prompt_arm):
    """Split-half over seeds (2 vs 3), all 10 splits, cosine between the two halves."""
    idx = [FEATURES_23.index(c) for c in cols]
    by = {(r["prompt"], r["arm"], r["seed"]): r for r in rows}
    out = {}
    for (p, a) in prompt_arm:
        vals = []
        for half in itertools.combinations(SEEDS_5, 2):
            other = [s for s in SEEDS_5 if s not in half]
            v1 = np.mean([by[(p, a, s)]["z"][idx] - by[(p, "baseline", s)]["z"][idx] for s in half], axis=0)
            v2 = np.mean([by[(p, a, s)]["z"][idx] - by[(p, "baseline", s)]["z"][idx] for s in other], axis=0)
            vals.append(cosine(v1, v2))
        out[(p, a)] = float(np.mean(vals))
    return out


def cosine(u, v):
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu == 0 or nv == 0:
        return float("nan")
    return float(np.dot(u, v) / (nu * nv))


def gap_flat(cvals, same, keep):
    """W, Bt, G over the kept pairs, all arrays flattened over the upper triangle."""
    w_mask, b_mask = same & keep, (~same) & keep
    if w_mask.sum() == 0 or b_mask.sum() == 0:
        return float("nan"), float("nan"), float("nan"), int(w_mask.sum()), int(b_mask.sum())
    w, b = float(cvals[w_mask].mean()), float(cvals[b_mask].mean())
    return w, b, w - b, int(w_mask.sum()), int(b_mask.sum())


def perm_p_flat(cvals, labels, ia, ib, keep, g_obs, rng):
    """Permute the labels over prompts, sizes fixed. One-sided on G."""
    if math.isnan(g_obs):
        return float("nan")
    lab = list(labels)
    ge = 0
    for _ in range(N_PERM):
        rng.shuffle(lab)
        arr = np.asarray(lab)
        same = arr[ia] == arr[ib]
        _, _, g, _, _ = gap_flat(cvals, same, keep)
        if not math.isnan(g) and g >= g_obs:
            ge += 1
    return (1 + ge) / (1 + N_PERM)


def boot_w_flat(M, same_m, keep_m, n, ia, ib, rng):
    """Percentile bootstrap over prompts for W. A prompt paired with its own copy is dropped."""
    vals = []
    for _ in range(N_BOOT):
        pick = np.asarray([rng.randrange(n) for _ in range(n)])
        a, b = pick[ia], pick[ib]
        m = (a != b) & same_m[a, b] & keep_m[a, b]
        if m.any():
            vals.append(float(M[a[m], b[m]].mean()))
    if not vals:
        return float("nan"), float("nan")
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))]


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    out = [0.0] * len(pvals)
    running = 0.0
    for rank, i in enumerate(order):
        adj = min(1.0, (len(pvals) - rank) * pvals[i])
        running = max(running, adj)
        out[i] = running
    return out


def analyse(rows, cols, rep_name, prompt_subset, pairs_sink, tests_sink):
    deltas, meta, missing = build_deltas(rows, cols)
    rel = reliability(rows, cols, [k for k in deltas if k[1] in ARMS_ALL])
    results = {}
    for arm in ARMS_ALL:
        prompts = sorted([p for p in prompt_subset if (p, arm) in deltas])
        if len(prompts) < 4:
            continue
        n = len(prompts)
        V = np.array([deltas[(p, arm)] for p in prompts])
        M = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                M[i, j] = cosine(V[i], V[j])
        fam = np.array([FAMILY_OF[p] for p in prompts])
        run = np.array([meta[(p, arm)]["run_arm"] for p in prompts])
        same_fam_m = fam[:, None] == fam[None, :]
        same_run_m = run[:, None] == run[None, :]
        ia, ib = np.triu_indices(n, k=1)
        cvals = M[ia, ib]
        same_fam = same_fam_m[ia, ib]
        same_run = same_run_m[ia, ib]
        keep_all = np.ones(len(cvals), dtype=bool)
        keep_cross = ~same_run

        if rep_name == "features_23" and len(prompt_subset) == 48:
            for k in range(len(cvals)):
                i, j = int(ia[k]), int(ib[k])
                pairs_sink.append(dict(
                    arm=arm, representation=rep_name, prompt_a=prompts[i], prompt_b=prompts[j],
                    family_a=fam[i], family_b=fam[j], run_a=run[i], run_b=run[j],
                    same_family=int(same_fam[k]), same_run=int(same_run[k]),
                    cosine=round(float(cvals[k]), 6)))

        rng = random.Random(PERM_SEED)
        w, b, g, nw, nb = gap_flat(cvals, same_fam, keep_all)
        p_perm = perm_p_flat(cvals, list(fam), ia, ib, keep_all, g, rng)
        rng_b = random.Random(PERM_SEED)
        keep_all_m = np.ones((n, n), dtype=bool)
        lo, hi = boot_w_flat(M, same_fam_m, keep_all_m, n, ia, ib, rng_b)

        # Guard R2 - cross-run pairs only
        w2, b2, g2, nw2, nb2 = gap_flat(cvals, same_fam, keep_cross)
        rng2 = random.Random(PERM_SEED)
        p2 = perm_p_flat(cvals, list(fam), ia, ib, keep_cross, g2, rng2)

        # Guard R1 - run gap inside A1 only
        a1 = [i for i, p in enumerate(prompts) if FAMILY_OF[p] == "A1"]
        g_run, p_run, n_runs = float("nan"), float("nan"), 0
        if len(a1) >= 6:
            Ma = M[np.ix_(a1, a1)]
            ra = run[a1]
            n_runs = len(set(ra.tolist()))
            if n_runs >= 2:
                na = len(a1)
                ja, jb = np.triu_indices(na, k=1)
                cva = Ma[ja, jb]
                same_r = ra[ja] == ra[jb]
                keep_a = np.ones(len(cva), dtype=bool)
                _, _, g_run, _, _ = gap_flat(cva, same_r, keep_a)
                rng3 = random.Random(PERM_SEED)
                p_run = perm_p_flat(cva, list(ra), ja, jb, keep_a, g_run, rng3)

        rels = [rel[(p, arm)] for p in prompts if (p, arm) in rel]
        rel_mean = float(np.mean(rels)) if rels else float("nan")
        results[arm] = dict(
            representation=rep_name, arm=arm, prompt_set=f"{len(prompt_subset)}_prompts",
            n_prompts=n, n_pairs_within=nw, n_pairs_between=nb,
            W=w, Bt=b, G=g, perm_p=p_perm, rel=rel_mean,
            W_over_rel=(w / rel_mean if rel_mean and not math.isnan(rel_mean) and rel_mean != 0 else float("nan")),
            W_boot_lo=lo, W_boot_hi=hi,
            guardR2_W=w2, guardR2_Bt=b2, guardR2_G=g2, guardR2_perm_p=p2,
            guardR2_n_within=nw2, guardR2_n_between=nb2,
            guardR1_G_run_A1=g_run, guardR1_perm_p=p_run, guardR1_n_runs=n_runs,
        )
    # Holm inside the primary set and inside the secondary set, separately
    for group, tag in ((ARMS_PRIMARY, "primary"), (ARMS_SECONDARY, "secondary")):
        present = [a for a in group if a in results]
        adj = holm([results[a]["perm_p"] for a in present])
        for a, v in zip(present, adj):
            results[a]["holm_p"] = v
            results[a]["arm_set"] = tag
    for a in ARMS_ALL:
        if a in results:
            tests_sink.append(results[a])
    return results, missing


def verdict(res):
    """Section 7 of the pre-registration, applied to preset_pos."""
    pp, rp = res.get("preset_pos"), res.get("rand_pos")
    if pp is None:
        return "not_computed"
    if pp["G"] <= 0:
        return "refuted"
    if pp["holm_p"] >= 0.05:
        return "not_significant"
    if (not math.isnan(pp["guardR1_G_run_A1"]) and pp["guardR1_G_run_A1"] >= 0.5 * pp["G"]) \
       or (not math.isnan(pp["guardR2_G"]) and pp["guardR2_G"] <= 0):
        return "ambiguous_family_not_separable_from_run"
    if rp is not None and rp["G"] > 0 and rp["holm_p"] < 0.05 and pp["G"] < 2 * rp["G"]:
        return "holds_but_not_specific_to_the_preset"
    return "holds_and_specific"


def main():
    runs = load_runs()
    rows = load_rows(runs)
    mu, sd, dropped, n_base = standardise(rows)
    if dropped:
        print(f"  dropped zero-variance features: {dropped}")

    prompts_48 = sorted(FAMILY_OF.keys())
    prompts_44 = [p for p in prompts_48 if p not in ("F1", "F2", "F3", "F4")]

    # inventory
    inv = []
    present = defaultdict(set)
    for r in rows:
        present[(r["prompt"], r["arm"])].add(r["seed"])
    for p in prompts_48:
        for a in ["baseline"] + ARMS_ALL:
            seeds = sorted(present.get((p, a), []))
            paired = sum(1 for s in seeds if s in present.get((p, "baseline"), set()))
            inv.append(dict(prompt=p, family=FAMILY_OF[p], arm=a, n_seeds=len(seeds),
                            n_paired_with_baseline=paired,
                            included=int(len(seeds) == 5 and (a == "baseline" or paired == 5)),
                            note=("" if len(seeds) == 5 else "arm absent for this family"
                                  if len(seeds) == 0 else "incomplete seed set"),
                            stage9_alias=("S%s_*" % p[2:] if p.startswith("ST") else "")))

    pairs, tests = [], []
    all_missing = []
    for cols, rep in ((FEATURES_23, "features_23"), (FEATURES_19, "features_19_texture")):
        for subset, _ in ((prompts_48, 48), (prompts_44, 44)):
            res, miss = analyse(rows, cols, rep, subset, pairs, tests)
            all_missing += miss
            if rep == "features_23":
                v = verdict(res)
                print(f"  verdict [{rep}, {len(subset)} prompts]: {v}")
                for t in tests:
                    if t["representation"] == rep and t["prompt_set"] == f"{len(subset)}_prompts":
                        t["verdict_preset_pos"] = v
            else:
                for t in tests:
                    if t["representation"] == rep and t["prompt_set"] == f"{len(subset)}_prompts":
                        t.setdefault("verdict_preset_pos", "sensitivity_only")

    with (DATA / "family_coherence_inventory.csv").open("w", newline="", encoding="utf-8") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(inv[0].keys()))
        wtr.writeheader(); wtr.writerows(inv)
    with (DATA / "family_coherence_pairs.csv").open("w", newline="", encoding="utf-8") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(pairs[0].keys()))
        wtr.writeheader(); wtr.writerows(pairs)
    keys = sorted({k for t in tests for k in t})
    order = ["representation", "prompt_set", "arm", "arm_set", "n_prompts", "n_pairs_within",
             "n_pairs_between", "W", "Bt", "G", "perm_p", "holm_p", "rel", "W_over_rel",
             "W_boot_lo", "W_boot_hi", "guardR2_G", "guardR2_perm_p", "guardR2_W",
             "guardR2_Bt", "guardR2_n_within", "guardR2_n_between", "guardR1_G_run_A1",
             "guardR1_perm_p", "guardR1_n_runs", "verdict_preset_pos"]
    order += [k for k in keys if k not in order]
    with (DATA / "family_coherence_tests.csv").open("w", newline="", encoding="utf-8") as fh:
        wtr = csv.DictWriter(fh, fieldnames=order)
        wtr.writeheader()
        for t in tests:
            wtr.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in t.items()})
    print(f"  baseline rows in the standardisation: {n_base}")
    print(f"  incomplete (prompt, arm) cells: {sorted(set(all_missing))}")
    print(f"  wrote {len(inv)} inventory rows, {len(pairs)} pair rows, {len(tests)} test rows")


if __name__ == "__main__":
    main()
