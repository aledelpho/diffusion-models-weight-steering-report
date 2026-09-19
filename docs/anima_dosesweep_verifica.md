# Anima — sweep di dose: verifica indipendente e verdetto sulla pre-registrazione

**Data**: 2026-09-19 · **Materiale**: 116 render (`benchmark_anima_dosesweep/renders`), 2 render
di controllo (`test_identity`) · **Metodo**: ri-estrazione completa delle feature e ricalcolo
da zero, senza riusare i numeri del report dell'esecutore.

---

## 0. Controllo positivo: il tuner a guadagno zero è identità

`pure_baseline` (nodo assente) e `tuner_zero` (nodo presente, tutti i guadagni a 0), stesso
seed: **identici bit per bit**, differenza massima di canale 0 su 1280 × 1024 × 3.

Il tuner legge, scala e riscrive 1059 tensori; a guadagno zero compie comunque un giro
bf16 → fp32 → bf16. Se quel giro non fosse esattamente identità aggiungerebbe un pavimento
a **ogni** spostamento misurato nel progetto, identico nel trattamento e nei due controlli a
norma appaiata, quindi invisibile in ogni contrasto e cancellato in ogni p-value, ma capace
di gonfiare tutte le dimensioni d'effetto assolute. Non è il caso. Vedi pitfall 54.

## 1. Spazio di misura

La pre-registrazione §5 fissa cinque feature: `glcm_contrast`, `glcm_homogeneity`,
`lbp_entropy`, `edge_density`, `crosshatch_entropy_mean`. Non specifica **su quale insieme**
si z-standardizza, che è un'ambiguità reale. Sono state calcolate entrambe le letture:

| standardizzazione | σ_seed | spostamento dose 10 | dose 50 in σ |
|---|--:|--:|--:|
| solo i 21 baseline | 1.407 | 1.632 | 3.88σ |
| tutte le 116 immagini | 0.943 | 1.070 | 3.62σ |

Il rapporto è quasi invariante: **la conclusione non dipende dalla scelta**. Nel seguito si usa
la prima. σ_seed è la distanza media fra baseline dello stesso prompt a seed diversi
(21 coppie: 7 prompt × 3 seed), DS 0.659, intervallo 0.50–2.90.

Questo **conferma** i due numeri chiave riportati dall'esecutore (σ = 1.407, spostamento 1.63
a dose 10) e **smentisce** la stima precedente di chi scrive (σ ≈ 1.98, spostamento 1.19),
che era estrapolata dai baseline dello stage 1 — corpus diverso, stima non portabile.

## 2. I due criteri della pre-registrazione, misurati

| dose | n | spostamento | in σ | ≥ 3σ | immagini che falliscono il cancello |
|---:|--:|--:|--:|:--:|--:|
| 10 | 7 | 1.632 | 1.16σ | no | 0/7 |
| 15 | 7 | 2.237 | 1.59σ | no | 0/7 |
| 20 | 7 | 2.756 | 1.96σ | no | 0/7 |
| 30 | 7 | 3.852 | 2.74σ | no | 0/7 |
| 40 | 14 | 4.812 | 3.42σ | **sì** | **3/14** |
| 50 | 14 | 5.466 | 3.88σ | **sì** | **2/14** |
| 60 | 14 | 5.935 | 4.22σ | **sì** | **3/14** |
| 80 | 4 | 7.423 | 5.27σ | **sì** | **3/4** |

Controlli, a dose appaiata: `blockshuf_neg` 15 → 1.45σ, 20 → 1.31σ; `randsign` 15 → 1.21σ.

**La dose più piccola che raggiunge 3σ è 40, e 40 fallisce già il cancello.** La
pre-registrazione chiede il cancello superato da *tutte* le immagini: **nessuna dose provata
soddisfa entrambi i criteri. La finestra è vuota.**

I fallimenti non sono rumore. Sono quasi tutti un prompt solo:

| prompt | 40 | 50 | 60 | 80 |
|---|:--:|:--:|:--:|:--:|
| P01–P04 | 2/2 | 2/2 | 2/2 | 1/2 (P03) |
| P05 | 2/2 | 2/2 | **1/2** | — |
| P06 | **1/2** | 2/2 | 2/2 | **0/2** |
| P07 | **0/2** | **0/2** | **0/2** | — |

`P07` sfonda `edge_density` a ogni dose da 40 in su, su entrambi i seed.

## 3. Perché il cancello non sta misurando quello che dovrebbe

A dose alta Anima allarga il campo: la frazione di pixel quasi-bianchi di `P07` passa da 0.50
(baseline) a 0.68 (dose 40), e la crescita del bianco correla −0.55 con la perdita di bordi.
Un'inquadratura più larga abbassa `edge_density` senza che il tratto peggiori.

Non è la spiegazione. Misurando `edge_density` **solo dentro il soggetto** (maschera del
non-bianco, chiusura morfologica 9 × 9), la frazione di bordi conservata rispetto al proprio
baseline è:

