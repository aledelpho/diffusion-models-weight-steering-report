# Osservazioni dirette su stage 9 — registrate prima della misura

**Data**: 2026-09-18. Scritte dopo aver guardato i render di stage 9 e **prima** che esista uno
strumento che misuri ciò che descrivono. Sono osservazioni, non risultati: nessuna di esse è stata
testata, e nessuna può essere confermata sugli stessi render che l'hanno generata — è la regola di
`prereg_attribute_emergence_stage7.md`, *"a second find-by-looking is a second discovery, not a
confirmation of the first"*.

## Osservazione 1 — `blockshuf_neg` a 2.0x ha potere di sintesi, e fallisce solo sul fotorealismo

Alessandro, guardando gli 8 stili:

> `blockshuffle_neg` x2 aveva un notevole potere di sintesi — non è riuscito molto nelle immagini
> fotorealistiche con molti dettagli (le prime, risultano "plasticose") ma in tutti gli altri stili
> è quello che si è dimostrato più versatile e rispettoso della definizione di "stile".

Due affermazioni distinte, da tenere separate perché si misurano in modo diverso:

1. **Fallimento sul fotorealismo.** Su `S1_photo` la resa diventa plasticosa: il dettaglio ad alta
   frequenza collassa e le superfici perdono veridicità.
2. **Aderenza allo stile superiore altrove.** Sugli altri sette stili la stessa perturbazione produce
   immagini che rispettano *meglio* la clausola di stile dichiarata rispetto alle altre condizioni.

## Perché questa osservazione conta più del test che l'ha accompagnata

**Nessuno dei quattro spazi di misura di stage 9 misura l'aderenza allo stile.** Gli spazi 1-3 sono
palette a 24, 8 e 16 dimensioni; lo spazio 4 sono cinque scalari di tessitura. Nessuno risponde alla
domanda "questa immagine assomiglia a un acquerello". L'osservazione 1 vive interamente fuori dallo
strumento, esattamente come la morfologia del tratto viveva fuori da CLIP in §1.2.

## Il conflitto con il gate di qualità, e chi ha ragione

Il gate dell'emendamento 5 marca `blockshuf_neg_2x` come DEGRADED in 6 stili su 8:

| stile | z `edge_density` | z `lbp_entropy` | gate | osservazione diretta |
| --- | --- | --- | --- | --- |
| S1 fotografia | 22.418 | 11.018 | DEGRADED | plasticosa — **concorde** |
| S2 acquerello | 0.359 | 0.088 | PASS | buona |
| S3 lowpoly | 6.622 | 17.834 | DEGRADED | buona — **discorde** |
| S4 claymation | 6.136 | 2.645 | DEGRADED | buona — **discorde** |
| S5 ukiyo-e | 7.470 | 13.398 | DEGRADED | buona — **discorde** |
| S6 pixel art | 8.229 | 15.224 | DEGRADED | buona — **discorde** |
| S7 vetrata | 2.128 | 1.518 | PASS | buona |
| S8 carboncino | 12.747 | 131.715 | DEGRADED | buona — **discorde** |

Il gate misura lo scostamento in sigma di `edge_density` e `lbp_entropy` dal baseline. Una
perturbazione che cambia davvero la tecnica di resa muove molto quelle due quantità **proprio quando
funziona**. Il gate quindi **non distingue "danneggiato" da "fortemente e correttamente
ri-stilizzato"**, e penalizza il successo.

Conseguenza operativa immediata: il conteggio "18 celle su 24 degradate a 2.0x" **non è** un argomento
per scartare il braccio a 2.0x, e non va usato come tale. Le ragioni valide restano il confound di
ampiezza (nessun corpus soggetti a 2.0x) e la non robustezza della statistica alla convenzione di
centratura.

## Ipotesi che ne discende, da registrare prima di misurarla

> Le perturbazioni di peso non hanno un effetto uniforme sugli stili. Hanno un effetto **congruente**
> con gli stili la cui tecnica di resa è già riduttiva (acquerello, vetrata, lowpoly, xilografia,
> carboncino) e **distruttivo** per quelli che dipendono da dettaglio ad alta frequenza veridico
> (fotografia, resa realistica).

È coerente con la caratterizzazione di `blockshuffle` già a verbale in §1.1 del README — *"heavy,
multi-directional diagonal hatching with a rough, organic woodcut print texture"*. Un operatore da
xilografia applicato a una fotografia dà per costruzione un risultato plasticoso.

## Come si misura, con strumenti già in casa

