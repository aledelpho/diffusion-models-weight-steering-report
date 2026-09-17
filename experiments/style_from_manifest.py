# -*- coding: utf-8 -*-
"""
experiments/style_from_manifest.py
Feature di stile di uno stage, lette dal suo manifesto.

PERCHE' NON SI USA run_style_features.py PER LO STAGE 7 DI CONFERMA.
Quel raccoglitore legge `stage7_images.csv`, che e' il manifesto di un ALTRO
esperimento -- 228 immagini con prefisso `S7_` -- mentre la conferma sta in
`stage7b_images.csv` con prefisso `I*`. Le due serie scrivono nella STESSA
cartella, `benchmark_stage7\\renders`. Puntare il raccoglitore alla cartella, o
al manifesto sbagliato, misurerebbe l'esperimento sbagliato e non lo direbbe.

Lo script di MISURA non si tocca: le feature arrivano da
`style_features.extract_all_features`, la stessa funzione che ha prodotto
`style_features.csv` e quindi i numeri esplorativi su cui poggia la previsione.
Qui si aggiungono solo le colonne di identita' prese dal manifesto, come fa
palette_from_manifest.py, e si scrive in un file separato per non sovrascrivere
il CSV che regge le misure precedenti.

USO
    python style_from_manifest.py \
        --manifest ../stage7b_images.csv \
        --renders-root "C:\\...\\output\\benchmark_stage7\\renders" \
        --out ../style_features_stage7.csv
"""
import os, csv, argparse, hashlib
from style_features import extract_all_features


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--renders-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--also", action="append", default=[],
                    help="altro manifesto da unire (es. i baseline del tempo A); "
                         "si puo' ripetere, come 'manifesto=radice'")
    args = ap.parse_args()

    sources = [(args.manifest, args.renders_root)]
    for a in args.also:
        m, _, r = a.partition("=")
        sources.append((m, r or args.renders_root))

    rows, absent, seen = [], [], set()
    for man_path, root in sources:
        man = list(csv.DictReader(open(man_path, encoding="utf-8-sig")))
        need = {"image_path", "cond_name", "prompt_sha1", "seed"}
        if need - set(man[0]):
            raise SystemExit(f"{man_path}: mancano le colonne {sorted(need - set(man[0]))}")
        for r in man:
            key = (r["prompt_sha1"], r["cond_name"], r["seed"])
            if key in seen:
                continue
            seen.add(key)
            rel = r["image_path"].replace("/", os.sep)
            path = os.path.join(root, os.path.basename(rel))
            if not os.path.isfile(path):
                path = os.path.join(root, rel)
            if not os.path.isfile(path):
                absent.append(path); continue
            base = os.path.basename(path)
            fseed = next((p[4:] for p in os.path.splitext(base)[0].split("_")
                          if p.startswith("seed")), None)
            if fseed is not None and fseed != r["seed"]:
                raise SystemExit(f"{base}: seed {fseed} nel nome, {r['seed']} nel "
                                 f"manifesto. L'appaiamento sarebbe sbagliato.")
            feat = extract_all_features(path)
            feat.update({"condition": r["cond_name"],
                         "prompt_dir": base.split("_")[0],
                         "prompt_sha1": r["prompt_sha1"], "seed": r["seed"],
                         "rel_path": r["image_path"],
                         "source_manifest": os.path.basename(man_path)})
            rows.append(feat)

    if absent:
        print(f"[stile] {len(absent)} file NON trovati -- non si scartano in silenzio:")
        for m in absent[:10]:
            print("   ", m)
        if len(absent) > 10:
            print(f"    ... e altri {len(absent)-10}")
    if not rows:
        raise SystemExit("niente elaborato: controllare --renders-root")

    cov = {}
    for r in rows:
        cov.setdefault((r["prompt_sha1"], r["condition"]), set()).add(r["seed"])
    shas = sorted({k[0] for k in cov}); conds = sorted({k[1] for k in cov})
    print(f"[stile] {len(rows)} immagini, {len(shas)} prompt, {len(conds)} condizioni")
    bad = [(s, c) for s in shas for c in conds if len(cov.get((s, c), ())) != 5]
    print(f"[stile] celle senza cinque seed: {len(bad)}")
    for s, c in bad[:10]:
        print(f"    {s} / {c}: {len(cov.get((s,c),()))} seed")

    cols = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"\n-> {args.out}   sha1 {hashlib.sha1(open(args.out,'rb').read()).hexdigest()[:12]}")


if __name__ == "__main__":
    main()
