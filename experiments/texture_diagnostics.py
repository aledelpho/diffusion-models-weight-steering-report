"""
experiments/texture_diagnostics.py  --  tre controlli prima di credere all'inversione

analyze_texture.py ha trovato che nello spazio del tratto l'ordine delle tre
condizioni CAMBIA rispetto a CLIP: randsign (+0.489) supera blockshuffle
(+0.354), e preset - blockshuffle diventa significativo (+0.249, P = 0.001) dopo
essere stato insignificante per due tappe. Prima di costruirci sopra, tre cose
vanno verificate, e tutte e tre si verificano sui dati che ci sono.

1. CHI PORTA LA DIREZIONE. La tabella delle feature che si muovono e' magra --
   undici righe sopra |z| = 1 -- e in cima ci sono freq_banda_8 e freq_banda_9,
   cioe' le due bande piu' vicine a Nyquist del ridimensionamento a 512x640:
   esattamente dove mi aspetterei artefatti di ricampionamento, non tratteggio.
   Le larghezze del tratto, che sulle due immagini di esempio separavano di un
   fattore 2.5, non compaiono affatto. Qui si guarda il carico della direzione A
   su ogni feature, non la media grezza: la media mescola S e A, il carico no.

2. L'AMPIEZZA NON E' PIU' APPAIATA. In CLIP |A| era identico alla terza cifra
   (0.2214 / 0.2243 / 0.2209): l'appaiamento in spazio dei pesi si trasmetteva
   all'immagine e le coerenze erano confrontabili senza riserve. Nel tratto NON
   e' cosi': preset 3.261, blockshuffle 2.678, randsign 2.741. Il preset si
   muove il 19-22% piu' dei controlli a pari spostamento dei pesi. Ma una
   direzione piu' grande rispetto al rumore e' stimata meglio, e una stima
   migliore attenua di meno i coseni: parte del vantaggio del preset potrebbe
   essere solo rapporto segnale-rumore. Si misura l'affidabilita' dividendo i
   seed a meta' e si disattenua.

3. ROBUSTEZZA AI BLOCCHI DI FEATURE. Se l'inversione regge togliendo le bande
   alte, o usando solo l'inchiostro, o solo la piattezza, e' un fatto sulla
   tecnica di resa. Se vive in un blocco solo, e' un fatto su quel blocco.

Zero immagini nuove.
"""

import os
import sys
import csv
import glob
import collections
import itertools
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_texture import (COND, PAIRS, CSV_IN, CSV_BASE, TEX_NPZ, NAMES, b)

ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
OUT = os.path.join(ROOT, "texture_diagnostics.csv")
RNG = np.random.default_rng(20260914)

BLOCCHI = {
    "ink (mark)": lambda n: n.startswith("mark_") or n.startswith("ink_"),
    "flatness (fill)": lambda n: n.startswith("flat_"),
    "frequency": lambda n: n.startswith("freq_"),
    "edges": lambda n: n.startswith("edge_"),
    "senza le 3 bande alte": lambda n: n not in ("freq_banda_7", "freq_banda_8", "freq_banda_9"),
    "tutto": lambda n: True,
}


def load():
    z = np.load(TEX_NPZ, allow_pickle=True)
    T = {k: z[k] for k in z.files if k != "__names__"}
    rows = []
    for p in CSV_IN:
        if os.path.exists(p):
            rows += [r for r in csv.DictReader(open(p, encoding="utf-8-sig"))
                     if r.get("preset_file") in COND]
    bases = {}
    for p in CSV_BASE:
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8-sig")):
                if r.get("operation") == "baseline":
                    bases.setdefault((r["prompt_id"], r["seed"]), r["image_path"])
    for r in rows:
        bases.setdefault((r["prompt_id"], r["seed"]), r["baseline_path"])
    byc = collections.defaultdict(dict)
    for r in rows:
        byc[COND[r["preset_file"]]][(r["prompt_id"], r["seed"])] = r["image_path"]
    return T, byc, bases


def A_cells(E, byc, bases, cp, cn, prompts, mask):
    """A per (prompt, seed), sul sottoinsieme di feature indicato da mask."""
    out = collections.defaultdict(dict)
    for k in byc[cp]:
        if k not in byc[cn] or k[0] not in prompts:
            continue
        dp = E[b(byc[cp][k])][mask] - E[b(bases[k])][mask]
        dn = E[b(byc[cn][k])][mask] - E[b(bases[k])][mask]
        out[k[0]][k[1]] = (dp - dn) / 2.0
    return out