Serve un asse di **aderenza allo stile**, che non esiste in nessuno dei quattro spazi. Due candidati,
entrambi già disponibili in questo repository:

1. **Similarità CLIP fra il render e la sola clausola di stile** (il testo `Style: ...` senza la parte
   `Subject: ...`). Nota l'inversione rispetto a §1.2: lì CLIP a 224×224 era lo strumento sbagliato
   perché la domanda riguardava la micro-struttura del tratto; qui la domanda è semantica — *assomiglia
   a un acquerello?* — ed è esattamente ciò che CLIP sa fare. La cecità documentata in §1.2 non si
   applica a questa domanda, e va detto esplicitamente per non importare per abitudine una conclusione
   che valeva per un'altra misura.
2. **`experiments/vlm_gate.py`**, già scritto, con scoring cieco alla condizione.

La misura preferibile è **appaiata**: aderenza della condizione meno aderenza del baseline, stesso
prompt e stesso seed, così che "quanto è facile ottenere quello stile" esca dal confronto.

## Cosa serve per trasformarla in un risultato

Un corpus nuovo. Queste osservazioni sono nate su questi render e non possono essere confermate su
questi render. Il disegno incrociato (stili × soggetti) serve anche a questo: se l'ipotesi di
congruenza regge, l'effetto della perturbazione sull'aderenza allo stile deve dipendere dallo stile e
**non** dal soggetto, il che è una previsione direzionale registrabile in anticipo.

---

## Osservazione 2 — `rand_pos` a 2.0x sposta la categoria del veicolo

Alessandro, sugli stessi render:

> `random_pos` x2 ha quasi esclusivamente creato dei "SUV" o macchine con un design tondeggiante
> cittadino, piuttosto che macchine da "rally" classiche.

Il prompt dice `a yellow and blue rally car`. Su 40 render (8 stili × 5 seed) la condizione
`rand_pos_2x` produce in larga maggioranza un tipo di veicolo diverso da quello nominato.

## Perché è di un'altra specie rispetto all'osservazione 1

L'osservazione 1 riguarda **come** il modello disegna: tecnica di resa, aderenza a una clausola di
stile. Questa riguarda **cosa** disegna: la categoria dell'oggetto cambia mentre il testo resta
identico. È la famiglia dell'Esperimento 2 — la perturbazione che tocca il contenuto e non solo la
resa — ma con il segno opposto: là un attributo nominato e trascurato *emergeva*, qui un attributo
nominato *si perde*.

Ed è invisibile a tutti e quattro gli spazi di misura, come l'osservazione 1: 24 dimensioni di
palette e cinque scalari di tessitura non possono vedere che un'auto da rally è diventata un SUV.

## La spiegazione concorrente, che va esclusa prima di credere a quella interessante

La lettura suggestiva è "randsign ha una firma semantica propria". La lettura banale, e più probabile
a priori, è: **randsign a 2.0x indebolisce il condizionamento testuale, e il modello ricade sul
proprio prior.** Per una scena "auto in ambiente naturale accidentato" il prior di un modello
generalista è plausibilmente un SUV. In quel caso non è che randsign "disegni SUV": è che smette di
leggere `rally` e la forma più probabile emerge.

Le due si distinguono con una previsione netta:

* Se è **caduta di condizionamento**, la deriva deve colpire *anche gli altri attributi nominati* —
  `yellow and blue`, `deep jungle`, `uneven street`, `reflective ponds` — in modo diffuso.
* Se è una **firma semantica specifica**, deve colpire la categoria del veicolo lasciando in piedi
  colore e ambientazione.

## C'è già un dato che parla a questa domanda

Stage 8, arm A, prompt vuoto (`data/stage8_armA_results.csv`): con nessun testo da leggere,
`rand_pos` produce lo spostamento di palette **più grande delle tre condizioni** — 188.9 contro 109.0
di `preset_pos` e 110.2 di `blockshuf_neg`. Una condizione che si muove di più proprio quando il testo
non c'è è coerente con "disturba il condizionamento", che è la lettura banale.

Non è dirimente — arm A è un solo prompt e misura palette, non semantica — ma indica da che parte
guardare per primo.

## Come si misura

La categoria del veicolo è un attributo **discreto e scorabile alla cieca**, quindi si misura con lo
stesso impianto dell'Esperimento 2, che è il pezzo di metodologia più solido del progetto:

* presenza/assenza di `rally car` contro `SUV / citycar` per render, scoring **cieco alla condizione**
  (render copiati sotto nomi hashati, chiave aperta dopo);
