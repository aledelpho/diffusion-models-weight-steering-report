# Fari — scoring cieco, risultati

**2026-09-18.** 280 immagini di stage 9, scoring cieco alla condizione secondo
`BRIEF_stage10_strumenti.md`. Chiave scritta alle 12:17, scoring iniziato alle 12:28, chiave aperta
dopo. Ordine mescolato: condizioni adiacenti uguali 39 su 279, atteso ~40.

**Non è una conferma.** L'osservazione dei fari è nata guardando questi render e qui viene misurata
sugli stessi. È il passaggio *"l'occhio diceva 95%, la misura dice 96.7%"*. La conferma richiede
render nuovi.

## Il risultato

| condizione | accesi / validi | tasso | ambigui |
| --- | --- | --- | --- |
| baseline | 10 / 35 | 0.286 | 5 |
| `preset_pos_1x` | 16 / 36 | 0.444 | 4 |
| **`preset_pos_2x`** | **31 / 38** | **0.816** | 2 |
| `blockshuf_neg_1x` | 6 / 38 | 0.158 | 2 |
| **`blockshuf_neg_2x`** | **0 / 39** | **0.000** | 1 |
| `rand_pos_1x` | 7 / 39 | 0.179 | 1 |
| `rand_pos_2x` | 2 / 36 | 0.056 | 4 |

L'osservazione diretta riguardava solo `preset_pos`. **La misura aggiunge il verso opposto**, che
nessuno aveva notato: `blockshuf_neg` a 2× spegne i fari in **39 immagini su 39**, comprese quelle
dove il baseline li aveva accesi 4 volte su 5 (claymation) e 2 su 2 (vetrata).

## Per prompt — il dettaglio che cambia la lettura statistica

| prompt | baseline | `preset_pos_2x` | `blockshuf_neg_2x` |
| --- | --- | --- | --- |
| S1 photo | 3/5 | **5/5** | 0/5 |
| S2 watercolor | 0/3 | **5/5** | 0/5 |
| S3 lowpoly | 1/5 | **5/5** | 0/5 |
| S4 claymation | 4/5 | **5/5** | 0/5 |
| S5 ukiyo-e | 0/5 | 0/5 | 0/5 |
| S6 pixel | 0/5 | 1/3 | 0/4 |
| S7 glass | 2/2 | 5/5 | 0/5 |
| S8 charcoal | 0/5 | **5/5** | 0/5 |

`preset_pos_2x` è a **5/5 in sei stili su otto**, compresi due che partivano da zero — acquerello
(0/3 → 5/5) e carboncino (0/5 → 5/5). Un disegno a carboncino monocromatico che accende i fari in
tutti e cinque i seed.

I due prompt che non si muovono **non sono controesempi**:

* **S7 vetrata** parte già a 2/2, cioè al soffitto: non può salire.
* **S5 ukiyo-e** è a 0 in *tutte e sette* le condizioni: è uno stile che non rappresenta mai fari
  accesi, non una risposta negativa alla perturbazione.

## Il test è al suo pavimento, e va letto sapendolo

`preset_pos_2x`: Δ = +0.467, **p esatto = 0.0312**, Holm = 0.1875.

Quel p **è** il pavimento: dei 6 prompt informativi (gli altri due hanno Δ = 0 per soffitto e per
stile non rappresentativo), tutti e 6 si muovono nella stessa direzione, e $2/2^6 = 0.0312$ è il
minimo raggiungibile. Con Holm su 6 condizioni servirebbe $p \le 0.0083$, che a 6 prompt informativi
**nessun effetto di qualunque ampiezza può raggiungere**. È lo stesso soffitto strutturale descritto
in §1.3 per la famiglia colour-free a 6 prompt: la regola 8 dell'errors_log applicata qui.

Quindi: effetto grande, concordanza perfetta fra i prompt che potevano muoversi, e impossibilità
strutturale di superare la soglia corretta. Non va scritto né come confermato né come debole.

## Il confound della luminanza — controllato, e l'effetto sopravvive

