"""
experiments/analyze_quantization.py  --  il terzo spazio: quanti colori, non quali

IL BUCO CHE CHIUDE.
Alessandro descrive l'effetto come "meno sfumature, meno colori", non come
campiture piu' piatte. Sono cose diverse e nessuno dei due spazi costruiti finora
puo' vederla:
  - la normalizzazione LAB, introdotta dopo Block_6, cancella la dominante ma
    insieme a quella cancella anche la distribuzione del colore;
  - lo spazio del tratto lavora su sola luminanza, quindi il colore non c'e'
    proprio.
Block_6 era una trappola sulla DOMINANTE, cioe' su QUALI colori. Il numero di
colori e' un'altra cosa, ed e' invariante alla dominante: si puo' misurare DOPO
aver riallineato il cast, che e' esattamente quello che si fa qui. Avevo buttato
via due cose quando ne bastava una.

COSA MISURA. Ogni immagine viene prima riallineata in media e deviazione LAB alla
propria baseline -- quindi nessuna dominante puo' entrare nel punteggio -- e poi:

  A. quanti colori   numero efficace di colori (esponenziale dell'entropia
                     dell'istogramma LAB quantizzato) e quota cumulata dei primi
                     4, 8, 16, 32: la firma della posterizzazione.
  B. quante sfumature  istogramma della magnitudine del gradiente di crominanza.
                     Una transizione morbida popola le bande di mezzo; una
                     campitura cel ha o zero o un salto, e le bande di mezzo si
                     svuotano. E' letteralmente "meno sfumature".
  C. quanta croma    istogramma della croma e numero di modi della tinta.

Stessa decomposizione S/A, stesso null a permutazione di segno, stesso bootstrap
appaiato degli altri due spazi. Zero immagini nuove.
"""

import os
import sys
import csv
import glob
import collections
import itertools
import numpy as np
import cv2
from skimage import color

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_texture import COND, PAIRS, CSV_IN, CSV_BASE, DIRS, b
from analyze_stage5 import color_match

ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
NPZ = os.path.join(ROOT, "_stage5_quant.npz")
OUT = os.path.join(ROOT, "quantization_sa.csv")
CONFRONTI = [("preset", "randsign"), ("preset", "blockshuffle"), ("blockshuffle", "randsign")]
N_BOOT, N_PERM = 20000, 10000
RNG = np.random.default_rng(20260914)

TOPK = [4, 8, 16, 32]
CHROMA_BINS = [0, 4, 8, 14, 22, 32, 48, 1e9]
GRAD_BINS = [0, .5, 1.5, 3, 6, 12, 24, 1e9]


def names():
    n = ["effective_colours_log"] + [f"top_share_{k}" for k in TOPK]
    n += [f"gradation_grad_{i}" for i in range(len(GRAD_BINS) - 1)]
    n += [f"chroma_{i}" for i in range(len(CHROMA_BINS) - 1)]
    n += ["chroma_mean", "chroma_std", "hue_n_modes", "flat_colour_area"]
    return n


NAMES = names()


