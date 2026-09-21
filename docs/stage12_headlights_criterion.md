# Criterio di scoring fari — stage 12, congelato prima di aprire qualunque immagine
Depositato: 2026-09-21. Annotatore: Claude (mai esposto a queste immagini).
Chiave NON consultata: `data/stage12_bbox_key.csv` resta chiusa finche' i punteggi non sono scritti.

## Categorie
- **ACCESO**: almeno un faro appare come regione distintamente PIU' CHIARA del pannello di
  carrozzeria adiacente, con alone/bagliore o gradino di luminanza netto.
- **SPENTO**: la zona dei fari e' visibile ma non piu' chiara dell'intorno (vetro scuro, cromatura
  riflettente senza bagliore).
- **INCERTO**: fari non visibili (vista posteriore, occlusi, troppo piccoli) oppure luminanza ambigua.

## Vincoli dichiarati prima
- Giudizio di **sola luminanza**. La tinta e' ruotata fino a +/-178 gradi dai disturbi, quindi
  qualunque criterio cromatico e' inutilizzabile e non viene usato.
- Le immagini possono essere specchiate e capovolte: l'orientamento non entra nel giudizio.
- Ogni immagine e' ritagliata sul proprio bounding box annotato e riscalata a dimensione comune,
  cosi' la GRANDEZZA DEL SOGGETTO - che e' l'ipotesi 1 e correla con la condizione - non e'
  disponibile come indizio.
- Nessuna immagine viene rivista dopo aver visto le successive. Un passaggio solo.
- Il tasso di INCERTO viene riportato, non redistribuito.

## Deviazioni dalla pre-registrazione, dichiarate
1. La passata fari doveva precedere quella bbox con rimescolamento indipendente: l'ordine e'
   invertito e il rimescolamento e' lo stesso.
2. "Non si riusa nessuna chiave esistente": la cecita' riusata e' quella della tornata bbox.
3. L'annotatore non e' quello pre-registrato e conosce l'ipotesi.
   Mitigazione: file a nome-hash, chiave aperta solo a punteggi congelati.
4. `preset_pos_1x` non e' fra le immagini cieche: l'ipotesi 2 non lo richiede
   (nessun ordinamento di dose), ma la gradazione non sara' misurabile.

## PRECISAZIONE, dopo i primi 27 tile e PRIMA di aprire la chiave
La clausola ACCESO "alone/bagliore **oppure** gradino di luminanza netto" e' troppo lasca: una
lente passiva e' quasi sempre piu' chiara della carrozzeria, e la definizione di SPENTO si
contraddiceva citando la cromatura riflettente come SPENTO pur essendo piu' chiara.

**Lettura vincolante da qui in avanti, e applicata retroattivamente ai tile 001-027:**
ACCESO richiede **evidenza di emissione** — bagliore che deborda oltre il contorno del fanale,
oppure il fanale e' fra le regioni piu' luminose del ritaglio, piu' del riflesso speculare sulla
carrozzeria. Una lente chiara, un cerchio cromato o un riflesso senza spill sono SPENTO.

Dichiarato: 27 tile sono stati visti prima che la precisazione fosse scritta. La precisazione
e' un inasprimento simmetrico rispetto alle condizioni (la chiave resta chiusa), ma i risultati
saranno riportati anche escludendo quei 27.
