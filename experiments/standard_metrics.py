"""Standard image metrics for C45, C47, C49 (docs/prereg_standard_metrics.md).
Written by Claude, 2026-10-05. Runs on Alessandro's PC with the GPU (ComfyUI venv):

  <ComfyUI venv>\\Scripts\\python.exe -m pip install piq --no-deps
  <ComfyUI venv>\\Scripts\\python.exe experiments/standard_metrics.py --bench c47
  ... --bench c49
  ... --bench c45

Per image (all at 512x640 unless stated):
  brisque      no-reference quality, piq.brisque (lower = better)
  clipiqa      no-reference quality, piq.CLIPIQA (higher = better)
  colorfulness Hasler-Suesstrunk on the full image
  clipscore    100 * cos(CLIP image, CLIP prompt text), open_clip ViT-B-32 laion2b_s34b_b79k
               (text truncated at 77 tokens by the tokenizer)
Per image against the baseline of the same prompt and seed:
  lpips, dists (piq, lower = closer), ssim (piq, higher = closer),
  dino_cos     cosine of DINOv2 ViT-B/14 CLS embeddings at 224x280 (higher = same content)
  clip_cos     cosine of CLIP image embeddings
Outputs data/standard_metrics_<bench>.csv and data/standard_metrics_<bench>_emb.npz
(DINOv2 and CLIP image embeddings, keyed "prompt|seed|cond").
"""
import argparse, csv, os, sys
import numpy as np
import torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")
IMG = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
DEV = "cuda" if torch.cuda.is_available() else "cpu"


def items(bench):
    """[(prompt_id, seed, cond, path, prompt_text)] with a 'baseline' cond for every (prompt, seed)."""
    out = []
    if bench == "c47":
        for r in csv.DictReader(open(os.path.join(DATA, "blk23_colorful_plan.csv"), encoding="utf-8")):
            out.append((r["prompt_id"], r["seed"], r["cond"], os.path.join(IMG, "benchmark_blk23_colorful", r["expected_filename"]), r["prompt_text"]))
    elif bench == "c49":
        for r in csv.DictReader(open(os.path.join(DATA, "prompt_family_plan.csv"), encoding="utf-8")):
            if r["prompt_id"].startswith("REPRO"):
                continue
            out.append((r["prompt_id"], r["seed"], r["cond"], os.path.join(IMG, "benchmark_prompt_family", r["expected_filename"]), r["prompt_text"]))
    elif bench == "c45":
        import analyze_prompt_writing as A
        txt = {}
        for r in csv.DictReader(open(os.path.join(DATA, "prompt_writing_plan.csv"), encoding="utf-8-sig")):
            txt[r["prompt_id"]] = r["prompt"]
        for r in csv.DictReader(open(os.path.join(DATA, "prompt_order_experiment_plan.csv"), encoding="utf-8-sig")):
            if r["prompt_id"] == "V1_Original": txt["S1_W1_original"] = r["prompt"]
            if r["prompt_id"] == "V5_Inverse": txt["S1_W2_reordered"] = r["prompt"]
        for pid in A.WRIT["S1"] + A.WRIT["S2"] + list(A.CONTENT.values()):
            for c in A.plan():
                for s in A.SEEDS:
                    out.append((pid, s, c, A.path(pid, c, s), txt[pid]))
    else:
        raise SystemExit("bench must be c45, c47 or c49")
    return out


def load(p, size):
    im = Image.open(p).convert("RGB").resize(size, Image.BICUBIC)
    return torch.from_numpy(np.asarray(im, dtype=np.float32) / 255.0).permute(2, 0, 1)[None]


def colorfulness(p):
    a = np.asarray(Image.open(p).convert("RGB"), dtype=np.float64)
    rg = a[..., 0] - a[..., 1]; yb = 0.5 * (a[..., 0] + a[..., 1]) - a[..., 2]
    return float(np.hypot(rg.std(), yb.std()) + 0.3 * np.hypot(rg.mean(), yb.mean()))


@torch.no_grad()
def main():
    import piq, open_clip
    ap = argparse.ArgumentParser(); ap.add_argument("--bench", required=True); b = ap.parse_args().bench
    it = items(b)
    missing = [x[3] for x in it if not os.path.exists(x[3])]
    assert not missing, f"{len(missing)} missing, e.g. {missing[:2]}"
    lp, di, ciqa = piq.LPIPS().to(DEV), piq.DISTS().to(DEV), piq.CLIPIQA(data_range=1.).to(DEV)
    clip, _, prep = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
    clip = clip.to(DEV).eval(); tok = open_clip.get_tokenizer("ViT-B-32")
    dino = torch.hub.load("facebookresearch/dinov2", "dinov2_vitb14").to(DEV).eval()
    mean = torch.tensor([0.485, 0.456, 0.406], device=DEV)[:, None, None]; std = torch.tensor([0.229, 0.224, 0.225], device=DEV)[:, None, None]
    per, emb_d, emb_c = {}, {}, {}
    for n, (pid, seed, cond, p, text) in enumerate(it):
        x = load(p, (512, 640)).to(DEV)
        d = dino(((load(p, (224, 280)).to(DEV)[0] - mean) / std)[None])[0]
        ci = clip.encode_image(prep(Image.open(p).convert("RGB"))[None].to(DEV))[0]
        ct = clip.encode_text(tok([text]).to(DEV))[0]
        d = d / d.norm(); ci = ci / ci.norm(); ct = ct / ct.norm()
        per[(pid, seed, cond)] = {"x": x, "d": d, "c": ci,
                                  "brisque": float(piq.brisque(x, data_range=1.)), "clipiqa": float(ciqa(x).mean()),
                                  "colorfulness": colorfulness(p), "clipscore": float(100 * (ci @ ct))}
        emb_d[f"{pid}|{seed}|{cond}"] = d.cpu().numpy(); emb_c[f"{pid}|{seed}|{cond}"] = ci.cpu().numpy()
        if n % 50 == 0:
            print(n, "/", len(it), flush=True)
    rows = []
    for (pid, seed, cond), v in per.items():
        base = per[(pid, seed, "baseline")]
        r = {"prompt_id": pid, "seed": seed, "cond": cond, **{k: round(v[k], 5) for k in ("brisque", "clipiqa", "colorfulness", "clipscore")}}
        if cond == "baseline":
            r.update(lpips="", dists="", ssim="", dino_cos="", clip_cos="")
        else:
            r.update(lpips=round(float(lp(v["x"], base["x"])), 5), dists=round(float(di(v["x"], base["x"])), 5),
                     ssim=round(float(piq.ssim(v["x"], base["x"], data_range=1.)), 5),
                     dino_cos=round(float(v["d"] @ base["d"]), 5), clip_cos=round(float(v["c"] @ base["c"]), 5))
        rows.append(r)
    with open(os.path.join(DATA, f"standard_metrics_{b}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    np.savez_compressed(os.path.join(DATA, f"standard_metrics_{b}_emb.npz"),
                        keys=np.array(list(emb_d)), dino=np.array(list(emb_d.values())), clip=np.array(list(emb_c.values())))
    print("written", len(rows), "rows")


if __name__ == "__main__":
    main()
