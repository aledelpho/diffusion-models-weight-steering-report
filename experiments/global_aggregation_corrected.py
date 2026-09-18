# -*- coding: utf-8 -*-
"""
experiments/global_aggregation_corrected.py

Versione corretta di global_statistical_aggregation.py. Le feature e l'impianto
sono quelli di Antigravity e restano; cambiano cinque cose, e la prima da sola
riscrive quasi tutti i p-value.

1. L'UNITA' DI ANALISI. L'originale tratta 30 celle (6 prompt x 5 seed) come 30
   osservazioni indipendenti, df = 29. Non lo sono: i cinque seed dentro un
   prompt sono misure ripetute dello STESSO soggetto, non repliche indipendenti
   dell'effetto. Quanto siano ridondanti lo dice l'ICC che lo script stesso
   stampa nella sezione 3: da 0.66 a 0.95. Con ICC 0.95 e k = 5 il design effect
   e' 1 + 4*0.95 = 4.8, cioe' l'informazione indipendente vale n ~ 6, non 30, e
   ogni t e' gonfiato di circa 2.2 volte.

   Le conseguenze non sono cosmetiche: "PC1 Block+ vs Rand+" passa da t = -2.30
   (p = 0.041) a t = -1.05, non significativo. Idem per i due contrasti sui
   contorni che coinvolgono Rand+. Spariscono esattamente i risultati marginali,
   che sono quelli su cui si stava decidendo qualcosa. I t enormi (10-17)
   sopravvivono con margine.

   Qui si aggrega PRIMA sui seed -- una media per (prompt, condizione) -- e si
   testa sui prompt. E' il caso conservativo e corretto: il prompt e' l'unita' su
   cui si vuole generalizzare.

2. IL CONTRASTO "ASIMMETRIA" E' LA SIMMETRIA. La formula
   Preset+ + Preset- - 2*Base vale 2*S, cioe' la parte PARI, quella che NON
   cambia segno invertendo l'intervento. La parte antisimmetrica e'
   Preset+ - Preset-. Il nome dice l'opposto del calcolo. Qui si riportano
   entrambe, con i nomi giusti.

3. LA PCA SULLE FEATURE GREZZE TROVA I PROMPT, NON GLI INTERVENTI. I sei prompt
   hanno tinte monocromatiche diverse per costruzione, e infatti PC1 pesa
   color_n_effective, color_top4_cluster_share, entropia dei cluster di colore:
   e' l'asse "quale personaggio e'". Un contrasto su quell'asse misura di quanto
   l'intervento sposta lungo una direzione definita dalla varianza FRA soggetti.
   Qui la PCA e' calcolata sulle DIFFERENZE dalla baseline appaiata, cosi' gli
   assi sono assi di effetto.

4. L'ICC MISURA LA COSA SBAGLIATA. Calcolata sul valore grezzo, dice se la
   feature e' stabile fra seed a parita' di soggetto -- ed e' alta anche per la
   Baseline, che non ha nessun intervento. Per dire "il seed non disturba
   l'effetto" va calcolata sulla DIFFERENZA dalla baseline appaiata.

5. NIENTE CORREZIONE PER MOLTEPLICITA' E PERMUTAZIONI TROPPO POCHE. Trenta test
   senza Holm. E con 1000 permutazioni il p non scende sotto 0.001, quindi tutti
   gli "0.0010***" sono solo "sotto la risoluzione" e non sono confrontabili fra
   loro. Con n prompt <= 12 le permutazioni di segno si enumerano TUTTE (2^n), e
   allora il p e' esatto -- ma si vede anche il suo limite: con 10 prompt il p
   minimo possibile e' 2/1024 = 0.002, per quanto grande sia l'effetto.

In piu': si recuperano F1..F4, che l'originale perdeva solo perche' le loro
baseline stanno in stage2_images.csv e non in stage5. Dieci prompt invece di sei.
"""

