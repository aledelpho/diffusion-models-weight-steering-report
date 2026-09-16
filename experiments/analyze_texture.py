"""
experiments/analyze_texture.py  --  lo stesso test, in uno spazio che vede il tratto

PERCHE' SERVE UN SECONDO SPAZIO.
Tutte le misure fatte finora passano da CLIP ViT-L-14, che lavora a 224x224. Le
immagini sono 1024x1280: prima ancora di calcolare qualsiasi cosa, lo spessore
del tratto e la densita' del tratteggio sono in gran parte gia' stati buttati via
dal ridimensionamento. Stavamo misurando semantica e composizione con uno
strumento cieco proprio alla dimensione che un illustratore guarda per prima.

Due immagini dello stesso prompt e dello stesso seed, una col preset e una col
blockshuffle, si leggono come DUE STILI DISTINTI: una a tratto sottile e
variabile con tratteggio fitto, campiture con gradiente e bordi morbidi; l'altra
a contorni neri spessi e uniformi, campiture piatte a scalini, crosshatch grosso
e forme semplificate. Nessuna delle due e' "l'altra degradata". La prima e' meno
"bold" di quanto il prompt chieda ma piu' da fumetto; la seconda e' molto piu'
bold ma da cartone animato. Sono due assi diversi, e CLIP non li separa.

COSA MISURA QUESTO SPAZIO. Tutto su LUMINANZA, quindi cieco al colore per
costruzione -- il che chiude nativamente la questione Block_6, senza bisogno di
riallineare niente.

  A. morfologia dell'inchiostro  -- l'asse "bold". Maschera dell'inchiostro,
     trasformata di distanza, istogramma delle mezze-larghezze: e' letteralmente
     la distribuzione dello spessore dei tratti. Piu' copertura, numero e area
     media delle componenti: molti tratti sottili contro pochi tratti grossi.
  B. piattezza delle campiture   -- l'asse "cel contro dipinto". Deviazione
     locale fuori dall'inchiostro, frazione di area piatta, numero di modi
     dell'istogramma di luminanza (la posterizzazione del cel shading).
  C. contenuto in frequenza      -- finezza del tratteggio. Spettro di potenza
     radiale in bande logaritmiche.
  D. durezza dei bordi           -- rapporto fra gradiente a scala fine e a scala
     grossa sui pixel di bordo: taglio netto contro sfumato.

E UNA SECONDA DOMANDA, che si risponde con gli stessi dati.
Se preset e blockshuffle fossero lo stesso asse a intensita' diverse, per lo
stesso soggetto le loro direzioni A sarebbero quasi parallele. Se sono due
attrattori distinti, il loro coseno deve essere paragonabile -- o piu' basso --
di quello che UNA SOLA condizione ottiene fra prompt diversi (+0.22 in CLIP).
Il confronto e' quello, non lo zero.

Zero immagini nuove: gira su quello che c'e'.
"""

import os
import sys
import csv
import glob
import collections
import itertools
import numpy as np
import cv2
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

COMFY_OUT = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"
DIRS = [os.path.join(COMFY_OUT, d, "renders") for d in
        ("benchmark_stage5", "benchmark_stage4_preset", "benchmark_stage2_family")]
ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
CSV_IN = [os.path.join(ROOT, "stage4_images.csv"), os.path.join(ROOT, "stage5_images.csv")]
CSV_BASE = [os.path.join(ROOT, "stage2_images.csv"), os.path.join(ROOT, "stage5_images.csv")]
CLIP_NPZ = os.path.join(ROOT, "_stage5_emb.npz")
TEX_NPZ = os.path.join(ROOT, "_stage5_tex.npz")
OUT_SA = os.path.join(ROOT, "texture_sa.csv")
OUT_FEAT = os.path.join(ROOT, "texture_features.csv")

COND = {
    "Arthemy_Bench_Base.json": "preset_pos", "Arthemy_Bench_NEG.json": "preset_neg",
    "Arthemy_Bench_RANDSIGN.json": "rand_pos", "Arthemy_Bench_RANDSIGN_NEG.json": "rand_neg",
    "Arthemy_Bench_BLOCKSHUFFLE.json": "blockshuf_pos",
    "Arthemy_Bench_BLOCKSHUFFLE_NEG.json": "blockshuf_neg",
}
PAIRS = [("preset", "preset_pos", "preset_neg"),
         ("blockshuffle", "blockshuf_pos", "blockshuf_neg"),
         ("randsign", "rand_pos", "rand_neg")]
