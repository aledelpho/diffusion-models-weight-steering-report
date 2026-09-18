import os
import re
import sys
import json
import math
import torch
import safetensors
from collections import defaultdict

COMFY_ROOT = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
SUITE_DIR = os.path.join(COMFY_ROOT, "custom_nodes", "Arthemy_Krea2_Tuner")
PRESET_DIR_NODE = os.path.join(SUITE_DIR, "presets")
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
PRESET_DIR_REPO = os.path.join(REPORT_ROOT, "presets")
MODELS_ROOT = r"C:\StabilityMatrix-win-x64\Data\Models"

sys.path.insert(0, COMFY_ROOT)
sys.path.append(SUITE_DIR)
from Arthemy_Krea2_Tuner import Krea2TensorParser

BASE = "Arthemy_Bench_Base"
MODEL_FILE = "krea2_turbo_bf16.safetensors"
CLIP_FILE = "qwen3vl_4b_bf16.safetensors"

def find_model(fn):
    for root, _d, files in os.walk(MODELS_ROOT):
        if fn in files:
            return os.path.join(root, fn)
    raise FileNotFoundError(fn)

def norm_table(path, keys):
    want, norms = set(keys), {}
    with safetensors.safe_open(path, framework="pt", device="cpu") as f:
        for raw in f.keys():
            ck = Krea2TensorParser.clean_key(raw)
            if ck in want and ck not in norms:
                norms[ck] = float(torch.linalg.vector_norm(
                    f.get_tensor(raw).to(torch.float32)).item())
    missing = want - set(norms)
    if missing:
        raise KeyError(f"{len(missing)} chiavi senza tensore nel modello: {list(missing)[:5]}")
    return norms

def dn(patches, norms):
    return math.sqrt(sum((v * norms[k]) ** 2 for k, v in patches.items() if k in norms))

def split_indexed(patches, pattern):
    rx = re.compile(pattern)
    grouped, rest = defaultdict(dict), {}
    for k, v in patches.items():
        m = rx.match(k)
        if m:
            grouped[int(m.group(1))][m.group(2)] = v
        else:
            rest[k] = v
    return dict(grouped), rest

def scale_subset(base_patches, pattern, pref, norms, filter_fn):
    grouped, rest = split_indexed(base_patches, pattern)
    idx = sorted(grouped)
    sub_full = {f"{pref}{i}.{s}": v for i in idx for s, v in grouped[i].items()}
    d_rest = dn(rest, norms)
    d_tot = math.hypot(dn(sub_full, norms), d_rest)
    
    sub_filtered = {}
    for i in idx:
        for s, v in grouped[i].items():
            k = f"{pref}{i}.{s}"
            m = filter_fn(i, s, v)
            if m != 0.0:
                sub_filtered[k] = v * m

    d_filtered = dn(sub_filtered, norms)
    target = d_tot ** 2 - d_rest ** 2
    if target <= 0:
        raise RuntimeError("Il resto supera il totale")
    if d_filtered <= 0:
        raise RuntimeError("Il sottoinsieme filtrato ha norma zero")
        
    alpha = math.sqrt(target) / d_filtered
    new_patches = dict(rest)
    for i in idx:
        for s, v in grouped[i].items():
            k = f"{pref}{i}.{s}"
            new_patches[k] = sub_filtered.get(k, 0.0) * alpha

    d_final = dn(new_patches, norms)
    res = abs(d_final - d_tot) / d_tot
    if res > 1e-6:
        raise RuntimeError(f"Riscalatura non convergente: target {d_tot:.8f}, ottenuto {d_final:.8f}, res {res:.2e}")
        
    return new_patches, alpha, d_final

def main():
    print("=== DERIVAZIONE E CALIBRAZIONE DI Arthemy_Bench_CHAOS_EDGES_V2 ===")
    base_file = os.path.join(PRESET_DIR_REPO, BASE + ".json")
    with open(base_file, encoding="utf-8") as f:
        base = json.load(f)

    print("Caricamento norme di Frobenius dai pesi fisici...")
    m_norms = norm_table(find_model(MODEL_FILE), base["model_patches"].keys())
    c_norms = norm_table(find_model(CLIP_FILE), base["clip_patches"].keys())

    d_base_m = dn(base["model_patches"], m_norms)
    d_base_c = dn(base["clip_patches"], c_norms)
    print(f"Target Frobenius Model D: {d_base_m:.8f} | Clip D: {d_base_c:.8f}")

    name = "Arthemy_Bench_CHAOS_EDGES_V2"
    desc = "Primo e ultimo ottavo del DiT (blocchi 0-3 e 24-27) e del CLIP (layer 0-3 e 28-31)"
    
    # Blocchi 0-3 e 24-27 per DiT (8 blocchi)
    m_filt = lambda i, s, v: 1.0 if i in (0, 1, 2, 3, 24, 25, 26, 27) else 0.0
    # Layer 0-3 e 28-31 per CLIP (8 layer)
    c_filt = lambda i, s, v: 1.0 if i in (0, 1, 2, 3, 28, 29, 30, 31) else 0.0

    print(f"\n--- Calibrazione: {name} ---")
    m_patches, m_alpha, m_d = scale_subset(base["model_patches"], r"blocks\.(\d+)\.(.*)", "blocks.", m_norms, m_filt)
    c_patches, c_alpha, c_d = scale_subset(base["clip_patches"], r"layers\.(\d+)\.(.*)", "layers.", c_norms, c_filt)

    o = json.loads(json.dumps(base))
    o["name"] = name
    o["model_patches"] = m_patches
    o["clip_patches"] = c_patches
    o["notes"] = (f"Preset Chaos Edges V2: {desc}. Frobenius matching: "
                  f"Model D={m_d:.8f} (alpha={m_alpha:.4f}), CLIP D={c_d:.8f} (alpha={c_alpha:.4f}).")

    for pdir in [PRESET_DIR_NODE, PRESET_DIR_REPO]:
        os.makedirs(pdir, exist_ok=True)
        out_path = os.path.join(pdir, name + ".json")
        with open(out_path, "w", encoding="utf-8") as f_out:
            json.dump(o, f_out, indent=1)
        print(f"   Salvato con successo in: {out_path}")

    print(f"\n[RISULTATO]")
    print(f"   Model Alpha:      {m_alpha:.6f}")
    print(f"   CLIP Alpha:       {c_alpha:.6f}")
    print(f"   Model D misurato: {m_d:.8f} (target: {d_base_m:.8f}, residuo: {abs(m_d - d_base_m):.2e})")
    print(f"   CLIP D misurato:  {c_d:.8f} (target: {d_base_c:.8f}, residuo: {abs(c_d - d_base_c):.2e})")
    print(f"   Stato: PASS")

if __name__ == "__main__":
    main()