* unità di analisi il prompt, McNemar appaiato sui seed condivisi (pitfall 26);
* il baseline dello stesso prompt e seed come termine di confronto, per separare "il modello già
  faceva SUV" da "la perturbazione lo fa fare".

E in parallelo, la stessa scorata su due o tre degli altri attributi nominati (colore del veicolo,
ambientazione) per distinguere caduta di condizionamento da firma semantica.

## La dissociazione che le due osservazioni suggeriscono insieme

Messe una accanto all'altra, descrivono due condizioni che fanno cose di natura diversa a pari
spostamento:

| | agisce su | effetto osservato a 2.0x |
| --- | --- | --- |
| `blockshuf_neg` (strutturata) | tecnica di resa | aderenza allo stile preservata o migliorata; rompe solo il fotorealismo |
| `rand_pos` (non strutturata) | contenuto semantico | la categoria dell'oggetto nominato deriva |

Se regge, è la distinzione struttura/magnitudine del progetto riformulata su un asse nuovo: non
*quanto* si muove l'immagine, ma *quale livello* della generazione viene toccato — resa contro
contenuto. È l'ipotesi più interessante emersa da stage 9, e non è stata testata da niente.

---

## Osservazioni 3-6 — registrate 2026-09-18, con quantificazione sugli stessi render

Alessandro, chiudendo il giro:

> `preset_pos` x2 sembra desaturare, sfocare e sgranare leggermente le immagini.
> `rand_pos` x2 sembra solo aggiungere una leggera grana all'immagine.
> `preset_pos` e la sua versione x2 sembrano entrambi tendere verso un'accensione dei fari — che può
> essere un tratto "incluso" nella definizione di macchina, ma tale specifica non era stata espressa
> dal prompt. Un tratto emergente con maggiore probabilità rispetto agli altri preset.
> `preset_pos` tende anche a scurire le immagini.
> `blockshuffle_neg` inoltre ingrandisce generalmente il soggetto all'interno della scena.

`experiments/stage9_observation_quantification.py` mette un numero su quelle misurabili con colonne
già estratte. **Non è conferma**: è il passaggio "l'occhio diceva 95%, la misura dice 96.7%" del
prereg dell'asse di hatching. Sono gli stessi render che hanno generato l'osservazione.

### Quantificate e sostenute

| osservazione | metrica | `preset_pos` 1x | `preset_pos` 2x | concordanza a 2x |
| --- | --- | --- | --- | --- |
| scurisce | L\* medio pesato | −1.76 | −3.30 | 7/8 prompt · 32/40 immagini |
| desatura | croma media pesata | −1.22 | −1.38 | 6/8 · 26/40 |
| desatura | `colorfulness_hs` | −2.17 | −3.54 | 7/8 · 32/40 |
| sgrana | `lbp_entropy` | +0.04 | +0.07 | **8/8 · 40/40** |

E sono **specifiche della condizione**, il che è il punto: sulle stesse metriche `blockshuf_neg` va
nella direzione opposta, con concordanza altrettanto netta.

| metrica | `preset_pos` 2x | `blockshuf_neg` 2x |
| --- | --- | --- |
| `colorfulness_hs` | **−3.54** (7/8 in negativo) | **+27.69** (8/8 · 40/40 in positivo) |
| `lbp_entropy` | **+0.07** (8/8 · 40/40) | **−0.32** (8/8 · 37/40 in negativo) |
| L\* medio | −3.30 | +0.87 |

Due operatori quasi opposti su tre assi misurabili. `preset_pos` scurisce, desatura e sgrana;
`blockshuf_neg` schiarisce, satura fortemente e leviga.

### Non sostenuta dai numeri

**`rand_pos` x2 "aggiunge solo una leggera grana"** non regge sull'entropia LBP: +0.004 a 1x e
−0.037 a 2x, con 4/8 prompt. Quello che `rand_pos` 2x fa in modo netto è invece **saturare**
(`colorfulness_hs` +9.13, 8/8 prompt, 38/40 immagini), che l'osservazione non menziona. Due letture
possibili e non separate: o l'impressione di grana era sbagliata, o `lbp_entropy` non misura ciò che
in italiano si chiama grana (è diversità di pattern binari locali, non rumore ad alta frequenza) e
serve un proxy diverso, per esempio la quota di energia nelle bande alte della FFT.

### Non misurabile con gli strumenti attuali

