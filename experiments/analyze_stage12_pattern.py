# -*- coding: utf-8 -*-
"""
experiments/analyze_stage12_pattern.py

Analisi Statistica dell'Esperimento 12-B: Perceptual Pattern Discrimination (4-AFC)
- Carica data/stage12_pattern_raw.csv (risposte dell'operatore)
- Carica data/stage12_pattern_key.csv (chiave sigillata)
- Calcola:
  1. Successi doppi k_both (entrambe corrette) su N=20 trial
  2. Test Binomiale Esatto ad 1 coda vs H0 (p = 1/12 ~ 0.08333)
  3. Accuratezza marginale Blockshuf_neg_2x vs H0 (p = 0.25)
  4. Accuratezza marginale Preset_pos_2x vs H0 (p = 0.25)
  5. Matrice di confusione completa sulle 4 condizioni
     (focalizzata sul tasso di confusione con blockshuf_neg_1x)
  6. Tempi di reazione medi per trial
  7. Dettaglio per stile artistico
"""

import os
import sys
import csv
import json
import math
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
DATA_DIR = os.path.join(REPORT_ROOT, "data")

KEY_CSV = os.path.join(DATA_DIR, "stage12_pattern_key.csv")
RAW_CSV = os.path.join(DATA_DIR, "stage12_pattern_raw.csv")
OUT_JSON = os.path.join(DATA_DIR, "stage12_pattern_results.json")


def binom_pmf(n, k, p):
    comb = math.comb(n, k)
    return comb * (p ** k) * ((1.0 - p) ** (n - k))


def binom_test_greater(n, k, p):
    """Calcola la p-value ad una coda P(X >= k) sotto B(n, p)."""
    return sum(binom_pmf(n, i, p) for i in range(k, n + 1))


