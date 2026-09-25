# -*- coding: utf-8 -*-
"""
experiments/print_atlas_regions.py
==================================
Defines and prints the perturbation atlas regions per:
  - docs/prereg_perturbation_atlas_amendment_01.md (§2: 4 depth bands x 2 components + 2 degenerate)
  - docs/prereg_perturbation_atlas_amendment_03.md (§3: uniform_all added)
  - docs/prereg_perturbation_atlas_amendment_04.md (§3: modulation_norm and txtfusion added, 13 conditions)

Outputs:
  - data/perturbation_atlas_regions.csv
"""

import csv
import json
import os
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
BASE_PRESET_PATH = ROOT / "presets" / "Arthemy_Bench_Base.json"
OUT_CSV = ROOT / "data" / "perturbation_atlas_regions.csv"

TOTAL_MODEL_TENSORS = 430

def main():
    with open(BASE_PRESET_PATH, encoding="utf-8") as f:
        b = json.load(f)

    m_keys = sorted(b["model_patches"].keys())
    c_keys = sorted(b["clip_patches"].keys())

    bands = [
        ("early", list(range(0, 7)), "0-6", 7),
        ("early_mid", list(range(7, 14)), "7-13", 7),
        ("late_mid", list(range(14, 21)), "14-20", 7),
        ("late", list(range(21, 28)), "21-27", 7),
    ]

    components = [
        ("attn", "blocks.{i}.attn.*"),
        ("mlp", "blocks.{i}.mlp.*"),
    ]

    regions = []
    # Set of keys covered by the specific sub-model regions (8 depth + modulation_norm + txtfusion)
    accounted_model_keys = set()

    # 1-8. Depth x component regions
    for band_name, block_list, block_str, n_blocks in bands:
        for comp_name, pat_template in components:
            reg_name = f"{band_name}_{comp_name}"
            matched_m = [
                k for k in m_keys
                if any(k.startswith(f"blocks.{i}.{comp_name}.") for i in block_list)
            ]
            accounted_model_keys.update(matched_m)
            n_m = len(matched_m)
            regions.append({
                "region": reg_name,
                "domain": "model",
                "block_indices": block_str,
                "tensor_pattern": f"blocks.[{block_str}].{comp_name}.*",
                "n_model_tensors": n_m,
                "n_clip_tensors": 0,
                "total_tensors": n_m,
                "mean_tensors_per_block": round(n_m / n_blocks, 4),
                "share_of_model_tensors": round(n_m / TOTAL_MODEL_TENSORS, 4),
            })

    # 9. modulation_norm (Amendment 04: mod.lin, prenorm.scale, postnorm.scale across all 28 blocks)
    mod_norm_m = [
        k for k in m_keys
        if re.match(r"blocks\.\d+\.(mod\.lin|prenorm\.scale|postnorm\.scale)$", k)
    ]
    accounted_model_keys.update(mod_norm_m)
    n_mod = len(mod_norm_m)
    regions.append({
        "region": "modulation_norm",
        "domain": "model",
        "block_indices": "0-27 (all blocks)",
        "tensor_pattern": "blocks.[0-27].{mod.lin, prenorm.scale, postnorm.scale}",
        "n_model_tensors": n_mod,
        "n_clip_tensors": 0,
        "total_tensors": n_mod,
        "mean_tensors_per_block": round(n_mod / 28.0, 4),
        "share_of_model_tensors": round(n_mod / TOTAL_MODEL_TENSORS, 4),
    })

    # 10. txtfusion (Amendment 04: txtfusion.*)
    txtfusion_m = [k for k in m_keys if k.startswith("txtfusion.")]
    accounted_model_keys.update(txtfusion_m)
    n_txt = len(txtfusion_m)
    regions.append({
        "region": "txtfusion",
        "domain": "model",
        "block_indices": "adapters (txtfusion)",
        "tensor_pattern": "txtfusion.*",
        "n_model_tensors": n_txt,
        "n_clip_tensors": 0,
        "total_tensors": n_txt,
        "mean_tensors_per_block": 0.0,
        "share_of_model_tensors": round(n_txt / TOTAL_MODEL_TENSORS, 4),
    })

    # 11. clip_only (Amendment 01: all CLIP patched tensors, no model patch)
    regions.append({
        "region": "clip_only",
        "domain": "clip",
        "block_indices": "none",
        "tensor_pattern": "all CLIP patched tensors",
        "n_model_tensors": 0,
        "n_clip_tensors": len(c_keys),
        "total_tensors": len(c_keys),
        "mean_tensors_per_block": 0.0,
        "share_of_model_tensors": 0.0,
    })

    # 12. model_only (Amendment 01: all model patched tensors, no CLIP patch)
    regions.append({
        "region": "model_only",
        "domain": "model",
        "block_indices": "0-27 (all model)",
        "tensor_pattern": "all model patched tensors",
        "n_model_tensors": len(m_keys),
        "n_clip_tensors": 0,
        "total_tensors": len(m_keys),
        "mean_tensors_per_block": round(len(m_keys) / 28.0, 4),
        "share_of_model_tensors": 1.0,
    })

    # 13. uniform_all (Amendment 03: all model and CLIP patched tensors)
    regions.append({
        "region": "uniform_all",
        "domain": "both",
        "block_indices": "0-27 + CLIP",
        "tensor_pattern": "all model and CLIP patched tensors",
        "n_model_tensors": len(m_keys),
        "n_clip_tensors": len(c_keys),
        "total_tensors": len(m_keys) + len(c_keys),
        "mean_tensors_per_block": round(len(m_keys) / 28.0, 4),
        "share_of_model_tensors": 1.0,
    })

    # 14. Uncovered remainder (17 tensors)
    uncovered_keys = sorted(set(m_keys) - accounted_model_keys)
    uncovered_counts = Counter(k.split(".")[0] for k in uncovered_keys)
    uncovered_desc = ", ".join(f"{pfx}: {cnt}" for pfx, cnt in sorted(uncovered_counts.items()))

    regions.append({
        "region": "uncovered",
        "domain": "model",
        "block_indices": "non-block inputs/outputs/projections",
        "tensor_pattern": f"17 residual tensors ({uncovered_desc})",
        "n_model_tensors": len(uncovered_keys),
        "n_clip_tensors": 0,
        "total_tensors": len(uncovered_keys),
        "mean_tensors_per_block": 0.0,
        "share_of_model_tensors": round(len(uncovered_keys) / TOTAL_MODEL_TENSORS, 4),
    })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "region", "domain", "block_indices", "tensor_pattern",
        "n_model_tensors", "n_clip_tensors", "total_tensors",
        "mean_tensors_per_block", "share_of_model_tensors"
    ]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(regions)

    print(f"=== PERTURBATION ATLAS: REGIONS DEFINITION (13 conditions + uncovered) ===")
    print(f"{'Region':16s} | {'Domain':6s} | {'Blocks':20s} | {'Tensors':7s} | {'Mean/Blk':8s} | {'ModelShare':10s} | Tensor Pattern")
    print("-" * 135)
    for r in regions:
        print(f"{r['region']:16s} | {r['domain']:6s} | {r['block_indices']:20s} | {r['total_tensors']:7d} | {r['mean_tensors_per_block']:8.2f} | {r['share_of_model_tensors']:10.4f} | {r['tensor_pattern']}")
    print(f"\nWrote {OUT_CSV}")

if __name__ == "__main__":
    main()
