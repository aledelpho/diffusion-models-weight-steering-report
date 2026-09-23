# -*- coding: utf-8 -*-
"""
experiments/measure_block_group_displacements.py
================================================
Phase 0 of the sensitivity curve. NO RENDERS: it reads the checkpoint and nothing else.

Page 10 rotates all six block groups by the SAME ANGLE -- plus/minus 5, 10 and 15 degrees --
and reports that B6 moves the image far more than the others. A rotation by a fixed angle
is not a fixed perturbation: how far the weights actually travel is
||dW||_F / ||W||_F, and that depends on the group's own norm. Until this file exists, the
depth profile on page 10 confounds "this group is more sensitive" with "this group received
a bigger push", and the page says so.

For every group in ArthemyKrea2ModelBlockSurgeonTuner.MODEL_TARGET_MAP and every angle the
bench used, this writes:

  D_fp32    ||dW||_F / ||W_model||_F, the displacement the engine asks for
  D_bf16    the displacement ComfyUI actually writes, (W.float() + dW).to(bfloat16)
  cos       cos(dW_bf16, dW_fp32), the same fidelity check as the v4 gate
  group_norm  ||W_G||_F, the reason the same angle is not the same dose

Conventions are taken from experiments/calibrate_rotations_v4.py -- same engine, same
depth_rank, same TOTAL_NORM -- and the file is a sibling of it, not an edit of it
(pitfall 32).

Output: data/block_group_displacements.csv
Then run: python experiments/sensitivity_curve.py
"""
import os, sys, csv, math, argparse
import torch

COMFY = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
SUITE = os.path.join(COMFY, "custom_nodes", "Arthemy_Krea2_Tuner")
MODEL = r"C:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\krea2_turbo_bf16.safetensors"
REPORT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.insert(0, COMFY)
sys.path.append(SUITE)
sys.path.insert(0, r"C:\Users\aless\Desktop\comfyui-pilot\experiments")
from calibrate_rotations_v2 import StreamingSafetensors
from Arthemy_Krea2_Tuner import Krea2TensorParser, ArthemyKrea2ModelBlockSurgeonTuner
from arthemy_geometry_engine import fast_dual_orthogonal_rotation

ANGLES = [5.0, 10.0, 15.0]          # the bench's low / mid / high, both signs
TOTAL_NORM = 5009.4475              # ||W||_F of the whole model, as in v2, v3 and v4
DEPTH_RANK = 16


def load_block(reader, label):
    idxs = ArthemyKrea2ModelBlockSurgeonTuner.MODEL_TARGET_MAP[label]
    out = {}
    for k in reader.keys():
        idx, _ = Krea2TensorParser.extract_model_block_idx(Krea2TensorParser.clean_key(k))
        if idx is not None and idx in idxs and len(reader.get_shape(k)) >= 2:
            out[k] = reader.get_tensor(k)
    return out


def deltas(tensors, angle):
    out = {}
    for k, w in tensors.items():
        res = fast_dual_orthogonal_rotation(w, structural_x=angle, depth_rank=DEPTH_RANK, layer_name=k)
        if res is None:
            raise RuntimeError(f"the engine returns no rotation for {k}")
        out[k] = (res.A.float() @ res.B.float()).reshape(w.shape)
    return out


def measure(tensors, angle):
    dw = deltas(tensors, angle)
    n32 = sum(float((d ** 2).sum()) for d in dw.values())
    num = dot = 0.0
    for k, w in tensors.items():
        w32 = w.float()
        real = (w32 + dw[k]).to(torch.bfloat16).float() - w32
        num += float((real ** 2).sum())
        dot += float((real * dw[k]).sum())
    return (math.sqrt(n32) / TOTAL_NORM,
            math.sqrt(num) / TOTAL_NORM,
            dot / math.sqrt(num * n32))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=MODEL, help="the checkpoint to read")
    ap.add_argument("--out", default=os.path.join(REPORT, "data", "block_group_displacements.csv"))
    a = ap.parse_args()
    reader = StreamingSafetensors(a.model)
    labels = list(ArthemyKrea2ModelBlockSurgeonTuner.MODEL_TARGET_MAP)
    groups = {}
    for label in labels:
        t = load_block(reader, label)
        if t:
            groups[label] = t
    reader.close()
    if not groups:
        sys.exit("no group matched MODEL_TARGET_MAP -- the parser or the checkpoint changed")

    rows = []
    for label, tensors in groups.items():
        idxs = sorted(ArthemyKrea2ModelBlockSurgeonTuner.MODEL_TARGET_MAP[label])
        gnorm = math.sqrt(sum(float((w.float() ** 2).sum()) for w in tensors.values()))
        for a in ANGLES:
            for sign in (+1, -1):
                d32, dbf, cos = measure(tensors, sign * a)
                rows.append({
                    "group_label": label,
                    "block_indices": " ".join(str(i) for i in idxs),
                    "n_tensors": len(tensors),
                    "group_norm_fro": round(gnorm, 4),
                    "total_model_norm": TOTAL_NORM,
                    "angle_deg": sign * a,
                    "angle_label": {5.0: "low", 10.0: "mid", 15.0: "high"}[a],
                    "D_fp32": d32,
                    "D_bf16": dbf,
                    "cos_bf16_fp32": cos,
                })
                print(f"{label:24s} {sign * a:+6.1f} deg   D_fp32 {d32:.7f}   "
                      f"D_bf16 {dbf:.7f}   cos {cos:.5f}", flush=True)

    out = a.out
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {out}  ({len(rows)} rows, {len(groups)} groups)")


if __name__ == "__main__":
    main()
