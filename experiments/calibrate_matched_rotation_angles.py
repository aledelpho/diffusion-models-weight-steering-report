#!/usr/bin/env python3
"""
calibrate_matched_rotation_angles.py
====================================
Fase 1 della pre-registrazione:
1. Calcola numericamente su krea2_turbo_bf16.safetensors il displacement D_modello
   per Block_1 (23.69°) e Block_6 (32.21°).
2. Verifica che lo scarto sia < 0.0002 o raffina l'angolo con bisezione al centesimo di grado.
3. Costruisce e calibra due controlli a segni scambiati indipendenti (scramble_A e scramble_B)
   allo stesso D_target esatto.
4. Salva data/matched_rotation_calibration.json con tutti i parametri congelati.
"""

import os
import sys
import json
import struct
import math
import torch

sys.stdout.reconfigure(encoding='utf-8')

COMFY_ROOT = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
SUITE_DIR = os.path.join(COMFY_ROOT, "custom_nodes", "Arthemy_Krea2_Tuner")
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
DATA_DIR = os.path.join(REPORT_ROOT, "data")
MODEL_PATH = r"C:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\krea2_turbo_bf16.safetensors"

sys.path.insert(0, COMFY_ROOT)
sys.path.append(SUITE_DIR)

from Arthemy_Krea2_Tuner import Krea2TensorParser, ArthemyKrea2ModelBlockSurgeonTuner
from arthemy_geometry_engine import (
    fast_dual_orthogonal_rotation,
    fast_chaos_orthogonal_rotation,
    _resolve_rank,
    _truncated_svd,
    _skew_from_planes,
    _finalize,
    normalize_signed_angle,
    _MIN_ROTATABLE_DIM,
    _EPS
)

DTYPE_MAP = {
    "BF16": torch.bfloat16,
    "F16": torch.float16,
    "F32": torch.float32,
    "I32": torch.int32,
    "I64": torch.int64,
    "U8": torch.uint8,
}

class StreamingSafetensors:
    def __init__(self, filepath):
        self.filepath = filepath
        self.f = open(filepath, "rb")
        header_len = struct.unpack("<Q", self.f.read(8))[0]
        header_bytes = self.f.read(header_len)
        self.header = json.loads(header_bytes.decode("utf-8"))
        self.data_start = 8 + header_len

    def get_tensor(self, name):
        meta = self.header[name]
        dtype = DTYPE_MAP[meta["dtype"]]
        shape = meta["shape"]
        start_off, end_off = meta["data_offsets"]
        length = end_off - start_off
        self.f.seek(self.data_start + start_off)
        data = self.f.read(length)
        return torch.frombuffer(bytearray(data), dtype=dtype).reshape(shape)

    def get_shape(self, name):
        return self.header[name]["shape"]

    def keys(self):
        return [k for k in self.header.keys() if k != "__metadata__"]

    def close(self):
        self.f.close()

def compute_block_delta_norm(reader, block_2d_keys, angle_deg, scramble_signs=None):
    """Calcola ||ΔW_blocco||_F per un dato angolo su rotX, opzionalmente con segni scambiati per tensore/piano."""
    tot_delta_sq = 0.0
    for i, k in enumerate(block_2d_keys):
        w = reader.get_tensor(k)
        sign = scramble_signs[i] if scramble_signs is not None else 1.0
        eff_angle = angle_deg * sign
        res = fast_dual_orthogonal_rotation(w, structural_x=eff_angle, depth_rank=16, layer_name=k)
        if res is not None:
            AtA = res.A.float().t() @ res.A.float()
            BBt = res.B.float() @ res.B.float().t()
            d_sq = float(torch.clamp((AtA * BBt).sum(), min=0.0).item())
            tot_delta_sq += d_sq
    return math.sqrt(tot_delta_sq)

