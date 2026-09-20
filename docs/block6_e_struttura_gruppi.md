# La teoria su Block 6, e i gruppi non contigui

**Data**: 2026-09-20 · **Materiale**: `benchmark_mappa` (519 render, entrambi i segni, sei dosi) e
i 168 render dei blocchi singoli. Nessuna generazione nuova.

---

## 1. Un test sbagliato, riconosciuto e sostituito

Primo tentativo: modellare la differenza come `(modificata − baseline) = a · passa-alto(baseline)`,
un filtro lineare a un parametro. Risultato: `a ≈ −1.1` e σ al massimo del range **per tutte e
dodici le combinazioni blocco × segno**, con R² fra 0.17 e 0.29.

Quel valore è un artefatto. Se il dettaglio fine dell'immagine modificata è **scorrelato** da
quello del baseline, i minimi quadrati danno $a \to -1$ per costruzione, perché
$\langle h, x\rangle \approx 0$ e $\langle h, b\rangle = \langle h, h\rangle$. Il test misurava
la decorrelazione, non la sfocatura, e avrebbe dato lo stesso risultato su rumore puro. Scartato
e rifatto con misure dirette. Vedi pitfall 59.

## 2. La teoria dell'utente, misurata

> «Amplificandolo in positivo, l'effetto è una grana molto forte, accentuata e brillante, in modo
> uniforme sull'immagine come se la sua filigrana si bruciasse. In negativo invece sembra
> sfocarsi e scurirsi, come se ogni pixel si fosse mescolato con una fusione di moltiplicazione e
> allargato, fondendosi con i vicini.»

Dose 0.200, rapporti rispetto al baseline dello stesso seed, 6 celle:

| blocco | segno | alta freq. | var. Laplaciano | luminanza | uniformità della grana |
|---|---|--:|--:|--:|--:|
| *baseline* | | 1.00× | 1.00× | — | 0.440 |
| B6 | **pos** | 0.99× | 0.94× | **+5.4** | **0.341** ← la più uniforme di tutte |
| B6 | **neg** | **0.79×** | **0.81×** | **−9.0** | **0.666** ← la meno uniforme di tutte |
| B1 | pos | 0.86× | 0.81× | −1.1 | 0.419 |
| B5 | pos | 0.86× | 0.68× | +4.5 | 0.575 |

**Il negativo è confermato in pieno e con precisione.** Alta frequenza a 0.79×, varianza del
Laplaciano a 0.81×, luminanza **−9.0** su 255 — il calo più forte misurato in tutto l'esperimento,
quattro volte il secondo. Sfoca e scurisce, esattamente come descritto, 6/6 celle concordi.

E il dettaglio che l'utente ha aggiunto è quello che distingue il meccanismo: **una sfocatura pura
conserva la luminanza media.** Un calo di 9 punti insieme alla perdita di alta frequenza non è una
sfocatura, è una composizione di tipo moltiplicativo — che è la parola che ha usato lui guardando
le immagini, prima di qualunque misura.

**Il positivo è confermato in una forma diversa da quella attesa.** L'alta frequenza **non
aumenta** (0.99×): il totale resta quello. Ma la sua **distribuzione spaziale** cambia più che in
qualunque altra condizione — il coefficiente di variazione fra riquadri scende da 0.440 a
**0.341**, il valore più basso di tutte e dodici le condizioni.

Non aggiunge grana: **la ridistribuisce in modo uniforme.** La grana compare dove non ce n'era —
coerente con la misura indipendente che a dose alta ogni modifica amplifica di 3.3–4.8× il
residuo ad alta frequenza **nelle zone piatte**. Più il +5.4 di luminanza. «Come se la filigrana
si bruciasse, in modo uniforme sull'immagine» è una descrizione accurata di un appiattimento della
varianza di grana verso l'alto.

## 3. È una manopola di messa a fuoco?

Probabilmente no, e il dato dice perché.

La firma di una manopola di fuoco è che l'effetto sull'alta frequenza **si inverta col segno**.
Differenza pos − neg sull'alta frequenza, test dei segni esatto su 6 celle:

