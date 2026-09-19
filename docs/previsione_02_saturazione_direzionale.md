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
