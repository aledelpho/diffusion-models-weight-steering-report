# -*- coding: utf-8 -*-
"""
experiments/calibrate_rotations_v4.py
=====================================
Fase 0 di rotations_matched_v4 (docs/prereg_rotations_block1_vs_block6_emendamento_v4.md).

Per ogni dose della scala {0.0035, 0.0025, 0.0018}:
1. risolve per bisezione l'angolo di Block_1 (blocchi 0-4, 40 tensori 2D) e di Block_6 (24-27, 32)
   tale che D_fp32 = ||dW||_F / ||W||_F coincida con il target entro 1e-7; se non converge, solleva;
2. per ciascuno degli 8 bracci (B1, B6, scrA, scrB x pos/neg) ricostruisce il peso come lo scrive
   ComfyUI: (W.float() + dW).to(bfloat16) (comfy/float.py: per bf16 cast al piu' vicino), e misura
   D_bf16 = ||W_bf16 - W||_F / ||W||_F e cos(dW_bf16, dW_fp32) sui tensori del blocco concatenati;
3. cancello sulla dose: |D_bf16 / D_target - 1| <= 2% e cos >= 0.99 su tutti gli 8 bracci.

La rotazione e' quella del motore del nodo (arthemy_geometry_engine.fast_dual_orthogonal_rotation,
depth_rank = 16), con i segni scramble di SCRAMBLE_MAP_A / _B letti dal nodo.
Output: data/matched_rotation_calibration_v4.json
"""
import os, sys, re, json, math
import torch

COMFY = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
SUITE = os.path.join(COMFY, "custom_nodes", "Arthemy_Krea2_Tuner")
MODEL = r"C:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\krea2_turbo_bf16.safetensors"
REPORT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.insert(0, COMFY)
sys.path.append(SUITE)
sys.path.insert(0, r"C:\Users\aless\Desktop\comfyui-pilot\experiments")
from calibrate_rotations_v2 import StreamingSafetensors
from Arthemy_Krea2_Tuner import Krea2TensorParser, ArthemyKrea2ModelBlockSurgeonTuner, ArthemyKrea2ModelScrambleRotator
from arthemy_geometry_engine import fast_dual_orthogonal_rotation

DOSES = [0.0035, 0.0025, 0.0018]
TOTAL_NORM = 5009.4475  # ||W||_F del modello intero, come in v2 e v3
TOL = 1e-7


def load_block(reader, label):
    idxs = ArthemyKrea2ModelBlockSurgeonTuner.MODEL_TARGET_MAP[label]
    out = {}
    for k in reader.keys():
        idx, _ = Krea2TensorParser.extract_model_block_idx(Krea2TensorParser.clean_key(k))
        if idx is not None and idx in idxs and len(reader.get_shape(k)) >= 2:
            out[k] = reader.get_tensor(k)
    return out


def deltas(tensors, angle, signs=None):
    """dW fp32 per tensore, come il motore del nodo (dW = A @ B)"""
    out = {}
    for k, w in tensors.items():
        s = 1.0 if signs is None else float(signs[Krea2TensorParser.clean_key(k)])
        res = fast_dual_orthogonal_rotation(w, structural_x=angle * s, depth_rank=16, layer_name=k)
        if res is None:
            raise RuntimeError(f"il motore non restituisce una rotazione per {k}")
        out[k] = (res.A.float() @ res.B.float()).reshape(w.shape)
    return out


def d_fp32(tensors, angle, signs=None):
    return math.sqrt(sum(float((d ** 2).sum()) for d in deltas(tensors, angle, signs).values())) / TOTAL_NORM


def bf16_check(tensors, angle, signs=None):
    dw = deltas(tensors, angle, signs)
    num = dot = n32 = 0.0
    for k, w in tensors.items():
        w32 = w.float()
        real = (w32 + dw[k]).to(torch.bfloat16).float() - w32
        num += float((real ** 2).sum())
        n32 += float((dw[k] ** 2).sum())
        dot += float((real * dw[k]).sum())
    return math.sqrt(num) / TOTAL_NORM, dot / math.sqrt(num * n32)


