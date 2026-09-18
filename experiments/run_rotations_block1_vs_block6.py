#!/usr/bin/env python3
"""
experiments/run_rotations_block1_vs_block6.py
=============================================
Lancia il batch di 210 generazioni per l'esperimento:
Block_1 vs Block_6 con Frobenius Displacement appaiato (D = 0.04500)
e controlli a segni scramblati (scramble_A vs scramble_B).

Parametri pre-registrati:
- 10 stili di rendering (S01..S10 da stage12_prompts.json)
- 3 seed controllati: 42, 1337, 4242145
- 7 condizioni:
    1. baseline (0.0)
    2. Block_1_pos (+23.69°)
    3. Block_1_neg (-23.69°)
    4. Block_6_pos (+32.21°)
    5. Block_6_neg (-32.21°)
    6. scramble_A (Rademacher seed 20260919, D = 0.04500)
    7. scramble_B (Rademacher seed 20260920, D = 0.04500)
- Campionatore: euler_ancestral, 9 passi, CFG 1.0, risoluzione 1024x1280 (1024x1760 con visualizer HUD)
"""

import os
import sys
import json
import time
import csv
import urllib.request
import urllib.parse

COMFY_URL = "http://127.0.0.1:8188"
SLUG = "rotations_block1_vs_block6"

REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
PILOT_ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
DATA_DIR = os.path.join(REPORT_ROOT, "data")

PROMPTS_FILE = os.path.join(DATA_DIR, "stage12_prompts.json")
if not os.path.exists(PROMPTS_FILE):
    PROMPTS_FILE = os.path.join(PILOT_ROOT, "stage12_prompts.json")

SEEDS = [42, 1337, 4242145]
STEPS = 9
CFG = 1.0
SAMPLER = "euler_ancestral"
SCHEDULER = "simple"
WIDTH, HEIGHT = 1024, 1280
VIS_HEIGHT = 480

CONDITIONS = [
    {
        "cond_id": "baseline",
        "node_type": "rotator",
        "target_block": "Block_1 (All 0-4)",
        "angle": 0.0,
        "d_target": 0.0,
    },
    {
        "cond_id": "Block_1_pos",
        "node_type": "rotator",
        "target_block": "Block_1 (All 0-4)",
        "angle": 23.69,
        "d_target": 0.04500,
    },
    {
        "cond_id": "Block_1_neg",
        "node_type": "rotator",
        "target_block": "Block_1 (All 0-4)",
        "angle": -23.69,
        "d_target": 0.04500,
    },
    {
        "cond_id": "Block_6_pos",
        "node_type": "rotator",
        "target_block": "Block_6 (All 24-27)",
        "angle": 32.21,
        "d_target": 0.04500,
    },
    {
        "cond_id": "Block_6_neg",
        "node_type": "rotator",
        "target_block": "Block_6 (All 24-27)",
        "angle": -32.21,
        "d_target": 0.04500,
    },
    {
        "cond_id": "scramble_A",
        "node_type": "scramble",
        "control": "scramble_A",
        "angle": 23.69,
        "d_target": 0.04500,
    },
    {
        "cond_id": "scramble_B",
        "node_type": "scramble",
        "control": "scramble_B",
        "angle": 23.69,
        "d_target": 0.04500,
    },
]

def build_graph(prompt_text: str, seed: int, condition: dict, prefix: str) -> dict:
    graph = {
        "36": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "krea2_turbo_bf16.safetensors",
                "weight_dtype": "default"
            }
        },
        "47": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen3vl_4b_bf16.safetensors",
                "type": "krea2",
                "device": "default"
            }
        },
        "48": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "qwen_image_vae.safetensors"
            }
        },
        "45": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": WIDTH,
                "height": HEIGHT,
                "batch_size": 1
            }
        },
        "37": {
            "class_type": "ArthemyKrea2ResetPatcher",
            "inputs": {
                "model": ["36", 0],
                "clip": ["47", 0],
                "reset_model": True,
                "reset_clip": True
            }
        },
        "40": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["37", 1],
                "text": prompt_text
            }
        },
        "43": {
            "class_type": "ConditioningZeroOut",
            "inputs": {
                "conditioning": ["40", 0]
            }
        }
    }

    if condition["node_type"] == "rotator":
        graph["50"] = {
            "class_type": "ArthemyKrea2ModelRotator",
            "inputs": {
                "model": ["37", 0],
                "target_block": condition["target_block"],
                "sub_components": "All Components",
                "depth_reach": "Default",
                "structural_rot_x": float(condition["angle"]),
                "structural_rot_y": 0.0,
                "tensor_rot_x": 0.0,
                "tensor_rot_y": 0.0
            }
        }
    elif condition["node_type"] == "scramble":
        graph["50"] = {
            "class_type": "ArthemyKrea2ModelScrambleRotator",
            "inputs": {
                "model": ["37", 0],
                "control": condition["control"],
                "depth_reach": "Default"
            }
        }

    graph["198"] = {
        "class_type": "ArthemyKrea2ModelVisualizer",
        "inputs": {
            "model": ["50", 0],
            "scale": 5.0,
            "image_width": WIDTH,
            "image_height": VIS_HEIGHT
        }
    }
    graph["42"] = {
        "class_type": "KSampler",
        "inputs": {
            "model": ["198", 0],
            "positive": ["40", 0],
            "negative": ["43", 0],
            "latent_image": ["45", 0],
            "seed": int(seed),
            "steps": STEPS,
            "cfg": CFG,
            "sampler_name": SAMPLER,
            "scheduler": SCHEDULER,
            "denoise": 1.0
        }
    }
    graph["46"] = {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["42", 0],
            "vae": ["48", 0]
        }
    }
    graph["307"] = {
        "class_type": "ArthemyImageStitcher",
        "inputs": {
            "image1": ["46", 0],
            "image2": ["198", 1],
            "direction": "Vertical (Top / Bottom)",
            "match_size": True
        }
    }
    graph["61"] = {
        "class_type": "SaveImage",
        "inputs": {
            "images": ["307", 0],
            "filename_prefix": prefix
        }
    }

    return graph