import os
import csv
import argparse
import itertools
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.decomposition import PCA

# Percorsi portabili: da un clone del repository gli input stanno in ../data,
# sulla macchina dell'autore in comfyui-pilot. Senza questo, "verifica i numeri da
# solo" nel README e' una promessa che il lettore non puo' mantenere.
_HERE = os.path.dirname(os.path.abspath(__file__))
def _first(*cand):
    for c in cand:
        if os.path.isdir(c):
            return c
    return cand[-1]

ROOT = _first(os.path.join(_HERE, os.pardir, "data"),
              r"c:\Users\aless\Desktop\comfyui-pilot")
FEAT = os.path.join(ROOT, "style_features.csv")

# I manifest che compongono il corpus dell'Esperimento 1.
#
# CORREZIONE. Le due liste citavano "stage7_images.csv", che in questo
# repository NON esiste: quel nome e' stato ritirato con la pitfall 30 (due
# esperimenti che scrivevano nella stessa cartella con manifest omonimi) e
# sostituito da stage7a_images.csv / stage7b_images.csv, che pero' contengono
# il corpus di CONFERMA (prompt I01..I24, sezioni 1.5-1.6) e non i 6 prompt
# colour-free. I 6 colour-free (S7_01..S7_06) stanno in
# stage6b_pilot_images.csv e non erano caricati da nessuna delle due liste.
#
# Conseguenza del bug: il blocco 2 trovava 0 prompt completi e usciva con un
# warning, e il "pool completo a 24 prompt" era in realta' il solo
# sottoinsieme colour-pinned a 18, con un titolo che dichiarava 24.
MANIFEST_COND = ("stage4_images.csv", "stage5_images.csv",
                 "stage6_images.csv", "stage6b_pilot_images.csv")
MANIFEST_BASE = ("stage2_images.csv", "stage5_images.csv",
                 "stage6_images.csv", "stage6b_pilot_images.csv")
CSV_COND = [os.path.join(ROOT, f) for f in MANIFEST_COND]
CSV_BASE = [os.path.join(ROOT, f) for f in MANIFEST_BASE]
OUT = os.path.join(ROOT, "global_aggregation_corrected.csv")

# Sotto questa soglia un blocco non e' calcolabile. Di default e' un errore
# bloccante e non un warning: regola 5 dell'errors_log, un cancello che conta
# le assenze e prosegue e' un cancello muto.
MIN_PROMPTS = 4

COND_MAP = {
    "Arthemy_Bench_Base.json": "Preset+", "Arthemy_Bench_NEG.json": "Preset-",
    "Arthemy_Bench_BLOCKSHUFFLE.json": "Block+", "Arthemy_Bench_BLOCKSHUFFLE_NEG.json": "Block-",
    "Arthemy_Bench_RANDSIGN.json": "Rand+", "Arthemy_Bench_RANDSIGN_NEG.json": "Rand-",
}
CONDS = ["Preset+", "Preset-", "Block+", "Block-", "Rand+", "Rand-"]

CONTRASTI = [
    ("Preset+  -  Block+", lambda d: d["Preset+"] - d["Block+"]),
    ("Preset+  -  Rand+", lambda d: d["Preset+"] - d["Rand+"]),
    ("Block+   -  Rand+", lambda d: d["Block+"] - d["Rand+"]),
    ("A (odd)   Preset", lambda d: (d["Preset+"] - d["Preset-"]) / 2),
    ("A (odd)   Block", lambda d: (d["Block+"] - d["Block-"]) / 2),
    ("A (odd)   Rand", lambda d: (d["Rand+"] - d["Rand-"]) / 2),
    ("S (even)  Preset", lambda d: (d["Preset+"] + d["Preset-"]) / 2),
]


