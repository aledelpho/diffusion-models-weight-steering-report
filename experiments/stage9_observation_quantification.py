# -*- coding: utf-8 -*-
"""
experiments/stage9_observation_quantification.py

Mette un numero sulle osservazioni dirette registrate in docs/observations_stage9.md.

NON E' UNA CONFERMA. Le osservazioni sono nate guardando questi render e vengono
qui misurate sugli stessi render: e' il passaggio "il mio occhio diceva 95%, la
misura dice 96.7%" del prereg dell'asse di hatching, cioe' quantificazione di una
scoperta, non sua conferma. La conferma richiede un corpus nuovo.

Tutte le quantita' usate erano gia' estratte: nessun render nuovo, nessuna GPU.

Unita' di analisi: il prompt. Delta = condizione - baseline allo stesso prompt e
allo stesso seed, mediato sui seed e poi sui prompt (pitfall 17). Si riporta anche
la concordanza per prompt e per coppia di immagini, che e' il modo in cui questo
progetto ha riportato l'asse di hatching.
"""

import os
import re
import csv
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))


def _first(*cand):
    for c in cand:
        if os.path.isdir(c):
            return c
    return cand[-1]


ROOT = _first(os.path.join(_HERE, os.pardir, "data"),
              r"c:\Users\aless\Desktop\comfyui-pilot")
PAL = os.path.join(ROOT, "palette_features_stage9.csv")
STY = os.path.join(ROOT, "style_features_stage9.csv")
OUT = os.path.join(ROOT, "stage9_observation_quantification.csv")

CONDS = ["preset_pos_1x", "preset_pos_2x", "blockshuf_neg_1x",
         "blockshuf_neg_2x", "rand_pos_1x", "rand_pos_2x"]
SW = [f"sw{i}" for i in range(1, 7)]

# metrica -> (sorgente, osservazione, verso atteso dall'occhio)
METRICS = [
    ("L_mean",          "palette", "oss.6 preset_pos scurisce",            "negativo per preset_pos"),
    ("C_mean",          "palette", "oss.3 preset_pos desatura",            "negativo per preset_pos"),
    ("subject_frac",    "palette", "oss.8 blockshuf_neg ingrandisce",      "positivo per blockshuf_neg"),
    ("colorfulness_hs", "style",   "oss.3 desaturazione (colorfulness)",   "negativo per preset_pos"),
    ("lbp_entropy",     "style",   "oss.3/4 grana",                        "positivo per preset_pos e rand_pos"),
    ("edge_density",    "style",   "oss.3 sfocatura",                      "negativo per preset_pos"),
]


def load_palette():
    d = pd.read_csv(PAL)
    d = d[d["prompt_dir"].astype(str).str.startswith("S")].copy()
    w = d[[f"{s}_share" for s in SW]].values.astype(float)
    w = w / np.clip(w.sum(1, keepdims=True), 1e-9, None)
    d["L_mean"] = (d[[f"{s}_L" for s in SW]].values * w).sum(1)
    d["C_mean"] = (d[[f"{s}_C" for s in SW]].values * w).sum(1)
    return d[["prompt_dir", "condition", "seed", "L_mean", "C_mean", "subject_frac"]]


def load_style():
    d = pd.read_csv(STY)
    rows = []
    for _, r in d.iterrows():
        m = re.match(r"^(S\d+)_([a-z0-9]+)_(.+)_seed(\d+)_", str(r["file"]))
        if not m:
            continue
        rec = {c: r[c] for c in d.columns
               if c not in ("file", "condition", "prompt_dir", "seed")}
        rec.update(prompt_dir=m.group(1), condition=m.group(3), seed=int(m.group(4)))
        rows.append(rec)
    return pd.DataFrame(rows)


def paired(df, metric):
    base = df[df.condition == "baseline"].set_index(["prompt_dir", "seed"])[metric]
    out = {}
    for c in CONDS:
        cur = df[df.condition == c].set_index(["prompt_dir", "seed"])[metric]
        common = cur.index.intersection(base.index)
        if len(common) == 0:
            continue
        d = cur.loc[common] - base.loc[common]
        per_prompt = d.groupby(level=0).mean()
        out[c] = dict(
            delta=float(per_prompt.mean()),
            prompts_pos=int((per_prompt > 0).sum()), prompts_n=int(len(per_prompt)),
            images_pos=int((d > 0).sum()), images_n=int(len(d)),
        )
    return out


def main():
    pal, sty = load_palette(), load_style()
    rows = []
    print("QUANTIFICAZIONE DELLE OSSERVAZIONI DIRETTE — stage 9, 8 prompt, 5 seed")
    print("delta = condizione - baseline (stesso prompt, stesso seed)")
    print("NON e' conferma: misura sugli stessi render che hanno generato l'osservazione\n")
    for metric, src, obs, atteso in METRICS:
        df = pal if src == "palette" else sty
        if metric not in df.columns:
            print(f"  [{metric}] non disponibile")
            continue
        res = paired(df, metric)
        print(f"  {obs}  —  {metric}   (atteso: {atteso})")
        print(f"    {'condizione':18s} {'delta':>10s} {'prompt +':>10s} {'immagini +':>13s}")
        for c, v in res.items():
            print(f"    {c:18s} {v['delta']:+10.3f} "
                  f"{v['prompts_pos']:>6d}/{v['prompts_n']:<3d} "
                  f"{v['images_pos']:>8d}/{v['images_n']:<3d}")
            rows.append(dict(observation=obs, metric=metric, source=src,
                             condition=c, **v))
        print()
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  -> scritto {os.path.basename(OUT)}")


if __name__ == "__main__":
    main()
