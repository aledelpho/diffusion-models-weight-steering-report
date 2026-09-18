#!/usr/bin/env python3
"""
extract_pilot_benchmarks.py
===========================
Lavoro A del BRIEF per la ri-analisi delle rotazioni dei benchmark pilota.

Legge i 9 file benchmark_*_report.html (escluso dryrun_v3) e produce:
- data/pilot_rotations.csv (216 rotX + 54 Block_3 altre rotazioni = 270 righe)
- data/pilot_macro.csv (216 righe sweep macro)

Cancelli di accettazione:
- Solleva eccezione se i conteggi non sono esattamente 216 / 54 / 216 / 9.
- Solleva eccezione se i prompt_id distinti non sono esattamente 7.
- Ogni clip_dist e cosine_sim nel CSV è letto verbatim dall'HTML.
"""

import os
import re
import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

BENCHMARK_DIR = r"C:\Users\aless\Desktop\comfyui-pilot"
OUTPUT_DIR = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data"

VALID_REPORTS = [
    "benchmark_african_scientist_report.html",
    "benchmark_combat_robot_report.html",
    "benchmark_elf_brawler_report.html",
    "benchmark_flag_report.html",
    "benchmark_preraphaelite_altar_report.html",
    "benchmark_tiefling_report.html",
    "benchmark_tiefling_seed1337_report.html",
    "benchmark_tiefling_seed42_report.html",
    "benchmark_troll_shaman_report.html",
]

CSV_FIELDNAMES = [
    "report",
    "prompt_id",
    "seed",
    "steps",
    "cfg",
    "family",
    "block",
    "rot_kind",
    "angle_deg",
    "amplitude",
    "image_rel",
    "clip_dist",
    "cosine_sim",
]

def extract_prompt_id(report_name: str) -> str:
    """Deriva prompt_id rimuovendo prefisso benchmark_, suffisso _report.html e qualsiasi _seed\\d+."""
    base = report_name.replace("benchmark_", "").replace("_report.html", "")
    base = re.sub(r"_seed\d+", "", base)
    return base

def extract_seed(html: str, report_name: str) -> int:
    """Estrae il seed dall'HTML o dal nome del file se specificato."""
    m = re.search(r'Seed(?:\s+Fissato)?:\s*<b>(\d+)</b>', html, re.IGNORECASE)
    if not m:
        m = re.search(r'Seed:\s*(\d+)', html, re.IGNORECASE)
    if m:
        return int(m.group(1))
    seed_m = re.search(r'_seed(\d+)', report_name)
    if seed_m:
        return int(seed_m.group(1))
    return 4242145

def parse_report(filepath: str, report_name: str):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    prompt_id = extract_prompt_id(report_name)
    seed = extract_seed(html, report_name)
    steps = 6
    cfg = 1.0

    rotX_rows = []
    rot_other_rows = []
    macro_rows = []
    baseline_rows = []

    # Regex per estrarre le card
    card_pattern = re.compile(
        r'<div class=\"card([^\"]*)\" data-rel=\"([^\"]*)\">.*?'
        r'<span class=\"card-title\">([^<]*)</span>.*?'
        r'<span class=\"card-badge\">([^<]*)</span>.*?'
        r'<span class=\"metric-value dist-val\">([^<]*)</span>.*?'
        r'<span class=\"metric-value\">([^<]*)</span>',
        re.DOTALL
    )

    found_baseline = False

    for match in card_pattern.finditer(html):
        classes, data_rel, title, badge, dist_str, cos_str = match.groups()
        classes = classes.strip()
        data_rel = data_rel.strip()
        title = title.strip()
        badge = badge.strip()
        dist = float(dist_str.strip())
        cos = float(cos_str.strip())

        is_baseline = (
            "baseline-card" in classes
            or "00_baseline" in data_rel
            or "Controllo Baseline" in title
            or "0.0 (Rif)" in badge
            or "0° (Rif)" in badge
        )

        if is_baseline:
            if not found_baseline and "00_baseline" in data_rel:
                baseline_rows.append({
                    "report": report_name,
                    "prompt_id": prompt_id,
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "family": "baseline",
                    "block": "None",
                    "rot_kind": "None",
                    "angle_deg": "",
                    "amplitude": 0.0,
                    "image_rel": data_rel,
                    "clip_dist": dist,
                    "cosine_sim": cos,
                })
                found_baseline = True
            continue

        # Macro sweep
        if data_rel.startswith("macro/") or "Tuning Macro Blocco" in title:
            m_macro = re.search(r'(Block_\d+)_([+-]?\d+\.?\d*)', data_rel)
            if not m_macro:
                m_macro = re.search(r'(Block_\d+)\s+([+-]?\d+\.?\d*)', title)
            if m_macro:
                block = m_macro.group(1)
                amp = float(m_macro.group(2))
                macro_rows.append({
                    "report": report_name,
                    "prompt_id": prompt_id,
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "family": "macro",
                    "block": block,
                    "rot_kind": "",
                    "angle_deg": "",
                    "amplitude": amp,
                    "image_rel": data_rel,
                    "clip_dist": dist,
                    "cosine_sim": cos,
                })

        # Rotazioni di asse
        elif data_rel.startswith("rotations/"):
            m_rotX = re.search(r'(Block_\d+)_rotX_([+-]?\d+\.?\d*)', data_rel)
            if m_rotX:
                block = m_rotX.group(1)
                angle = float(m_rotX.group(2))
                rotX_rows.append({
                    "report": report_name,
                    "prompt_id": prompt_id,
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "family": "rotX",
                    "block": block,
                    "rot_kind": "rotX",
                    "angle_deg": angle,
                    "amplitude": "",
                    "image_rel": data_rel,
                    "clip_dist": dist,
                    "cosine_sim": cos,
                })
            else:
                m_other = re.search(r'(Block_\d+)_([a-zA-Z0-9_]+)_([+-]?\d+\.?\d*)', data_rel)
                if m_other:
                    block = m_other.group(1)
                    rot_kind = m_other.group(2)
                    angle = float(m_other.group(3))
                    rot_other_rows.append({
                        "report": report_name,
                        "prompt_id": prompt_id,
                        "seed": seed,
                        "steps": steps,
                        "cfg": cfg,
                        "family": "rot_other",
                        "block": block,
                        "rot_kind": rot_kind,
                        "angle_deg": angle,
                        "amplitude": "",
                        "image_rel": data_rel,
                        "clip_dist": dist,
                        "cosine_sim": cos,
                    })

    return rotX_rows, rot_other_rows, macro_rows, baseline_rows

