#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
block_sweep_maps.py — dove agisce ogni blocco, misurato sui pixel.

COSA PRODUCE, per ogni slot
  1. mappa di differenza media  |render(dose) - baseline|, mediata su prompt e seed
  2. il PAVIMENTO DI RUMORE della stessa mappa, dai soli baseline a seed diversi
  3. la mappa ripulita: solo i pixel che superano il pavimento
  4. la curva dose-risposta: quanta area supera il pavimento, al crescere della dose
  5. lo SPOSTAMENTO DI COMPOSIZIONE per dose, che dice fino a che dose le mappe valgono
  6. una gif della rampa

PERCHE' IL PAVIMENTO DI RUMORE E' OBBLIGATORIO
  `euler_ancestral` inietta rumore nuovo a ogni passo. Una perturbazione minima dei pesi
  puo' far prendere al campionatore una decisione diversa e riorganizzare un bordo intero:
  quella differenza e' reale nei pixel ma non dice niente su DOVE agisce il blocco. Senza
  un pavimento, la mappa mostra soprattutto dove l'immagine si e' riorganizzata per caso.
  Il pavimento si costruisce dalle differenze fra baseline a seed diversi: e' quanto due
  render dello stesso prompt differiscono quando NESSUN peso e' stato toccato.

PERCHE' LO SPOSTAMENTO DI COMPOSIZIONE VA SORVEGLIATO
  Una differenza per pixel ha senso solo se le due immagini sono spazialmente confrontabili.
  Quando la dose cresce la composizione si sposta — su Krea-2 l'ingrandimento del soggetto e'
  misurato a rho = 1.22 — e da quel punto in poi la mappa misura "il soggetto si e' mosso",
  non "questa regione e' cambiata". Lo script stima lo spostamento con la correlazione di
  fase e segnala la dose oltre la quale le mappe non sono piu' interpretabili.

USO
  python block_sweep_maps.py --renders <cartella> --out <cartella> [--gif]

  Nomi file attesi:
      <prompt>_<slot><segno>_<dose>_<modello>_seed<seed>_00001_.png
      <prompt>_baseline_<modello>_seed<seed>_00001_.png
  esempi:  A01_Block_3pos_0.080_krea2_seed42_00001_.png
           A01_baseline_krea2_seed42_00001_.png
