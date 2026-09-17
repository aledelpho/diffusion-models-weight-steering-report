# -*- coding: utf-8 -*-
"""
experiments/run_stage7b.py  --  Stage 7 (Tempo B: le 6 condizioni sui 16 selezionati)

Genera i 480 render (16 prompt x 6 condizioni x 5 seed):
- prompt: 16 prompt selezionati deterministicamente da Tempo A (confirmation_prompts.csv)
- condizioni (6): preset_pos, preset_neg, blockshuf_pos, blockshuf_neg, rand_pos, rand_neg
- parametri: euler_ancestral, 9 steps, cfg 1.0, 1024x1280
- seed: 42, 777, 1337, 9999, 4242145
- naming: renders/{pid}_{cond}_seed{seed}_00001_.png
- output folder: C:\\StabilityMatrix-win-x64\\Data\\Packages\\ComfyUI\\output\\benchmark_stage7\\renders
- manifesto: stage7b_images.csv
"""

import os
import sys
import glob
import json
import shutil
import hashlib
import urllib.request
import csv
import argparse
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stage7_prompts import STAGE7_CANDIDATES
from stage5_config import CORE_SEEDS, make_condition_id, suite_fingerprint

COMFY_URL = "http://127.0.0.1:8188"
SLUG = "benchmark_stage7"
ROOT_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output" + rf"\{SLUG}"
ROOT_IMG = os.path.join(ROOT_DIR, "renders")
PILOT_ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
CSV_PATH = os.path.join(PILOT_ROOT, "stage7b_images.csv")
REPORT_CSV_PATH = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\stage7b_images.csv"
CONFIRM_CSV_PATH = os.path.join(PILOT_ROOT, "confirmation_prompts.csv")

STEPS, CFG, WIDTH, HEIGHT = 9, 1.0, 1024, 1280
SAMPLER, SCHEDULER = "euler_ancestral", "simple"

CONDITIONS = [
    ("preset_pos", "preset", "Arthemy_Bench_Base"),
    ("preset_neg", "preset", "Arthemy_Bench_NEG"),
    ("blockshuf_pos", "preset_blockshuffle", "Arthemy_Bench_BLOCKSHUFFLE"),
    ("blockshuf_neg", "preset_blockshuffle", "Arthemy_Bench_BLOCKSHUFFLE_NEG"),
    ("rand_pos", "preset_randsign", "Arthemy_Bench_RANDSIGN"),
    ("rand_neg", "preset_randsign", "Arthemy_Bench_RANDSIGN_NEG"),
]

FIELDS = ["run_id", "stage", "condition_id", "cond_name", "renders_root",
          "image_path", "baseline_path", "prompt_id", "prompt_sha1", "prompt_tag",
          "prompt_text", "seed", "sampler", "steps", "cfg", "width", "height",
          "operation", "preset_file", "suite_git_sha", "timestamp"]


