# -*- coding: utf-8 -*-
"""
experiments/analyze_pilot_rotations_followup.py

Controllo indipendente di analyze_pilot_rotations.py, scritto il 2026-09-18 dopo
aver riprodotto i suoi numeri (che sono corretti) e aver trovato tre cose che
quell'analisi non fa.

1. NON USA LO SWEEP DI AMPIEZZA.
   extract_pilot_benchmarks.py estrae 216 celle di ampiezza (Block_N ±1.0/±2.0)
   negli stessi 7 prompt, e nessuno le guarda. Sono una perturbazione di tipo
   COMPLETAMENTE DIVERSO dalla rotazione: se il profilo per blocco e' una
   proprieta' della posizione e non della rotazione, deve ricomparire li'.
   Ricompare per Block_6 e NON ricompare per Block_1.

2. IL CONTRASTO PRE-REGISTRATO FONDE DUE BLOCCHI CHE NON SI COMPORTANO UGUALE.
   "Estremi (1,6) vs centrali (2-5)" e' stato scritto quando l'unica cosa nota
   era la media di CLIP-Dist. Scomposto, Block_6 e Block_1 hanno firme diverse:
   Block_6 e' alto a ogni dose e in entrambe le famiglie di perturbazione;
   Block_1 e' indistinguibile dai centrali a dose piccola e esplode a dose
   grande, solo nella rotazione.

3. IL RESIDUO SU D NON E' UN OSTACOLO SUPERATO, E' UN OSTACOLO ASSENTE.
   La pendenza della regressione e' positiva (+3.16 su d_model) e Block_6 ha il
   d_model PIU' BASSO dei sei. Condizionare su D puo' quindi solo aumentare
   l'eccesso apparente di Block_6: il test "l'effetto sopravvive alla correzione
   per D" non poteva restituire "no". Il fatto grezzo e' piu' forte e non ha
   bisogno di regressioni: Block_6 muove il modello MENO di tutti e cambia
   l'immagine PIU' di tutti.

Scrive data/pilot_rotations_followup.csv.
Non genera immagini, non tocca il checkpoint: legge solo i CSV gia' pubblicati.
"""
import os
import itertools

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
DATA = os.path.join(ROOT, "data")

CENTRAL = ["Block_2", "Block_3", "Block_4", "Block_5"]
EXTREME = ["Block_1", "Block_6"]


def signflip(v):
    """Permutazione esatta a scambio di segno. Restituisce anche il pavimento,
    perche' con n = 7 e sette segni concordi il test puo' restituire UN SOLO
    valore e riportarlo senza il pavimento accanto e' fuorviante (regola 8)."""
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    n = len(v)
    obs = float(v.mean())
    S = np.array(list(itertools.product([1, -1], repeat=n)))
    null = (S * v).mean(1)
    p = float((np.abs(null) >= abs(obs) - 1e-12).mean())
    return obs, p, 2 / 2 ** n, n, int((v > 0).sum())


def holm(ps):
    order = np.argsort(ps)
    out = [0.0] * len(ps)
    for rank, i in enumerate(order):
        out[i] = min(1.0, max(ps[order[j]] * (len(ps) - j) for j in range(rank + 1)))
    return out


def spearman(x, y):
    rx = pd.Series(x).rank().values
    ry = pd.Series(y).rank().values
    return float(np.corrcoef(rx, ry)[0, 1])


def contrast(df, value, target, reference=CENTRAL):
    """Differenza (target - riferimento) calcolata DENTRO ogni prompt e poi
    testata sui prompt. L'unita' e' il prompt, mai la cella (pitfall 17)."""
    v = []
    for pr in sorted(df.prompt_id.unique()):
        s = df[df.prompt_id == pr]
        a = s[s.block.isin(target)][value].mean()
        b = s[s.block.isin(reference)][value].mean()
        v.append(a - b)
    return v


