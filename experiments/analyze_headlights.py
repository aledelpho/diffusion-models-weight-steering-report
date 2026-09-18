# -*- coding: utf-8 -*-
"""
experiments/analyze_headlights.py  —  lavoro A del BRIEF_stage10_strumenti

Unisce i punteggi ciechi dei fari alla chiave e produce:
  data/stage9_headlights_results.csv

Regole fissate nel brief PRIMA dello scoring:
  - il codice 1 ("non chiaro") non e' un valore intermedio: esce da numeratore e
    denominatore, e il conteggio degli ambigui si riporta per condizione;
  - unita' di analisi = il prompt, i seed si mediano prima (pitfall 17);
  - test di permutazione esatta sign-flip sugli 8 prompt, Holm sulle 6 condizioni;
  - l'osservazione vale solo se sopravvive a luminanza tenuta ferma.

NON E' UNA CONFERMA: l'osservazione dei fari e' nata guardando questi render e qui
viene misurata sugli stessi. La conferma richiede render nuovi.
"""
import os, csv, itertools
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
def _first(*c):
    for x in c:
        if os.path.isdir(x): return x
    return c[-1]
ROOT = _first(os.path.join(_HERE, os.pardir, "data"), r"c:\Users\aless\Desktop\comfyui-pilot")
CONDS = ["preset_pos_1x","preset_pos_2x","blockshuf_neg_1x","blockshuf_neg_2x","rand_pos_1x","rand_pos_2x"]
SW = [f"sw{i}" for i in range(1,7)]

def exact_signflip(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    n = len(x); obs = x.mean()
    S = np.array(list(itertools.product([1,-1], repeat=n)))
    null = (S * x).mean(1)
    informative = int((np.abs(x) > 1e-12).sum())
    return obs, float((np.abs(null) >= abs(obs) - 1e-12).mean()), n, informative

def holm(ps):
    order = np.argsort(ps); out = [0.0]*len(ps)
    for rank, i in enumerate(order):
        out[i] = min(1.0, max(ps[order[j]]*(len(ps)-j) for j in range(rank+1)))
    return out

def main():
    raw = pd.read_csv(os.path.join(ROOT, "stage9_headlights_raw.csv"))
    key = pd.read_csv(os.path.join(ROOT, "stage9_headlights_key.csv"))

    # Il viewer APPENDE una riga nuova quando si torna indietro e si ricorregge,
    # invece di sostituire quella vecchia. Senza questo, le immagini ricorrette
    # entrano due volte e i conteggi si gonfiano in silenzio: 284 righe per 280
    # immagini, con il punteggio vecchio e quello nuovo entrambi contati.
    # Vale l'ULTIMO punteggio dato.
    n_before = len(raw)
    raw = raw.sort_values("timestamp_ms").drop_duplicates("hash_id", keep="last")
    if n_before != len(raw):
        print(f"  ri-punteggiature risolte tenendo l'ultima: {n_before} righe -> {len(raw)}")

    d = key.merge(raw, on="hash_id", how="left")
    # Cancello che deve fallire rumorosamente (regola 5 dell'errors_log)
    if len(d) != len(key):
        raise RuntimeError(f"merge ha cambiato il numero di righe: {len(key)} -> {len(d)}")
    if d.code.isna().any():
        raise RuntimeError(f"{int(d.code.isna().sum())} immagini senza punteggio")
    d["prompt"] = d.prompt_id
    d["lit"] = d.code.map({0:0.0, 2:1.0, 1:np.nan})
    d["amb"] = (d.code == 1).astype(int)

    seq = d.sort_values("order").cond_name.values
    adj = int((seq[1:] == seq[:-1]).sum())
    print(f"cecita: condizioni adiacenti uguali {adj}/{len(seq)-1} (atteso ~{(len(seq)-1)/7:.0f})")

    pal = pd.read_csv(os.path.join(ROOT, "palette_features_stage9.csv"))
    pal = pal[pal.prompt_dir.astype(str).str.startswith("S")].copy()
    w = pal[[f"{s}_share" for s in SW]].values.astype(float)
    w = w / np.clip(w.sum(1, keepdims=True), 1e-9, None)
    pal["L_mean"] = (pal[[f"{s}_L" for s in SW]].values * w).sum(1)
    pal["prompt_short"] = pal.prompt_dir
    d["prompt_short"] = d.prompt.str.split("_").str[0]
    d = d.merge(pal[["prompt_short","condition","seed","L_mean"]],
                left_on=["prompt_short","cond_name","seed"],
                right_on=["prompt_short","condition","seed"], how="left")

    rows, ps = [], []
    rate = lambda s: (s.lit.sum()/s.lit.notna().sum()) if s.lit.notna().sum() else np.nan
    for c in CONDS:
        dl = []
        for p in sorted(d.prompt.unique()):
            b = rate(d[(d.prompt==p)&(d.cond_name=="baseline")])
            q = rate(d[(d.prompt==p)&(d.cond_name==c)])
            dl.append(q-b if not (np.isnan(b) or np.isnan(q)) else np.nan)
        m, p_, n, info = exact_signflip(dl)
        ps.append(p_)
        s = d[d.cond_name==c]
        rows.append(dict(condition=c, rate=round(rate(s),4),
                         lit=int(s.lit.sum()), n_valid=int(s.lit.notna().sum()),
                         ambiguous=int(s.amb.sum()),
                         delta_vs_baseline=round(m,4), prompts_n=n,
                         prompts_informative=info, p_exact=round(p_,4)))
    for r, h in zip(rows, holm(ps)):
        r["p_holm"] = round(h, 4)

    b = d[d.cond_name=="baseline"]
    rows.insert(0, dict(condition="baseline", rate=round(rate(b),4), lit=int(b.lit.sum()),
                        n_valid=int(b.lit.notna().sum()), ambiguous=int(b.amb.sum()),
                        delta_vs_baseline="", prompts_n="", prompts_informative="",
                        p_exact="", p_holm=""))

    v = d.dropna(subset=["lit","L_mean"]).copy()
    v["tert"] = pd.qcut(v.L_mean, 3, labels=["dark","mid","light"])
    for r in rows:
        for t in ["dark","mid","light"]:
            s = v[(v.cond_name==r["condition"]) & (v.tert==t)]
            r[f"rate_{t}"] = round(s.lit.mean(),3) if len(s) else ""
            r[f"n_{t}"] = len(s)

    out = os.path.join(ROOT, "stage9_headlights_results.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w2 = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w2.writeheader(); w2.writerows(rows)
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"\n-> {os.path.basename(out)}")

if __name__ == "__main__":
    main()
