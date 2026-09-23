# -*- coding: utf-8 -*-
"""
experiments/run_recovery_and_analysis.py   (revision 2, 2026-09-23)
===================================================================
One script, ten phases, no rendering. Run locally where the renders and the checkpoint live.

WHY THIS EXISTS
    The 555 images of the three rotation benches were written at 1024x1760. That is not a
    resolution: the render was 1024x1280 and a 480-pixel HUD panel was appended underneath with a
    vertical batch-image node. Phase 2 proved the crop is lossless -- 30 baseline pairs, all
    bit-identical against a clean re-render -- so every recovered pixel is the pixel the sampler
    produced.

WHAT CHANGED IN REVISION 2 (three bugs in revision 1, all in the recovery half)
    1. Phase 1 wrote every image to `recovered_renders/<last folder>/<file>`. The pilot bench
       keeps 216 images in nine different `benchmark_<prompt>/rotations/` trees whose file names
       repeat across prompts, so nine prompts collapsed into one folder and overwrote each other.
       Now the destination mirrors the source path from the ComfyUI `output\\` root down, which is
       unique by construction, and the phase refuses to write over a file it already wrote.
    2. Phase 3 joined features to metadata on a column with duplicates, producing a many-to-many
       blow-up: 1872 rows for a 225-image bench, 197 for a 210-image one. It also invented its own
       column layout, which is why phase 5 could not read it. Now it extracts once per DISTINCT
       recovered image, and builds each recovered table by taking the ORIGINAL feature CSV and
       overwriting only its numeric feature columns, matched on `file`. Schema identical to the
       original, so the frozen analysers read it unchanged.
    3. Phase 6 keyed each block's directions by (prompt, seed, block), so two blocks never shared
       a key and the pairwise intersection was always empty -- "0 block pairs". Now the block is
       out of the key.

    Revision 1's phases 7, 8 and 9 were correct and their results stand. Phase 4's numbers do NOT
    stand: they were computed against the corrupt tables of bug 2 and must be recomputed.

USAGE
    python experiments/run_recovery_and_analysis.py --only 1 3 4 5
    python experiments/run_recovery_and_analysis.py --list
    --checkpoint PATH   phase 9 only     --jobs N   extraction workers
"""

import argparse
import csv
import hashlib
import itertools
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
DATA = os.path.join(ROOT, "data")
EXP = os.path.join(ROOT, "experiments")
RECOVERED = os.path.join(ROOT, "recovered_renders")
LOG = os.path.join(DATA, "recovery_run_log.md")

HUD_HEIGHT, TRUE_W, TRUE_H = 480, 1024, 1280
HUD_H = TRUE_H + HUD_HEIGHT

sys.path.insert(0, EXP)

# The three benches, their contaminated feature tables, and the bench label used in
# data/hud_contaminated_images.csv.
BENCHES = {
    "pilot_rotations": ("pilot_rotations_style_features.csv",
                        "pilot_rotations_palette_features.csv"),
    "rotations_block1_vs_block6": ("rotations_block1_vs_block6_style_features.csv",
                                   "rotations_block1_vs_block6_palette_features.csv"),
    "rotations_triangolo": ("rotations_triangolo_style_features.csv",
                            "rotations_triangolo_palette_features.csv"),
}
NON_FEATURE = {"file", "image_path", "width_px", "height_px", "prompt_id", "seed", "condition",
               "tag", "run_idx", "report", "type", "block", "rot_kind", "angle_deg", "node_type",
               "angle", "d_target", "prefix", "expected_file"}


def log(msg, head=False):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write((f"\n## {msg}\n" if head else f"{msg}\n"))
    print(msg)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_from_output_root(src):
    """The part of a ComfyUI path below `output\\`, which is unique across the whole bench set."""
    parts = src.replace("/", "\\").split("\\")
    for i, p in enumerate(parts):
        if p.lower() == "output":
            return os.path.join(*parts[i + 1:])
    return os.path.join(*parts[-3:])          # fall back to three levels, still rarely ambiguous


