# -*- coding: utf-8 -*-
"""
experiments/stage9_centering_sensitivity.py

Controllo di sensibilita' alla convenzione di centratura, per stage 9.

analyze_stage9_style_direction.py standardizza le differenze con
(v - mu_congiunta) / sigma_congiunta. analyze_palette_coherence.py, che ha
prodotto i coseni di sezione 1.5, divide solo per sigma e NON centra. Le due
grandezze non sono sulla stessa scala, ed e' gia' un problema di comparabilita'
(famiglia della pitfall 33).

Ma in un confronto FRA GRUPPI la centratura fa un danno peggiore e specifico.
Sottrarre un vettore comune che non e' la media del singolo gruppo lascia dentro
ogni vettore di quel gruppo una componente condivisa -mu, e quella componente
allinea artificialmente i vettori fra loro. Il gruppo la cui media si discosta
di piu' da mu_congiunta ne riceve di piu', quindi la sua coerenza sale per
costruzione. Con 8 prompt di stile contro 18 di soggetto, e con il braccio di
stile renderizzato a 2.0x mentre il confronto sta a 1.0x, l'asimmetria non e'
un rischio: e' garantita.

Questo script ricalcola Delta C = C_soggetto - C_stile sotto entrambe le
convenzioni, sugli stessi dati, e scrive data/stage9_centering_sensitivity.csv.
Non rifa' il test di permutazione: serve a mostrare se il SEGNO della conclusione
dipende dalla convenzione. Se dipende, non c'e' conclusione.

Nessuna GPU, nessun render nuovo.
"""

import os
import csv
import itertools
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
STYLE_CSV = os.path.join(ROOT, "palette_features_stage9.csv")
SUBJ_CSV = os.path.join(ROOT, "palette_features_all.csv")
OUT = os.path.join(ROOT, "stage9_centering_sensitivity.csv")

SLOTS = ["paper", "ink"] + [f"sw{i}" for i in range(1, 7)]

# (condizione stile, condizione soggetto). Il corpus soggetto esiste solo a 1.0x:
# le righe 2x confrontano stile a D~0.108 contro soggetto a D~0.0538, ed e' un
# confound dichiarato, non un difetto di questo script.
CELLS = [
    ("preset_pos_1x", "preset_pos", "Ampiezza 1.0x"),
    ("blockshuf_neg_1x", "blockshuf_neg", "Ampiezza 1.0x"),
    ("rand_pos_1x", "rand_pos", "Ampiezza 1.0x"),
    ("preset_pos_2x", "preset_pos", "Ampiezza 2.0x"),
    ("blockshuf_neg_2x", "blockshuf_neg", "Ampiezza 2.0x"),
    ("rand_pos_2x", "rand_pos", "Ampiezza 2.0x"),
]

SPACES = [
    ("1. 24-D Completo (L*, a*, b*)", list(range(24))),
    ("2. 8-D Solo Luminanza (L*)", [i for i in range(24) if i % 3 == 0]),
    ("3. 16-D Solo Cromatico (a*, b*)", [i for i in range(24) if i % 3 != 0]),
]


def vec24(r):
    out = []
    for s in SLOTS:
        L = float(r[f"{s}_L"])
        C = float(r[f"{s}_C"])
        h = np.deg2rad(float(r[f"{s}_hue_deg"]))
        out += [L, C * np.cos(h), C * np.sin(h)]
    return np.array(out, float)


def seed_deltas(df, cond):
    """{prompt: array(seed x 24)} della differenza dalla baseline APPAIATA."""
    V = {}
    for _, r in df.iterrows():
        V[(str(r["prompt_dir"]), str(r["condition"]), int(r["seed"]))] = vec24(r)
    out = {}
    for p in sorted({k[0] for k in V}):
        seeds = sorted({k[2] for k in V if k[0] == p})
        ds = [V[(p, cond, s)] - V[(p, "baseline", s)] for s in seeds
              if (p, cond, s) in V and (p, "baseline", s) in V]
        if len(ds) >= 4:
            out[p] = np.stack(ds)
    return out


def mean_pairwise_cos(M):
    acc = []
    for a, b in itertools.combinations(M, 2):
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na > 0 and nb > 0:
            acc.append(float(a @ b / (na * nb)))
    return float(np.mean(acc)) if acc else float("nan")


def main():
    style = pd.read_csv(STYLE_CSV)
    style = style[style["prompt_dir"].astype(str).str.startswith("S")]
    subj = pd.read_csv(SUBJ_CSV)

    rows = []
    print("SENSIBILITA' ALLA CENTRATURA — Delta C = C_soggetto - C_stile")
    print("l'ipotesi prevede Delta > 0\n")
    print(f"  {'ampiezza':14s} {'spazio':34s} {'condizione':18s}"
          f" {'centrato':>10s} {'non centr.':>11s}  concordi")

    for cs, cj, amp in CELLS:
        Ds, Dj = seed_deltas(style, cs), seed_deltas(subj, cj)
        if not Ds or not Dj:
            print(f"  [SALTATA] {cs}: celle mancanti")
            continue
        pool = np.concatenate([np.concatenate(list(Ds.values())),
                               np.concatenate(list(Dj.values()))])
        mu, sd = pool.mean(0), pool.std(0)
        sd[sd < 1e-9] = 1.0

        for space_name, idx in SPACES:
            vals = {}
            for label, m0 in (("centrato", mu), ("non_centrato", np.zeros(24))):
                Us = [(((v - m0) / sd)[:, idx]).mean(0) for v in Ds.values()]
                Uj = [(((v - m0) / sd)[:, idx]).mean(0) for v in Dj.values()]
                vals[label] = (mean_pairwise_cos(Us), mean_pairwise_cos(Uj))
            d_c = vals["centrato"][1] - vals["centrato"][0]
            d_u = vals["non_centrato"][1] - vals["non_centrato"][0]
            agree = "si" if (d_c > 0) == (d_u > 0) else "NO — SEGNO INVERTITO"
            print(f"  {amp:14s} {space_name:34s} {cs:18s}"
                  f" {d_c:+10.4f} {d_u:+11.4f}  {agree}")
            rows.append(dict(
                amplitude=amp, space=space_name,
                condition_style=cs, condition_subject=cj,
                c_style_centered=round(vals["centrato"][0], 4),
                c_subject_centered=round(vals["centrato"][1], 4),
                delta_c_centered=round(d_c, 4),
                c_style_uncentered=round(vals["non_centrato"][0], 4),
                c_subject_uncentered=round(vals["non_centrato"][1], 4),
                delta_c_uncentered=round(d_u, 4),
                sign_agrees=("yes" if (d_c > 0) == (d_u > 0) else "NO"),
            ))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    flips = sum(1 for r in rows if r["sign_agrees"] == "NO")
    print(f"\n  celle in cui il segno dipende dalla convenzione: {flips} su {len(rows)}")
    print(f"  -> scritto {os.path.basename(OUT)}")


if __name__ == "__main__":
    main()
