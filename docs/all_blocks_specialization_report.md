# Profilo di Specializzazione Funzionale dei Macro-Blocchi (Block_1 .. Block_6)

**Data e ora**: 2026-09-22 16:44:36  
**Corpus**: 294 render rigorosamente 1024x1280 (zero HUD), angoli conservativi 5°/10°/15° su Krea-2.  

## 1. Quadro Comparativo: Modifiche del Colore vs Modifiche della Forma

L'indice $\log_2(\text{Chroma} / \text{Shape})$ misura oggettivamente se la rotazione del blocco agisce prevalentemente sulla banda cromatica ($>0$) oppure sulla geometria e sullo spessore/densità del segno ($<0$):

| Blocco | Magnitudo Cromia (Lab/Spread) | Magnitudo Forma (Stroke/Edges) | Magnitudo Tessitura (GLCM/LBP) | Indice $\log_2(\text{Colore}/\text{Forma})$ | Specializzazione Funzionale |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **B1** | `0.8746` | `1.1437` | `0.4386` | `-0.387` | **Specializzazione Morfologica / Linework Dominante (Forma/Tratto)** |
| **B2** | `0.3519` | `0.2616` | `0.1519` | `+0.428` | **Specializzazione Cromatica Dominante (Banda/Saturazione)** |
| **B3** | `0.3163` | `0.5407` | `0.3064` | `-0.773` | **Specializzazione Morfologica / Linework Dominante (Forma/Tratto)** |
| **B4** | `0.5626` | `0.4476` | `0.2087` | `+0.330` | **Azione Mista Bilanciata (Forma + Colore)** |
| **B5** | `0.5554` | `0.5886` | `0.1763` | `-0.084` | **Azione Mista Bilanciata (Forma + Colore)** |
| **B6** | `2.0583` | `2.6662` | `1.8560` | `-0.373` | **Specializzazione Morfologica / Linework Dominante (Forma/Tratto)** |

## 2. Dettaglio delle Modifiche Fisiche Cardine (Livello 10° Mid)

| Blocco | $\Delta$ Chroma Spread | $\Delta$ Stroke Median (px) | $\Delta$ Stroke Modulazione CV | $\Delta$ Edge Density |
| :---: | :---: | :---: | :---: | :---: |
| **B1** | `+0.367` | `-0.500` | `+0.089` | `+0.0050` |
| **B2** | `+0.580` | `+0.000` | `+0.000` | `+0.0003` |
| **B3** | `-1.709` | `-0.100` | `+0.053` | `-0.0060` |
| **B4** | `-0.014` | `+0.000` | `+0.059` | `-0.0029` |
| **B5** | `+0.630` | `-0.200` | `+0.019` | `+0.0036` |
| **B6** | `+12.389` | `-0.600` | `+0.263` | `-0.0414` |

## 3. Considerazioni di Interpretabilità Meccanicistica

- **Blocchi Iniziali (B1, B2)**: governano la tessitura fine e la modulazione del tratto continuo senza stravolgere la saturazione globale.
- **Blocchi Centrali (B3, B4)**: punto di transizione tra composizione sintattica e resa materiale.
- **Blocchi Finali (B5, B6)**: modulano drammaticamente la dinamica della luce, il contrasto di saturazione e la densità estrema del tratteggio.
