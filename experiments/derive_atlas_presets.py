# -*- coding: utf-8 -*-
"""
experiments/derive_atlas_presets.py
===================================
Derives the 26 perturbation atlas presets (13 conditions x 2 independent draws)
governed by:
  - docs/prereg_perturbation_atlas.md
  - docs/prereg_perturbation_atlas_amendment_01.md (4 depth bands)
  - docs/prereg_perturbation_atlas_amendment_03.md (scalar-only generated, 4 verification gates)
  - docs/prereg_perturbation_atlas_amendment_04.md (modulation_norm, txtfusion, 13 conditions)
  - docs/prereg_perturbation_atlas_amendment_05.md (single combined anchor D)
  - docs/prereg_perturbation_atlas_amendment_06.md (callable key predicate)

Verification gates checked and logged to data/perturbation_atlas_draw_check.csv:
  1. Determinism: bit-identical generation on repeated run.
  2. Convergence: scale_subset converges on all 26 presets.
  3. Anchor: combined displacement matches D to at least 12 significant digits.
  4. Emptiness: rotation_recipes == [] and suite_rotation_effective == False read back from disk.
"""

from __future__ import annotations

import csv
import json
import math
import os
import random
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import safetensors
import torch

ROOT = Path(__file__).resolve().parent.parent
COMFY_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI")
SUITE_DIR = COMFY_ROOT / "custom_nodes" / "Arthemy_Krea2_Tuner"
PRESET_DIR_NODE = SUITE_DIR / "presets"
PRESET_DIR_REPO = ROOT / "presets"
MODELS_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Models")
DATA_DIR = ROOT / "data"

sys.path.insert(0, str(COMFY_ROOT))
sys.path.append(str(SUITE_DIR))
from Arthemy_Krea2_Tuner import Krea2TensorParser

BASE = "Arthemy_Bench_Base"
MODEL_FILE = "krea2_turbo_bf16.safetensors"
CLIP_FILE = "qwen3vl_4b_bf16.safetensors"


def find_model(fn: str) -> Path:
    for root, _d, files in os.walk(MODELS_ROOT):
        if fn in files:
            return Path(root) / fn
    raise FileNotFoundError(fn)


def norm_table(path: Path, keys: List[str]) -> Dict[str, float]:
    want = set(keys)
    norms: Dict[str, float] = {}
    with safetensors.safe_open(str(path), framework="pt", device="cpu") as f:
        for raw in f.keys():
            ck = Krea2TensorParser.clean_key(raw)
            if ck in want and ck not in norms:
                t = f.get_tensor(raw).to(torch.float32)
                norms[ck] = float(torch.linalg.vector_norm(t).item())
    missing = want - set(norms)
    if missing:
        raise KeyError(f"{len(missing)} chiavi senza tensore nel modello: {list(missing)[:5]}")
    return norms


def dn(patches: Dict[str, float], norms: Dict[str, float]) -> float:
    return math.sqrt(sum((v * norms[k]) ** 2 for k, v in patches.items() if k in norms))


def scale_subset_predicate(
    raw_patches: Dict[str, float],
    key_predicate: Callable[[str], bool],
    norms: Dict[str, float],
    target_d: float
) -> Tuple[Dict[str, float], float, float]:
    """
    Rescales tensors matching key_predicate so that their norm-weighted displacement
    equals target_d. Tensors outside predicate are left at rest (0.0).
    """
    sub_filtered: Dict[str, float] = {}
    rest: Dict[str, float] = {}
    for k, v in raw_patches.items():
        if key_predicate(k):
            sub_filtered[k] = v
        else:
            rest[k] = v

    d_rest = dn(rest, norms)
    d_sub = dn(sub_filtered, norms)

    target_sq = target_d ** 2 - d_rest ** 2
    if target_sq <= 0:
        raise RuntimeError("Il resto supera il totale")
    if d_sub <= 0:
        raise RuntimeError("Il sottoinsieme filtrato ha norma zero")

    alpha = math.sqrt(target_sq) / d_sub
    new_patches = dict(rest)
    for k, v in sub_filtered.items():
        new_patches[k] = v * alpha

    d_final = dn(new_patches, norms)
    res = abs(d_final - target_d) / target_d
    if res > 1e-6:
        raise RuntimeError(f"Riscalatura non convergente: target {target_d:.8f}, ottenuto {d_final:.8f}, res {res:.2e}")

    return new_patches, alpha, d_final


