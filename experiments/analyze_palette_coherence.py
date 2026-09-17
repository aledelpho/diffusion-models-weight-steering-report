# -*- coding: utf-8 -*-
"""
experiments/analyze_palette_coherence.py
Ogni condizione ha una propria coerenza cromatica interna?

LA DOMANDA E' CAMBIATA, E VA SCRITTO PERCHE'. Le analisi precedenti chiedevano
"il preset e' diverso dal controllo?", trattando randsign come un null. Ma
l'ipotesi di Alessandro e' un'altra: OGNI spostamento dei pesi -- preset,
blockshuffle, randsign, e i rispettivi negativi -- genera una propria coerenza
cromatica. Randsign non e' l'assenza di firma: e' un'ALTRA firma. In quel
quadro un randsign che si muove non e' un fallimento del preset, e' una conferma
dell'ipotesi generale.

Le due affermazioni sono separate e vanno testate separatamente.

  (1) COERENZA INTERNA. Fissata una condizione, la direzione che imprime alla
      palette e' la stessa in prompt diversi? Misura: coseno medio a coppie fra
      le direzioni per prompt. Null: inversione di segno per prompt (esatta).

  (2) DISTINZIONE. Le condizioni si muovono in direzioni DIVERSE fra loro, o
      tutte nella stessa? Misura: coerenza dentro la condizione meno coerenza
      fra condizioni diverse, entrambe calcolate su coppie di prompt DIVERSI
      cosi' che la struttura del prompt non entri da un lato solo. Null:
      permutazione delle etichette di condizione dentro il prompt.

  (1) senza (2) non basta: se tutte le condizioni spingessero la palette nella
  stessa direzione, ognuna sarebbe "coerente" e non ci sarebbe nessuna firma.

SPAZIO DELLE FEATURE. Sei swatch piu' carta e inchiostro, ciascuno come (L*, a*,
b*), cioe' 24 dimensioni. a* e b* si ricostruiscono da C e tinta (a = C cos h,
b = C sin h) perche' la tinta in gradi e' circolare e non si puo' mediare ne'
sottrarre: 359 e 1 distano 2 gradi, non 358. Le quote di massa restano fuori:
sono composizione, non cromia.

RIFERIMENTO. Ogni vettore e' la DIFFERENZA dallo stesso prompt e dallo stesso
seed in baseline. E' la pitfall 19: su feature assolute la varianza fra soggetti
domina e si finisce per misurare "quale personaggio e' ritratto". Lo stage 4 non
ha righe baseline e percio' non entra nell'analisi primaria -- si esclude
dichiarandolo, non in silenzio.

UNITA' DI ANALISI: il prompt. I seed dentro un prompt si mediano prima (pitfall 17).
"""
import csv, os, itertools, argparse
import numpy as np
from collections import defaultdict

RANDOM_STATE = 20260917
EXACT_MAX = 16      # oltre questi prompt l'enumerazione esatta non e' praticabile
N_MC = 20000        # estrazioni Monte Carlo quando l'esatta non si puo' fare

SW = range(1, 7)


def feature_vector(r):
    """(L, a, b) per i sei swatch piu' carta e inchiostro -> 24 dimensioni."""
    v = []
    for pre in [f"sw{i}" for i in SW] + ["paper", "ink"]:
        L = float(r[f"{pre}_L"]); C = float(r[f"{pre}_C"])
        h = np.deg2rad(float(r[f"{pre}_hue_deg"]))
        v += [L, C * np.cos(h), C * np.sin(h)]
    return np.array(v)


