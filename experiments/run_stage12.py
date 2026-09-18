# -*- coding: utf-8 -*-
"""
experiments/run_stage12.py  --  Stage 12: Conferma Ingrandimento su Corpus Nuovo

250 render totali:
- 10 stili nuovi (S01_oil .. S10_synthwave) da stage12_prompts.json
- Nuovo soggetto: red and white vintage sports car on coastal cliff road at golden hour
- 5 condizioni:
  1. baseline (1.0)
  2. blockshuf_neg_1x (1.0)
  3. blockshuf_neg_2x (2.0)
  4. preset_pos_1x (1.0)
  5. preset_pos_2x (2.0)
- 5 seed standard: 42, 777, 1337, 9999, 4242145
- Totale: 10 x 5 x 5 = 250 render

Parametri standard:
- Sampler: euler_ancestral, scheduler: simple, steps: 9, cfg: 1.0
- Risoluzione: 1024x1280
- Output folder: benchmark_stage12/renders/
"""

import os
import sys
import json
import shutil
import hashlib
import urllib.request
import csv
import argparse
import datetime

PILOT_ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"

COMFY_URL = "http://127.0.0.1:8188"
SLUG = "benchmark_stage12"
ROOT_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output" + rf"\{SLUG}"
ROOT_IMG = os.path.join(ROOT_DIR, "renders")

CSV_PATH_PILOT = os.path.join(PILOT_ROOT, "stage12_images.csv")
CSV_PATH_REPORT = os.path.join(REPORT_ROOT, "data", "stage12_images.csv")
PROMPTS_JSON_PATH = os.path.join(REPORT_ROOT, "data", "stage12_prompts.json")
if not os.path.exists(PROMPTS_JSON_PATH):
    PROMPTS_JSON_PATH = os.path.join(PILOT_ROOT, "stage12_prompts.json")

STEPS, CFG, WIDTH, HEIGHT = 9, 1.0, 1024, 1280
SAMPLER, SCHEDULER = "euler_ancestral", "simple"
CORE_SEEDS = [42, 777, 1337, 9999, 4242145]

CONDITIONS_STAGE12 = [
    ("baseline", "baseline", None, 1.0),
    ("blockshuf_neg_1x", "preset_blockshuffle", "Arthemy_Bench_BLOCKSHUFFLE_NEG", 1.0),
    ("blockshuf_neg_2x", "preset_blockshuffle", "Arthemy_Bench_BLOCKSHUFFLE_NEG", 2.0),
    ("preset_pos_1x", "preset", "Arthemy_Bench_Base", 1.0),
    ("preset_pos_2x", "preset", "Arthemy_Bench_Base", 2.0),
]

FIELDS = [
    "run_id", "stage", "arm", "condition_id", "cond_name", "strength", "renders_root",
    "image_path", "baseline_path", "prompt_id", "prompt_sha1", "prompt_tag",
    "prompt_text", "seed", "sampler", "steps", "cfg", "width", "height",
    "operation", "preset_file", "suite_git_sha", "timestamp"
]


def suite_fingerprint():
    suite_dir = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_Krea2_Tuner"
    suite_files = ["Arthemy_Krea2_Tuner.py", "arthemy_geometry_engine.py"]
    h = hashlib.sha256()
    for name in suite_files:
        p = os.path.join(suite_dir, name)
        if os.path.exists(p):
            with open(p, "rb") as f:
                h.update(name.encode("utf-8"))
                h.update(f.read())
    return h.hexdigest()[:16]


def make_condition_id(stage, preset, strength):
    return hashlib.sha1(f"{stage}_{preset}_{strength}".encode("utf-8")).hexdigest()[:12]


def build_workflow(preset_name, strength, text, seed, tag):
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
                               "strength_model": float(strength), "strength_clip": float(strength), "custom_path": ""}}
        wf["40"]["inputs"]["clip"] = ["70", 1]
        wf["42"]["inputs"]["model"] = ["70", 0]
    return wf


