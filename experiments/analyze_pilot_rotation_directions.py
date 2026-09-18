# -*- coding: utf-8 -*-
"""
experiments/analyze_pilot_rotation_directions.py

La domanda che questo script risponde e' l'unica che conti sulle rotazioni:
**la DIREZIONE del cambiamento dipende dal blocco, o solo la sua AMPIEZZA?**

CLIP-Dist non poteva rispondere: e' una distanza senza segno, dice quanto
l'immagine si e' mossa e mai verso dove. Le feature di tratto e palette hanno un
segno, quindi qui si puo'.

TRE COSE CHE measure_pilot_rotation_directions.py NON FA, E CHE CAMBIANO L'ESITO
--------------------------------------------------------------------------------
1. MEDIA SUI QUATTRO ANGOLI PRIMA DI CALCOLARE LA DIREZIONE.
   `groupby(["prompt_id","block"]).mean()` fonde -30, -15, +15, +30 in un unico
   vettore. Se la rotazione e' ANTISIMMETRICA — cioe' se ruotare in un verso
   sposta le feature nel verso opposto rispetto all'altro — quella media le
   CANCELLA, e quel che resta e' rumore piu' la parte simmetrica. Qui i due versi
   si tengono separati e si decompone come nell'Esperimento 1:
       S = (d(+t) + d(-t)) / 2      (parte simmetrica: "quanto", comune ai versi)
       A = (d(+t) - d(-t)) / 2      (parte antisimmetrica: "verso")

2. NESSUNA COERENZA INTERNA AL BLOCCO, QUINDI NESSUN NULLO.
   Un coseno di 0.85 fra due blocchi non significa niente finche' non si sa quanto
   vale il coseno DENTRO un blocco, fra prompt diversi. Se dentro un blocco i
   prompt concordano a 0.30, due blocchi non possono superare 0.30 nemmeno avendo
   la stessa identica direzione vera. E' il pitfall 36 di questo progetto: una
   graduatoria di coerenze misurate con precisioni diverse. Qui si riporta il
   coseno grezzo E quello disattenuato.

3. LA TINTA IN GRADI TRATTATA COME UN NUMERO QUALSIASI.
   `*_hue_deg` e' una coordinata circolare: sottrarla e mediarla linearmente e'
   un errore (nota metodologica della pre-registrazione dello stage 9). Qui ogni
   swatch diventa a* = C cos(h), b* = C sin(h) e la tinta grezza viene scartata.

E due cose che questo script fa perche' il progetto ha gia' pagato per impararle:
- standardizzazione UNA SOLA VOLTA sui dati uniti (pitfall 33);
- ogni risultato riportato sotto ENTRAMBE le convenzioni di centratura, perche'
  il segno di una coerenza si ribalta a seconda della convenzione (pitfall 37).

Unita' di analisi = il prompt (n = 7): i tre report di tiefling si mediano prima
(pitfall 17). Pavimento della permutazione esatta: 2/2^7 = 0.0156 (regola 8).

Scrive data/pilot_rotation_direction_tests.csv.
"""
import os
import itertools

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
DATA = os.path.join(ROOT, "data")

SW = ["paper", "ink"] + ["sw%d" % i for i in range(1, 7)]
BLOCKS = ["Block_%d" % i for i in range(1, 7)]
DROP = {"type", "report", "prompt_id", "seed", "block", "rot_kind", "angle_deg",
        "image_path", "file", "condition", "prompt_dir", "prompt_sha1", "rel_path",
        "width_px", "height_px"}