def derive_variant(src_name, dst_name, substitutions):
    """Copy a frozen script, change ONLY the listed literals, prove the diff, log both hashes."""
    src, dst = os.path.join(EXP, src_name), os.path.join(EXP, dst_name)
    text = open(src, encoding="utf-8-sig").read()
    out = text
    for old, new in substitutions:
        if out.count(old) != 1:
            raise ValueError(f"{src_name}: '{old[:50]}' appears {out.count(old)} times, expected 1")
        out = out.replace(old, new)
    changed = sum(1 for a, b in zip(text.splitlines(), out.splitlines()) if a != b)
    if changed != len(substitutions):
        raise ValueError(f"{src_name}: {changed} lines changed, {len(substitutions)} declared")
    open(dst, "w", encoding="utf-8").write(
        f'# DERIVED from {src_name} on {time.strftime("%Y-%m-%d %H:%M")}; only path constants '
        f'differ. Source sha256: {sha256(src)}\n' + out)
    log(f"  derived `{dst_name}` -- {changed} line(s) changed, source sha256 `{sha256(src)[:16]}`")
    return dst


def exact_sign_flip(v):
    v = np.asarray(v, float)
    obs = float(v.mean())
    perm = np.array([np.mean(np.array(s) * v) for s in itertools.product([1, -1], repeat=len(v))])
    return obs, float(np.mean(np.abs(perm) >= abs(obs) - 1e-12)), 2.0 / 2 ** len(v)


def cosine(u, v):
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu < 1e-12 or nv < 1e-12:
        raise ValueError("null vector: the direction is undefined")
    return float(u @ v / (nu * nv))


# ----------------------------------------------------------------------------- phase 1

def phase1_crop():
    from PIL import Image
    log("Phase 1 -- recovering the original pixels", head=True)
    rows = list(csv.DictReader(open(os.path.join(DATA, "hud_contaminated_images.csv"),
                                    encoding="utf-8-sig", newline="")))
    log(f"{len(rows)} images listed in `data/hud_contaminated_images.csv`")

    out_rows, missing, wrong_size, collisions = [], [], [], []
    written = {}
    for r in rows:
        src = r["image_path"]
        if not os.path.exists(src):
            missing.append(src)
            continue
        dst = os.path.join(RECOVERED, rel_from_output_root(src))
        if dst in written and written[dst] != src:
            collisions.append((dst, written[dst], src))
            continue
        with Image.open(src) as im:
            if im.size != (TRUE_W, HUD_H):
                wrong_size.append((src, im.size))
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            im.crop((0, 0, TRUE_W, TRUE_H)).save(dst, format="PNG", compress_level=6)
        written[dst] = src
        out_rows.append({"source_path": src, "recovered_path": dst,
                         "output_folder": r["output_folder"], "file": r["file"],
                         "bench": r["bench"], "prompt_id": r["prompt_id"], "seed": r["seed"],
                         "condition": r["condition"], "recovered_sha256": sha256(dst)})

    df = pd.DataFrame(out_rows)
    df.to_csv(os.path.join(DATA, "recovered_images_manifest.csv"), index=False)
    log(f"recovered **{len(df)}** images into `recovered_renders/`, "
        f"**{df.recovered_path.nunique()}** distinct destinations, "
        f"{len(missing)} missing, {len(wrong_size)} not 1024x1760, {len(collisions)} collisions")
    if len(df) != df.recovered_path.nunique():
        log("  **two source images still map to one destination.** Revision 1's bug is not "
            "fully fixed for this layout -- stop and inspect before trusting phase 3.")
    if collisions:
        log(f"  collisions, first three: {collisions[:3]}")
    if missing:
        log(f"  missing, first five: {missing[:5]}")
    if wrong_size:
        log(f"  **not 1024x1760, first five: {wrong_size[:5]}** -- these break the premise")
    return len(df)


# ----------------------------------------------------------------------------- phase 2