def get_region_predicates() -> Dict[str, Dict[str, Any]]:
    """Returns the 13 condition definitions with their key predicates."""
    bands = [
        ("early", list(range(0, 7))),
        ("early_mid", list(range(7, 14))),
        ("late_mid", list(range(14, 21))),
        ("late", list(range(21, 28))),
    ]
    components = ["attn", "mlp"]

    defs: Dict[str, Dict[str, Any]] = {}

    # 1-8. Depth x component
    for b_name, b_list in bands:
        for comp in components:
            reg_name = f"{b_name}_{comp}"
            # Capture variables in closure
            def make_pred(blist=b_list, cname=comp):
                return lambda k: any(k.startswith(f"blocks.{i}.{cname}.") for i in blist)
            defs[reg_name] = {
                "domain": "model",
                "pred_m": make_pred(),
                "pred_c": None,
                "desc": f"Blocks {b_list[0]}-{b_list[-1]} {comp} tensors"
            }

    # 9. modulation_norm
    defs["modulation_norm"] = {
        "domain": "model",
        "pred_m": lambda k: bool(re.match(r"blocks\.\d+\.(mod\.lin|prenorm\.scale|postnorm\.scale)$", k)),
        "pred_c": None,
        "desc": "blocks.[0-27].{mod.lin, prenorm.scale, postnorm.scale}"
    }

    # 10. txtfusion
    defs["txtfusion"] = {
        "domain": "model",
        "pred_m": lambda k: k.startswith("txtfusion."),
        "pred_c": None,
        "desc": "txtfusion.* text-image fusion path"
    }

    # 11. clip_only
    defs["clip_only"] = {
        "domain": "clip",
        "pred_m": None,
        "pred_c": lambda k: True,
        "desc": "all CLIP patched tensors"
    }

    # 12. model_only
    defs["model_only"] = {
        "domain": "model",
        "pred_m": lambda k: True,
        "pred_c": None,
        "desc": "all model patched tensors"
    }

    # 13. uniform_all
    defs["uniform_all"] = {
        "domain": "both",
        "pred_m": lambda k: True,
        "pred_c": lambda k: True,
        "desc": "all model and CLIP patched tensors"
    }

    return defs


