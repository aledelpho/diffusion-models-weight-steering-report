# -*- coding: utf-8 -*-
"""
experiments/run_stage7a.py  --  Stage 7 (Tempo A: 24 candidati, solo baseline)

Genera i 120 render baseline (24 prompt x 5 seed):
- prompt: I01..I24 da newpromptlist.txt
- parametri: euler_ancestral, 9 steps, cfg 1.0, 1024x1280
- seed: 42, 777, 1337, 9999, 4242145
- naming: renders/I01_baseline_seed1337_00001_.png
- manifesto: stage7a_images.csv
"""

import os
import sys
import glob
import json
import hashlib
import urllib.request
import csv
import argparse
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stage7_prompts import STAGE7_CANDIDATES
from stage5_config import CORE_SEEDS, suite_fingerprint

COMFY_URL = "http://127.0.0.1:8188"
SLUG = "benchmark_stage7a"
ROOT_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output" + rf"\{SLUG}"
ROOT_IMG = os.path.join(ROOT_DIR, "renders")
CSV_PATH = r"c:\Users\aless\Desktop\comfyui-pilot\stage7a_images.csv"

STEPS, CFG, WIDTH, HEIGHT = 9, 1.0, 1024, 1280
SAMPLER, SCHEDULER = "euler_ancestral", "simple"

FIELDS = ["run_id", "stage", "condition_id", "cond_name", "renders_root",
          "image_path", "baseline_path", "prompt_id", "prompt_sha1", "prompt_tag",
          "prompt_text", "seed", "sampler", "steps", "cfg", "width", "height",
          "operation", "preset_file", "suite_git_sha", "timestamp"]

def build_workflow(text, seed, tag):
    return {
        "36": {"class_type": "UNETLoader",
               "inputs": {"unet_name": "krea2_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "47": {"class_type": "CLIPLoader",
               "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
        "48": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "45": {"class_type": "EmptyLatentImage", "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1}},
        "37": {"class_type": "ArthemyKrea2ResetPatcher",
               "inputs": {"model": ["36", 0], "clip": ["47", 0], "reset_model": True, "reset_clip": True}},
        "40": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["37", 1], "text": text}},
        "43": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["40", 0]}},
        "42": {"class_type": "KSampler",
               "inputs": {"model": ["37", 0], "positive": ["40", 0], "negative": ["43", 0],
                          "latent_image": ["45", 0], "seed": seed, "steps": STEPS, "cfg": CFG,
                          "sampler_name": SAMPLER, "scheduler": SCHEDULER, "denoise": 1.0}},
        "46": {"class_type": "VAEDecode", "inputs": {"samples": ["42", 0], "vae": ["48", 0]}},
        "61": {"class_type": "SaveImage",
               "inputs": {"images": ["46", 0], "filename_prefix": f"{SLUG}/renders/{tag}"}},
    }

def queue_prompt(wf):
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Crea solo il manifesto senza inviare richieste a ComfyUI")
    args = ap.parse_args()

    os.makedirs(ROOT_IMG, exist_ok=True)
    fp = suite_fingerprint()
    run_id = f"stage7a_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("==================================================================")
    print(f" STAGE 7 (Tempo A: 24 candidati x 5 seed = 120 render baseline)")
    print(f" Impronta suite: {fp}")
    print(f" Output folder:  {ROOT_IMG}")
    print(f" Manifesto:      {CSV_PATH}")
    print("==================================================================")

    tasks = []
    for p in STAGE7_CANDIDATES:
        pid, txt, tag = p["id"], p["text"], p["tag"]
        sha = hashlib.sha1(txt.encode("utf-8")).hexdigest()[:10]

        for s in CORE_SEEDS:
            img_tag = f"{pid}_baseline_seed{s}"
            img_rel = f"renders/{img_tag}_00001_.png"
            row = dict(
                run_id=run_id, stage="stage7a",
                condition_id=f"baseline_{s}",
                cond_name="baseline",
                renders_root=ROOT_IMG,
                image_path=img_rel,
                baseline_path=img_rel,
                prompt_id=pid,
                prompt_sha1=sha,
                prompt_tag=tag,
                prompt_text=txt,
                seed=str(s),
                sampler=SAMPLER, steps=STEPS, cfg=CFG,
                width=WIDTH, height=HEIGHT,
                operation="baseline",
                preset_file="",
                suite_git_sha=fp,
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            tasks.append((img_tag, txt, s, row))

    print(f"[Stage 7a] Pianificati {len(tasks)} render baseline.")

    # Scrivi il manifesto
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for _, _, _, r in tasks:
            w.writerow(r)
    print(f"[Stage 7a] Manifesto salvato: {CSV_PATH}")

    if args.dry_run:
        print("[Stage 7a] Dry-run completato.")
        return

    # Invia le generazioni a ComfyUI in batch veloce
    print("[Stage 7a] Invio richieste alla coda di ComfyUI...")
    queued_count = 0
    for idx, (img_tag, txt, s, _) in enumerate(tasks, 1):
        target_png = os.path.join(ROOT_DIR, f"renders/{img_tag}_00001_.png")
        if os.path.exists(target_png):
            print(f"  [{idx:03d}/{len(tasks):03d}] Gia' esistente: {img_tag}")
            continue
        wf = build_workflow(txt, s, img_tag)
        queue_prompt(wf)
        queued_count += 1
        if queued_count % 20 == 0 or queued_count == len(tasks):
            print(f"  [{idx:03d}/{len(tasks):03d}] Accodati {queued_count} task...")

    print(f"\n[Stage 7a] Accodamento completato: {queued_count} nuovi task registrati.")

    # Verifica immediata della coda
    try:
        req = urllib.request.urlopen(f"{COMFY_URL}/queue")
        qdata = json.loads(req.read().decode("utf-8"))
        r_len = len(qdata.get("queue_running", []))
        p_len = len(qdata.get("queue_pending", []))
        print(f"[Stage 7a] Stato ComfyUI Queue: {r_len} in esecuzione, {p_len} in attesa.")
    except Exception as e:
        print(f"[Stage 7a] Errore verifica queue: {e}")

if __name__ == "__main__":
    main()