def quant_features(rgb01):
    lab = color.rgb2lab(rgb01)
    L, a, bb = lab[..., 0], lab[..., 1], lab[..., 2]

    # A. quanti colori -- griglia grossolana, cosi' conta la POSTERIZZAZIONE e non
    # il rumore di quantizzazione a 8 bit
    q = (np.clip(L / 100 * 15, 0, 15).astype(np.int32) * 256 +
         np.clip((a + 128) / 256 * 15, 0, 15).astype(np.int32) * 16 +
         np.clip((bb + 128) / 256 * 15, 0, 15).astype(np.int32))
    cnt = np.bincount(q.ravel(), minlength=4096).astype(np.float64)
    p = cnt / cnt.sum()
    nz = p[p > 0]
    f = [float(np.log(np.exp(-np.sum(nz * np.log(nz))) + 1e-9))]
    srt = np.sort(p)[::-1]
    f += [float(srt[:k].sum()) for k in TOPK]

    # B. quante sfumature -- gradiente della crominanza, non della luminanza:
    # il tratto vive in L, la sfumatura di colore in (a,b)
    ga = cv2.magnitude(cv2.Sobel(a.astype(np.float32), cv2.CV_32F, 1, 0, 3),
                       cv2.Sobel(a.astype(np.float32), cv2.CV_32F, 0, 1, 3))
    gb = cv2.magnitude(cv2.Sobel(bb.astype(np.float32), cv2.CV_32F, 1, 0, 3),
                       cv2.Sobel(bb.astype(np.float32), cv2.CV_32F, 0, 1, 3))
    g = np.hypot(ga, gb)
    h, _ = np.histogram(g, bins=GRAD_BINS)
    f += list(h / g.size)

    # C. quanta croma
    C = np.hypot(a, bb)
    h, _ = np.histogram(C, bins=CHROMA_BINS)
    f += list(h / C.size)
    f += [float(C.mean()), float(C.std())]
    hue = (np.degrees(np.arctan2(bb, a)) + 360) % 360
    hh, _ = np.histogram(hue[C > 6], bins=36, range=(0, 360))
    sm = np.convolve(hh.astype(float), np.ones(3) / 3, mode="same")
    modi = int(np.sum((sm[1:-1] > sm[:-2]) & (sm[1:-1] > sm[2:]) & (sm[1:-1] > sm.max() * 0.15)))
    k = 9
    mu = cv2.blur(C.astype(np.float32), (k, k))
    sdv = np.sqrt(np.maximum(cv2.blur((C ** 2).astype(np.float32), (k, k)) - mu * mu, 0))
    f += [float(modi), float((sdv < 1.5).mean())]
    return np.array(f, dtype=np.float32)


