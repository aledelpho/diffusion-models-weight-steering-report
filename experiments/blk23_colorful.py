"""C47 — blk23 against "colorful" in the prompt (docs/prereg_blk23_vs_colorful.md).

Written by Claude, 2026-10-04. Three steps, run in this order:

  python experiments/blk23_colorful.py --plan            # writes data/blk23_colorful_plan.csv (128 rows)
  python experiments/blk23_colorful.py --queue --first 1 # one render, to try the chain
  python experiments/blk23_colorful.py --queue           # the rest (skips files that exist)
  python experiments/blk23_colorful.py --repro           # seed-A images that already exist must be identical

Output folder: Text2Img/benchmark_blk23_colorful, files
{prompt_id}_{cond}_krea2_seed{seed}_00001_.png (the names analyze_blk23_vs_colorful.py reads).
Workflow identical to queue_single_blocks_styles.py; the Tuner node is used only for b23_* rows.
"""
import argparse, csv, json, os, time, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
PLAN = DATA / "blk23_colorful_plan.csv"
IMG_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img")
FOLDER = "benchmark_blk23_colorful"
COMFY = "http://127.0.0.1:8188"

PROMPTS = [("E1_cartoon", "single_blocks_styles_plan.csv", "2718281"),
           ("E3_oil", "single_blocks_styles_plan.csv", "2718281"),
           ("E7_sepiaphoto", "single_blocks_styles_plan.csv", "2718281"),
           ("C2_rally", "single_blocks_styles_plan.csv", "2718281"),
           ("C3_fox", "single_blocks_styles_plan.csv", "2718281"),
           ("C4_stilllife", "single_blocks_styles_plan.csv", "2718281"),
           ("P3_archerforest", "single_blocks_v3_plan.csv", "3141592"),
           ("P4_selfie", "single_blocks_v3_plan.csv", "1618033")]
SEED_B = "4669201"
TXT_POS = ", colorful, vivid highly saturated colors"
TXT_NEG = ", muted colors, desaturated, low saturation"
CONDS = [("baseline", None, None), ("txtpos", None, TXT_POS), ("txtneg", None, TXT_NEG),
         ("b23_m0.450", -0.45, None), ("b23_m0.300", -0.30, None), ("b23_m0.150", -0.15, None),
         ("b23_p0.150", 0.15, None), ("b23_p0.300", 0.30, None)]
# seed-A conditions that already exist in the single-block benches (for --repro)
EXISTING = {"baseline": "baseline", "b23_m0.300": "blk23_neg_d0.300",
            "b23_p0.300": "blk23_pos_d0.300", "b23_p0.150": "blk23_pos_d0.150"}


def add_suffix(text, suffix):
    t = text.rstrip()
    if t.endswith((".", ",")):
        return t + " " + suffix[2:]
    return t + suffix


def vector(dose):
    v = [0.0] * 34
    if dose is not None:
        v[23] = dose
    return ",".join(f"{x:.3f}" for x in v)


