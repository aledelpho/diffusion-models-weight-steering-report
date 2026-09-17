# -*- coding: utf-8 -*-
"""
experiments/analyze_palette.py  --  la STRUTTURA della palette, non quanti colori ci sono

IPOTESI, SCRITTA PRIMA DEL CODICE E PRIMA DI GUARDARE I NUMERI.

  Il preset riduce il NUMERO DI GRADINI TONALI sul soggetto e aumenta la
  DISTANZA fra quelli che restano. In parole di Alessandro: "meno sfumature,
  meno colori". Se esce il contrario, o esce piatto, si scrive quello.

  Ipotesi secondaria, sollevata dopo aver visto gli output e quindi piu' debole:
  in alcune condizioni il "fumetto" scivola verso "carta stampata / ingiallita".
  Se e' vero, la carta guadagna croma e la sua tinta si sposta verso il giallo,
  e il nero d'inchiostro si alza in L*. Questa e' una previsione direzionale su
  due misure separate, non un pescaggio.

PERCHE' SERVE, DATO CHE IL COLORE E' GIA' STATO MISURATO DUE VOLTE.
analyze_quantization.py conta i colori (colori_efficaci_log, quota_primi_k) e
color_freedom.py misura lo spostamento LAB del soggetto. Sono entrambe
statistiche AGGREGATE sui pixel: nessuna delle due dice quanto sono DISTANTI
fra loro i toni. Due immagini con identico numero di colori efficaci e identica
croma media possono avere una palette a tre gradini larghi e una a sei gradini
appiccicati. Quella differenza e' esattamente cio' che "meno sfumature" descrive,
e nessuna feature attuale la vede.

LA MASCHERA DEL SOGGETTO DI color_freedom.py NON VA BENE QUI, ed e' il motivo
per cui questo script ne costruisce un'altra. Quella e':

    soggetto = ~((L > 88) & (hypot(A, B) < 8))

cioe' "non e' sfondo se non e' chiaro E poco saturo". Su carta ingiallita la
croma dello sfondo supera 8, la condizione diventa falsa, e **lo sfondo entra
nel soggetto** portandosi dietro milioni di pixel di carta. Proprio nel caso che
si vuole misurare, la maschera cede. Qui la carta si STIMA invece di assumerla
bianca, e il soggetto e' cio' che dista dalla carta misurata. Funziona che la
carta sia bianca, crema o gialla.

LA PRIMA VERSIONE DI QUESTA STIMA ERA SBAGLIATA, e vale la pena tenerne traccia.
Stimava la carta da un anello di 12 px sul bordo del fotogramma, perche' i prompt
dicono `white background`. Ma gli stessi prompt dicono anche `extreme close-up on
the head only, tight framing`: la testa arriva fino al bordo. Risultato,
paper_L = 65.7 +/- 23.5, bimodale, e subject_frac fra 0.89 e 0.95 -- cioe' la
"carta" era guancia. La versione attuale prende i cluster estremi in L* fra
quelli con almeno MIN_MASS di massa sull'immagine intera: paper_L = 99.0 +/- 0.5.
E' la pitfall 29 di docs/errors_log.md.

CHE COSA PRODUCE.
Una riga per immagine con le stesse convenzioni di style_features.csv, cosi'
global_aggregation_corrected.py la puo' ingerire cambiando una sola costante
(FEAT) senza una riga di statistica nuova.

  identita'    condition, prompt_dir, prompt_sha1, seed, rel_path
  carta        paper_L, paper_C, paper_hue_deg, paper_frac, paper_hex
  inchiostro   ink_L, ink_C, ink_hue_deg, ink_frac, ink_hex
  palette      sw1..6_L, sw1..6_C, sw1..6_hue_deg, sw1..6_share, sw1..6_hex
  derivate     tonal_range, step_regularity, effective_steps,
               top2_mass_share, chroma_spread, subject_frac

LE COLONNE DI IDENTITA' NON SONO UN ABBELLIMENTO. I render stanno in
`<condizione>/<prompt>/<seed>.webp` e il basename e' solo il seed: `1337.webp`
esiste identico in tutte e otto le condizioni. Un CSV con la sola colonna `file`
non e' raggruppabile per preset e non e' appaiabile per seed -- cioe' non
risponde alla domanda "che differenza c'e' fra un preset e l'altro". Le cinque
colonne si ricavano dal percorso e rendono il file autosufficiente.

L'HEX DI OGNI SWATCH SERVE A GUARDARE LA PALETTE, non a calcolarci sopra. L*, C
e la tinta in gradi sono le misure; l'hex e' la stessa terna riportata in una
forma che si puo' incollare in un file e vedere. Chi calcola usa i numeri.

I SEI SWATCH SEGUONO LA SPECIFICA DI ALESSANDRO: il piu' scuro, il piu' chiaro,
e i quattro piu' diversi in saturazione e tinta. Non e' un k-means a 6: si
sovra-segmenta a 12, si prendono gli estremi di L*, e i quattro intermedi si
scelgono per massima distanza reciproca nel piano (a*, b*) -- che e' esattamente
"piu' diversi in croma e tinta", visto che C e h ne sono le coordinate polari.
Poi si ordinano per L*, perche' una palette non ordinata non e' confrontabile
fra immagini.

ESITO DELLA PRE-REGISTRAZIONE  (20 seed appaiati, prompt "full", A1 blockshuffle
vs A5 baseline vs A7 randsign a spostamento identico; permutazione esatta a
inversione di segno sulle differenze appaiate, Holm su tre primarie).

  L'IPOTESI PRIMARIA NON REGGE. Il numero di gradini non cala
  (effective_steps, delta = -0.20, p = 0.49) e la distanza fra quelli che
  restano non cresce (mean_gap, delta = -0.07, p = 0.63). "Meno sfumature" non
  descrive quello che succede alla scala tonale.

  QUELLO CHE CAMBIA E' LA CROMA, NON I GRADINI. chroma_spread scende di 4.53
  unita' (Holm p = 1.8e-4), e randsign allo stesso spostamento va nella
  direzione OPPOSTA (+2.06, p = 0.09): non e' un effetto generico di
  perturbazione.

  L'IPOTESI SECONDARIA NON E' TESTABILE SU QUESTO SOTTOINSIEME. La carta qui e'
  bianca in tutte e tre le condizioni (paper_L 99.0-99.8, paper_C 0.1-0.4): la
  carta ingiallita che Alessandro descrive non compare in questi tre preset, e
  un canale piatto non e' una smentita. Va rieseguito sui sette preset della
  griglia, dove il caso estremo esiste.

  ATTENZIONE: questa esecuzione e' sui webp q82 del repository, non sui PNG
  originali. Una misura di croma su un formato lossy va riconfermata sui PNG
  prima di entrare nel report.

RIPRODUCIBILITA'. k-means e' sensibile all'inizializzazione: random_state fisso
e n_init=10, o due esecuzioni danno palette diverse sulla stessa immagine.
"""

