# -*- coding: utf-8 -*-
"""
experiments/select_confirmation_prompts.py
Sceglie i 16 prompt di conferma fra i 24 candidati, leggendo SOLO i baseline.

E' l'emendamento 1 della pre-registrazione, messo in codice cosi' che la scelta
non passi da un giudizio. Il criterio originale -- "almeno quattro prompt nei
freddi" -- riguardava la tinta del RENDER, che non si conosce prima di
renderizzare. Qui i ventiquattro candidati si renderizzano al solo baseline, si
misura la tinta, e la selezione e' una regola deterministica.

PERCHE' QUESTA SELEZIONE NON E' UN TRUCCO. Guarda esclusivamente i baseline e
mai una condizione. L'effetto in esame e' una DIFFERENZA dal baseline: scegliere
sui baseline non puo' selezionare la direzione o l'ampiezza di quella differenza.
Il pareggio si rompe con prompt_sha1 in ordine lessicografico -- non con la croma,
non con la coerenza, non con "questo mi piace" -- proprio perche' nessuna
preferenza entri dalla porta di servizio.

USO
    python select_confirmation_prompts.py --baselines palette_features_candidates.csv
"""
import csv, argparse
import numpy as np
from collections import defaultdict

ARCS = [(0, 90), (90, 180), (180, 270), (270, 360)]
PER_ARC = 4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baselines", required=True,
                    help="palette_features dei 24 candidati, sole righe baseline")
    ap.add_argument("--out", default="confirmation_prompts.csv")
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open(args.baselines, encoding="utf-8"))
            if r["condition"] == "baseline"]
    if not rows:
        raise SystemExit("nessuna riga con condition='baseline' nel file")

    per = defaultdict(list)
    for r in rows:
        per[r["prompt_sha1"]].append(r)

    hue = {}
    for sha, rs in per.items():
        # media CIRCOLARE delle tinte dei sei swatch di ogni render: 359 e 1
        # distano 2 gradi, non 358, e una media aritmetica lo sbaglierebbe
        ang = []
        for r in rs:
            for i in range(1, 7):
                ang.append(np.deg2rad(float(r[f"sw{i}_hue_deg"])))
        ang = np.array(ang)
        hue[sha] = float(np.degrees(np.arctan2(np.sin(ang).mean(),
                                               np.cos(ang).mean())) % 360.0)

    print(f"[selezione] {len(hue)} candidati, {len(rows)} render baseline")
    buckets = {a: sorted([s for s, h in hue.items() if a[0] <= h < a[1]]) for a in ARCS}
    for a in ARCS:
        print(f"    {a[0]:>3}-{a[1]:<3} : {len(buckets[a]):>2} candidati  "
              + ", ".join(f"{s}({hue[s]:.0f})" for s in buckets[a]))

    chosen, short = [], []
    for a in ARCS:
        take = buckets[a][:PER_ARC]
        chosen += take
        if len(take) < PER_ARC:
            short.append((a, PER_ARC - len(take)))

    if short:
        print("\n[selezione] archi in difetto -- si dichiara, non si aggiusta in silenzio:")
        for a, k in short:
            print(f"    {a[0]}-{a[1]}: mancano {k}")
        pool = sorted(set(hue) - set(chosen),
                      key=lambda s: (-len(buckets[next(b for b in ARCS
                                                       if b[0] <= hue[s] < b[1])]), s))
        need = sum(k for _, k in short)
        fill = pool[:need]
        print(f"    riempiti con: {', '.join(fill)}")
        chosen += fill

    chosen = sorted(chosen)
    print(f"\n[selezione] {len(chosen)} prompt scelti:")
    for s in chosen:
        print(f"    {s}   tinta media {hue[s]:6.1f}deg")
    if len(chosen) != 16:
        print(f"\n!! attesi 16, ottenuti {len(chosen)}: il pool di candidati non basta.")

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["prompt_sha1", "baseline_mean_hue_deg", "arc"])
        for s in chosen:
            a = next(b for b in ARCS if b[0] <= hue[s] < b[1])
            w.writerow([s, f"{hue[s]:.2f}", f"{a[0]}-{a[1]}"])
    print(f"\n-> {args.out}   (stage B: le 6 condizioni su questi, 5 seed, 480 render)")


if __name__ == "__main__":
    main()