def main():
    print("=== LAVORO A: ESTRAZIONE BENCHMARK PILOTA ===")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_rotX = []
    all_rot_other = []
    all_macro = []
    all_baseline = []
    unique_prompts = set()

    for r_name in VALID_REPORTS:
        r_path = os.path.join(BENCHMARK_DIR, r_name)
        if not os.path.exists(r_path):
            raise FileNotFoundError(f"File non trovato: {r_path}")

        rotX, other, macro, base = parse_report(r_path, r_name)
        prompt_id = extract_prompt_id(r_name)
        unique_prompts.add(prompt_id)

        print(f"  {r_name:45s} -> prompt={prompt_id:20s} | rotX={len(rotX):2d} | other={len(other):2d} | macro={len(macro):2d} | base={len(base):2d}")

        all_rotX.extend(rotX)
        all_rot_other.extend(other)
        all_macro.extend(macro)
        all_baseline.extend(base)

    print("\n--- VERIFICA INTEGRITA' CANCELLI ---")
    print(f"  rotX estratti:       {len(all_rotX):4d} (atteso: 216)")
    print(f"  rot_other estratti:  {len(all_rot_other):4d} (atteso: 54)")
    print(f"  macro estratti:      {len(all_macro):4d} (atteso: 216)")
    print(f"  baseline estratti:   {len(all_baseline):4d} (atteso: 9)")
    print(f"  prompt_id unici:     {len(unique_prompts):4d} (atteso: 7) -> {sorted(list(unique_prompts))}")

    # CANCELLI LOUD-FAILING
    if len(all_rotX) != 216:
        raise AssertionError(f"CANCELLO FALLITO: rotX={len(all_rotX)}, atteso 216!")
    if len(all_rot_other) != 54:
        raise AssertionError(f"CANCELLO FALLITO: rot_other={len(all_rot_other)}, atteso 54!")
    if len(all_macro) != 216:
        raise AssertionError(f"CANCELLO FALLITO: macro={len(all_macro)}, atteso 216!")
    if len(all_baseline) != 9:
        raise AssertionError(f"CANCELLO FALLITO: baseline={len(all_baseline)}, atteso 9!")
    if len(unique_prompts) != 7:
        raise AssertionError(f"CANCELLO FALLITO: unique_prompts={len(unique_prompts)}, atteso 7!")

    # SCRITTURA CSV
    rotations_csv = os.path.join(OUTPUT_DIR, "pilot_rotations.csv")
    macro_csv = os.path.join(OUTPUT_DIR, "pilot_macro.csv")

    with open(rotations_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rotX)
        writer.writerows(all_rot_other)
    print(f"\n[OK] Scritto {rotations_csv} ({len(all_rotX) + len(all_rot_other)} righe)")

    with open(macro_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_macro)
    print(f"[OK] Scritto {macro_csv} ({len(all_macro)} righe)")

if __name__ == "__main__":
    main()
