"""
style_features.py
==================

Estrazione algoritmica (nessun training, nessun giudice esterno) di feature
di "stile di resa" da immagini illustrative, organizzate nelle 5 famiglie
discusse: Tratto/Linework, Colore, Durezza delle ombre, Texture generale,
Dominio delle frequenze.

Progettato per essere usato in DIFFERENZE APPAIATE a parità di prompt e seed
(preset vs blockshuffle vs randsign vs baseline), non come punteggio assoluto
per immagine — molte feature correlano fortemente col soggetto, non solo
con l'intervento sui pesi.

Dipendenze: opencv-python-headless, scikit-image, scipy, numpy, scikit-learn, pandas

Uso da riga di comando:
    python style_features.py img1.png img2.png ... --out features.csv
    python style_features.py --dir /path/to/folder --out features.csv

Uso come libreria:
    from style_features import extract_all_features
    feats = extract_all_features("image.png")
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import warnings
from dataclasses import dataclass, asdict
from typing import Optional

import numpy as np
import cv2
from scipy import ndimage as ndi
from scipy.stats import entropy as scipy_entropy
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")


# --------------------------------------------------------------------------
# Utility di caricamento e preprocessing
# --------------------------------------------------------------------------

def load_image(path: str, max_side: Optional[int] = None) -> tuple[np.ndarray, np.ndarray]:
    """Carica un'immagine e ritorna (BGR uint8, grayscale uint8).

    max_side: se impostato, ridimensiona SOLO per feature che non dipendono
    dalla risoluzione nativa (nessuna delle funzioni qui sotto lo richiede
    per default — vedi nota nel modulo sul rischio di perdere lo spessore
    del tratto se si ridimensiona troppo aggressivamente prima di misurarlo).
    """
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Impossibile leggere l'immagine: {path}")
    if max_side is not None:
        h, w = img.shape[:2]
        scale = max_side / max(h, w)
        if scale < 1.0:
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img, gray


def ink_mask(gray: np.ndarray, block_size: int = 35, C: int = 10) -> np.ndarray:
    """Maschera binaria dei pixel 'inchiostro' (tratto/ombreggiatura scura)
    tramite soglia adattiva. Usata come base per le feature di linework.
    """
    mask = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        blockSize=block_size, C=C,
    )
    # ripulisce rumore isolato di 1-2 px
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    return mask


# --------------------------------------------------------------------------
# FAMIGLIA 1 — Tratto e linework
# --------------------------------------------------------------------------

def stroke_width_stats(gray: np.ndarray) -> dict:
    """Mediana e varianza dello spessore del tratto, via distance transform
    sullo scheletro della maschera d'inchiostro (Stroke Width Transform
    semplificato). Restituisce anche il coefficiente di variazione, che è
    la vera misura di "modulazione" del tratto (pennino vs linea uniforme)
    indipendente dalla scala assoluta.
    """
    mask = ink_mask(gray)
    if mask.sum() == 0:
        return {"stroke_width_median_px": np.nan, "stroke_width_std_px": np.nan,
                "stroke_width_cv": np.nan}

    # distance transform: ogni pixel d'inchiostro -> distanza dal bordo più vicino
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)

    # scheletro morfologico per campionare solo l'asse centrale del tratto
    # (altrimenti la distanza è dominata dai pixel vicino al bordo, non dal centro)
    skel = _skeletonize(mask)
    widths = dist[skel > 0] * 2.0  # raggio -> diametro = spessore
    widths = widths[widths > 0]

    if widths.size == 0:
        return {"stroke_width_median_px": np.nan, "stroke_width_std_px": np.nan,
                "stroke_width_cv": np.nan}

    median_w = float(np.median(widths))
    std_w = float(np.std(widths))
    cv_w = float(std_w / median_w) if median_w > 0 else np.nan
    return {
        "stroke_width_median_px": median_w,
        "stroke_width_std_px": std_w,
        "stroke_width_cv": cv_w,
    }


def _skeletonize(mask: np.ndarray) -> np.ndarray:
    """Scheletro morfologico via erosione/dilatazione iterativa (Zhang-Suen
    approssimato con operazioni OpenCV, evita dipendenza extra).
    """
    img = (mask > 0).astype(np.uint8)
    skel = np.zeros_like(img)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    temp = img.copy()
    while True:
        eroded = cv2.erode(temp, element)
        opened = cv2.dilate(eroded, element)
        subset = cv2.subtract(temp, opened)
        skel = cv2.bitwise_or(skel, subset)
        temp = eroded
        if cv2.countNonZero(temp) == 0:
            break
    return skel


def edge_density(gray: np.ndarray, low: int = 50, high: int = 150) -> dict:
    """Percentuale di pixel classificati come bordo (Canny)."""
    edges = cv2.Canny(gray, low, high)
    density = float(np.count_nonzero(edges)) / edges.size
    return {"edge_density": density}


def contour_continuity(gray: np.ndarray, low: int = 50, high: int = 150) -> dict:
    """Lunghezza media delle componenti connesse di bordo. Contorni chiusi
    e continui (stile 'cartone') danno componenti lunghe; tratteggio
    spezzato/sketchy (stile 'fumetto a china') dà molte componenti corte.
    """
    edges = cv2.Canny(gray, low, high)
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(edges, connectivity=8)
    if n_labels <= 1:
        return {"contour_mean_length_px": 0.0, "contour_n_components": 0}
    areas = stats[1:, cv2.CC_STAT_AREA]  # esclude il background (label 0)
    return {
        "contour_mean_length_px": float(np.mean(areas)),
        "contour_n_components": int(n_labels - 1),
    }


def crosshatch_orientation_entropy(gray: np.ndarray, win: int = 24, stride: int = 12) -> dict:
    """Entropia dell'istogramma di orientazione del gradiente locale, mediata
    su finestre scorrevoli. Zone di crosshatching hanno gradiente distribuito
    su più direzioni (entropia alta); zone di ombreggiatura piatta o tratto
    a direzione unica hanno entropia bassa. Questa è probabilmente la
    feature singola più vicina a "quanto sembra china disegnata a mano".
    """
    gx = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx ** 2 + gy ** 2)
    ang = (np.arctan2(gy, gx) * 180.0 / np.pi) % 180.0  # orientazione non direzionale, 0-180

    h, w = gray.shape
    entropies = []
    mag_thresh = np.percentile(mag, 60)  # ignora finestre quasi piatte (sfondo/carta)

    for y in range(0, h - win, stride):
        for x in range(0, w - win, stride):
            win_mag = mag[y:y + win, x:x + win]
            if win_mag.mean() < mag_thresh * 0.3:
                continue  # finestra troppo piatta, non informativa
            win_ang = ang[y:y + win, x:x + win]
            weights = win_mag.ravel()
            hist, _ = np.histogram(win_ang.ravel(), bins=18, range=(0, 180), weights=weights)
            if hist.sum() <= 0:
                continue
            p = hist / hist.sum()
            entropies.append(scipy_entropy(p + 1e-12, base=2))

    if not entropies:
        return {"crosshatch_entropy_mean": np.nan, "crosshatch_entropy_p90": np.nan}

    entropies = np.array(entropies)
    return {
        "crosshatch_entropy_mean": float(entropies.mean()),
        "crosshatch_entropy_p90": float(np.percentile(entropies, 90)),
    }


# --------------------------------------------------------------------------
# FAMIGLIA 2 — Colore
# --------------------------------------------------------------------------

def color_flatness(img_bgr: np.ndarray, k: int = 16, sample: int = 20000,
                    seed: int = 0) -> dict:
    """Quantizza i colori con k-means e misura quanta massa di pixel è
    spiegata dai cluster più popolosi. Stile 'flat/cel-shaded' concentra
    la maggioranza dei pixel in pochissimi cluster; stile pittorico/sfumato
    distribuisce la massa su molti cluster.
    """
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).reshape(-1, 3).astype(np.float32)
    if rgb.shape[0] > sample:
        idx = np.random.RandomState(seed).choice(rgb.shape[0], sample, replace=False)
        rgb_sample = rgb[idx]
    else:
        rgb_sample = rgb

    km = KMeans(n_clusters=k, n_init=4, random_state=seed).fit(rgb_sample)
    counts = np.bincount(km.labels_, minlength=k)
    freqs = np.sort(counts / counts.sum())[::-1]  # decrescente

    top4_share = float(freqs[:4].sum())
    # entropia normalizzata della distribuzione dei cluster: bassa = pochi
    # colori dominanti (flat), alta = palette diffusa
    ent = scipy_entropy(freqs + 1e-12, base=2) / np.log2(k)

    return {
        "color_top4_cluster_share": top4_share,
        "color_cluster_entropy_norm": float(ent),
        "color_n_effective": float(2 ** (scipy_entropy(freqs + 1e-12, base=2))),
    }


def colorfulness_hasler_susstrunk(img_bgr: np.ndarray) -> dict:
    """Metrica di 'colorfulness' di Hasler & Süsstrunk (2003) — standard in
    letteratura, più robusta della sola saturazione media perché combina
    rg/yb opponent channels.
    """
    b, g, r = cv2.split(img_bgr.astype(np.float32))
    rg = r - g
    yb = 0.5 * (r + g) - b
    std_rg, mean_rg = np.std(rg), np.mean(rg)
    std_yb, mean_yb = np.std(yb), np.mean(yb)
    std_root = np.sqrt(std_rg ** 2 + std_yb ** 2)
    mean_root = np.sqrt(mean_rg ** 2 + mean_yb ** 2)
    colorfulness = std_root + 0.3 * mean_root
    return {"colorfulness_hs": float(colorfulness)}


def luminance_banding(gray: np.ndarray, n_levels_test: int = 12) -> dict:
    """Stima quanti livelli di luminanza distinti sono effettivamente
    'usati' nell'immagine, misurando quanti picchi significativi ha
    l'istogramma di luminanza smussato. Shading a bande nette (cel-shading,
    2-4 livelli) produce pochi picchi netti; gradiente continuo (pittorico)
    produce un istogramma liscio senza picchi distinti.
    """
    hist, bin_edges = np.histogram(gray, bins=64, range=(0, 255))
    hist_smooth = ndi.gaussian_filter1d(hist.astype(np.float32), sigma=1.5)

    # conta i massimi locali sopra una soglia relativa
    peaks = 0
    thresh = hist_smooth.max() * 0.05
    for i in range(1, len(hist_smooth) - 1):
        if hist_smooth[i] > thresh and hist_smooth[i] > hist_smooth[i - 1] and hist_smooth[i] >= hist_smooth[i + 1]:
            peaks += 1

    return {"luminance_hist_n_peaks": int(peaks)}


# --------------------------------------------------------------------------
# FAMIGLIA 3 — Durezza dei bordi d'ombra
# --------------------------------------------------------------------------

def shadow_edge_hardness(gray: np.ndarray, canny_low=40, canny_high=120,
                          profile_len: int = 15, min_gradient: float = 15.0) -> dict:
    """Per un campione di bordi ad alto gradiente, misura la larghezza
    della zona di transizione (in pixel) necessaria a passare dal 10% al
    90% del salto di luminanza, lungo la normale al bordo. Bordo netto/
    cel-shading -> transizione stretta; sfumatura morbida -> transizione
    larga. È la feature più vicina alla differenza 'contorni netti vs
    ombre sfumate' osservata a occhio.
    """
    gray_f = gray.astype(np.float32)
    gx = cv2.Sobel(gray_f, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_f, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx ** 2 + gy ** 2)

    edges = cv2.Canny(gray, canny_low, canny_high)
    ys, xs = np.where(edges > 0)
    if len(ys) == 0:
        return {"shadow_edge_transition_width_px": np.nan}

    # sottocampiona per efficienza
    rng = np.random.RandomState(0)
    n_sample = min(800, len(ys))
    sel = rng.choice(len(ys), n_sample, replace=False)

    h, w = gray.shape
    widths = []
    for idx in sel:
        y, x = ys[idx], xs[idx]
        gxx, gyy = gx[y, x], gy[y, x]
        norm = np.hypot(gxx, gyy)
        if norm < min_gradient:
            continue
        nx, ny = gxx / norm, gyy / norm  # direzione normale al bordo

        # campiona il profilo di luminanza lungo la normale
        ts = np.arange(-profile_len, profile_len + 1)
        xs_p = np.clip((x + ts * nx).astype(int), 0, w - 1)
        ys_p = np.clip((y + ts * ny).astype(int), 0, h - 1)
        profile = gray_f[ys_p, xs_p]

        lo, hi = profile.min(), profile.max()
        span = hi - lo
        if span < 20:  # bordo troppo debole, salta
            continue
        lo_t, hi_t = lo + 0.1 * span, lo + 0.9 * span

        # trova quanti pixel del profilo cadono nella fascia di transizione
        in_transition = np.where((profile > lo_t) & (profile < hi_t))[0]
        if in_transition.size == 0:
            widths.append(1.0)
        else:
            widths.append(float(in_transition.size))

    if not widths:
        return {"shadow_edge_transition_width_px": np.nan}

    return {
        "shadow_edge_transition_width_px": float(np.median(widths)),
        "shadow_edge_transition_width_std": float(np.std(widths)),
    }


# --------------------------------------------------------------------------
# FAMIGLIA 4 — Texture generale (GLCM, LBP)
# --------------------------------------------------------------------------

def glcm_features(gray: np.ndarray, distances=(1, 3), angles=(0, np.pi / 4, np.pi / 2, 3 * np.pi / 4),
                   levels: int = 32) -> dict:
    """Gray-Level Co-occurrence Matrix: contrast, homogeneity, energy,
    correlation. Quantizza a 'levels' toni di grigio per tenere la matrice
    gestibile e ridurre sensibilità al rumore. Valori mediati su distanze
    e angoli per ottenere descrittori invarianti a orientazione locale.
    """
    gray_q = (gray.astype(np.float32) / 255.0 * (levels - 1)).astype(np.uint8)
    glcm = graycomatrix(gray_q, distances=list(distances), angles=list(angles),
                         levels=levels, symmetric=True, normed=True)

    out = {}
    for prop in ("contrast", "homogeneity", "energy", "correlation"):
        vals = graycoprops(glcm, prop)
        out[f"glcm_{prop}"] = float(vals.mean())
    return out


def lbp_features(gray: np.ndarray, P: int = 8, R: int = 1) -> dict:
    """Local Binary Patterns (uniform): istogramma di micro-pattern locali.
    Riassunto in due numeri: entropia dell'istogramma (ruvidezza/complessità
    di texture) e quota di pattern 'uniform' (regioni lisce/omogenee vs
    texture disordinata).
    """
    lbp = local_binary_pattern(gray, P=P, R=R, method="uniform")
    n_bins = P + 2  # uniform LBP ha P+2 pattern possibili
    hist, _ = np.histogram(lbp, bins=n_bins, range=(0, n_bins), density=True)
    ent = float(scipy_entropy(hist + 1e-12, base=2))
    uniform_share = float(hist[:-1].sum())  # esclude il bin "non-uniform" (ultimo)
    return {"lbp_entropy": ent, "lbp_uniform_share": uniform_share}


# --------------------------------------------------------------------------
# FAMIGLIA 5 — Dominio delle frequenze
# --------------------------------------------------------------------------

def fft_radial_profile(gray: np.ndarray, n_bins: int = 40) -> dict:
    """Trasformata di Fourier 2D, media dell'energia per anelli di frequenza
    crescente (profilo radiale). Riassunto con:
      - la pendenza (slope) della regressione log-log energia vs frequenza
        (più negativa = energia concentrata alle basse frequenze = stile
        morbido/flat; meno negativa/piatta = molto dettaglio fine =
        hatching fitto, texture densa)
      - la quota di energia nel terzo di frequenze più alto
    """
    f = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    power = np.abs(fshift) ** 2

    h, w = gray.shape
    cy, cx = h // 2, w // 2
    y, x = np.indices((h, w))
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    r_max = r.max()

    bin_edges = np.linspace(0, r_max, n_bins + 1)
    radial_energy = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (r >= bin_edges[i]) & (r < bin_edges[i + 1])
        if mask.sum() > 0:
            radial_energy[i] = power[mask].mean()

    # evita log(0)
    valid = radial_energy > 0
    freqs = (bin_edges[:-1] + bin_edges[1:]) / 2
    log_f = np.log10(freqs[valid] + 1e-6)
    log_e = np.log10(radial_energy[valid] + 1e-6)

    if log_f.size >= 2:
        slope, _ = np.polyfit(log_f, log_e, 1)
    else:
        slope = np.nan

    high_third = radial_energy[int(n_bins * 2 / 3):].sum()
    total = radial_energy.sum()
    high_freq_share = float(high_third / total) if total > 0 else np.nan

    return {
        "fft_radial_slope": float(slope),
        "fft_high_freq_share": high_freq_share,
    }


# --------------------------------------------------------------------------
# Orchestrazione
# --------------------------------------------------------------------------

@dataclass
class ExtractionConfig:
    """Parametri esposti per eventuale tuning; i default sono ragionevoli
    per illustrazioni digitali a linea marcata in stile fumetto/cartoon."""
    canny_low: int = 50
    canny_high: int = 150
    crosshatch_win: int = 24
    crosshatch_stride: int = 12
    glcm_levels: int = 32
    color_k: int = 16
    fft_bins: int = 40


def extract_all_features(path: str, config: Optional[ExtractionConfig] = None) -> dict:
    """Calcola tutte le feature delle 5 famiglie per una singola immagine.
    Non ridimensiona l'immagine: le feature di linework/texture dipendono
    dalla risoluzione nativa (lo stesso principio del ritaglio a risoluzione
    piena discusso per il gate del VLM — ridimensionare qui riprodurrebbe
    lo stesso problema di insensibilità al tratto).
    """
    cfg = config or ExtractionConfig()
    img_bgr, gray = load_image(path)

    feats = {"file": os.path.basename(path), "width_px": gray.shape[1], "height_px": gray.shape[0]}

    feats.update(stroke_width_stats(gray))
    feats.update(edge_density(gray, cfg.canny_low, cfg.canny_high))
    feats.update(contour_continuity(gray, cfg.canny_low, cfg.canny_high))
    feats.update(crosshatch_orientation_entropy(gray, cfg.crosshatch_win, cfg.crosshatch_stride))

    feats.update(color_flatness(img_bgr, k=cfg.color_k))
    feats.update(colorfulness_hasler_susstrunk(img_bgr))
    feats.update(luminance_banding(gray))

    feats.update(shadow_edge_hardness(gray))

    feats.update(glcm_features(gray, levels=cfg.glcm_levels))
    feats.update(lbp_features(gray))

    feats.update(fft_radial_profile(gray, n_bins=cfg.fft_bins))

    return feats


def extract_batch(paths: list[str], config: Optional[ExtractionConfig] = None,
                   verbose: bool = True) -> "list[dict]":
    rows = []
    for i, p in enumerate(paths):
        if verbose:
            print(f"[{i+1}/{len(paths)}] {os.path.basename(p)}", file=sys.stderr)
        try:
            rows.append(extract_all_features(p, config))
        except Exception as e:
            print(f"  ERRORE su {p}: {e}", file=sys.stderr)
            rows.append({"file": os.path.basename(p), "error": str(e)})
    return rows


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="*", help="Percorsi di immagini da analizzare")
    ap.add_argument("--dir", type=str, default=None, help="Cartella da cui prendere tutte le immagini (*.png, *.jpg)")
    ap.add_argument("--out", type=str, default="style_features.csv", help="Percorso file CSV di output")
    ap.add_argument("--json", action="store_true", help="Stampa anche output JSON su stdout")
    args = ap.parse_args()

    paths = list(args.images)
    if args.dir:
        for ext in ("*.png", "*.jpg", "*.jpeg"):
            paths.extend(sorted(glob.glob(os.path.join(args.dir, ext))))

    if not paths:
        ap.error("Nessuna immagine fornita. Usa argomenti posizionali o --dir.")

    rows = extract_batch(paths)

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f"\nScritte {len(df)} righe in {args.out}", file=sys.stderr)

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