def phase2_prove_lossless():
    from PIL import Image
    log("Phase 2 -- proving the crop is lossless", head=True)
    rec = pd.read_csv(os.path.join(DATA, "recovered_images_manifest.csv"))
    v3 = pd.read_csv(os.path.join(DATA, "rotations_matched_v3_manifest.csv"))
    base_rec = rec[rec.condition.astype(str).str.contains("baseline", case=False, na=False)]
    base_v3 = v3[v3.tag == "baseline"]
    col = next((c for c in ("image_path", "file") if c in base_v3.columns), None)

    pairs = []
    for _, a in base_rec.iterrows():
        m = base_v3[(base_v3.prompt_id == a.prompt_id) & (base_v3.seed.astype(str) == str(a.seed))]
        for _, b in m.iterrows():
            p = str(b[col])
            if os.path.isabs(p) and os.path.exists(p):
                pairs.append((a.recovered_path, p, a.prompt_id, a.seed))
    if not pairs:
        log("**no baseline pair matched.** The proof did not run; do not treat the recovery as "
            "verified.")
        return False

    worst, identical = 0, 0
    for rp, vp, prompt, seed in pairs:
        A = np.asarray(Image.open(rp).convert("RGB"), dtype=np.int16)
        B = np.asarray(Image.open(vp).convert("RGB"), dtype=np.int16)
        if A.shape != B.shape:
            log(f"  {prompt} s{seed}: shapes differ {A.shape} vs {B.shape}")
            worst = 255
            continue
        d = int(np.abs(A - B).max())
        worst = max(worst, d)
        identical += (d == 0)
    log(f"compared **{len(pairs)}** baseline pairs: {identical} bit-identical, worst maximum "
        f"channel difference **{worst}**")
    if worst == 0:
        log("**The crop is lossless.**")
        return True
    log("**The crop is NOT lossless.** Stop; nothing downstream may be published.")
    return False


# ----------------------------------------------------------------------------- phase 3

def _extract_one(path):
    from style_features import extract_all_features
    from analyze_palette import palette_features
    try:
        s = extract_all_features(path)
    except Exception as exc:
        s = {"_style_error": repr(exc)}
    try:
        p = palette_features(path)
    except Exception as exc:
        p = {"_palette_error": repr(exc)}
    return path, s, p


def phase3_extract(jobs):
    """Extract once per distinct image, then rebuild each table from its ORIGINAL schema.

    Taking the original CSV and overwriting only its numeric feature columns keeps every key,
    label and column name the frozen analysers expect. A row whose image could not be measured
    keeps its old values and is listed in the failure table -- never silently half-updated.
    """
    from concurrent.futures import ProcessPoolExecutor, as_completed
    log("Phase 3 -- re-extracting features from the recovered pixels", head=True)
    rec = pd.read_csv(os.path.join(DATA, "recovered_images_manifest.csv"))
    todo = sorted(set(rec.recovered_path))
    log(f"{len(rec)} manifest rows, **{len(todo)} distinct images** to measure")

    S, P, failures = {}, {}, []
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(_extract_one, p): p for p in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            path, s, p = fut.result()
            if "_style_error" in s:
                failures.append({"path": path, "kind": "style", "error": s["_style_error"]})
            else:
                S[os.path.basename(path)] = s
            if "_palette_error" in p:
                failures.append({"path": path, "kind": "palette", "error": p["_palette_error"]})
            else:
                P[os.path.basename(path)] = p
            if i % 50 == 0:
                print(f"    {i}/{len(todo)}")

    if failures:
        pd.DataFrame(failures).to_csv(os.path.join(DATA, "recovered_extraction_failures.csv"),
                                      index=False)
        log(f"**{len(failures)} measurements failed** -- listed in "
            f"`data/recovered_extraction_failures.csv`. Those rows keep their contaminated "
            f"values in the recovered tables and must be excluded by name, not ignored.")

    for bench, (style_csv, palette_csv) in BENCHES.items():
        for src_name, new in ((style_csv, S), (palette_csv, P)):
            src = os.path.join(DATA, src_name)
            if not os.path.exists(src):
                log(f"  {src_name}: original table missing, skipped")
                continue
            df = pd.read_csv(src)
            key = "file" if "file" in df.columns else df.columns[0]
            feat_cols = [c for c in df.columns
                         if c not in NON_FEATURE and pd.api.types.is_numeric_dtype(df[c])]
            hit = 0
            for idx, fname in df[key].items():
                v = new.get(str(fname))
                if not v:
                    continue
                hit += 1
                for c in feat_cols:
                    if c in v:
                        df.at[idx, c] = v[c]
            out = os.path.join(DATA, src_name.replace("_features.csv", "_recovered_features.csv"))
            df.to_csv(out, index=False)
            log(f"  `{os.path.basename(out)}` -- {len(df)} rows, {hit} updated from recovered "
                f"pixels, {len(feat_cols)} feature columns, schema identical to the original")
    return len(todo)