"""
import argparse, os, re, sys, json
from collections import defaultdict
import numpy as np

try:
    from PIL import Image
except ImportError:
    sys.exit("Serve Pillow:  pip install pillow")

RE_COND = re.compile(r"^(?P<prompt>[A-Za-z0-9]+)_(?P<slot>[A-Za-z0-9_]+?)(?P<sign>pos|neg)_"
                     r"(?P<dose>[0-9.]+)_(?P<model>[A-Za-z0-9]+)_seed(?P<seed>\d+)_")
RE_BASE = re.compile(r"^(?P<prompt>[A-Za-z0-9]+)_baseline_(?P<model>[A-Za-z0-9]+)_seed(?P<seed>\d+)_")

DOWN = 4              # riduzione delle mappe: 1024x1280 -> 256x320
NULL_PERCENTILE = 99  # percentile del null che definisce la soglia


def load_gray(path, down=DOWN):
    im = Image.open(path).convert("L")
    if down > 1:
        im = im.resize((im.size[0] // down, im.size[1] // down), Image.BOX)
    return np.asarray(im, dtype=np.float32) / 255.0


def phase_shift(a, b):
    """Spostamento rigido stimato con correlazione di fase, in pixel della mappa ridotta."""
    A = np.fft.rfft2(a - a.mean())
    B = np.fft.rfft2(b - b.mean())
    R = A * np.conj(B)
    m = np.abs(R)
    R = np.divide(R, m, out=np.zeros_like(R), where=m > 1e-12)
    c = np.fft.irfft2(R, s=a.shape)
    p = np.unravel_index(np.argmax(c), c.shape)
    dy = p[0] if p[0] <= a.shape[0] // 2 else p[0] - a.shape[0]
    dx = p[1] if p[1] <= a.shape[1] // 2 else p[1] - a.shape[1]
    return float(np.hypot(dx, dy))


def scan(folder):
    base, cond = defaultdict(dict), defaultdict(lambda: defaultdict(dict))
    for f in sorted(os.listdir(folder)):
        if not f.lower().endswith(".png"):
            continue
        m = RE_BASE.match(f)
        if m:
            g = m.groupdict()
            base[(g["model"], g["prompt"])][g["seed"]] = os.path.join(folder, f)
            continue
        m = RE_COND.match(f)
        if m:
            g = m.groupdict()
            key = (g["model"], g["slot"] + g["sign"], float(g["dose"]))
            cond[key][(g["prompt"], g["seed"])] = os.path.join(folder, f)
    return base, cond


def noise_floor(base, model, down=DOWN):
    """Null costruito con LO STESSO ESTIMATORE del segnale.

    Il segnale e' una media di |condizione - baseline| su piu' coppie prompt/seed.
    Il null deve avere la stessa forma, altrimenti si confrontano quantita' con
    dispersioni diverse: una media di k campioni contro un percentile di campioni
    singoli produce un confronto privo di significato, e la frazione di pixel
    "sopra soglia" diventa un numero sul rumore invece che sull'effetto.

    Quindi: D_null = media su prompt di |baseline(seed a) - baseline(seed b)|,
    e la soglia e' un percentile alto della distribuzione dei pixel di D_null.
    Soglia scalare e non per pixel: con pochi seed un null per pixel e' esso stesso
    cosi' rumoroso da lasciar passare una frazione arbitraria di pixel.
    """
    per_prompt = []
    n_seeds = []
    for (mdl, prompt), seeds in base.items():
        if mdl != model or len(seeds) < 2:
            continue
        n_seeds.append(len(seeds))
        paths = list(seeds.values())
        imgs = [load_gray(p, down) for p in paths]
        pair = [np.abs(imgs[i] - imgs[j])
                for i in range(len(imgs)) for j in range(i + 1, len(imgs))]
        per_prompt.append(np.mean(np.stack(pair), axis=0))
    if not per_prompt:
        return None, None, 0
    d_null = np.mean(np.stack(per_prompt), axis=0)
    thr = float(np.percentile(d_null, NULL_PERCENTILE))
    return d_null, thr, min(n_seeds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--down", type=int, default=DOWN)
    ap.add_argument("--gif", action="store_true")
    ap.add_argument("--regions", help="JSON {prompt: {nome_regione: [x0,y0,x1,y1]}} in frazioni "
                                      "dell'immagine (0-1). Se presente, il riepilogo riporta "
                                      "la frazione di area sopra soglia DENTRO ogni regione.")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    regions = json.load(open(a.regions, encoding="utf-8")) if a.regions else {}
    if regions:
        print(f"regioni dichiarate per {len(regions)} prompt: "
              f"{ {p: list(r) for p, r in regions.items()} }")

    base, cond = scan(a.renders)
    if not base:
        sys.exit("Nessun baseline trovato: controlla i nomi dei file.")
    models = sorted({m for m, _ in base})
    print(f"modelli: {models}   baseline: {len(base)} combinazioni prompt/modello   "
          f"condizioni: {len(cond)}")

    rows = []
    for model in models:
        d_null, thr, min_seeds = noise_floor(base, model, a.down)
        if d_null is None:
            print(f"[{model}] SALTATO: servono almeno 2 seed di baseline per prompt")
            continue
        print(f"\n[{model}] null da rumore di seed: mediana {np.median(d_null):.4f}, "
              f"soglia al {NULL_PERCENTILE}o pct = {thr:.4f}   (seed per prompt: {min_seeds})")
        if min_seeds < 3:
            print(f"[{model}] ATTENZIONE: con {min_seeds} seed il null poggia su una sola "
                  f"coppia per prompt ed e' instabile. Tre seed lo rendono affidabile.")
        np.save(os.path.join(a.out, f"{model}_null_map.npy"), d_null)

        keys = sorted([k for k in cond if k[0] == model], key=lambda k: (k[1], k[2]))
        by_slot = defaultdict(list)
        for k in keys:
            by_slot[k[1]].append(k)

        for slot, ks in by_slot.items():
            frames = []
            for key in sorted(ks, key=lambda k: k[2]):
                dose = key[2]
                diffs, shifts = [], []
                by_prompt = defaultdict(list)
                for (prompt, seed), path in cond[key].items():
                    bp = base.get((model, prompt), {}).get(seed)
                    if bp is None:
                        continue
                    b = load_gray(bp, a.down)
                    x = load_gray(path, a.down)
                    d = np.abs(x - b)
                    diffs.append(d)
                    by_prompt[prompt].append(d)
                    shifts.append(phase_shift(b, x))
                if not diffs:
                    continue
                D = np.mean(np.stack(diffs), axis=0)
                above = D > thr
                frac = float(above.mean())
                shift = float(np.mean(shifts))
                reg_stats = {}
                for prompt, ds in by_prompt.items():
                    for name, box in regions.get(prompt, {}).items():
                        Dp = np.mean(np.stack(ds), axis=0)
                        H, W = Dp.shape
                        x0, y0, x1, y1 = box
                        sub = Dp[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
                        if sub.size:
                            reg_stats[f"{prompt}:{name}"] = round(float((sub > thr).mean()), 4)

                rows.append(dict(model=model, slot=slot, dose=dose,
                                 n_pairs=len(diffs), null_threshold=round(thr, 5),
                                 mean_abs_diff=float(D.mean()),
                                 frac_above_floor=frac,
                                 composition_shift_px=shift,
                                 maps_interpretable=bool(shift <= 2.0),
                                 **reg_stats))
                np.save(os.path.join(a.out, f"{model}_{slot}_{dose:.3f}_diff.npy"), D)
                if a.gif:
                    v = np.clip(D * above / max(D.max(), 1e-6), 0, 1)
                    frames.append(Image.fromarray((v * 255).astype(np.uint8)))
            if a.gif and len(frames) > 1:
                g = os.path.join(a.out, f"{model}_{slot}_ramp.gif")
                frames[0].save(g, save_all=True, append_images=frames[1:],
                               duration=400, loop=0)

    if not rows:
        sys.exit("Nessuna coppia condizione/baseline appaiata. Controlla i nomi dei file.")

    import csv
    out_csv = os.path.join(a.out, "sweep_summary.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        cols = list(rows[0])
        for r in rows:
            for c in r:
                if c not in cols:
                    cols.append(c)
        w = csv.DictWriter(f, fieldnames=cols, restval="")
        w.writeheader(); w.writerows(rows)

    print(f"\n{'='*86}")
    print(f"{'modello':<8}{'slot':<16}{'dose':>7}{'|diff|':>9}{'area>soglia':>13}"
          f"{'shift px':>10}  mappe")
    print(f"{'='*86}")
    for r in rows:
        flag = "ok" if r["maps_interpretable"] else "NON INTERPRETABILI (composizione mossa)"
        print(f"{r['model']:<8}{r['slot']:<16}{r['dose']:>7.3f}{r['mean_abs_diff']:>9.4f}"
              f"{r['frac_above_floor']:>13.1%}{r['composition_shift_px']:>10.1f}  {flag}")
        regs = {k: v for k, v in r.items() if ":" in k}
        if regs:
            top = sorted(regs.items(), key=lambda kv: -kv[1])[:4]
            print("        per regione: " + "   ".join(f"{k.split(':')[1]} {v:.0%}" for k, v in top))
    print(f"\nscritto {out_csv}")
    print("Le mappe .npy sono in scala di grigi ridotta di "
          f"{a.down}x; rileggerle con numpy.load per qualunque analisi successiva.")


if __name__ == "__main__":
    main()