def bisect(tensors, target, lo=0.01, hi=10.0):
    flo, fhi = d_fp32(tensors, lo) - target, d_fp32(tensors, hi) - target
    if flo * fhi > 0:
        raise RuntimeError(f"target {target} non racchiuso fra {lo} e {hi} gradi")
    for _ in range(80):
        mid = (lo + hi) / 2
        fm = d_fp32(tensors, mid) - target
        if abs(fm) <= TOL:
            return mid, fm + target
        if fm * flo < 0:
            hi = mid
        else:
            lo, flo = mid, fm
    raise RuntimeError(f"bisezione non convergente per target {target}: ultimo scarto {fm:.3e}")


def main():
    reader = StreamingSafetensors(MODEL)
    b1, b6 = load_block(reader, "Block_1 (All 0-4)"), load_block(reader, "Block_6 (All 24-27)")
    reader.close()
    if (len(b1), len(b6)) != (40, 32):
        raise RuntimeError(f"tensori: Block_1 {len(b1)} (attesi 40), Block_6 {len(b6)} (attesi 32)")
    sA, sB = ArthemyKrea2ModelScrambleRotator.SCRAMBLE_MAP_A, ArthemyKrea2ModelScrambleRotator.SCRAMBLE_MAP_B
    for name, tens, sm in (("A", b1, sA), ("B", b6, sB)):
        keys = {Krea2TensorParser.clean_key(k) for k in tens}
        if keys != set(sm):
            raise RuntimeError(f"SCRAMBLE_MAP_{name} non copre esattamente i tensori del blocco: {sorted(keys ^ set(sm))[:4]}")
    out = {"model_file": os.path.basename(MODEL), "total_model_norm": TOTAL_NORM, "rounding": "bf16 round-to-nearest",
           "gate": "|D_bf16/D_target-1| <= 0.02 and cos(dW_bf16, dW_fp32) >= 0.99 on all 8 arms", "levels": {}}
    for D in DOSES:
        th1, d1 = bisect(b1, D)
        th6, d6 = bisect(b6, D)
        lvl = {"target_D": D, "theta_B1_deg": th1, "theta_B6_deg": th6, "D_fp32_B1": d1, "D_fp32_B6": d6, "arms": {}}
        ok = True
        for arm, tens, th, sg in (("B1", b1, th1, None), ("B6", b6, th6, None), ("scrA", b1, th1, sA), ("scrB", b6, th6, sB)):
            for sign in (+1, -1):
                db, c = bf16_check(tens, sign * th, sg)
                dfp = d_fp32(tens, sign * th, sg)
                passed = abs(db / D - 1) <= 0.02 and c >= 0.99
                ok &= passed
                lvl["arms"][f"{arm}_{'pos' if sign > 0 else 'neg'}"] = {
                    "angle_deg": sign * th, "D_fp32": dfp, "D_bf16": db, "ratio_bf16_to_target": db / D,
                    "cos_bf16_fp32": c, "passed": passed}
                print(f"D={D} {arm:4s} {'+' if sign > 0 else '-'} angle {sign * th:+.6f}  D_fp32 {dfp:.7f}  "
                      f"D_bf16 {db:.7f} ({db / D - 1:+.2%})  cos {c:.5f}  {'OK' if passed else 'FAIL'}", flush=True)
        lvl["dose_gate_passed"] = ok
        out["levels"][f"d{D:.4f}".replace("0.", "")] = lvl
    for d in (os.path.join(REPORT, "data"), r"C:\Users\aless\Desktop\comfyui-pilot\data"):
        with open(os.path.join(d, "matched_rotation_calibration_v4.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
    print("dosi che passano il cancello bf16:", [k for k, v in out["levels"].items() if v["dose_gate_passed"]])


if __name__ == "__main__":
    main()
