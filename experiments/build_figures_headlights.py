# -*- coding: utf-8 -*-
"""
experiments/build_figures_headlights.py

Ricostruisce le tre figure dei fari (Esperimento 2, sezione fari) COMPONENDOLE
DAI DATI invece che a mano.

PERCHE' ESISTE
--------------
La prima versione di queste figure (build_figures_stage12.py, FIG 1/2/3) aveva
le coordinate dei ritagli e le etichette scritte a mano nel sorgente. Due
conseguenze, entrambe verificate:

1. Diversi ritagli non inquadravano i fari (seed 9999 di S8_charcoal mostrava la
   fiancata; seed 9999 di S4_claymation mostrava il numero di gara sulla porta).
   Una figura che deve far vedere un faro e non lo inquadra non dimostra nulla.

2. Il pannello "S5 ukiyoe (seed 42) - preset_pos x2 - Headlight lit" era FALSO.
   Nello scoring cieco S5_ukiyoe ha il codice 0 (spento) in tutte e 35 le celle,
   cioe' in tutti e cinque i seed di tutte e sette le condizioni. Anche i valori
   L* stampati in quella figura (60.4 / 60.2 / 62.8) non corrispondono a nessuna
   luminanza calcolata da palette_features_stage9.csv, dove il taglio del terzile
   chiaro sta a L* = 34.0.

Il rimedio non e' "stare piu' attenti". E' togliere all'autore della figura la
possibilita' di scrivere un'etichetta: qui OGNI immagine e' scelta interrogando
lo scoring cieco, OGNI etichetta e' derivata dallo stesso scoring, e lo script
solleva un'eccezione se la cella scelta non ha il ruolo che la figura le
attribuisce. Per costruzione la figura non puo' dire una cosa che i dati
smentiscono.

Le immagini sono mostrate INTERE e rimpicciolite, non ritagliate. Un ritaglio e'
un'affermazione su dove si trova la cosa da guardare, e quell'affermazione era
sbagliata cinque volte su venti. Il fotogramma intero non afferma niente.

COSA CAMBIA NELLA FIG 3
-----------------------
La vecchia FIG 3 stratificava sulla luminanza MISURATA SULL'IMMAGINE TRATTATA.
La luminanza e' pero' essa stessa un effetto del trattamento (preset_pos x2
sposta L* di -3.3 in media), quindi quel terzile e' una variabile
post-trattamento: condizionarci sopra non tiene fermo il confondente, lo
ricostruisce. Si vede anche nel campione: nel terzile chiaro post-trattamento
sopravvivevano due soli stili, e tutti e cinque i "lit" del preset erano
acquerello.

Qui si stratifica sulla luminanza del BASELINE della stessa coppia
(prompt, seed) - una variabile pre-trattamento, che il trattamento non puo'
aver mosso. Il controllo regge meglio di prima e su cinque stili invece di due.

USO
---
    python experiments/build_figures_headlights.py
    python experiments/build_figures_headlights.py --renders <cartella>

La cartella dei render si puo' passare anche con la variabile d'ambiente
STAGE9_RENDERS. Senza i PNG originali lo script non parte: non inventa nulla.
"""
import os
import sys
import argparse
import itertools

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "assets", "02_attribute_emergence", "_figures")

SEEDS = [42, 777, 1337, 9999, 4242145]
SW = [f"sw{i}" for i in range(1, 7)]

# cartelle candidate per i render originali di stage 9
RENDER_CANDIDATES = [
    r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage9\renders",
    r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage9_affidabilita\renders",
]

# palette scura del notebook
BG = (14, 17, 22)
BORDER = (38, 44, 54)
INK = (227, 231, 238)
DIM = (152, 162, 178)
POS = (111, 192, 154)
NEG = (221, 136, 136)
ACC = (114, 174, 208)
WARN = (215, 167, 66)


# --------------------------------------------------------------------------
# infrastruttura
# --------------------------------------------------------------------------
def font(size, bold=False):
    names = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
    ]
    for p in names:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.truetype("segoeuib.ttf" if bold else "segoeui.ttf", size)
    except Exception:
        return ImageFont.load_default()


