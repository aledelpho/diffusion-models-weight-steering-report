# MOSS3: Atlante di MOSS-Image in Turbo (1335 Render) — 2026-10-25 / 2026-10-26

Esecuzione automatizzata condotta da Antigravity seguendo le direttive prescritte in [docs/directives_antigravity_moss_atlas.md](directives_antigravity_moss_atlas.md) e la pre-registrazione [docs/prereg_moss_atlas.md](prereg_moss_atlas.md) (Emendamenti 1, 2 e 3).  
L'esperimento mappa sistematicamente 148 unità (42 layer DiT x {attention, MLP} + 32 layer Text Encoder Qwen3.5-9B x {attention, MLP}) a tre dosi:
* $d = +1.0$ (`p`, contributo raddoppiato)
* $d = -1.0$ (`m`, contributo rimosso)
* $d = +2.0$ (`pp`, contributo triplicato, introdotto con Emendamento 3)

sui tre prompt di riferimento degli atlanti Krea-2 (`P01_blacksmith`, `S1_rally`, `F4_closeup`) al seed fisso 2718281 in configurazione **T10 Turbo** (10 step euler, DMD2 LoRA a forza 1.0, 1024×1280).

---

## Step 1 — Esecuzione e Conteggio File

1. **Primo blocco (891 render)**: accodati inizialmente con `moss_atlas.py --queue` (`queued 891`), coprendo le 148 unità a $d = +1.0$ e $d = -1.0$ oltre ai 3 plain.
2. **Secondo blocco (444 render, Emendamento 3)**: al termine del primo blocco, rieseguito `moss_atlas.py --queue` che ha riconosciuto gli 891 render già esistenti su disco e accodato esclusivamente i 444 render mancanti a $d = +2.0$ (`queued 444`).

### Verifica del Conteggio File

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& $PY moss_atlas.py --count
```

*Output Verbatim:*
```text
expected 1335 missing 0 []
```

### Tempi di Rendering Misurati (T10 Turbo: 10 step euler, DMD2 LoRA)

* **Statistiche per immagine (1334 intervalli)**:
  * Media netta: **22.5 s**
  * Mediana: **22.0 s**
  * Minimo: **20.7 s**
  * Massimo: **97.4 s**
* **Arco temporale totale**: **8.33 ore** continue per l'intero set dei 1.335 render (nessuna interruzione o riavvio).

---

## Step 2 — Analisi DINOv2 e Fogli di Contatto

### Output Verbatim (`moss_atlas.py --analyze`)

```text
H1 DiT mlp p: depth orders the change (reported if |rho| < 0.5) | Spearman layer vs median D +0.74 | ordered
H1 TE mlp p | Spearman layer vs median D +0.19 | not ordered
H1 DiT mlp m: depth orders the change (reported if |rho| < 0.5) | Spearman layer vs median D +0.56 | ordered
H1 TE mlp m | Spearman layer vs median D -0.21 | not ordered
H1 DiT mlp pp: depth orders the change (reported if |rho| < 0.5) | Spearman layer vs median D +0.76 | ordered
H1 TE mlp pp | Spearman layer vs median D +0.12 | not ordered
H1 DiT attn p: depth orders the change (reported if |rho| < 0.5) | Spearman layer vs median D +0.43 | not ordered
H1 TE attn p | Spearman layer vs median D -0.18 | not ordered
H1 DiT attn m: depth orders the change (reported if |rho| < 0.5) | Spearman layer vs median D +0.66 | ordered
H1 TE attn m | Spearman layer vs median D -0.54 | ordered
H1 DiT attn pp: depth orders the change (reported if |rho| < 0.5) | Spearman layer vs median D +0.40 | not ordered
H1 TE attn pp | Spearman layer vs median D -0.06 | not ordered
H2 dit p: MLP moves the picture more than attention | 19 of 42 layers (bar 2/3) | does not hold
H2 dit m: MLP moves the picture more than attention | 16 of 42 layers (bar 2/3) | does not hold
H2 dit pp: MLP moves the picture more than attention | 23 of 42 layers (bar 2/3) | does not hold
H2 te p: MLP moves the picture more than attention | 21 of 32 layers (bar 2/3) | does not hold
H2 te m: MLP moves the picture more than attention | 25 of 32 layers (bar 2/3) | holds
H2 te pp: MLP moves the picture more than attention | 19 of 32 layers (bar 2/3) | does not hold
H3 TE full-attention vs linear-attention layers (reported) | median D 0.030 vs 0.026 | -
strongest ten units x sign (reported) | dit32_attn_m 0.986; dit00_attn_m 0.967; dit33_attn_m 0.860; dit33_mlp_m 0.853; te00_attn_m 0.806; dit31_mlp_pp 0.805; dit34_mlp_m 0.753; te00_attn_pp 0.708; dit41_attn_m 0.541; dit32_mlp_pp 0.538 | -
```

I dataset delle metriche calcolate e dei test sono stati registrati rispettivamente in [data/moss_atlas_metrics.csv](../data/moss_atlas_metrics.csv) (1.332 righe di perturbazioni) e [data/moss_atlas_tests.csv](../data/moss_atlas_tests.csv).

### Generazione Fogli di Contatto (`moss_atlas.py --sheets`)

```powershell
& $PY moss_atlas.py --sheets
```

*Output Verbatim:*
```text
sheets in D:\StabilityMatrix-win-x64\Data\Images\Text2Img\_moss_atlas - columns: plain, attention x2, attention x3, attention removed, MLP x2, MLP x3, MLP removed
```

File generati in `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\_moss_atlas\`:
1. `P01_blacksmith_dit.jpg` (42 righe DiT × 7 colonne)
2. `P01_blacksmith_te.jpg` (32 righe TE × 7 colonne)
3. `S1_rally_dit.jpg` (42 righe DiT × 7 colonne)
4. `S1_rally_te.jpg` (32 righe TE × 7 colonne)
5. `F4_closeup_dit.jpg` (42 righe DiT × 7 colonne)
6. `F4_closeup_te.jpg` (32 righe TE × 7 colonne)

Colonne di ciascun foglio:
`plain` | `attention x2` ($d = +1$) | `attention x3` ($d = +2$) | `attention removed` ($d = -1$) | `MLP x2` ($d = +1$) | `MLP x3` ($d = +2$) | `MLP removed` ($d = -1$)

---

## Vincoli di Riservatezza Visiva

In conformità al protocollo del banco MOSS3 e alle regole operative del progetto, **nessuna immagine generata o foglio di contatto è stato aperto o descritto visivamente dall'agente**. La consultazione e la valutazione qualitativa sono interamente riservate ad Alessandro e a Claude.