import os
import re
import sys
import csv
import glob
import argparse
import numpy as np
import cv2
from sklearn.cluster import KMeans

# ------------------------------------------------------------------ costanti
K_OVERSEG      = 12      # cluster di sovra-segmentazione, prima della selezione
N_SWATCH       = 6       # swatch finali: 2 estremi di L* + 4 piu' distanti in (a,b)
PAPER_DELTA_E  = 12.0    # distanza da cui un pixel smette di essere carta
MIN_MASS       = 0.03    # massa minima perche' un cluster conti come carta o inchiostro
K_GLOBAL       = 8       # cluster sull'immagine intera, per stimare carta e inchiostro
STEP_JND       = 5.0     # salto di L* oltre il quale due toni sono distinti
MIN_SUBJECT    = 0.05    # sotto questa frazione la maschera ha fallito
RANDOM_STATE   = 20260917

_HERE = os.path.dirname(os.path.abspath(__file__))


def _first(*cand):
    for c in cand:
        if os.path.isdir(c):
            return c
    return cand[-1]


ROOT = _first(os.path.join(_HERE, os.pardir, "data"),
              r"c:\Users\aless\Desktop\comfyui-pilot")


# ------------------------------------------------------------------ colore
def to_lab(bgr):
    """BGR uint8 -> CIELAB float con L in [0,100], a/b in [-128,127]."""
    lab = cv2.cvtColor(bgr.astype(np.float32) / 255.0, cv2.COLOR_BGR2LAB)
    return lab.reshape(-1, 3)