def render_roots(extra=None):
    roots = []
    if extra:
        roots.append(extra)
    env = os.environ.get("STAGE9_RENDERS")
    if env:
        roots.append(env)
    roots.extend(RENDER_CANDIDATES)
    return [r for r in roots if r]


def find_render(fname, roots):
    for r in roots:
        p = os.path.join(r, os.path.basename(fname))
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "render non trovato: %s\n  cercato in:\n    %s\n"
        "  passa la cartella giusta con --renders o STAGE9_RENDERS."
        % (fname, "\n    ".join(roots))
    )


def load_scores():
    """Scoring cieco dei fari, unito alla chiave e alla luminanza di palette.

    code: 0 = spento, 2 = acceso, 1 = non chiaro (fuori da numeratore E
    denominatore, come fissato nel brief prima dello scoring).
    """
    key = pd.read_csv(os.path.join(DATA, "stage9_headlights_key.csv"))
    raw = pd.read_csv(os.path.join(DATA, "stage9_headlights_raw.csv"))
    # il viewer APPENDE quando si ricorregge: vale l'ultimo punteggio (pitfall 35)
    n0 = len(raw)
    raw = raw.sort_values("timestamp_ms").drop_duplicates("hash_id", keep="last")
    if n0 != len(raw):
        print("  ri-punteggiature risolte tenendo l'ultima: %d -> %d righe" % (n0, len(raw)))

    d = key.merge(raw, on="hash_id", how="left")
    if len(d) != len(key):
        raise RuntimeError("il merge ha cambiato il numero di righe: %d -> %d" % (len(key), len(d)))
    if d.code.isna().any():
        raise RuntimeError("%d immagini senza punteggio" % int(d.code.isna().sum()))
    d["lit"] = d.code.map({0: 0.0, 2: 1.0, 1: np.nan})

    pal = pd.read_csv(os.path.join(DATA, "palette_features_stage9.csv"))
    pal = pal[pal.prompt_dir.astype(str).str.startswith("S")].copy()
    w = pal[[f"{s}_share" for s in SW]].values.astype(float)
    w = w / np.clip(w.sum(1, keepdims=True), 1e-9, None)
    pal["L_mean"] = (pal[[f"{s}_L" for s in SW]].values * w).sum(1)
    pal["ps"] = pal.prompt_dir
    d["ps"] = d.prompt_id.str.split("_").str[0]
    d = d.merge(
        pal[["ps", "condition", "seed", "L_mean"]],
        left_on=["ps", "cond_name", "seed"],
        right_on=["ps", "condition", "seed"],
        how="left",
    )
    if len(d) != len(key):
        raise RuntimeError("il merge con palette ha duplicato righe")

    # luminanza PRE-trattamento: quella del baseline della stessa scena
    base = (d[d.cond_name == "baseline"][["prompt_id", "seed", "L_mean"]]
            .rename(columns={"L_mean": "L_base"}))
    d = d.merge(base, on=["prompt_id", "seed"], how="left")
    return d


def rate(d, prompt, cond):
    s = d[(d.prompt_id == prompt) & (d.cond_name == cond)]
    return int(np.nansum(s.lit.values)), int(s.lit.notna().sum())


def cell(d, prompt, cond, seed):
    s = d[(d.prompt_id == prompt) & (d.cond_name == cond) & (d.seed == seed)]
    if len(s) != 1:
        raise RuntimeError("cella non univoca: %s / %s / %s (%d righe)" % (prompt, cond, seed, len(s)))
    return s.iloc[0]


def verdict(lit):
    if lit == 1.0:
        return "lit", POS
    if lit == 0.0:
        return "unlit", NEG
    return "unclear", WARN


