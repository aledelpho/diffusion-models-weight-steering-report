# -*- coding: utf-8 -*-
"""
experiments/prepare_stage12_pattern.py

Generatore del dataset cieco per l'Esperimento 12-B: Perceptual Pattern Discrimination (4-AFC)
- 10 stili artistici inediti x 2 prove = 20 trial totali.
- In ciascun trial:
  * 4 immagini con lo STESSO stile.
  * 4 seed RIGOROSAMENTE DIVERSI per impedire template matching spaziale.
  * Le 4 condizioni:
    - blockshuf_neg_2x (Target A)
    - preset_pos_2x    (Target B)
    - blockshuf_neg_1x (Near Foil - Distrattore Difficile)
    - baseline         (Neutral Foil)
  * Rimescolamento casuale delle 4 posizioni (slot 1, 2, 3, 4).
  * Applicazione indipendente dei disturbi di cecita' di livello 3:
    - specchiatura orizzontale/verticale
    - rotazione tinta in [-180, +180] gradi
    - saturazione in [0.6, 1.6]
    - luminosita' in [0.85, 1.15]
    - rumore gaussiano sigma in [0, 4]
- Salva le immagini in viewer/blind_stage12_pattern/
- Scrive il file manifest del viewer: viewer/stage12_pattern_trials.json (privo di label)
- Scrive la chiave sigillata: data/stage12_pattern_key.csv (e relativo SHA256)
"""

import os
import sys
import csv
import json
import random
import hashlib
import cv2
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
DATA_DIR = os.path.join(REPORT_ROOT, "data")
VIEWER_DIR = os.path.join(REPORT_ROOT, "viewer")
BLIND_PATTERN_DIR = os.path.join(VIEWER_DIR, "blind_stage12_pattern")

MANIFEST_CSV = os.path.join(DATA_DIR, "stage12_images.csv")
KEY_CSV = os.path.join(DATA_DIR, "stage12_pattern_key.csv")
KEY_SHA = os.path.join(DATA_DIR, "stage12_pattern_key.sha256")
TRIALS_JSON = os.path.join(VIEWER_DIR, "stage12_pattern_trials.json")

SEED_PRNG = 20260920
TARGET_CONDITIONS = ["blockshuf_neg_2x", "preset_pos_2x", "blockshuf_neg_1x", "baseline"]


