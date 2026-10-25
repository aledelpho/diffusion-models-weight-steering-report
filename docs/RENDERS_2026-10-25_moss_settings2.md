# MOSS-S2: Proporzionalità degli Edit a Dosi Visibili (72 Render) — 2026-10-25

Esecuzione condotta da Antigravity seguendo le direttive prescritte in [docs/directives_antigravity_moss_settings2.md](directives_antigravity_moss_settings2.md) e la pre-registrazione [docs/prereg_moss_settings2.md](prereg_moss_settings2.md).
Obiettivo: verificare se a dosi che muovono visibilmente l'immagine ($d = 1.0, 2.0$) le configurazioni veloci (E25 a 25 step, T10 turbo LoRA a 10 step euler, T10A turbo LoRA a 10 step euler_ancestral) preservano la gerarchia e la proporzionalità degli effetti di steering rispetto al riferimento R50 (50 step euler).

---

## Step 1 — Esecuzione e Conteggio File

Accodati i 72 render del piano [data/moss_settings2_plan.csv](moss_settings2_plan.csv) (`queued 72`).

### Verifica del Conteggio File

```powershell
& $PY moss_settings2.py --count
```

```text
expected 72 missing 0 []
```

### Tempi di Rendering Misurati per Impostazione

* **`T10`** (10 step, euler, CFG 1.0, LoRA turbo DMD2): **24.4 s** di media (mediana 24.6 s, min 21.6 s, max 30.2 s)
* **`T10A`** (10 step, euler_ancestral, CFG 1.0, LoRA turbo DMD2): **24.5 s** di media (mediana 24.5 s, min 21.9 s, max 30.1 s)
* **`E25`** (25 step, euler, CFG 3.0, shift 5): **86.4 s** di media (mediana 86.4 s, min 83.0 s, max 93.6 s)
* **`R50`** (50 step, euler, CFG 3.0, riferimento): **178.1 s** di media (mediana 171.3 s, min 159.1 s, max 208.3 s)

---

## Step 2 — Analisi DINOv2 e Foglio di Contatto

### Output Verbatim (`moss_settings2.py --analyze`)

```text
power (reported) | R50 median edit D 0.046; informative if >= 0.03 | -
S2 E25 edits proportional to R50 | Spearman 0.57 (bar 0.80), median ratio 1.20 (0.5-2) | FAIL
S2 T10 edits proportional to R50 | Spearman 0.86 (bar 0.80), median ratio 1.18 (0.5-2) | PASS
S2 T10A edits proportional to R50 | Spearman 0.67 (bar 0.80), median ratio 1.02 (0.5-2) | FAIL
```

### Output Verbatim (`moss_settings2.py --sheet`)

```text
sheet: rows dwarf R50/E25/T10/T10A then rally; columns plain then ['dit06_p1', 'dit06_p2', 'dit20_p1', 'dit20_p2', 'te06_p1', 'te06_p2', 'te27_p1', 'te27_p2'] -> D:\StabilityMatrix-win-x64\Data\Images\Text2Img\_moss_settings2_sheet.jpg
```

* **Contact sheet generato**: `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\_moss_settings2_sheet.jpg` (confronto visivo delle 16 celle per R50, E25, T10 e T10A su dwarf e rally).

---

## Sintesi dei Risultati e Criteri di Decisione

1. **Potenza del Test (Power)**:
   * A $d = 1.0$ e $d = 2.0$, la distanza mediana D degli edit su R50 è pari a **$0.046 \ge 0.03$**. Il test è informativo ed esce dalla zona di rumore numerico che aveva impedito la decisione in MOSS-S.

2. **Esito del Criterio $S_2$ (Proporzionalità rispetto a R50)**:
   * **`T10` (Turbo LoRA 10 step, campionatore `euler`)**: **PASS**
     * Correlazione di rango Spearman: **$\rho = 0.86 \ge 0.80$**
     * Rapporto mediano della magnitudo degli effetti: **$1.18$** (perfettamente all'interno dell'intervallo accettato $0.5 - 2.0$).
     * Risultato: **`T10` rispecchia fedelmente la gerarchia e la sensibilità agli edit di R50**, impiegando solo **~24.5 secondi** per immagine anziché ~178 secondi (un'accelerazione di oltre $7.2\times$).
   * **`T10A` (Turbo LoRA 10 step, campionatore `euler_ancestral`)**: **FAIL**
     * Spearman $\rho = 0.67 < 0.80$, rapporto mediano $1.02$. La stocasticità ancestrale degrada la concordanza di rango con il riferimento deterministico euler a 50 step.
   * **`E25` (25 step, campionatore `euler`)**: **FAIL**
     * Spearman $\rho = 0.57 < 0.80$, rapporto mediano $1.20$.

3. **Decisione Operativa (come da pre-registrazione §"Use")**:
   * **`T10`** è convalidato come setting di lavoro per i futuri sweep e benchmark esplorativi su MOSS-Image.
   * Ciascun esperimento esteso designerà a priori le proprie celle di conferma (10–15%) da riverificare sul riferimento lento R50.