def make_plan():
    rows = []
    for pid, src, seed_a in PROMPTS:
        base = [r for r in csv.DictReader(open(DATA / src, encoding="utf-8-sig"))
                if r["prompt_id"] == pid and r["condition"] == "baseline"]
        assert len(base) == 1, (pid, len(base))
        b = base[0]
        assert b["seed"] == seed_a, (pid, b["seed"])
        for k in ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height"):
            assert b[k] == {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0",
                            "denoise": "1.0", "width": "1024", "height": "1280"}[k], (pid, k, b[k])
        for seed in (seed_a, SEED_B):
            for cond, dose, suffix in CONDS:
                text = add_suffix(b["prompt_text"], suffix) if suffix else b["prompt_text"]
                prefix = f"{pid}_{cond}_krea2_seed{seed}"
                rows.append({"row": len(rows), "prompt_id": pid, "seed": seed, "cond": cond,
                             "dose": "" if dose is None else f"{dose:.3f}",
                             "vectors_override": vector(dose) if dose is not None else "",
                             "prompt_text": text, "output_prefix": prefix,
                             "expected_filename": f"{prefix}_00001_.png",
                             **{k: b[k] for k in ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")}})
    assert len(rows) == 128, len(rows)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))
    ex = [r for r in rows if r["prompt_id"] in ("C3_fox", "P4_selfie") and r["seed"] == SEED_B and r["cond"] in ("txtpos", "txtneg")]
    for r in ex:
        print(f"\n[{r['prompt_id']} {r['cond']}]\n{r['prompt_text']}")


def workflow(r):
    perturbed = bool(r["vectors_override"])
    wf = {
        "36": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "47": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
        "48": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "45": {"class_type": "EmptyLatentImage", "inputs": {"width": int(r["width"]), "height": int(r["height"]), "batch_size": 1}},
        "37": {"class_type": "ArthemyKrea2ResetPatcher", "inputs": {"model": ["36", 0], "clip": ["47", 0], "reset_model": True, "reset_clip": True}},
        "40": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["37", 1], "text": r["prompt_text"]}},
        "43": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["40", 0]}},
        "42": {"class_type": "KSampler", "inputs": {"model": ["50", 0] if perturbed else ["37", 0], "positive": ["40", 0],
                                                     "negative": ["43", 0], "latent_image": ["45", 0], "seed": int(r["seed"]),
                                                     "steps": int(r["steps"]), "cfg": float(r["cfg"]), "sampler_name": r["sampler"],
                                                     "scheduler": r["scheduler"], "denoise": float(r["denoise"])}},
        "46": {"class_type": "VAEDecode", "inputs": {"samples": ["42", 0], "vae": ["48", 0]}},
        "61": {"class_type": "SaveImage", "inputs": {"images": ["46", 0], "filename_prefix": f"{FOLDER}/{r['output_prefix']}"}},
    }
    if perturbed:
        wf["50"] = {"class_type": "ArthemyKrea2ModelTuner", "inputs": {
            "model": ["37", 0], "mode": "Real Value", "vectors_override": r["vectors_override"], "granular_json": "",
            "Text_Fusion": 0.0, "Time_Embed": 0.0, "Projection": 0.0, "Block_1": 0.0, "Block_2": 0.0,
            "Block_3": 0.0, "Block_4": 0.0, "Block_5": 0.0, "Block_6": 0.0}}
    return wf


def queue(first):
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    if first:
        rows = rows[:first]
    n = 0
    for r in rows:
        if (IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
        print("queued", r["output_prefix"])
    print("queued", n, "of", len(rows))


def repro():
    import numpy as np
    from PIL import Image
    src = {"single_blocks_styles_plan.csv": "benchmark_single_blocks_styles", "single_blocks_v3_plan.csv": "benchmark_single_blocks_v3"}
    bad = checked = 0
    for pid, plan, seed in PROMPTS:
        for cond, old in EXISTING.items():
            ref = IMG_ROOT / src[plan] / "renders" / f"{pid}_{old}_krea2_seed{seed}_00001_.png"
            new = IMG_ROOT / FOLDER / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"
            if not ref.exists():
                continue
            if not new.exists():
                print("MISSING", new.name); bad += 1; continue
            a = np.asarray(Image.open(new).convert("RGB"), dtype=np.int16)
            b = np.asarray(Image.open(ref).convert("RGB"), dtype=np.int16)
            mx = int(np.abs(a - b).max()) if a.shape == b.shape else -1
            checked += 1; bad += mx != 0
            print(f"{pid:16s} {cond:11s} max abs diff {mx}")
    print("REPRO", "PASS" if bad == 0 and checked else "FAIL", f"({checked} pairs)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true"); ap.add_argument("--queue", action="store_true")
    ap.add_argument("--repro", action="store_true"); ap.add_argument("--first", type=int, default=0)
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.repro: repro()
