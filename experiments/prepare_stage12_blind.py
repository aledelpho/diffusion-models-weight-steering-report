# -*- coding: utf-8 -*-
"""
experiments/prepare_stage12_blind.py

Generatore del dataset cieco con 3 livelli di controllo per lo Stage 12:
1. Livello 1: Prima esposizione dentro il viewer (nessuna anteprima o contact sheet).
2. Livello 2: Chiave nuova, hash univoci a 12 caratteri, ordine mescolato con seed registrato.
3. Livello 3: Disturbi randomizzati e registrati (usati come covariate):
   - Specchiatura orizzontale (p=0.5) [invariante per area]
   - Ribaltamento verticale (p=0.5) [invariante per area]
   - Rotazione di tinta in [-180, +180] gradi
   - Fattore di saturazione in [0.6, 1.6]
   - Fattore di luminosita' in [0.85, 1.15]
   - Rumore gaussiano sigma in [0, 4] livelli
4. Iniezione di 20 duplicati nascosti con stato di specchiatura invertito.
   Totale presentato per l'ingrandimento BBox: 200 uniche (4 condizioni standard) + 20 duplicati = 220 immagini.
   (Le 50 immagini di preset_pos_1x restano disponibili per la passata di scoring fari).
5. Scrive data/stage12_bbox_key.csv (SIGILLATO).
"""

import os
import sys
import csv
import json
import random
import hashlib
import cv2
import numpy as np
from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
DATA_DIR = os.path.join(REPORT_ROOT, "data")
VIEWER_DIR = os.path.join(REPORT_ROOT, "viewer")
BLIND_DIR = os.path.join(VIEWER_DIR, "blind_stage12")

MANIFEST_CSV = os.path.join(DATA_DIR, "stage12_images.csv")
KEY_CSV = os.path.join(DATA_DIR, "stage12_bbox_key.csv")
ORDER_JSON = os.path.join(VIEWER_DIR, "blind_order_stage12.json")

SHUFFLE_SEED = 20260919
SALT = "arthemy_stage12_blind_salt_v1"

# Le 4 condizioni primarie per l'ipotesi di ingrandimento
BBOX_CONDITIONS = ["baseline", "blockshuf_neg_1x", "blockshuf_neg_2x", "preset_pos_2x"]