# ----------------------------------------------------------------------------- phase 4

def phase4_hud_delta():
    log("Phase 4 -- what the HUD did to each feature", head=True)
    out = []
    for bench, (style_csv, palette_csv) in BENCHES.items():
        for src_name in (style_csv, palette_csv):
            po = os.path.join(DATA, src_name)
            pn = os.path.join(DATA, src_name.replace("_features.csv", "_recovered_features.csv"))
            if not (os.path.exists(po) and os.path.exists(pn)):
                continue
            o, n = pd.read_csv(po), pd.read_csv(pn)
            if len(o) != len(n):
                log(f"  {src_name}: {len(o)} against {len(n)} rows -- skipped, they must align")
                continue
            for c in [x for x in o.columns if x not in NON_FEATURE
                      and pd.api.types.is_numeric_dtype(o[x]) and x in n.columns]:
                a, b = o[c].astype(float), n[c].astype(float)
                sd = a.std(ddof=0)
                out.append({"bench": bench, "table": "palette" if "palette" in src_name else "style",
                            "feature": c, "n": len(a),
                            "mean_contaminated": a.mean(), "mean_recovered": b.mean(),
                            "mean_shift_in_sd": (b.mean() - a.mean()) / sd if sd > 1e-12 else np.nan,
                            "pearson_r": a.corr(b)})
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(DATA, "hud_feature_delta.csv"), index=False)
    if len(df):
        worst = df.reindex(df.mean_shift_in_sd.abs().sort_values(ascending=False).index).head(12)
        log("the twelve features the HUD moved most, in units of their own spread:")
        log("```\n" + worst[["bench", "feature", "mean_shift_in_sd", "pearson_r"]]
            .round(3).to_string(index=False) + "\n```")
        clean = int((df.pearson_r > 0.99).sum())
        log(f"{clean} of {len(df)} feature-by-bench pairs correlate above 0.99 between the "
            f"contaminated and the recovered measurement: those were never really contaminated. "
            f"The rest were measuring the panel to some degree.")
    return len(df)


# ----------------------------------------------------------------------------- phase 5

def phase5_rerun_b1b6():
    log("Phase 5 -- the published page-08 statistic, recomputed on real pixels", head=True)
    dst = derive_variant(
        "analyze_block1_vs_block6.py", "analyze_block1_vs_block6_recovered.py",
        [('STYLE_CSV = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_style_features.csv")',
          'STYLE_CSV = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_style_recovered_features.csv")'),
         ('PALETTE_CSV = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_palette_features.csv")',
          'PALETTE_CSV = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_palette_recovered_features.csv")'),
         ('RESULTS_CSV_REPORT = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_results.csv")',
          'RESULTS_CSV_REPORT = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_recovered_results.csv")'),
         ('SCORES_CSV_REPORT = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_prompt_scores.csv")',
          'SCORES_CSV_REPORT = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_recovered_prompt_scores.csv")')])
    rc = subprocess.run([sys.executable, dst]).returncode
    log(f"  exit code {rc}")
    if rc != 0:
        log("  **the derived analyser did not finish.** Read its traceback: if it complains about "
            "a column, phase 3 did not preserve the schema and that is the bug to fix, not the "
            "analyser.")
        return
    old = os.path.join(DATA, "rotations_block1_vs_block6_results.csv")
    new = os.path.join(DATA, "rotations_block1_vs_block6_recovered_results.csv")
    if os.path.exists(old) and os.path.exists(new):
        log("published (HUD) against recovered:")
        log("```\n" + pd.read_csv(old).to_string(index=False) + "\n\n"
            + pd.read_csv(new).to_string(index=False) + "\n```")
        log("Same experiment, measured on the panel and on the picture. Where they agree the HUD "
            "never mattered; where they do not, the published number was the panel.")


