# La mappa completa: sterzo contro deriva, e perché due blocchi concordi si annullano

**Data**: 2026-09-19, notte · **Materiale**: 519 render in `benchmark_mappa` (6 gruppi × 6 dosi
× **entrambi i segni** × 2 prompt sonda × 3 seed) più le 12 di `benchmark_composizione`.
Nessuna generazione nuova.

---

## 1. La decomposizione

Con positivo e negativo appaiati si separa, per ogni grandezza:

* **A = (Δ⁺ − Δ⁻)/2** — lo **sterzo**: la parte che si inverte cambiando segno al guadagno.
* **S = (Δ⁺ + Δ⁻)/2** — la **deriva**: la parte che accade in entrambi i versi.

Frazione di sterzo = |A|/(|A|+|S|). Vale 1 se la modifica è perfettamente reversibile, 0 se il
blocco fa la stessa cosa qualunque segno gli si dia.

### Al livello dei pixel: domina la deriva

| blocco | 0.020 | 0.050 | 0.120 | 0.200 | media |
|---|--:|--:|--:|--:|--:|
| B1 | 0.396 | 0.410 | 0.404 | 0.403 | 0.403 |
| B2 | 0.418 | 0.406 | 0.402 | 0.388 | 0.404 |
| B3 | 0.418 | 0.416 | 0.408 | 0.403 | 0.411 |
| B4 | 0.424 | 0.422 | 0.406 | 0.400 | 0.414 |
| B5 | 0.427 | 0.427 | 0.418 | 0.402 | 0.421 |
| **B6** | 0.418 | 0.431 | 0.442 | **0.459** | **0.434** |

Tutti fra 0.39 e 0.46: **meno della metà di ciò che un blocco fa ai pixel si inverte col segno.**
La maggior parte è deriva — la traiettoria si sposta, e si sposta in un modo largamente
indipendente dal verso della modifica. `B6` è l'unico la cui frazione di sterzo **cresce** con
la dose invece di calare.

### Al livello del tono: solo B1 sterza davvero

Dose 0.200, sei celle, test dei segni esatto.

| grandezza | blocco | A (sterzo) | p | S (deriva) | p | frazione |
|---|---|--:|--:|--:|--:|--:|
| alte luci | B1 | **−7.75** | 0.031 | −2.25 | 0.031 | 0.78 |
| | B4 | **+3.42** | 0.031 | +1.42 | 0.219 | 0.71 |
| | B5 | **+6.50** | 0.031 | +0.83 | 0.125 | 0.89 |
| contrasto | B1 | **−5.05** | 0.031 | −1.65 | 0.094 | 0.75 |
| | B5 | **+2.38** | 0.031 | +1.09 | 0.062 | 0.69 |
| | B4 | +0.87 | 0.438 | **+2.74** | 0.031 | 0.24 |
| saturazione | B1 | **−13.64** | 0.031 | +5.29 | 0.031 | 0.72 |
| | B3 | +3.69 | 0.062 | **+10.45** | 0.031 | 0.26 |
| | B5 | +4.88 | 0.094 | **+12.25** | 0.031 | 0.28 |
| | **B4** | −0.38 | 0.719 | **+12.51** | 0.031 | **0.03** |

## 2. Correzione a un risultato precedente

`docs/coerenza_traiettoria.md` §7 riportava che «B3 e B4 saturano fortemente (+14.1 e +12.1,
6/6)». **La direzione era attribuita a torto.** Con il guadagno **negativo** B4 satura di
**+12.89**, praticamente identico al +12.14 del positivo: la frazione di sterzo sulla
saturazione è **0.03**. B4 non satura: *qualunque* modifica a B4 satura, in entrambi i versi.

È una variante del pitfall 50 — attribuire al trattamento un effetto che non gli appartiene —
in una forma che solo il braccio negativo può smascherare. Chi misura un solo segno non può
distinguere uno sterzo da una deriva, e le due cose portano a decisioni opposte: uno sterzo è
una manopola, una deriva è un costo da pagare. Vedi pitfall 57.

L'unico blocco che **sterza** la saturazione è B1, verso il basso, −13.64 con p = 0.031.

