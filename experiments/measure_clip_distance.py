# -*- coding: utf-8 -*-
"""
experiments/measure_clip_distance.py
====================================
The half of `clip-224-is-blind-to-it` that needs the encoder. MUST RUN LOCALLY: it loads
Data/Models/ClipVision/clip_vision_h.safetensors through ComfyUI's own loader, so nothing is
downloaded and no new dependency is introduced. No renders.

Page 01 has claimed since it was written that CLIP at 224x224 cannot see the mark-style
shift. `experiments/measure_downsample_blindness.py` has now tested the REASON the page gave
-- that the resample destroys the signal -- and found it wanting: several of the statistics
that separate the preset from its control keep most of their effect size at 224, and one
grows. What remains untested is the encoder itself: a learned representation can be blind to
a signal that survives the resample, because it was never trained to encode it.

This measures exactly that, and nothing else:

  for each prompt, at one seed, encode the preset arm and the block-shuffle control, and
  record 1 - cos(e_preset, e_control) in CLIP's embedding space;
  as a scale, encode the same preset arm against a DIFFERENT PROMPT's render, which is a
  change CLIP certainly sees. Blindness is a claim about the ratio, not about a raw cosine:
  without the second number a small distance means nothing.

Then the same paired statistics as the rest of the notebook: mean, Cohen's dz, exact
sign-flip p over prompts. The prompt is the unit; seeds are repeated measures (pitfall 17).

Read this before believing the output: clip_vision_h is ViT-H/14 trained on LAION, not the
OpenAI ViT-B/32 the phrase "CLIP at 224" usually means. Both read 224x224, so the resampling
argument applies to both, but a result here is a result about THIS encoder and the page must
say so.

Usage (from the repository root, with ComfyUI on the path):
    python experiments/measure_clip_distance.py \
        --renders "C:/StabilityMatrix-win-x64/Data/Images/Text2Img/benchmark_stage7/renders" \
        --manifest data/stage7b_images.csv --seed 1337 \
        --out data/clip_distance_mark_style.csv
"""

from __future__ import annotations

import argparse
import csv
import itertools
import os
import statistics
import sys

import numpy as np
import torch

COMFY = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
CLIP_VISION = r"C:\StabilityMatrix-win-x64\Data\Models\ClipVision\clip_vision_h.safetensors"
sys.path.insert(0, COMFY)

import comfy.clip_vision            # noqa: E402
from PIL import Image               # noqa: E402


def load_image(path: str) -> torch.Tensor:
    """ComfyUI's LoadImage convention: float32 in [0, 1], shape (1, H, W, 3)."""
    img = Image.open(path).convert("RGB")
    arr = np.array(img).astype(np.float32) / 255.0
    return torch.from_numpy(arr)[None, ]


def embed(model, path: str) -> np.ndarray:
    out = model.encode_image(load_image(path))
    vec = out["image_embeds"] if isinstance(out, dict) else out.image_embeds
    v = vec.detach().cpu().float().numpy().reshape(-1)
    return v / np.linalg.norm(v)


def sign_flip_p(diffs: list[float]) -> tuple[float, float]:
    n = len(diffs)
    if n > 20:
        raise SystemExit(f"{n} pairs is too many to enumerate exactly")
    obs = abs(statistics.fmean(diffs))
    hits = sum(1 for s in itertools.product((1, -1), repeat=n)
               if abs(statistics.fmean(a * d for a, d in zip(s, diffs))) >= obs - 1e-12)
    return hits / 2 ** n, 2 / 2 ** n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--treatment", default="preset_pos")
    ap.add_argument("--control", default="blockshuf_pos")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    if not os.path.exists(CLIP_VISION):
        sys.exit(f"{CLIP_VISION} is not there; point CLIP_VISION at the encoder you mean to use")
    model = comfy.clip_vision.load(CLIP_VISION)
    if model is None:
        sys.exit("ComfyUI could not load the CLIP vision model")

    rows = list(csv.DictReader(open(a.manifest, encoding="utf-8-sig")))
    cells: dict[str, dict[str, str]] = {}
    for r in rows:
        if r["seed"] == a.seed:
            cells.setdefault(r["prompt_id"], {})[r["cond_name"]] = os.path.basename(r["image_path"])
    prompts = sorted(p for p, c in cells.items() if a.treatment in c and a.control in c)
    if len(prompts) < 4:
        sys.exit(f"only {len(prompts)} prompts carry both arms at seed {a.seed}")

    emb = {}
    for p in prompts:
        for arm in (a.treatment, a.control):
            emb[(p, arm)] = embed(model, os.path.join(a.renders, cells[p][arm]))
            print(f"  encoded {p} {arm}", file=sys.stderr, flush=True)

    out = []
    for i, p in enumerate(prompts):
        other = prompts[(i + 1) % len(prompts)]
        within = 1.0 - float(emb[(p, a.treatment)] @ emb[(p, a.control)])
        across = 1.0 - float(emb[(p, a.treatment)] @ emb[(other, a.treatment)])
        out.append({
            "prompt_id": p,
            "seed": a.seed,
            "contrast": f"{a.treatment} vs {a.control}",
            "clip_distance_within_prompt": round(within, 6),
            "reference_prompt": other,
            "clip_distance_across_prompts": round(across, 6),
            "ratio_within_over_across": round(within / across, 6) if across else "",
            "encoder": os.path.basename(CLIP_VISION),
        })

    ratios = [r["ratio_within_over_across"] for r in out if isinstance(r["ratio_within_over_across"], float)]
    within = [r["clip_distance_within_prompt"] for r in out]
    dz = statistics.fmean(within) / statistics.stdev(within)
    p_val, floor = sign_flip_p(within)
    out.append({
        "prompt_id": "ALL",
        "seed": a.seed,
        "contrast": f"{a.treatment} vs {a.control}",
        "clip_distance_within_prompt": round(statistics.fmean(within), 6),
        "reference_prompt": f"{len(prompts)} prompts",
        "clip_distance_across_prompts": "",
        "ratio_within_over_across": round(statistics.fmean(ratios), 6) if ratios else "",
        "encoder": f"mean; dz = {dz:.4f}; sign-flip p = {p_val:.6f} (floor {floor:.6f})",
    })

    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"\nwrote {a.out}  ({len(out)} rows, {len(prompts)} prompts)")
    print(f"mean within-prompt CLIP distance {statistics.fmean(within):.5f}, "
          f"as a fraction of the across-prompt distance {statistics.fmean(ratios):.4f}")
    print("A small ratio is what 'blind' would look like. Publish the ratio, not the raw cosine.")


if __name__ == "__main__":
    main()