def chroma_hue(a, b):
    C = float(np.hypot(a, b))
    h = float(np.degrees(np.arctan2(b, a)) % 360.0)
    return C, h


def lab_to_hex(lab3):
    """Centro LAB -> #rrggbb, per poter GUARDARE la palette e non solo misurarla.

    Il giro passa da cv2 con lo stesso identico spazio usato in andata (L in
    [0,100]), cosi' l'hex e' davvero il colore misurato e non una conversione
    con un'altra convenzione. Fuori gamut si clippa: un centroide k-means puo'
    cadere fuori dal cubo sRGB, e in quel caso l'hex e' il piu' vicino
    rappresentabile -- il numero resta la misura buona."""
    lab = np.asarray(lab3, dtype=np.float32).reshape(1, 1, 3)
    bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR).reshape(3)
    b, g, r = np.clip(bgr, 0.0, 1.0) * 255.0
    return "#{:02x}{:02x}{:02x}".format(int(round(r)), int(round(g)), int(round(b)))


def identity_from_path(path, images_root):
    """condition / prompt_dir / prompt_sha1 / seed dal percorso del render.

    Supporta sia la struttura a directory <root>/<condizione>/<id>_<tag>_<sha1>/<seed>.webp
    sia la convenzione ComfyUI piatta <prompt>_<condizione>_seed<seed>_<counter>_.png."""
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(images_root)) if images_root else os.path.basename(path)
    parts = rel.replace(os.sep, "/").split("/")
    seed = os.path.splitext(parts[-1])[0]
    prompt_dir = parts[-2] if len(parts) >= 2 else ""
    condition = parts[-3] if len(parts) >= 3 else ""
    sha1 = prompt_dir.rsplit("_", 1)[-1] if "_" in prompt_dir else ""
    if not re.fullmatch(r"[0-9a-f]{6,40}", sha1):
        sha1 = ""

    # Fallback per benchmark con naming ComfyUI: P<prompt>_<condition>_seed<seed>_...
    if not condition or prompt_dir in ("renders", "hud", ""):
        basename = os.path.basename(path)
        m = re.match(r"^([A-Za-z0-9]+?)_([A-Za-z0-9_]+?)_seed(\d+)", basename)
        if m:
            prompt_dir = m.group(1)
            condition = m.group(2)
            seed = m.group(3)

    # Estrazione crittografica di prompt_sha1 dai metadati embedded del PNG ComfyUI
    if not sha1 and os.path.exists(path):
        try:
            from PIL import Image
            import json, hashlib
            with Image.open(path) as im:
                if "prompt" in im.info:
                    pdata = json.loads(im.info["prompt"])
                    pos_txt = ""
                    for nid, node in pdata.items():
                        if node.get("class_type") == "CLIPTextEncode":
                            t = node.get("inputs", {}).get("text", "")
                            if "negative" not in t.lower() and len(t) > len(pos_txt):
                                pos_txt = t.strip()
                    if pos_txt:
                        sha1 = hashlib.sha1(pos_txt.encode("utf-8")).hexdigest()[:10]
        except Exception:
            pass

    return {"condition": condition, "prompt_dir": prompt_dir,
            "prompt_sha1": sha1, "seed": seed,
            "rel_path": rel.replace(os.sep, "/")}


