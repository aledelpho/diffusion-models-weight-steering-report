#!/usr/bin/env python3
"""
compute_rotation_displacement.py
================================
Lavoro B del BRIEF per la ri-analisi delle rotazioni dei benchmark pilota.

Calcola offline, in modo deterministico e senza generare immagini:
- D_blocco = ||ΔW_blocco||_F / ||W_blocco||_F
- D_modello = ||ΔW_blocco||_F / ||W_modello||_F
- Numero di tensori toccati per ciascun blocco e condizione

Salva il risultato in data/pilot_rotation_displacement.csv.
"""

import os
import sys
import json
import struct
import math
import csv
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
from arthemy_geometry_engine import fast_dual_orthogonal_rotation

DTYPE_MAP = {
    "BF16": torch.bfloat16,
    "F16": torch.float16,
    "F32": torch.float32,
    "I32": torch.int32,
    "I64": torch.int64,
    "U8": torch.uint8,
}

class StreamingSafetensors:
    """Lettore binario in streaming per safetensors: zero mmap, zero commit limit error su Windows."""
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
        t = torch.frombuffer(bytearray(data), dtype=dtype).reshape(shape)
        return t

    def get_shape(self, name):
        return self.header[name]["shape"]

    def keys(self):
        return [k for k in self.header.keys() if k != "__metadata__"]

    def close(self):
        self.f.close()