def main():
    print("=== FASE 1: CALIBRAZIONE NON-LINEARE D APPAIATO PER COSTRUZIONE ===")
    assert os.path.exists(MODEL_PATH), f"Modello mancante: {MODEL_PATH}"
    os.makedirs(DATA_DIR, exist_ok=True)

    reader = StreamingSafetensors(MODEL_PATH)
    keys = reader.keys()
    total_model_norm = 5009.4475  # Misurato e congelato in Lavoro B

    target_map = ArthemyKrea2ModelBlockSurgeonTuner.MODEL_TARGET_MAP
    b1_indices = target_map["Block_1 (All 0-4)"]
    b6_indices = target_map["Block_6 (All 24-27)"]

    b1_2d_keys = []
    b6_2d_keys = []

    for k in keys:
        clean_k = Krea2TensorParser.clean_key(k)
        idx, _ = Krea2TensorParser.extract_model_block_idx(clean_k)
        if idx is not None:
            if idx in b1_indices and len(reader.get_shape(k)) >= 2:
                b1_2d_keys.append(k)
            elif idx in b6_indices and len(reader.get_shape(k)) >= 2:
                b6_2d_keys.append(k)

    print(f"Tensori 2D Block_1: {len(b1_2d_keys)} | Block_6: {len(b6_2d_keys)}")
    assert len(b1_2d_keys) == 40, f"Attesi 40 tensori per Block_1, trovati {len(b1_2d_keys)}"
    assert len(b6_2d_keys) == 32, f"Attesi 32 tensori per Block_6, trovati {len(b6_2d_keys)}"

    # 1. Verifica numerica per Block_1 a 23.69°
    target_D = 0.04500
    print(f"\nTarget D_modello prefissato: {target_D:.5f}")

    print("Misura Block_1 a 23.69°...")
    delta_b1 = compute_block_delta_norm(reader, b1_2d_keys, 23.69)
    d_model_b1 = delta_b1 / total_model_norm
    print(f"  Block_1 (23.69°): ||ΔW|| = {delta_b1:.4f}, D_modello = {d_model_b1:.6f}")

    print("Misura Block_6 a 32.21°...")
    delta_b6 = compute_block_delta_norm(reader, b6_2d_keys, 32.21)
    d_model_b6 = delta_b6 / total_model_norm
    print(f"  Block_6 (32.21°): ||ΔW|| = {delta_b6:.4f}, D_modello = {d_model_b6:.6f}")

    diff_D = abs(d_model_b1 - d_model_b6)
    print(f"\nDifferenza |D_1 - D_6| = {diff_D:.7f}")

    theta_1 = 23.69
    theta_6 = 32.21

    if diff_D > 0.0002:
        print("Scarto > 0.0002! Esecuzione raffinamento per bisezione su theta_6...")
        # Bisezione fine
        low, high = 31.5, 33.0
        for _ in range(10):
            mid = (low + high) / 2.0
            cur_delta = compute_block_delta_norm(reader, b6_2d_keys, mid)
            cur_D = cur_delta / total_model_norm
            if cur_D < d_model_b1:
                low = mid
            else:
                high = mid
        theta_6 = round((low + high) / 2.0, 2)
        delta_b6 = compute_block_delta_norm(reader, b6_2d_keys, theta_6)
        d_model_b6 = delta_b6 / total_model_norm
        diff_D = abs(d_model_b1 - d_model_b6)
        print(f"Raffinato: theta_6 = {theta_6:.2f}° -> D_modello = {d_model_b6:.6f}, diff = {diff_D:.7f}")

    assert diff_D <= 0.0002, f"CANCELLO FALLITO: diff_D = {diff_D} > 0.0002!"
    print(f"\n[OK] CANCELLO TOLLERANZA SUPERATO: diff_D = {diff_D:.6f} <= 0.0002")

    # 2. Generazione controlli a segni scambiati indipendenti: scramble_A e scramble_B
    # Scramble su Block_1: applica a ciascuno dei 40 tensori un segno Rademacher (+1 o -1)
    # Poiché ||(R - I) S||_F = 2 sin(|theta|/2) ||S||_F indipendentemente dal segno (+theta o -theta),
    # il displacement D è MATEMATICAMENTE INVARIANTE rispetto a qualsiasi combinazione di segni!
    # Verifichiamo empiricamente.
    rng_a = torch.Generator().manual_seed(20260918 + 1)
    signs_a = (torch.randint(0, 2, (40,), generator=rng_a) * 2 - 1).tolist()

    rng_b = torch.Generator().manual_seed(20260918 + 2)
    signs_b = (torch.randint(0, 2, (40,), generator=rng_b) * 2 - 1).tolist()

    print(f"\nVerifica scramble_A su Block_1 (semi-segni casuali, seed 20260919):")
    delta_scr_a = compute_block_delta_norm(reader, b1_2d_keys, theta_1, scramble_signs=signs_a)
    d_scr_a = delta_scr_a / total_model_norm
    print(f"  scramble_A: ||ΔW|| = {delta_scr_a:.4f}, D_modello = {d_scr_a:.6f} (scarto vs Block_1: {abs(d_scr_a - d_model_b1):.8f})")

    print(f"Verifica scramble_B su Block_1 (semi-segni casuali indipendenti, seed 20260920):")
    delta_scr_b = compute_block_delta_norm(reader, b1_2d_keys, theta_1, scramble_signs=signs_b)
    d_scr_b = delta_scr_b / total_model_norm
    print(f"  scramble_B: ||ΔW|| = {delta_scr_b:.4f}, D_modello = {d_scr_b:.6f} (scarto vs Block_1: {abs(d_scr_b - d_model_b1):.8f})")

    assert abs(d_scr_a - d_model_b1) < 1e-6, "Invarianza di norma di scramble_A violata!"
    assert abs(d_scr_b - d_model_b1) < 1e-6, "Invarianza di norma di scramble_B violata!"
    assert signs_a != signs_b, "scramble_A e scramble_B non sono indipendenti!"
    print("[OK] Controlli scramble_A e scramble_B verificati: identico D per costruzione a precisione macchina.")

    reader.close()

    # Salva parametri congelati
    calib_meta = {
        "model_file": "krea2_turbo_bf16.safetensors",
        "total_model_norm": total_model_norm,
        "target_D_model": round((d_model_b1 + d_model_b6) / 2.0, 6),
        "Block_1": {
            "target_block": "Block_1 (All 0-4)",
            "angle_deg": theta_1,
            "d_model": round(d_model_b1, 6),
            "delta_norm": round(delta_b1, 4),
            "tensors_2d_count": len(b1_2d_keys),
        },
        "Block_6": {
            "target_block": "Block_6 (All 24-27)",
            "angle_deg": theta_6,
            "d_model": round(d_model_b6, 6),
            "delta_norm": round(delta_b6, 4),
            "tensors_2d_count": len(b6_2d_keys),
        },
        "tolerance_achieved": round(diff_D, 7),
        "scramble_A": {
            "base_block": "Block_1 (All 0-4)",
            "angle_deg": theta_1,
            "seed": 20260918 + 1,
            "d_model": round(d_scr_a, 6),
            "signs": signs_a,
        },
        "scramble_B": {
            "base_block": "Block_1 (All 0-4)",
            "angle_deg": theta_1,
            "seed": 20260918 + 2,
            "d_model": round(d_scr_b, 6),
            "signs": signs_b,
        }
    }

    out_file = os.path.join(DATA_DIR, "matched_rotation_calibration.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(calib_meta, f, indent=2)
    print(f"\n[OK] Parametri di calibrazione congelati salvati in: {out_file}")

if __name__ == "__main__":
    main()
