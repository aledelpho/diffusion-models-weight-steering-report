"""
experiments/stage5_followup.py  --  due domande che i dati gia' sul disco
possono rispondere, senza generare una sola immagine nuova.

Legge la cache _stage5_emb.npz e basta.

DOMANDA 1 -- e' replica o e' estensione?
  Lo Stage 4 aveva misurato preset contro randsign su QUATTRO prompt e ottenuto
  +0.173 con un intervallo che toccava lo zero. Lo Stage 5 ne usa sette e
  ottiene +0.165 con un intervallo che lo zero non lo tocca. La tentazione e'
  chiamarla replica, ma quei sette prompt CONTENGONO i quattro di prima: non e'
  un campione indipendente. L'unico confronto onesto e' la coerenza calcolata
  sui soli tre prompt nuovi -- G2, G4, G6, due maschi e tre tinte che nei primi
  quattro non comparivano -- contro quella sui soli quattro vecchi. Tre prompt
  danno tre coppie e quindi un numero rumorosissimo; non serve a dichiarare
  niente, serve a vedere se il segno e l'ordine reggono fuori campione.

DOMANDA 2 -- domani, dove conviene spendere?
  Il confronto preset - blockshuffle e' rimasto a +0.078 con IC [-0.059, +0.239]:
  la domanda "conta QUESTA assegnazione" resta aperta. Prima di comprare altri
  prompt vale la pena sapere se l'incertezza viene dai prompt o dai seed, e la
  risposta e' nei dati: basta rifare il bootstrap usando meno seed per cella e
  meno prompt, e guardare come si allarga l'intervallo nei due casi. Se
  togliere seed non lo allarga, i seed sono gia' abbastanza e ogni immagine in
  piu' va spesa in prompt nuovi. Poi si estrapola quanti prompt servirebbero
  davvero per staccare quel +0.078 dallo zero.
"""

import os
import sys
import csv
import collections
import itertools
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
EMB_NPZ = os.path.join(ROOT, "_stage5_emb.npz")
CSV_IN = [os.path.join(ROOT, "stage4_images.csv"), os.path.join(ROOT, "stage5_images.csv")]
CSV_BASE = [os.path.join(ROOT, "stage2_images.csv"), os.path.join(ROOT, "stage5_images.csv")]
OUT = os.path.join(ROOT, "stage5_followup.csv")

COND = {
    "Arthemy_Bench_Base.json": "preset_pos", "Arthemy_Bench_NEG.json": "preset_neg",
    "Arthemy_Bench_RANDSIGN.json": "rand_pos", "Arthemy_Bench_RANDSIGN_NEG.json": "rand_neg",
    "Arthemy_Bench_BLOCKSHUFFLE.json": "blockshuf_pos",
    "Arthemy_Bench_BLOCKSHUFFLE_NEG.json": "blockshuf_neg",
}
PAIRS = [("preset", "preset_pos", "preset_neg"),
         ("blockshuffle", "blockshuf_pos", "blockshuf_neg"),
         ("randsign", "rand_pos", "rand_neg")]
CONFRONTI = [("preset", "randsign"), ("preset", "blockshuffle"), ("blockshuffle", "randsign")]
PAIRMAP = {n: (cp, cn) for n, cp, cn in PAIRS}
N_BOOT = 20000
RNG = np.random.default_rng(20260914)
b = os.path.basename


def load_all():
    z = np.load(EMB_NPZ, allow_pickle=True)
    E = {"GREZZO": {k[4:]: z[k] for k in z.files if k.startswith("raw|")},
         "COLORE NORMALIZZATO": {k[3:]: z[k] for k in z.files if k.startswith("cn|")}}
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
    return E, byc, bases


def A_cells(E, byc, bases, cp, cn, prompts, seeds=None):
    """A per (prompt, seed), limitata ai prompt e ai seed indicati."""
    out = collections.defaultdict(list)
    for k in byc[cp]:
        if k not in byc[cn] or k[0] not in prompts:
            continue
        if seeds is not None and k[1] not in seeds:
            continue
        dp = E[b(byc[cp][k])] - E[b(bases[k])]
        dn = E[b(byc[cn][k])] - E[b(bases[k])]
        out[k[0]].append((dp - dn) / 2.0)
    return out


def gram_of(cells, prompts):
    M = np.stack([np.mean(cells[p], axis=0) for p in prompts])
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    return M @ M.T


def coh(G):
    iu = np.triu_indices(len(G), 1)
    return float(G[iu].mean())