# ----------------------------------------------------------------- costruzione
def build_spaces():
    st = pd.read_csv(os.path.join(DATA, "pilot_rotations_style_features.csv"))
    pa = pd.read_csv(os.path.join(DATA, "pilot_rotations_palette_features.csv"))
    if len(st) != 225 or len(pa) != 225:
        raise RuntimeError("attese 225 righe per file, trovate %d / %d" % (len(st), len(pa)))

    # image_path e' l'unica chiave pulita e presente in entrambi: nel file palette
    # `seed` e' vuoto ovunque e `block`/`rot_kind` sono vuoti sulle baseline, quindi
    # un ordinamento su quelle colonne non allinea. I metadati si prendono dal file
    # style, che li ha completi.
    if set(st.image_path) != set(pa.image_path):
        raise RuntimeError("style e palette non coprono le stesse immagini")
    if st.image_path.duplicated().any() or pa.image_path.duplicated().any():
        raise RuntimeError("image_path duplicato: la chiave non e' univoca")
    st = st.sort_values("image_path").reset_index(drop=True)
    pa = pa.sort_values("image_path").reset_index(drop=True)
    if not (st.image_path.values == pa.image_path.values).all():
        raise RuntimeError("allineamento fallito dopo l'ordinamento")

    key = ["type", "report", "prompt_id", "seed", "block", "rot_kind", "angle_deg"]
    meta = st[key].copy()

    # spazio TESSITURA: le feature di tratto, nessuna coordinata circolare
    tex_cols = [c for c in st.columns if c not in DROP and st[c].dtype.kind in "fi"]
    TEX = st[tex_cols].copy()

    # spazio PALETTE: L, a*, b*, share per ogni slot + gli scalari, con la tinta
    # convertita analiticamente e MAI usata grezza
    P = {}
    for s in SW:
        L, C, h = pa["%s_L" % s], pa["%s_C" % s], np.deg2rad(pa["%s_hue_deg" % s])
        P["%s_L" % s] = L
        P["%s_a" % s] = C * np.cos(h)
        P["%s_b" % s] = C * np.sin(h)
        frac = "%s_frac" % s if "%s_frac" % s in pa.columns else "%s_share" % s
        if frac in pa.columns:
            P["%s_w" % s] = pa[frac]
    for c in ["subject_frac", "tonal_range", "step_regularity", "effective_steps",
              "top2_mass_share", "chroma_spread"]:
        if c in pa.columns:
            P[c] = pa[c]
    PAL = pd.DataFrame(P)

    # standardizzazione UNA VOLTA SOLA sulle 225 righe unite (pitfall 33)
    def z(df):
        sd = df.std(ddof=0).replace(0, np.nan)
        out = (df - df.mean()) / sd
        return out.fillna(0.0)

    return meta, z(TEX), z(PAL), list(TEX.columns), list(PAL.columns)


def deltas(meta, X):
    """d = trattata - baseline DELLO STESSO REPORT (cosi' i tre seed di tiefling
    usano ciascuno la propria baseline, non una media)."""
    base = {}
    for i in meta.index[meta.type == "baseline"]:
        base[meta.at[i, "report"]] = X.loc[i].values.astype(float)
    rows, idx = [], []
    for i in meta.index[meta.type == "rotX"]:
        rep = meta.at[i, "report"]
        if rep not in base:
            raise RuntimeError("baseline mancante per %s" % rep)
        rows.append(X.loc[i].values.astype(float) - base[rep])
        idx.append(i)
    D = pd.DataFrame(rows, columns=X.columns)
    M = meta.loc[idx, ["report", "prompt_id", "block", "angle_deg"]].reset_index(drop=True)
    return M, D


def sym_antisym(M, D):
    """Per ogni (report, blocco, |angolo|): S e A. Poi media sui report dello
    stesso prompt, cosi' l'unita' resta il prompt."""
    M = M.copy()
    M["absang"] = M.angle_deg.abs()
    S_rows, A_rows, keys = [], [], []
    for (rep, blk, aa), g in M.groupby(["report", "block", "absang"]):
        pos = g.index[g.angle_deg > 0]
        neg = g.index[g.angle_deg < 0]
        if len(pos) != 1 or len(neg) != 1:
            raise RuntimeError("attesa una cella per verso in %s/%s/%s" % (rep, blk, aa))
        dp = D.loc[pos[0]].values
        dn = D.loc[neg[0]].values
        S_rows.append((dp + dn) / 2.0)
        A_rows.append((dp - dn) / 2.0)
        keys.append((rep, M.loc[pos[0], "prompt_id"], blk, aa))
    K = pd.DataFrame(keys, columns=["report", "prompt_id", "block", "absang"])
    S = pd.DataFrame(S_rows, columns=D.columns)
    A = pd.DataFrame(A_rows, columns=D.columns)
    # unita' = prompt (pitfall 17)
    def collapse(V):
        return (pd.concat([K[["prompt_id", "block", "absang"]], V], axis=1)
                .groupby(["prompt_id", "block", "absang"], as_index=False).mean())
    return collapse(S), collapse(A), K


