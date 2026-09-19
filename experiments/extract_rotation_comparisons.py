#!/usr/bin/env python3
"""
extract_rotation_comparisons.py

QC + figura per l'esperimento "Rotazioni Block_1 vs Block_6" (rotations_block1_vs_block6).

Nessuna delle 210 immagini e' mai stata guardata da un umano: la pre-registrazione
segnava il cancello "210 immagini estratte con zero errori" come [x], ma quel
cancello controlla che lo script di estrazione feature non abbia sollevato eccezioni,
non che le immagini siano visivamente sane (soggetto assente, render corrotto,
condizione scambiata, ecc.). Questo script fa tre cose, in quest'ordine:

  1. VERIFICA GREZZA: apre ognuna delle 210 immagini elencate nel CSV e segnala
     quelle mancanti o corrotte, PRIMA di costruire qualunque composizione.
  2. CONTACT SHEET DI QC per ciascuno dei 10 prompt: righe = 7 condizioni,
     colonne = 3 seed, cosi' da poter scorrere visivamente tutto il dataset.
  3. STRIP DI EVIDENZA per i due stili "limite" della tabella pubblicata
     (V(p) piu' alto e piu' basso), scelti automaticamente da
     rotations_block1_vs_block6_prompt_scores.csv anziche' hard-coded:
     baseline / Block_1_pos / Block_1_neg / Block_6_pos / Block_6_neg,
     un seed, con V(p) annotato in didascalia.

Uso:
    python extract_rotation_comparisons.py

Configura solo le tre variabili sotto (REPO_DIR, IMAGE_ROOT_OVERRIDE, OUT_DIR)
se il layout locale non corrisponde a quello di default.

Dipendenze: pillow (pip install pillow). Nessun'altra libreria richiesta.
"""

import csv
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Manca Pillow. Installa con:  pip install pillow")

# ----------------------------------------------------------------------------
# CONFIGURAZIONE — adatta questi tre percorsi al tuo ambiente locale
# ----------------------------------------------------------------------------

# Cartella del repository clonato di diffusion-models-weight-steering-report
REPO_DIR = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report")

# Se gli image_path nel CSV puntano a un percorso che oggi non esiste piu'
# (es. hai spostato l'output di ComfyUI), imposta qui la nuova cartella radice
# e lo script sostituira' automaticamente il prefisso vecchio con questo.
# Lascia None per usare i path del CSV cosi' come sono.
IMAGE_ROOT_OVERRIDE = None  # es: Path(r"D:\comfy_output\rotations_block1_vs_block6")
OLD_IMAGE_ROOT_PREFIX = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\rotations_block1_vs_block6"

STYLE_FEATURES_CSV = REPO_DIR / "data" / "rotations_block1_vs_block6_style_features.csv"
PROMPT_SCORES_CSV = REPO_DIR / "data" / "rotations_block1_vs_block6_prompt_scores.csv"
OUT_DIR = REPO_DIR / "qc_output" / "rotations_block1_vs_block6"

# Ordine di visualizzazione delle condizioni (righe del contact sheet)
CONDITION_ORDER = [
    "baseline",
    "Block_1_pos", "Block_1_neg",
    "Block_6_pos", "Block_6_neg",
    "scramble_A", "scramble_B",
]
HIGHLIGHT_CONDITIONS = ["baseline", "Block_1_pos", "Block_1_neg", "Block_6_pos", "Block_6_neg"]

THUMB_W = 220          # larghezza miniatura nel contact sheet
HIGHLIGHT_W = 420       # larghezza immagine nella strip di evidenza
LABEL_H = 26
PAD = 6
BG = (250, 250, 249)
TEXT = (20, 20, 20)
BAD = (200, 40, 40)


def resolve_path(raw_path: str) -> Path:
    if IMAGE_ROOT_OVERRIDE is not None and raw_path.startswith(OLD_IMAGE_ROOT_PREFIX):
        rel = raw_path[len(OLD_IMAGE_ROOT_PREFIX):].lstrip("\\/")
        return IMAGE_ROOT_OVERRIDE / rel
    return Path(raw_path)