PAIRMAP = {n: (a, b) for n, a, b in PAIRS}
CONFRONTI = [("preset", "randsign"), ("preset", "blockshuffle"), ("blockshuffle", "randsign")]
N_BOOT, N_PERM = 20000, 20000
RNG = np.random.default_rng(20260914)
b = os.path.basename

WIDTH_BINS = [0, 1.5, 2.5, 3.5, 5, 7, 10, 14, 1e9]   # mezze-larghezze in pixel
STD_BINS = [0, .005, .012, .025, .05, .10, 1e9]
N_FREQ = 10


def feature_names():
    n = [f"mark_width_{i}" for i in range(len(WIDTH_BINS) - 1)]
    n += ["ink_coverage", "ink_n_components", "ink_mean_area",
          "ink_width_median", "ink_width_p90"]
    n += [f"flat_std_{i}" for i in range(len(STD_BINS) - 1)]
    n += ["flat_fraction", "flat_n_modes", "flat_entropy_L"]
    n += [f"freq_band_{i}" for i in range(N_FREQ)]
    n += ["edge_hardness", "edge_contrast_p99", "edge_mean_grad"]
    return n


NAMES = feature_names()


def texture_features(bgr):
    """Tutto su luminanza: questo spazio non puo' premiare una dominante."""
    L = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    lo, hi = np.percentile(L, [1, 99])
    # float32 esplicito: np.percentile restituisce float64 e promuoverebbe Ln,
    # che poi fa fallire i filtri OpenCV con ddepth CV_32F
    Ln = np.clip((L - lo) / max(hi - lo, 1e-6), 0, 1).astype(np.float32)

    f = []

    # --- A. morfologia dell'inchiostro -------------------------------------
    ink = (Ln < 0.35).astype(np.uint8)
    dist = ndimage.distance_transform_edt(ink)          # mezza larghezza locale
    dv = dist[ink > 0]
    if dv.size:
        h, _ = np.histogram(dv, bins=WIDTH_BINS)
        f += list(h / dv.size)
        med, p90 = float(np.median(dv)), float(np.percentile(dv, 90))
    else:
        f += [0.0] * (len(WIDTH_BINS) - 1)
        med = p90 = 0.0
    n_lab, _lab, stats, _c = cv2.connectedComponentsWithStats(ink, 8)
    areas = stats[1:, cv2.CC_STAT_AREA] if n_lab > 1 else np.array([0])
    mp = ink.size / 1e6
    f += [float(ink.mean()), float((n_lab - 1) / mp),
          float(areas.mean() / 1e3), med, p90]

    # --- B. piattezza delle campiture ---------------------------------------
    k = 9
    mu = cv2.blur(Ln, (k, k))
    sd = np.sqrt(np.maximum(cv2.blur(Ln * Ln, (k, k)) - mu * mu, 0))
    fill = sd[ink == 0]
    if fill.size:
        h, _ = np.histogram(fill, bins=STD_BINS)
        f += list(h / fill.size)
        f.append(float((fill < 0.012).mean()))
    else:
        f += [0.0] * (len(STD_BINS) - 1) + [0.0]
    hist, _ = np.histogram(Ln, bins=64, range=(0, 1), density=True)
    sm = np.convolve(hist, np.ones(5) / 5, mode="same")
    modi = int(np.sum((sm[1:-1] > sm[:-2]) & (sm[1:-1] > sm[2:]) & (sm[1:-1] > sm.max() * 0.08)))
    p = hist / max(hist.sum(), 1e-9)
    f += [float(modi), float(-np.sum(p[p > 0] * np.log(p[p > 0])))]

    # --- C. contenuto in frequenza ------------------------------------------
    small = cv2.resize(Ln, (512, 640), interpolation=cv2.INTER_AREA)
    F = np.abs(np.fft.fftshift(np.fft.fft2(small - small.mean()))) ** 2
    yy, xx = np.indices(F.shape)
    r = np.hypot(yy - F.shape[0] / 2, xx - F.shape[1] / 2)
    edges = np.geomspace(2, r.max(), N_FREQ + 1)
    band = np.array([F[(r >= edges[i]) & (r < edges[i + 1])].mean() for i in range(N_FREQ)])
    # log, non frazione: lo spettro di potenza cade di ordini di grandezza, e
    # normalizzando a somma 1 la prima banda si prende tutto e le ultime quattro
    # diventano zero identico -- feature morte. In log diventa il PROFILO DI
    # PENDENZA, che e' quello che distingue un tratteggio fitto da uno rado.
    f += list(np.log10(np.maximum(band, 1e-12)))

    # --- D. durezza dei bordi ------------------------------------------------
    g1 = cv2.magnitude(cv2.Sobel(Ln, cv2.CV_32F, 1, 0, 3), cv2.Sobel(Ln, cv2.CV_32F, 0, 1, 3))
    Lb = cv2.GaussianBlur(Ln, (0, 0), 3)
    g3 = cv2.magnitude(cv2.Sobel(Lb, cv2.CV_32F, 1, 0, 3), cv2.Sobel(Lb, cv2.CV_32F, 0, 1, 3))
    thr = np.percentile(g1, 97)
    m = g1 >= thr
    # NB: il rapporto g1/g3 e' in parte confuso con lo spessore -- un tratto
    # grosso conserva meglio il gradiente sotto sfocatura, quindi scende. Va
    # letto insieme all'istogramma delle larghezze, non da solo.
    # (m.mean() sarebbe 0.03 per costruzione: era una feature morta, tolta.)
    f += [float(g1[m].mean() / max(g3[m].mean(), 1e-9)),
          float(np.percentile(g1, 99)), float(g1.mean())]

    return np.array(f, dtype=np.float32)