def main():
    idx = {}
    for d in DIRS:
        if os.path.isdir(d):
            for p in glob.glob(os.path.join(d, "*.png")):
                idx.setdefault(b(p), p)

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

    conds = [c for _n, x, y in PAIRS for c in (x, y) if c in byc]
    prompts = sorted({p for c in conds for p, _s in byc[c]})
    prompts = [p for p in prompts
               if all(sum(1 for pp, _s in byc[c] if pp == p) >= 5 for c in conds)]
    print(f"[quant] {len(prompts)} prompt completi, {len(NAMES)} feature")

    Q = {}
    if os.path.exists(NPZ):
        z = np.load(NPZ, allow_pickle=True)
        Q = {k: z[k] for k in z.files if k != "__names__"}
        print(f"[quant] cache: {len(Q)}")

    def rgb(rel):
        img = cv2.imread(idx[b(rel)], cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(rel)
        return img[:, :, ::-1].astype(np.float32) / 255.0

    todo = [(c, k, v) for c in conds for k, v in byc[c].items()
            if k[0] in prompts and b(v) not in Q]
    todo += [(None, k, v) for k, v in bases.items() if k[0] in prompts and b(v) not in Q]
    if todo:
        print(f"[quant] da calcolare: {len(todo)}")
        bc = {}
        for n, (_c, k, rel) in enumerate(todo, 1):
            if k not in bc:
                bc[k] = rgb(bases[k])
            im = rgb(rel)
            # il cast se ne va PRIMA: cosi' resta il numero di colori, non quali
            Q[b(rel)] = quant_features(color_match(im, bc[k]) if rel != bases[k] else im)
            if n % 25 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)}")
        np.savez_compressed(NPZ, __names__=np.array(NAMES), **Q)
        print(f"[quant] cache scritta -> {NPZ}")

    keys = sorted(Q)
    M = np.stack([Q[k] for k in keys])
    mu, sd = M.mean(0), M.std(0)
    sd[sd < 1e-9] = 1.0
    E = {k: (Q[k] - mu) / sd for k in keys}

    P = len(prompts)
    iu = np.triu_indices(P, 1)
    sg = RNG.choice([-1.0, 1.0], size=(N_PERM, P))
    out, G, vals = [], {}, {}
    print("\n" + "=" * 82)
    print("  QUANTIZZAZIONE DEL COLORE  (dominante gia' rimossa)")
    print("=" * 82)
    print(f"\n  {'pair':14s}{'|A|':>8s}{'|A|/|S|':>9s}{'cos(+,-)':>10s}"
          f"{'A coherence':>13s}{'null p95':>10s}{'p':>9s}")
    for name, cp, cn in PAIRS:
        ks = [k for k in byc[cp] if k in byc[cn] and k[0] in prompts]
        dp = np.stack([E[b(byc[cp][k])] - E[b(bases[k])] for k in ks])
        dnn = np.stack([E[b(byc[cn][k])] - E[b(bases[k])] for k in ks])
        S, A = (dp + dnn) / 2, (dp - dnn) / 2
        cospm = float(np.mean(np.sum(dp * dnn, 1) / (np.linalg.norm(dp, axis=1) *
                                                     np.linalg.norm(dnn, axis=1) + 1e-12)))
        g = collections.defaultdict(list)
        for v, (p, _s) in zip(A, ks):
            g[p].append(v)
        Mp = np.stack([np.mean(g[p], axis=0) for p in prompts])
        Mp = Mp / (np.linalg.norm(Mp, axis=1, keepdims=True) + 1e-12)
        G[name] = Mp @ Mp.T
        vals[name] = float(G[name][iu].mean())
        nullp = np.array([float(np.mean((np.outer(v, v) * G[name])[iu])) for v in sg])
        pv = float((np.sum(nullp >= vals[name]) + 1) / (N_PERM + 1))
        ns, na = float(np.mean(np.linalg.norm(S, axis=1))), float(np.mean(np.linalg.norm(A, axis=1)))
        print(f"  {name:14s}{na:>8.3f}{na/ns:>9.3f}{cospm:>+10.3f}{vals[name]:>+12.3f}"
              f"{np.percentile(nullp, 95):>+10.3f}{pv:>9.4f}")
        out.append(dict(key=name, coherence=round(vals[name], 4), p=round(pv, 5),
                        A=round(na, 4), ratio=round(na / ns, 4), cos_pm=round(cospm, 4)))

    def take(Gx, t):
        k = len(t)
        sub = Gx[np.ix_(t, t)]
        i2 = np.triu_indices(k, 1)
        same = t[:, None] == t[None, :]
        v = sub[i2][~same[i2]]
        return float(v.mean()) if v.size else np.nan

    print(f"\n  differenze (bootstrap appaiato sui {P} prompt)")
    for a, bb2 in CONFRONTI:
        dr = np.empty(N_BOOT)
        for i in range(N_BOOT):
            t = RNG.integers(0, P, P)
            dr[i] = take(G[a], t) - take(G[bb2], t)
        dr = dr[~np.isnan(dr)]
        lo, hi = np.percentile(dr, [2.5, 97.5])
        print(f"    {a:12s} - {bb2:12s}{vals[a]-vals[bb2]:>+8.3f}   "
              f"IC95 [{lo:+.3f}, {hi:+.3f}]   P(<=0) {np.mean(dr <= 0):.4f}")
        out.append(dict(key=f"{a}-{bb2}", coherence=round(vals[a] - vals[bb2], 4),
                        p=round(float(np.mean(dr <= 0)), 5),
                        A="", ratio=f"CI[{lo:+.3f},{hi:+.3f}]", cos_pm=""))

    print("\n" + "=" * 82)
    print("  WHICH DIMENSIONS  (loading of the A direction)")
    print("=" * 82)
    for name, cp, cn in PAIRS:
        ks = [k for k in byc[cp] if k in byc[cn] and k[0] in prompts]
        g = collections.defaultdict(list)
        for k in ks:
            g[k[0]].append((E[b(byc[cp][k])] - E[b(byc[cn][k])]) / 2)
        Mp = np.stack([np.mean(g[p], axis=0) for p in prompts])
        Mp = Mp / (np.linalg.norm(Mp, axis=1, keepdims=True) + 1e-12)
        med = np.median(Mp, 0)
        med = med / (np.linalg.norm(med) + 1e-12)
        o = np.argsort(-np.abs(med))[:6]
        print(f"  {name:14s}" + ", ".join(f"{NAMES[i]} {med[i]:+.2f}" for i in o))
        for i in o:
            out.append(dict(key=f"loading|{name}|{NAMES[i]}",
                            coherence=round(float(med[i]), 4), p="", A="",
                            ratio="", cos_pm=""))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["key", "coherence", "p", "A", "ratio", "cos_pm"])
        w.writeheader(); w.writerows(out)
    print(f"\n-> {OUT}\n-> {NPZ}")


if __name__ == "__main__":
    main()