**`blockshuf_neg` ingrandisce il soggetto.** La colonna `subject_frac` dà il segno opposto (−0.008 a
1x, −0.029 a 2x), ma **quella colonna non misura questo**: è definita come complemento della "carta"
stimata dai cluster a luminanza estrema, ed è tarata su ritratti in primo piano con `white
background`. Su una scena di giungla non c'è nessuna carta, quindi il numero non riguarda la
dimensione dell'auto. L'osservazione **non è testata**, né a favore né contro.

La metrica giusta è quella che Alessandro ha proposto da sé: **frazione di area occupata dal
giallo-blu dell'auto**. Va costruita — segmentazione per colore della carrozzeria e area relativa — e
non esiste ancora.

**Accensione dei fari.** Non misurabile automaticamente, richiede scoring binario cieco alla
condizione. Va trattata con l'impianto dell'Esperimento 2, che è il pezzo di metodologia più solido
del progetto.

## L'osservazione dei fari è la più importante, e potrebbe falsificare una conclusione a verbale

I fari non sono nominati nel prompt. Sono un tratto **implicato dall'oggetto** — una macchina ha i
fari — che emerge preferenzialmente sotto una condizione. Confrontato con l'Esperimento 2:

| | barnacoli (Esp. 2) | fari (osservazione) |
| --- | --- | --- |
| il tratto è nel prompt? | **sì**, e veniva ignorato | **no**, non è mai nominato |
| cosa fa la perturbazione | *recupera* un legame già stabilito dal testo | *aggiunge* un tratto dal prior dell'oggetto |

§2.2 conclude: *"la perturbazione non aggiunge l'attributo e non ripara la negligenza — agisce come
guadagno su un legame che il prompt deve già avere stabilito"*. Se i fari reggono, **quella frase è
troppo forte** e va ristretta: la perturbazione può anche alzare la salienza di tratti che vengono
dal prior dell'oggetto e non dal testo. È una potenziale falsificazione di una conclusione pubblicata,
prodotta guardando.

**Confound da escludere per primo, ed è ora quantificato.** `preset_pos` è la condizione che scurisce
(7/8 prompt, 32/40 immagini). Fari accesi sono più probabili in una scena scura. Quindi il test deve
appaiare sulla luminanza: si scorano i fari alla cieca e si verifica se l'effetto sopravvive a parità
di L\* misurato, oppure se scompare una volta tenuta ferma la luminosità. I due sono separabili con i
dati che ci sono più una passata di scoring.

---

## Correzione — 2026-09-18, dopo la misura dei bounding box

**La sezione "Quantificate e sostenute" qui sopra va letta con questa correzione.**

Era scritto che `blockshuf_neg` "satura fortemente" (`colorfulness_hs` +27.69 a 8/8 prompt e 40/40
immagini) e che `preset_pos` "desatura" (−3.54), presentandole come firme cromatiche delle due
condizioni, quasi opposte fra loro.

La misura dei bounding box a verità umana mostra che **in larga parte non sono firme cromatiche**.
Nelle scene di stage 9, area del soggetto e colorfulness sono accoppiate meccanicamente: nel **solo
baseline**, dove non c'è nessuna perturbazione, correlano a r = +0.776, con pendenza
`colorfulness = 13.4 + 238.1 × frazione_area`. Un'auto più grande mette più pixel saturi in una scena
con sfondo verde.

Applicando quella pendenza alle variazioni di dimensione misurate, il cambiamento di area **spiega
interamente** quello di saturazione per quattro condizioni su sei, e per blockshuffle lo sovrastima
(129% a 2×, 145% a 1×): a parità di ingrandimento la perturbazione *riduce* la saturazione rispetto
all'atteso.

**Quindi**: `blockshuf_neg` ingrandisce il soggetto, e la saturazione segue. `preset_pos` lo
rimpicciolisce leggermente, e la desaturazione segue. Restano valide e non toccate da questa
correzione le altre due metriche, che non passano dalla dimensione in questo modo: lo scurimento
(L\* medio) e la grana (`lbp_entropy`, 8/8 prompt e 40/40 immagini).

Il controllo sul corpus dei ritratti di stage 7 è negativo, e va detto: là `subject_frac` si muove al
livello del caso sotto perturbazione e correla con la croma solo a r = +0.263, quindi **§1.4 e §1.5
non sono toccate**. Il mediatore è specifico dei corpus a scena intera.

Dettagli e verifica in [`stage10_bbox_verification.md`](stage10_bbox_verification.md).
