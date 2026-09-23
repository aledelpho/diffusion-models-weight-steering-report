# Emendamento v4 alla pre-registrazione `prereg_rotations_block1_vs_block6.md`

**Data**: 2026-09-23, **prima** di qualsiasi render v4. Sostituisce le parti di
`prereg_rotations_block1_vs_block6_emendamento_v3.md` indicate sotto; tutto il resto dell'emendamento
v3 resta valido (ipotesi, spazio primario, formula, criterio, secondari, unità).

## Che cosa è successo a v3

* Il cancello del pilota è **fallito a tutte e tre le dosi**: 13/24 (0.0141), 16/24 (0.0106),
  18/24 (0.0071). A 0.0071 `scrB` sposta la luminanza di 29–37 livelli (limite 20). La regola diceva
  «il run si ferma, decide l'autore».
* L'esecutore ha proseguito a 0.0071 e ha scritto nel log «100% di superamento, |dL| ≤ 7.88», contrario
  al proprio CSV. Sul corpus completo `scrB` fallisce 30/30 per segno e `B6_neg` 5/30.
* `measured_D_node` nel manifest riporta il valore obiettivo (0.0071), non una misura: la verifica sul
  nodo era stata fatta solo a 0.0141.
* **Decisione dell'autore, 2026-09-23, prima di qualsiasi analisi delle feature v3**: v3 non entra nel
  test confermativo. Le immagini restano come registrazione del fallimento del cancello. La statistica
  primaria su v3 **non è stata calcolata**.

## Che cosa cambia

| | v3 | v4 | motivo |
| --- | --- | --- | --- |
| scala di dosi | {0.0141, 0.0106, 0.0071} | **{0.0035, 0.0025, 0.0018}** | a 0.0071 `scrB` arriva a \|dL\| = 40.4 su `S06_pastel`; la risposta è concava, quindi la scala lineare sottostima: 0.0035 → ≥ 19.9, 0.0025 → ≥ 14.2, 0.0018 → ≥ 10.2 |
| pilota | 3 prompt × seed 90210 | **tutti i 10 prompt** × seed 90210 | pitfall 52: un cancello «tutte passano» non si valuta su un campione più piccolo del corpus. A 0.0071 il pilota non vedeva `S06_pastel`, il caso peggiore |
| dose misurata | D sul calcolo fp32 | **D sui pesi dopo il cast a bf16**, a ogni dose della scala, su tutti gli 8 bracci | ComfyUI riscrive i pesi patchati in bf16 (`comfy/float.py`, arrotondamento al più vicino). Alle dosi nuove gli angoli scendono a 0.94–2.47°: variazioni per elemento sotto mezzo passo bf16 vengono assorbite (pitfall 4, 46) |
| cancello sulla dose (nuovo) | — | per ogni braccio: \|D_bf16 / D_target − 1\| ≤ 2% **e** cos(ΔW_bf16, ΔW_fp32) ≥ 0.99, sui tensori del blocco concatenati | una dose che il formato non trasporta non è quella dichiarata |
| controllo di identità (nuovo) | — | rotatore a 0° su `Block_1` e `Block_6`, e scramble a 0°, contro la baseline: pixel identici | pitfall 54: il nodo a zero deve essere un'identità esatta |
| punti di arresto | uno | **due fermate obbligatorie con verifica esterna**: dopo la Fase 0 e dopo la Fase 1 | il cancello di v3 è stato ignorato da chi lo eseguiva |

**Regola di scelta, invariata nella forma**: si prova 0.0035; se tutte le 80 immagini attive del
pilota passano (grad_ratio in [0.67, 1.50] e \|dL\| ≤ 20), è la dose. Altrimenti 0.0025, poi 0.0018.
Una dose che non passa il cancello sulla dose (bf16) è esclusa prima del pilota. Se nessuna dose passa
entrambi i cancelli, **il run si ferma**.

**Probe P01/P02** (3 seed ciascuno, le 9 condizioni, alla dose scelta): aggiunti su richiesta
dell'autore per il confronto con gli sweep di intensità di v2. **Esplorativi**, in una cartella
separata, esclusi dal test e dalla standardizzazione.

## Script di analisi

`experiments/analyze_rotations_matched_v4.py` è `analyze_rotations_matched_v3.py` (sha256 `aec99c04…`)
con i soli nomi dei file cambiati da v3 a v4. Congelato per sha256 e per copia sotto, prima che
esistano immagini v4.

**Congelato 2026-09-23 15:01**: `experiments/analyze_rotations_matched_v4.py`, sha256
`9e54e906f47245448b209a9173458c7d83a16cac655a59b3d4844bada06d5619`, copia in `docs/frozen/analyze_rotations_matched_v4.py.frozen`. Collaudato solo su dati
sintetici. Nessuna immagine v4 esiste a questa data.

## Esito: v4 non è stato reso — 2026-09-23

**Fase 0 (calibrazione, `experiments/calibrate_rotations_v4.py`, `data/matched_rotation_calibration_v4.json`)**:
nessuna dose della scala passa il cancello bf16. D dopo il cast resta entro il 2.4%, ma la direzione
della modifica applicata si allontana da quella voluta:

| D | cos(ΔW_bf16, ΔW_fp32) `Block_1` | `Block_6` | parte antisimmetrica `Block_1` |
| ---: | ---: | ---: | ---: |
| 0.0071 (v3) | 0.9960 | 0.9980 | 0.9965 |
| 0.0053 | 0.9930 | 0.9965 | 0.9939 |
| 0.0035 | 0.9850 | 0.9924 | 0.9862 |
| 0.0025 | 0.9731 | 0.9861 | — |
| 0.0018 | 0.9548 | 0.9758 | — |

Il cancello di luminanza richiede per `scrB` D ≲ 0.0035 (a 0.0071 \|dL\| fino a 40.4, risposta concava);
la fedeltà bf16 (cos ≥ 0.99) richiede D ≳ 0.005. Le due regioni non si toccano. Il rendering in fp32
non è possibile sulla macchina (pesi fp32 ≈ 52 GB, RAM 48 GB, VRAM 20 GB).

**Decisione dell'autore**: il test confermativo si ferma. Non si allenta un cancello dopo che è fallito.
La statistica primaria non è stata calcolata né su v3 né su altro corpus pulito; lo script congelato
`analyze_rotations_matched_v4.py` resta inutilizzato. La pagina `08` resta sospesa sotto il suo banner.

**Che cosa rimane utilizzabile**: le 324 immagini v3 (strutturalmente pulite: 0 problemi su grafo,
dimensioni, sha256; cancello ricalcolato identico entro 1e-4, `data/rotations_matched_v3_audit.csv`)
e le loro feature (`data/rotations_matched_v3_features.csv`), solo a scopo **esplorativo** e con
la dichiarazione che il cancello del pilota era fallito.
