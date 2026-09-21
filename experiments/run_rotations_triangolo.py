#!/usr/bin/env python3
"""
experiments/run_rotations_triangolo.py
======================================
Lancia il batch di 120 nuove generazioni per l'esperimento:
Triangolo Block_1 vs Block_3 vs Block_6 (Opzione a)
con Frobenius Displacement appaiato (D = 0.04500) e controlli
scramble su Block_3 (scramble_C vs scramble_D).

Condizioni nuove (4 condizioni x 10 stili x 3 seed = 120 generazioni):
  1. Block_3_pos (+25.24°)
  2. Block_3_neg (-25.24°)
  3. scramble_C (Rademacher seed 20260922 su Block_3, D = 0.04500)
  4. scramble_D (Rademacher seed 20260923 su Block_3, D = 0.04500)

Riuso delle 210 immagini esistenti:
  - baseline (30 img)
  - Block_1_pos / Block_1_neg (60 img)
  - Block_6_pos / Block_6_neg (60 img)
  - scramble_A / scramble_B (60 img)
Totale dataset combinato: 330 generazioni.

Tutte le immagini vengono salvate in:
  rotations_block1_vs_block6/{prompt_id}_s{seed}_{cond}
per garantire co-locazione diretta e assenza di duplicazioni.
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

PROMPTS_FILE = os.path.join(PILOT_ROOT, "stage12_prompts.json")
if not os.path.exists(PROMPTS_FILE):
    PROMPTS_FILE = os.path.join(DATA_DIR, "stage12_prompts.json")

SEEDS = [42, 1337, 4242145]
STEPS = 9
CFG = 1.0
SAMPLER = "euler_ancestral"
SCHEDULER = "simple"
WIDTH, HEIGHT = 1024, 1280
VIS_HEIGHT = 480

CONDITIONS = [
    {
        "cond_id": "Block_3_pos",
        "node_type": "rotator",
        "target_block": "Block_3 (All 10-14)",
        "angle": 25.24,
        "d_target": 0.04500,
    },
    {
        "cond_id": "Block_3_neg",
        "node_type": "rotator",
        "target_block": "Block_3 (All 10-14)",
        "angle": -25.24,
        "d_target": 0.04500,
    },
    {
        "cond_id": "scramble_C",
        "node_type": "scramble",
        "control": "scramble_C",
        "angle": 25.24,
        "d_target": 0.04500,
    },
    {
        "cond_id": "scramble_D",
        "node_type": "scramble",
        "control": "scramble_D",
        "angle": 25.24,
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
    print("=== COMFYUI PILOT: LANCIO ESPERIMENTO TRIANGOLO (BLOCK_1 VS BLOCK_3 VS BLOCK_6) ===")
    print(f"File prompt: {PROMPTS_FILE}")

    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    cond_names = [c["cond_id"] for c in CONDITIONS]
    print(f"Caricati {len(prompts)} prompt stilistici.")
    print(f"Seed per cella ({len(SEEDS)}): {SEEDS}")
    print(f"Condizioni per cella ({len(CONDITIONS)}): {cond_names}")
    total_runs = len(prompts) * len(SEEDS) * len(CONDITIONS)
    print(f"Totale nuove esecuzioni da accodare: {total_runs}\n")

    manifest = []
    task_queue = []

    # Inizia da run_idx 210 per garantire sequenzialita con i primi 210 run
    run_idx = 210
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

    # Salvataggio manifest 120 run
    for out_dir in [DATA_DIR, os.path.join(PILOT_ROOT, "data")]:
        os.makedirs(out_dir, exist_ok=True)
        manifest_json_path = os.path.join(out_dir, "rotations_triangolo_manifest.json")
        manifest_csv_path = os.path.join(out_dir, "rotations_triangolo_manifest.csv")

        with open(manifest_json_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        with open(manifest_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
            writer.writeheader()
            writer.writerows(manifest)
        print(f"[OK] Manifest salvato in: {manifest_csv_path}")

    # Creazione manifest unificato 330 righe (210 esistenti + 120 nuove)
    b1_b6_manifest_path = os.path.join(DATA_DIR, "rotations_block1_vs_block6_manifest.csv")
    if not os.path.exists(b1_b6_manifest_path):
        b1_b6_manifest_path = os.path.join(PILOT_ROOT, "data", "rotations_block1_vs_block6_manifest.csv")

    if os.path.exists(b1_b6_manifest_path):
        with open(b1_b6_manifest_path, "r", encoding="utf-8") as f:
            existing_manifest = list(csv.DictReader(f))
        combined_manifest = existing_manifest + manifest
        for out_dir in [DATA_DIR, os.path.join(PILOT_ROOT, "data")]:
            all330_path = os.path.join(out_dir, "rotations_triangolo_all330_manifest.csv")
            with open(all330_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(combined_manifest[0].keys()))
                writer.writeheader()
                writer.writerows(combined_manifest)
            print(f"[OK] Manifest unificato 330 salvato in: {all330_path}")

    print(f"\nAvvio invio concorrente di {len(task_queue)} prompt a {COMFY_URL}/prompt...")
    queued_prompt_ids = []
    t0 = time.time()

    for idx_run, prefix, graph in task_queue:
        try:
            res = queue_prompt(graph)
            p_id = res.get("prompt_id")
            queued_prompt_ids.append(p_id)
            step_num = idx_run - 210 + 1
            if step_num % 20 == 0 or step_num == len(task_queue):
                print(f"  [Accodamento] {step_num}/{len(task_queue)} inviati con successo...")
        except Exception as e:
            print(f"  [ERRORE accodamento run {idx_run} ({prefix})]: {e}")

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