def estimate_extremes(lab):
    """Carta e inchiostro come i cluster estremi in L* CHE HANNO MASSA.

    La prima versione stimava la carta dall'anello di bordo, sul presupposto che
    'white background, simple background' la mettesse li'. Sbagliato su questo
    corpus: i prompt dicono anche 'extreme close-up on the head only, tight
    framing', e la testa occupa il bordo in buona parte dei render. La stima
    usciva a L* 65 con deviazione 23 -- bimodale, cioe' a volte carta e a volte
    capelli, senza modo di sapere quale.

    Qui si segmenta l'immagine intera e si prendono il cluster piu' chiaro e il
    piu' scuro FRA QUELLI CON ALMENO MIN_MASS di pixel. La soglia di massa e' il
    punto: esclude il riflesso speculare da quattro pixel e la singola ombra
    piu' nera, che sono code e non superfici. Funziona che la carta sia bianca,
    crema o gialla, e che sia il 60% dell'immagine o il 3%.

    `paper_frac` e `ink_frac` sono riportate proprio perche' un lettore veda
    quanto sono grandi: una carta al 3% e' un'altra cosa da una al 50%."""
    pts = lab
    if len(pts) > 200_000:
        rng = np.random.default_rng(RANDOM_STATE)
        pts = pts[rng.choice(len(pts), 200_000, replace=False)]
    k = min(K_GLOBAL, len(np.unique(pts.round(1), axis=0)))
    km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(pts)
    cen = km.cluster_centers_
    mass = np.bincount(km.labels_, minlength=k).astype(float) / len(km.labels_)

    heavy = [i for i in range(k) if mass[i] >= MIN_MASS]
    if not heavy:                      # immagine degenere: nessun cluster con massa
        heavy = list(range(k))
    i_paper = max(heavy, key=lambda i: cen[i, 0])
    i_ink = min(heavy, key=lambda i: cen[i, 0])
    return cen[i_paper], float(mass[i_paper]), cen[i_ink], float(mass[i_ink])


def pick_swatches(centers, weights):
    """Il piu' scuro, il piu' chiaro, e i quattro piu' distanti in (a*, b*).

    I quattro intermedi si scelgono per farthest-point sampling: si parte dal
    piu' saturo e a ogni passo si aggiunge quello che massimizza la distanza
    MINIMA dai gia' scelti. E' deterministico e non privilegia i cluster grandi,
    che e' il punto: un accento raro ma cromaticamente lontano e' esattamente
    cio' che si vuole vedere."""
    idx_dark = int(np.argmin(centers[:, 0]))
    idx_light = int(np.argmax(centers[:, 0]))
    chosen = [idx_dark, idx_light]

    rest = [i for i in range(len(centers)) if i not in chosen]
    ab = centers[:, 1:3]
    # seme: il piu' saturo fra i rimanenti
    sat = np.hypot(ab[rest, 0], ab[rest, 1])
    chosen.append(rest[int(np.argmax(sat))])

    while len(chosen) < N_SWATCH and len(chosen) < len(centers):
        rest = [i for i in range(len(centers)) if i not in chosen]
        if not rest:
            break
        d = np.array([min(np.linalg.norm(ab[i] - ab[j]) for j in chosen) for i in rest])
        chosen.append(rest[int(np.argmax(d))])

    chosen = sorted(chosen, key=lambda i: centers[i, 0])   # ordinati per L*
    return chosen


