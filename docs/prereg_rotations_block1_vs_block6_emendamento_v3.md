# Emendamento v3 alla pre-registrazione `prereg_rotations_block1_vs_block6.md`

**Data di congelamento**: 2026-09-23, **prima** di qualsiasi render v3.
**Stato**: dichiarato dopo aver visto v1 e v2 (`docs/audit_rotations_clean_v2_2026-09-23.md`).
Ogni deviazione sotto è una **riparazione dichiarata**, non una previsione originale (pitfall 68).
L'ipotesi, lo spazio primario e la formula del §1 del documento originale **non cambiano**.

## Perché serve

1. Le 210 immagini originali hanno la HUD (1024×1760): inutilizzabili.
2. La dose registrata D = 0.045 è nel regime di collasso: in v1 `Block_6_pos` ha luminanza media
   7/255, `Block_6_neg` 193/255 con deviazione 11. Un test su quei fotogrammi non misura la tessitura.
3. v2 ha abbandonato l'appaiamento di D (stesso angolo: `Block_1` sposta il 35% in più), ha due prompt
   invece di dieci, e le sue braccia `Block_6` a 10–15° sono già degradate.
4. Il disegno originale aveva gli scramble **a un solo segno**, e `scramble_B` (tensori di `Block_6`)
   era reso a 23.69°, cioè D ≈ 0.033 e non 0.045. La componente A degli scramble richiesta dal
   criterio nullo del §4 non era calcolabile.

## Deviazioni, tutte fissate ora

| | originale | v3 | motivo |
| --- | --- | --- | --- |
| risoluzione | 1024×1760 | **1024×1280** | 1760 era la HUD |
| dose | D = 0.045 | **la più alta di {0.0141, 0.0106, 0.0071} che passa il cancello di qualità della Fase 1** | 0.045 collassa |
| angoli | 23.69° / 32.21° | risolti per bisezione alla dose scelta, \|D₁ − D₆\| ≤ 1e-6, misurati sulla patch reale del nodo | |
| scramble | `scramble_A`, `scramble_B` a segno + | **`scrA_pos/neg` all'angolo di `Block_1`, `scrB_pos/neg` all'angolo di `Block_6`** | il §4 richiede A = (Δ⁺ − Δ⁻)/2; ciascuno scramble alla D del suo ancoraggio |
| condizioni per cella | 7 | **9** (baseline, B1±, B6±, scrA±, scrB±) | |
| render | 210 | **270** + pilota di qualità | |

Invariati: i 10 prompt `S01`–`S10` testo per testo (dal manifest originale, verificati per sha1), i
seed `42`, `1337`, `4242145`, `euler_ancestral`, 9 passi, CFG 1.0, `simple`, denoise 1.0,
`krea2_turbo_bf16`, `qwen3vl_4b_bf16`, `qwen_image_vae`.

## Il cancello di qualità (Fase 1), fissato prima di vedere qualsiasi immagine

Sul **pilota** (3 prompt `S01_oil`, `S05_pencil`, `S10_synthwave` × seed **`90210`**, che non entra
nel test), per ogni render attivo contro la sua baseline appaiata, in scala di grigi 8 bit:

* rapporto del gradiente medio `mean(hypot(∇x, ∇y))` fra **0.67 e 1.50**;
* differenza di luminanza media **|ΔL| ≤ 20**.

Si parte da D = 0.0141 e si scende nella scala. La dose scelta è **la prima in cui tutte le 24 immagini
attive del pilota passano**. Se nessuna passa, il run si ferma e la decisione torna all'autore. La scelta
usa solo queste due misure di qualità, mai la tessitura o la statistica del test.

Sul **corpus completo** lo stesso cancello si applica a tutte le 240 immagini attive e si riporta per
condizione. Un'immagine che fallisce **resta nell'analisi** (escluderla sceglierebbe i dati), ma se più
del 10% di una condizione fallisce, il risultato è dichiarato «in regime degradato» qualunque sia il p.

## Analisi, fissata ora

* **Primario**: la formula del §1 originale, invariata: A per prompt come media sui 3 seed,
  vantaggio stesso-blocco leave-one-out V(p), sign-flip esatto su 10 prompt a due code, pavimento
  2/2¹⁰ = 0.00195. Spazio Tessitura (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy`),
  z-standardizzato una volta sull'intero corpus v3 (270 immagini).
* **Criterio**: V̄ > 0 con p < 0.05 **e** V̄ > V̄_scramble (§4), con V̄_scramble calcolato dalla stessa
  formula sulle A di `scrA` e `scrB`. Entrambe le condizioni, altrimenti non confermato.
* **Secondari** (esplorativi, Holm su quattro): Linework (3), Shadow (2), Palette (le 5 del codice
  esistente; il registrato ne dichiarava 6, discrepanza riportata). **Frequency è esclusa**: con una
  sola feature il coseno vale ±1 e non misura una direzione.
* **Unità**: il prompt (n = 10). I seed si mediano prima.
* **Nessun altro primario** verrà calcolato su questi dati. Nessuna seconda dose.

Lo script di analisi sarà scritto e congelato per sha256 e per copia **prima** che le feature v3 esistano.

## Congelamento dello script di analisi — 2026-09-23 14:55

`experiments/analyze_rotations_matched_v3.py`, sha256 `aec99c0481160e9ff2ea8605a7bc625371ed04bb941d9eca3483a50bcf505d5c`, copia in
`docs/frozen/analyze_rotations_matched_v3.py.frozen`. Congelato **prima** che
`data/rotations_matched_v3_features.csv` esistesse. Collaudato solo su dati sintetici (un effetto
piantato, rilevato; un nullo, non confermato), mai sulle immagini v3.

Nota di trasparenza: il testo sopra dice «Holm su quattro» elencando tre spazi secondari; lo script
applica m = 4 come scritto, che è la scelta conservativa.