def main():
    print("==================================================================")
    print(" ANALISI STATISTICA ESPERIMENTO 12-B: PATTERN DISCRIMINATION")
    print("==================================================================")

    if not os.path.exists(KEY_CSV):
        raise SystemExit(f"Errore: Chiave non trovata: {KEY_CSV}")
    if not os.path.exists(RAW_CSV):
        raise SystemExit(f"Errore: Risposte non trovate: {RAW_CSV}. Completa prima l'annotazione su viewer/pattern_stage12.html!")

    # 1. Carica chiave
    with open(KEY_CSV, "r", encoding="utf-8-sig") as f:
        key_list = list(csv.DictReader(f))
    key_map = {int(r["trial_id"]): r for r in key_list}

    # 2. Carica risposte
    with open(RAW_CSV, "r", encoding="utf-8-sig") as f:
        raw_list = list(csv.DictReader(f))
    raw_map = {int(r["trial_id"]): r for r in raw_list}

    n_trials = len(key_list)
    n_answered = len(raw_map)
    print(f"Trial pre-registrati: {n_trials} | Risposte registrate: {n_answered}")

    if n_answered < n_trials:
        print(f"[ATTENZIONE] Risposte incomplete ({n_answered}/{n_trials}). Calcolo parziale.")

    # 3. Valutazione
    k_both = 0
    k_blockshuf = 0
    k_preset = 0

    conf_blockshuf = defaultdict(int) # quale condizione era davvero lo slot scelto come blockshuf_2x
    conf_preset = defaultdict(int)    # quale condizione era davvero lo slot scelto come preset_pos_2x

    durations = []
    style_breakdown = defaultdict(lambda: {"total": 0, "both_correct": 0, "b2_correct": 0, "p2_correct": 0})

    for tid, key in key_map.items():
        if tid not in raw_map:
            continue
        ans = raw_map[tid]

        c_b2 = int(key["correct_blockshuf_2x_slot"])
        c_p2 = int(key["correct_preset_pos_2x_slot"])

        u_b2 = int(ans["chosen_blockshuf_2x_slot"])
        u_p2 = int(ans["chosen_preset_pos_2x_slot"])

        cond_at_u_b2 = key.get(f"slot_{u_b2}_cond", "unknown")
        cond_at_u_p2 = key.get(f"slot_{u_p2}_cond", "unknown")

        conf_blockshuf[cond_at_u_b2] += 1
        conf_preset[cond_at_u_p2] += 1

        b2_ok = (u_b2 == c_b2)
        p2_ok = (u_p2 == c_p2)
        both_ok = (b2_ok and p2_ok)

        if b2_ok:
            k_blockshuf += 1
        if p2_ok:
            k_preset += 1
        if both_ok:
            k_both += 1

        dur = float(ans.get("duration_ms", 0))
        if dur > 0:
            durations.append(dur)

        st = key["style_id"]
        style_breakdown[st]["total"] += 1
        if both_ok:
            style_breakdown[st]["both_correct"] += 1
        if b2_ok:
            style_breakdown[st]["b2_correct"] += 1
        if p2_ok:
            style_breakdown[st]["p2_correct"] += 1

    # 4. Statistica Primaria (Entrambe corrette)
    p_both_h0 = 1.0 / 12.0
    pval_both = binom_test_greater(n_answered, k_both, p_both_h0)
    chance_exp_both = n_answered * p_both_h0

    # Statistiche Marginali
    p_marg_h0 = 0.25
    pval_b2 = binom_test_greater(n_answered, k_blockshuf, p_marg_h0)
    pval_p2 = binom_test_greater(n_answered, k_preset, p_marg_h0)

    print("\n--- RISULTATI STATISTICI PRIMARI ---")
    print(f"1. Successo Congiunto (Dual 4-AFC): {k_both} / {n_answered} ({k_both/n_answered*100:.1f}%)")
    print(f"   Atteso dal caso puro (H0: p = 1/12): {chance_exp_both:.2f} successi")
    print(f"   Test Binomiale Esatto ad 1 coda: p = {pval_both:.6e}")
    if pval_both < 0.001:
        print("   ESITO: *** SIGNIFICATIVITÀ ESTREMA (p < 0.001) ***")
    elif pval_both < 0.01:
        print("   ESITO: ** ALTAMENTE SIGNIFICATIVO (p < 0.01) **")
    elif pval_both < 0.05:
        print("   ESITO: * SIGNIFICATIVO (p < 0.05) *")
    else:
        print("   ESITO: Non significativo (H0 non respinta)")

    print(f"\n2. Accuratezza Marginale Blockshuf_neg_2x: {k_blockshuf} / {n_answered} ({k_blockshuf/n_answered*100:.1f}%)")
    print(f"   Atteso dal caso puro (H0: p = 0.25): {n_answered*0.25:.1f} | p = {pval_b2:.6e}")

    print(f"\n3. Accuratezza Marginale Preset_pos_2x: {k_preset} / {n_answered} ({k_preset/n_answered*100:.1f}%)")
    print(f"   Atteso dal caso puro (H0: p = 0.25): {n_answered*0.25:.1f} | p = {pval_p2:.6e}")

    print("\n--- MATRICE DI CONFUSIONE PERCEZIONI ---")
    print("Quando l'operatore ha indicato 'Blockshuf_neg_2x', la cella reale era:")
    for cond in ["blockshuf_neg_2x", "blockshuf_neg_1x", "baseline", "preset_pos_2x"]:
        cnt = conf_blockshuf[cond]
        pct = (cnt / n_answered) * 100 if n_answered > 0 else 0
        tag = " <- TARGET CORRETTO" if cond == "blockshuf_neg_2x" else (" <- NEAR FOIL (DOSAGGIO)" if cond == "blockshuf_neg_1x" else "")
        print(f"   * {cond:<18}: {cnt:>2} / {n_answered} ({pct:>5.1f}%){tag}")

    print("\nQuando l'operatore ha indicato 'Preset_pos_2x', la cella reale era:")
    for cond in ["preset_pos_2x", "baseline", "blockshuf_neg_1x", "blockshuf_neg_2x"]:
        cnt = conf_preset[cond]
        pct = (cnt / n_answered) * 100 if n_answered > 0 else 0
        tag = " <- TARGET CORRETTO" if cond == "preset_pos_2x" else ""
        print(f"   * {cond:<18}: {cnt:>2} / {n_answered} ({pct:>5.1f}%){tag}")

    if durations:
        avg_dur = sum(durations) / len(durations) / 1000.0
        print(f"\nTempo medio per trial: {avg_dur:.1f} secondi (Totale sessione: {sum(durations)/1000.0/60.0:.1f} min)")

    print("\n--- DETTAGLIO PER STILE ARTISTICO ---")
    print(f"{'Stile':<16} | {'Tot':<3} | {'Both OK':<7} | {'B2 OK':<5} | {'P2 OK':<5}")
    print("-" * 48)
    for st, v in sorted(style_breakdown.items()):
        print(f"{st:<16} | {v['total']:<3} | {v['both_correct']:<7} | {v['b2_correct']:<5} | {v['p2_correct']:<5}")

    # Salva JSON
    out_data = {
        "n_trials": n_trials,
        "n_answered": n_answered,
        "k_both": k_both,
        "p_both_h0": p_both_h0,
        "pval_both": pval_both,
        "k_blockshuf_2x": k_blockshuf,
        "pval_blockshuf_2x": pval_b2,
        "k_preset_pos_2x": k_preset,
        "pval_preset_pos_2x": pval_p2,
        "confusion_blockshuf_2x": dict(conf_blockshuf),
        "confusion_preset_pos_2x": dict(conf_preset),
        "style_breakdown": dict(style_breakdown)
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)
    print(f"\n[OK] Risultati esportati in: {OUT_JSON}")


if __name__ == "__main__":
    main()