def palette_features(path, images_root=None):
    bgr = cv2.imread(path, cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(path)
    H, W = bgr.shape[:2]
    lab = to_lab(bgr)

    # --- carta e inchiostro: cluster estremi con massa, non bordo ne' percentile --
    paper, paper_frac, ink, ink_frac = estimate_extremes(lab)
    paper_C, paper_h = chroma_hue(paper[1], paper[2])
    ink_C, ink_h = chroma_hue(ink[1], ink[2])

    d_paper = np.linalg.norm(lab - paper, axis=1)
    subject = d_paper > PAPER_DELTA_E
    subj_frac = float(subject.mean())
    if subj_frac < MIN_SUBJECT:
        raise RuntimeError(
            f"{os.path.basename(path)}: maschera del soggetto al {subj_frac:.1%}, "
            f"sotto la soglia del {MIN_SUBJECT:.0%}. La stima della carta ha "
            f"probabilmente inghiottito il soggetto: va guardata, non aggirata.")

    # --- palette del soggetto -----------------------------------------------
    pts = lab[subject]
    if len(pts) > 200_000:                      # campionamento per velocita'
        rng = np.random.default_rng(RANDOM_STATE)
        pts = pts[rng.choice(len(pts), 200_000, replace=False)]
    k = min(K_OVERSEG, len(np.unique(pts.round(1), axis=0)))
    km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(pts)
    centers = km.cluster_centers_
    counts = np.bincount(km.labels_, minlength=k).astype(float)
    shares = counts / counts.sum()

    sel = pick_swatches(centers, shares)
    sw_L, sw_C, sw_h, sw_w, sw_hex = [], [], [], [], []
    for i in sel:
        C, h = chroma_hue(centers[i, 1], centers[i, 2])
        sw_L.append(float(centers[i, 0])); sw_C.append(C); sw_h.append(h)
        sw_w.append(float(shares[i])); sw_hex.append(lab_to_hex(centers[i]))
    while len(sw_L) < N_SWATCH:                 # immagine quasi piatta
        sw_L.append(float("nan")); sw_C.append(float("nan"))
        sw_h.append(float("nan")); sw_w.append(0.0); sw_hex.append("")

    # --- le quattro derivate che sono l'ipotesi ------------------------------
    Ls = np.array([x for x in sw_L if np.isfinite(x)])
    gaps = np.diff(Ls) if len(Ls) > 1 else np.array([0.0])
    row = {"file": os.path.basename(path)}
    row.update(identity_from_path(path, images_root) if images_root else
               {"condition": "", "prompt_dir": "", "prompt_sha1": "",
                "seed": "", "rel_path": ""})
    row.update({
        "width_px": W, "height_px": H,
        "paper_L": round(float(paper[0]), 4), "paper_C": round(paper_C, 4),
        "paper_hue_deg": round(paper_h, 2), "paper_frac": round(paper_frac, 4),
        "paper_hex": lab_to_hex(paper),
        "ink_L": round(float(ink[0]), 4), "ink_C": round(ink_C, 4),
        "ink_hue_deg": round(ink_h, 2), "ink_frac": round(ink_frac, 4),
        "ink_hex": lab_to_hex(ink),
        "subject_frac": round(subj_frac, 4),
        "tonal_range": round(float(Ls.max() - Ls.min()), 4) if len(Ls) > 1 else 0.0,
        "step_regularity": round(float(np.std(gaps)), 4),
        "effective_steps": int((gaps > STEP_JND).sum() + 1),
        "top2_mass_share": round(float(np.sort(sw_w)[::-1][:2].sum()), 4),
        "chroma_spread": round(float(np.nanmax(sw_C) - np.nanmin(sw_C)), 4),
    })
    for i in range(N_SWATCH):
        row[f"sw{i+1}_L"] = round(sw_L[i], 4) if np.isfinite(sw_L[i]) else ""
        row[f"sw{i+1}_C"] = round(sw_C[i], 4) if np.isfinite(sw_C[i]) else ""
        row[f"sw{i+1}_hue_deg"] = round(sw_h[i], 2) if np.isfinite(sw_h[i]) else ""
        row[f"sw{i+1}_share"] = round(sw_w[i], 4)
        row[f"sw{i+1}_hex"] = sw_hex[i]
    return row


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--src", "--images", dest="images", required=True,
                    help="cartella con i render (ricorsiva) o glob")
    ap.add_argument("--out", default=os.path.join(ROOT, "palette_features.csv"))
    ap.add_argument("--offset", type=int, default=0,
                    help="salta le prime N immagini (elaborazione a blocchi)")
    ap.add_argument("--limit", type=int, default=0,
                    help="elabora al massimo N immagini; 0 = tutte")
    ap.add_argument("--root", default=None,
                    help="radice da cui ricavare condition/prompt/seed; "
                         "default: --images se e' una cartella")
    ap.add_argument("--include-hud", action="store_true",
                    help="non escludere i file da hud/ e _orphans")
    ap.add_argument("--log", default=None,
                    help="file di log persistente per monitorare l'avanzamento")
    args = ap.parse_args()

    is_glob = any(c in args.images for c in "*?[")
    pats = [args.images] if is_glob else \
           [os.path.join(args.images, "**", "*.png"), os.path.join(args.images, "**", "*.webp")]
    files = sorted({f for p in pats for f in glob.glob(p, recursive=True)})
    if not files:
        raise SystemExit(f"nessuna immagine trovata in {args.images}")

    # Esclusione automatica di directory ausiliarie se ci sono render effettivi
    if not args.include_hud and any("/renders/" in f.replace(os.sep, "/") or "\\renders\\" in f for f in files):
        valid_files = [f for f in files if "/hud/" not in f.replace(os.sep, "/")
                                       and "\\hud\\" not in f
                                       and "_orphans" not in f]
        if len(valid_files) < len(files):
            print(f"[palette] Escluse {len(files) - len(valid_files)} immagini ausiliarie (hud / _orphans). "
                  f"Analisi limitata ai {len(valid_files)} render effettivi.")
            files = valid_files

    if args.root:
        root = args.root
    elif is_glob:
        root = os.path.commonpath([os.path.dirname(f) for f in files]) if files else None
    else:
        root = args.images
    total = len(files)
    if args.offset or args.limit:
        files = files[args.offset:(args.offset + args.limit) if args.limit else None]
        print(f"[palette] blocco {args.offset}..{args.offset+len(files)} di {total}")
    print(f"[palette] {len(files)} immagini", flush=True)
    print(f"[palette] carta e inchiostro = cluster estremi con massa >= {MIN_MASS:.0%}; soggetto = distanza LAB > {PAPER_DELTA_E}", flush=True)
    print(f"[palette] {K_OVERSEG} cluster sovra-segmentati -> {N_SWATCH} swatch, random_state={RANDOM_STATE}", flush=True)

    import time
    t_start = time.time()
    if args.log:
        os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)
        with open(args.log, "a", encoding="utf-8") as lf:
            lf.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] === INIZIO BATCH: {len(files)} immagini | Target: {args.out} ===\n")

    rows, failed = [], []
    for n, f in enumerate(files, 1):
        try:
            rows.append(palette_features(f, root))
        except Exception as e:
            failed.append((os.path.basename(f), str(e)))

        elapsed = time.time() - t_start
        rate = elapsed / n if n > 0 else 0
        eta_s = (len(files) - n) * rate
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_s))
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))

        if n % 10 == 0 or n == len(files):
            print(f"  {n}/{len(files)} (trascorso {elapsed_str}, ETA {eta_str})", flush=True)

        if args.log:
            msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{n:03d}/{len(files):03d} - {(n/len(files))*100:5.1f}%] {os.path.basename(f)} | trascorso: {elapsed_str} | ETA: {eta_str}"
            with open(args.log, "a", encoding="utf-8") as lf:
                lf.write(msg + "\n")

    if args.log:
        with open(args.log, "a", encoding="utf-8") as lf:
            lf.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] === COMPLETATO: {len(rows)} righe salvate in {args.out} (durata totale: {time.strftime('%H:%M:%S', time.gmtime(time.time() - t_start))}) ===\n\n")

    if failed:
        print(f"\n[palette] {len(failed)} immagini NON elaborate -- non si scartano in silenzio:")
        for name, err in failed[:10]:
            print(f"    {name}: {err}")
        if len(failed) > 10:
            print(f"    ... e altre {len(failed)-10}")

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\n-> {args.out}   ({len(rows)} righe, {len(rows[0])-8} feature)")

    conds = sorted({r["condition"] for r in rows if r["condition"]})
    if len(conds) > 1:
        print(f"\n[palette] {len(conds)} condizioni nel file. Medie per condizione")
        print("          (DESCRITTIVE: non appaiate per prompt/seed, quindi non sono")
        print("           un contrasto. Il contrasto va fatto appaiando prompt_sha1 + seed.)")
        keys = ["paper_L", "paper_C", "ink_L", "chroma_spread",
                "effective_steps", "tonal_range", "top2_mass_share"]
        hdr = f"  {'condition':<18}{'n':>5}" + "".join(f"{k:>16}" for k in keys)
        print(hdr); print("  " + "-" * (len(hdr) - 2))
        for c in conds:
            sub = [r for r in rows if r["condition"] == c]
            line = f"  {c:<18}{len(sub):>5}"
            for k in keys:
                v = [float(r[k]) for r in sub if r[k] not in ("", None)]
                line += f"{(sum(v)/len(v) if v else float('nan')):>16.2f}"
            print(line)

    print("\nPer i contrasti: puntare FEAT di global_aggregation_corrected.py a questo file")
    print("e aggiungere a METR le derivate da testare. Nessuna statistica nuova da scrivere.")


if __name__ == "__main__":
    main()
