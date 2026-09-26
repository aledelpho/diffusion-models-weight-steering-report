# -*- coding: utf-8 -*-
"""
experiments/build_qkvo_presets.py
=================================
Builds the 18 presets for the QKVO Atlas (RUNBOOK_qkvo_atlas_plan_1.md §7.1):
  - 16 live conditions: {wq, wk, wv, wo} x {b1, b6} x {pos, neg}
  - 2 controls: normscales over all blocks (0-27) x {pos, neg}

Saves to both:
  - C:\\StabilityMatrix-win-x64\\Data\\Packages\\ComfyUI\\custom_nodes\\Arthemy_Krea2_Tuner\\presets\\
  - presets/ in the report repository

Then verifies each preset via ArthemyKrea2PresetLoader, writes
data/qkvo_preset_layer_counts.csv, and checks §7.4 safety gates.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Set, Any

ROOT = Path(__file__).resolve().parent.parent
COMFY_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI")
SUITE_DIR = COMFY_ROOT / "custom_nodes" / "Arthemy_Krea2_Tuner"
PRESET_DIR_NODE = SUITE_DIR / "presets"
PRESET_DIR_REPO = ROOT / "presets"
DATA_DIR = ROOT / "data"
MODELS_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Models")

sys.path.insert(0, str(COMFY_ROOT))
sys.path.append(str(SUITE_DIR))

import safetensors
import torch
from Arthemy_Krea2_Tuner import (
    Krea2TensorParser,
    ArthemyKrea2ModelBlockSurgeonTuner,
    ArthemyKrea2PresetLoader,
)

MODEL_FILE = "krea2_turbo_bf16.safetensors"
SOFT_DAMPENING_FACTOR = 0.10  # 1.0 in Soft Value -> +0.10 offset multiplier


def find_model(fn: str) -> Path:
    for root, _d, files in os.walk(MODELS_ROOT):
        if fn in files:
            return Path(root) / fn
    raise FileNotFoundError(fn)


def build_preset_dict(
    name: str,
    patches: Dict[str, float],
    author: str = "Antigravity (Block J)"
) -> Dict[str, Any]:
    return {
        "name": name,
        "author": author,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": "2.1",
        "suite_rotation_effective": True,
        "stats": {
            "model_patched_layers": len(patches),
            "model_granular_layers": 0,
            "clip_patched_layers": 0,
            "clip_granular_layers": 0,
            "chaos_recipes_count": 0,
            "rotation_recipes_count": 0,
            "chaos_rotation_recipes_count": 0,
            "channel_recipes_count": 0,
            "five_d_recipes_count": 0,
            "excluded_lora_tensors": 0,
        },
        "model_patches": patches,
        "model_granular_patches": {},
        "clip_patches": {},
        "clip_granular_patches": {},
        "chaos_recipes": [],
        "rotation_recipes": [],
        "chaos_rotation_recipes": [],
        "channel_recipes": [],
        "five_d_recipes": [],
    }


def main():
    print("=== COSTRUZIONE DEI 18 PRESET QKVO ATLAS (RUNBOOK §7.1) ===")
    m_path = find_model(MODEL_FILE)
    print(f"Modello DiT individuato: {m_path}")

    # Estrazione delle chiavi reali del modello
    with safetensors.safe_open(str(m_path), framework="pt", device="cpu") as f:
        clean_keys = [Krea2TensorParser.clean_key(k) for k in f.keys()]

    target_map = ArthemyKrea2ModelBlockSurgeonTuner.MODEL_TARGET_MAP
    b1_indices = target_map["Block_1 (All 0-4)"]
    b6_indices = target_map["Block_6 (All 24-27)"]
    all_indices = target_map["All Blocks (0-27)"]

    components = {
        "wq": "ATTN_wq_query",
        "wk": "ATTN_wk_key",
        "wv": "ATTN_wv_value",
        "wo": "ATTN_wo_out",
    }
    bands = {
        "b1": b1_indices,
        "b6": b6_indices,
    }
    signs = {
        "pos": 1.0 * SOFT_DAMPENING_FACTOR,   # +0.10
        "neg": -1.0 * SOFT_DAMPENING_FACTOR,  # -0.10
    }

    # Creazione delle definizioni dei 18 preset
    preset_definitions = {}

    # 1. 16 condizioni live
    for comp_code, widget_name in components.items():
        for band_code, band_set in bands.items():
            for sign_code, delta_val in signs.items():
                preset_name = f"Arthemy_QKVO_{comp_code}_{band_code}_{sign_code}"
                # Filtra le chiavi dei tensori corrispondenti
                matched_tensors = {}
                for k in clean_keys:
                    idx, sub = Krea2TensorParser.extract_model_block_idx(k)
                    if idx is not None and idx in band_set:
                        if Krea2TensorParser.match_model_sub_tensor(sub) == widget_name:
                            matched_tensors[k] = round(delta_val, 6)
                preset_definitions[preset_name] = matched_tensors

    # 2. 2 controlli negativi (normscales_all)
    for sign_code, delta_val in signs.items():
        preset_name = f"Arthemy_QKVO_normscales_all_{sign_code}"
        matched_tensors = {}
        for k in clean_keys:
            idx, sub = Krea2TensorParser.extract_model_block_idx(k)
            if idx is not None and idx in all_indices:
                if Krea2TensorParser.match_model_sub_tensor(sub) == "NORMS_block_scales":
                    matched_tensors[k] = round(delta_val, 6)
        preset_definitions[preset_name] = matched_tensors

    print(f"\nDefiniti {len(preset_definitions)} preset:")
    PRESET_DIR_NODE.mkdir(parents=True, exist_ok=True)
    PRESET_DIR_REPO.mkdir(parents=True, exist_ok=True)

    for pname, patches in preset_definitions.items():
        p_obj = build_preset_dict(pname, patches)
        for pdir in [PRESET_DIR_NODE, PRESET_DIR_REPO]:
            out_file = pdir / f"{pname}.json"
            with open(out_file, "w", encoding="utf-8") as fh:
                json.dump(p_obj, fh, indent=2, ensure_ascii=False)
        print(f"  - {pname:38s}: {len(patches):2d} layer(s)")

    # 3. Verifica con Preset Loader
    print("\n=== VERIFICA CON ARTHEMY PRESET LOADER ===")
    loader = ArthemyKrea2PresetLoader()

    # Creazione di un mock patcher minimale con lo state dict delle sole chiavi
    class MinimalModel:
        def __init__(self, keys_list):
            self._keys = {k: torch.empty(0, dtype=torch.bfloat16) for k in keys_list}
        def state_dict(self):
            return self._keys

    class MinimalPatcher:
        def __init__(self, keys_list):
            self.model = MinimalModel(keys_list)
            self.model_keys = set(keys_list)
            self.patches = {}
            self.object_patches = {}
            self.backup = {}
        def clone(self):
            c = MinimalPatcher([])
            c.model = self.model
            c.model_keys = self.model_keys
            return c

    dummy_model = MinimalPatcher(clean_keys)
    dummy_clip = MinimalPatcher([])

    layer_count_records = []
    zero_layer_live_count = 0

    for pname in preset_definitions:
        preset_file = f"{pname}.json"
        _m, _c, info_text = loader.load_preset(
            dummy_model, dummy_clip, preset=pname, custom_path=str(PRESET_DIR_REPO / preset_file)
        )
        # Parse info_text:
        # info_parts: ["Loaded Preset '...' by ...", "Model: N scalar layers, 0 granular layers (x1.00)", ...]
        lines = [line.strip() for line in info_text.split(" | ")]
        model_line = next((l for l in lines if l.startswith("Model:")), "")
        if not model_line:
            # Fallback direct search in text
            import re
            m = re.search(r"Model:\s*(\d+)\s*scalar layers", info_text)
            n_layers = int(m.group(1)) if m else 0
            model_line = f"Model: {n_layers} scalar layers"
        else:
            import re
            m = re.search(r"Model:\s*(\d+)\s*scalar layers", model_line)
            n_layers = int(m.group(1)) if m else 0

        layer_count_records.append({
            "preset": pname,
            "layer_count": n_layers,
            "info_line": model_line
        })
        print(f"  {pname:38s} -> {model_line}")

        if "normscales" not in pname and n_layers == 0:
            zero_layer_live_count += 1

    # Scrittura di data/qkvo_preset_layer_counts.csv
    out_csv = DATA_DIR / "qkvo_preset_layer_counts.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["preset", "layer_count", "info_line"])
        writer.writeheader()
        writer.writerows(layer_count_records)
    print(f"\nWrote {out_csv} ({len(layer_count_records)} rows)")

    # Valutazione della condizione d'arresto §7.4
    if zero_layer_live_count >= 9:
        sys.exit(f"ABORT (§7.4): {zero_layer_live_count}/16 live presets report 0 layers. "
                 "Component naming mismatch.")
    else:
        print(f"Safety Gate §7.4 PASS: {zero_layer_live_count}/16 live presets with 0 layers (< 9 threshold).")


if __name__ == "__main__":
    main()
