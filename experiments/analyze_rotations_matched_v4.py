# -*- coding: utf-8 -*-
"""
experiments/analyze_rotations_matched_v4.py
===========================================
Analisi confermativa di rotations_matched_v4, come fissata in
docs/prereg_rotations_block1_vs_block6_emendamento_v4.md (e v3) (formula del §1 e criterio del §4 di
docs/prereg_rotations_block1_vs_block6.md, invariati).

Congelato per sha256 e per copia PRIMA che le feature v3 esistano. Non modificare: se una modifica
e' inevitabile, vale la procedura del pitfall 32.

Input:  data/rotations_matched_v4_features.csv  (una riga per PNG, chiave `file`, style + palette)
        data/rotations_matched_v4_manifest.csv
        data/rotations_matched_v4_quality_gate.csv
Output: data/rotations_matched_v4_results.csv          (una riga per spazio)
        data/rotations_matched_v4_prompt_scores.csv    (V(p) e V_scr(p) per prompt e spazio)
        data/rotations_matched_v4_gate_by_condition.csv

Solo i 10 prompt S01..S10 entrano. Le righe P01/P02 (probe aggiunti dopo il congelamento del
disegno) sono escluse qui, anche dalla standardizzazione.
"""

import os
import sys
import hashlib
import itertools
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
DATA = os.path.join(ROOT, "data")

PROMPTS = ["S01_oil", "S02_linocut", "S03_cyberpunk", "S04_gouache", "S05_pencil",
           "S06_pastel", "S07_comic", "S08_papercraft", "S09_fresco", "S10_synthwave"]
SHA1 = {"S01_oil": "6de4189f5e", "S02_linocut": "e20e86ac75", "S03_cyberpunk": "6ab02b69aa",
        "S04_gouache": "6335032007", "S05_pencil": "9a68323a39", "S06_pastel": "61861c7677",
        "S07_comic": "69f4e68eba", "S08_papercraft": "17e466c859", "S09_fresco": "9e81add78f",
        "S10_synthwave": "25147e923b"}
SEEDS = [42, 1337, 4242145]
TAGS = ["baseline", "B1_pos", "B1_neg", "B6_pos", "B6_neg", "scrA_pos", "scrA_neg", "scrB_pos", "scrB_neg"]

PRIMARY = ("Texture", ["glcm_contrast", "glcm_homogeneity", "lbp_entropy"])
SECONDARY = [
    ("Linework", ["stroke_width_cv", "edge_density", "contour_mean_length_px"]),
    ("Shadow", ["crosshatch_entropy_mean", "crosshatch_entropy_p90"]),
    ("Palette", ["paper_L", "ink_L", "sw1_L", "chroma_spread", "tonal_range"]),
]
# L'emendamento scrive "Holm su quattro" pur escludendo Frequency: si applica m = 4 come scritto,
# che e' la scelta conservativa.
HOLM_M = 4
ALPHA = 0.05
DEGRADED_FAIL_MAX = 3  # piu' di 3 su 30 in una condizione -> "regime degradato"


def cos(u, v):
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu < 1e-12 or nv < 1e-12:
        raise ValueError("vettore nullo in un coseno: la direzione non e' definita")
    return float(u @ v / (nu * nv))


def sign_flip(v):
    v = np.asarray(v, float)
    n = len(v)
    obs = float(v.mean())
    perm = np.array([np.mean(np.array(s) * v) for s in itertools.product([1, -1], repeat=n)])
    p = float(np.mean(np.abs(perm) >= abs(obs) - 1e-12))
    return obs, p, 2.0 / 2 ** n


