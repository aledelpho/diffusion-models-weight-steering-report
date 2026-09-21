#!/usr/bin/env python3
"""
experiments/extract_triangolo_qc.py
===================================
Generazione contact sheet QC per l'esperimento Triangolo (330 immagini):
1. Verifica integrita' apertura per tutte le 330 immagini.
2. Contact sheet a griglia per ciascuno dei 10 stili:
   - 11 righe: baseline, Block_1_pos, Block_1_neg, Block_3_pos, Block_3_neg,
     Block_6_pos, Block_6_neg, scramble_A, scramble_B, scramble_C, scramble_D.
   - 3 colonne: seed 42, 1337, 4242145.
3. Salva i contact sheet in qc_output/rotations_triangolo/.
"""

import os
import sys
import csv
import glob
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PILOT_ROOT = Path(r"c:\Users\aless\Desktop\comfyui-pilot")
REPORT_ROOT = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report")
RENDERS_DIR = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\rotations_block1_vs_block6")
MANIFEST_CSV = PILOT_ROOT / "data" / "rotations_triangolo_all330_manifest.csv"
OUT_DIR = REPORT_ROOT / "qc_output" / "rotations_triangolo"

CONDITION_ORDER = [
    "baseline",
    "Block_1_pos", "Block_1_neg",
    "Block_3_pos", "Block_3_neg",
    "Block_6_pos", "Block_6_neg",
    "scramble_A", "scramble_B",
    "scramble_C", "scramble_D",
]

SEEDS = ["42", "1337", "4242145"]

THUMB_W = 200
LABEL_H = 22
PAD = 5
BG = (250, 250, 249)
TEXT = (20, 20, 20)

def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def main():
    print("=== COMFYUI PILOT: QC VISIVO ESPERIMENTO TRIANGOLO ===")
    if not MANIFEST_CSV.exists():
        sys.exit(f"Manifest non trovato: {MANIFEST_CSV}")

    with open(MANIFEST_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Righe nel manifesto: {len(rows)}")

    # 1. Verifica apertura
    print("Verifica apertura file...")
    img_map = {}
    missing = []
    corrupted = []

    for r in rows:
        p_id = r["prompt_id"]
        seed = str(r["seed"])
        cond = r["condition"]
        fn = r["expected_file"]
        p = RENDERS_DIR / fn
        if not p.exists():
            cands = list(RENDERS_DIR.glob(f"{p_id}_s{seed}_{cond}*.png"))
            if cands:
                p = cands[0]
            else:
                missing.append(fn)
                continue
        try:
            with Image.open(p) as img:
                img.verify()
            img_map[(p_id, cond, seed)] = p
        except Exception as e:
            corrupted.append((fn, str(e)))

    if missing:
        print(f"[ERRORE] {len(missing)} immagini mancanti!")
        sys.exit(1)
    if corrupted:
        print(f"[ERRORE] {len(corrupted)} immagini corrotte!")
        sys.exit(1)

    print(f"[OK] Tutte le {len(img_map)} immagini sono integre e leggibili!")

    # 2. Generazione contact sheet per ciascun prompt
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    font_title = load_font(16)
    font_lbl = load_font(12)

    prompts = sorted(list({r["prompt_id"] for r in rows}))
    print(f"\nGenerazione contact sheet per {len(prompts)} stili in {OUT_DIR}...")

    # Determina altezza proporzionale del thumbnail (le immagini originali sono 1024x1760 con HUD)
    sample_path = list(img_map.values())[0]
    with Image.open(sample_path) as im:
        orig_w, orig_h = im.size
    thumb_h = int(THUMB_W * orig_h / orig_w)

    n_cols = len(SEEDS)
    n_rows = len(CONDITION_ORDER)

    row_h = thumb_h + LABEL_H + PAD
    col_w = THUMB_W + PAD
    margin_top = 50
    margin_left = 130
    sheet_w = margin_left + n_cols * col_w + PAD
    sheet_h = margin_top + n_rows * row_h + PAD

    for p_id in prompts:
        sheet = Image.new("RGB", (sheet_w, sheet_h), BG)
        draw = ImageDraw.Draw(sheet)

        draw.text((margin_left, 15), f"Contact Sheet QC: {p_id} (11 Condizioni x 3 Seed)", fill=TEXT, font=font_title)

        # Header colonne
        for c_idx, s in enumerate(SEEDS):
            x = margin_left + c_idx * col_w
            draw.text((x + 10, 32), f"Seed {s}", fill=(80, 80, 80), font=font_lbl)

        # Griglia righe x colonne
        for r_idx, cond in enumerate(CONDITION_ORDER):
            y = margin_top + r_idx * row_h
            # Label riga
            draw.text((10, y + thumb_h // 2 - 6), cond, fill=TEXT, font=font_lbl)

            for c_idx, s in enumerate(SEEDS):
                x = margin_left + c_idx * col_w
                img_p = img_map.get((p_id, cond, s))
                if img_p and img_p.exists():
                    try:
                        with Image.open(img_p) as im:
                            thumb = im.copy()
                            thumb.thumbnail((THUMB_W, thumb_h), Image.Resampling.LANCZOS)
                            sheet.paste(thumb, (x, y))
                    except Exception as e:
                        draw.text((x + 5, y + 20), "Err Load", fill=(200, 0, 0), font=font_lbl)

        out_file = OUT_DIR / f"qc_{p_id}.png"
        sheet.save(out_file, quality=92)
        print(f"  [Salvato] {out_file.name}")

    print("\n[OK] Tutti i 10 contact sheet generati con successo!")

if __name__ == "__main__":
    main()