def audit_manifests(strict=True):
    """Rende visibile quali manifest sono stati effettivamente letti.

    load() salta i file inesistenti con os.path.exists e prosegue: un manifest
    rinominato sparisce dal corpus senza che nulla lo dica. Qui l'assenza si
    vede, e di default ferma l'esecuzione."""
    tutti = sorted(set(CSV_COND) | set(CSV_BASE))
    presenti = [os.path.basename(p) for p in tutti if os.path.exists(p)]
    mancanti = [os.path.basename(p) for p in tutti if not os.path.exists(p)]
    print(f"  Manifest letti ({len(presenti)}): {', '.join(presenti)}")
    if mancanti:
        msg = (f"manifest mancanti ({len(mancanti)}): {', '.join(mancanti)} — "
               f"cercati in {os.path.abspath(ROOT)}")
        if strict:
            raise FileNotFoundError(
                msg + ". Il corpus sarebbe incompleto senza dirlo. "
                      "Usa --allow-incomplete solo per un clone parziale.")
        print(f"  [WARNING] {msg}")


def load():
    F = pd.read_csv(FEAT).set_index("file")
    cols = [c for c in F.columns if c not in ("width_px", "height_px", "error")]
    base, cond = {}, {}
    for p in CSV_BASE:
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8-sig")):
                if r.get("operation") == "baseline":
                    base.setdefault((r["prompt_id"], r["seed"]),
                                    os.path.basename(r["image_path"]))
    for p in CSV_COND:
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8-sig")):
                g = COND_MAP.get(r.get("preset_file", ""))
                if g:
                    cond[(r["prompt_id"], r["seed"], g)] = os.path.basename(r["image_path"])
                    if r.get("baseline_path"):
                        base.setdefault((r["prompt_id"], r["seed"]),
                                        os.path.basename(r["baseline_path"]))
    return F, cols, base, cond


