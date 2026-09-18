import os
import sys
import json
import math
import csv
import torch
import safetensors

COMFY_ROOT = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
SUITE_DIR = os.path.join(COMFY_ROOT, "custom_nodes", "Arthemy_Krea2_Tuner")
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
PRESET_DIR = os.path.join(REPORT_ROOT, "presets")
MODELS_ROOT = r"C:\StabilityMatrix-win-x64\Data\Models"

sys.path.insert(0, COMFY_ROOT)
sys.path.append(SUITE_DIR)
from Arthemy_Krea2_Tuner import Krea2TensorParser

MODEL_FILE = "krea2_turbo_bf16.safetensors"
CLIP_FILE = "qwen3vl_4b_bf16.safetensors"

TARGET_PRESETS = [
    # 6 Preset originali / SA
    "Arthemy_Bench_Base",
    "Arthemy_Bench_NEG",
    "Arthemy_Bench_BLOCKSHUFFLE",
    "Arthemy_Bench_BLOCKSHUFFLE_NEG",
    "Arthemy_Bench_RANDSIGN",
    "Arthemy_Bench_RANDSIGN_NEG",
    # 6 Preset Chaos V1
    "Arthemy_Bench_CHAOS_EDGES",
    "Arthemy_Bench_CHAOS_MID",
    "Arthemy_Bench_CHAOS_ATTN",
    "Arthemy_Bench_CHAOS_MLP",
    "Arthemy_Bench_CHAOS_RAMP",
    "Arthemy_Bench_CHAOS_RAND2",
    # Preset Chaos V2
    "Arthemy_Bench_CHAOS_EDGES_V2",
    # Bonus dose-response
    "Arthemy_Bench_HALF",
]

def find_model(fn):
    for root, _d, files in os.walk(MODELS_ROOT):
        if fn in files:
            return os.path.join(root, fn)
    raise FileNotFoundError(fn)

def load_full_norms(path):
    norms = {}
    with safetensors.safe_open(path, framework="pt", device="cpu") as f:
        for raw in f.keys():
            ck = Krea2TensorParser.clean_key(raw)
            if ck not in norms:
                t = f.get_tensor(raw).to(torch.float32)
                norms[ck] = float(torch.linalg.vector_norm(t).item())
    return norms

def dn(patches, norms):
    tot_sq = 0.0
    for k, v in patches.items():
        if k in norms:
            tot_sq += (v * norms[k]) ** 2
    return math.sqrt(tot_sq)

def main():
    print("=== MISURA DEI DISPLACEMENT DI TUTTI I PRESET (Norme Frobenius) ===")
    m_path = find_model(MODEL_FILE)
    c_path = find_model(CLIP_FILE)

    print("Caricamento norme complete per il Model DiT...")
    m_norms = load_full_norms(m_path)
    total_m_norm = math.sqrt(sum(v ** 2 for v in m_norms.values()))
    print(f"Norma totale Model DiT: {total_m_norm:.6f}")

    print("Caricamento norme complete per il CLIP Text Encoder...")
    c_norms = load_full_norms(c_path)
    total_c_norm = math.sqrt(sum(v ** 2 for v in c_norms.values()))
    print(f"Norma totale CLIP: {total_c_norm:.6f}")

    rows = []
    print("\nMisura dei preset...")
    for p_name in TARGET_PRESETS:
        p_path = os.path.join(PRESET_DIR, p_name + ".json")
        if not os.path.exists(p_path):
            print(f"  [MISSING] {p_name}.json")
            continue

        with open(p_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        m_patches = data.get("model_patches", {})
        c_patches = data.get("clip_patches", {})

        d_m_abs = dn(m_patches, m_norms)
        d_c_abs = dn(c_patches, c_norms)

        d_m_rel = d_m_abs / total_m_norm
        d_c_rel = d_c_abs / total_c_norm

        print(f"  {p_name:30s} | Model ‖ΔW‖: {d_m_abs:10.4f} (D={d_m_rel:.8f}) | CLIP ‖ΔW‖: {d_c_abs:8.4f} (D={d_c_rel:.8f})")

        rows.append({
            "preset_name": p_name,
            "delta_w_model_abs": f"{d_m_abs:.8f}",
            "d_model_relative": f"{d_m_rel:.8f}",
            "model_base_total_norm": f"{total_m_norm:.8f}",
            "delta_w_clip_abs": f"{d_c_abs:.8f}",
            "d_clip_relative": f"{d_c_rel:.8f}",
            "clip_base_total_norm": f"{total_c_norm:.8f}",
            "status": "PASS"
        })

    out_csv = os.path.join(REPORT_ROOT, "data", "preset_displacements.csv")
    fieldnames = ["preset_name", "delta_w_model_abs", "d_model_relative", "model_base_total_norm",
                  "delta_w_clip_abs", "d_clip_relative", "clip_base_total_norm", "status"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\n[OK] Tabella displacements salvata con successo in: {out_csv}")

if __name__ == "__main__":
    main()