def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def load_rows(csv_path: Path):
    if not csv_path.exists():
        sys.exit(f"Non trovo {csv_path}. Aggiorna REPO_DIR in cima allo script.")
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def step1_verify(rows):
    print("=" * 70)
    print("STEP 1 — verifica grezza dei 210 file immagine")
    print("=" * 70)
    missing, corrupt, ok = [], [], 0
    for r in rows:
        p = resolve_path(r["image_path"])
        if not p.exists():
            missing.append((r["prompt_id"], r["condition"], r["seed"], str(p)))
            continue
        try:
            with Image.open(p) as im:
                im.verify()
            ok += 1
        except Exception as e:
            corrupt.append((r["prompt_id"], r["condition"], r["seed"], str(p), str(e)))

    print(f"OK: {ok}/{len(rows)}")
    if missing:
        print(f"\nMANCANTI ({len(missing)}):")
        for m in missing:
            print(f"  prompt={m[0]:15s} cond={m[1]:14s} seed={m[2]:>8s}  {m[3]}")
    if corrupt:
        print(f"\nCORROTTI ({len(corrupt)}):")
        for c in corrupt:
            print(f"  prompt={c[0]:15s} cond={c[1]:14s} seed={c[2]:>8s}  {c[3]}  [{c[4]}]")
    if not missing and not corrupt:
        print("Nessun file mancante o corrotto.")
    print()
    return missing, corrupt


def make_thumb(path: Path, width: int):
    try:
        im = Image.open(path).convert("RGB")
    except Exception:
        im = Image.new("RGB", (width, int(width * 1.3)), (230, 200, 200))
        d = ImageDraw.Draw(im)
        d.text((8, 8), "ERRORE\nAPERTURA", fill=BAD)
        return im
    w, h = im.size
    new_h = int(h * (width / w))
    return im.resize((width, new_h), Image.LANCZOS)