def run_analysis(F, cols, base, cond, prompt_list, out_csv, loadings_csv, title,
                 strict=True):
    have = set(F.index)
    seeds = {}
    ok = []
    for p in sorted(prompt_list):
        ss = sorted({s for (pp, s, g) in cond if pp == p}, key=int)
        good = [s for s in ss
                if (p, s) in base and base[(p, s)] in have
                and all((p, s, g) in cond and cond[(p, s, g)] in have for g in CONDS)]
        if len(good) >= 3:
            seeds[p] = good
            ok.append(p)

    print("\n" + "=" * 96)
    print(f"  {title.upper()}")
    print("=" * 96)
    print(f"  Prompts requested: {len(prompt_list)}  "
          f"({', '.join(sorted(prompt_list)) if prompt_list else '-'})")
    print(f"  Prompts complete across all 6 conditions: {len(ok)}  ({', '.join(ok)})")
    print(f"  Seeds per prompt: " + ", ".join(f"{p}:{len(seeds[p])}" for p in ok))
    n_celle = sum(len(seeds[p]) for p in ok)
    print(f"  Images used: {n_celle * (len(CONDS) + 1)}  "
          f"({n_celle} cells x {len(CONDS)} conditions + paired baseline)")
    if len(ok) < MIN_PROMPTS:
        msg = (f"'{title}': {len(ok)} complete prompts out of "
               f"{len(prompt_list)} requested, minimum is {MIN_PROMPTS}. "
               f"This block is not computable and its published CSV is NOT "
               f"being regenerated.")
        if strict:
            raise RuntimeError(msg)
        print(f"  [WARNING] {msg} Skipping.")
        return

    # z-score globale, poi differenza dalla baseline APPAIATA
    Z = (F[cols] - F[cols].mean()) / F[cols].replace(0, np.nan).std().fillna(1.0)
    Z = Z.fillna(0.0)

    cells = []      # (prompt, seed, cond) -> vettore differenza
    for p in ok:
        for s in seeds[p]:
            b = Z.loc[base[(p, s)]].values
            for g in CONDS:
                cells.append((p, s, g, Z.loc[cond[(p, s, g)]].values - b))
    D = np.stack([c[3] for c in cells])

    # PCA sulle DIFFERENZE: gli assi sono assi di effetto, non di soggetto
    pca = PCA(n_components=4).fit(D)
    P = pca.transform(D)
    print("\n  PCA on differences from the paired baseline (effect axes)")
    cum = 0
    loadings_dict = {"feature": cols}
    for i, v in enumerate(pca.explained_variance_ratio_):
        cum += v * 100
        L = pd.Series(pca.components_[i], index=cols)
        loadings_dict[f"PC{i+1}"] = [float(pca.components_[i, cols.index(c)]) for c in cols]
        hi = ", ".join(f"{k} {x:+.2f}" for k, x in L.sort_values(ascending=False).head(3).items())
        lo = ", ".join(f"{k} {x:+.2f}" for k, x in L.sort_values().head(3).items())
        print(f"    PC{i+1}  {v*100:5.2f}%  (cum {cum:5.1f}%)   (+) {hi}   (-) {lo}")

    ldf = pd.DataFrame(loadings_dict)
    var_row = {"feature": "EXPLAINED_VARIANCE_RATIO"}
    for i, v in enumerate(pca.explained_variance_ratio_):
        var_row[f"PC{i+1}"] = round(float(v), 5)
    ldf = pd.concat([pd.DataFrame([var_row]), ldf], ignore_index=True)
    ldf.to_csv(loadings_csv, index=False)
    print(f"    -> Loadings written to: {os.path.basename(loadings_csv)}")

    METR = [("PC1", None), ("PC2", None), ("PC3", None),
            ("stroke_width_median_px", None), ("contour_mean_length_px", None),
            ("contour_n_components", None),
            ("crosshatch_entropy_mean", None), ("fft_radial_slope", None),
            ("color_n_effective", None), ("color_top4_cluster_share", None)]

    def valore(nome, idx):
        if nome.startswith("PC"):
            return P[idx, int(nome[2:]) - 1]
        return D[idx, cols.index(nome)]

    # media sui seed -> una riga per (prompt, condizione)
    per_prompt = {}
    for nome, _ in METR:
        tab = {}
        for p in ok:
            tab[p] = {}
            for g in CONDS:
                v = [valore(nome, i) for i, c in enumerate(cells)
                     if c[0] == p and c[2] == g]
                tab[p][g] = float(np.mean(v))
        per_prompt[nome] = tab

    n = len(ok)
    if n <= 16:
        segni = np.array(list(itertools.product([-1.0, 1.0], repeat=n)), dtype=np.float32)
        print(f"\n  Sign-flip permutation: exact enumeration of {2**n} assignments"
              f"   lowest reachable p {2/2**n:.5f}")
    else:
        rng = np.random.default_rng(42)
        segni = rng.choice([-1.0, 1.0], size=(100000, n)).astype(np.float32)
        print(f"\n  Sign-flip permutation: Monte Carlo over 100,000 assignments (fixed seed)"
              f"   empirical p resolution = {2/100000:.5f}")

    righe = []
    print("\n" + "-" * 96)
    print(f"  CONTRASTS OVER {n} PROMPTS   (seeds averaged within each prompt first)")
    print("-" * 96)
    intestazione = (f"  {'metric':26s}{'contrast':20s}{'delta':>8s}{'CI95':>18s}"
                    f"{'t':>7s}{'dz':>6s}{'p':>8s}{'p Holm':>9s}")
    for nome, _ in METR:
        tab = per_prompt[nome]
        blocco_primari = []
        blocco_descrittivi = []

        # 1. Contrasti primari (famiglia Holm a 3)
        for etichetta, fn in CONTRASTI[:3]:
            x = np.array([fn(tab[p]) for p in ok])
            m, sd = x.mean(), x.std(ddof=1)
            se = sd / np.sqrt(n)
            t = m / se if se > 1e-12 else 0.0
            ci = stats.t.ppf(0.975, n - 1) * se
            if segni is not None:
                mm = (segni * x).mean(1)
                ss = (segni * x).std(1, ddof=1)
                tt = np.where(ss > 1e-12, mm / (ss / np.sqrt(n)), 0.0)
                # un p da permutazione non puo' valere zero: il minimo osservabile
                # e' 1/(N+1). Stamparlo come 0.0 dichiara una precisione inesistente.
                pp = float((np.sum(np.abs(tt) >= abs(t) - 1e-12) + 1) / (len(tt) + 1))
            else:
                pp = float(2 * (1 - stats.t.cdf(abs(t), n - 1)))
            blocco_primari.append([etichetta, m, ci, t, m / sd if sd > 1e-12 else 0.0, pp])

        # Holm sulla famiglia dei 3 primari
        ordine = np.argsort([b[5] for b in blocco_primari])
        k = len(blocco_primari)
        prec = 0.0
        for rank, j in enumerate(ordine):
            adj = min(1.0, max(prec, blocco_primari[j][5] * (k - rank)))
            prec = adj
            blocco_primari[j].append(adj)

        # 2. Componenti descrittive pari/dispari (non soggette a Holm)
        for etichetta, fn in CONTRASTI[3:]:
            x = np.array([fn(tab[p]) for p in ok])
            m, sd = x.mean(), x.std(ddof=1)
            se = sd / np.sqrt(n)
            t = m / se if se > 1e-12 else 0.0
            ci = stats.t.ppf(0.975, n - 1) * se
            if segni is not None:
                mm = (segni * x).mean(1)
                ss = (segni * x).std(1, ddof=1)
                tt = np.where(ss > 1e-12, mm / (ss / np.sqrt(n)), 0.0)
                # un p da permutazione non puo' valere zero: il minimo osservabile
                # e' 1/(N+1). Stamparlo come 0.0 dichiara una precisione inesistente.
                pp = float((np.sum(np.abs(tt) >= abs(t) - 1e-12) + 1) / (len(tt) + 1))
            else:
                pp = float(2 * (1 - stats.t.cdf(abs(t), n - 1)))
            blocco_descrittivi.append([etichetta, m, ci, t, m / sd if sd > 1e-12 else 0.0, pp, np.nan])

        print(intestazione if nome == METR[0][0] else "")
        # Stampa primari
        for et, m, ci, t, dz, pp, adj in blocco_primari:
            star = "***" if adj < 0.005 else ("*" if adj < 0.05 else "")
            print(f"  {nome[:26]:26s}{et:20s}{m:>+8.3f}"
                  f"{f'[{m-ci:+.2f}, {m+ci:+.2f}]':>18s}{t:>+7.2f}{dz:>+6.2f}"
                  f"{pp:>8.4f}{adj:>8.4f}{star}")
            righe.append(dict(metric=nome, contrast=et, delta=round(m, 5),
                              ci_lo=round(m - ci, 5), ci_hi=round(m + ci, 5),
                              t=round(t, 3), dz=round(dz, 3), p=round(pp, 5),
                              p_holm=round(adj, 5), n_prompts=n))
        # Stampa descrittivi
        for et, m, ci, t, dz, pp, _ in blocco_descrittivi:
            print(f"  {'':26s}{et:20s}{m:>+8.3f}"
                  f"{f'[{m-ci:+.2f}, {m+ci:+.2f}]':>18s}{t:>+7.2f}{dz:>+6.2f}"
                  f"{pp:>8.4f}{' (descr)':>9s}")
            righe.append(dict(metric=nome, contrast=et, delta=round(m, 5),
                              ci_lo=round(m - ci, 5), ci_hi=round(m + ci, 5),
                              t=round(t, 3), dz=round(dz, 3), p=round(pp, 5),
                              p_holm="", n_prompts=n))
        print("  " + "-" * 92)

    # ICC sulle DIFFERENZE: "il seed disturba l'effetto?"
    print("\n" + "=" * 96)
    print("  ICC ON DIFFERENCES FROM BASELINE  --  does the seed disturb the EFFECT?")
    print("=" * 96)
    kmin = min(len(seeds[p]) for p in ok)
    print(f"\n  {'metric':28s}" + "".join(f"{g:>10s}" for g in ("Preset+", "Block+", "Rand+")))
    for nome, _ in METR:
        out = []
        for g in ("Preset+", "Block+", "Rand+"):
            M = np.array([[float(np.mean([valore(nome, i) for i, c in enumerate(cells)
                                          if c[0] == p and c[1] == s and c[2] == g]))
                           for s in seeds[p][:kmin]] for p in ok])
            nn, kk = M.shape
            gm = M.mean()
            ssr = kk * ((M.mean(1) - gm) ** 2).sum()
            ssc = nn * ((M.mean(0) - gm) ** 2).sum()
            sse = ((M - gm) ** 2).sum() - ssr - ssc
            msr, msc = ssr / (nn - 1), ssc / (kk - 1)
            mse = sse / ((nn - 1) * (kk - 1))
            icc = (msr - mse) / (msr + (kk - 1) * mse + (kk / nn) * (msc - mse)) \
                if abs(msr + (kk - 1) * mse + (kk / nn) * (msc - mse)) > 1e-12 else float("nan")
            out.append(icc)
            righe.append(dict(metric=nome, contrast=f"ICC_diff|{g}",
                              delta=round(float(icc), 4), ci_lo="", ci_hi="", t="",
                              dz="", p="", p_holm="", n_prompts=n))
        print(f"  {nome[:28]:28s}" + "".join(f"{v:>10.3f}" for v in out))

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0].keys()), restval="")
        w.writeheader()
        w.writerows(righe)
    print(f"\n  -> Results written to: {os.path.basename(out_csv)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="degrada a warning i manifest mancanti e i blocchi "
                         "senza abbastanza prompt. Solo per cloni parziali: "
                         "i numeri che ne escono non sono quelli pubblicati.")
    args = ap.parse_args()
    strict = not args.allow_incomplete

    print("=" * 96)
    print("  CORPUS AUDIT")
    print("=" * 96)
    audit_manifests(strict=strict)

    F, cols, base, cond = load()
    prompts_all = sorted({p for p, _s, _g in cond})

    prompts_mono = [p for p in prompts_all if not p.startswith("S7")]
    prompts_color = [p for p in prompts_all if p.startswith("S7")]
    print(f"  Prompt ids in corpus: {len(prompts_all)} "
          f"({len(prompts_mono)} colour-pinned + {len(prompts_color)} colour-free)")

    # 1. Colour-pinned (F1..F4, G1..G6, H01..H08)
    run_analysis(
        F, cols, base, cond, prompts_mono,
        os.path.join(ROOT, "global_aggregation_colour_pinned_18p.csv"),
        os.path.join(ROOT, "pca_loadings_colour_pinned_18p.csv"),
        "1. Colour-pinned subset (F1..F4 + G1..G6 + H01..H08)",
        strict=strict
    )

    # 2. Color Freedom (S7_01..S7_06, manifest stage6b_pilot_images.csv)
    run_analysis(
        F, cols, base, cond, prompts_color,
        os.path.join(ROOT, "global_aggregation_colour_free_6p.csv"),
        os.path.join(ROOT, "pca_loadings_colour_free_6p.csv"),
        "2. Colour-free subset (S7_01..S7_06)",
        strict=strict
    )

    # 3. Globale completo (colour-pinned + colour-free)
    run_analysis(
        F, cols, base, cond, prompts_all,
        os.path.join(ROOT, "global_aggregation_corrected.csv"),
        os.path.join(ROOT, "pca_difference_loadings.csv"),
        "3. Full pool (colour-pinned + colour-free)",
        strict=strict
    )


if __name__ == "__main__":
    main()
