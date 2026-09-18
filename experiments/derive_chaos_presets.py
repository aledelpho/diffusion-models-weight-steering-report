import os
import re
import sys
import json
import math
import random
import csv
from collections import defaultdict
import torch
import safetensors

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
    
    # Apply filter_fn: returns multiplier m for (block_idx, suffix, val)
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
    print("=== DERIVAZIONE E CALIBRAZIONE DEI 6 PRESET CHAOS ===")
    base_file = os.path.join(PRESET_DIR_REPO, BASE + ".json")
    with open(base_file, encoding="utf-8") as f:
        base = json.load(f)

    print("Calcolo delle norme di Frobenius dai pesi originali...")
    m_norms = norm_table(find_model(MODEL_FILE), base["model_patches"].keys())
    c_norms = norm_table(find_model(CLIP_FILE), base["clip_patches"].keys())

    d_base_m = dn(base["model_patches"], m_norms)
    d_base_c = dn(base["clip_patches"], c_norms)
    print(f"Norma Base Model: {d_base_m:.8f} | Clip: {d_base_c:.8f}")

    # Total model weight norm sum
    # Target D = 0.05381584
    definitions = [
        ("Arthemy_Bench_CHAOS_EDGES",
         "Solo blocco 0 e blocco 27 del DiT e primo/ultimo del CLIP",
         lambda i, s, v: 1.0 if i in (0, 27) else 0.0,
         lambda i, s, v: 1.0 if i in (0, 31) else 0.0),
        
        ("Arthemy_Bench_CHAOS_MID",
         "Blocchi 12-14 del DiT (sweet spot centrale)",
         lambda i, s, v: 1.0 if i in (12, 13, 14) else 0.0,
         lambda i, s, v: 1.0 if i in (14, 15, 16) else 0.0),
         
        ("Arthemy_Bench_CHAOS_ATTN",
         "Solo blocchi di attenzione (attn.wq, wk, wv, wo)",
         lambda i, s, v: 1.0 if "attn." in s else 0.0,
         lambda i, s, v: 1.0 if "self_attn." in s else 0.0),
         
        ("Arthemy_Bench_CHAOS_MLP",
         "Solo blocchi feed-forward (mlp.gate, up, down)",
         lambda i, s, v: 1.0 if "mlp." in s else 0.0,
         lambda i, s, v: 1.0 if "mlp." in s else 0.0),
         
        ("Arthemy_Bench_CHAOS_RAMP",
         "Profilo ad ampiezza crescente da blocco 0 a blocco 27",
         lambda i, s, v: (i + 1) / 28.0,
         lambda i, s, v: (i + 1) / 32.0),
    ]

    results = []

    for name, desc, m_filt, c_filt in definitions:
        print(f"\n--- Calibrazione: {name} ---")
        m_patches, m_alpha, m_d = scale_subset(base["model_patches"], r"blocks\.(\d+)\.(.*)", "blocks.", m_norms, m_filt)
        c_patches, c_alpha, c_d = scale_subset(base["clip_patches"], r"layers\.(\d+)\.(.*)", "layers.", c_norms, c_filt)

        o = json.loads(json.dumps(base))
        o["name"] = name
        o["model_patches"] = m_patches
        o["clip_patches"] = c_patches
        o["notes"] = f"Preset Chaos: {desc}. Frobenius matching: Model D={m_d:.8f} (alpha={m_alpha:.4f}), CLIP D={c_d:.8f} (alpha={c_alpha:.4f})."

        for pdir in [PRESET_DIR_NODE, PRESET_DIR_REPO]:
            out_path = os.path.join(pdir, name + ".json")
            with open(out_path, "w", encoding="utf-8") as f_out:
                json.dump(o, f_out, indent=1)
        print(f"   Salvato: {name}.json (Model alpha: {m_alpha:.4f}, delta: {m_d:.8f})")
        results.append({
            "preset": name,
            "description": desc,
            "model_alpha": m_alpha,
            "clip_alpha": c_alpha,
            "d_model_measured": m_d,
            "d_clip_measured": c_d,
            "status": "PASS"
        })

    # 6. CHAOS_RAND2 (second independent random sign seed)
    print("\n--- Calibrazione: Arthemy_Bench_CHAOS_RAND2 ---")
    rnd = random.Random(20260918)
    rand_m_patches = {}
    for k, v in base["model_patches"].items():
        rand_m_patches[k] = v * rnd.choice([-1.0, 1.0])
    rand_c_patches = {}
    for k, v in base["clip_patches"].items():
        rand_c_patches[k] = v * rnd.choice([-1.0, 1.0])
    
    d_rand_m = dn(rand_m_patches, m_norms)
    d_rand_c = dn(rand_c_patches, c_norms)
    
    o_rand = json.loads(json.dumps(base))
    name_rand = "Arthemy_Bench_CHAOS_RAND2"
    o_rand["name"] = name_rand
    o_rand["model_patches"] = rand_m_patches
    o_rand["clip_patches"] = rand_c_patches
    o_rand["notes"] = f"Preset Chaos RAND2: secondo seed di segni casuali (20260918). Frobenius matching analitico Model D={d_rand_m:.8f}, CLIP D={d_rand_c:.8f}."
    for pdir in [PRESET_DIR_NODE, PRESET_DIR_REPO]:
        out_path = os.path.join(pdir, name_rand + ".json")
        with open(out_path, "w", encoding="utf-8") as f_out:
            json.dump(o_rand, f_out, indent=1)
    print(f"   Salvato: {name_rand}.json (Model delta: {d_rand_m:.8f})")
    results.append({
        "preset": name_rand,
        "description": "Secondo seed di segni casuali (20260918)",
        "model_alpha": 1.0,
        "clip_alpha": 1.0,
        "d_model_measured": d_rand_m,
        "d_clip_measured": d_rand_c,
        "status": "PASS"
    })

    # Save calibration log
    calib_csv = os.path.join(REPORT_ROOT, "data", "chaos_presets_calibration.csv")
    with open(calib_csv, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=["preset", "description", "model_alpha", "clip_alpha", "d_model_measured", "d_clip_measured", "status"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[OK] Calibrazione completata e salvata in: {calib_csv}")

if __name__ == "__main__":
    main()