def load():
    man = pd.read_csv(os.path.join(DATA, "rotations_matched_v4_manifest.csv"))
    feat = pd.read_csv(os.path.join(DATA, "rotations_matched_v4_features.csv"))
    for df, name in ((man, "manifest"), (feat, "features")):
        if df["file"].duplicated().any():
            raise ValueError(f"{name}: file duplicati")
    man = man[man.prompt_id.isin(PROMPTS)].set_index("file")
    feat = feat.set_index("file")
    missing = sorted(set(man.index) - set(feat.index))
    if missing:
        raise ValueError(f"{len(missing)} immagini del manifest senza feature, es. {missing[:3]}")
    df = man[["prompt_id", "prompt_sha1", "seed", "tag"]].join(feat, how="left", rsuffix="_feat")
    # copertura esatta: 10 x 3 x 9
    if len(df) != 270:
        raise ValueError(f"attese 270 righe, trovate {len(df)}")
    got = set(zip(df.prompt_id, df.seed, df.tag))
    want = set(itertools.product(PROMPTS, SEEDS, TAGS))
    if got != want:
        raise ValueError(f"celle mancanti {sorted(want - got)[:5]} / in piu' {sorted(got - want)[:5]}")
    bad = df[df.prompt_id.map(SHA1) != df.prompt_sha1.astype(str)]
    if len(bad):
        raise ValueError(f"sha1 del prompt discordante su {len(bad)} righe")
    return df


def antisym(Z, df, prompt, arm):
    """A_arm(p): media sui 3 seed di (f(+) - f(-)) / 2, feature z-standardizzate. La baseline si elide."""
    out = []
    for s in SEEDS:
        pos = Z[(df.prompt_id == prompt) & (df.seed == s) & (df.tag == f"{arm}_pos")]
        neg = Z[(df.prompt_id == prompt) & (df.seed == s) & (df.tag == f"{arm}_neg")]
        if len(pos) != 1 or len(neg) != 1:
            raise ValueError(f"{prompt} s{s} {arm}: {len(pos)} pos, {len(neg)} neg")
        out.append((pos.values[0] - neg.values[0]) / 2.0)
    return np.mean(out, axis=0)


def loo_advantage(A_x, A_y):
    """V(p) del §1: vantaggio stesso-blocco leave-one-out, simmetrizzato, per ciascun prompt."""
    V, coh_x, coh_y = [], [], []
    for i, p in enumerate(PROMPTS):
        others = [q for q in PROMPTS if q != p]
        cx = np.mean([A_x[q] for q in others], axis=0)
        cy = np.mean([A_y[q] for q in others], axis=0)
        v = 0.5 * ((cos(A_x[p], cx) - cos(A_x[p], cy)) + (cos(A_y[p], cy) - cos(A_y[p], cx)))
        V.append(v)
        coh_x.append(cos(A_x[p], cx))
        coh_y.append(cos(A_y[p], cy))
    return np.array(V), np.array(coh_x), np.array(coh_y)


def holm(ps, m):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * ps[i]))
        adj[i] = running
    return adj


