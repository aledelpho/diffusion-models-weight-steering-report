"""Queue the residual-probe runs (docs/prereg_residual_probe.md). Run by Alessandro only.

23 baseline renders, no weight edit: the 12 prompts of single_blocks_styles, the 6 of
v3 and the 5 of v4, each with the seed of its bench. Workflow identical to the
benchmark queues, plus the ArthemyResidualProbe node (tools/comfy_residual_probe,
copied into ComfyUI/custom_nodes) between ResetPatcher and KSampler.
Images go to benchmark_residual_probe/ and must be pixel-identical to the existing
baselines (the probe is read-only): checked by analyze_residual_probe.py --repro.

  python experiments/queue_residual_probe.py            # queue all 23
  python experiments/queue_residual_probe.py --first 1  # queue only the first, to try the node
"""
import argparse, csv, json, urllib.request
from pathlib import Path

COMFY_HOST = "http://127.0.0.1:8188"
REPO = Path(__file__).resolve().parent.parent
PLANS = ["single_blocks_styles_plan.csv", "single_blocks_v3_plan.csv", "single_blocks_v4_plan.csv"]
RAW = REPO / "data" / "residual_probe_raw.csv"
OUT_FOLDER = "benchmark_residual_probe"


def baselines():
    rows = []
    for p in PLANS:
        for r in csv.DictReader(open(REPO / "data" / p, encoding="utf-8-sig")):
            if r["condition"] == "baseline":
                r["_plan"] = p
                rows.append(r)
    assert len(rows) == 23, len(rows)
    return rows


def workflow(r):
    label = f"{r['prompt_id']}_seed{r['seed']}"
    return {
        "36": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "47": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
        "48": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "45": {"class_type": "EmptyLatentImage", "inputs": {"width": int(r["width"]), "height": int(r["height"]), "batch_size": 1}},
        "37": {"class_type": "ArthemyKrea2ResetPatcher", "inputs": {"model": ["36", 0], "clip": ["47", 0], "reset_model": True, "reset_clip": True}},
        "70": {"class_type": "ArthemyResidualProbe", "inputs": {"model": ["37", 0], "csv_path": str(RAW), "run_label": label}},
        "40": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["37", 1], "text": r["prompt_text"]}},
        "43": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["40", 0]}},
        "42": {"class_type": "KSampler", "inputs": {"model": ["70", 0], "positive": ["40", 0], "negative": ["43", 0],
                                                     "latent_image": ["45", 0], "seed": int(r["seed"]), "steps": int(r["steps"]),
                                                     "cfg": float(r["cfg"]), "sampler_name": r["sampler"],
                                                     "scheduler": r["scheduler"], "denoise": float(r["denoise"])}},
        "46": {"class_type": "VAEDecode", "inputs": {"samples": ["42", 0], "vae": ["48", 0]}},
        "61": {"class_type": "SaveImage", "inputs": {"images": ["46", 0], "filename_prefix": f"{OUT_FOLDER}/PROBE_{label}"}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", type=int, default=23)
    n = ap.parse_args().first
    for r in baselines()[:n]:
        data = json.dumps({"prompt": workflow(r)}).encode()
        req = urllib.request.Request(f"{COMFY_HOST}/prompt", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("queued", r["prompt_id"], r["seed"], json.loads(resp.read()).get("prompt_id"))


if __name__ == "__main__":
    main()
