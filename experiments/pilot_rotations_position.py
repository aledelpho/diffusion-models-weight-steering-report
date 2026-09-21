# -*- coding: utf-8 -*-
"""
experiments/pilot_rotations_position.py

Join the pilot rotation sweep into one per-block table, and check it against the analysis
that produced it.

The "does it matter where you edit" material is spread over four files and two scripts, and
the one table a reader wants -- per block: how much the image moved, how far the weights
moved, how much of the response reverses with the sign, and how consistent its direction is
across prompts -- exists nowhere. That is rule 7.

Nothing is re-implemented. The symmetric/antisymmetric decomposition and the coherence come
from `analyze_pilot_rotation_directions`, imported, and every norm this script computes is
asserted against `data/pilot_rotation_direction_tests.csv`, which the original run wrote.

    python experiments/pilot_rotations_position.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
sys.path.insert(0, str(HERE))
import analyze_pilot_rotation_directions as apd  # noqa: E402

OUT = DATA / "pilot_rotations_position.csv"
ANGLE = 30.0
TOL = 5e-3


def displacement() -> dict:
    d = pd.read_csv(DATA / "pilot_rotation_displacement.csv")
    d = d[d.angle_deg.abs() == ANGLE]
    return dict(zip(d.block, d.d_model))


def image_movement() -> dict:
    """Mean CLIP distance per block over the 216 rotation cells, prompt averaged first.

    Two traps in one file. `pilot_rotations.csv` holds 270 rows, not 216: 54 of them are a
    DIFFERENT perturbation family (structural_rot_y, tensor_rot_x, tensor_rot_y) and every
    one of them sits on Block_3. A plain groupby therefore mixes another experiment into one
    block and moves it from 0.1171 to 0.1064 without saying so. And the nine reports are
    seven prompts -- tiefling appears three times at different seeds -- so the mean is taken
    per prompt first, because the unit of analysis is the prompt (pitfall 17).
    """
    r = pd.read_csv(DATA / "pilot_rotations.csv")
    rot = r[r.family == "rotX"]
    if len(rot) != 216:
        raise ValueError(f"expected 216 rotation cells, found {len(rot)}")
    per_prompt = rot.groupby(["block", "prompt_id"]).clip_dist.mean()
    return per_prompt.groupby("block").mean().to_dict()


def frozen_norms() -> dict:
    """||S|| and ||A|| per block as the original run wrote them, texture space, raw."""
    out = {}
    for row in csv.DictReader((DATA / "pilot_rotation_direction_tests.csv")
                              .open(encoding="utf-8", newline="")):
        if (row["space"] == "TESSITURA" and row["centering"] == "nessuna (grezza)"
                and float(row["angle"]) == ANGLE and row["test"] == "norme_S_A"):
            out[row["block"]] = (float(row["value_S"]), float(row["value_A"]))
    if len(out) != 6:
        raise ValueError(f"expected 6 frozen norm rows, found {len(out)}")
    return out


def main() -> int:
    # build_spaces returns (meta, texture, palette, texture columns, palette columns),
    # standardised once over all 225 rows. The texture space is the one the decisive test
    # of this sweep runs in.
    meta, TEX, _PAL, cols, _pal_cols = apd.build_spaces()

    M, D = apd.deltas(meta, TEX)
    T_S, T_A, _ = apd.sym_antisym(M, D)

    frozen = frozen_norms()
    disp = displacement()
    moved = image_movement()
    rank = {b: i + 1 for i, b in enumerate(sorted(disp, key=disp.get, reverse=True))}

    rows = []
    for b in apd.BLOCKS:
        nS = float(np.linalg.norm(apd.block_mean_dir(T_S, cols, b, ANGLE)))
        nA = float(np.linalg.norm(apd.block_mean_dir(T_A, cols, b, ANGLE)))
        fS, fA = frozen[b]
        for name, got, want in (("S", nS, fS), ("A", nA, fA)):
            if abs(got - want) > TOL:
                raise ValueError(f"{b}: recomputed ||{name}|| {got:.4f} against {want:.4f} in "
                                 f"pilot_rotation_direction_tests.csv -- the runs disagree")
        coh, n = apd.within_coherence(T_A, cols, b, ANGLE)
        rows.append({
            "block": b,
            "clip_dist_mean_rotation": round(moved[b], 4),
            "d_model_at_30deg": round(disp[b], 5),
            "displacement_rank": rank[b],
            "norm_S_texture_30deg": round(nS, 4),
            "norm_A_texture_30deg": round(nA, 4),
            "antisymmetric_share": round(nA / (nA + nS), 4),
            "within_block_coherence_A": round(coh, 4),
            "n_prompts": n,
        })

    print(f"all 12 norms agree with pilot_rotation_direction_tests.csv to {TOL}")
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"\n{'block':<9}{'CLIP-Dist':>10}{'D_model':>10}{'rank':>6}{'||S||':>8}{'||A||':>8}"
          f"{'share':>8}{'coherence':>11}")
    for r in rows:
        print(f"{r['block']:<9}{r['clip_dist_mean_rotation']:>10.4f}"
              f"{r['d_model_at_30deg']:>10.5f}{r['displacement_rank']:>6}"
              f"{r['norm_S_texture_30deg']:>8.2f}{r['norm_A_texture_30deg']:>8.2f}"
              f"{r['antisymmetric_share']:>8.2f}{r['within_block_coherence_A']:>11.2f}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