def queue_prompt(prompt_dict: dict) -> dict:
    payload = json.dumps({"prompt": prompt_dict}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def query_queue() -> dict:
    req = urllib.request.Request(f"{COMFY_URL}/queue")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    print("=== COMFYUI PILOT: LANCIO ESPERIMENTO BLOCK_1 VS BLOCK_6 ===")
    print(f"File prompt: {PROMPTS_FILE}")

    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    cond_names = [c["cond_id"] for c in CONDITIONS]
    print(f"Caricati {len(prompts)} prompt stilistici.")
    print(f"Seed per cella ({len(SEEDS)}): {SEEDS}")
    print(f"Condizioni per cella ({len(CONDITIONS)}): {cond_names}")
    total_runs = len(prompts) * len(SEEDS) * len(CONDITIONS)
    print(f"Totale esecuzioni da accodare: {total_runs}\n")

    manifest = []
    task_queue = []

    run_idx = 0
    for p in prompts:
        p_id = p["prompt_id"]
        p_text = p["text"]
        for s in SEEDS:
            for cond in CONDITIONS:
                c_id = cond["cond_id"]
                prefix = f"{SLUG}/{p_id}_s{s}_{c_id}"
                graph = build_graph(p_text, s, cond, prefix)
                
                manifest_row = {
                    "run_idx": run_idx,
                    "prompt_id": p_id,
                    "prompt_text": p_text,
                    "seed": s,
                    "condition": c_id,
                    "node_type": cond["node_type"],
                    "angle": cond["angle"],
                    "d_target": cond["d_target"],
                    "prefix": prefix,
                    "expected_file": f"{p_id}_s{s}_{c_id}_00001_.png"
                }
                manifest.append(manifest_row)
                task_queue.append((run_idx, prefix, graph))
                run_idx += 1

    os.makedirs(DATA_DIR, exist_ok=True)
    manifest_json_path = os.path.join(DATA_DIR, "rotations_block1_vs_block6_manifest.json")
    manifest_csv_path = os.path.join(DATA_DIR, "rotations_block1_vs_block6_manifest.csv")

    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Manifest JSON salvato: {manifest_json_path}")

    with open(manifest_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)
    print(f"[OK] Manifest CSV salvato: {manifest_csv_path}")

    # Anche nel pilot data dir per sicurezza
    pilot_data = os.path.join(PILOT_ROOT, "data")
    os.makedirs(pilot_data, exist_ok=True)
    with open(os.path.join(pilot_data, "rotations_block1_vs_block6_manifest.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)

    print(f"\nAvvio invio concorrente di {len(task_queue)} prompt a {COMFY_URL}/prompt...")
    queued_prompt_ids = []
    t0 = time.time()

    for idx, prefix, graph in task_queue:
        try:
            res = queue_prompt(graph)
            p_id = res.get("prompt_id")
            queued_prompt_ids.append(p_id)
            if (idx + 1) % 25 == 0 or idx == len(task_queue) - 1:
                print(f"  [Accodamento] {idx + 1}/{len(task_queue)} inviati con successo...")
        except Exception as e:
            print(f"  [ERRORE accodamento run {idx} ({prefix})]: {e}")

    dt = time.time() - t0
    print(f"\n[OK] Accodamento completato in {dt:.2f}s ({len(queued_prompt_ids)}/{len(task_queue)} prompt accettati).")

    print("\nVerifica immediata della coda ComfyUI (/queue)...")
    time.sleep(1.0)
    q = query_queue()
    running = len(q.get("queue_running", []))
    pending = len(q.get("queue_pending", []))
    total_active = running + pending

    print(f"Stato coda ComfyUI: running={running}, pending={pending}, totale attivo={total_active}")
    if total_active >= len(task_queue) - 2:
        print(f"[CANCELLO SUPERATO] Tutti i {total_runs} task sono registrati e attivi nella coda di ComfyUI!")
    else:
        print(f"[ATTENZIONE] Totale in coda ({total_active}) inferiore a {total_runs}!")

if __name__ == "__main__":
    main()
