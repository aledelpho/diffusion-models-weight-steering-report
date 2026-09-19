# Pre-registrazione — Stage 2: l'asse di tratteggio su corpus nativo, due architetture

**Stato**: bozza da congelare. Nessun render generato al momento della scrittura.
**Corpus**: `data/prompts_anima_native.json`, 10 prompt, hash verificati.
**Modelli**: Anima Base v1.0 e Krea-2 Turbo, stesso corpus, stesso protocollo.

---

## 1. Perché questo esperimento esiste

Lo stage 1 ha prodotto due risultati e una domanda aperta.

* **Risultato**: la trasposizione gerarchica del preset separa da `randsign` sulla morfologia
  del tratto, due feature al pavimento del test dopo correzione per molteplicità. La firma
  sopravvive al cambio di architettura.
* **Risultato**: `blockshuf_neg` è l'unica condizione che muove il colore, su entrambe le
  architetture. Replica specifica per condizione.
* **Domanda aperta**: su Krea-2 `preset` e `blockshuffle` spingono il tratteggio in direzioni
  **opposte** ($-0.370$ contro $+0.288$, segno predetto in anticipo, 16/16 prompt). Su Anima
  si sono mossi **insieme** ($+0.292$ contro $+0.280$, confronto diretto $p = 0.86$).

Due spiegazioni, non distinte dai dati esistenti:

1. l'asse di tratteggio è una proprietà di Krea-2 e non si trasferisce;
2. i prompt dello stage 1 erano scritti per Krea-2 e Anima li ha digeriti male, quindi
   l'asse è stato misurato su una comprensione degradata.

Questo esperimento le separa, generando su un corpus in **formato nativo Anima** e
replicando lo stesso corpus su Krea-2. È l'applicazione diretta del pitfall 48: il protocollo
dei prompt lo detta il modello con la tolleranza di input più stretta, e si porta verso l'alto.

## 2. Proprietà del corpus, dichiarate prima di misurare

Misurate su `data/prompts_anima_native.json` prima di qualunque render.

| proprietà | valore |
|---|---|
| densità relazionale | **0.028 verbi/parola** (Krea-2 I07: 0.105, quasi 4×) |
| `hatched shadows` | 10/10 — l'asse di tratteggio è definito su questo corpus |
| `white background, simple background` | 10/10 — la misura di sfondo è ben definita |
| `gradients` | 10/10 — **nuovo rispetto al corpus Krea-2** |
| `realistic comic style` | 9/10 (A05 dice `western cartoon style`) |
| camera | 3 dal basso · 4 dall'alto · 3 close-up |
| lunghezza | 72–122 parole, mediana 95 |

Due conseguenze da tenere presenti in lettura, non da correggere:

* **`gradients` in 10/10 è una interazione potenziale.** Su Krea-2 il preset comprime i
  passaggi tonali; qui il prompt chiede esplicitamente gradienti. Se le metriche tonali si
  comportano diversamente dal corpus Krea-2, questa è una spiegazione candidata e va citata
  prima di cercarne altre.
* **A05 è l'unico `western cartoon style`.** Su 10 prompt pesa il 10%. Resta nel corpus come
  test di generalità interna; se è un outlier su una feature, va riportato, non rimosso.

## 3. Le tre ipotesi primarie

Famiglia primaria di **3 test**, correzione di Holm interna alla famiglia. Con $n = 10$ il
pavimento del test di permutazione esatto a scambio di segno è $2/2^{10} = 0.00195$, che
lascia spazio fino a 25 test: la famiglia è tenuta a 3 per scelta, non per vincolo.

Unità statistica: **il prompt**, con i 5 seed mediati preventivamente. $df = 9$.

**P1 — L'asse di tratteggio esiste su Anima?**
Confronto `preset` contro `blockshuf_neg` su `crosshatch_entropy_mean`, appaiato per prompt.
**Predizione direzionale dichiarata**: le due condizioni si separano con **segni opposti**
rispetto al baseline, come su Krea-2. Una separazione significativa con lo **stesso** segno
per entrambe **non** conta come conferma parziale: conta come fallimento della predizione,
perché è esattamente il pattern osservato nello stage 1.

**P2 — La separazione struttura/ampiezza regge su prompt nativi?**
`preset` contro `randsign` su `crosshatch_entropy_mean`. Replica diretta del primario dello
stage 1, su corpus diverso. Criterio: CI 95% bootstrap che esclude lo zero.

**P3 — La specificità cromatica di `blockshuf_neg` replica?**
`colorfulness_hs`: `blockshuf_neg` contro la media di `preset` e `randsign`. Criterio: CI 95%
che esclude lo zero **e** nessuna delle altre due condizioni significativa contro il baseline
sulla stessa feature. La seconda clausola serve perché la claim è di *specificità*, non di
effetto: se anche il preset muovesse il colore, la replica non sarebbe quella di Krea-2.

**Tutti e tre i test si eseguono identici sui due modelli.** Il confronto fra i due esiti è
il risultato cross-architettura, e non richiede un test proprio: è la tabella dei segni.

## 4. Famiglia secondaria, dichiarata e corretta a parte

5 test, Holm interno alla famiglia, riportati come secondari a prescindere dall'esito:
`contour_mean_length_px` (preset vs randsign), `white_background_pct` (randsign vs baseline),
`stroke_width_median_px`, `edge_density`, `glcm_homogeneity` (tutte preset vs randsign).

**Esclusa in anticipo**: `lbp_entropy`. Nello stage 1 è salita in tutte e quattro le
condizioni, al pavimento in ciascuna, 10/10 prompt. Non discrimina e non va usata.

