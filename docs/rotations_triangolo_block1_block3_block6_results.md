# Risultati Sperimentali — Il Triangolo: Block_1 vs Block_3 vs Block_6

**Data di esecuzione**: 2026-09-21  
**Stato**: Eseguito, verificato e congelato a fronte di [`docs/prereg_rotations_triangolo_block1_block3_block6.md`](prereg_rotations_triangolo_block1_block3_block6.md)  
**Protocollo metodologico adottato**: Opzione (a) con controlli scramble cross-anchored (`scramble_C` e `scramble_D` su Block_3)  
**Displacement target appaiato**: $D_{\text{modello}} = 0.04500$ (scarto tra i 3 blocchi: $\Delta D \le 0.000005$)  
**Matrice generazioni**: 330 immagini (210 riusate da Block_1 vs Block_6 + 120 generate ex-novo per Block_3 e scramble C/D)  
**File di calibrazione**: [`data/matched_rotation_calibration.json`](../data/matched_rotation_calibration.json)  
**File risultati**: [`data/rotations_triangolo_results.csv`](../data/rotations_triangolo_results.csv)  
**Punteggi per prompt**: [`data/rotations_triangolo_prompt_scores.csv`](../data/rotations_triangolo_prompt_scores.csv)  

> **REVISIONATO 2026-09-21** a fronte di
> [`docs/REVISIONE_triangolo_da_applicare.md`](REVISIONE_triangolo_da_applicare.md).
> Il disegno non e' in discussione: opzione (a), scramble cross-anchored e margine di
> equivalenza dichiarato sono stati eseguiti come previsto. Cambia la **lettura** dei
> risultati, su tre punti, piu' due cose che la revisione stessa non diceva e una che diceva
> al rovescio. Il verdetto passa da «4. Asimmetria di Propagazione» a **non determinato**.
> I numeri della vecchia lettura restano in `data/rotations_triangolo_results.csv` nelle
> colonne `*_acfloor`, cosi' il cambio e' verificabile riga per riga.

---

## 1. Verdetto Primario dell'Albero Decisionale (§2 Pre-registrazione)

### **Regime Selezionato: 0. Non determinato — un primario non e' misurato**

> Il lato Block_3–Block_6 non ha un nullo ancorato su Block_6, quindi il suo contrasto non e' un
> test. L'albero non si puo' percorrere finche' quel pavimento non esiste.

### Riepilogo Numerico delle Ipotesi Primarie nello Spazio Tessitura

Il pavimento e' la **media delle quattro coppie cross** (`A`-`C`, `A`-`D`, `B`-`C`, `B`-`D`), per
la regola fissata in §1-bis.

| Contrasto | Osservato | Pavimento | Delta | p esatto | Esito |
|---|---|---|---|---|---|
| **LATO 1: Block_1 vs Block_3** | +0.0802 (p=0.11328) | +0.5630 media cross | **-0.4828** | 0.00391 | **NON confermato** — significativamente *sotto* il nullo |
| **LATO 2: Block_3 vs Block_6** | +0.3539 (p=0.01172) | *nessuno* | -0.2091 | 0.08594 | **NON misurato** — §1-bis punto 2 |
| **LATO 3: Block_1 vs Block_6** | +0.9555 (p=0.00195) | +0.6070 omologo Block_1 | **+0.3485** | 0.00195 | regge, sotto **ogni** pavimento |

La vecchia lettura, con `A`-vs-`C` come pavimento, dava Delta(1,3) = +0.1197
(p = 0.03711) e Delta(3,6) = +0.3934
(p = 0.00781), entrambi «CONFERMATO».

---

## 1-bis. Perche' il verdetto cambia

### 1. Quale coppia cross e' «il pavimento»

Il report riportava due valori della stessa quantita' concettuale nella stessa sezione:
`A`-vs-`C` a **-0.0396** e la media delle quattro coppie cross a
**+0.5630**. Differiscono di 0.60, e la scelta fra i due decideva
il verdetto da sola.

| pavimento | Delta(1,3) | Delta(3,6) | esito |
|---|---|---|---|
| `A`-vs-`C` | +0.1197 | +0.3934 | due «CONFERMATO» |
| media delle 4 coppie | -0.4828 | -0.2091 | entrambi negativi |

