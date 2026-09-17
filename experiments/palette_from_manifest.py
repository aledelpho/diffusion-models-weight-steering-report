# -*- coding: utf-8 -*-
"""
experiments/palette_from_manifest.py
Misura la palette di uno stage intero leggendo il suo manifesto.

PERCHE' NON BASTA PUNTARE analyze_palette.py ALLA CARTELLA. I render degli stage
stanno tutti piatti dentro `renders/` con nomi come `G1_preset_pos_seed42_00001_.png`.
Da quel nome si ricava l'etichetta di comodo `G1`, non il prompt_sha1: l'hash sta
nel manifesto. Ricostruire l'identita' dal nome del file significa inventarla, e
un CSV con identita' inventata non e' verificabile -- e' la stessa ragione per cui
esiste palette_stage4_baseline.py, generalizzata a tutte le condizioni.

Il manifesto porta anche cond_name, seed e prompt_text: si prendono da li', e si
verifica che il seed scritto nel manifesto coincida con quello nel nome del file.
Se non coincidono lo script si ferma, perche' un disallineamento fra i due
significa che l'appaiamento per seed -- su cui poggia ogni contrasto -- e' rotto.

USO
    python palette_from_manifest.py \
        --manifest .../stage7_images.csv \
        --renders-root "C:\...\output\benchmark_stage7" \
        --out palette_features_stage7.csv \
        --source-csv palette_features_stage7.csv
"""
import os, csv, argparse, hashlib
from analyze_palette import palette_features


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--renders-root", required=True,
                    help="cartella rispetto a cui image_path e' relativo")
    ap.add_argument("--out", required=True)
    ap.add_argument("--source-csv", default=None,
                    help="valore della colonna source_csv; default: il nome di --out")
    ap.add_argument("--conditions", default=None,
                    help="elenco separato da virgole; default: tutte quelle nel manifesto")
    args = ap.parse_args()
    source = args.source_csv or os.path.basename(args.out)
    keep = set(args.conditions.split(",")) if args.conditions else None

    man = list(csv.DictReader(open(args.manifest, encoding="utf-8")))
    need = {"image_path", "cond_name", "prompt_sha1", "seed"}
    missing_cols = need - set(man[0])
    if missing_cols:
        raise SystemExit(f"il manifesto non ha le colonne {sorted(missing_cols)}")

    rows, absent, mismatch = [], [], []
    seen = set()
    for r in man:
        cond = r["cond_name"]
        if keep and cond not in keep:
            continue
        ip = r["image_path"].strip()
        key = (r["prompt_sha1"], cond, r["seed"])
        if key in seen:      # il manifesto elenca una riga per contrasto, non per file
            continue
        seen.add(key)
        path = os.path.join(args.renders_root, ip.replace("/", os.sep))
        if not os.path.isfile(path):
            absent.append(path); continue
        stem = os.path.splitext(os.path.basename(path))[0]
        parts = stem.split("_")
        fseed = next((p[4:] for p in parts if p.startswith("seed")), None)
        if fseed is not None and fseed != r["seed"]:
            mismatch.append((os.path.basename(path), r["seed"], fseed)); continue
        row = palette_features(path)
        row.update({"condition": cond, "prompt_dir": parts[0],
                    "prompt_sha1": r["prompt_sha1"], "seed": r["seed"],
                    "rel_path": ip, "source_csv": source})
        rows.append(row)

    if mismatch:
        print(f"[manifesto] {len(mismatch)} righe con seed discordante fra manifesto e nome file.")
        for b, m, f in mismatch[:10]:
            print(f"    {b}: manifesto {m}, nome file {f}")
        raise SystemExit("l'appaiamento per seed sarebbe sbagliato: si ferma qui.")
    if absent:
        print(f"[manifesto] {len(absent)} file NON trovati -- non si scartano in silenzio:")
        for m in absent[:10]:
            print("   ", m)
        if len(absent) > 10:
            print(f"    ... e altri {len(absent)-10}")
    if not rows:
        raise SystemExit("niente elaborato: controllare --renders-root")

    # copertura: quante celle (prompt x condizione) e quanti seed ciascuna
    cov = {}
    for r in rows:
        cov.setdefault((r["prompt_sha1"], r["condition"]), set()).add(r["seed"])
    shas = sorted({k[0] for k in cov}); conds = sorted({k[1] for k in cov})
    print(f"[manifesto] {len(rows)} render, {len(shas)} prompt, {len(conds)} condizioni")
    bad = [(s, c, len(cov.get((s, c), ()))) for s in shas for c in conds
           if len(cov.get((s, c), ())) != 5]
    if bad:
        print(f"[manifesto] {len(bad)} celle senza cinque seed -- vanno guardate:")
        for s, c, k in bad[:15]:
            print(f"    {s} / {c}: {k} seed")
    else:
        print("[manifesto] tutte le celle hanno cinque seed")

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    h = hashlib.sha1(open(args.out, "rb").read()).hexdigest()[:12]
    print(f"\n-> {args.out}   sha1 {h}")


if __name__ == "__main__":
    main()
