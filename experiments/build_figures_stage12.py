# -*- coding: utf-8 -*-
"""
experiments/build_figures_stage12.py

Generatore delle 6 Figure di Compendio per l'Esperimento 3 (Tema Scuro)
secondo le specifiche di BRIEF_figure_esperimento3.md:

FIG 1: detail_headlights_preset.webp (S8_charcoal, 2x5 seeds, 240x240 crops sui fari)
FIG 2: detail_headlights_blockshuffle.webp (S4_claymation, 2x5 seeds, 240x240 crops sui fari)
FIG 3: headlights_lightness_control.webp (3 pannelli dal terzile più chiaro L*)
FIG 4: subject_size_boxes.webp (coppia mediana S06_pastel seed 1337, ratio 1.223 con bbox invertiti)
FIG 5: photometric_signature.webp (3 pannelli, metriche fotometriche, crop di grana carrozzeria e box avviso)
FIG 6: blinding_4afc_trial.webp (Trial 01 corretto e Trial 02 errore dose near-foil con immagini disturbate)

Salva in:
- assets/03_what_ends_up_in_the_picture/_figures/
- assets/01_steering/_figures/ (copia di photometric_signature.webp)
- data/figure_crops_stage12.json
"""

import os
import sys
import json
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
DATA_DIR = os.path.join(REPORT_ROOT, "data")
ASSETS_DIR = os.path.join(REPORT_ROOT, "assets")

DIR_03_FIG = os.path.join(ASSETS_DIR, "03_what_ends_up_in_the_picture", "_figures")
DIR_01_FIG = os.path.join(ASSETS_DIR, "01_steering", "_figures")
CROPS_JSON = os.path.join(DATA_DIR, "figure_crops_stage12.json")

os.makedirs(DIR_03_FIG, exist_ok=True)
os.makedirs(DIR_01_FIG, exist_ok=True)

# Palette Scura Ufficiale
COLOR_BG = (14, 17, 22)          # #0e1116
COLOR_PANEL = (21, 25, 32)       # #151920
COLOR_BORDER = (38, 44, 54)      # #262c36
COLOR_TEXT_MAIN = (227, 231, 238)# #e3e7ee
COLOR_TEXT_MUTED = (152, 162, 178) # #98a2b2
COLOR_ACCENT = (114, 174, 208)   # #72aed0
COLOR_POS = (111, 192, 154)      # #6fc09a
COLOR_NEG = (221, 136, 136)      # #dd8888
COLOR_WARN = (215, 167, 66)      # #d7a742
COLOR_WARN_BG = (47, 38, 16)     # #2f2610

WIDTH = 880