def coh_of(cells, prompts, seeds=None):
    M = []
    for p in prompts:
        v = [x for s, x in cells[p].items() if seeds is None or s in seeds]
        if not v:
            return np.nan
        M.append(np.mean(v, axis=0))
    M = np.stack(M)
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    G = M @ M.T
    iu = np.triu_indices(len(M), 1)
    return float(G[iu].mean())


def main():
    T, byc, bases = load()
    keys = sorted(T)
    M = np.stack([T[k] for k in keys])
    mu, sd = M.mean(0), M.std(0)
    sd[sd < 1e-9] = 1.0
    E = {k: (T[k] - mu) / sd for k in keys}

    conds = [c for _n, a, bb in PAIRS for c in (a, bb) if c in byc]
    prompts = sorted({p for c in conds for p, _s in byc[c]})
    prompts = [p for p in prompts
               if all(sum(1 for pp, _s in byc[c] if pp == p) >= 5 for c in conds)]
    seeds = sorted({s for p, s in byc[conds[0]] if p in prompts}, key=int)
    print(f"[diag] {len(prompts)} prompt, {len(seeds)} seed, {len(NAMES)} feature")

    full = np.ones(len(NAMES), dtype=bool)
    out = []

    # ---- 1. chi porta la direzione ------------------------------------------
    print("\n" + "=" * 82)
    print("  WHAT CARRIES DIRECTION A   (loading of the mean direction, not of the raw mean)")
    print("=" * 82)
    for name, cp, cn in PAIRS:
        cells = A_cells(E, byc, bases, cp, cn, prompts, full)
        Mp = np.stack([np.mean(list(cells[p].values()), axis=0) for p in prompts])
        Mp = Mp / (np.linalg.norm(Mp, axis=1, keepdims=True) + 1e-12)
        med = np.median(Mp, axis=0)                 # direzione condivisa, robusta
        med = med / (np.linalg.norm(med) + 1e-12)
        ordine = np.argsort(-np.abs(med))
        quota = {}
        for lab, fn in BLOCCHI.items():
            if lab in ("tutto", "senza le 3 bande alte"):
                continue
            m = np.array([fn(n) for n in NAMES])
            quota[lab] = float((med[m] ** 2).sum())
        print(f"\n  {name}")
        print("    prime sei feature: " +
              ", ".join(f"{NAMES[i]} {med[i]:+.2f}" for i in ordine[:6]))
        print("    energia per blocco: " +
              "   ".join(f"{k} {v*100:.0f}%" for k, v in
                         sorted(quota.items(), key=lambda x: -x[1])))
        for i in ordine[:8]:
            out.append(dict(type="loading", condition=name, key=NAMES[i],
                            value=round(float(med[i]), 4)))
        for k, v in quota.items():
            out.append(dict(type="block_energy", condition=name, key=k,
                            value=round(v, 4)))

    # ---- 2. affidabilita' e disattenuazione ----------------------------------
    print("\n" + "=" * 82)
    print("  AFFIDABILITA'   (meta' dei seed contro l'altra meta')")
    print("  Una direzione piu' grande rispetto al rumore e' stimata meglio, e una")
    print("  stima migliore attenua di meno i coseni. rho corregge questo.")
    print("=" * 82)
    h1, h2 = set(seeds[0::2]), set(seeds[1::2])
    print(f"\n  {'condition':14s}{'|A|':>8s}{'rho':>8s}{'coherence':>10s}"
          f"{'disattenuata':>14s}")
    dis = {}
    for name, cp, cn in PAIRS:
        cells = A_cells(E, byc, bases, cp, cn, prompts, full)
        na = float(np.mean([np.linalg.norm(v) for p in prompts for v in cells[p].values()]))
        cs = []
        for p in prompts:
            u = np.mean([v for s, v in cells[p].items() if s in h1], axis=0)
            w = np.mean([v for s, v in cells[p].items() if s in h2], axis=0)
            cs.append(float(u @ w / (np.linalg.norm(u) * np.linalg.norm(w) + 1e-12)))
        # Spearman-Brown: da meta' campione al campione intero
        r = float(np.mean(cs))
        rho = 2 * r / (1 + r) if r > -1 else 0.0
        c = coh_of(cells, prompts)
        dis[name] = c / rho if rho > 0.05 else np.nan
        print(f"  {name:14s}{na:>8.3f}{rho:>8.3f}{c:>+10.3f}{dis[name]:>+14.3f}")
        out.append(dict(type="reliability", condition=name, key="rho",
                        value=round(rho, 4)))
        out.append(dict(type="reliability", condition=name, key="coh_disattenuated",
                        value=round(float(dis[name]), 4)))
    print("\n  differenze disattenuate:")
    for a, bb in (("preset", "randsign"), ("preset", "blockshuffle"),
                  ("blockshuffle", "randsign")):
        print(f"    {a:14s} - {bb:14s}{dis[a]-dis[bb]:>+8.3f}")
        out.append(dict(type="reliability", condition=f"{a}-{bb}",
                        key="diff_disattenuated", value=round(float(dis[a] - dis[bb]), 4)))

    # ---- 3. robustezza ai blocchi di feature ---------------------------------
    print("\n" + "=" * 82)
    print("  ROBUSTEZZA   (coerenza ricalcolata su sottoinsiemi di feature)")
    print("=" * 82)
    # un blocco di feature e' un sottospazio: la coerenza va confrontata col
    # proprio null, non con quello dello spazio intero, e le differenze fra
    # condizioni vanno testate dentro lo stesso sottospazio.
    def gram_of(cells):
        M = np.stack([np.mean(list(cells[p].values()), axis=0) for p in prompts])
        M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
        return M @ M.T

    def take_coh(G, t):
        k = len(t)
        if k < 2:
            return np.nan
        sub = G[np.ix_(t, t)]
        iu = np.triu_indices(k, 1)
        same = t[:, None] == t[None, :]
        v = sub[iu][~same[iu]]
        return float(v.mean()) if v.size else np.nan

    P = len(prompts)
    iu = np.triu_indices(P, 1)
    sg = RNG.choice([-1.0, 1.0], size=(10000, P))
    for lab, fn in BLOCCHI.items():
        m = np.array([fn(n) for n in NAMES])
        if m.sum() < 3:
            continue
        G, vals = {}, {}
        print(f"\n  {lab}   ({int(m.sum())} feature)")
        print(f"    {'condition':14s}{'coherence':>10s}{'null p95':>10s}{'p':>9s}")
        for name, cp, cn in PAIRS:
            cells = A_cells(E, byc, bases, cp, cn, prompts, m)
            G[name] = gram_of(cells)
            vals[name] = float(G[name][iu].mean())
            nullp = np.array([float(np.mean((np.outer(v, v) * G[name])[iu])) for v in sg])
            pv = float((np.sum(nullp >= vals[name]) + 1) / 10001)
            print(f"    {name:14s}{vals[name]:>+10.3f}"
                  f"{np.percentile(nullp, 95):>+10.3f}{pv:>9.4f}")
            out.append(dict(type="block_coherence", condition=name, key=lab,
                            value=round(vals[name], 4)))
            out.append(dict(type="block_p", condition=name, key=lab,
                            value=round(pv, 5)))
        for a, bb in (("preset", "randsign"), ("preset", "blockshuffle"),
                      ("blockshuffle", "randsign")):
            dr = np.empty(8000)
            for i in range(8000):
                t = RNG.integers(0, P, P)
                dr[i] = take_coh(G[a], t) - take_coh(G[bb], t)
            dr = dr[~np.isnan(dr)]
            lo, hi = np.percentile(dr, [2.5, 97.5])
            print(f"      {a:12s} - {bb:12s}{vals[a]-vals[bb]:>+8.3f}"
                  f"   IC95 [{lo:+.3f}, {hi:+.3f}]   P(<=0) {np.mean(dr <= 0):.4f}")
            out.append(dict(type="block_diff", condition=f"{a}-{bb}",
                            key=f"{lab}|CI[{lo:+.3f},{hi:+.3f}]",
                            value=round(float(vals[a] - vals[bb]), 4)))
        print(f"    ordine: " + " > ".join(k for k in sorted(vals, key=lambda k: -vals[k])))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["type", "condition", "key", "value"])
        w.writeheader(); w.writerows(out)
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
