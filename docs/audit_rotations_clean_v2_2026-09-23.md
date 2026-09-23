# Audit di `rotations_clean_v2` e `all_blocks_clean_v2` — 2026-09-23

**Oggetto**: i 13 CSV di `export_esperimento_rotazioni_v2/`, le 294 immagini di
`benchmark_rotations_clean_v2/renders/`, i tre report `docs/rotations_clean_v2_results.md`,
`docs/rotations_clean_v2_chromatic_and_stroke_analysis.md`, `docs/all_blocks_specialization_report.md`.
**Metodo**: ricalcolo indipendente (script scritti dalle definizioni, non copiati da quelli che hanno
prodotto i file), join per nome file e mai per posizione, ri-estrazione completa delle feature sulle
294 immagini. Nessun file esistente è stato modificato.

## Verdetto in una riga

I pixel sono puliti e i numeri sono aritmeticamente giusti; **il disegno non è quello registrato e
tre interpretazioni pubblicate nei report non reggono**. Nulla di v2 può sostituire le affermazioni di
`08-block1-vs-block6` così com'è.

## 1. Ciò che regge (verificato)

| Controllo | Esito |
| --- | --- |
| Dimensioni decodificate | 294/294 a 1024×1280×3. Nessuna HUD: il grafo nel `tEXt` di ogni PNG contiene solo loader, encoder, KSampler, VAEDecode, SaveImage e al più un nodo rotatore |
| Tre copie (ComfyUI output, pilot, report) | 294/294 byte-identiche (sha256) |
| Grafo PNG contro nome file | 0 discordanze su seed, sha1 del prompt, blocco bersaglio, angolo con segno, sampler, step, CFG, scheduler, denoise, latente. Nessun duplicato di pixel |
| Allineamento righe↔immagini nei CSV | 0 discordanze (lo script v2 incollava la cache per posizione, ma l'ordine coincideva) |
| Statistiche pubblicate, dalle feature salvate | tutte riprodotte a precisione di macchina: `results`, `prompt_scores`, `chromatic_scores`, `stroke_scores`, le due tabelle di medie, `stroke_sa_decomp`, `all_blocks_specialization_summary` |
| Statistiche dalle feature ri-estratte da zero | identiche per style; la palette differisce di ≤ 0.013 su `chroma_spread` (k-means non bit-riproducibile), ≤ 5e-4 sugli s. Nessun esito cambia |

## 2. Errori nei dati esportati

1. **`all_blocks_clean_v2_palette_features.csv`, colonna `seed`**: nelle 144 righe B2–B5 contiene lo
   stem del file (`P01_s1618033_B2_neg_high_00001_`) invece del seed. `palette_features()` restituisce
   una chiave `seed` che sovrascrive quella dei metadati. Il riassunto non ne è toccato (unisce su
   `image_path`), ma chiunque raggruppi per `seed` quel file perde silenziosamente 144 righe.
   Pitfall 7/D1.
2. **Manifest**: `angle_deg` e `prompt_sha1` sono ricavati dal nome file e da una costante, non dal
   grafo. Qui coincidono (verificato sopra), ma il manifest non lo dimostra da sé. `checkpoint_sha256`,
   `tuner_version`, `suite_git_sha`: `not recorded`. **Manca `measured_D`**, presente in v1.
3. **`README_DATASETS.txt`**: «33 feature di stile» — sono 23. «subset delle prime 150 immagini» — sono
   le braccia B1/B6/scrA/scrB/baseline, non le prime 150.
4. **Cartella condivisa**: v2 (150) e B2–B5 (144) sono scritti nello stesso `renders/`. Lo script v2
   ora non può più girare (il suo cancello si aspetta 150 file e ne trova 294). Pitfall 30, quarta volta.

## 3. Il disegno: v2 non è una replica di `08`

**Lo spostamento non è appaiato.** La calibrazione v2 fissa la relazione esattamente,
D = k·2·sin(θ/2), con k = 0.10962 (`Block_1`) e 0.08112 (`Block_6`), costante sui tre livelli. Allo
stesso angolo:

| angolo | D `Block_1` / `scrA` | D `Block_6` / `scrB` |
| ---: | ---: | ---: |
| 5° | 0.0096 | 0.0071 |
| 10° | 0.0191 | 0.0141 |
| 15° | 0.0286 | 0.0212 |

`Block_1` sposta il modello del 35% in più di `Block_6` a ogni livello, e tutti i livelli stanno sotto la
dose più bassa di v1 (0.030). La pre-registrazione di `08` è costruita sullo spostamento appaiato; gli
scramble ereditano lo stesso sbilanciamento, quindi la statistica s resta internamente bilanciata, ma
il disegno è un altro. È un esperimento nuovo, **deciso dopo aver visto v1** e senza piano né
pre-registrazione nel repository (pitfall 68, famiglia F3).

**La ragione del cambio è però fondata, e v1 va riletto.** Le immagini v1 a D = 0.045, la dose
registrata, sono distrutte: `B6_pos` luminanza media 7/255, `B6_neg` 193/255 con deviazione 11,
`scrB` idem. Anche a D = 0.030 `B6_pos` ha gradiente medio 1.4 contro 11.1 della baseline. Quindi:

* il **negativo** di v1 (s = −0.857, 9 step) è misurato su fotogrammi collassati e non è un test;
* il **positivo** di v1 a D = 0.030 lo è altrettanto;
* nessuna delle due serie può essere scritta come conferma o smentita di `08`.

**v2 non è «senza collasso»**, come afferma il suo report. Rispetto alla baseline appaiata:

| condizione | Δ luminanza | gradiente / baseline |
| --- | ---: | ---: |
| `B6_pos_mid` | −9 … −3 | 0.55–0.58 |
| `B6_pos_high` | −38 … −25 | **0.20–0.26** |
| `scrB_pos_mid` | −52 … −39 | 0.58–0.84 |
| `scrB_neg_high` | +31 … +40 | 0.31–0.44 |
| tutte le B1–B5, scrA | entro ±15 | 0.87–1.23 |

Visivamente le braccia ancorate a `Block_6` applicano soprattutto una dominante cromatica globale
(ambra / viola) più ammorbidimento; a 15° l'immagine è sfocata. Nessun cancello di qualità è stato
dichiarato prima dell'analisi (il precedente è la soglia 3σ di stage 9).

## 4. Il risultato primario, riletto

s (tessitura, 10°) = +0.8817, 6/6 celle positive, p = 0.03125: **aritmeticamente corretto**. Ma:

* **Unità statistica.** Tre seed per prompt non sono indipendenti (regola 6, pitfall 17). Per prompt:
  P01 +1.518, P02 +0.245 (celle P02: +0.146, +0.002, +0.587). Con due prompt il pavimento esatto è
  0.5. Il p = 0.03125 generalizza sui seed di due soggetti in uno stile, non oltre.
* **Molteplicità nascosta.** È il quarto primario eseguito sullo stesso disegno in 30 ore
  (v1 a 9, 7, 5 step, poi v2), l'unico positivo, e con un parametro cambiato dopo aver visto i primi tre.
  Sei unità reggono un solo test a α = 0.05 (regola 11).
* **Dose.** 5°: −0.372 (2/6 positive, P02 −1.035); 10°: +0.882; 15°: +0.973. Aggiungendo v1:
  il segno cambia tre volte fra D = 0.007 e D = 0.060. Non è una curva dose-risposta.
* **Spazi secondari.** La «Frequency» ha una sola feature: il coseno di vettori 1-D vale ±1, s può
  valere solo −2, 0, +2. Non è una misura di direzione. Il registrato ne prevedeva 2, la Palette 6
  (il codice ne usa 5): discrepanza già presente in `analyze_block1_vs_block6.py`.

## 5. I due report derivati

**`rotations_clean_v2_chromatic_and_stroke_analysis.md`**

* cos(A_B1, A_B6) = **+0.479** nello spazio stroke è descritto come «forte divergenza»: un coseno
  positivo significa che le direzioni **concordano**. L'interpretazione è rovesciata.
* Lo spazio 24-D Lab non è standardizzato e confronta `sw1` con `sw1` fra immagini in cui il k-means può
  riordinare gli swatch. Standardizzato: s = +0.082, p = 0.41. Nulla in entrambe le versioni.
* `paper_L` di baseline: P01 57–61, P02 88–89. Su P01 lo stimatore della carta non trova carta
  (pitfall 29): `Paper L*/C*` non sono misure della carta.
* `stroke_width_median_px` assume tre valori (2.0, 2.8, 4.0): le medie «3.000» e le A di ±0.5 px sono
  salti di quantizzazione.
* Spazio «Stroke 3-D» definito dopo i dati, fuori dalla pre-registrazione.

**`all_blocks_specialization_report.md`** — la conclusione non è sostenuta.

* **Non c'è nullo.** Gli scramble sono nello stesso CSV e non sono stati analizzati (regola 15).
  Aggiunti al calcolo identico:

  | | cromia | forma | tessitura | log2(C/F) | celle con log2 > 0 |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | B1 | 0.875 | 1.144 | 0.439 | −0.39 | 2/6 |
  | B6 | 2.058 | 2.666 | 1.856 | −0.37 | 1/6 |
  | **scrA** (nessuna struttura, D di B1) | 0.607 | 1.208 | 0.393 | −0.99 | 0/6 |
  | **scrB** (nessuna struttura, D di B6) | **3.442** | 2.191 | 0.891 | **+0.65** | 6/6 |

  Uno scramble senza struttura verrebbe classificato «Specializzazione Cromatica Dominante», e con più
  coerenza di qualunque blocco. La classificazione misura quanto si muove l'immagine, non che cosa fa un
  blocco.
* **D non appaiato fra blocchi** allo stesso angolo: le magnitudini confondono posizione e spostamento
  (pitfall 41; claim *open* di `04`).
* **Dimensionalità**: cromia su 5 feature, forma su 4; il log2 è spostato di +0.16 a favore della cromia.
  Corretto, B2 (+0.27) e B4 (+0.17) scendono sotto la soglia 0.35 e da «cromatico» diventano «misto».
* **Stabilità**: nessun blocco ha il segno del log2 coerente oltre 3/6 celle, tranne B6 (1/6).
* Le colonne «Δ» sono in realtà A = (Δ⁺ − Δ⁻)/2 (pitfall 18).
* La sezione 3 («B1, B2 governano la tessitura fine…», «B5, B6 modulano drammaticamente…») è testo
  fisso nello script, non derivato dai dati, e li contraddice: B5 ha la tessitura più bassa di tutti
  (0.176), B1 è 4 volte sotto B6 (regola 10).

## 6. Che cosa si può usare

* **Le immagini**: pulite, tracciate, riproducibili. Utilizzabili come corpus.
* **Le feature style**: esatte. Palette: esatte a meno del rumore di k-means, colonna `seed` da rifare.
* **Nessuna affermazione** di `08` o `04` può essere ripristinata con questi dati: v2 non è appaiato,
  ha due soggetti, e le braccia di `Block_6` a 10–15° sono già fortemente degradate.
* **Nuovo disegno appaiato a bassa dose** (proposta, non eseguita): D = 0.0141, che è `Block_6` a 10°
  (ultimo livello non sfocato) e `Block_1` a ≈ 7.4° (da risolvere per bisezione, non da questa formula), con cancello di qualità dichiarato prima del render
  e i dieci prompt registrati di `08` in una cartella nuova. Il pavimento torna a 2/2¹⁰.

## File di lavoro

Script e tabelle di questo audit (fuori dal repository): `audit_v2_images.py` (294 immagini, sha256,
grafo, ri-estrazione), `recompute_v2_stats.py` (tutte le statistiche), `audit_v2_images.csv`.