def mean_pairwise_cos(U, V=None, exclude_diag=True):
    """Coseno medio fra righe gia' normalizzate. Con V, fra due insiemi,
    saltando le coppie con lo stesso indice di prompt."""
    if V is None:
        M = U @ U.T; iu = np.triu_indices(len(U), 1); return float(M[iu].mean())
    M = U @ V.T
    if exclude_diag:
        M = M[~np.eye(len(U), dtype=bool)]
    return float(M.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", required=True)
    ap.add_argument("--baseline", default="baseline")
    ap.add_argument("--out-matrix", default=None)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.features, encoding='utf-8')))
    stage_key = "source_csv" if "source_csv" in rows[0] else None

    cell = {}
    for r in rows:
        pid = (r.get(stage_key, ""), r["prompt_sha1"])
        cell[(pid, r["condition"], r["seed"])] = feature_vector(r)

    prompts = sorted({k[0] for k in cell})
    conds = sorted({k[1] for k in cell} - {args.baseline})

    # --- differenze appaiate per seed, poi media sui seed -> una riga per prompt
    diffs = defaultdict(dict)
    skipped = []
    for p in prompts:
        bseeds = {k[2] for k in cell if k[0] == p and k[1] == args.baseline}
        if not bseeds:
            skipped.append(p); continue
        for c in conds:
            cseeds = sorted({k[2] for k in cell if k[0] == p and k[1] == c} & bseeds)
            if not cseeds:
                continue
            diffs[c][p] = np.mean([cell[(p, c, s)] - cell[(p, args.baseline, s)]
                                   for s in cseeds], axis=0)

    if skipped:
        print(f"[coerenza] {len(skipped)} prompt ESCLUSI perche' senza '{args.baseline}':")
        for p in skipped:
            print(f"    {p[0].replace('palette_features_','').replace('.csv','')}/{p[1]}")
        print()

    # condizioni presenti in TUTTI i prompt usabili: le altre si riportano a parte
    usable = sorted({p for c in diffs for p in diffs[c]})
    full = [c for c in conds if set(diffs[c]) >= set(usable)]
    partial = [c for c in conds if c not in full]
    n = len(usable)
    print(f"[coerenza] {n} prompt, {len(full)} condizioni complete: {', '.join(full)}")
    if partial:
        for c in partial:
            print(f"[coerenza] '{c}' copre solo {len(diffs[c])} prompt: fuori dal test principale")
    # Il pavimento del p va dichiarato per il test che si USA davvero. Sopra i 16
    # prompt l'enumerazione esatta diventa impraticabile e si passa a Monte Carlo:
    # li' il p non puo' scendere sotto 1/(N+1), che e' un pavimento piu' alto di
    # quello esatto. Stampare il pavimento esatto mentre si gira in Monte Carlo
    # farebbe sembrare un limite del metodo un risultato del dato.
    exact = n <= EXACT_MAX
    floor = 2 / 2 ** n if exact else 1 / (N_MC + 1)
    print(f"[coerenza] permutazione {'esatta' if exact else f'Monte Carlo, N={N_MC}'} "
          f"su {n} prompt, p minimo ottenibile = {floor:.2e}\n")

    # --- scala: ogni dimensione per la sua SD sull'insieme delle differenze ----
    allv = np.stack([diffs[c][p] for c in full for p in usable])
    sd = allv.std(axis=0); sd[sd < 1e-9] = 1.0
    D = {c: np.stack([diffs[c][p] / sd for p in usable]) for c in full}
    U = {c: D[c] / np.linalg.norm(D[c], axis=1, keepdims=True) for c in full}

    # --- (1) coerenza interna ------------------------------------------------
    print("(1) COERENZA INTERNA -- stessa condizione, prompt diversi")
    print(f"    {'condizione':<18}{'coseno medio':>14}{'p':>12}")
    print("    " + "-" * 44)
    signs = np.array(list(itertools.product([1, -1], repeat=n))) if exact else None
    coh = {}
    for c in full:
        obs = mean_pairwise_cos(U[c]); coh[c] = obs
        if signs is not None:
            null = np.array([mean_pairwise_cos(s[:, None] * U[c]) for s in signs])
            p = float(np.mean(null >= obs - 1e-12))
        else:
            rng = np.random.default_rng(RANDOM_STATE)
            sgn = rng.choice([1, -1], size=(N_MC, n))
            null = np.array([mean_pairwise_cos(x[:, None] * U[c]) for x in sgn])
            p = float((np.sum(null >= obs - 1e-12) + 1) / (N_MC + 1))
        print(f"    {c:<18}{obs:>+14.3f}{p:>12.2e}")

    # --- (2) distinzione -----------------------------------------------------
    print("\n(2) MATRICE FRA CONDIZIONI -- coseno su coppie di prompt DIVERSI")
    print("    (diagonale = coerenza interna; ~ -1 fra pos e neg = risposta antisimmetrica)")
    hdr = "    " + " " * 18 + "".join(f"{c[:11]:>13}" for c in full)
    print(hdr)
    M = np.zeros((len(full), len(full)))
    for i, a in enumerate(full):
        line = f"    {a:<18}"
        for j, b in enumerate(full):
            M[i, j] = coh[a] if i == j else mean_pairwise_cos(U[a], U[b])
            line += f"{M[i,j]:>+13.3f}"
        print(line)

    def stat(Ustack):
        C = len(Ustack)
        w = np.mean([mean_pairwise_cos(Ustack[i]) for i in range(C)])
        o = [abs(mean_pairwise_cos(Ustack[i], Ustack[j]))
             for i in range(C) for j in range(i + 1, C)]
        return w - np.mean(o), w, float(np.mean(o))

    Us = np.stack([U[c] for c in full])
    obs, within, between = stat(Us)
    print(f"\n    coerenza interna media          {within:+.3f}")
    print(f"    |coseno| medio fra condizioni   {between:+.3f}")
    print(f"    statistica (dentro - fra)       {obs:+.3f}")
    print("    (si usa il valore assoluto fra condizioni: una coppia pos/neg a -1")
    print("     sarebbe massimamente allineata, non indipendente, e va contata come tale)")

    # NULL: si permutano le ETICHETTE di condizione DENTRO ogni prompt. Cosi' la
    # struttura del prompt e le ampiezze restano intatte e cade solo l'identita'
    # della condizione -- che e' esattamente l'ipotesi nulla che serve.
    rng = np.random.default_rng(RANDOM_STATE); N = 10000
    null = np.empty(N)
    for t in range(N):
        Up = Us.copy()
        for k in range(n):
            Up[:, k, :] = Us[rng.permutation(len(full)), k, :]
        null[t] = stat(Up)[0]
    pval = (np.sum(null >= obs - 1e-12) + 1) / (N + 1)
    print(f"    null per permutazione delle etichette (N={N}): media {null.mean():+.3f}, "
          f"p95 {np.quantile(null, .95):+.3f}  ->  p = {pval:.4f}")

    print("\n(3) AMPIEZZA dello spostamento di palette (norma del vettore scalato)")
    print("    serve a escludere che la coerenza segua semplicemente chi si muove di piu'")
    for c in full:
        print(f"    {c:<18}{np.linalg.norm(D[c], axis=1).mean():>8.2f}")

    if args.out_matrix:
        with open(args.out_matrix, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow([""] + full)
            for i, a in enumerate(full):
                w.writerow([a] + [f"{M[i,j]:.4f}" for j in range(len(full))])
        print(f"\n-> {args.out_matrix}")


if __name__ == "__main__":
    main()
