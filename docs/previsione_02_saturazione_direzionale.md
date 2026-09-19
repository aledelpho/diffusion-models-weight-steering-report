# Previsione 02 — La saturazione dipende dall'angolo fra le modifiche

**Scritta il 2026-09-19, ore 23:50 (Europe/Rome), PRIMA di generare le immagini che la testano.**

---

## 1. La regola, e da dove viene

Da `docs/mappa_completa_sterzo_e_deriva.md` §3. Ogni condizione è un vettore di spostamento
nello spazio a 23 feature di stile, standardizzato sui sei baseline. Combinando due modifiche:

$$ \rho = \frac{\|\Delta(A{+}B)\|}{\|\Delta(A) + \Delta(B)\|} $$

Due punti misurati:

| coppia | cos(A,B) | ρ |
|---|--:|--:|
| B5 + B1 | −0.34 | 0.99 |
| B5 + B4 | +0.77 | 0.60 |

**Ipotesi**: ρ decresce al crescere di cos(A,B). Modifiche che puntano in direzioni diverse si
sommano; modifiche che puntano nella stessa direzione saturano lungo quella direzione.

**Questo è esplorativo.** Due punti non definiscono una legge, e la pendenza è stimata sulle
stesse due coppie che l'hanno suggerita. Serve materiale non usato per formularla.

## 2. Le previsioni

Condizioni: Krea-2, dose 0.200 su entrambi gli slot, tutti gli altri a 0, prompt `P01` e `P02`,
seed 42 / 777 / 1337. Baseline e condizioni singole già esistenti. **12 immagini nuove.**

| combinazione | cos(A,B) | ρ previsto | previsione dichiarata |
|---|--:|--:|---|
| **B2 + B6** | **−0.43** | ~1.02 | **ρ > 0.85** — si sommano |
| **B3 + B6** | **+0.80** | ~0.59 | **ρ < 0.70** — saturano |

La forma dichiarata è **a bande, non puntuale**: con due punti di taratura una previsione
puntuale sarebbe una precisione finta. Le bande sono separate da un intervallo vuoto di 0.15,
quindi una coppia non può soddisfarle entrambe.

**La previsione è confermata se entrambe le bande sono rispettate.** Se una sola lo è, è
smentita: il potere della regola sta nel distinguere i due casi, non nell'indovinarne uno.

### Controllo di realizzabilità (pitfall 56)

ρ è un rapporto di norme in uno spazio z non limitato. Non ha tetti né pavimenti vicini ai
valori previsti (0.59 e 1.02 su un dominio [0, ∞)). Le soglie 0.70 e 0.85 sono raggiungibili da
entrambi i lati. **Controllato prima di committare**, cosa che nella previsione 01 non era stata
fatta e aveva prodotto una previsione impossibile su `ombre`.

### Perché queste due coppie

Sono gli estremi disponibili del coseno fra coppie **non ancora combinate**: −0.43 è il più
negativo della matrice, +0.80 il più positivo. Entrambe coinvolgono `B6`, che ha lo spostamento
più grande (40.9) e quindi il rapporto meno sensibile al rumore. Nessuna delle due contiene
`B5`, che compare in entrambe le coppie usate per formulare la regola.

## 3. Cosa significherebbe una smentita

* **Se entrambe danno ρ alto**: la saturazione osservata su `B5+B4` non dipende dall'angolo ma
  è una proprietà di quella coppia specifica, e la regola cade.
* **Se entrambe danno ρ basso**: la saturazione è generale e `B5+B1` era l'eccezione — forse
  perché B1 è l'unico blocco che sterza davvero (§2 della mappa completa). La regola
  cambierebbe da «dipende dall'angolo» a «dipende dal fatto che uno dei due sterzi».
* **Se il verso è invertito**: la regola è sbagliata di segno, che sarebbe il risultato più
  informativo dei tre.

Le tre alternative portano a disegni successivi diversi, ed è per questo che il test vale 12
immagini.

## 4. Conseguenza pratica se la regola regge