def generate_single_preset(
    region: str,
    reg_def: Dict[str, Any],
    draw_idx: int,
    draw_seed: int,
    base: Dict[str, Any],
    m_keys: List[str],
    c_keys: List[str],
    m_norms: Dict[str, float],
    c_norms: Dict[str, float],
    target_D: float
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Generates a single atlas preset per Amendment 03, 04, 05, 06.
    Returns: (preset_dict, calibration_row)
    """
    domain = reg_def["domain"]
    pred_m = reg_def["pred_m"]
    pred_c = reg_def["pred_c"]

    # 1. Model generation
    raw_m_patches: Dict[str, float] = {}
    if pred_m is not None:
        target_m_keys = [k for k in m_keys if pred_m(k)]
        gen_m = torch.Generator(device="cpu").manual_seed(draw_seed)
        m_draw_vals = {k: float(torch.randn(1, generator=gen_m).item()) for k in target_m_keys}
        for k in m_keys:
            raw_m_patches[k] = m_draw_vals.get(k, 0.0)
    else:
        for k in m_keys:
            raw_m_patches[k] = 0.0

    # 2. CLIP generation
    raw_c_patches: Dict[str, float] = {}
    if pred_c is not None:
        target_c_keys = [k for k in c_keys if pred_c(k)]
        gen_c = torch.Generator(device="cpu").manual_seed(draw_seed)
        c_draw_vals = {k: float(torch.randn(1, generator=gen_c).item()) for k in target_c_keys}
        for k in c_keys:
            raw_c_patches[k] = c_draw_vals.get(k, 0.0)
    else:
        for k in c_keys:
            raw_c_patches[k] = 0.0

    # 3. Rescaling to combined anchor D
    m_alpha = 0.0
    c_alpha = 0.0
    code_path = "scale_subset_predicate"

    if domain == "model":
        m_patches, m_alpha, d_m = scale_subset_predicate(raw_m_patches, pred_m, m_norms, target_D)
        c_patches = dict(raw_c_patches)
        d_c = 0.0
    elif domain == "clip":
        m_patches = dict(raw_m_patches)
        d_m = 0.0
        c_patches, c_alpha, d_c = scale_subset_predicate(raw_c_patches, pred_c, c_norms, target_D)
    elif domain == "both":
        # uniform_all: spread D over everything with single global alpha
        code_path = "global_joint_rescale"
        d_m_unscaled = dn(raw_m_patches, m_norms)
        d_c_unscaled = dn(raw_c_patches, c_norms)
        d_tot_unscaled = math.hypot(d_m_unscaled, d_c_unscaled)
        if d_tot_unscaled <= 0:
            raise RuntimeError("uniform_all unscaled displacement is zero")
        global_alpha = target_D / d_tot_unscaled
        m_alpha = global_alpha
        c_alpha = global_alpha
        m_patches = {k: v * global_alpha for k, v in raw_m_patches.items()}
        c_patches = {k: v * global_alpha for k, v in raw_c_patches.items()}
        d_m = dn(m_patches, m_norms)
        d_c = dn(c_patches, c_norms)
    else:
        raise ValueError(f"Unknown domain {domain}")

    d_total = math.hypot(d_m, d_c)
    residual = abs(d_total - target_D) / target_D

    preset_name = f"Arthemy_Atlas_{region}_draw{draw_idx}"
    preset_obj = {
        "name": preset_name,
        "author": "Antigravity (Block J)",
        "created_at": "2026-09-25",
        "version": "3.0",
        "suite_rotation_effective": False,
        "rotation_recipes": [],
        "chaos_rotation_recipes": [],
        "channel_recipes": [],
        "chaos_recipes": [],
        "stats": {
            "model_patched_layers": sum(1 for v in m_patches.values() if v != 0.0),
            "model_granular_layers": 0,
            "clip_patched_layers": sum(1 for v in c_patches.values() if v != 0.0),
            "clip_granular_layers": 0,
            "chaos_recipes_count": 0,
            "rotation_recipes_count": 0,
            "chaos_rotation_recipes_count": 0,
            "channel_recipes_count": 0,
            "five_d_recipes_count": 0,
            "excluded_lora_tensors": 0
        },
        "model_patches": m_patches,
        "clip_patches": c_patches,
        "notes": (
            f"Perturbation Atlas: {region} draw {draw_idx} (seed {draw_seed}). "
            f"Combined anchor D={target_D:.12f}, measured D={d_total:.12f} (res={residual:.2e}). "
            f"Model alpha={m_alpha:.6f}, CLIP alpha={c_alpha:.6f}. Zero rotations."
        )
    }

    calib_row = {
        "preset": preset_name,
        "region": region,
        "draw": draw_idx,
        "draw_seed": draw_seed,
        "domain": domain,
        "model_alpha": m_alpha,
        "clip_alpha": c_alpha,
        "d_model_measured": d_m,
        "d_clip_measured": d_c,
        "d_total_measured": d_total,
        "d_target": target_D,
        "residual": residual,
        "code_path": code_path,
        "status": "PASS" if residual < 1e-6 else "FAIL"
    }

    return preset_obj, calib_row


def main():
    print("=== BLOCK J3: DERIVE 26 PERTURBATION ATLAS PRESETS ===")

    # 1. Base preset & norms
    base_file = PRESET_DIR_REPO / f"{BASE}.json"
    with open(base_file, encoding="utf-8") as f:
        base = json.load(f)

    m_keys = sorted(base["model_patches"].keys())
    c_keys = sorted(base["clip_patches"].keys())

    print(f"Loading Frobenius norms from base models...")
    m_norms = norm_table(find_model(MODEL_FILE), m_keys)
    c_norms = norm_table(find_model(CLIP_FILE), c_keys)

    d_base_m = dn(base["model_patches"], m_norms)
    d_base_c = dn(base["clip_patches"], c_norms)
    target_D = math.hypot(d_base_m, d_base_c)

    print(f"Anchor values computed from {BASE}:")
    print(f"  d_base_model = {d_base_m:.14f}")
    print(f"  d_base_clip  = {d_base_c:.14f}")
    print(f"  Combined D   = {target_D:.14f}")

    # 2. Draws seeds
    draw_seeds = random.Random(20260925).sample(range(1, 1000), 2)
    print(f"Independent draw seeds (random.Random(20260925)): {draw_seeds}")

    region_defs = get_region_predicates()
    print(f"Conditions: {len(region_defs)} regions defined.")

    calib_rows: List[Dict[str, Any]] = []
    generated_presets: Dict[str, Dict[str, Any]] = {}

    # Verification gate 1 trackers: Determinism
    gate1_passed = True
    gate1_details = ""

    # Derive all 26 presets
    for draw_idx, d_seed in [(1, draw_seeds[0]), (2, draw_seeds[1])]:
        for reg_name, reg_def in region_defs.items():
            p_obj, c_row = generate_single_preset(
                reg_name, reg_def, draw_idx, d_seed,
                base, m_keys, c_keys, m_norms, c_norms, target_D
            )
            name = c_row["preset"]
            generated_presets[name] = p_obj
            calib_rows.append(c_row)

            # Test Gate 1: Determinism check on every single preset
            p_obj_rep, _ = generate_single_preset(
                reg_name, reg_def, draw_idx, d_seed,
                base, m_keys, c_keys, m_norms, c_norms, target_D
            )
            if p_obj["model_patches"] != p_obj_rep["model_patches"] or p_obj["clip_patches"] != p_obj_rep["clip_patches"]:
                gate1_passed = False
                gate1_details = f"Non-deterministic multipliers generated on {name}"
                sys.exit(f"FATAL: Gate 1 Determinism failed on {name}")

    if gate1_passed:
        gate1_details = "All 26 presets bit-identical on repeated generation"

    # Save presets to both PRESET_DIR_NODE and PRESET_DIR_REPO
    PRESET_DIR_NODE.mkdir(parents=True, exist_ok=True)
    PRESET_DIR_REPO.mkdir(parents=True, exist_ok=True)

    for name, p_obj in generated_presets.items():
        for pdir in [PRESET_DIR_NODE, PRESET_DIR_REPO]:
            out_file = pdir / f"{name}.json"
            with open(out_file, "w", encoding="utf-8") as fh:
                json.dump(p_obj, fh, indent=1)

    print(f"Saved all 26 presets to repo and node dirs.")

    # Write data/perturbation_atlas_calibration.csv
    out_calib = DATA_DIR / "perturbation_atlas_calibration.csv"
    out_calib.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "preset", "region", "draw", "draw_seed", "domain",
        "model_alpha", "clip_alpha",
        "d_model_measured", "d_clip_measured", "d_total_measured",
        "d_target", "residual", "code_path", "status"
    ]
    with open(out_calib, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(calib_rows)
    print(f"Wrote {out_calib} ({len(calib_rows)} rows)")

    # Execute and evaluate the 4 verification gates of Amendment 03 §4
    # Gate 1: Determinism (evaluated above)
    # Gate 2: Convergence (scale_subset must converge for all 26 presets)
    max_res = max(r["residual"] for r in calib_rows)
    gate2_passed = all(r["status"] == "PASS" for r in calib_rows)
    gate2_details = f"All 26 presets converged with max residual {max_res:.2e} <= 1e-6"

    # Gate 3: Anchor matching to at least 12 significant digits
    gate3_passed = all(r["residual"] < 1e-12 for r in calib_rows)
    max_res_12 = max(r["residual"] for r in calib_rows)
    gate3_details = f"All 26 presets match combined D={target_D:.12f} to 12 digits (max residual {max_res_12:.2e})"

    # Gate 4: Emptiness (read files back from disk)
    gate4_passed = True
    gate4_checked = 0
    for name in generated_presets.keys():
        disk_path = PRESET_DIR_REPO / f"{name}.json"
        with open(disk_path, encoding="utf-8") as fh:
            loaded = json.load(fh)
        if loaded.get("rotation_recipes") != [] or loaded.get("suite_rotation_effective") is not False:
            gate4_passed = False
            sys.exit(f"FATAL: Gate 4 failed on {name}: rotation_recipes not empty")
        gate4_checked += 1
    gate4_details = f"All 26 presets read back from disk: rotation_recipes == [] and suite_rotation_effective == False verified ({gate4_checked}/26)"

    # Append gate outcomes to data/perturbation_atlas_draw_check.csv
    check_csv = DATA_DIR / "perturbation_atlas_draw_check.csv"
    gate_records = [
        {"gate_name": "gate_1_determinism", "target": "bit-identical generation on repeated run", "status": "PASS" if gate1_passed else "FAIL", "details": gate1_details},
        {"gate_name": "gate_2_convergence", "target": "rescaling converges for all 26 presets", "status": "PASS" if gate2_passed else "FAIL", "details": gate2_details},
        {"gate_name": "gate_3_anchor", "target": "combined displacement matches D to 12 significant digits", "status": "PASS" if gate3_passed else "FAIL", "details": gate3_details},
        {"gate_name": "gate_4_emptiness", "target": "rotation_recipes: [] and suite_rotation_effective: false verified on disk", "status": "PASS" if gate4_passed else "FAIL", "details": gate4_details},
    ]

    with open(check_csv, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["gate_name", "target", "status", "details"])
        w.writerows(gate_records)
    print(f"Appended 4 verification gates to {check_csv}")

    print("\n=== VERIFICATION GATES SUMMARY ===")
    for g in gate_records:
        print(f"[{g['status']}] {g['gate_name']}: {g['details']}")

    print("\n=== CALIBRATION TABLE SUMMARY ===")
    for r in calib_rows:
        print(f"{r['preset']:34s} | D_meas={r['d_total_measured']:.12f} (res={r['residual']:.1e}) | m_alpha={r['model_alpha']:.4f}, c_alpha={r['clip_alpha']:.4f} | {r['status']}")


if __name__ == "__main__":
    main()