La luminanza **conta davvero**: sul corpus intero il tasso di fari accesi è 0.448 nel terzile scuro,
0.276 nel medio, 0.103 nel chiaro. E `preset_pos` è la condizione che scurisce. Il confound era
reale.

Ma non spiega l'effetto:

| condizione | terzile scuro | terzile medio | terzile chiaro |
| --- | --- | --- | --- |
| baseline | 0.30 (n=10) | 0.44 (n=16) | **0.00 (n=9)** |
| `preset_pos_2x` | 1.00 (n=20) | 0.67 (n=9) | **0.56 (n=9)** |
| `blockshuf_neg_2x` | 0.00 (n=9) | 0.00 (n=8) | **0.00 (n=22)** |

Nel terzile **più chiaro** il baseline non accende mai i fari (0 su 9) e `preset_pos_2x` li accende
in 5 casi su 9. A luminosità comparabile, la condizione fa ancora la differenza. E
`blockshuf_neg_2x` è a zero in tutti e tre i terzili, 22 immagini nel chiaro comprese.

**La regola di lettura fissata nel brief è soddisfatta**: l'effetto sopravvive a luminanza tenuta
ferma, in entrambi i versi.

## Cosa fa questo a §2.2

§2.2 del README conclude che la perturbazione *"non aggiunge l'attributo e non ripara la negligenza —
agisce come guadagno su un legame che il prompt deve già avere stabilito"*.

I fari **non sono nel prompt**. Eppure `preset_pos_2x` li porta da 0/3 a 5/5 sull'acquerello e da 0/5
a 5/5 sul carboncino, e `blockshuf_neg_2x` li toglie da un baseline a 4/5 e da uno a 2/2.

Nessuna delle due cose è "guadagno su un legame stabilito dal prompt". **La frase di §2.2 è troppo
forte come affermazione generale**: vale per il caso barnacoli, dove il tratto era nel testo ed era
ignorato, e non si estende a tratti che vengono dal prior dell'oggetto. Va ristretta al caso in cui
è stata misurata.

Questo resta soggetto alla riserva in testa al documento: è quantificazione su render che hanno
generato l'osservazione. La restrizione di §2.2 va scritta come *ipotesi sostenuta e da confermare*,
non come fatto stabilito.

## Candidata pitfall 35 — il viewer appende invece di sostituire

Tornando indietro per correggere un punteggio, il viewer **aggiunge una riga** invece di sostituire
quella vecchia. Il file grezzo ha **284 righe per 280 immagini**: quattro immagini ricorrette, due
con punteggio cambiato (2→0 e 0→1) e due riconfermate.

Senza accorgersene, entrambi i punteggi entrano nel conteggio e i tassi si gonfiano in silenzio —
`preset_pos_2x` leggeva 32/39 invece di 31/38. Numeri plausibili, conclusione invariata, ma sbagliati:
il profilo esatto delle pitfall di questo progetto.

`analyze_headlights.py` ora tiene l'**ultimo** punteggio per hash e solleva un'eccezione se il merge
cambia il numero di righe o se un'immagine resta senza punteggio (regola 5).

## Dimensionare la conferma

Con l'effetto osservato (Δ ≈ 0.47), permutazione sign-flip e Holm su 6 condizioni:

| prompt | potenza |
| --- | --- |
| 8 | 0.18 |
| 12 | 0.43 |
| 16 | 0.65 |
| 20 | 0.79 |

Ma il guadagno maggiore non viene dai numeri: viene dallo **schermare i prompt sui baseline**. Qui
due prompt su otto erano non informativi — uno al soffitto, uno a zero in ogni condizione. Una
selezione in due tempi come stage 7a/7b, che rende solo i baseline e ammette al round di conferma
solo i prompt il cui tasso di baseline sta **strettamente fra 0 e 1**, elimina quella perdita con una
regola deterministica e senza giudizio. Con quella schermatura, 16 prompt sono verosimilmente
sufficienti.

Il corpus di conferma deve essere di **oggetti diversi con un tratto implicato ma non nominato** —
non altre auto — altrimenti si conferma un fatto sui fari e non sul meccanismo.