| blocco | pos | neg | differenza | p |
|---|--:|--:|--:|--:|
| B1 | 0.86× | 1.09× | −0.24 | **0.031** |
| B3 | 1.08× | 0.97× | +0.11 | **0.031** |
| B4 | 0.86× | 1.04× | −0.18 | **0.031** |
| B5 | 0.86× | 1.02× | −0.15 | **0.031** |
| **B6** | 0.99× | 0.79× | +0.20 | **0.156** |

**B6 è l'unico blocco in cui l'effetto sull'alta frequenza non si inverte in modo significativo.**
Quattro altri blocchi si comportano da manopole di fuoco molto meglio di lui — e in verso opposto
all'atteso: il loro *positivo* riduce l'alta frequenza.

Quello che distingue B6 non è il fuoco. È che ha la maggiore escursione di **luminanza**
(+5.4 / −9.0, nessun altro supera ±4.5) e la maggiore escursione di **uniformità della grana**
(0.341 / 0.666, contro un baseline di 0.440). Descritto meglio come un controllo di
**esposizione e distribuzione della grana**, asimmetrico nei due versi.

**Sull'ipotesi VAE**: non è affrontabile con queste misure, che sono tutte sui pixel dopo la
decodifica. Un test diretto esiste ed è semplice — salvare il **latente** prima del VAE e
ripetere le stesse tre misure lì. Se l'escursione di uniformità è già nel latente, B6 agisce
sulla rappresentazione; se compare solo dopo la decodifica, è il VAE a produrla da un latente
che è cambiato in altro modo. Sono due conclusioni diverse e le distingue un salvataggio di file.

## 4. Gruppi non contigui: reali, ma sopravvalutati dal metodo

Raggruppamento gerarchico dei 28 blocchi **senza vincolo di contiguità**, su 1 − coseno:

| partizione | separazione (tutti i dati) |
|---|--:|
| cluster liberi, k = 6 | **+0.5784** |
| migliore contigua, k = 6 (2, 7, 12, 17, 26) | +0.2936 |
| partizione in uso (5, 10, 15, 20, 24) | +0.1166 |

I cluster liberi **non sono contigui**: a k=3 il primo raggruppa 0, 2, 3, 4, 8, 9, 17, 18, 23, 24,
25 — blocchi iniziali e finali insieme. Il che risponderebbe di sì alla domanda «ci sono cluster
che muovono le stesse cose in blocchi diversi».

**Ma il numero è gonfiato**, e con 28 punti in 23 dimensioni era prevedibile: l'algoritmo
ottimizza esattamente la misura con cui poi lo si giudica. Validazione incrociata — raggruppo su
un prompt, misuro sull'altro:

| k | separazione dove ho raggruppato | sull'altro prompt | tenuta |
|--:|--:|--:|--:|
| 3 | 0.498 | 0.176 | 35% |
| 4 | 0.547 | 0.253 | 46% |
| 5 | 0.594 | 0.218 | 37% |
| 6 | 0.596 | 0.228 | 38% |

Nel verso opposto: 15%, 53%, 60%, 57%.

Fuori campione i cluster liberi valgono **+0.18 … +0.30**, cioè **quanto la migliore partizione
contigua** (+0.20 su P01, +0.32 su P02) e non di più. Il +0.58 era per metà sovradattamento.

**Conclusione onesta**: il dato dice che *qualunque* raggruppamento fondato batte quello in uso
(+0.157 / +0.103, mai adattato). Non dice che i gruppi non contigui battano le bande contigue:
fuori campione le due opzioni pareggiano. L'ipotesi dei cluster sparsi resta aperta e richiede un
terzo prompt mai usato per decidere.

## 5. Conseguenza operativa per il prossimo test

Per rifare la composizione sui gruppi derivati dal dato, la scelta pratica è la **partizione
contigua ottimale (2, 7, 12, 17, 26)**:

* tiene fuori campione quanto i cluster liberi, senza il loro sovradattamento;
* è uno spazio di ipotesi molto più piccolo, quindi meno adattata di quanto sembri;
* si esprime come intervalli di blocchi, quindi è già eseguibile con il menu `target_block`
  esistente, senza scrivere strumenti nuovi.

I cluster non contigui richiederebbero un meccanismo di selezione per insiemi arbitrari, e vanno
rimandati finché non esiste un terzo prompt che li validi.
