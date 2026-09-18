# -*- coding: utf-8 -*-
"""
experiments/run_stage9.py  --  Stage 9: La Direzione Dipende dallo Stile Dichiarato?

300 render totali:
- Parte 1 (Varianti di Stile): 8 prompt x (1 baseline + 3 condizioni x 2 ampiezze) x 5 seed = 280 render
  - Condizioni: baseline, preset_pos (1.0 e 2.0), blockshuf_neg (1.0 e 2.0), rand_pos (1.0 e 2.0)
  - Prompt da stage9_prompts.json (S1_photo .. S8_charcoal)
- Parte 2 (Chaos Edges V2): 4 prompt I x 1 condizione x 5 seed = 20 render
  - Condizione: chaos_edges_v2 (ampiezza 1.0)
  - Prompt I06, I07, I20, I24 (baseline preesistente da Stage 7a)

Parametri standard:
- Sampler: euler_ancestral, scheduler: simple, steps: 9, cfg: 1.0
- Risoluzione: 1024x1280
- Seed: 42, 777, 1337, 9999, 4242145
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
SLUG = "benchmark_stage9"
ROOT_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output" + rf"\{SLUG}"
ROOT_IMG = os.path.join(ROOT_DIR, "renders")

STAGE7A_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage7a\renders"

CSV_PATH_PILOT = os.path.join(PILOT_ROOT, "stage9_images.csv")
CSV_PATH_REPORT = os.path.join(REPORT_ROOT, "data", "stage9_images.csv")
PROMPTS_JSON_PATH = os.path.join(PILOT_ROOT, "stage9_prompts.json")

STEPS, CFG, WIDTH, HEIGHT = 9, 1.0, 1024, 1280
SAMPLER, SCHEDULER = "euler_ancestral", "simple"
CORE_SEEDS = [42, 777, 1337, 9999, 4242145]

# Condizioni per Parte 1 (8 prompt di stile, 7 condizioni)
CONDITIONS_STYLE = [
    ("baseline", "baseline", None, 1.0),
    ("preset_pos_1x", "preset", "Arthemy_Bench_Base", 1.0),
    ("preset_pos_2x", "preset", "Arthemy_Bench_Base", 2.0),
    ("blockshuf_neg_1x", "preset_blockshuffle", "Arthemy_Bench_BLOCKSHUFFLE_NEG", 1.0),
    ("blockshuf_neg_2x", "preset_blockshuffle", "Arthemy_Bench_BLOCKSHUFFLE_NEG", 2.0),
    ("rand_pos_1x", "preset_randsign", "Arthemy_Bench_RANDSIGN", 1.0),
    ("rand_pos_2x", "preset_randsign", "Arthemy_Bench_RANDSIGN", 2.0),
]

# 4 Prompt I dello Stage 7 per Chaos Edges V2
PROMPTS_CHAOS_V2 = [
    {
        "prompt_id": "I06",
        "prompt_sha1": "a324a148e4",
        "prompt_tag": "female_elf_ranger",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, hard teal-tinted rim light glowing along the edges of her face, upper body portrait. A lithe female elf ranger, sharp cheekbones, long silver hair braided with green vines, piercing amber eyes with a focused calculating gaze, dark leather cowl pulled low over her pointed ears, holding a notched wooden arrow. Simple background, teal overall hue, monochromatic teal."
    },
    {
        "prompt_id": "I07",
        "prompt_sha1": "402376662d",
        "prompt_tag": "male_cyborg_soldier",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, hard crimson-tinted rim light glowing along the edges of his face, upper body portrait. A battle-scarred male cyborg soldier, half of his skull replaced by polished chrome plating, glowing red ocular implant humming faintly, tight jawline set in grim defiance, tactical ballistic collar framing his throat. Simple background, crimson overall hue, monochromatic crimson."
    },
    {
        "prompt_id": "I20",
        "prompt_sha1": "952efcc3c6",
        "prompt_tag": "tiefling_warlock",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, hard purple-tinted rim light glowing along the edges of his face, upper body portrait. A sinister male tiefling warlock, obsidian skin, obsidian ram horns curving backward, smirking lips displaying sharp pointed teeth, dark hooded mantle pinned by a tarnished bronze amulet. Simple background, purple overall hue, monochromatic purple."
    },
    {
        "prompt_id": "I24",
        "prompt_sha1": "66faaa372d",
        "prompt_tag": "female_water_genasi",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, hard blue-tinted rim light glowing along the edges of her face, upper body portrait. A serene female water genasi, translucent turquoise skin with faint crystalline ripples, floating azure hair defying gravity, droplet-shaped silver earrings, relaxed thoughtful expression. Simple background, blue overall hue, monochromatic blue."
    }
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


def load_style_prompts():
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
    run_id = f"stage9_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    style_prompts = load_style_prompts()
    print("==================================================================")
    print(" STAGE 9: La Direzione Dipende dallo Stile Dichiarato?")
    print(f" Impronta suite: {fp}")
    print(f" Output folder:  {ROOT_IMG}")
    print(f" Manifesto:      {CSV_PATH_PILOT}")
    print("==================================================================")

    tasks = []

    # 1. Parte 1: 8 prompt di stile x 7 condizioni x 5 seed = 280 render
    for p in style_prompts:
        pid, txt, tag, sha = p["prompt_id"], p["text"], p["prompt_id"], p["prompt_sha1"]
        for cond_name, op, preset_stem, strength in CONDITIONS_STYLE:
            cid = make_condition_id("stage9", preset_stem or "baseline", strength)
            for s in CORE_SEEDS:
                img_tag = f"{pid}_{cond_name}_seed{s}"
                img_rel = f"renders/{img_tag}_00001_.png"
                base_rel = f"renders/{pid}_baseline_seed{s}_00001_.png"
                row = dict(
                    run_id=run_id, stage="stage9", arm="style_variants",
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

    # 2. Parte 2: 4 prompt I x 1 condizione (chaos_edges_v2) x 5 seed = 20 render
    for p in PROMPTS_CHAOS_V2:
        pid, txt, tag, sha = p["prompt_id"], p["prompt_text"], p["prompt_tag"], p["prompt_sha1"]
        cond_name = "chaos_edges_v2"
        preset_stem = "Arthemy_Bench_CHAOS_EDGES_V2"
        op = "chaos_edges_v2"
        strength = 1.0
        cid = make_condition_id("stage9", preset_stem, strength)
        for s in CORE_SEEDS:
            img_tag = f"{pid}_{cond_name}_seed{s}"
            img_rel = f"renders/{img_tag}_00001_.png"
            base_rel = os.path.join(STAGE7A_DIR, f"{pid}_baseline_seed{s}_00001_.png")
            row = dict(
                run_id=run_id, stage="stage9", arm="chaos_edges_v2",
                condition_id=cid, cond_name=cond_name, strength=str(strength),
                renders_root=ROOT_IMG,
                image_path=img_rel, baseline_path=base_rel,
                prompt_id=pid, prompt_sha1=sha, prompt_tag=tag,
                prompt_text=txt, seed=str(s),
                sampler=SAMPLER, steps=STEPS, cfg=CFG,
                width=WIDTH, height=HEIGHT, operation=op,
                preset_file=f"{preset_stem}.json",
                suite_git_sha=fp,
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            tasks.append((img_tag, preset_stem, strength, txt, s, row))

    expected_total = 280 + 20
    if len(tasks) != expected_total:
        raise ValueError(f"Attesi {expected_total} task, ma pianificati {len(tasks)}!")
    print(f"[Stage 9] Pianificazione completata: {len(tasks)} render (Parte 1: 280, Parte 2: 20).")

    # Scrivi il manifesto
    with open(CSV_PATH_PILOT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for _, _, _, _, _, r in tasks:
            w.writerow(r)
    print(f"[Stage 9] Manifesto salvato: {CSV_PATH_PILOT}")

    # Sincronizza su report/data
    if os.path.exists(os.path.dirname(CSV_PATH_REPORT)):
        shutil.copy2(CSV_PATH_PILOT, CSV_PATH_REPORT)
        print(f"[Stage 9] Manifesto sincronizzato: {CSV_PATH_REPORT}")

    if args.dry_run:
        print("[Stage 9] Dry-run completato con successo.")
        return

    # Invia le generazioni a ComfyUI in batch veloce
    print("[Stage 9] Invio richieste alla coda di ComfyUI...")
    queued_count = 0
    skipped_count = 0
    for idx, (img_tag, preset_stem, strength, txt, s, _) in enumerate(tasks, 1):
        target_png = os.path.join(ROOT_DIR, f"renders/{img_tag}_00001_.png")
        if os.path.exists(target_png):
            skipped_count += 1
            continue
        wf = build_workflow(preset_stem, strength, txt, s, img_tag)
        queue_prompt(wf)
        queued_count += 1
        if queued_count % 30 == 0 or queued_count == len(tasks):
            print(f"  [{idx:03d}/{len(tasks):03d}] Accodati {queued_count} task...")

    print(f"\n[Stage 9] Accodamento completato: {queued_count} nuovi task registrati, {skipped_count} gia' presenti.")

    # Verifica immediata della coda
    try:
        req = urllib.request.urlopen(f"{COMFY_URL}/queue", timeout=5)
        qdata = json.loads(req.read().decode("utf-8"))
        r_len = len(qdata.get("queue_running", []))
        p_len = len(qdata.get("queue_pending", []))
        print(f"[Stage 9] Stato ComfyUI Queue: {r_len} in esecuzione, {p_len} in attesa.")
    except Exception as e:
        print(f"[Stage 9] Errore verifica queue: {e}")


if __name__ == "__main__":
    main()