# ------------------------------------------------------------------ statistica

def gram(A_by_prompt, prompts):
    M = np.stack([A_by_prompt[p] for p in prompts])
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    return M @ M.T


def coh_take(G, take):
    k = len(take)
    if k < 2:
        return np.nan
    sub = G[np.ix_(take, take)]
    iu = np.triu_indices(k, 1)
    same = take[:, None] == take[None, :]
    v = sub[iu][~same[iu]]
    return float(v.mean()) if v.size else np.nan


def main():
    idx = {}
    for d in DIRS:
        if os.path.isdir(d):
            for p in glob.glob(os.path.join(d, "*.png")):
                if b(p) in idx:
                    raise RuntimeError(f"basename duplicato fra due run: {b(p)}")
                idx[b(p)] = p
    print(f"[texture] {len(idx)} immagini indicizzate")

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

    conds = [c for _n, a, bb in PAIRS for c in (a, bb) if c in byc]
    prompts = sorted({p for c in conds for p, _s in byc[c]})
    prompts = [p for p in prompts
               if all(sum(1 for pp, _s in byc[c] if pp == p) >= 5 for c in conds)]
    print(f"[texture] {len(prompts)} prompt completi: {', '.join(prompts)}")
    if len(prompts) < 4:
        raise RuntimeError("troppo pochi prompt completi")

    # --- feature del tratto, con cache ---------------------------------------
    need = sorted({v for c in conds for v in byc[c].values()} | set(bases.values()))
    T = {}
    if os.path.exists(TEX_NPZ):
        z = np.load(TEX_NPZ, allow_pickle=True)
        T = {k: z[k] for k in z.files if k != "__names__"}
        print(f"[texture] cache: {len(T)}")
    todo = [r for r in need if b(r) not in T]
    if todo:
        print(f"[texture] da calcolare: {len(todo)}  (piena risoluzione, ci vuole qualche minuto)")
        for n, rel in enumerate(todo, 1):
            img = cv2.imread(idx[b(rel)], cv2.IMREAD_COLOR)
            if img is None:
                raise FileNotFoundError(rel)
            T[b(rel)] = texture_features(img)
            if n % 25 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)}")
        np.savez_compressed(TEX_NPZ, __names__=np.array(NAMES), **T)
        print(f"[texture] cache scritta -> {TEX_NPZ}")

    # standardizzazione: le feature hanno unita' diverse, senza z-score il coseno
    # lo deciderebbe la feature con la scala piu' grande
    keys = sorted(T)
    M = np.stack([T[k] for k in keys])
    mu, sd = M.mean(0), M.std(0)
    sd[sd < 1e-9] = 1.0
    TEX = {k: (T[k] - mu) / sd for k in keys}
    morti = [NAMES[i] for i in range(len(NAMES)) if M[:, i].std() < 1e-9]
    if morti:
        print(f"[texture] feature costanti, ignorate di fatto: {morti}")

    zc = np.load(CLIP_NPZ, allow_pickle=True)
    CLIPE = {k[3:]: zc[k] for k in zc.files if k.startswith("cn|")}

    SPACES = [("CLIP (colour-normalised)", CLIPE), ("MARK (luminance)", TEX)]
    out_rows, feat_rows = [], []
    A_space = {}

    for space, E in SPACES:
        print("\n" + "=" * 82)
        print(f"  {space}")
        print("=" * 82)
        A_by, grams, stats, diag = {}, {}, {}, []
        print(f"\n  {'pair':14s}{'|S|':>8s}{'|A|':>8s}{'|A|/|S|':>9s}"
              f"{'cos(+,-)':>10s}{'A coherence':>13s}{'null p95':>10s}{'p':>9s}")
        for name, cp, cn in PAIRS:
            keysel = [k for k in byc[cp] if k in byc[cn] and k[0] in prompts]
            if not keysel:
                continue
            dp = np.stack([E[b(byc[cp][k])] - E[b(bases[k])] for k in keysel])
            dn = np.stack([E[b(byc[cn][k])] - E[b(bases[k])] for k in keysel])
            S, A = (dp + dn) / 2, (dp - dn) / 2
            cospm = float(np.mean(np.sum(dp * dn, 1) / (np.linalg.norm(dp, axis=1) *
                                                        np.linalg.norm(dn, axis=1) + 1e-12)))
            g = collections.defaultdict(list)
            for v, (p, _s) in zip(A, keysel):
                g[p].append(v)
            Ap = {p: np.mean(g[p], axis=0) for p in g}
            A_by[name] = Ap
            G = gram(Ap, prompts)
            grams[name] = G
            iu = np.triu_indices(len(prompts), 1)
            coh = float(G[iu].mean())
            sg = RNG.choice([-1.0, 1.0], size=(N_PERM, len(prompts)))
            nullp = np.array([float(np.mean((np.outer(v, v) * G)[iu])) for v in sg])
            p95 = float(np.percentile(nullp, 95))
            pval = float((np.sum(nullp >= coh) + 1) / (N_PERM + 1))
            ns, na = float(np.mean(np.linalg.norm(S, axis=1))), float(np.mean(np.linalg.norm(A, axis=1)))
            # DIAGNOSTICA DEL DIVARIO fra |A|/|S| e sqrt((1-c)/(1+c)).
            # L'identita' vale PER CELLA. Qui si riportano medie prese in ordine
            # diverso: mean(||A||)/mean(||S||) e' pesato sull'ampiezza della cella,
            # mean(cos) non lo e'. Se le celle che si spostano di piu' sono anche le
            # piu' simmetriche, il rapporto riportato scende SOTTO la formula. Non e'
            # un bug: e' una misura di quella correlazione. Si stampa invece di
            # lasciarla dedurre -- in CLIP il divario e' 0.3%, nel tratto fino al 4%.
            kk = (np.linalg.norm(dp, axis=1) + np.linalg.norm(dn, axis=1)) / 2
            cc = np.sum(dp * dn, 1) / (np.linalg.norm(dp, axis=1) *
                                       np.linalg.norm(dn, axis=1) + 1e-12)
            diag.append((name, na / ns,
                         float(np.sqrt((1 - cospm) / (1 + cospm))),
                         float(np.sum(kk * cc) / np.sum(kk)),
                         float(np.corrcoef(kk, cc)[0, 1]),
                         float(np.mean(np.linalg.norm(dp, axis=1) /
                                       (np.linalg.norm(dn, axis=1) + 1e-12)))))
            print(f"  {name:14s}{ns:>8.3f}{na:>8.3f}{na/ns:>9.3f}{cospm:>+10.3f}"
                  f"{coh:>+12.3f}{p95:>+10.3f}{pval:>9.4f}")
            stats[name] = dict(S=ns, A=na, ratio=na / ns, cos_pm=cospm, coh=coh,
                               null_p95=p95, p=pval)
            out_rows.append(dict(space=space, pair=name, n_prompts=len(prompts),
                                 **{k: round(v, 6) for k, v in stats[name].items()}))
        A_space[space] = (A_by, grams, stats)

        print(f"\n  {'pair':14s}{'|A|/|S|':>10s}{'from mean cos':>15s}{'gap':>9s}"
              f"{'cos pesato':>12s}{'corr(ampi,cos)':>16s}{'||d+||/||d-||':>15s}")
        for nm, r, f, cw, rho, asy in diag:
            print(f"  {nm:14s}{r:>10.3f}{f:>14.3f}{(r-f)/f:>+9.1%}{cw:>12.3f}{rho:>16.3f}{asy:>15.3f}")
        print("    Lo scarto e' atteso: il rapporto e' pesato sull'ampiezza, il coseno medio no.")
        print("    corr(ampiezza,cos) > 0  =>  scarto NEGATIVO, ed e' quella correlazione che si")
        print("    sta misurando: la parte pari cresce piu' in fretta dell'ampiezza.")

        print(f"\n  differenze   (bootstrap appaiato sui {len(prompts)} prompt)")
        for a, bb in CONFRONTI:
            if a not in grams or bb not in grams:
                continue
            obs = stats[a]["coh"] - stats[bb]["coh"]
            n = len(prompts)
            dr = np.empty(N_BOOT)
            for i in range(N_BOOT):
                t = RNG.integers(0, n, n)
                dr[i] = coh_take(grams[a], t) - coh_take(grams[bb], t)
            dr = dr[~np.isnan(dr)]
            lo, hi = np.percentile(dr, [2.5, 97.5])
            print(f"    {a:12s} - {bb:12s}{obs:>+8.3f}   IC95 [{lo:+.3f}, {hi:+.3f}]"
                  f"   P(<=0) {np.mean(dr <= 0):.4f}")
            out_rows.append(dict(space=space, pair=f"{a}-{bb}", n_prompts=len(prompts),
                                 coh=round(obs, 6), ic_lo=round(float(lo), 6),
                                 ic_hi=round(float(hi), 6), p=round(float(np.mean(dr <= 0)), 6)))

    # --- stesso asse, o attrattori distinti? ---------------------------------
    print("\n" + "=" * 82)
    print("  UN ASSE SOLO, O ATTRATTORI DISTINTI?")
    print("=" * 82)
    print("  Coseno fra le direzioni A di DUE condizioni sullo STESSO prompt.")
    print("  Il metro di paragone non e' lo zero: e' la coerenza che UNA condizione")
    print("  ottiene fra prompt diversi. Sopra = stesso asse a intensita' diverse.")
    print("  Sotto o pari = attrattori distinti.\n")
    for space, _E in SPACES:
        A_by, _g, stats = A_space[space]
        print(f"  {space}")
        print(f"    {'riferimento: coerenza fra prompt':44s}" +
              "".join(f"{n[:11]:>13s}" for n in A_by))
        print(f"    {'':44s}" + "".join(f"{stats[n]['coh']:>+13.3f}" for n in A_by))
        print()
        for a, bb in itertools.combinations(list(A_by), 2):
            cs = []
            for p in prompts:
                u, v = A_by[a][p], A_by[bb][p]
                cs.append(float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-12)))
            rif = max(stats[a]["coh"], stats[bb]["coh"])
            ver = "stesso asse" if np.mean(cs) > rif * 1.5 else "attrattori distinti"
            print(f"    {a:14s} vs {bb:14s} cos {np.mean(cs):>+7.3f} "
                  f"(dev {np.std(cs):.3f})   rif {rif:+.3f}   -> {ver}")
            out_rows.append(dict(space=space, pair=f"cos[{a},{bb}]",
                                 n_prompt=len(prompts), coh=round(float(np.mean(cs)), 6)))
        print()

    # --- che cosa si muove, in unita' leggibili ------------------------------
    print("=" * 82)
    print("  QUALI DIMENSIONI DELLA TECNICA SI MUOVONO")
    print("  z contro la deviazione fra baseline a seed diversi; solo |z| >= 1")
    print("=" * 82)
    bkeys = [k for k in bases if k[0] in prompts]
    B = np.stack([TEX[b(bases[k])] for k in bkeys])
    bsd = B.std(0)
    bsd[bsd < 1e-9] = 1.0
    for c in conds:
        d = {k: v for k, v in byc[c].items() if k[0] in prompts}
        delta = np.mean(np.stack([TEX[b(v)] - TEX[b(bases[k])] for k, v in d.items()]), 0)
        z = delta / bsd
        for i in np.argsort(-np.abs(z)):
            if abs(z[i]) < 1.0:
                break
            feat_rows.append(dict(condition=c, feature=NAMES[i], z=round(float(z[i]), 3)))
        top = np.argsort(-np.abs(z))[:4]
        print(f"  {c:16s}" + "   ".join(f"{NAMES[i]} {z[i]:+.2f}" for i in top))

    head = ["space", "pair", "n_prompts"]
    ks = head + sorted({k for r in out_rows for k in r} - set(head))
    with open(OUT_SA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ks, restval=""); w.writeheader(); w.writerows(out_rows)
    with open(OUT_FEAT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["condition", "feature", "z"])
        w.writeheader(); w.writerows(feat_rows)
    print(f"\n-> {OUT_SA}\n-> {OUT_FEAT}\n-> {TEX_NPZ}")


if __name__ == "__main__":
    main()
