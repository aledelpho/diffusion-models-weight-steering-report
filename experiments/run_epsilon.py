"""
experiments/run_epsilon.py  --  sessanta immagini per misurare un esponente

Quattro prompt originali x tre condizioni nuove x cinque seed = 60, circa 28
minuti. Scrive nella cartella dello Stage 4, accanto a HALF (che esiste gia' e
non si rigenera) e alle baseline con cui si appaiano.

La scala completa risulta:

    eps = 0.25   QUARTER      QUARTER_NEG     (nuove)
    eps = 0.50   HALF         HALF_NEG        (HALF gia' c'e')
    eps = 1.00   Base         NEG             (gia' ci sono entrambe)

tre punti, sei condizioni, e da li' la pendenza in log-log di ||A|| e ||S||.
"""

import os
import sys
import glob
import json
import hashlib
import urllib.request
import csv
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stage5_config import ORIGINAL_FOUR, CORE_SEEDS, make_condition_id, suite_fingerprint

COMFY_URL = "http://127.0.0.1:8188"
SLUG = "benchmark_stage4_preset"
ROOT_IMG = (r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"
            rf"\{SLUG}\renders")
PRESET_DIR = (r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
              r"\custom_nodes\Arthemy_Krea2_Tuner\presets")
CSV_PATH = r"c:\Users\aless\Desktop\comfyui-pilot\epsilon_images.csv"

STEPS, CFG, WIDTH, HEIGHT = 9, 1.0, 1024, 1280
SAMPLER, SCHEDULER = "euler_ancestral", "simple"

# solo le tre che mancano: HALF e' gia' generata, Base e NEG anche
NEW = [("Arthemy_Bench_HALF_NEG", "preset_half_neg", 0.50),
       ("Arthemy_Bench_QUARTER", "preset_quarter_pos", 0.25),
       ("Arthemy_Bench_QUARTER_NEG", "preset_quarter_neg", 0.25)]

FIELDS = ["run_id", "stage", "condition_id", "cond_name", "eps", "renders_root",
          "image_path", "baseline_path", "prompt_id", "prompt_sha1", "prompt_tag",
          "prompt_text", "seed", "sampler", "steps", "cfg", "width", "height",
          "operation", "preset_file", "suite_git_sha", "timestamp"]


def build(preset, text, seed, tag):
    wf = {
        "36": {"class_type": "UNETLoader",
               "inputs": {"unet_name": "krea2_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "47": {"class_type": "CLIPLoader",
               "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
        "48": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "45": {"class_type": "EmptyLatentImage", "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1}},
        "37": {"class_type": "ArthemyKrea2ResetPatcher",
               "inputs": {"model": ["36", 0], "clip": ["47", 0], "reset_model": True, "reset_clip": True}},
        "70": {"class_type": "ArthemyKrea2PresetLoader",
               "inputs": {"model": ["37", 0], "clip": ["37", 1], "preset": preset + ".json",
                          "strength_model": 1.0, "strength_clip": 1.0, "custom_path": ""}},
        "40": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["70", 1], "text": text}},
        "43": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["40", 0]}},
        "42": {"class_type": "KSampler",
               "inputs": {"model": ["70", 0], "positive": ["40", 0], "negative": ["43", 0],
                          "latent_image": ["45", 0], "seed": seed, "steps": STEPS, "cfg": CFG,
                          "sampler_name": SAMPLER, "scheduler": SCHEDULER, "denoise": 1.0}},
        "46": {"class_type": "VAEDecode", "inputs": {"samples": ["42", 0], "vae": ["48", 0]}},
        "61": {"class_type": "SaveImage",
               "inputs": {"images": ["46", 0], "filename_prefix": f"{SLUG}/renders/{tag}"}},
    }
    return wf


def queue(wf):
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    for name, _c, _e in NEW:
        p = os.path.join(PRESET_DIR, name + ".json")
        if not os.path.exists(p):
            raise FileNotFoundError(f"manca {p}: genera prima con derive_epsilon.py")

    fp = suite_fingerprint()
    run_id = f"eps_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"[epsilon] impronta del suite: {fp}")

    tasks = []
    for p in ORIGINAL_FOUR:
        pid, txt = p["id"], p["text"]
        sha = hashlib.sha1(txt.encode("utf-8")).hexdigest()[:10]
        for preset, cond, eps in NEW:
            cid = make_condition_id("epsilon", preset)
            for s in CORE_SEEDS:
                tag = f"{pid}_{cond}_seed{s}"
                tasks.append((tag, preset, txt, s, dict(
                    run_id=run_id, stage="epsilon", condition_id=cid, cond_name=cond,
                    eps=eps, renders_root=ROOT_IMG,
                    image_path=f"renders/{tag}_00001_.png",
                    baseline_path=f"renders/{pid}_baseline_seed{s}_00001_.png",
                    prompt_id=pid, prompt_sha1=sha, prompt_tag=p["tag"], prompt_text=txt,
                    seed=s, sampler=SAMPLER, steps=STEPS, cfg=CFG, width=WIDTH,
                    height=HEIGHT, operation="preset", preset_file=preset + ".json",
                    suite_git_sha=fp, timestamp="")))

    print(f"=== epsilon: {len(tasks)} Total Tasks ===")
    if len(tasks) != 60:
        raise ValueError(f"attesi 60 task, configurati {len(tasks)}")

    try:
        urllib.request.urlopen(f"{COMFY_URL}/system_stats", timeout=5)
    except Exception as e:
        print(f"[epsilon] ERRORE: ComfyUI non risponde su {COMFY_URL}: {e}")
        sys.exit(1)

    os.makedirs(ROOT_IMG, exist_ok=True)
    rows, n, skip = [], 0, 0
    for tag, preset, txt, seed, row in tasks:
        row["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows.append(row)
        if glob.glob(os.path.join(ROOT_IMG, f"{tag}_00001_.png")):
            skip += 1
            continue
        queue(build(preset, txt, seed, tag))
        n += 1
        if n % 20 == 0 or n == 1:
            print(f"  [{n} accodati] ultimo: {tag}")

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    print(f"\n[epsilon] accodati {n}, gia' presenti {skip}")
    print(f"[epsilon] {CSV_PATH}")


if __name__ == "__main__":
    main()