# ----------------------------------------------------------------- statistiche
def cos(u, v):
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    return float(np.dot(u, v) / (nu * nv)) if nu > 1e-12 and nv > 1e-12 else np.nan


def within_coherence(T, cols, block, absang):
    """Coseno medio fra coppie di PROMPT distinti, stesso blocco e stesso angolo.
    E' il tetto che due blocchi non possono superare."""
    g = T[(T.block == block) & (T.absang == absang)]
    V = g[cols].values
    cs = [cos(V[i], V[j]) for i, j in itertools.combinations(range(len(V)), 2)]
    return float(np.nanmean(cs)), len(V)


def block_mean_dir(T, cols, block, absang):
    g = T[(T.block == block) & (T.absang == absang)]
    return g[cols].values.mean(0)


def signflip(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    n = len(v); obs = float(v.mean())
    S = np.array(list(itertools.product([1, -1], repeat=n)))
    return obs, float((np.abs((S * v).mean(1)) >= abs(obs) - 1e-12).mean()), 2 / 2 ** n, n


def analyse(space_name, T_S, T_A, cols, rows, centered_label):
    print("\n" + "=" * 78)
    print(" SPAZIO %s   (%d dimensioni, centratura: %s)" % (space_name, len(cols), centered_label))
    print("=" * 78)

    for absang in sorted(T_S.absang.unique()):
        print("\n  --- angolo %g gradi ---" % absang)

        # 1. quanto della risposta e' ANTISIMMETRICA
        nS = [np.linalg.norm(block_mean_dir(T_S, cols, b, absang)) for b in BLOCKS]
        nA = [np.linalg.norm(block_mean_dir(T_A, cols, b, absang)) for b in BLOCKS]
        print("  ampiezza del vettore medio per blocco (||S|| simmetrica / ||A|| antisimmetrica):")
        for b, a_, s_ in zip(BLOCKS, nA, nS):
            share = a_ / (a_ + s_) if (a_ + s_) > 0 else np.nan
            print("    %-9s ||S||=%6.3f  ||A||=%6.3f   quota antisimmetrica %.2f" % (b, s_, a_, share))
            rows.append(dict(space=space_name, centering=centered_label, angle=absang,
                             test="norme_S_A", block=b, value_S=round(s_, 4), value_A=round(a_, 4),
                             stat=round(share, 4), p="", floor=""))

        # 2. coerenza DENTRO il blocco (il tetto) e FRA blocchi (il confronto)
        for label, T in [("A (verso)", T_A), ("S (quanto)", T_S)]:
            wc = {}
            for b in BLOCKS:
                c, n = within_coherence(T, cols, b, absang)
                wc[b] = c
            pairs = []
            for b1, b2 in itertools.combinations(BLOCKS, 2):
                raw = cos(block_mean_dir(T, cols, b1, absang), block_mean_dir(T, cols, b2, absang))
                den = np.sqrt(max(wc[b1], 0) * max(wc[b2], 0))
                dis = raw / den if den > 1e-6 else np.nan
                pairs.append((b1, b2, raw, dis))
            mw = float(np.nanmean(list(wc.values())))
            mr = float(np.nanmean([p[2] for p in pairs]))
            md = float(np.nanmean([p[3] for p in pairs]))
            print("  componente %s:" % label)
            print("    coerenza DENTRO il blocco, media fra prompt : %+.3f   (per blocco: %s)"
                  % (mw, "  ".join("%s %+.2f" % (b.replace("Block_", "B"), wc[b]) for b in BLOCKS)))
            print("    coseno FRA blocchi, grezzo                  : %+.3f" % mr)
            print("    coseno FRA blocchi, disattenuato            : %+.3f%s"
                  % (md, "   <- >=1 significa: nessuna differenza di direzione rilevabile"
                     if md >= 0.95 else ""))
            rows.append(dict(space=space_name, centering=centered_label, angle=absang,
                             test="coerenza_%s" % label.split()[0], block="",
                             value_S=round(mw, 4), value_A=round(mr, 4), stat=round(md, 4),
                             p="", floor=""))

            # 3. il test: la direzione di un blocco predice se stessa meglio di
            #    quanto predica gli altri? Unita' = prompt.
            v = []
            for pr in sorted(T.prompt_id.unique()):
                same, other = [], []
                for b in BLOCKS:
                    g = T[(T.block == b) & (T.absang == absang)]
                    mine = g[g.prompt_id == pr][cols].values
                    rest = g[g.prompt_id != pr][cols].values
                    if not len(mine) or not len(rest):
                        continue
                    same.append(cos(mine[0], rest.mean(0)))
                    for b2 in BLOCKS:
                        if b2 == b:
                            continue
                        g2 = T[(T.block == b2) & (T.absang == absang)]
                        r2 = g2[g2.prompt_id != pr][cols].values
                        if len(r2):
                            other.append(cos(mine[0], r2.mean(0)))
                v.append(np.nanmean(same) - np.nanmean(other))
            obs, p, fl, n = signflip(v)
            print("    stesso-blocco meno altri-blocchi            : %+.3f   p = %.4f (pavimento %.4f, n = %d)"
                  % (obs, p, fl, n))
            rows.append(dict(space=space_name, centering=centered_label, angle=absang,
                             test="stesso_meno_altri_%s" % label.split()[0], block="",
                             value_S="", value_A="", stat=round(obs, 4),
                             p=round(p, 4), floor=round(fl, 4)))



# --------------------------------------------------------------- i due decisivi
def spearman(x, y):
    rx = pd.Series(x).rank().values
    ry = pd.Series(y).rank().values
    return float(np.corrcoef(rx, ry)[0, 1])


def holm(ps):
    order = np.argsort(ps)
    out = [0.0] * len(ps)
    for rank, i in enumerate(order):
        out[i] = min(1.0, max(ps[order[j]] * (len(ps) - j) for j in range(rank + 1)))
    return out


def decisive(space_name, T_S, T_A, cols, rows):
    """DUE domande, in quest'ordine, perche' la seconda ha senso solo se la prima
    ha una risposta scomoda.

    1. La coerenza di un blocco misura una sua proprieta', o solo il fatto che si
       muove di piu'? Se coerenza e ampiezza sono ordinate allo stesso modo, la
       frase "Block_6 ha una direzione e i centrali no" e' una frase sul rapporto
       segnale/rumore, non sul modello (pitfall 36).

    2. Allora si confrontano SOLO i blocchi misurati abbastanza bene da poter
       essere confrontati (coerenza > 0.25), con un test appaiato per prompt: il
       vettore di un prompt sotto il blocco X somiglia agli ALTRI prompt sotto X
       piu' di quanto somigli agli altri prompt sotto Y? Questo non e' spiegabile
       dall'ampiezza, perche' entrambi i blocchi sono ben misurati.
    """
    print("\n" + "=" * 78)
    print(" DECISIVO — %s" % space_name)
    print("=" * 78)

    for comp, T in [("A (verso)", T_A), ("S (quanto)", T_S)]:
        for aa in sorted(T.absang.unique()):
            amp = [np.linalg.norm(block_mean_dir(T, cols, b, aa)) for b in BLOCKS]
            coh = [within_coherence(T, cols, b, aa)[0] for b in BLOCKS]
            r = spearman(amp, coh)
            print("  1) %s %2gdeg  Spearman(ampiezza, coerenza) = %+.3f%s"
                  % (comp, aa, r, "   <- la coerenza segue l'ampiezza" if r > 0.8 else ""))
            rows.append(dict(space=space_name, centering="", angle=aa,
                             test="spearman_ampiezza_coerenza_%s" % comp.split()[0],
                             block="", value_S="", value_A="", stat=round(r, 4), p="", floor=""))

    print()
    res = []
    for comp, T in [("A (verso)", T_A)]:
        for aa in sorted(T.absang.unique()):
            coh = {b: within_coherence(T, cols, b, aa)[0] for b in BLOCKS}
            good = [b for b in BLOCKS if coh[b] > 0.25]
            if len(good) < 2:
                print("  2) %s %2gdeg: meno di due blocchi misurabili, test impossibile" % (comp, aa))
                continue
            print("  2) %s %2gdeg  blocchi con coerenza > 0.25: %s"
                  % (comp, aa, ", ".join("%s(%+.2f)" % (b, coh[b]) for b in good)))
            for b1, b2 in itertools.combinations(good, 2):
                v = []
                for pr in sorted(T.prompt_id.unique()):
                    g1 = T[(T.block == b1) & (T.absang == aa)]
                    g2 = T[(T.block == b2) & (T.absang == aa)]
                    mine = g1[g1.prompt_id == pr][cols].values
                    o1 = g1[g1.prompt_id != pr][cols].values
                    o2 = g2[g2.prompt_id != pr][cols].values
                    if len(mine) and len(o1) and len(o2):
                        v.append(cos(mine[0], o1.mean(0)) - cos(mine[0], o2.mean(0)))
                obs, p, fl, n = signflip(v)
                res.append((space_name, comp, aa, b1, b2, obs, p, fl, sum(x > 0 for x in v), n))
                print("     %s vs %s: vantaggio stesso-blocco %+.3f  p = %.4f (pavimento %.4f)  %d/%d concordi"
                      % (b1, b2, obs, p, fl, sum(x > 0 for x in v), n))

    if res:
        hs = holm([r[6] for r in res])
        print("\n  Holm sulla famiglia dei %d confronti (NON dichiarata in anticipo):" % len(res))
        for r, h in zip(res, hs):
            print("     %s %s vs %s: p %.4f -> Holm %.4f%s"
                  % (r[0], r[3], r[4], r[6], h, "" if h <= 0.05 else "   <- cade"))
            rows.append(dict(space=r[0], centering="", angle=r[2],
                             test="appaiato_%s_vs_%s" % (r[3], r[4]), block="",
                             value_S="", value_A="", stat=round(r[5], 4),
                             p=round(r[6], 4), floor=round(r[7], 4)))
        print("\n  IL PUNTO CHE DECIDE, E CHE NON E' STATO DECISO IN ANTICIPO.")
        print("  Con n = 7 il pavimento e' 0.0156, quindi Holm regge al massimo TRE test")
        print("  nella stessa famiglia: 0.0156 x 3 = 0.0469 passa, x 4 = 0.0625 no.")
        print("  Qui i confronti sono %d per spazio. Se tessitura e palette sono due" % len(res))
        print("  famiglie separate (come le dichiara la pre-registrazione dello stage 9),")
        print("  i tre confronti di tessitura passano a 0.0469 — sul filo. Se sono una")
        print("  famiglia sola, sono quattro e non passa niente. La famiglia non e' mai")
        print("  stata dichiarata, quindi il risultato sta esattamente sul confine che")
        print("  quella dichiarazione avrebbe deciso. E' un'ipotesi da pre-registrare,")
        print("  non un risultato da citare.")


def main():
    meta, TEX, PAL, tex_cols, pal_cols = build_spaces()
    rows = []
    for space, X, cols in [("TESSITURA", TEX, tex_cols), ("PALETTE", PAL, pal_cols)]:
        M, D = deltas(meta, X)
        for centered, lab in [(False, "nessuna (grezza)"), (True, "media generale sottratta")]:
            Dc = D - D.mean() if centered else D
            T_S, T_A, _ = sym_antisym(M, Dc)
            analyse(space, T_S, T_A, cols, rows, lab)
            if not centered:
                # la componente A e' invariante alla convenzione di centratura
                # (sottrarre una costante a tutti i delta si cancella in
                # (d+ - d-)/2), quindi i test decisivi girano una volta sola
                decisive(space, T_S, T_A, cols, rows)

    out = os.path.join(DATA, "pilot_rotation_direction_tests.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    print("\n-> %s" % os.path.basename(out))


if __name__ == "__main__":
    main()