`A`-vs-`C` e' negativo **solo nello spazio primario**: +0.2979 Tratteggio, +0.4632 Ombreggio,
+0.1821 Palette, 0.0000 Frequenze. Il verdetto positivo poggiava sull'unico valore negativo
della tabella, nell'unico spazio che decide. **1 spazio su 5** aveva entrambi i Delta positivi
con `A`-vs-`C`; **0 su 5** con la media.

**Regola fissata**: il pavimento e' la media delle quattro coppie cross, perche' sono nulli
**scambiabili per costruzione** — niente nel disegno distingue `A` da `B` ne' `C` da `D`.
Dichiarata **dopo** aver visto i dati: non e' una pre-registrazione, e' una riparazione
dichiarata. Pitfall 68.

### 2. Il pavimento del lato 2 non esiste

`V_scr_3_6` era identica a `V_scr_1_3` su tutti e dieci i prompt, scarto massimo esattamente 0.
Non per un errore di copia. Il codice diceva

```python
V_scr_1_3 = calc_loo_v(A_scrA, A_scrC, prompts)   # scramble_A vs scramble_C
V_scr_3_6 = calc_loo_v(A_scrC, A_scrA, prompts)   # scramble_C vs scramble_A
```

la stessa coppia con gli argomenti scambiati, e `calc_loo_v` e' **simmetrica per costruzione**:
scambiarli scambia i due termini della somma e lascia il risultato invariato. Le due colonne
erano identiche per algebra.

Nessuno scramble e' ancorato su Block_6 — `A`,`B` su Block_1 e `C`,`D` su Block_3 — e che i
pavimenti non siano intercambiabili lo dice il banco: tre ancoraggi, 0.65 punti di escursione.

| ancoraggio | pavimento |
|---|---|
| `A` vs `B` (Block_1, Block_1) | +0.6070 |
| `C` vs `D` (Block_3, Block_3) | +0.1837 |
| `A` vs `C` (Block_1, Block_3) | -0.0396 |

Servono `scramble_E` ed `scramble_F` su Block_6 allo stesso D = 0.04500: **60 immagini**,
10 stili × 3 seed × 2 condizioni. Finche' non esistono il lato 2 e' **non misurato**. Pitfall 69.

### 3. La diramazione stava su 0.024

«Asimmetria di Propagazione» dipendeva da |V(1,3) − V(3,6)| = 0.2737 contro un margine di 0.25:
oltre di 0.0237. Ricalcolata per prompt, quella differenza da' un sign-flip esatto su n = 10 con
**p = 0.0586** e un intervallo per prompt da −0.768 a +0.390. Il margine 0.25 non era stato
calibrato sulla dispersione dei dieci stili, che era disponibile. Pitfall 61 in forma nuova.

> **Correzione alla revisione.** Il documento scrive «3 prompt su 10 hanno lo scarto nel verso
> della media; gli altri sette vanno al contrario». E' invertito: **7 su 10 vanno nel verso
> della media** e 3 al contrario. La critica regge — una diramazione scelta su una stima che non
> supera la propria soglia — ma la concordanza fra prompt non e' il punto debole descritto.

### 4. Due cose che la revisione non diceva

**«Frequenze Spaziali» non e' uno spazio, e' un arto morto.** Una sola feature, e ogni sua
statistica vale esattamente 0.0000 con p = 1.0000: V, pavimenti, Delta, tutto. Con una
dimensione sola il coseno fra due vettori vale ±1 e la statistica LOO degenera. Contarlo fra gli
spazi che «atterrano su Centro Piatto» e' contare un arto che non misura niente.

**Il ramo 1 dell'albero e' il ramo di fallimento.** Ci si atterra quando almeno un contrasto non
supera il proprio nullo. Contare quattro spazi che ci atterrano come quattro voti concordi per
«l'effetto sta ai confini» scambia una **mancata reiezione** per un risultato: la revisione
chiede di portare quel 4-su-5 sopra la piega, e in quella forma non va fatto. Nell'albero
rivisto il ramo si chiama «Nessuna separazione dal nullo (ramo di fallimento)», e gli spazi in
cui il lato 2 non e' misurato ricevono il ramo 0.