## 3. Perché B5 e B4 si annullavano

La `previsione_01` è stata confermata su `B5+B1` e smentita su `B5+B4`, e l'esito registrava
che non c'era un meccanismo proposto. Ora c'è, ed è quantitativo.

Estraendo le 23 feature di stile e standardizzandole sui sei baseline, ogni condizione è un
**vettore di spostamento**. Coseni fra le direzioni, dose 0.200:

| | B1 | B2 | B3 | B4 | B5 | B6 | \|D\| |
|---|--:|--:|--:|--:|--:|--:|--:|
| B1 | 1.00 | 0.56 | −0.12 | −0.14 | **−0.34** | −0.16 | 8.19 |
| B4 | −0.14 | −0.40 | 0.72 | 1.00 | **+0.77** | 0.64 | 20.29 |
| B5 | −0.34 | −0.39 | 0.20 | 0.77 | 1.00 | 0.16 | 13.26 |
| B6 | −0.16 | −0.43 | 0.80 | 0.64 | 0.16 | 1.00 | **40.90** |

E le combinazioni, come somma vettoriale:

| combinazione | cos(A,B) | \|osservato\| | \|previsto\| | **rapporto** | cos(oss,prev) |
|---|--:|--:|--:|--:|--:|
| **B5 + B1** | **−0.34** | 12.87 | 12.98 | **0.99** | +0.93 |
| **B5 + B4** | **+0.77** | 19.12 | 31.62 | **0.60** | +0.74 |

**Quando due modifiche puntano in direzioni diverse si sommano come vettori; quando puntano
nella stessa direzione saturano.** B1 e B5 sono quasi ortogonali e la somma è esatta al 99%.
B4 e B5 puntano quasi nello stesso verso e la somma rende il 60%.

**L'ipotesi originale di saturazione era giusta nella sostanza e l'ho testata sulla grandezza
sbagliata.** Quattro scalari tonali con pavimenti e tetti non potevano distinguere saturazione
da antagonismo; la norma del vettore di spostamento lo ha fatto al primo colpo.

## 4. B6 si separa da tutti, su quattro misure indipendenti

| misura | B6 | gli altri |
|---|--:|---|
| spostamento nello spazio di stile | **40.90** | 2.6 – 20.3 |
| \|diff\| medio sui pixel, dose 0.200 | **0.1286** (il più basso) | 0.133 – 0.156 |
| coerenza di traiettoria, dose 0.200 | **0.164** (in altopiano) | 0.047 – 0.072 |
| frazione di sterzo sui pixel | **cresce** con la dose | cala |

Cambia le statistiche di stile più di chiunque, muove i pixel meno di chiunque, conserva la
traiettoria più di chiunque.

**Con una qualificazione che ne ridimensiona la lettura.** Lo spostamento di B6 è dominato da
una feature sola: `lbp_entropy` a **−33.6** z, con `lbp_uniform_share` a +14.6. B6 rende la
micro-texture **uniforme**. Non è «B6 cambia molto stile»: è «B6 appiattisce la varietà locale»,
coerente con il collasso di B6 già documentato altrove nel progetto.

**Controllo su una possibile illusione metrica.** La correlazione è invariante di scala: se un
blocco riducesse l'ampiezza della filigrana lasciandone il disegno, la coerenza resterebbe alta
per un motivo sbagliato. Misurata l'ampiezza: **tutti i blocchi amplificano** il residuo ad alta
frequenza nelle zone piatte di 3.3–4.8× (p = 0.031 per tutti), B6 di 3.99×, in mezzo al gruppo.
L'illusione è esclusa e la conclusione su B6 regge.

Risultato collaterale, universale e non previsto: **a dose 0.200 ogni modifica di peso inietta
grana nelle aree piatte, quadruplicandone l'ampiezza.** È un costo comune a tutti i blocchi e
nessuna delle metriche in uso lo catturava.

## 5. Cosa resta da capire

La regola del §3 poggia su **due soli punti**. È una relazione ordinale plausibile con una
pendenza stimata su due coppie, non una legge. Serve testarla su coppie non usate per
formularla: è l'oggetto di `docs/previsione_02_saturazione_direzionale.md`.