def analyse_space(df, name, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"{name}: feature mancanti {missing}")
    X = df[cols].astype(float)
    if X.isna().any().any():
        raise ValueError(f"{name}: NaN nelle feature {X.columns[X.isna().any()].tolist()}")
    sd = X.std(ddof=0)
    if (sd < 1e-12).any():
        raise ValueError(f"{name}: feature costanti {sd[sd < 1e-12].index.tolist()}")
    Z = (X - X.mean()) / sd  # una sola standardizzazione, sulle 270 immagini
    A = {arm: {p: antisym(Z, df, p, arm) for p in PROMPTS} for arm in ("B1", "B6", "scrA", "scrB")}
    V, coh1, coh6 = loo_advantage(A["B1"], A["B6"])
    Vs, cohA, cohB = loo_advantage(A["scrA"], A["scrB"])
    if np.allclose(V, Vs):
        raise ValueError(f"{name}: V e V_scramble identiche su tutti i prompt (pitfall 69)")
    v_mean, p, floor = sign_flip(V)
    vs_mean, ps, _ = sign_flip(Vs)
    d_mean, pd_, _ = sign_flip(V - Vs)
    per_prompt = pd.DataFrame({"space": name, "prompt_id": PROMPTS, "V": V, "V_scr": Vs, "V_minus_V_scr": V - Vs,
                               "coh_B1": coh1, "coh_B6": coh6, "coh_scrA": cohA, "coh_scrB": cohB,
                               "norm_A_B1": [np.linalg.norm(A["B1"][q]) for q in PROMPTS],
                               "norm_A_B6": [np.linalg.norm(A["B6"][q]) for q in PROMPTS],
                               "norm_A_scrA": [np.linalg.norm(A["scrA"][q]) for q in PROMPTS],
                               "norm_A_scrB": [np.linalg.norm(A["scrB"][q]) for q in PROMPTS]})
    row = {"space": name, "n_features": len(cols), "features": ";".join(cols),
           "V_mean": v_mean, "p_signflip": p, "floor": floor, "n_prompts_V_pos": int((V > 0).sum()),
           "V_scr_mean": vs_mean, "p_scr": ps,
           "V_minus_V_scr_mean": d_mean, "p_V_minus_V_scr_descriptive": pd_,
           "coh_B1_mean": coh1.mean(), "coh_B6_mean": coh6.mean(),
           "coh_scrA_mean": cohA.mean(), "coh_scrB_mean": cohB.mean()}
    return row, per_prompt


def main():
    df = load()
    rows, per = [], []
    for kind, (name, cols) in [("primary", PRIMARY)] + [("secondary", s) for s in SECONDARY]:
        r, pp = analyse_space(df, name, cols)
        r["type"] = kind
        rows.append(r)
        per.append(pp)
    res = pd.DataFrame(rows)
    sec = res.type == "secondary"
    res["p_holm"] = np.nan
    res.loc[sec, "p_holm"] = holm(res.loc[sec, "p_signflip"].values, HOLM_M)
    prim = res.type == "primary"
    res["criterion_V_pos_p"] = (res.V_mean > 0) & (res.p_signflip < ALPHA)
    res.loc[sec, "criterion_V_pos_p"] = (res.loc[sec, "V_mean"] > 0) & (res.loc[sec, "p_holm"] < ALPHA)
    res["criterion_V_gt_V_scr"] = res.V_mean > res.V_scr_mean
    res["confirmed"] = res.criterion_V_pos_p & res.criterion_V_gt_V_scr

    # cancello di qualita' per condizione (solo S01..S10)
    gate = pd.read_csv(os.path.join(DATA, "rotations_matched_v4_quality_gate.csv"))
    gate = gate[gate.prompt_id.isin(PROMPTS)]
    g = gate.groupby("tag").agg(n=("passed", "size"), n_fail=("passed", lambda x: int((~x.astype(bool)).sum())))
    g["degraded"] = g.n_fail > DEGRADED_FAIL_MAX
    if (g.n != 30).any():
        raise ValueError(f"cancello: attese 30 immagini per condizione\n{g}")
    res["regime_degradato"] = bool(g.degraded.any())
    res["degraded_conditions"] = ";".join(g.index[g.degraded])

    res.to_csv(os.path.join(DATA, "rotations_matched_v4_results.csv"), index=False)
    pd.concat(per).to_csv(os.path.join(DATA, "rotations_matched_v4_prompt_scores.csv"), index=False)
    g.to_csv(os.path.join(DATA, "rotations_matched_v4_gate_by_condition.csv"))

    pd.set_option("display.width", 220)
    print(g.to_string())
    print(res[["space", "type", "V_mean", "p_signflip", "p_holm", "n_prompts_V_pos", "V_scr_mean",
               "V_minus_V_scr_mean", "coh_B1_mean", "coh_B6_mean", "confirmed", "regime_degradato"]].to_string())
    print("sha256 di questo script:", hashlib.sha256(open(__file__, "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