def queue_prompt(wf):
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def load_prompts():
    if not os.path.exists(PROMPTS_JSON_PATH):
        raise FileNotFoundError(f"Manca il file: {PROMPTS_JSON_PATH}")
    with open(PROMPTS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Genera solo il manifesto senza inviare richieste a ComfyUI")
    args = ap.parse_args()

    os.makedirs(ROOT_IMG, exist_ok=True)
    fp = suite_fingerprint()
    run_id = f"stage12_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    prompts = load_prompts()
    print("==================================================================")
    print(" STAGE 12: Conferma Ingrandimento su Corpus Nuovo (250 Render)")
    print(f" Impronta suite: {fp}")
    print(f" Output folder:  {ROOT_IMG}")
    print(f" Manifesto:      {CSV_PATH_REPORT}")
    print("==================================================================")

    tasks = []

    # 10 stili x 5 condizioni x 5 seed = 250 render
    for p in prompts:
        pid, txt, tag, sha = p["prompt_id"], p["text"], p["prompt_id"], p["prompt_sha1"]
        for cond_name, op, preset_stem, strength in CONDITIONS_STAGE12:
            cid = make_condition_id("stage12", preset_stem or "baseline", strength)
            for s in CORE_SEEDS:
                img_tag = f"{pid}_{cond_name}_seed{s}"
                img_rel = f"renders/{img_tag}_00001_.png"
                base_rel = f"renders/{pid}_baseline_seed{s}_00001_.png"
                row = dict(
                    run_id=run_id, stage="stage12", arm="new_corpus_enlargement",
                    condition_id=cid, cond_name=cond_name, strength=str(strength),
                    renders_root=ROOT_IMG,
                    image_path=img_rel, baseline_path=base_rel,
                    prompt_id=pid, prompt_sha1=sha, prompt_tag=tag,
                    prompt_text=txt, seed=str(s),
                    sampler=SAMPLER, steps=STEPS, cfg=CFG,
                    width=WIDTH, height=HEIGHT, operation=op,
                    preset_file=f"{preset_stem}.json" if preset_stem else "",
                    suite_git_sha=fp,
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                tasks.append((img_tag, preset_stem, strength, txt, s, row))

    total = len(tasks)
    print(f"Totale task pianificati: {total} render")

    # Scrittura manifest CSV
    for csv_out in [CSV_PATH_PILOT, CSV_PATH_REPORT]:
        os.makedirs(os.path.dirname(csv_out), exist_ok=True)
        with open(csv_out, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for _, _, _, _, _, r in tasks:
                writer.writerow(r)
        print(f"[Manifest] Salvato: {csv_out}")

    if args.dry_run:
        print("\n[DRY RUN] Manifesto generato con successo. Nessuna richiesta inviata a ComfyUI.")
        return

    # Invio sequenziale rapido in coda (Fast Batch Queuing)
    print(f"\nInoltro delle {total} richieste a ComfyUI ({COMFY_URL})...")
    queued_count = 0
    for idx, (img_tag, preset_stem, strength, txt, s, _) in enumerate(tasks, 1):
        wf = build_workflow(preset_stem, strength, txt, s, img_tag)
        try:
            queue_prompt(wf)
            queued_count += 1
            if idx % 25 == 0 or idx == total:
                print(f"  Accodati: {idx}/{total} ({idx/total*100:.1f}%)")
        except Exception as e:
            print(f"  [ERRORE] Invio fallito per {img_tag}: {e}")

    print(f"\n[OK] Accodati con successo {queued_count}/{total} render.")

    # Verifica immediata dello stato della coda
    try:
        req = urllib.request.urlopen(f"{COMFY_URL}/queue", timeout=5)
        d = json.loads(req.read().decode("utf-8"))
        running = len(d.get("queue_running", []))
        pending = len(d.get("queue_pending", []))
        print(f"[Verifica Coda] Attivi in esecuzione: {running} | In attesa nella coda: {pending}")
    except Exception as e:
        print(f"[ATTENZIONE] Impossibile interrogare /queue: {e}")

    print("==================================================================")
    print(" BATCH STAGE 12 ACCODATO CON SUCCESSO. COOKING SILENZIOSO ATTIVO.")
    print("==================================================================")


if __name__ == "__main__":
    main()