Tutto il resto è **descrittivo**: si riporta senza test e non entra in nessuna conclusione.

## 5. Calibrazione della dose — per effetto, non per spostamento dei pesi

Lo spostamento relativo di Frobenius **non è un'unità di dose portabile**: pitfall 44 (una
tabella di embedding al 99.96% della norma su Anima) e pitfall 49 (soglia di collasso a 100%
su Anima contro il 30% usabile). Qui la dose si appaia sull'effetto.

Per **ciascun modello**, prima di generare il corpus:

1. **Rumore di seed.** Render baseline su 2 prompt pilota (A01, A10) × 5 seed. Si calcola
   $\sigma_{\text{seed}}$ = distanza media fra seed dello stesso prompt nello spazio texture
   z-standardizzato (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy`, `edge_density`,
   `crosshatch_entropy_mean`).
2. **Sweep di dose** sul solo `preset`, stessi 2 prompt × 3 seed, moltiplicatori
   $\{1.00, 0.70, 0.50, 0.30, 0.20, 0.10\}$ del preset trasposto.
3. **Si sceglie la dose più piccola** che soddisfa **entrambe**:
   * spostamento medio dal baseline $\ge 3\,\sigma_{\text{seed}}$;
   * **cancello di collasso superato da tutte le immagini**: `edge_density` > 0.02,
     `glcm_contrast` > 2.0, `color_n_effective` > 2.5, `contour_n_components` > 50.
4. La stessa dose si applica a `blockshuf_neg` e `randsign` **dello stesso modello**, ciascuno
   riscalato individualmente al $D$ che quella dose produce sul `preset` (pitfall 45).
5. Dose e $\sigma_{\text{seed}}$ si registrano per iscritto **prima** di generare il corpus.

Nota sui valori di riferimento: nello stage 1 il braccio A ad Anima girava a dose 0.30 con
margine 3× sul cancello (densità di bordi minima 0.059 contro soglia 0.02) e **zero immagini
collassate su 250**. Il braccio B ne aveva 34 su 120. Il cancello è tarato su quella
separazione.

## 6. Cancello sui baseline, prima di misurare qualunque condizione

Identico allo stage 1 e da ripetere: si guardano i **50 baseline di ciascun modello** prima di
toccare le condizioni.

* Nessun tratteggio riconoscibile in un modello → P1 e P2 sono **indefiniti** su quel modello
  e vanno **esclusi**, non riportati come negativi.
* Baseline deformi o illeggibili → il regime di campionamento è sbagliato, si ritara.
* **Aderenza al prompt**: per ciascun modello si conta su quanti dei 10 baseline compaiono i
  tre attributi più specifici del prompt (annotazione binaria, 30 giudizi per modello). Se il
  divario di aderenza fra i due modelli supera il 30%, il corpus **non è condiviso** e il
  confronto cross-architettura va dichiarato confuso con la comprensione — che è esattamente
  il difetto che questo stage esiste per evitare.

## 7. Matrice

| | prompt | seed | condizioni | immagini |
|---|---:|---:|---:|---:|
| Anima, regime nativo (30 passi, CFG 5.5, `euler_ancestral`) | 10 | 5 | 4 | 200 |
| Krea-2, regime nativo (9 passi, CFG 1.0, `euler_ancestral`) | 10 | 5 | 4 | 200 |
| calibrazione (2 prompt, sweep dose, per modello) | 2 | 3–5 | 7 | ~80 |
| **totale** | | | | **~480** |

Condizioni: `baseline`, `preset`, `blockshuf_neg`, `randsign`.
Seed: 42, 777, 1337, 9999, 4242145.
`preset_nocross` **non** viene ripetuto: lo stage 1 ha già risposto — indistinguibile da
`preset` su 8 feature su 9.

Nomi file: `<prompt_id>_<condizione>_<modello>_seed<seed>_00001_.png`, cartella piatta
`benchmark_stage2/renders/`.

## 8. Regole di decisione, scritte prima

| esito | lettura |
|---|---|
| P1 con segni opposti su **entrambi** i modelli | L'asse di tratteggio è una proprietà dell'operazione, non dell'architettura. Il fallimento dello stage 1 era dei prompt, e il micro→macro è confermato come metodo. |
| P1 con segni opposti **solo su Krea-2** | L'asse è specifico di Krea-2. I prompt non erano il problema, e lo stage 1 va letto come risultato negativo valido. |
| P1 fallito su entrambi **sul corpus nativo** | L'asse dipende dal corpus, non dall'architettura. Rimette in discussione anche il risultato di §1.6 su Krea-2, che è misurato su un corpus solo. |
| P2 confermato, P1 fallito | Resta la separazione struttura/ampiezza, si perde la direzionalità. È la claim più debole già registrata nella revisione dello stage 1. |
| P3 confermato su entrambi | La specificità cromatica di `blockshuf_neg` è la proprietà più portabile del programma, e diventa il candidato naturale per il terzo modello. |

## 9. Cosa questo esperimento non può dire

* Non distingue **formato del prompt** da **contenuto del prompt**: il corpus nativo cambia
  entrambi insieme. Separarli richiederebbe gli stessi soggetti scritti nei due formati.
* Non tocca le rotazioni, che restano non trasposte su Anima.
* Non varia il regime di campionamento dentro un modello: ciascuno gira nel proprio, e il
  ponte dello stage 1 resta l'unico dato sull'argomento, per di più sotto-dosato.
* Con 10 prompt di un solo registro figurativo, un esito positivo riguarda i ritratti di
  personaggi a mezzo busto su fondo bianco, come ogni altro risultato di questo programma.