Un preset è una combinazione di più guadagni. Se la saturazione dipende dall'angolo, allora la
progettazione di un preset ha una regola: **scegliere blocchi le cui direzioni di spostamento
siano fra loro poco allineate**, perché è lì che i contributi si sommano invece di sprecarsi.
La matrice dei coseni del §3 della mappa completa diventa lo strumento di progetto, e il preset
tarato a mano smette di essere l'unico modo.

Se invece cade, la taratura a mano resta l'unica via, e va detto.

---

# ESITO — aggiunto il 2026-09-20, ore 00:05, dopo la generazione

Le previsioni del §2 **non sono state modificate**. 12 immagini in `benchmark_previsione02`,
feature ri-estratte dalle immagini, stesso spazio a 23 feature e stessa standardizzazione sui
sei baseline usati per formulare la regola.

## Risultato: SMENTITA (1 banda su 2)

| coppia | cos(A,B) | ‖osservato‖ | ‖previsto‖ | ρ | banda | esito |
|---|--:|--:|--:|--:|---|---|
| **B2 + B6** | −0.43 | 40.37 | 39.83 | **1.013** | > 0.85 | **rispettata** |
| **B3 + B6** | +0.80 | 36.93 | 50.02 | **0.738** | < 0.70 | **violata** |

Il criterio dichiarato era che **entrambe** le bande reggessero. Una sola ha retto.

**La violazione non è rumore.** Calcolando ρ cella per cella: `B3B6` dà 0.740 ± 0.021 di errore
standard, con la soglia 0.70 a **1.95 errori standard** e **una sola cella su sei** sotto la
soglia (0.83, 0.71, 0.69, 0.75, 0.71, 0.75). La previsione era sbagliata, non sfortunata.

## Cosa è sopravvissuto e cosa no

**Il verso della relazione ha retto su entrambe le coppie nuove.** Tutti e quattro i punti
disponibili, ordinati per angolo:

| coppia | cos | ρ (media ± DS su 6 celle) |
|---|--:|--:|
| B2 + B6 | −0.43 | 1.007 ± 0.047 |
| B5 + B1 | −0.34 | 0.929 ± 0.135 |
| B5 + B4 | +0.77 | 0.687 ± 0.164 |
| B3 + B6 | +0.80 | 0.740 ± 0.051 |

L'ordinamento è monotono decrescente, r = −0.974. **Ma con n = 4 il test esatto sulle
permutazioni dà p = 0.125, contro un pavimento di 0.083: nemmeno un ordinamento perfetto
sarebbe significativo a questa numerosità.** La monotonia resta un'impressione, non un
risultato.

**La pendenza era sbagliata.** Tarata su due punti dava −0.351; sui quattro punti è **−0.282**,
e la retta diventa ρ ≈ 0.892 − 0.282·cos. La banda «< 0.70» derivava dalla pendenza troppo
ripida. Estrapolare una pendenza da due punti e poi usarla per fissare una soglia è il modo in
cui questa previsione ha fallito, e la forma a bande — pensata per evitare una precisione finta
— non è bastata perché le bande erano centrate sulla retta sbagliata.

## Enunciato che regge, e cosa serve per stabilirlo

Descrittivo, non dimostrato:

> Con angolo negativo fra le direzioni di spostamento, la composizione è **additiva entro il
> rumore** (ρ = 0.93 e 1.01). Con angolo sopra +0.75, si perde **circa il 30%** (ρ = 0.69 e 0.74).

Per trasformarlo in un risultato servono **almeno 8 coppie** che coprano l'intervallo del
coseno, compreso il vuoto fra −0.3 e +0.7 dove non esiste nessun punto — ed è proprio lì che si
deciderebbe se la relazione è una retta, una soglia o una curva. Le quattro coppie attuali
stanno tutte agli estremi e non possono distinguere fra le tre forme.

## Conseguenza operativa

Lo strumento di progetto del §4 sopravvive in forma qualitativa: **combinare blocchi con
direzioni poco allineate resta preferibile**, perché è dove i contributi si sommano. Ma non
esiste un fattore di correzione affidabile da applicare: chi volesse prevedere l'intensità di un
preset composto non può ancora farlo con questi numeri.

Il corpus sigillato `data/prompts_sealed_krea2.json` **resta chiuso**.