def main():
    rot = pd.read_csv(os.path.join(DATA, "pilot_rotations.csv"))
    mac = pd.read_csv(os.path.join(DATA, "pilot_macro.csv"))
    dsp = pd.read_csv(os.path.join(DATA, "pilot_rotation_displacement.csv"))

    rx = rot[rot.family == "rotX"].copy()
    if len(rx) != 216:
        raise RuntimeError("attese 216 celle rotX, trovate %d" % len(rx))
    if len(mac) != 216:
        raise RuntimeError("attese 216 celle di ampiezza, trovate %d" % len(mac))

    rx = rx.merge(dsp[["block", "rot_kind", "angle_deg", "d_block", "d_model"]],
                  on=["block", "rot_kind", "angle_deg"], how="left")
    if rx.d_model.isna().any():
        raise RuntimeError("displacement mancante per almeno una cella")

    # unita' = prompt: i tre report di tiefling si mediano PRIMA (pitfall 17)
    R = rx.groupby(["prompt_id", "block", "angle_deg"], as_index=False).agg(
        cd=("clip_dist", "mean"), d_model=("d_model", "first"), d_block=("d_block", "first"))
    M = mac.groupby(["prompt_id", "block", "amplitude"], as_index=False).agg(
        cd=("clip_dist", "mean"))
    if R.prompt_id.nunique() != 7:
        raise RuntimeError("attesi 7 prompt, trovati %d" % R.prompt_id.nunique())

    blocks = sorted(R.block.unique())
    rows = []

    # ------------------------------------------------------------------
    print("=" * 74)
    print(" 1. IL FATTO GREZZO, SENZA REGRESSIONI")
    print("=" * 74)
    print(f"{'blocco':9} {'cd medio':>9} {'d_model@30':>11} {'d_block@30':>11} {'norma base':>11} {'matrici':>8}")
    cm, dm, db = [], [], []
    for b in blocks:
        s = R[R.block == b]
        row = dsp[(dsp.block == b) & (dsp.rot_kind == "rotX") & (dsp.angle_deg == 30)].iloc[0]
        cm.append(s.cd.mean()); dm.append(row.d_model); db.append(row.d_block)
        print(f"{b:9} {s.cd.mean():9.4f} {row.d_model:11.5f} {row.d_block:11.5f} "
              f"{row.base_block_norm:11.1f} {int(row.tensors_touched):8d}")
    cm, dm, db = np.array(cm), np.array(dm), np.array(db)

    keep = [i for i, b in enumerate(blocks) if b in CENTRAL]
    print("\n  Spearman fra blocchi, cd ~ d_model:")
    print("    tutti e sei          rho = %+.3f" % spearman(cm, dm))
    print("    solo i centrali 2-5  rho = %+.3f   <-- fra i centrali il displacement" % spearman(cm[keep], dm[keep]))
    print("                                          spiega l'ordinamento per intero")
    print("  Block_6 ha il d_model PIU' BASSO (%.5f, contro %.5f di Block_2)" % (dm[5], dm[1]))
    print("  e il cd PIU' ALTO (%.4f, contro %.4f di Block_2): %.1fx a fronte di %.0f%% di"
          % (cm[5], cm[1], cm[5] / cm[1], 100 * (1 - dm[5] / dm[1])))
    print("  spostamento in MENO. Nessuna regressione serve a vederlo.")
    rows.append(dict(test="spearman_cd_dmodel_tutti", statistic=round(spearman(cm, dm), 4), p="", floor="", n=6))
    rows.append(dict(test="spearman_cd_dmodel_centrali", statistic=round(spearman(cm[keep], dm[keep]), 4), p="", floor="", n=4))

    # ------------------------------------------------------------------
    print("\n" + "=" * 74)
    print(" 2. I DUE 'ESTREMI' NON SONO LO STESSO FENOMENO")
    print("=" * 74)
    print("  rotazione (angolo) e ampiezza (scala) sono perturbazioni diverse.")
    print(f"  {'famiglia':12} {'dose':>6}  {'bersaglio':10} {'delta vs centrali':>18} {'p':>8} {'pavimento':>10} {'concordi':>9}")
    for fam, df, dosecol, doses in [("rotazione", R, "angle_deg", [15, 30]),
                                    ("ampiezza", M, "amplitude", [1, 2])]:
        for dose in doses:
            sub = df[df[dosecol].abs() == dose]
            for lab, tgt in [("Block_1", ["Block_1"]), ("Block_6", ["Block_6"])]:
                o, p, fl, n, npos = signflip(contrast(sub, "cd", tgt))
                flag = "" if p <= 0.05 else "   <- non significativo"
                print(f"  {fam:12} {dose:>6}  {lab:10} {o:>+18.4f} {p:>8.4f} {fl:>10.4f} {npos:>6}/{n}{flag}")
                rows.append(dict(test=f"{fam}_dose{dose}_{lab}_vs_centrali",
                                 statistic=round(o, 4), p=round(p, 4), floor=round(fl, 4), n=n))
    print("\n  Block_6: alto in ENTRAMBE le famiglie e a ogni dose utile -> replica interna.")
    print("  Block_1: assente nell'ampiezza (p = 0.09 a dose 2, 5 prompt su 7) e con un")
    print("           rapporto dose 15->30 di x3.1 contro x1.4 dei centrali -> non e' una")
    print("           proprieta' della posizione, e' una rottura a grande angolo.")

    print("\n  rapporto dose-risposta (la firma che separa i due):")
    for b in blocks:
        s = R[R.block == b]
        c15 = s[s.angle_deg.abs() == 15].cd.mean(); c30 = s[s.angle_deg.abs() == 30].cd.mean()
        sm = M[M.block == b]
        a1 = sm[sm.amplitude.abs() == 1].cd.mean(); a2 = sm[sm.amplitude.abs() == 2].cd.mean()
        print(f"    {b}: rotazione x{c30/c15:.2f}   ampiezza x{a2/a1:.2f}")

    # ------------------------------------------------------------------
    print("\n" + "=" * 74)
    print(" 3. IL CONTRASTO PRE-REGISTRATO, RIPORTATO COM'E' E POI SCOMPOSTO")
    print("=" * 74)
    o, p, fl, n, npos = signflip(contrast(R, "cd", EXTREME))
    print(f"  pre-registrato, estremi(1,6) vs centrali: {o:+.4f}  p = {p:.4f}  pavimento {fl:.4f}  {npos}/{n}")
    print("  Passa. Va riportato cosi', perche' era congelato. Ma p e' ESATTAMENTE il")
    print("  pavimento: con 7 prompt concordi il test non puo' restituire altro, quindi")
    print("  non distingue un effetto enorme da uno appena consistente (regola 8).")
    rows.append(dict(test="prereg_estremi_vs_centrali", statistic=round(o, 4), p=round(p, 4), floor=round(fl, 4), n=n))

    # ------------------------------------------------------------------
    print("\n" + "=" * 74)
    print(" 4. ANTISIMMETRIA: ESPLORATIVA, E NON E' LA DECOMPOSIZIONE DELL'ESPERIMENTO 1")
    print("=" * 74)
    print("  CLIP-Dist e' una distanza SENZA SEGNO dal baseline. A = d(+t) - d(-t) dice")
    print("  'un verso sposta piu' dell'altro', non 'i due versi vanno in direzioni")
    print("  opposte'. La decomposizione S/A dell'Esperimento 1 opera su proiezioni CON")
    print("  segno: una distanza senza segno non puo' vedere un compromesso (pitfall 2).")
    ps, labs, stats = [], [], []
    for b in blocks:
        v = []
        for pr in sorted(R.prompt_id.unique()):
            s = R[(R.prompt_id == pr) & (R.block == b)]
            v.append(s[s.angle_deg > 0].cd.mean() - s[s.angle_deg < 0].cd.mean())
        o2, p2, fl2, n2, _ = signflip(v)
        ps.append(p2); labs.append(b); stats.append(o2)
    hs = holm(ps)
    print(f"\n  {'blocco':9} {'A':>9} {'p grezzo':>9} {'p Holm(6)':>10}")
    for b, st, p2, h in zip(labs, stats, ps, hs):
        mark = "" if h <= 0.05 else "   <- cade con Holm"
        print(f"  {b:9} {st:+9.4f} {p2:9.4f} {h:10.4f}{mark}")
        rows.append(dict(test=f"antisimmetria_{b}_esplorativa", statistic=round(st, 4),
                         p=round(p2, 4), floor=round(2/2**7, 4), n=7))
    print("\n  Nessuno dei sei sopravvive a Holm. Erano sei test non previsti dal brief:")
    print("  vanno riportati come descrittivi. E l'antisimmetria globale e' concentrata")
    print("  nei due blocchi anomali, quindi non e' una proprieta' generale delle")
    print("  rotazioni ma un'altra faccia della stessa anomalia.")

    # ------------------------------------------------------------------
    print("\n" + "=" * 74)
    print(" 5. RUMORE DI SEED — l'unica stima disponibile in tutto lo sweep")
    print("=" * 74)
    t = rot[(rot.family == "rotX") & (rot.prompt_id == "tiefling")]
    sd = t.groupby(["block", "angle_deg"]).clip_dist.std()
    eff = R[R.block == "Block_6"].cd.mean() - R[R.block.isin(CENTRAL)].cd.mean()
    print("  tiefling ha 3 seed; tutti gli altri prompt ne hanno UNO.")
    print("  sd fra seed, mediana sulle 24 celle: %.4f" % sd.median())
    print("  scarto Block_6 - centrali: %.4f  ->  circa %.0f volte il rumore di seed" % (eff, eff / sd.median()))
    print("  Block_1 ha la sd fra seed piu' alta di tutti (%.4f): oltre a essere alto a"
          % t[t.block == "Block_1"].groupby("angle_deg").clip_dist.std().mean())
    print("  30 gradi, e' anche il piu' instabile, che e' coerente con una rottura.")
    rows.append(dict(test="sd_seed_mediana_tiefling", statistic=round(float(sd.median()), 4), p="", floor="", n=24))
    rows.append(dict(test="block6_meno_centrali", statistic=round(float(eff), 4), p="", floor="", n=7))

    out = os.path.join(DATA, "pilot_rotations_followup.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    print("\n-> %s" % os.path.basename(out))


if __name__ == "__main__":
    main()