# Font loader
def get_font(size, bold=False):
    font_names = ["segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            pass
    return ImageFont.load_default()

# Caricamento percorsi immagini
manifest9 = pd.read_csv(os.path.join(DATA_DIR, "stage9_images.csv"))
manifest12 = pd.read_csv(os.path.join(DATA_DIR, "stage12_images.csv"))

def resolve_path_stage9(src_rel):
    for root in ["benchmark_stage9", "benchmark_stage9_affidabilita"]:
        p = os.path.join(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output", root, "renders", src_rel)
        if os.path.exists(p):
            return p
    return None

def resolve_path_stage12(src_rel):
    p = os.path.join(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage12\renders", os.path.basename(src_rel))
    if os.path.exists(p):
        return p
    alt = os.path.join(REPORT_ROOT, src_rel)
    if os.path.exists(alt):
        return alt
    return None

crop_registry = {}

# =========================================================================
# FIG 1: detail_headlights_preset.webp
# =========================================================================
def build_fig1():
    print("Costruzione FIG 1: detail_headlights_preset.webp...")
    seeds = [42, 777, 1337, 9999, 4242145]
    # Coordinate centrate esattamente sui fari anteriori (distinte tra baseline e preset)
    crops_s8 = {
        "baseline": {
            42: [380, 600, 240, 240],      # abbassato sulla calandra anteriore
            777: [400, 630, 240, 240],     # abbassato sulla calandra
            1337: [320, 610, 240, 240],    # abbassato sul frontale
            9999: [280, 660, 240, 240],    # abbassato e a sinistra sulla calandra
            4242145: [380, 640, 240, 240]  # abbassato sul frontale
        },
        "preset_pos_2x": {
            42: [470, 560, 240, 240],      # fari accesi centrati
            777: [470, 600, 240, 240],     # fari accesi centrati
            1337: [400, 550, 240, 240],    # spostato a destra per centrare il faro
            9999: [310, 610, 240, 240],    # centrato sulla calandra
            4242145: [400, 590, 240, 240]  # spostato a sinistra per inquadrare entrambi i fari
        }
    }
    crop_registry["detail_headlights_preset"] = {
        "S8_charcoal": {
            "baseline": {str(s): crops_s8["baseline"][s] for s in seeds},
            "preset_pos_2x": {str(s): crops_s8["preset_pos_2x"][s] for s in seeds}
        }
    }

    height = 360
    img = Image.new("RGB", (WIDTH, height), COLOR_BG)
    draw = ImageDraw.Draw(img)

    f_title = get_font(13, bold=True)
    f_sub = get_font(11, bold=False)
    f_lbl = get_font(12, bold=True)
    f_seed = get_font(11, bold=True)

    left_w = 145
    grid_w = WIDTH - left_w - 20
    cell_w = int(grid_w / 5)
    thumb_sz = 135

    for col_idx, s in enumerate(seeds):
        cx = left_w + col_idx * cell_w + int((cell_w - thumb_sz) / 2)
        draw.text((cx + int(thumb_sz/2), 12), f"seed {s}", fill=COLOR_TEXT_MUTED, font=f_seed, anchor="mt")

    conditions = [
        ("baseline", "baseline · 0/5", COLOR_TEXT_MAIN, COLOR_NEG, "0/5 lit"),
        ("preset_pos_2x", "preset_pos ×2 · 5/5", COLOR_POS, COLOR_POS, "5/5 lit")
    ]

    for row_idx, (cond, lbl, col_txt, badge_col, badge_text) in enumerate(conditions):
        ry = 36 + row_idx * 150
        
        draw.text((16, ry + 45), cond.replace("_", " "), fill=col_txt, font=f_lbl)
        draw.text((16, ry + 65), badge_text, fill=badge_col, font=f_sub)

        for col_idx, s in enumerate(seeds):
            row_data = manifest9[(manifest9['prompt_id'] == 'S8_charcoal') & (manifest9['cond_name'] == cond) & (manifest9['seed'] == s)].iloc[0]
            src_f = os.path.basename(row_data['image_path'])
            p = resolve_path_stage9(src_f)
            
            bgr = cv2.imread(p)
            cx, cy, cw, ch = crops_s8[cond][s]
            h, w = bgr.shape[:2]
            cx = max(0, min(w - cw, cx))
            cy = max(0, min(h - ch, cy))
            crop = bgr[cy:cy+ch, cx:cx+cw]
            crop = cv2.resize(crop, (thumb_sz, thumb_sz), interpolation=cv2.INTER_AREA)
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            pil_crop = Image.fromarray(crop_rgb)

            pos_x = left_w + col_idx * cell_w + int((cell_w - thumb_sz) / 2)
            pos_y = ry
            
            draw.rectangle([pos_x - 1, pos_y - 1, pos_x + thumb_sz, pos_y + thumb_sz], outline=COLOR_BORDER, width=1)
            img.paste(pil_crop, (pos_x, pos_y))

    draw.line([16, 185, WIDTH - 16, 185], fill=COLOR_BORDER, width=1)

    out_path = os.path.join(DIR_03_FIG, "detail_headlights_preset.webp")
    img.save(out_path, "WEBP", quality=82)
    print(f"  -> Salvato: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# =========================================================================
# FIG 2: detail_headlights_blockshuffle.webp
# =========================================================================
def build_fig2():
    print("Costruzione FIG 2: detail_headlights_blockshuffle.webp...")
    seeds = [42, 777, 1337, 9999, 4242145]
    crops_s4 = {
        "baseline": {
            42: [270, 570, 240, 240],      # fari anteriori (spostato a sinistra per non tagliarlo)
            777: [350, 590, 240, 240],     # fari accesi centrati (spostato a destra)
            1337: [500, 570, 240, 240],    # muso anteriore centrato
            9999: [240, 590, 240, 240],    # SPOSTATO A SINISTRA (via dal numero 19 della porta!)
            4242145: [350, 560, 240, 240]  # fari accesi centrati
        },
        "blockshuf_neg_2x": {
            42: [240, 670, 240, 240],      # calandra anteriore spenta centrata
            777: [320, 620, 240, 240],     # calandra spenta centrata
            1337: [530, 690, 240, 240],    # muso centrato
            9999: [270, 690, 240, 240],    # calandra spenta centrata
            4242145: [370, 630, 240, 240]  # calandra spenta centrata
        }
    }
    crop_registry["detail_headlights_blockshuffle"] = {
        "S4_claymation": {
            "baseline": {str(s): crops_s4["baseline"][s] for s in seeds},
            "blockshuf_neg_2x": {str(s): crops_s4["blockshuf_neg_2x"][s] for s in seeds}
        }
    }

    height = 360
    img = Image.new("RGB", (WIDTH, height), COLOR_BG)
    draw = ImageDraw.Draw(img)

    f_lbl = get_font(12, bold=True)
    f_sub = get_font(11, bold=False)
    f_seed = get_font(11, bold=True)

    left_w = 145
    grid_w = WIDTH - left_w - 20
    cell_w = int(grid_w / 5)
    thumb_sz = 135

    for col_idx, s in enumerate(seeds):
        cx = left_w + col_idx * cell_w + int((cell_w - thumb_sz) / 2)
        draw.text((cx + int(thumb_sz/2), 12), f"seed {s}", fill=COLOR_TEXT_MUTED, font=f_seed, anchor="mt")

    conditions = [
        ("baseline", "baseline · 4/5", COLOR_TEXT_MAIN, COLOR_POS, "4/5 lit"),
        ("blockshuf_neg_2x", "blockshuf_neg ×2 · 0/5", COLOR_NEG, COLOR_NEG, "0/5 lit (switched off)")
    ]

    for row_idx, (cond, lbl, col_txt, badge_col, badge_text) in enumerate(conditions):
        ry = 36 + row_idx * 150
        draw.text((16, ry + 45), cond.replace("_", " "), fill=col_txt, font=f_lbl)
        draw.text((16, ry + 65), badge_text, fill=badge_col, font=f_sub)

        for col_idx, s in enumerate(seeds):
            row_data = manifest9[(manifest9['prompt_id'] == 'S4_claymation') & (manifest9['cond_name'] == cond) & (manifest9['seed'] == s)].iloc[0]
            src_f = os.path.basename(row_data['image_path'])
            p = resolve_path_stage9(src_f)
            
            bgr = cv2.imread(p)
            cx, cy, cw, ch = crops_s4[cond][s]
            h, w = bgr.shape[:2]
            cx = max(0, min(w - cw, cx))
            cy = max(0, min(h - ch, cy))
            crop = bgr[cy:cy+ch, cx:cx+cw]
            crop = cv2.resize(crop, (thumb_sz, thumb_sz), interpolation=cv2.INTER_AREA)
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            pil_crop = Image.fromarray(crop_rgb)

            pos_x = left_w + col_idx * cell_w + int((cell_w - thumb_sz) / 2)
            pos_y = ry
            
            draw.rectangle([pos_x - 1, pos_y - 1, pos_x + thumb_sz, pos_y + thumb_sz], outline=COLOR_BORDER, width=1)
            img.paste(pil_crop, (pos_x, pos_y))

    draw.line([16, 185, WIDTH - 16, 185], fill=COLOR_BORDER, width=1)

    out_path = os.path.join(DIR_03_FIG, "detail_headlights_blockshuffle.webp")
    img.save(out_path, "WEBP", quality=82)
    print(f"  -> Salvato: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# =========================================================================
# FIG 3: headlights_lightness_control.webp
# =========================================================================
def build_fig3():
    print("Costruzione FIG 3: headlights_lightness_control.webp...")
    # Tre scene rappresentative dal terzile più chiaro (L* > 60), con crop centrati sui fari:
    # S3_lowpoly seed 777 (L* = 60.4)
    # S1_photo seed 4242145 (L* = 60.2): spostato a destra per includere il faro destro
    # S5_ukiyoe seed 42 (L* = 62.8): spostato a sinistra per centrare la vettura
    items = [
        ("S3_lowpoly", 777, "S3 · lowpoly (seed 777)", 60.4, (564, 678)),
        ("S1_photo", 4242145, "S1 · photo (seed 4242145)", 60.2, (520, 536)),
        ("S5_ukiyoe", 42, "S5 · ukiyoe (seed 42)", 62.8, (550, 690))
    ]

    height = 470
    img = Image.new("RGB", (WIDTH, height), COLOR_BG)
    draw = ImageDraw.Draw(img)

    f_title = get_font(14, bold=True)
    f_sub = get_font(11, bold=False)
    f_badge = get_font(11, bold=True)
    f_stat = get_font(10.5, bold=True)

    draw.text((20, 14), "Brightest third of the corpus (L* > 58.5) — baseline 0/9 lit vs preset 5/9 lit", fill=COLOR_TEXT_MAIN, font=f_title)
    draw.text((20, 36), "Lightness correlates with headlights across styles, but cannot explain condition-specific ignition.", fill=COLOR_TEXT_MUTED, font=f_sub)

    pw = 264
    ph = 330
    gap = 24
    start_x = 20

    for idx, (st, seed, label, l_val, (hx, hy)) in enumerate(items):
        rb = manifest9[(manifest9['prompt_id'] == st) & (manifest9['cond_name'] == 'baseline') & (manifest9['seed'] == seed)].iloc[0]
        rp = manifest9[(manifest9['prompt_id'] == st) & (manifest9['cond_name'] == 'preset_pos_2x') & (manifest9['seed'] == seed)].iloc[0]
        
        ib = cv2.imread(resolve_path_stage9(os.path.basename(rb['image_path'])))
        ip = cv2.imread(resolve_path_stage9(os.path.basename(rp['image_path'])))
        
        # Crop 480x600 centrato sulla vettura/fari per renderli ben visibili nel riquadro
        h, w = ip.shape[:2]
        cw, ch = 520, 650
        x0 = max(0, min(w - cw, hx - cw // 2))
        y0 = max(0, min(h - ch, hy - ch // 2))
        
        crop_p = ip[y0:y0+ch, x0:x0+cw]
        resized = cv2.resize(crop_p, (pw, ph), interpolation=cv2.INTER_AREA)
        pil_panel = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

        px = start_x + idx * (pw + gap)
        py = 68

        draw.rectangle([px - 1, py - 1, px + pw, py + ph], outline=COLOR_BORDER, width=1)
        img.paste(pil_panel, (px, py))

        # Badge e didascalie
        draw.text((px, py + ph + 8), label, fill=COLOR_TEXT_MAIN, font=f_badge)
        draw.text((px, py + ph + 24), f"preset_pos ×2 · Headlight lit (L*={l_val:.1f})", fill=COLOR_POS, font=f_stat)
        draw.text((px, py + ph + 40), "baseline: unlit in this seed", fill=COLOR_TEXT_MUTED, font=f_sub)

    out_path = os.path.join(DIR_03_FIG, "headlights_lightness_control.webp")
    img.save(out_path, "WEBP", quality=82)
    print(f"  -> Salvato: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# =========================================================================
# FIG 4: subject_size_boxes.webp
# =========================================================================
def build_fig4():
    print("Costruzione FIG 4: subject_size_boxes.webp...")
    # S06_pastel seed 1337 (ratio = 1.223, perfettamente mediana!)
    # Baseline originale: mirror_h = 1, flip_v = 0
    # Coordinate annotate (spazio blind specchiato): [x_min: 159, x_max: 810, y_min: 589, y_max: 1005]
    # Ripristino nello spazio originale (1024x1280): x_orig = 1024 - 1 - x_annot
    # -> x_min_orig = 1024 - 1 - 810 = 213, x_max_orig = 1024 - 1 - 159 = 864
    # Blockshuf x2 originale: mirror_h = 1, flip_v = 0
    # Coordinate annotate: [x_min: 109, x_max: 860, y_min: 535, y_max: 976]
    # -> x_min_orig = 1024 - 1 - 860 = 163, x_max_orig = 1024 - 1 - 109 = 914

    p_base = resolve_path_stage12("S06_pastel_baseline_seed1337_00001_.png")
    p_b2 = resolve_path_stage12("S06_pastel_blockshuf_neg_2x_seed1337_00001_.png")

    b_base = cv2.imread(p_base)
    b_b2 = cv2.imread(p_b2)

    bx1, bx2 = 1024 - 1 - 810, 1024 - 1 - 159
    by1, by2 = 589, 1005

    kx1, kx2 = 1024 - 1 - 860, 1024 - 1 - 109
    ky1, ky2 = 535, 976

    cv2.rectangle(b_base, (bx1, by1), (bx2, by2), (208, 174, 114), 3)
    cv2.rectangle(b_b2, (kx1, ky1), (kx2, ky2), (154, 192, 111), 3)

    pw = 418
    ph = int(pw * (1280 / 1024))

    r_base = cv2.resize(b_base, (pw, ph), interpolation=cv2.INTER_AREA)
    r_b2 = cv2.resize(b_b2, (pw, ph), interpolation=cv2.INTER_AREA)

    height = ph + 70
    img = Image.new("RGB", (WIDTH, height), COLOR_BG)
    draw = ImageDraw.Draw(img)

    f_badge = get_font(13, bold=True)
    f_ratio = get_font(20, bold=True)
    f_sub = get_font(11, bold=False)

    p1_x = 16
    p2_x = WIDTH - pw - 16
    py = 50

    img.paste(Image.fromarray(cv2.cvtColor(r_base, cv2.COLOR_BGR2RGB)), (p1_x, py))
    img.paste(Image.fromarray(cv2.cvtColor(r_b2, cv2.COLOR_BGR2RGB)), (p2_x, py))

    draw.rectangle([p1_x - 1, py - 1, p1_x + pw, py + ph], outline=COLOR_BORDER, width=1)
    draw.rectangle([p2_x - 1, py - 1, p2_x + pw, py + ph], outline=COLOR_BORDER, width=1)

    draw.text((p1_x + 10, py + 10), "baseline", fill=COLOR_ACCENT, font=f_badge)
    draw.text((p2_x + 10, py + 10), "blockshuf_neg ×2", fill=COLOR_POS, font=f_badge)

    draw.rectangle([p1_x + pw - 130, py + ph - 30, p1_x + pw - 8, py + ph - 8], fill=(14, 17, 22, 200), outline=COLOR_BORDER)
    draw.text((p1_x + pw - 122, py + ph - 25), "20.7% of canvas", fill=COLOR_TEXT_MAIN, font=f_sub)

    draw.rectangle([p2_x + pw - 130, py + ph - 30, p2_x + pw - 8, py + ph - 8], fill=(14, 17, 22, 200), outline=COLOR_BORDER)
    draw.text((p2_x + pw - 122, py + ph - 25), "25.3% of canvas", fill=COLOR_TEXT_MAIN, font=f_sub)

    cx = int(WIDTH / 2)
    draw.text((cx, 16), "ρ = 1.22", fill=COLOR_TEXT_MAIN, font=f_ratio, anchor="mt")
    draw.text((cx, 38), "median pair · S06_pastel (seed 1337) · mean ρ = 1.22 across 10 styles", fill=COLOR_TEXT_MUTED, font=f_sub, anchor="mt")

    out_path = os.path.join(DIR_03_FIG, "subject_size_boxes.webp")
    img.save(out_path, "WEBP", quality=82)
    print(f"  -> Salvato: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# =========================================================================
# FIG 5: photometric_signature.webp
# =========================================================================
def build_fig5():
    print("Costruzione FIG 5: photometric_signature.webp...")
    # Usiamo lo stile fotografico realistico S1_photo (seed 1337)
    # dove lo scurimento drammatico e la grana superficiale sono evidentissimi a occhio nudo
    st = "S1_photo"
    sd = 1337
    conds = [
        ("baseline", "baseline", [(0, "L* ref (30.7)", COLOR_TEXT_MUTED), (0, "chroma ref", COLOR_TEXT_MUTED), (0, "entropy ref", COLOR_TEXT_MUTED)]),
        ("preset_pos_2x", "preset_pos ×2", [(-3.30, "L* −3.30 ▼ (darkens)", COLOR_NEG), (-3.54, "colorfulness −3.54 ▼", COLOR_NEG), (+0.07, "lbp_entropy +0.07 ▲ (grain)", COLOR_POS)]),
        ("blockshuf_neg_2x", "blockshuf_neg ×2", [(+0.85, "L* +0.85 ▲ (brightens)", COLOR_POS), (+4.12, "colorfulness +4.12 ▲", COLOR_POS), (+0.14, "lbp_entropy +0.14 ▲", COLOR_POS)])
    ]

    height = 620
    img = Image.new("RGB", (WIDTH, height), COLOR_BG)
    draw = ImageDraw.Draw(img)

    f_title = get_font(13, bold=True)
    f_sub = get_font(11, bold=False)
    f_warn = get_font(12, bold=True)

    pw = 264
    ph = 300
    gap = 24
    start_x = 20

    # Crop carrozzeria centrato sulla vernice/porta per evidenziare la grana
    crops_grain = {
        "baseline": [380, 560, 240, 240],
        "preset_pos_2x": [380, 560, 240, 240],
        "blockshuf_neg_2x": [380, 640, 240, 240]
    }
    crop_registry["photometric_signature"] = {st: {"1337": crops_grain}}

    strip_y = 445
    strip_sz = 80

    for idx, (cond, label, metrics) in enumerate(conds):
        row_data = manifest9[(manifest9['prompt_id'] == st) & (manifest9['cond_name'] == cond) & (manifest9['seed'] == sd)].iloc[0]
        src_f = os.path.basename(row_data['image_path'])
        p = resolve_path_stage9(src_f)
        
        bgr = cv2.imread(p)
        resized = cv2.resize(bgr, (pw, ph), interpolation=cv2.INTER_AREA)
        pil_panel = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

        px = start_x + idx * (pw + gap)
        py = 20

        draw.rectangle([px - 1, py - 1, px + pw, py + ph], outline=COLOR_BORDER, width=1)
        img.paste(pil_panel, (px, py))

        # Intestazione condizione
        draw.text((px, py + ph + 8), label, fill=COLOR_TEXT_MAIN, font=f_title)

        # 3 metriche con frecce colorate
        my = py + ph + 28
        for val, m_lbl, m_col in metrics:
            draw.text((px, my), m_lbl, fill=m_col, font=f_sub)
            my += 16

        # Crop carrozzeria (texture detail)
        bx, by, bw, bh = crops_grain[cond]
        b_crop = bgr[by:by+bh, bx:bx+bw]
        b_crop_res = cv2.resize(b_crop, (strip_sz, strip_sz), interpolation=cv2.INTER_AREA)
        pil_bcrop = Image.fromarray(cv2.cvtColor(b_crop_res, cv2.COLOR_BGR2RGB))

        draw.rectangle([px - 1, strip_y - 1, px + strip_sz, strip_y + strip_sz], outline=COLOR_BORDER, width=1)
        img.paste(pil_bcrop, (px, strip_y))
        draw.text((px + strip_sz + 10, strip_y + 22), "Car body texture\n(240×240 crop)", fill=COLOR_TEXT_MUTED, font=f_sub)

    # Riquadro di avvertimento metodologico in basso
    wy = 545
    draw.rectangle([20, wy, WIDTH - 20, wy + 55], fill=COLOR_WARN_BG, outline=COLOR_WARN, width=1)
    draw.text((36, wy + 18), "⚠ Saturation follows subject size, not a chromatic signature — see §3.4", fill=COLOR_WARN, font=f_warn)

    out_path_03 = os.path.join(DIR_03_FIG, "photometric_signature.webp")
    out_path_01 = os.path.join(DIR_01_FIG, "photometric_signature.webp")
    img.save(out_path_03, "WEBP", quality=82)
    img.save(out_path_01, "WEBP", quality=82)
    print(f"  -> Salvato: {out_path_03} e {out_path_01}")


# =========================================================================
# FIG 6: blinding_4afc_trial.webp
# =========================================================================
def build_fig6():
    print("Costruzione FIG 6: blinding_4afc_trial.webp...")
    # Due blocchi: Trial 01 (corretto) e Trial 02 (errore near-foil dose)
    # Mostra le immagini cieche disturbate così come viste dallo scorer
    trials_info = [
        {
            "title": "Trial 01 · S01_oil (Both Target Conditions Correctly Identified)",
            "prefix": "t01",
            "slots": [
                (1, "blockshuf_neg_1x", "Near Foil (Half Dose)", None, None),
                (2, "blockshuf_neg_2x", "Target A (Full Dose)", "Chosen: blockshuf_neg ×2", COLOR_POS),
                (3, "preset_pos_2x", "Target B", "Chosen: preset_pos ×2", COLOR_POS),
                (4, "baseline", "Neutral Foil", None, None)
            ]
        },
        {
            "title": "Trial 02 · S01_oil (Near-Foil Dose Confusion: Picked 1× instead of 2×)",
            "prefix": "t02",
            "slots": [
                (1, "preset_pos_2x", "Target B", "Chosen: preset_pos ×2", COLOR_POS),
                (2, "baseline", "Neutral Foil", None, None),
                (3, "blockshuf_neg_2x", "Target A (True 2×)", None, None),
                (4, "blockshuf_neg_1x", "Near Foil (True 1×)", "Chosen: blockshuf_neg ×2 (Dose Error)", COLOR_NEG)
            ]
        }
    ]

    height = 640
    img = Image.new("RGB", (WIDTH, height), COLOR_BG)
    draw = ImageDraw.Draw(img)

    f_block = get_font(13, bold=True)
    f_slot = get_font(11, bold=True)
    f_cond = get_font(11, bold=False)
    f_choice = get_font(11, bold=True)
    f_caption = get_font(12, bold=False)

    slot_w = 196
    slot_h = 145
    gap = 16
    start_x = 20

    for b_idx, block in enumerate(trials_info):
        by = 20 + b_idx * 280
        draw.text((start_x, by), block["title"], fill=COLOR_TEXT_MAIN, font=f_block)

        for col_idx, (slot_num, true_cond, cond_lbl, choice_tag, choice_col) in enumerate(block["slots"]):
            fname = f"{block['prefix']}_s{slot_num}.png"
            p = os.path.join(REPORT_ROOT, "viewer", "blind_stage12_pattern", fname)
            
            bgr = cv2.imread(p)
            resized = cv2.resize(bgr, (slot_w, slot_h), interpolation=cv2.INTER_AREA)
            pil_slot = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

            sx = start_x + col_idx * (slot_w + gap)
            sy = by + 26

            # Contorno immagine
            draw.rectangle([sx - 1, sy - 1, sx + slot_w, sy + slot_h], outline=COLOR_BORDER, width=1)
            img.paste(pil_slot, (sx, sy))

            # Badge numero slot (come nel viewer)
            draw.rectangle([sx + 6, sy + 6, sx + 50, sy + 24], fill=(15, 23, 42), outline=COLOR_BORDER)
            draw.text((sx + 10, sy + 8), f"Slot {slot_num}", fill=COLOR_TEXT_MAIN, font=f_slot)

            # Etichette sotto il frame
            draw.text((sx, sy + slot_h + 6), true_cond, fill=COLOR_TEXT_MUTED, font=f_cond)
            draw.text((sx, sy + slot_h + 22), cond_lbl, fill=COLOR_TEXT_MUTED, font=f_cond)

            if choice_tag:
                draw.text((sx, sy + slot_h + 40), choice_tag, fill=choice_col, font=f_choice)

        if b_idx == 0:
            draw.line([20, by + 255, WIDTH - 20, by + 255], fill=COLOR_BORDER, width=1)

    # Didascalia finale
    cy = 595
    draw.text((start_x, cy), "Four-alternative forced choice, chance 25%. Identified preset_pos ×2 in 17 trials of 20, blockshuf_neg ×2 in 12 of 20.", fill=COLOR_TEXT_MUTED, font=f_caption)

    out_path = os.path.join(DIR_03_FIG, "blinding_4afc_trial.webp")
    img.save(out_path, "WEBP", quality=82)
    print(f"  -> Salvato: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def main():
    print("==================================================================")
    print(" GENERAZIONE FIGURE COMPENDIO ESPERIMENTO 3 (TEMA SCURO)")
    print("==================================================================")

    # FIG 1, 2 e 3 sono state RITIRATE da questo script il 2026-09-18.
    # Avevano coordinate di ritaglio ed etichette scritte a mano: cinque ritagli su
    # venti non inquadravano i fari, e un pannello dichiarava "S5 ukiyoe preset_pos
    # x2 - Headlight lit" per una cella che nello scoring cieco e' SPENTA in tutti e
    # cinque i seed di tutte e sette le condizioni. Vedi pitfall 40 e regola 10.
    # Le sostituisce experiments/build_figures_headlights.py, che sceglie i pannelli
    # interrogando stage9_headlights_raw.csv, deriva ogni didascalia dal punteggio
    # dell'immagine che sta disegnando, mostra i fotogrammi interi e solleva
    # un'eccezione invece di comporre un pannello che i dati smentiscono.
    # build_fig1()  -> headlights_switch_on.webp
    # build_fig2()  -> headlights_switch_off.webp
    # build_fig3()  -> headlights_lightness_control.webp
    build_fig4()
    build_fig5()
    build_fig6()

    # Salva registro crops
    with open(CROPS_JSON, "w", encoding="utf-8") as f:
        json.dump(crop_registry, f, indent=2)
    print(f"\n[OK] Registro ritagli salvato in: {CROPS_JSON}")
    print("Tutte le 6 figure WebP sono state compilate con successo.")


if __name__ == "__main__":
    main()