def apply_disturbances(bgr, mirror_h, flip_v, hue_shift_deg, sat_factor, lum_factor, noise_sigma, rng):
    """Applica i disturbi mantenendo rigorosamente invariata l'area del bounding box."""
    out = bgr.copy()

    # 1. Trasformazioni geometriche speculari (invarianti per area W x H)
    if mirror_h:
        out = cv2.flip(out, 1)
    if flip_v:
        out = cv2.flip(out, 0)

    # 2. Spazio HSV per rotazione di tinta e fattore di saturazione
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    # Tinta in OpenCV: [0, 180] corrispondente a [0, 360] gradi
    h_shift_cv = (hue_shift_deg / 2.0) % 180.0
    hsv[:, :, 0] = (hsv[:, :, 0] + h_shift_cv) % 180.0
    # Saturazione
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat_factor, 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # 3. Luminosita'
    out = np.clip(out.astype(np.float32) * lum_factor, 0, 255).astype(np.uint8)

    # 4. Rumore gaussiano lieve
    if noise_sigma > 0:
        noise = rng.normal(0, noise_sigma, out.shape).astype(np.float32)
        out = np.clip(out.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return out


def main():
    print("=== PREPARAZIONE SET CIECO STAGE 12 (3 LIVELLI + 20 DUPLICATI) ===")
    if not os.path.exists(MANIFEST_CSV):
        raise SystemExit(f"Manifesto non trovato: {MANIFEST_CSV}")

    os.makedirs(BLIND_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(MANIFEST_CSV, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))

    # Filtra le 200 immagini delle 4 condizioni primarie di BBox
    bbox_rows = [r for r in reader if r.get("cond_name") in BBOX_CONDITIONS]
    if len(bbox_rows) != 200:
        raise SystemExit(f"Attese 200 immagini per le 4 condizioni di BBox, trovate: {len(bbox_rows)}")

    print(f"[1/5] Filtrate 200 immagini primarie ({len(BBOX_CONDITIONS)} condizioni x 10 stili x 5 seed)")

    rng = random.Random(SHUFFLE_SEED)
    np_rng = np.random.RandomState(SHUFFLE_SEED)

    # Generazione record primari (200)
    primary_records = []
    seen_hashes = set()

    for r in bbox_rows:
        root = r["renders_root"]
        rel = r["image_path"].replace("/", os.sep)
        src_path = os.path.join(root, os.path.basename(rel))
        if not os.path.exists(src_path):
            src_path = os.path.join(root, rel)
        if not os.path.exists(src_path):
            raise SystemExit(f"Immagine non trovata sul disco: {src_path}")

        # Hash univoco
        payload = f"{SALT}_{r['prompt_sha1']}_{r['cond_name']}_{r['seed']}".encode("utf-8")
        hash_id = hashlib.sha256(payload).hexdigest()[:12]
        seen_hashes.add(hash_id)

        # Parametri di disturbo casuali ma deterministici
        mirror_h = rng.random() < 0.5
        flip_v = rng.random() < 0.5
        hue_shift = rng.uniform(-180.0, 180.0)
        sat_factor = rng.uniform(0.6, 1.6)
        lum_factor = rng.uniform(0.85, 1.15)
        noise_sigma = rng.uniform(0.0, 4.0)

        primary_records.append({
            "hash_id": hash_id,
            "src_path": src_path,
            "prompt_id": r["prompt_id"],
            "prompt_sha1": r["prompt_sha1"],
            "cond_name": r["cond_name"],
            "seed": r["seed"],
            "is_duplicate": 0,
            "orig_hash_id": hash_id,
            "mirror_h": int(mirror_h),
            "flip_v": int(flip_v),
            "hue_shift_deg": round(hue_shift, 2),
            "sat_factor": round(sat_factor, 4),
            "lum_factor": round(lum_factor, 4),
            "noise_sigma": round(noise_sigma, 2)
        })

    # [2/5] Selezione e iniezione di 20 duplicati nascosti (stratificati sulle baseline)
    print("[2/5] Selezione di 20 duplicati nascosti con specchiatura invertita...")
    # Seleziona 2 duplicati per ciascuno dei 10 stili dai baseline (20 duplicati)
    base_records = [rec for rec in primary_records if rec["cond_name"] == "baseline"]
    dup_records = []
    for p_id in sorted(list({rec["prompt_id"] for rec in base_records})):
        candidates = [rec for rec in base_records if rec["prompt_id"] == p_id]
        # Prendi 2 seed casuali tra i 5
        sampled = rng.sample(candidates, 2)
        for s_rec in sampled:
            dup_payload = f"{SALT}_DUP_{s_rec['hash_id']}".encode("utf-8")
            dup_hash = hashlib.sha256(dup_payload).hexdigest()[:12]

            # Stato di specchiatura invertito rispetto alla prima occorrenza
            dup_mirror = 1 - s_rec["mirror_h"]
            dup_flip = rng.random() < 0.5
            dup_hue = rng.uniform(-180.0, 180.0)
            dup_sat = rng.uniform(0.6, 1.6)
            dup_lum = rng.uniform(0.85, 1.15)
            dup_noise = rng.uniform(0.0, 4.0)

            dup_records.append({
                "hash_id": dup_hash,
                "src_path": s_rec["src_path"],
                "prompt_id": s_rec["prompt_id"],
                "prompt_sha1": s_rec["prompt_sha1"],
                "cond_name": s_rec["cond_name"],
                "seed": s_rec["seed"],
                "is_duplicate": 1,
                "orig_hash_id": s_rec["hash_id"],
                "mirror_h": int(dup_mirror),
                "flip_v": int(dup_flip),
                "hue_shift_deg": round(dup_hue, 2),
                "sat_factor": round(dup_sat, 4),
                "lum_factor": round(dup_lum, 4),
                "noise_sigma": round(dup_noise, 2)
            })

    total_records = primary_records + dup_records
    if len(total_records) != 220:
        raise SystemExit(f"Attesi 220 record totali, calcolati: {len(total_records)}")

    # [3/5] Mescolamento con seme fisso
    rng.shuffle(total_records)
    print(f"[3/5] Ordine di presentazione (220 immagini) mescolato con seed {SHUFFLE_SEED}")

    # [4/5] Generazione immagini distorte su viewer/blind_stage12/<hash_id>.png
    print(f"[4/5] Scrittura delle 220 immagini con disturbi applicati in {BLIND_DIR}...")
    manifest_blind_order = []
    for idx, rec in enumerate(total_records, 1):
        dst_filename = f"{rec['hash_id']}.png"
        dst_path = os.path.join(BLIND_DIR, dst_filename)

        img_bgr = cv2.imread(rec["src_path"])
        disturbed = apply_disturbances(
            img_bgr,
            mirror_h=bool(rec["mirror_h"]),
            flip_v=bool(rec["flip_v"]),
            hue_shift_deg=rec["hue_shift_deg"],
            sat_factor=rec["sat_factor"],
            lum_factor=rec["lum_factor"],
            noise_sigma=rec["noise_sigma"],
            rng=np_rng
        )
        cv2.imwrite(dst_path, disturbed)

        manifest_blind_order.append({
            "order": idx,
            "hash_id": rec["hash_id"],
            "filename": dst_filename
        })

    with open(ORDER_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest_blind_order, f, indent=2)
    print(f"      Elenco cieco salvato in: {ORDER_JSON}")

    # [5/5] Scrittura della chiave segreta con le covariate di disturbo (DA SIGILLARE)
    with open(KEY_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "order", "hash_id", "prompt_id", "prompt_sha1", "cond_name", "seed",
            "is_duplicate", "orig_hash_id", "mirror_h", "flip_v",
            "hue_shift_deg", "sat_factor", "lum_factor", "noise_sigma", "src_path"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, rec in enumerate(total_records, 1):
            writer.writerow({
                "order": idx,
                "hash_id": rec["hash_id"],
                "prompt_id": rec["prompt_id"],
                "prompt_sha1": rec["prompt_sha1"],
                "cond_name": rec["cond_name"],
                "seed": rec["seed"],
                "is_duplicate": rec["is_duplicate"],
                "orig_hash_id": rec["orig_hash_id"],
                "mirror_h": rec["mirror_h"],
                "flip_v": rec["flip_v"],
                "hue_shift_deg": rec["hue_shift_deg"],
                "sat_factor": rec["sat_factor"],
                "lum_factor": rec["lum_factor"],
                "noise_sigma": rec["noise_sigma"],
                "src_path": os.path.basename(rec["src_path"])
            })

    print(f"[5/5] Chiave segreta salvata in: {KEY_CSV}")
    print("      >>> AVVISO METODOLOGICO: Non aprire la chiave prima che tutti i 220 punteggi siano registrati!")
    print("=== SET CIECO STAGE 12 PREPARATO CON SUCCESSO ===")


if __name__ == "__main__":
    main()