def whole(path, width):
    """Fotogramma INTERO, rimpicciolito. Nessun ritaglio: un ritaglio sarebbe
    un'affermazione su dove guardare, ed e' esattamente l'affermazione che la
    versione precedente sbagliava."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    return im.resize((width, max(1, int(round(h * width / w)))), Image.LANCZOS)


# --------------------------------------------------------------------------
# FIG 1 e FIG 2 — griglia condizione x seed, fotogrammi interi
# --------------------------------------------------------------------------
def grid(d, roots, prompt, rows, title, subtitle, outfile, expect, panel=300):
    """rows: [(cond_name, etichetta, colore)]
    expect: {cond_name: 'all_lit' | 'all_unlit'} — verificato sui dati PRIMA di
    comporre. Se non torna, lo script si ferma invece di stampare una didascalia
    che i dati smentiscono."""
    for cond, want in expect.items():
        k, n = rate(d, prompt, cond)
        ok = (k == n and n > 0) if want == "all_lit" else (k == 0 and n > 0)
        if not ok:
            raise RuntimeError(
                "RIFIUTO DI COMPORRE %s: %s/%s e' %d/%d acceso, la figura lo "
                "userebbe come '%s'." % (outfile, prompt, cond, k, n, want)
            )

    LM, TOP, GAP, LAB = 210, 94, 12, 40
    sample = whole(find_render(cell(d, prompt, rows[0][0], SEEDS[0]).src_path, roots), panel)
    ph = sample.size[1]
    W = LM + len(SEEDS) * (panel + GAP) + GAP
    H = TOP + len(rows) * (ph + LAB + GAP) + 16

    fig = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(fig)
    dr.text((28, 22), title, font=font(23, True), fill=INK)
    dr.text((28, 54), subtitle, font=font(14), fill=DIM)

    for j, sd in enumerate(SEEDS):
        x = LM + j * (panel + GAP)
        dr.text((x, TOP - 22), "seed %d" % sd, font=font(13), fill=DIM)

    for i, (cond, label, col) in enumerate(rows):
        y = TOP + i * (ph + LAB + GAP)
        k, n = rate(d, prompt, cond)
        dr.text((28, y + 10), label, font=font(17, True), fill=col)
        dr.text((28, y + 36), "%d / %d lit" % (k, n), font=font(22, True), fill=col)
        dr.text((28, y + 66), "blind-scored,", font=font(12), fill=DIM)
        dr.text((28, y + 82), "all five seeds", font=font(12), fill=DIM)
        for j, sd in enumerate(SEEDS):
            r = cell(d, prompt, cond, sd)
            im = whole(find_render(r.src_path, roots), panel)
            x = LM + j * (panel + GAP)
            fig.paste(im, (x, y))
            dr.rectangle([x - 1, y - 1, x + im.size[0], y + im.size[1]], outline=BORDER)
            txt, tcol = verdict(r.lit)
            dr.text((x, y + im.size[1] + 8), txt, font=font(15, True), fill=tcol)

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, outfile)
    fig.save(path, "WEBP", quality=80, method=6)
    print("  %s  %dx%d  %.0f KB" % (outfile, W, H, os.path.getsize(path) / 1024))


# --------------------------------------------------------------------------
# FIG 3 — controllo luminanza, appaiato, su stratificazione PRE-trattamento
# --------------------------------------------------------------------------
def lightness_control(d, roots, outfile, panel=300, max_pairs=4):
    v = d.dropna(subset=["lit", "L_base"]).copy()
    v["tert_pre"] = pd.qcut(v.L_base, 3, labels=["dark", "mid", "light"])

    tab = {}
    for cond in ["baseline", "preset_pos_2x", "blockshuf_neg_2x"]:
        for t in ["dark", "mid", "light"]:
            s = v[(v.cond_name == cond) & (v.tert_pre == t)]
            tab[(cond, t)] = (float(s.lit.mean()) if len(s) else float("nan"), len(s))

    kb, nb = tab[("baseline", "light")][0], tab[("baseline", "light")][1]
    kp, npr = tab[("preset_pos_2x", "light")][0], tab[("preset_pos_2x", "light")][1]
    if not (kp > kb):
        raise RuntimeError(
            "RIFIUTO DI COMPORRE %s: nel terzio piu' chiaro il preset (%.2f) non "
            "supera il baseline (%.2f); la figura afferma il contrario." % (outfile, kp, kb)
        )

    lt = v[v.tert_pre == "light"]
    pairs = []
    for _, b in lt[(lt.cond_name == "baseline") & (lt.lit == 0.0)].sort_values(
            "L_base", ascending=False).iterrows():
        p = v[(v.prompt_id == b.prompt_id) & (v.cond_name == "preset_pos_2x") & (v.seed == b.seed)]
        if len(p) == 1 and p.iloc[0].lit == 1.0:
            pairs.append((b, p.iloc[0]))
    if len(pairs) < 2:
        raise RuntimeError(
            "solo %d coppie (baseline spento -> preset acceso) nel terzio chiaro "
            "pre-trattamento: la figura non regge, va riscritta la sezione." % len(pairs))
    pairs = pairs[:max_pairs]

    GAP, TOP, LAB, BOT = 16, 118, 46, 118
    sample = whole(find_render(pairs[0][0].src_path, roots), panel)
    ph = sample.size[1]
    W = GAP + len(pairs) * (panel + GAP)
    W = max(W, 880)
    H = TOP + 2 * (ph + LAB) + BOT

    fig = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(fig)
    dr.text((24, 20), "The brightest scenes, where a dark-image explanation has nothing to work with",
            font=font(23, True), fill=INK)
    dr.text((24, 52),
            "Top third by the lightness of the UNMODIFIED render — a pre-treatment measure, so the edit "
            "cannot have moved a scene into or out of this stratum.",
            font=font(13), fill=DIM)
    dr.text((24, 72),
            "baseline %.2f lit (n=%d)   ·   preset_pos x2 %.2f lit (n=%d)   ·   blockshuf_neg x2 %.2f lit (n=%d)"
            % (tab[("baseline", "light")][0], tab[("baseline", "light")][1],
               tab[("preset_pos_2x", "light")][0], tab[("preset_pos_2x", "light")][1],
               tab[("blockshuf_neg_2x", "light")][0], tab[("blockshuf_neg_2x", "light")][1]),
            font=font(14, True), fill=ACC)

    for j, (b, p) in enumerate(pairs):
        x = GAP + j * (panel + GAP)
        for i, (row, lbl, col) in enumerate([(b, "baseline", NEG), (p, "preset_pos x2", POS)]):
            y = TOP + i * (ph + LAB)
            im = whole(find_render(row.src_path, roots), panel)
            fig.paste(im, (x, y))
            dr.rectangle([x - 1, y - 1, x + im.size[0], y + im.size[1]], outline=BORDER)
            txt, tcol = verdict(row.lit)
            dr.text((x, y + im.size[1] + 8), "%s  ·  %s" % (lbl, txt), font=font(15, True), fill=col)
            dr.text((x, y + im.size[1] + 27),
                    "%s · seed %s · baseline L*=%.1f" % (row.prompt_id, row.seed, row.L_base),
                    font=font(11), fill=DIM)

    # tabella completa sotto, letta dai dati
    ty = TOP + 2 * (ph + LAB) + 14
    dr.text((24, ty), "rate of lit headlights, by tertile of the unmodified scene's lightness",
            font=font(13, True), fill=INK)
    cols = [("dark", 330), ("mid", 470), ("light", 610)]
    for name, cx in cols:
        dr.text((cx, ty + 22), name, font=font(12, True), fill=DIM)
    for i, (cond, lbl, col) in enumerate([("baseline", "baseline", INK),
                                          ("preset_pos_2x", "preset_pos x2", POS),
                                          ("blockshuf_neg_2x", "blockshuf_neg x2", NEG)]):
        ry = ty + 42 + i * 19
        dr.text((24, ry), lbl, font=font(12, True), fill=col)
        for name, cx in cols:
            m, n = tab[(cond, name)]
            dr.text((cx, ry), "%.2f  (n=%d)" % (m, n), font=font(12), fill=col)

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, outfile)
    fig.save(path, "WEBP", quality=80, method=6)
    print("  %s  %dx%d  %.0f KB" % (outfile, W, H, os.path.getsize(path) / 1024))

    # la tabella serve anche al notebook: la salvo accanto ai dati
    rows_out = []
    for cond in ["baseline", "preset_pos_1x", "preset_pos_2x", "blockshuf_neg_1x",
                 "blockshuf_neg_2x", "rand_pos_1x", "rand_pos_2x"]:
        r = {"condition": cond}
        for t in ["dark", "mid", "light"]:
            s = v[(v.cond_name == cond) & (v.tert_pre == t)]
            r["rate_%s" % t] = round(float(s.lit.mean()), 3) if len(s) else ""
            r["n_%s" % t] = len(s)
        rows_out.append(r)
    out_csv = os.path.join(DATA, "stage9_headlights_pretreatment_strata.csv")
    pd.DataFrame(rows_out).to_csv(out_csv, index=False)
    print("  -> %s" % os.path.basename(out_csv))


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", default=None, help="cartella dei PNG di stage 9")
    args = ap.parse_args()
    roots = render_roots(args.renders)

    d = load_scores()

    print("tassi per stile dallo scoring cieco (acceso / valido):")
    for p in sorted(d.prompt_id.unique()):
        cells = "  ".join(
            "%s %d/%d" % (c.replace("_2x", ""), *rate(d, p, c))
            for c in ["baseline", "preset_pos_2x", "blockshuf_neg_2x"]
        )
        print("  %-15s %s" % (p, cells))
    print()

    # FIG 1 — accensione. Lo stile NON e' scelto a mano: si prende quello che va
    # da 0/n a n/n, e se non esiste la figura non si fa.
    cand = [p for p in sorted(d.prompt_id.unique())
            if rate(d, p, "baseline")[0] == 0
            and rate(d, p, "preset_pos_2x")[1] > 0
            and rate(d, p, "preset_pos_2x")[0] == rate(d, p, "preset_pos_2x")[1]]
    if not cand:
        raise RuntimeError("nessuno stile va da 0/n a n/n sotto preset_pos x2: FIG 1 non ha soggetto")
    # fra i candidati vince quello con piu' immagini SCORABILI (meno "non chiaro"),
    # non quello che mi piace di piu'. A parita', ordine alfabetico.
    p1 = sorted(cand, key=lambda p: (-(rate(d, p, "baseline")[1] + rate(d, p, "preset_pos_2x")[1]), p))[0]
    print("FIG 1 su %s (scelto dai dati fra %s)" % (p1, ", ".join(cand)))
    grid(d, roots, p1,
         [("baseline", "baseline", ACC), ("preset_pos_2x", "preset_pos x2", POS)],
         "Headlights switch on — and the prompt never mentions them",
         "%s · whole frames, nothing cropped · scored blind, condition hidden" % p1,
         "headlights_switch_on.webp",
         expect={"baseline": "all_unlit", "preset_pos_2x": "all_lit"})

    # FIG 2 — spegnimento. Si prende lo stile con piu' fari accesi nel baseline
    # fra quelli che blockshuf_neg x2 porta a zero.
    cand2 = [p for p in sorted(d.prompt_id.unique())
             if rate(d, p, "baseline")[0] >= 2
             and rate(d, p, "blockshuf_neg_2x")[1] > 0
             and rate(d, p, "blockshuf_neg_2x")[0] == 0]
    if not cand2:
        raise RuntimeError("nessuno stile adatto a FIG 2")
    p2 = sorted(cand2, key=lambda p: -rate(d, p, "baseline")[0])[0]
    print("FIG 2 su %s (scelto dai dati fra %s)" % (p2, ", ".join(cand2)))
    grid(d, roots, p2,
         [("baseline", "baseline", ACC), ("blockshuf_neg_2x", "blockshuf_neg x2", NEG)],
         "...and the displacement-matched control switches them off, every time",
         "%s · whole frames, nothing cropped · the unmodified model had them lit" % p2,
         "headlights_switch_off.webp",
         expect={"blockshuf_neg_2x": "all_unlit"})

    # FIG 3 — controllo luminanza pre-trattamento
    print("FIG 3 (stratificazione sulla luminanza PRE-trattamento)")
    lightness_control(d, roots, "headlights_lightness_control.webp")

    print("\nfatto. Le figure sono in assets/02_attribute_emergence/_figures/")


if __name__ == "__main__":
    main()