def step2_contact_sheets(rows, out_dir: Path):
    print("=" * 70)
    print("STEP 2 — contact sheet di QC per ciascun prompt (7 condizioni x 3 seed)")
    print("=" * 70)
    out_dir.mkdir(parents=True, exist_ok=True)
    font = load_font(16)
    font_small = load_font(13)

    by_prompt = {}
    for r in rows:
        by_prompt.setdefault(r["prompt_id"], []).append(r)

    for prompt_id, prows in sorted(by_prompt.items()):
        seeds = sorted(set(r["seed"] for r in prows), key=lambda s: int(s))
        by_cond_seed = {(r["condition"], r["seed"]): r for r in prows}

        label_col_w = 150
        thumb_h_ref = None
        thumbs = {}
        for cond in CONDITION_ORDER:
            for seed in seeds:
                r = by_cond_seed.get((cond, seed))
                if r is None:
                    continue
                p = resolve_path(r["image_path"])
                thumb = make_thumb(p, THUMB_W) if p.exists() else Image.new(
                    "RGB", (THUMB_W, int(THUMB_W * 1.3)), (235, 235, 235))
                thumbs[(cond, seed)] = thumb
                if thumb_h_ref is None:
                    thumb_h_ref = thumb.height

        n_rows = len(CONDITION_ORDER)
        n_cols = len(seeds)
        sheet_w = label_col_w + n_cols * (THUMB_W + PAD) + PAD
        sheet_h = LABEL_H + n_rows * (thumb_h_ref + LABEL_H + PAD) + PAD
        sheet = Image.new("RGB", (sheet_w, sheet_h), BG)
        draw = ImageDraw.Draw(sheet)
        draw.text((PAD, 4), f"{prompt_id}  —  QC contact sheet", fill=TEXT, font=font)

        for c_idx, seed in enumerate(seeds):
            x = label_col_w + c_idx * (THUMB_W + PAD) + PAD
            draw.text((x, LABEL_H), f"seed {seed}", fill=TEXT, font=font_small)

        y = LABEL_H + LABEL_H
        for cond in CONDITION_ORDER:
            draw.text((PAD, y + thumb_h_ref // 2 - 8), cond, fill=TEXT, font=font_small)
            for c_idx, seed in enumerate(seeds):
                x = label_col_w + c_idx * (THUMB_W + PAD) + PAD
                thumb = thumbs.get((cond, seed))
                if thumb is not None:
                    sheet.paste(thumb, (x, y))
            y += thumb_h_ref + LABEL_H + PAD

        out_path = out_dir / f"qc_{prompt_id}.png"
        sheet.save(out_path)
        print(f"  scritto {out_path}")
    print()


def step3_highlights(rows, prompt_scores_path: Path, out_dir: Path):
    print("=" * 70)
    print("STEP 3 — strip di evidenza per gli stili limite (V(p) max e min)")
    print("=" * 70)
    if not prompt_scores_path.exists():
        print(f"  {prompt_scores_path} non trovato: salto (serve per scegliere gli stili).")
        return

    scores = load_rows(prompt_scores_path)
    scores_sorted = sorted(scores, key=lambda r: float(r["V_p"]))
    worst = scores_sorted[0]
    best = scores_sorted[-1]
    targets = [("best", best), ("worst", worst)]

    by_prompt_cond_seed = {}
    for r in rows:
        by_prompt_cond_seed[(r["prompt_id"], r["condition"], r["seed"])] = r

    font = load_font(18)
    font_small = load_font(14)

    for tag, score_row in targets:
        prompt_id = score_row["prompt_id"]
        v_p = float(score_row["V_p"])
        # scegli il seed piu' piccolo disponibile per coerenza fra condizioni
        seeds = sorted(
            {r["seed"] for r in rows if r["prompt_id"] == prompt_id},
            key=lambda s: int(s),
        )
        seed = seeds[0]

        thumbs = []
        for cond in HIGHLIGHT_CONDITIONS:
            r = by_prompt_cond_seed.get((prompt_id, cond, seed))
            if r is None:
                print(f"  ATTENZIONE: manca {prompt_id}/{cond}/seed{seed}")
                continue
            p = resolve_path(r["image_path"])
            thumb = make_thumb(p, HIGHLIGHT_W) if p.exists() else Image.new(
                "RGB", (HIGHLIGHT_W, int(HIGHLIGHT_W * 1.3)), (235, 235, 235))
            thumbs.append((cond, thumb))

        if not thumbs:
            continue

        thumb_h = thumbs[0][1].height
        strip_w = len(thumbs) * (HIGHLIGHT_W + PAD) + PAD
        strip_h = 70 + thumb_h + LABEL_H
        strip = Image.new("RGB", (strip_w, strip_h), BG)
        draw = ImageDraw.Draw(strip)
        draw.text(
            (PAD, 8),
            f"{prompt_id}  ({'V(p) massimo' if tag == 'best' else 'V(p) minimo'} = {v_p:+.4f})  —  seed {seed}",
            fill=TEXT, font=font,
        )
        x = PAD
        for cond, thumb in thumbs:
            strip.paste(thumb, (x, 60))
            draw.text((x, 60 + thumb_h + 4), cond, fill=TEXT, font=font_small)
            x += HIGHLIGHT_W + PAD

        out_path = out_dir / f"highlight_{tag}_{prompt_id}.png"
        strip.save(out_path)
        print(f"  scritto {out_path}  (V(p)={v_p:+.4f})")
    print()


def main():
    print(f"REPO_DIR = {REPO_DIR}")
    rows = load_rows(STYLE_FEATURES_CSV)
    print(f"Righe lette da {STYLE_FEATURES_CSV.name}: {len(rows)}\n")

    missing, corrupt = step1_verify(rows)
    step2_contact_sheets(rows, OUT_DIR)
    step3_highlights(rows, PROMPT_SCORES_CSV, OUT_DIR)

    print("=" * 70)
    print(f"Fatto. Output in: {OUT_DIR}")
    if missing or corrupt:
        print(f"ATTENZIONE: {len(missing)} file mancanti, {len(corrupt)} corrotti — "
              "vedi lo STEP 1 sopra prima di fidarti dei contact sheet.")
    print("=" * 70)


if __name__ == "__main__":
    main()
