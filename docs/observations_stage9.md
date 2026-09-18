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