| prompt | base | 20 | 30 | 40 | 50 | 60 |
|---|--:|--:|--:|--:|--:|--:|
| P01 | 0.1881 | 0.80 | 0.76 | 0.63 | 0.35 | 0.32 |
| P02 | 0.1652 | 0.97 | 0.66 | 0.45 | 0.45 | 0.40 |
| P03 | 0.1524 | 0.97 | 1.12 | 0.85 | 0.68 | 0.60 |
| P04 | 0.2250 | 1.00 | 0.81 | 0.59 | 0.53 | 0.55 |
| P05 | 0.0961 | 0.88 | 0.93 | 0.60 | 0.57 | 0.43 |
| P06 | 0.1626 | 0.91 | 0.43 | 0.41 | 0.55 | 0.63 |
| P07 | 0.1371 | 0.78 | 0.57 | 0.31 | 0.26 | 0.19 |

Il degrado di `P07` è reale — conserva il 26% del proprio tratto a dose 50 — ma **non è
isolato**: a dose 50 tutti e sette i prompt hanno perso fra il 32% e il 74% del tratto dentro
il soggetto. È esattamente il collasso che il cancello esiste per intercettare, e il cancello
ne segnala 2 su 14, perché è un **pavimento assoluto** e l'`edge_density` di baseline varia
2.3× fra prompt (0.059 su `P05`, 0.133 su `P01`). Passa chi partiva alto. Vedi pitfall 51.

Il cancello va riespresso **in rapporto al baseline del proprio prompt**, con il pavimento
assoluto conservato solo come guardia secondaria contro un fotogramma vuoto.

## 4. Il risultato sostanziale: preset contro controlli a D appaiato

Test di permutazione esatto per inversione di segno sulle differenze per prompt, seed 42,
n = 7, pavimento 2/2⁷ = 0.0156.

| confronto | preset | controllo | differenza media | p esatto |
|---|--:|--:|--:|--:|
| preset 15 vs `blockshuf_neg` 15 | 2.24σ | 2.04σ | +0.20 | 0.766 |
| preset 20 vs `blockshuf_neg` 20 | 2.76σ | 1.85σ | +0.91 | **0.078** |
| preset 15 vs `randsign` 15 | 2.24σ | 1.70σ | +0.54 | 0.406 |

**Correzione (2026-09-19, dopo il calcolo di potenza).** La prima stesura diceva «la
significatività era raggiungibile e non è raggiunta». È formalmente vero e sostanzialmente
fuorviante. Con l'effetto e la dispersione misurati a dose 20 (differenza media +0.909, DS 1.262
fra prompt, $d$ di Cohen 0.72), la potenza del test dei segni esatto a $n = 7$ e $\alpha = 0.05$
è **0.34**. La non-significatività era l'esito più probabile *anche se l'effetto è reale della
dimensione osservata*. Il pilota non ha fallito: non era dimensionato per decidere.

Quel che resta dicibile: **sul corpus nativo di Anima, alle dosi che non distruggono l'immagine,
non c'è prova che il preset strutturato si distingua da una permutazione a norma appaiata.** È
un'assenza di prova, non una prova di assenza, e il disegno del pilota non consentiva altro.

Potenza attesa per lo stage 2, stesso effetto, test dei segni esatto:

| n prompt | 1 seed/prompt | 5 seed/prompt |
|---:|--:|--:|
| 7 | 0.34 | — |
| 10 | 0.51 | 0.65 |
| 12 | 0.62 | 0.75 |

## 5. Conseguenze per la pre-registrazione

La finestra vuota **non è un fallimento di calibrazione**: è una misura sulla portabilità del
metodo, e va registrata come risultato. Ma il criterio §5 va emendato prima di generare il
corpus dello stage 2, e l'emendamento va datato.

La ragione tecnica per abbassarlo è quantitativa, non di comodo. σ_seed è la dispersione **per
immagine**; il disegno dello stage 2 aggrega su 50 immagini per condizione, dove l'errore
standard della media è σ/√50 ≈ 0.20. Uno spostamento di 2σ per immagine è ~14σ sulla media
aggregata. Il criterio "3σ per immagine" è molto più severo di quanto il test statistico
richieda, ed è stato scritto senza questo conto davanti.

Tre opzioni, da decidere e datare prima di guardare altri dati:

1. **Abbassare la soglia a 2σ per immagine** e fissare la dose a 20 (1.96σ misurati, 0/7
   fallimenti, ≥ 78% del tratto conservato su tutti i prompt). Motivazione scritta: il test
   poggia sull'aggregazione, non sulla dimensione d'effetto per immagine.
2. **Togliere il criterio in σ** e dichiarare che la dose si sceglie come la massima che
   conserva ≥ 80% del tratto su tutti i prompt — di nuovo dose 20.
3. **Riespressione del cancello in relativo** (§3) e mantenimento di 3σ: porterebbe a dose 40,
   dove però `P07` conserva il 31% e `P06` il 41% del tratto. Sconsigliata: passerebbe il
   cancello riformulato solo con una soglia relativa permissiva, e i render sono visibilmente
   piatti.

Le opzioni 1 e 2 convergono su **dose 20**. È la scelta che chi scrive raccomanda, con la nota
esplicita che a dose 20 il preset **non** si separa dai controlli (§4), e che quindi lo stage 2
su Anima va lanciato sapendo che il suo esito più probabile è un risultato nullo — il che è
informativo sulla portabilità e vale la generazione, ma non va scambiato per un test
confermativo.
