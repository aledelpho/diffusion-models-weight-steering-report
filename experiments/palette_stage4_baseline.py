# -*- coding: utf-8 -*-
"""
experiments/palette_stage4_baseline.py
Recupera le righe baseline mancanti dello stage 4, senza generare nuovi render.

PERCHE' MANCAVANO. palette_features_stage4_preset.csv contiene sette condizioni e
nessuna riga 'baseline', percio' i suoi quattro prompt non producono vettori
differenza e restano fuori dall'analisi di coerenza. Ma i render baseline
ESISTONO: stage4_images.csv ha una colonna `baseline_path` e vi compaiono venti
file distinti, quattro prompt per cinque seed. Non serve la GPU, serve leggerli.

PERCHE' NON SI RICAVA IL prompt_sha1 DAL NOME DEL FILE. Il nome dice `F1`, che e'
un'etichetta di comodo, non l'hash del prompt. L'associazione F1 -> sha1 sta nel
manifesto, e si prende da li': un hash indovinato da un prefisso e' esattamente
il tipo di identita' inventata che rende un CSV non verificabile.

USO
    python palette_stage4_baseline.py \
        --manifest .../data/stage4_images.csv \
        --renders-root <cartella che contiene renders/> \
        --out palette_features_stage4_baseline.csv

Poi si riunisce con gli altri, aggiungendo la colonna source_csv come negli altri
file, e si rilancia analyze_palette_coherence.py: i prompt usabili passano da 14 a 18.
"""
import os, csv, argparse
from collections import OrderedDict
from analyze_palette import palette_features, N_SWATCH   # stessa identica misura


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="stage4_images.csv")
    ap.add_argument("--renders-root", required=True,
                    help="cartella rispetto a cui baseline_path e' relativo")
    ap.add_argument("--out", required=True)
    ap.add_argument("--source-csv", default="palette_features_stage4_preset.csv",
                    help="valore da scrivere nella colonna source_csv")
    args = ap.parse_args()

    man = list(csv.DictReader(open(args.manifest, encoding="utf-8")))
    # baseline_path -> prompt_sha1, preso dal manifesto e non dal nome del file
    want = OrderedDict()
    for r in man:
        bp = r.get("baseline_path", "").strip()
        if not bp:
            continue
        sha = r["prompt_sha1"]
        if bp in want and want[bp] != sha:
            raise SystemExit(f"{bp} associato a due sha1 diversi: {want[bp]} e {sha}. "
                             f"Il manifesto e' incoerente, va guardato.")
        want[bp] = sha
    print(f"[stage4] {len(want)} baseline distinti nel manifesto")

    rows, missing = [], []
    for bp, sha in want.items():
        path = os.path.join(args.renders_root, bp.replace("/", os.sep))
        if not os.path.isfile(path):
            missing.append(path); continue
        base = os.path.basename(path)
        stem = os.path.splitext(base)[0]
        parts = stem.split("_")
        prompt_dir = parts[0]
        seed = next((p[4:] for p in parts if p.startswith("seed")), "")
        if not seed:
            raise SystemExit(f"{base}: nessun segmento 'seed<N>' nel nome, "
                             f"l'appaiamento per seed sarebbe impossibile.")
        row = palette_features(path)            # senza images_root: identita' a mano
        row.update({"condition": "baseline", "prompt_dir": prompt_dir,
                    "prompt_sha1": sha, "seed": seed, "rel_path": bp,
                    "source_csv": args.source_csv})
        rows.append(row)

    if missing:
        print(f"[stage4] {len(missing)} file NON trovati -- non si scartano in silenzio:")
        for m in missing[:10]:
            print("   ", m)
        if len(missing) > 10:
            print(f"    ... e altri {len(missing)-10}")
    if not rows:
        raise SystemExit("nessun baseline elaborato: controllare --renders-root")

    seeds_per_prompt = {}
    for r in rows:
        seeds_per_prompt.setdefault(r["prompt_sha1"], set()).add(r["seed"])
    print(f"[stage4] {len(rows)} righe, {len(seeds_per_prompt)} prompt")
    for sha, s in sorted(seeds_per_prompt.items()):
        print(f"    {sha}  {len(s)} seed: {', '.join(sorted(s))}")

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\n-> {args.out}")
    print("Poi: concatenare a palette_features_all.csv tenendo lo stesso ordine di colonne,")
    print("e rilanciare analyze_palette_coherence.py --features palette_features_all.csv")


if __name__ == "__main__":
    main()
