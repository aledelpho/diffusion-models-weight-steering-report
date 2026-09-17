# -*- coding: utf-8 -*-
"""
experiments/analyze_palette_sa.py -- decomposizione S/A sulle feature di palette

PERCHE' ESISTE QUESTO FILE. Il primo passaggio sul CSV di palette ha testato ogni
condizione contro il baseline, una per una, e non ha trovato niente. Era il
contrasto sbagliato, ed e' la pitfall 2 del log: una misura non segnata non
distingue +theta da -theta. Alessandro l'ha visto a occhio sul foglio delle
palette -- nelle direzioni positive i gradini centrali si scuriscono, nelle
negative si schiariscono -- che e' precisamente una struttura ANTISIMMETRICA,
invisibile a un contratto per condizione.

  A = (d+ - d-)/2   componente dispari: cosa fa il SEGNO dello spostamento
  S = (d+ + d-)/2   componente pari: cosa fa lo spostamento comunque orientato

dove d+ = cond_plus - baseline e d- = cond_neg - baseline, per lo stesso prompt
e lo stesso seed.

LA DOMANDA NON E' "ESISTE A?". A esiste per costruzione appena +v e -v danno
immagini diverse. La domanda e' se A del preset sia PIU' GRANDE o DIVERSO IN
DIREZIONE da A di randsign, che ha lo stesso spostamento di Frobenius e nessuna
struttura. Se non lo e', quello che si vede e' la firma del segno dello
spostamento, non della direzione scelta.

UNITA' DI ANALISI: il prompt, non il render. I seed dentro un prompt sono misure
ripetute (pitfall 17): si mediano prima, poi si conta n = numero di prompt.
"""
import csv, os, itertools, argparse
import numpy as np
from collections import defaultdict

PAIRS = {'preset': ('preset', 'preset_neg'),
         'blockshuffle': ('blockshuffle', 'blockshuffle_neg'),
         'randsign': ('randsign', 'randsign_neg')}
FEATS = ([f'sw{i}_L' for i in range(1, 7)] + [f'sw{i}_C' for i in range(1, 7)]
         + ['paper_L', 'ink_L', 'chroma_spread', 'tonal_range'])
CONTROL = 'randsign'


def perm_p(d):
    """Permutazione ESATTA a inversione di segno. Con n = 7 il p minimo e'
    2/2^7 = 0.0156: va detto, perche' un test che non puo' scendere sotto
    quella soglia non e' un test che ha fallito, e' un test che non poteva."""
    n = len(d); obs = abs(d.mean())
    sg = np.array(list(itertools.product([1, -1], repeat=n)))
    return float(np.mean(np.abs((sg * d).mean(axis=1)) >= obs - 1e-12))


def holm(ps):
    idx = np.argsort(ps); m = len(ps); out = [0.0] * m; run = 0.0
    for r, i in enumerate(idx):
        run = max(run, min(1.0, (m - r) * ps[i])); out[i] = run
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", required=True, help="palette_features_*.csv")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.features, encoding='utf-8')))
    by = defaultdict(dict)
    for r in rows:
        by[(r['prompt_sha1'], r['seed'])][r['condition']] = r

    acc = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for (_sha, _seed), v in by.items():
        for fam, (p_, n_) in PAIRS.items():
            if not all(c in v for c in ('baseline', p_, n_)):
                continue
            for f in FEATS:
                acc[fam][_sha][f].append((float(v[p_][f]) - float(v[n_][f])) / 2)

    shas = sorted(acc[CONTROL])
    A = {fam: {f: np.array([np.mean(acc[fam][s][f]) for s in shas]) for f in FEATS}
         for fam in PAIRS}
    n = len(shas)
    print(f"[S/A] {n} prompt, p minimo per permutazione esatta = {2/2**n:.4f}\n")

    tests = [(fam, f, (A[fam][f] - A[CONTROL][f]))
             for fam in PAIRS if fam != CONTROL for f in FEATS]
    ps = [perm_p(d) for _, _, d in tests]
    adj = holm(ps)
    print(f"A_condizione - A_{CONTROL}, appaiato per prompt:")
    for (fam, f, d), p, a in zip(tests, ps, adj):
        flag = '**' if a < .05 else ('*' if p < .05 else '')
        print(f"  {fam:<14}{f:<16}{d.mean():>8.2f}  p={p:.4f}  Holm={a:.3f} {flag}")
    print(f"\n  sopravvissuti a Holm su {len(tests)}: {sum(1 for a in adj if a < .05)}")

    print(f"\nAMPIEZZA di A sui sei gradini L* (norma per prompt):")
    norms = {fam: np.linalg.norm(
        np.stack([A[fam][f'sw{i}_L'] for i in range(1, 7)], axis=1), axis=1)
        for fam in PAIRS}
    for fam in PAIRS:
        if fam == CONTROL:
            print(f"  {fam:<16}{norms[fam].mean():6.2f}   (controllo)")
        else:
            d = norms[fam] - norms[CONTROL]
            print(f"  {fam:<16}{norms[fam].mean():6.2f}   delta vs controllo "
                  f"{d.mean():+.2f}, p = {perm_p(d):.4f}")


if __name__ == "__main__":
    main()