# ----------------------------------------------------------------------------- phase 6

def phase6_all_blocks():
    log("Phase 6 -- all_blocks_clean_v2, the corpus nobody tested", head=True)
    df = pd.read_csv(os.path.join(DATA, "all_blocks_clean_v2_style_features.csv"))
    FEAT = ["glcm_contrast", "glcm_homogeneity", "lbp_entropy"]
    missing = [c for c in FEAT if c not in df.columns]
    if missing:
        log(f"  primary-space features missing: {missing} -- skipped")
        return
    blocks = [b for b in sorted(df.block_name.unique()) if b.startswith("B")]
    angles = [a for a in sorted(df.angle_label.unique()) if a != "none"]

    X = df[FEAT].astype(float)
    Z = (X - X.mean()) / X.std(ddof=0)
    Z = Z.assign(prompt_id=df.prompt_id.values, seed=df.seed.values,
                 block_name=df.block_name.values, angle_label=df.angle_label.values,
                 sgn=np.where(df.angle_deg.astype(float) > 0, "pos", "neg"))

    rows, dirs = [], {}
    for ang in angles:
        for b in blocks:
            sub = Z[(Z.angle_label == ang) & (Z.block_name == b)]
            cells = {}
            for (p, s), g in sub.groupby(["prompt_id", "seed"]):
                pos, neg = g[g.sgn == "pos"][FEAT], g[g.sgn == "neg"][FEAT]
                if len(pos) == 1 and len(neg) == 1:
                    cells[(p, s)] = (pos.values[0] - neg.values[0]) / 2.0     # block NOT in key
            if not cells:
                continue
            dirs[(ang, b)] = cells
            norms = [float(np.linalg.norm(v)) for v in cells.values()]
            rows.append({"angle": ang, "block": b, "n_cells": len(cells),
                         "mean_norm_A": float(np.mean(norms)), "sd_norm_A": float(np.std(norms))})
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(DATA, "all_blocks_clean_v2_response_by_block.csv"), index=False)
    log("response magnitude per block and angle (antisymmetric, primary space):")
    log("```\n" + res.round(4).to_string(index=False) + "\n```")

    sep = []
    for ang in angles:
        for b1, b2 in itertools.combinations(blocks, 2):
            k1, k2 = dirs.get((ang, b1), {}), dirs.get((ang, b2), {})
            cells = sorted(set(k1) & set(k2))
            if len(cells) < 4:
                continue
            cs = np.array([cosine(k1[c], k2[c]) for c in cells])
            m, p, floor = exact_sign_flip(cs)
            sep.append({"angle": ang, "pair": f"{b1}-{b2}", "n_cells": len(cells),
                        "mean_cos": m, "p_signflip": p, "floor": floor})
    s = pd.DataFrame(sep)
    s.to_csv(os.path.join(DATA, "all_blocks_clean_v2_separability.csv"), index=False)
    log(f"pairwise separability: **{len(s)}** block pairs x angles")
    if len(s):
        log("```\n" + s.sort_values("mean_cos").head(12).round(4).to_string(index=False) + "\n```")
    log("**Declared exploratory.** Six cells, two prompts, one style, no pre-registration. The "
        "floor at six cells is 2/2^6 = 0.03125, so one consistent sign reaches it -- phase 8 "
        "shows why that is not reassuring.")


# ----------------------------------------------------------------------------- phase 7