def build_workflow(preset_name, text, seed, tag):
    wf = {
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
    if preset_name:
        wf["70"] = {"class_type": "ArthemyKrea2PresetLoader",
                    "inputs": {"model": ["37", 0], "clip": ["37", 1], "preset": preset_name + ".json",
                               "strength_model": 1.0, "strength_clip": 1.0, "custom_path": ""}}
        wf["40"]["inputs"]["clip"] = ["70", 1]
        wf["42"]["inputs"]["model"] = ["70", 0]
    return wf


def queue_prompt(wf):
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def load_selected_prompts():
    if not os.path.exists(CONFIRM_CSV_PATH):
        raise FileNotFoundError(f"Manca {CONFIRM_CSV_PATH} da Tempo A!")
    with open(CONFIRM_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sel_shas = {r["prompt_sha1"] for r in reader}
    
    selected = [p for p in STAGE7_CANDIDATES if p["sha1"] in sel_shas]
    if len(selected) != 16:
        raise ValueError(f"Attesi 16 prompt selezionati, trovati {len(selected)} in STAGE7_CANDIDATES!")
    return selected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Crea solo il manifesto senza inviare richieste a ComfyUI")
    args = ap.parse_args()

    os.makedirs(ROOT_IMG, exist_ok=True)
    fp = suite_fingerprint()
    run_id = f"stage7b_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    selected_prompts = load_selected_prompts()

    print("==================================================================")
    print(" STAGE 7 (Tempo B: 16 prompt selezionati x 6 condizioni x 5 seed = 480 render)")
    print(f" Impronta suite: {fp}")
    print(f" Output folder:  {ROOT_IMG}")
    print(f" Manifesto:      {CSV_PATH}")
    print("==================================================================")

    tasks = []
    for p in selected_prompts:
        pid, txt, tag = p["id"], p["text"], p["tag"]
        sha = hashlib.sha1(txt.encode("utf-8")).hexdigest()[:10]

        for cond_name, op, preset_stem in CONDITIONS:
            cid = make_condition_id("stage7b", preset_stem, "")
            for s in CORE_SEEDS:
                img_tag = f"{pid}_{cond_name}_seed{s}"
                img_rel = f"renders/{img_tag}_00001_.png"
                base_rel = f"renders/{pid}_baseline_seed{s}_00001_.png"
                row = dict(
                    run_id=run_id, stage="stage7b",
                    condition_id=cid,
                    cond_name=cond_name,
                    renders_root=ROOT_IMG,
                    image_path=img_rel,
                    baseline_path=base_rel,
                    prompt_id=pid,
                    prompt_sha1=sha,
                    prompt_tag=tag,
                    prompt_text=txt,
                    seed=str(s),
                    sampler=SAMPLER, steps=STEPS, cfg=CFG,
                    width=WIDTH, height=HEIGHT,
                    operation=op,
                    preset_file=f"{preset_stem}.json",
                    suite_git_sha=fp,
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                tasks.append((img_tag, preset_stem, txt, s, row))

    expected_total = 16 * 6 * 5
    if len(tasks) != expected_total:
        raise ValueError(f"Attesi {expected_total} task, ma calcolati {len(tasks)}")
    print(f"[Stage 7b] Pianificati {len(tasks)} render.")

    # Scrivi il manifesto
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for _, _, _, _, r in tasks:
            w.writerow(r)
    print(f"[Stage 7b] Manifesto salvato: {CSV_PATH}")

    # Sincronizza su report/data se la cartella esiste
    if os.path.exists(os.path.dirname(REPORT_CSV_PATH)):
        shutil.copy2(CSV_PATH, REPORT_CSV_PATH)
        print(f"[Stage 7b] Manifesto sincronizzato: {REPORT_CSV_PATH}")

    if args.dry_run:
        print("[Stage 7b] Dry-run completato.")
        return

    # Invia le generazioni a ComfyUI in batch veloce
    print("[Stage 7b] Invio richieste alla coda di ComfyUI...")
    queued_count = 0
    skipped_count = 0
    for idx, (img_tag, preset_stem, txt, s, _) in enumerate(tasks, 1):
        target_png = os.path.join(ROOT_DIR, f"renders/{img_tag}_00001_.png")
        if os.path.exists(target_png):
            skipped_count += 1
            continue
        wf = build_workflow(preset_stem, txt, s, img_tag)
        queue_prompt(wf)
        queued_count += 1
        if queued_count % 30 == 0 or queued_count == len(tasks):
            print(f"  [{idx:03d}/{len(tasks):03d}] Accodati {queued_count} task...")

    print(f"\n[Stage 7b] Accodamento completato: {queued_count} nuovi task registrati, {skipped_count} gia' presenti.")

    # Verifica immediata della coda
    try:
        req = urllib.request.urlopen(f"{COMFY_URL}/queue")
        qdata = json.loads(req.read().decode("utf-8"))
        r_len = len(qdata.get("queue_running", []))
        p_len = len(qdata.get("queue_pending", []))
        print(f"[Stage 7b] Stato ComfyUI Queue: {r_len} in esecuzione, {p_len} in attesa.")
    except Exception as e:
        print(f"[Stage 7b] Errore verifica queue: {e}")


if __name__ == "__main__":
    main()