def coh_take(G, take):
    k = len(take)
    if k < 2:
        return np.nan
    sub = G[np.ix_(take, take)]
    iu = np.triu_indices(k, 1)
    same = take[:, None] == take[None, :]
    v = sub[iu][~same[iu]]
    return float(v.mean()) if v.size else np.nan


def boot_ci(Ga, Gb, n, n_boot=N_BOOT):
    d = np.empty(n_boot)
    for i in range(n_boot):
        t = RNG.integers(0, n, n)
        d[i] = coh_take(Ga, t) - coh_take(Gb, t)
    d = d[~np.isnan(d)]
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def main():
    E, byc, bases = load_all()
    prompts = sorted({p for c in byc.values() for p, _ in c})
    prompts = [p for p in prompts
               if all(sum(1 for pp, _s in byc[c] if pp == p) >= 5
                      for nm, a, bb in PAIRS for c in (a, bb))]
    old = [p for p in prompts if p.startswith("F")]
    new = [p for p in prompts if p.startswith("G")]
    seeds = sorted({s for _, s in byc["preset_pos"]}, key=int)
    print(f"prompt completi {len(prompts)}: vecchi {old}  nuovi {new}")
    print(f"seed per cella: {len(seeds)}  {seeds}")

    out_rows = []

    # ---------------------------------------------------------------- domanda 1
    print("\n" + "=" * 78)
    print("  FUORI CAMPIONE  --  i tre prompt nuovi da soli")
    print("=" * 78)
    for space in E:
        print(f"\n  {space}")
        print(f"    {'condizione':14s}{'tutti 7':>10s}{'F1..F4':>10s}{'G2,G4,G6':>11s}")
        cells = {}
        for name, cp, cnx in PAIRS:
            cells[name] = A_cells(E[space], byc, bases, cp, cnx, prompts)
            vals = [coh(gram_of(cells[name], s)) for s in (prompts, old, new)]
            print(f"    {name:14s}" + "".join(f"{v:>+10.3f}" if i < 2 else f"{v:>+11.3f}"
                                              for i, v in enumerate(vals)))
            out_rows.append(dict(spazio=space, tipo="coerenza", chi=name,
                                 tutti=round(vals[0], 4), vecchi=round(vals[1], 4),
                                 nuovi=round(vals[2], 4)))
        print(f"\n    {'differenza':28s}{'tutti 7':>10s}{'F1..F4':>10s}{'G2,G4,G6':>11s}")
        for a, bb in CONFRONTI:
            vals = [coh(gram_of(cells[a], s)) - coh(gram_of(cells[bb], s))
                    for s in (prompts, old, new)]
            print(f"    {a+' - '+bb:28s}" + "".join(f"{v:>+10.3f}" if i < 2 else f"{v:>+11.3f}"
                                                    for i, v in enumerate(vals)))
            out_rows.append(dict(spazio=space, tipo="differenza", chi=f"{a}-{bb}",
                                 tutti=round(vals[0], 4), vecchi=round(vals[1], 4),
                                 nuovi=round(vals[2], 4)))
    print("\n  Tre prompt danno tre coppie: il numero e' rumoroso per costruzione.")
    print("  Serve a vedere se il SEGNO e l'ORDINE reggono fuori campione, non altro.")

    # ---------------------------------------------------------------- domanda 2
    print("\n" + "=" * 78)
    print("  DOVE STA L'INCERTEZZA  --  seed o prompt?")
    print("=" * 78)
    space = "COLORE NORMALIZZATO"
    Ecn = E[space]
    print(f"  ({space}; ampiezza dell'IC95 sulla differenza)\n")
    n_seed = len(seeds)
    seed_grid = [n for n in (n_seed, 3, 2) if n <= n_seed]
    print("    d = differenza,  h = semiampiezza IC95,  d/h > 1 significa deciso\n")
    print(f"    {'confronto':28s}" + "".join(f"{f'{n} seed':>22s}" for n in seed_grid))
    print(f"    {'':28s}" + "".join(f"{'d':>8s}{'h':>7s}{'d/h':>7s}" for _ in seed_grid))
    for a, bb in CONFRONTI:
        line = f"    {a+' - '+bb:28s}"
        rec = dict(spazio=space, tipo="per_seed", chi=f"{a}-{bb}")
        for ns in seed_grid:
            sub = seeds[:ns]
            ga = gram_of(A_cells(Ecn, byc, bases, *PAIRMAP[a], prompts, set(sub)), prompts)
            gb = gram_of(A_cells(Ecn, byc, bases, *PAIRMAP[bb], prompts, set(sub)), prompts)
            lo, hi = boot_ci(ga, gb, len(prompts), 4000)
            d, h = coh(ga) - coh(gb), (hi - lo) / 2
            rec[f"d_seed{ns}"] = round(d, 5)
            rec[f"h_seed{ns}"] = round(h, 5)
            rec[f"dh_seed{ns}"] = round(d / h if h else 0.0, 4)
            line += f"{d:>+8.3f}{h:>7.3f}{d/h if h else 0:>7.2f}"
        print(line)
        out_rows.append(rec)
    print("\n    Se d/h non peggiora togliendo seed, i seed sono gia' abbastanza e ogni")
    print("    immagine in piu' va spesa in prompt nuovi. Guardare la sola ampiezza non")
    print("    basta: meno seed = direzioni A piu' rumorose = coseni attenuati, quindi")
    print("    anche la differenza si accorcia.\n")

    kgrid = list(range(4, len(prompts) + 1))
    print(f"    {'confronto':28s}" + "".join(f"{f'{k}':>9s}" for k in kgrid) + "   prompt")
    scal = {}
    for a, bb in CONFRONTI:
        cells_a = A_cells(Ecn, byc, bases, *PAIRMAP[a], prompts)
        cells_b = A_cells(Ecn, byc, bases, *PAIRMAP[bb], prompts)
        Ga, Gb = gram_of(cells_a, prompts), gram_of(cells_b, prompts)
        line = f"    {a+' - '+bb:28s}"
        widths = []
        rec = dict(spazio=space, tipo="ampiezza_per_prompt", chi=f"{a}-{bb}")
        for k in kgrid:
            ws = []
            allc = list(itertools.combinations(range(len(prompts)), k))
            pick = ([allc[i] for i in RNG.choice(len(allc), 24, replace=False)]
                    if len(allc) > 24 else allc)
            for sub in pick:
                ii = np.array(sub)
                lo, hi = boot_ci(Ga[np.ix_(ii, ii)], Gb[np.ix_(ii, ii)], k, 3000)
                ws.append(hi - lo)
            widths.append(float(np.mean(ws)))
            rec[f"prompt_{k}"] = round(widths[-1], 5)
            line += f"{widths[-1]:>9.3f}"
        print(line)
        out_rows.append(rec)
        scal[(a, bb)] = (widths, coh(Ga) - coh(Gb))

    print("\n    Quanti prompt servirebbero perche' l'IC95 non contenga lo zero")
    print("    (ampiezza ~ 1/sqrt(P), stima dal punto a 7):\n")
    P = len(prompts)
    print(f"    {'confronto':28s}{'d':>9s}{'h a '+str(P):>9s}{'esp.':>7s}"
          f"{'P con 0.5':>11s}{'P con esp.':>12s}")
    for (a, bb), (w, obs) in scal.items():
        half = w[-1] / 2
        if obs <= 0:
            print(f"    {a+' - '+bb:28s}  punto stimato <= 0, nessuna proiezione")
            continue
        # esponente misurato: ampiezza ~ P^-alpha. La teoria dice 0.5; se esce
        # molto piu' alto, sospettare i sottoinsiemi prima di crederci.
        kk = np.array(kgrid[len(kgrid)//3:], dtype=float)
        yy = np.array(w[len(kgrid)//3:], dtype=float)
        alpha = float(-np.polyfit(np.log(kk), np.log(yy), 1)[0])
        n05 = P * (half / obs) ** 2
        na = P * (half / obs) ** (1.0 / alpha)
        print(f"    {a+' - '+bb:28s}{obs:>+9.3f}{half:>9.3f}{alpha:>7.2f}"
              f"{n05:>11.0f}{na:>12.0f}")
        out_rows.append(dict(spazio=space, tipo="proiezione", chi=f"{a}-{bb}",
                             tutti=round(obs, 4), vecchi=round(half, 4),
                             nuovi=round(float(n05), 1), esponente=round(alpha, 3),
                             P_con_esponente=round(float(na), 1)))

    # ogni tabella stampata finisce anche qui: nello Stage 4 la sezione degli
    # attributi e' andata persa nello scroll, e non deve piu' succedere
    head = ["spazio", "tipo", "chi", "tutti", "vecchi", "nuovi"]
    ks = head + sorted({k for r in out_rows for k in r} - set(head))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ks, restval="")
        w.writeheader(); w.writerows(out_rows)
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
