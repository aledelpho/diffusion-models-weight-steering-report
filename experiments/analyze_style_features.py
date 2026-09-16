# experiments/analyze_style_features.py
import os
import sys
import csv
import collections
import pandas as pd
import numpy as np

ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
FEAT_CSV = os.path.join(ROOT, "style_features.csv")
STAGE4_CSV = os.path.join(ROOT, "stage4_images.csv")
STAGE5_CSV = os.path.join(ROOT, "stage5_images.csv")
STAGE2_CSV = os.path.join(ROOT, "stage2_images.csv")

COND_MAP = {
    "Arthemy_Bench_Base.json": "preset_pos",
    "Arthemy_Bench_NEG.json": "preset_neg",
    "Arthemy_Bench_RANDSIGN.json": "rand_pos",
    "Arthemy_Bench_RANDSIGN_NEG.json": "rand_neg",
    "Arthemy_Bench_BLOCKSHUFFLE.json": "blockshuf_pos",
    "Arthemy_Bench_BLOCKSHUFFLE_NEG.json": "blockshuf_neg",
    "Arthemy_Bench_HALF.json": "preset_half",
}

PAIRS = [
    ("preset", "preset_pos", "preset_neg"),
    ("blockshuffle", "blockshuf_pos", "blockshuf_neg"),
    ("randsign", "rand_pos", "rand_neg"),
]

def load_data():
    df_feat = pd.read_csv(FEAT_CSV)
    feat_by_file = {r["file"]: r for _, r in df_feat.iterrows()}

    # Carica mapping manifest
    rows = []
    for c in (STAGE4_CSV, STAGE5_CSV):
        if os.path.exists(c):
            with open(c, encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    rows.append(r)

    # Carica baseline
    bases = {}
    for c in (STAGE2_CSV, STAGE5_CSV):
        if os.path.exists(c):
            with open(c, encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    if r.get("operation") == "baseline":
                        bases[(r["prompt_id"], r["seed"])] = os.path.basename(r["image_path"])
    for r in rows:
        if r.get("baseline_path"):
            bases.setdefault((r["prompt_id"], r["seed"]), os.path.basename(r["baseline_path"]))

    # Struttura dati: by_cond[cond][(prompt, seed)] = feature_dict
    by_cond = collections.defaultdict(dict)
    for r in rows:
        pre = r.get("preset_file")
        fname = os.path.basename(r.get("image_path", ""))
        p_id = r.get("prompt_id")
        seed = r.get("seed")
        cond = COND_MAP.get(pre)
        if cond and fname in feat_by_file:
            by_cond[cond][(p_id, seed)] = feat_by_file[fname]

    # Baseline features
    by_base = {}
    for k, bname in bases.items():
        if bname in feat_by_file:
            by_base[k] = feat_by_file[bname]

    return by_cond, by_base, feat_by_file

def main():
    by_cond, by_base, feat_by_file = load_data()
    feature_cols = [c for c in list(feat_by_file.values())[0].index if c not in ("file", "width_px", "height_px", "error")]

    print("=" * 105)
    print("  ANALISI DELLO STILE DI RESA (style_features.py) SU TUTTI I 10 PROMPT (STAGE 4 E 5)")
    print("=" * 105)

    # 1. Medie assolute per condizione sulle feature cardine
    key_feats = [
        ("stroke_width_median_px", "Spessore Tratto (px)"),
        ("stroke_width_cv", "Modulazione Tratto (CV)"),
        ("crosshatch_entropy_mean", "Entropia Cross-hatch"),
        ("color_top4_cluster_share", "Piattezza Colore (Top4)"),
        ("shadow_edge_transition_width_px", "Transizione Ombre (px)"),
        ("contour_mean_length_px", "Lunghezza Contorni (px)"),
        ("fft_radial_slope", "Pendenza Spettro FFT"),
    ]

    print("\n--- MEDIE ASSOLUTE SUI 10 PROMPT ---")
    header = f"{'Feature':35s}{'Baseline':>11s}{'Preset+':>11s}{'Preset-':>11s}{'Block+':>11s}{'Block-':>11s}{'Rand+':>11s}{'Rand-':>11s}"
    print(header)
    print("-" * len(header))

    for feat, label in key_feats:
        vals = {}
        # baseline
        b_vals = [by_base[k][feat] for k in by_base if feat in by_base[k] and not np.isnan(by_base[k][feat])]
        vals["base"] = np.mean(b_vals) if b_vals else np.nan
        for c in ("preset_pos", "preset_neg", "blockshuf_pos", "blockshuf_neg", "rand_pos", "rand_neg"):
            c_vals = [by_cond[c][k][feat] for k in by_cond[c] if feat in by_cond[c][k] and not np.isnan(by_cond[c][k][feat])]
            vals[c] = np.mean(c_vals) if c_vals else np.nan
        print(f"{label:35s}{vals['base']:>11.3f}{vals['preset_pos']:>11.3f}{vals['preset_neg']:>11.3f}{vals['blockshuf_pos']:>11.3f}{vals['blockshuf_neg']:>11.3f}{vals['rand_pos']:>11.3f}{vals['rand_neg']:>11.3f}")

    # 2. Decomposizione S/A per ciascuna feature cardine
    print("\n" + "=" * 105)
    print("  DECOMPOSIZIONE S / A NELLE DIFFERENZE APPAIATE (Delta rispetto alla paired baseline)")
    print("  S = (d+ + d-)/2  (distorsione simmetrica) | A = (d+ - d-)/2  (componente direzionale)")
    print("=" * 105)

    sa_header = f"{'Feature':32s} | {'PRESET':^22s} | {'BLOCKSHUFFLE':^22s} | {'RANDSIGN':^22s}"
    sa_sub    = f"{'':32s} | {'|A|':>7s}{'|S|':>7s}{'A/S':>8s} | {'|A|':>7s}{'|S|':>7s}{'A/S':>8s} | {'|A|':>7s}{'|S|':>7s}{'A/S':>8s}"
    print(sa_header)
    print(sa_sub)
    print("-" * len(sa_header))

    out_summary = []
    for feat, label in key_feats:
        line = f"{label:32s} | "
        for name, cp, cn in PAIRS:
            a_list, s_list = [], []
            for k in by_cond[cp]:
                if k in by_cond[cn] and k in by_base:
                    val_base = by_base[k][feat]
                    val_p = by_cond[cp][k][feat]
                    val_n = by_cond[cn][k][feat]
                    if not (np.isnan(val_base) or np.isnan(val_p) or np.isnan(val_n)):
                        dp = val_p - val_base
                        dn = val_n - val_base
                        a_list.append((dp - dn) / 2.0)
                        s_list.append((dp + dn) / 2.0)
            mA = np.mean(np.abs(a_list)) if a_list else np.nan
            mS = np.mean(np.abs(s_list)) if s_list else np.nan
            ratio = (mA / mS) if (mS and mS > 1e-6) else np.nan
            line += f"{mA:>7.3f}{mS:>7.3f}{ratio:>8.2f} | "
            out_summary.append({"feature": feat, "cond": name, "mA": mA, "mS": mS, "ratio": ratio})
        print(line)

    print("\nLegenda:")
    print(" - A/S > 1.0 : La componente direzionale antisimmetrica domina la distorsione (vero asse di stile)")
    print(" - A/S < 1.0 : Domina la distorsione simmetrica non direzionale")

if __name__ == "__main__":
    main()