### Quello che regge davvero

Il contrasto **Block_1 vs Block_6** e' positivo e significativo sotto **ogni** pavimento del
banco, non solo sotto quello scelto:

| pavimento | Delta(1,6) |
|---|---|
| omologo Block_1 (`A` vs `B`) | +0.3485 |
| media cross | +0.3925 |
| omologo Block_3 (`C` vs `D`) | +0.7718 |
| `A` vs `C` | +0.9950 |

Ed e' significativo in tre spazi su cinque (p = 0.0020 in Tessitura, Tratteggio e Palette). Ma
e' il risultato **gia' stabilito** da `rotations_block1_vs_block6_results.md`: il triangolo non
lo aggiunge, lo conferma. Quello che il triangolo doveva aggiungere e' il blocco di mezzo, ed e'
esattamente li' che non decide.

---

## 2. Punteggi Leave-One-Out per Ciascuno dei 10 Prompt Stilistici

Tabella analitica dei punteggi calcolati con la procedura Leave-One-Out cross-prompt nello spazio primario Tessitura (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy` z-standardizzate):

| Prompt ID | V(1,3) | V(3,6) | V(1,6) | V_scr,cross | V_scr(1,1) | Delta(1,3) | Delta(3,6) senza pavimento |
|---|---|---|---|---|---|---|---|
| `S01_oil` | +0.1873 | +0.4842 | +1.1067 | +0.6293 | +0.3723 | -0.4420 | -0.1451 |
| `S02_linocut` | +0.0737 | +0.5522 | +0.9524 | +0.7836 | +0.4688 | -0.7099 | -0.2314 |
| `S03_cyberpunk` | -0.1236 | +0.5575 | +1.0174 | +0.3406 | +0.8566 | -0.4642 | +0.2169 |
| `S04_gouache` | +0.1520 | +0.1175 | +0.8977 | +0.6126 | +0.7309 | -0.4606 | -0.4951 |
| `S05_pencil` | +0.2168 | -0.0026 | +0.9847 | -0.0802 | +0.5335 | +0.2971 | +0.0776 |
| `S06_pastel` | +0.2030 | +0.3455 | +1.0572 | +0.5318 | +0.6990 | -0.3288 | -0.1863 |
| `S07_comic` | -0.0269 | +0.5813 | +0.9012 | +0.6068 | +0.3409 | -0.6337 | -0.0254 |
| `S08_papercraft` | +0.1848 | -0.2051 | +1.0234 | +0.9796 | +0.7348 | -0.7947 | -1.1847 |
| `S09_fresco` | +0.1242 | +0.5300 | +1.0309 | +0.6157 | +0.8804 | -0.4915 | -0.0857 |
| `S10_synthwave` | -0.1895 | +0.5782 | +0.5832 | +0.6102 | +0.4529 | -0.7997 | -0.0320 |


---

## 3. Coerenza Interna e Geometria dei Centroidi

* **Coerenza Intra-Blocco (Coseno medio tra prompt dello stesso blocco)**:
  - $\text{coh}(Block\_1) = +0.9204$
  - $\text{coh}(Block\_3) = +0.3138$
  - $\text{coh}(Block\_6) = +0.9599$
  - $\text{coh}(scramble\_A) = +0.9044$ | $\text{coh}(scramble\_B) = +0.4914$
  - $\text{coh}(scramble\_C) = -0.0770$ | $\text{coh}(scramble\_D) = +0.2376$

* **Coseno tra Centroidi Medi (Separazione Direzionale Grezza vs Disattenuata)**:
  - $Block\_1$ vs $Block\_3$: cos grezzo = **+0.8862**, disattenuato = **+1.6491**
  - $Block\_3$ vs $Block\_6$: cos grezzo = **+0.4790**, disattenuato = **+0.8729**
  - $Block\_1$ vs $Block\_6$: cos grezzo = **+0.0188**, disattenuato = **+0.0200**

* **Quota Antisimmetrica ($\|A\| / (\|S\| + \|A\|)$)**:
  - $Block\_1$: **0.498** (dominanza antisimmetrica)
  - $Block\_3$: **0.466**
  - $Block\_6$: **0.441**

---

## 4. Analisi di Robustezza sugli Spazi Stilistici Secondari

| Spazio | Dim | V(1,3) | V(3,6) | V(1,6) | Delta(1,3) con media cross (p) | Delta(3,6) (p) | Delta(1,6) (p) | Regime |
|---|---|---|---|---|---|---|---|---|
| Tessitura (Primario) | 3 | +0.0802 | +0.3539 | +0.9555 | -0.4828 (0.0039) | -0.2091 (0.0859) | +0.3485 (0.0020) | 0. Non determina |
| Tratteggio e Bordi | 3 | +0.1385 | +1.1596 | +1.0923 | -0.0044 (0.9766) | +1.0166 (0.0039) | +0.9203 (0.0020) | 0. Non determina |
| Ombreggio e Crosshatch | 2 | +0.4064 | -0.1469 | +1.1960 | -0.3259 (0.2246) | -0.8792 (0.0020) | +0.4622 (0.0996) | 0. Non determina |
| Frequenze Spaziali | 1 | +0.0000 | +0.0000 | +0.0000 | +0.0000 (1.0000) | +0.0000 (1.0000) | +0.0000 (1.0000) | 0. Non determina |
| Spazio Palette | 5 | +0.2371 | +0.1644 | +0.9651 | -0.1571 (0.1016) | -0.2298 (0.0039) | +0.8017 (0.0020) | 0. Non determina |

**Come leggere questa tabella, e come non leggerla.** Con il pavimento medio nessuno spazio ha
entrambi i Delta primari positivi, e in tutti e cinque il lato 2 non e' misurato, quindi tutti
ricevono il ramo 0. La lettura da **non** fare e' contare i cinque «ramo di fallimento» come
cinque conferme concordi: e' il ramo su cui si atterra quando non si separa dal nullo. E
«Frequenze Spaziali» va tolto del tutto dal conteggio — una feature sola, ogni statistica
esattamente 0.0000 e p = 1.0000.

La riga che sopravvive alla tabella e' l'ultima colonna del Delta(1,6): positiva in tutti e
cinque gli spazi e significativa in tre.


---

## 5. Quality Control Visivo

I contact sheet completi a 11 condizioni $\times$ 3 seed per tutti i 10 stili sono stati generati e salvati in [`qc_output/rotations_triangolo/`](../qc_output/rotations_triangolo/):
* `qc_S01_oil.png` .. `qc_S10_synthwave.png`

---

## 6. Risposta alla Domanda Aperta di Ricerca

Alla domanda iniziale:
*«La separazione direzionale osservata riflette una reale specializzazione funzionale o la pura
prossimita' topografica ai confini della rete?»*

**Il triangolo non risponde, e la domanda resta aperta.**

Il lato che avrebbe dovuto decidere — Block_3 contro Block_6, cioe' se il centro si distingue
dall'uscita — non ha un nullo proprio e non e' misurato. Il lato Block_1 contro Block_3 non si
separa dal nullo sotto la regola dichiarata; sotto quella usata prima si separava, e la
differenza fra le due regole era una scelta fra nulli scambiabili. Resta che Block_1 e Block_6
si separano da qualunque nullo del banco, che e' cio' che gia' sapevamo prima di costruire il
triangolo.

La conseguenza va riportata dove la domanda e' stata posta: la §2 di
[`rotations_block1_vs_block6_results.md`](rotations_block1_vs_block6_results.md) **resta aperta**.

**Cosa la chiuderebbe, in ordine di costo.** I 60 render di `scramble_E`/`scramble_F` ancorati su
Block_6 danno al lato 2 il suo pavimento e rendono percorribile l'albero: mezz'ora di macchina.
Il margine di equivalenza va ricalcolato sulla dispersione dei dieci stili prima di essere
riusato, o la diramazione va tolta dal disegno. Le quattro coppie cross erano gia' calcolabili
dalle immagini esistenti e sono ora nel CSV per prompt: quel punto e' chiuso senza nuovi render.