def apply_disturbances(bgr, mirror_h, flip_v, hue_shift_deg, sat_factor, lum_factor, noise_sigma, rng):
    out = bgr.copy()
    if mirror_h:
        out = cv2.flip(out, 1)
    if flip_v:
        out = cv2.flip(out, 0)

    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    h_shift_cv = (hue_shift_deg / 2.0) % 180.0
    hsv[:, :, 0] = (hsv[:, :, 0] + h_shift_cv) % 180.0
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat_factor, 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    out = np.clip(out.astype(np.float32) * lum_factor, 0, 255).astype(np.uint8)

    if noise_sigma > 0:
        noise = rng.normal(0, noise_sigma, out.shape).astype(np.float32)
        out = np.clip(out.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return out


def main():
    print("=== PREPARAZIONE SET CIECO 4-AFC ESPERIMENTO 12-B ===")
    if not os.path.exists(MANIFEST_CSV):
        raise SystemExit(f"Manifesto non trovato: {MANIFEST_CSV}")

    os.makedirs(BLIND_PATTERN_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(VIEWER_DIR, exist_ok=True)

    with open(MANIFEST_CSV, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))

    index = {}
    for r in reader:
        k = (r["prompt_id"], r["cond_name"], int(r["seed"]))
        index[k] = r

    style_ids = sorted(list({r["prompt_id"] for r in reader}))
    available_seeds = sorted(list({int(r["seed"]) for r in reader}))

    rng = random.Random(SEED_PRNG)
    np_rng = np.random.RandomState(SEED_PRNG)

    trials_manifest = []
    key_rows = []

    trial_counter = 1
    for s_idx, style_id in enumerate(style_ids, 1):
        for run_idx in range(1, 3):
            chosen_seeds = rng.sample(available_seeds, 4)
            cond_seed_map = dict(zip(TARGET_CONDITIONS, chosen_seeds))

            shuffled_conds = TARGET_CONDITIONS.copy()
            rng.shuffle(shuffled_conds)

            trial_slots = []
            slot_records = {}

            for slot_pos, cond in enumerate(shuffled_conds, 1):
                seed_val = cond_seed_map[cond]
                item = index.get((style_id, cond, seed_val))
                if not item:
                    raise SystemExit(f"Immagine non trovata per {style_id}, {cond}, {seed_val}")

                root = item["renders_root"]
                rel = item["image_path"].replace("/", os.sep)
                raw_path = os.path.join(root, os.path.basename(rel))
                if not os.path.exists(raw_path):
                    raw_path = os.path.join(root, rel)
                if not os.path.exists(raw_path):
                    raise SystemExit(f"File sorgente non trovato: {raw_path}")

                bgr = cv2.imread(raw_path)
                if bgr is None:
                    raise SystemExit(f"Impossibile leggere: {raw_path}")

                m_h = rng.random() < 0.5
                f_v = rng.random() < 0.5
                hue_deg = rng.uniform(-180.0, 180.0)
                sat_f = rng.uniform(0.6, 1.6)
                lum_f = rng.uniform(0.85, 1.15)
                n_sig = rng.uniform(0.0, 4.0)

                dist_bgr = apply_disturbances(bgr, m_h, f_v, hue_deg, sat_f, lum_f, n_sig, np_rng)

                out_fname = f"t{trial_counter:02d}_s{slot_pos}.png"
                out_path = os.path.join(BLIND_PATTERN_DIR, out_fname)
                cv2.imwrite(out_path, dist_bgr)

                trial_slots.append({
                    "slot": slot_pos,
                    "image_url": f"blind_stage12_pattern/{out_fname}"
                })

                slot_records[slot_pos] = {
                    "cond": cond,
                    "seed": seed_val,
                    "mirror_h": m_h,
                    "flip_v": f_v,
                    "hue_shift_deg": round(hue_deg, 2),
                    "sat_factor": round(sat_f, 3),
                    "lum_factor": round(lum_f, 3),
                    "noise_sigma": round(n_sig, 2),
                    "orig_file": os.path.basename(raw_path)
                }

            correct_blockshuf = shuffled_conds.index("blockshuf_neg_2x") + 1
            correct_preset = shuffled_conds.index("preset_pos_2x") + 1
            correct_blockshuf_1x = shuffled_conds.index("blockshuf_neg_1x") + 1
            correct_baseline = shuffled_conds.index("baseline") + 1

            trials_manifest.append({
                "trial_id": trial_counter,
                "style_id": style_id,
                "style_label": f"Stile {s_idx:02d} ({style_id}) - Prova {run_idx}/2",
                "slots": trial_slots
            })

            key_rows.append({
                "trial_id": trial_counter,
                "style_id": style_id,
                "trial_run": run_idx,
                "correct_blockshuf_2x_slot": correct_blockshuf,
                "correct_preset_pos_2x_slot": correct_preset,
                "correct_blockshuf_1x_slot": correct_blockshuf_1x,
                "correct_baseline_slot": correct_baseline,
                "slot_1_cond": slot_records[1]["cond"],
                "slot_1_seed": slot_records[1]["seed"],
                "slot_2_cond": slot_records[2]["cond"],
                "slot_2_seed": slot_records[2]["seed"],
                "slot_3_cond": slot_records[3]["cond"],
                "slot_3_seed": slot_records[3]["seed"],
                "slot_4_cond": slot_records[4]["cond"],
                "slot_4_seed": slot_records[4]["seed"],
                "slot_1_orig": slot_records[1]["orig_file"],
                "slot_2_orig": slot_records[2]["orig_file"],
                "slot_3_orig": slot_records[3]["orig_file"],
                "slot_4_orig": slot_records[4]["orig_file"]
            })

            trial_counter += 1

    with open(TRIALS_JSON, "w", encoding="utf-8") as f:
        json.dump(trials_manifest, f, indent=2)
    print(f"[OK] Generato viewer/stage12_pattern_trials.json con {len(trials_manifest)} trial.")

    fieldnames = [
        "trial_id", "style_id", "trial_run",
        "correct_blockshuf_2x_slot", "correct_preset_pos_2x_slot",
        "correct_blockshuf_1x_slot", "correct_baseline_slot",
        "slot_1_cond", "slot_1_seed", "slot_2_cond", "slot_2_seed",
        "slot_3_cond", "slot_3_seed", "slot_4_cond", "slot_4_seed",
        "slot_1_orig", "slot_2_orig", "slot_3_orig", "slot_4_orig"
    ]
    with open(KEY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in key_rows:
            writer.writerow(r)

    hasher = hashlib.sha256()
    with open(KEY_CSV, "rb") as f:
        hasher.update(f.read())
    key_hash = hasher.hexdigest()
    with open(KEY_SHA, "w", encoding="utf-8") as f:
        f.write(key_hash + "\n")

    print(f"[OK] Sigillata chiave in data/stage12_pattern_key.csv")
    print(f"[OK] SHA-256: {key_hash}")
    print("Completata preparazione del set cieco 4-AFC!")


if __name__ == "__main__":
    main()