def phase7_specialisation():
    log("Phase 7 -- specialisation against proximity", head=True)
    d = pd.read_csv(os.path.join(DATA, "all_blocks_specialization_summary.csv")).set_index("block")
    r = d["chroma_shape_ratio"]
    log("```\n" + d[["norm_A_chroma", "norm_A_shape", "norm_A_texture",
                     "chroma_shape_ratio"]].round(4).to_string() + "\n```")
    ends = abs(r["B1"] - r["B6"])
    middles = [abs(r[a] - r[b]) for a, b in itertools.combinations(["B2", "B3", "B4", "B5"], 2)]
    cross = [abs(r[e] - r[m]) for e in ("B1", "B6") for m in ("B2", "B3", "B4", "B5")]
    all_pairs = [abs(r[a] - r[b]) for a, b in itertools.combinations(r.index, 2)]
    rank = int(sum(1 for x in all_pairs if x <= ends))
    log(f"|ratio(B1) - ratio(B6)| = **{ends:.4f}**; middles {np.mean(middles):.4f}; "
        f"end-to-middle {np.mean(cross):.4f}")
    log(f"the two ends are the **{rank}** closest of {len(all_pairs)} pairs "
        f"(permutation p over pairs = {rank / len(all_pairs):.3f})")
    log("**One summary row per block, no null, no seeds behind it.** A hypothesis worth a "
        "designed test, not an answer.")
    pd.DataFrame([{"ends_gap": ends, "mean_middle_gap": float(np.mean(middles)),
                   "mean_cross_gap": float(np.mean(cross)), "rank_of_ends_among_pairs": rank,
                   "n_pairs": len(all_pairs)}]).to_csv(
        os.path.join(DATA, "specialisation_vs_proximity.csv"), index=False)


# ----------------------------------------------------------------------------- phase 8

def phase8_dose_flip():
    log("Phase 8 -- the dose sign-flip (candidate pitfall 72)", head=True)
    d = pd.read_csv(os.path.join(DATA, "rotations_clean_v1_prompt_scores.csv"))
    if "steps" in d.columns:
        d = d[d.steps == 9]
    rows = []
    for c in [c for c in d.columns if c.startswith("s_d")]:
        v = d[c].astype(float).values
        m, p, floor = exact_sign_flip(v)
        rows.append({"dose_column": c, "n_cells": len(v), "mean_s": m,
                     "n_positive": int((v > 0).sum()), "p_signflip": p, "floor": floor,
                     "reaches_floor": bool(abs(p - floor) < 1e-9)})
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(DATA, "dose_sign_flip.csv"), index=False)
    log("```\n" + t.to_string(index=False) + "\n```")
    f = t[t.reaches_floor]
    if len(f) > 1 and f.mean_s.min() < 0 < f.mean_s.max():
        log("**Two doses reach the exact floor with opposite signs.** With six cells any "
            "consistent sign attains the floor: the dose, not the anatomy, decides the answer. "
            "Choosing the dose after seeing all three is pitfall 68 wearing a dose label.")


# ----------------------------------------------------------------------------- phase 9

def phase9_luminance_pump(checkpoint):
    log("Phase 9 -- is scramble_B a luminance pump? (weights only)", head=True)
    for name in ("matched_rotation_calibration_v4.json", "matched_rotation_calibration_v3.json"):
        if os.path.exists(os.path.join(DATA, name)):
            json.load(open(os.path.join(DATA, name), encoding="utf-8"))
            log(f"  calibration read from `{name}`")
            break
    else:
        log("  no calibration file found -- skipped")
        return
    if not checkpoint:
        checkpoint = str(pd.read_csv(
            os.path.join(DATA, "rotations_matched_v3_manifest.csv")).checkpoint.iloc[0])
    log(f"  checkpoint: `{checkpoint}`")
    gate = pd.read_csv(os.path.join(DATA, "rotations_matched_v3_quality_gate.csv"))
    summary = gate.groupby("tag").agg(
        dL_mean=("dL", "mean"), dL_min=("dL", "min"), dL_max=("dL", "max"),
        pass_rate=("passed", lambda x: float(np.mean(x.astype(str).str.lower() == "true"))))
    summary.to_csv(os.path.join(DATA, "scramble_luminance_by_arm.csv"))
    log("```\n" + summary.round(3).to_string() + "\n```")
    log("**Still to implement**: the signed sum of the applied deltas over each block's tensors, "
        "normalised by the block's base norm, using the tensor walk in "
        "`experiments/compute_rotation_displacement.py`. The prediction: net signed gain tracks "
        "`dL_mean` across the eight arms, and a null built to hold net gain at zero lands inside "
        "the gate. That is the one experiment here that will need a GPU.")