def main():
    print("=== LAVORO B: CALCOLO DEI DISPLACEMENT DI FROBENIUS DELLE ROTAZIONI ===")
    assert os.path.exists(MODEL_PATH), f"Checkpoint non trovato: {MODEL_PATH}"
    os.makedirs(DATA_DIR, exist_ok=True)

    reader = StreamingSafetensors(MODEL_PATH)
    keys = reader.keys()
    print(f"Modello caricato via StreamingSafetensors. Totale chiavi: {len(keys)}")

    target_map = ArthemyKrea2ModelBlockSurgeonTuner.MODEL_TARGET_MAP
    block_indices = {
        "Block_1": target_map["Block_1 (All 0-4)"],
        "Block_2": target_map["Block_2 (All 5-9)"],
        "Block_3": target_map["Block_3 (All 10-14)"],
        "Block_4": target_map["Block_4 (All 15-19)"],
        "Block_5": target_map["Block_5 (All 20-23)"],
        "Block_6": target_map["Block_6 (All 24-27)"],
    }

    # Raggruppa i tensori per macro-blocco
    block_keys = {b: [] for b in block_indices}
    block_2d_keys = {b: [] for b in block_indices}
    non_block_keys = []

    for k in keys:
        clean_k = Krea2TensorParser.clean_key(k)
        idx, _ = Krea2TensorParser.extract_model_block_idx(clean_k)
        assigned = False
        if idx is not None:
            for b_name, b_idx_set in block_indices.items():
                if idx in b_idx_set:
                    block_keys[b_name].append(k)
                    shape = reader.get_shape(k)
                    if len(shape) >= 2:
                        block_2d_keys[b_name].append(k)
                    assigned = True
                    break
        if not assigned:
            non_block_keys.append(k)

    print("\nInventario tensori per blocco:")
    for b in sorted(block_indices.keys()):
        print(f"  {b}: {len(block_keys[b])} tensori totali ({len(block_2d_keys[b])} matrici 2D rotatibili)")
    print(f"  Tensori non-blocco (adapters/emb/norm): {len(non_block_keys)}")

    # Calcolo norme di Frobenius di base
    print("\nCalcolo delle norme di base ||W||_F...")
    tensor_base_sq = {}
    block_base_sq = {b: 0.0 for b in block_indices}
    total_model_sq = 0.0

    for i, k in enumerate(keys):
        w = reader.get_tensor(k)
        norm_sq = float(torch.sum(w.float() ** 2).item())
        tensor_base_sq[k] = norm_sq
        total_model_sq += norm_sq
        for b_name in block_indices:
            if k in block_keys[b_name]:
                block_base_sq[b_name] += norm_sq
                break

    total_model_norm = math.sqrt(total_model_sq)
    block_base_norm = {b: math.sqrt(block_base_sq[b]) for b in block_indices}
    print(f"Norma totale di base Model DiT ||W_modello||: {total_model_norm:.4f}")
    for b in sorted(block_indices.keys()):
        pct = (block_base_sq[b] / total_model_sq) * 100.0
        print(f"  ||W_{b}||: {block_base_norm[b]:.4f} ({pct:.2f}% della varianza del modello)")

    # Definizione delle condizioni di rotazione testate
    conditions = []
    # 1. rotX per tutti i 6 blocchi
    for b_name in sorted(block_indices.keys()):
        for ang in [-30.0, -15.0, 15.0, 30.0]:
            conditions.append((b_name, "rotX", ang, {"structural_x": ang}))

    # 2. Block_3 altre rotazioni
    for rot_k, kw in [
        ("structural_rot_y", lambda a: {"structural_y": a}),
        ("tensor_rot_x", lambda a: {"tensor_x": a}),
        ("tensor_rot_y", lambda a: {"tensor_y": a}),
    ]:
        for ang in [-20.0, 20.0]:
            conditions.append(("Block_3", rot_k, ang, kw(ang)))

    print(f"\nCalcolo rotazioni per {len(conditions)} condizioni...")
    cond_delta_sq = {c[:3]: 0.0 for c in conditions}
    tensors_touched_count = {c[:3]: 0 for c in conditions}

    blocks_to_process = sorted(list(set(c[0] for c in conditions)))

    for b_name in blocks_to_process:
        b_conds = [c for c in conditions if c[0] == b_name]
        t2d_list = block_2d_keys[b_name]
        print(f"  Calcolo {b_name} ({len(t2d_list)} matrici 2D, {len(b_conds)} condizioni)...")

        for k in t2d_list:
            w = reader.get_tensor(k)
            for c in b_conds:
                cond_key = c[:3]
                rot_kw = c[3]
                res = fast_dual_orthogonal_rotation(w, depth_rank=16, layer_name=k, **rot_kw)
                if res is not None:
                    AtA = res.A.float().t() @ res.A.float()
                    BBt = res.B.float() @ res.B.float().t()
                    d_sq = float(torch.clamp((AtA * BBt).sum(), min=0.0).item())
                    cond_delta_sq[cond_key] += d_sq
                    tensors_touched_count[cond_key] += 1

    reader.close()

    # Formattazione e scrittura risultati
    rows = []
    fieldnames = [
        "block",
        "rot_kind",
        "angle_deg",
        "tensors_touched",
        "delta_norm",
        "base_block_norm",
        "d_block",
        "base_model_norm",
        "d_model",
    ]

    print("\n=== TABELLA DISPLACEMENT FINALE ===")
    print(f"{'Block':8s} | {'rot_kind':16s} | {'Angle':6s} | {'Touched':7s} | {'‖ΔW_blocco‖':12s} | {'D_blocco':10s} | {'D_modello':10s}")
    print("-" * 85)

    for c in conditions:
        cond_key = c[:3]
        b_name, rot_k, ang = cond_key
        delta_norm = math.sqrt(cond_delta_sq[cond_key])
        d_block = delta_norm / block_base_norm[b_name]
        d_model = delta_norm / total_model_norm
        n_touched = tensors_touched_count[cond_key]

        print(f"{b_name:8s} | {rot_k:16s} | {ang:6.1f} | {n_touched:7d} | {delta_norm:12.4f} | {d_block:10.6f} | {d_model:10.6f}")

        rows.append({
            "block": b_name,
            "rot_kind": rot_k,
            "angle_deg": ang,
            "tensors_touched": n_touched,
            "delta_norm": f"{delta_norm:.8f}",
            "base_block_norm": f"{block_base_norm[b_name]:.8f}",
            "d_block": f"{d_block:.8f}",
            "base_model_norm": f"{total_model_norm:.8f}",
            "d_model": f"{d_model:.8f}",
        })

    out_csv = os.path.join(DATA_DIR, "pilot_rotation_displacement.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[OK] Tabella displacements salvata con successo in: {out_csv}")

if __name__ == "__main__":
    main()
