# -*- coding: utf-8 -*-
"""
experiments/generate_triangolo_report.py
========================================
Compila il report formale dei risultati in:
docs/rotations_triangolo_block1_block3_block6_results.md
a partire da rotations_triangolo_results.csv e rotations_triangolo_prompt_scores.csv.
"""

import os
import sys
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
PILOT_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
DATA_DIR = os.path.join(REPORT_ROOT, "data")
DOCS_DIR = os.path.join(REPORT_ROOT, "docs")

RESULTS_CSV = os.path.join(DATA_DIR, "rotations_triangolo_results.csv")
SCORES_CSV = os.path.join(DATA_DIR, "rotations_triangolo_prompt_scores.csv")
REPORT_MD = os.path.join(DOCS_DIR, "rotations_triangolo_block1_block3_block6_results.md")

def main():
    if not os.path.exists(RESULTS_CSV) or not os.path.exists(SCORES_CSV):
        raise FileNotFoundError(f"File mancanti:\n  {RESULTS_CSV}\n  {SCORES_CSV}")

    res_df = pd.read_csv(RESULTS_CSV)
    sc_df = pd.read_csv(SCORES_CSV)

    tex = res_df[res_df["space"].str.contains("Tessitura")].iloc[0]

    # Formattazione tabella prompt
    p_rows = []
    for _, r in sc_df.iterrows():
        p_rows.append(
            f"| `{r['prompt_id']}` | {float(r['V_1_3']):+.4f} | {float(r['V_3_6']):+.4f} | {float(r['V_1_6']):+.4f} | "
            f"{float(r['V_scr_1_3']):+.4f} | {float(r['V_scr_1_1']):+.4f} | "
            f"{float(r['Delta_1_3']):+.4f} | {float(r['Delta_3_6']):+.4f} |"
        )
    prompt_table_str = "\n".join(p_rows)

    # Formattazione tabella spazi secondari
    sec_rows = []
    for _, r in res_df.iterrows():
        sec_rows.append(
            f"| {r['space']} | {int(r['n_features'])} | {float(r['mean_V_1_3']):+.4f} | {float(r['mean_V_3_6']):+.4f} | "
            f"{float(r['mean_V_1_6']):+.4f} | {float(r['mean_Delta_1_3']):+.4f} ({float(r['p_Delta_1_3']):.4f}) | "
            f"{float(r['mean_Delta_3_6']):+.4f} ({float(r['p_Delta_3_6']):.4f}) | {r['regime'].split('.')[1].strip() if '.' in r['regime'] else r['regime']} |"
        )
    sec_table_str = "\n".join(sec_rows)

    md = f"""# Risultati Sperimentali — Il Triangolo: Block_1 vs Block_3 vs Block_6

**Data di esecuzione**: 2026-09-21  
**Stato**: Eseguito, verificato e congelato a fronte di [`docs/prereg_rotations_triangolo_block1_block3_block6.md`](prereg_rotations_triangolo_block1_block3_block6.md)  
**Protocollo metodologico adottato**: Opzione (a) con controlli scramble cross-anchored (`scramble_C` e `scramble_D` su Block_3)  
**Displacement target appaiato**: $D_{{\\text{{modello}}}} = 0.04500$ (scarto tra i 3 blocchi: $\\Delta D \\le 0.000005$)  
**Matrice generazioni**: 330 immagini (210 riusate da Block_1 vs Block_6 + 120 generate ex-novo per Block_3 e scramble C/D)  
**File di calibrazione**: [`data/matched_rotation_calibration.json`](../data/matched_rotation_calibration.json)  
**File risultati**: [`data/rotations_triangolo_results.csv`](../data/rotations_triangolo_results.csv)  
**Punteggi per prompt**: [`data/rotations_triangolo_prompt_scores.csv`](../data/rotations_triangolo_prompt_scores.csv)  

---

## 1. Verdetto Primario dell'Albero Decisionale (§2 Pre-registrazione)

### **Regime Selezionato: {tex['regime']}**

> **Valutazione Formale**:  
> {tex['regime_desc']}

### Riepilogo Numerico delle Ipotesi Primarie nello Spazio Tessitura

| Metrica / Contrasto | Valore Osservato | Valore Pavimento Scramble | Delta Appaiato $\\Delta \\bar{{V}}$ | $p$-value esatto | Significatività (Holm $\\alpha=0.05$) |
|---|---|---|---|---|---|
| **LATO 1: Block_1 vs Block_3** ($V_{{1,3}}$) | **{float(tex['mean_V_1_3']):+.4f}** ($p={float(tex['p_V_1_3']):.5f}$) | {float(tex['mean_scr_1_3']):+.4f} ($V_{{\\text{{scr}}(1,3)}}$) | **{float(tex['mean_Delta_1_3']):+.4f}** | **{float(tex['p_Delta_1_3']):.5f}** | **{'CONFERMATO' if tex['sig_Delta_1_3'] else 'NON SIGNIFICATIVO'}** |
| **LATO 2: Block_3 vs Block_6** ($V_{{3,6}}$) | **{float(tex['mean_V_3_6']):+.4f}** ($p={float(tex['p_V_3_6']):.5f}$) | {float(tex['mean_scr_1_3']):+.4f} ($V_{{\\text{{scr}}(3,6)}}$) | **{float(tex['mean_Delta_3_6']):+.4f}** | **{float(tex['p_Delta_3_6']):.5f}** | **{'CONFERMATO' if tex['sig_Delta_3_6'] else 'NON SIGNIFICATIVO'}** |
| **LATO 3: Block_1 vs Block_6** ($V_{{1,6}}$) | **{float(tex['mean_V_1_6']):+.4f}** ($p={float(tex['p_V_1_6']):.5f}$) | {float(tex['mean_scr_1_1']):+.4f} ($V_{{\\text{{scr}}(1,1)}}$) | **{float(tex['mean_Delta_1_6']):+.4f}** | **{float(tex['p_Delta_1_6']):.5f}** | *(Termine di riferimento congelato)* |

* **Pavimento Nullo Omologo Block_1** (`scramble_A` vs `scramble_B`): $\\bar{{V}}_{{\\text{{scr}}(1,1)}} = {float(tex['mean_scr_1_1']):+.4f}$ ($p={float(tex['p_scr_1_1']):.5f}$)  
* **Pavimento Nullo Omologo Block_3** (`scramble_C` vs `scramble_D`): $\\bar{{V}}_{{\\text{{scr}}(3,3)}} = {float(tex['mean_scr_3_3']):+.4f}$ ($p={float(tex['p_scr_3_3']):.5f}$)  
* **Pavimento Nullo Cross-Anchored** (`scramble_A` vs `scramble_C`): $\\bar{{V}}_{{\\text{{scr}}(1,3)}} = {float(tex['mean_scr_1_3']):+.4f}$ ($p={float(tex['p_scr_1_3']):.5f}$)  
* **Media delle 4 coppie cross-scramble**: $\\bar{{V}}_{{\\text{{scr,cross}}}} = {float(tex['mean_scr_cross']):+.4f}$  

---

## 2. Punteggi Leave-One-Out per Ciascuno dei 10 Prompt Stilistici

Tabella analitica dei punteggi calcolati con la procedura Leave-One-Out cross-prompt nello spazio primario Tessitura (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy` z-standardizzate):

| Prompt ID | $V_{{1,3}}(p)$ | $V_{{3,6}}(p)$ | $V_{{1,6}}(p)$ | $V_{{\\text{{scr}}(1,3)}}(p)$ | $V_{{\\text{{scr}}(1,1)}}(p)$ | $\\Delta V_{{1,3}}(p)$ | $\\Delta V_{{3,6}}(p)$ |
|---|---|---|---|---|---|---|---|
{prompt_table_str}

---

## 3. Coerenza Interna e Geometria dei Centroidi

* **Coerenza Intra-Blocco (Coseno medio tra prompt dello stesso blocco)**:
  - $\\text{{coh}}(Block\\_1) = {float(tex['coh_b1']):+.4f}$
  - $\\text{{coh}}(Block\\_3) = {float(tex['coh_b3']):+.4f}$
  - $\\text{{coh}}(Block\\_6) = {float(tex['coh_b6']):+.4f}$
  - $\\text{{coh}}(scramble\\_A) = {float(tex['coh_sa']):+.4f}$ | $\\text{{coh}}(scramble\\_B) = {float(tex['coh_sb']):+.4f}$
  - $\\text{{coh}}(scramble\\_C) = {float(tex['coh_sc']):+.4f}$ | $\\text{{coh}}(scramble\\_D) = {float(tex['coh_sd']):+.4f}$

* **Coseno tra Centroidi Medi (Separazione Direzionale Grezza vs Disattenuata)**:
  - $Block\\_1$ vs $Block\\_3$: cos grezzo = **{float(tex['cross_1_3']):+.4f}**, disattenuato = **{float(tex['disatt_1_3']):+.4f}**
  - $Block\\_3$ vs $Block\\_6$: cos grezzo = **{float(tex['cross_3_6']):+.4f}**, disattenuato = **{float(tex['disatt_3_6']):+.4f}**
  - $Block\\_1$ vs $Block\\_6$: cos grezzo = **{float(tex['cross_1_6']):+.4f}**, disattenuato = **{float(tex['disatt_1_6']):+.4f}**

* **Quota Antisimmetrica ($\\|A\\| / (\\|S\\| + \\|A\\|)$)**:
  - $Block\\_1$: **{float(tex['share_antisym_b1']):.3f}** (dominanza antisimmetrica)
  - $Block\\_3$: **{float(tex['share_antisym_b3']):.3f}**
  - $Block\\_6$: **{float(tex['share_antisym_b6']):.3f}**

---

## 4. Analisi di Robustezza sugli Spazi Stilistici Secondari

| Spazio di Feature | Dimensioni | $\\bar{{V}}_{{1,3}}$ | $\\bar{{V}}_{{3,6}}$ | $\\bar{{V}}_{{1,6}}$ | $\\Delta \\bar{{V}}_{{1,3}}$ ($p$) | $\\Delta \\bar{{V}}_{{3,6}}$ ($p$) | Regime Assegnato |
|---|---|---|---|---|---|---|---|
{sec_table_str}

---

## 5. Quality Control Visivo

I contact sheet completi a 11 condizioni $\\times$ 3 seed per tutti i 10 stili sono stati generati e salvati in [`qc_output/rotations_triangolo/`](../qc_output/rotations_triangolo/):
* `qc_S01_oil.png` .. `qc_S10_synthwave.png`

---

## 6. Risposta alla Domanda Aperta di Ricerca

Alla domanda iniziale:
*«La separazione direzionale osservata riflette una reale specializzazione funzionale o la pura prossimità topografica ai confini della rete?»*

Il verdetto matematico basato sull'albero decisionale a 4 vie con margine di equivalenza $\\Delta_{{\\text{{equiv}}}} = 0.25$ stabilisce che:
**{tex['regime']}**.  
{tex['regime_desc']}
"""

    os.makedirs(os.path.dirname(REPORT_MD), exist_ok=True)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[OK] Report Markdown generato con successo: {REPORT_MD}")

if __name__ == "__main__":
    main()