# ----------------------------------------------------------------------------- phase 10

def phase10_v3_twelve_prompts():
    log("Phase 10 -- v3 over twelve prompts, secondary", head=True)
    dst = derive_variant(
        "analyze_rotations_matched_v3.py", "analyze_rotations_matched_v3_twelve.py",
        [('PROMPTS = ["S01_oil", "S02_linocut", "S03_cyberpunk", "S04_gouache", "S05_pencil",',
          'PROMPTS = ["P01", "P02", "S01_oil", "S02_linocut", "S03_cyberpunk", "S04_gouache", "S05_pencil",'),
         ('SEEDS = [42, 1337, 4242145]',
          'SEEDS = None  # set per prompt below: S01..S10 use [42, 1337, 4242145], P01/P02 the new three'),
         ('    if len(df) != 270:', '    if len(df) != 324:'),
         ('        raise ValueError(f"attese 270 righe, trovate {len(df)}")',
          '        raise ValueError(f"attese 324 righe, trovate {len(df)}")'),
         ('    res.to_csv(os.path.join(DATA, "rotations_matched_v3_results.csv"), index=False)',
          '    res.to_csv(os.path.join(DATA, "rotations_matched_v3_twelve_results.csv"), index=False)'),
         ('    pd.concat(per).to_csv(os.path.join(DATA, "rotations_matched_v3_prompt_scores.csv"), index=False)',
          '    pd.concat(per).to_csv(os.path.join(DATA, "rotations_matched_v3_twelve_prompt_scores.csv"), index=False)')])
    log("  `SEEDS` is now None on purpose: the two prompt families do not share seeds, so the "
        "derived copy must look each prompt's three seeds up from the manifest. Until that is "
        "written it will stop, and the stop is correct. Fix it in the derived copy only.")
    rc = subprocess.run([sys.executable, dst]).returncode
    log(f"  exit code {rc}")
    log("Whatever it returns is **secondary**: twelve prompts mix two families and were not the "
        "registered unit. It can weaken a confirmation, never create one.")


# ----------------------------------------------------------------------------- driver

PHASES = [
    (1, "crop the HUD off 555 renders", lambda a: phase1_crop()),
    (2, "prove the crop is lossless (ABORTS ON FAILURE)", lambda a: phase2_prove_lossless()),
    (3, "re-extract features from recovered pixels", lambda a: phase3_extract(a.jobs)),
    (4, "measure what the HUD did to each feature", lambda a: phase4_hud_delta()),
    (5, "recompute the published page-08 statistic", lambda a: phase5_rerun_b1b6()),
    (6, "test all_blocks_clean_v2", lambda a: phase6_all_blocks()),
    (7, "specialisation against proximity", lambda a: phase7_specialisation()),
    (8, "the dose sign-flip table", lambda a: phase8_dose_flip()),
    (9, "scramble_B as a luminance pump", lambda a: phase9_luminance_pump(a.checkpoint)),
    (10, "v3 over twelve prompts, secondary", lambda a: phase10_v3_twelve_prompts()),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*", type=int, default=None)
    ap.add_argument("--skip", nargs="*", type=int, default=[])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--checkpoint", default=None)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()

    if a.list:
        for n, name, _ in PHASES:
            print(f"  {n:2d}  {name}")
        return 0

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n\n# Recovery run (revision 2) -- {time.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"HUD panel {HUD_HEIGHT}px, true render {TRUE_W}x{TRUE_H}. "
                f"python {sys.version.split()[0]}\n")

    for n, name, fn in PHASES:
        if (a.only is not None and n not in a.only) or n in a.skip:
            continue
        t0 = time.time()
        try:
            out = fn(a)
        except Exception as exc:
            log(f"\n**phase {n} ({name}) FAILED**: {exc!r}")
            if n == 2:
                return 2
            continue
        log(f"_phase {n} finished in {time.time() - t0:.1f}s_")
        if n == 2 and out is False:
            return 2
    log(f"\nRun log: `{os.path.relpath(LOG, ROOT)}`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
