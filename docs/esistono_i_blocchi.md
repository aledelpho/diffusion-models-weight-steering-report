# I "blocchi" esistono davvero? — misurato sui 28 blocchi singoli

**Data**: 2026-09-20 · **Domanda dell'utente**: «secondo te i blocchi esistono davvero? Quello che
potrebbe essere successo è che ho diviso in gruppi quando magari erano di più o divisi in modo
diverso.» · **Materiale**: 168 render, 28 blocchi singoli × 2 prompt × 3 seed, dose 0.200.

La domanda è empirica e il materiale per risponderle esiste già: se i gruppi sono reali, 28
blocchi misurati **uno per uno** devono raggrupparsi da soli, e i confini devono cadere dove sono
stati messi.

Ogni blocco è un **vettore di spostamento** nello spazio a 23 feature di stile, standardizzato
sui sei baseline. Due blocchi che "fanno la stessa cosa" hanno direzioni con coseno alto.

---

## 1. La contiguità è reale — questo sì

| | separazione mediana |
|---|--:|
| partizioni **contigue** in 6 gruppi (11 488 campioni) | **+0.139** |
| stesse dimensioni, etichette **mescolate** (non contigue) | **−0.006** |

L'85% delle partizioni contigue batte il 95° percentile di quelle non contigue.

E la somiglianza decade con la distanza lungo la rete:

| distanza fra indici | coseno medio |
|---:|--:|
| 1 (adiacenti) | **+0.321** |
| 2–3 | +0.109 |
| 4–7 | +0.089 |
| 8–15 | +0.017 |
| 16–27 | −0.058 |

Correlazione distanza ↔ coseno: r = −0.203, p = 7.2 × 10⁻⁵ su 378 coppie.

**Blocchi vicini fanno cose simili. Raggruppare per posizione non è arbitrario come idea.**

## 2. I confini scelti però non portano informazione

La partizione in uso — `0-4 | 5-9 | 10-14 | 15-19 | 20-23 | 24-27` — dà separazione **+0.1166**.

| confronto | esito |
|---|---|
| fra le 15 permutazioni delle **stesse dimensioni** (5,5,5,5,4,4) | **9ª su 15** |
| contro 11 488 partizioni contigue casuali | **31° percentile** — sotto la mediana |

Non è una partizione sbagliata in modo dannoso. È una partizione **indifferente**: una qualunque
altra divisione contigua farebbe altrettanto bene, e la metà farebbe meglio.

## 3. Dove il dato metterebbe i confini

Ricerca esaustiva sulla separazione massima:

| k | confini migliori | separazione | mediana casuale |
|--:|---|--:|--:|
| 2 | (15) | +0.160 | +0.097 |
| 3 | (10, 17) | +0.221 | +0.104 |
| 4 | (2, 10, 17) | +0.259 | +0.115 |
| 5 | (2, 7, 12, 17) | +0.274 | +0.127 |
| 6 | (2, 7, 12, 17, 26) | **+0.294** | +0.137 |

Due cose da notare, e una da non concludere.

**Il periodo coincide, la fase no.** I confini ottimali a k=6 sono 2, 7, 12, 17 — passo **cinque**,
esattamente come la partizione in uso (5, 10, 15, 20), ma **sfasati di tre**. Se c'è una struttura
ripetuta ogni cinque blocchi, la partizione attuale ne ha preso il periodo e mancato la fase, e i
suoi confini cadono **in mezzo** ai gruppi naturali invece che fra di essi.

**Non esiste un numero giusto di gruppi.** La separazione continua a crescere aggiungendo gruppi
(0.16 → 0.22 → 0.26 → 0.27 → 0.29) senza un ginocchio. Questo è il segno di un **gradiente con
correlazione locale**, non di moduli discreti: non ci sono sei parti, c'è una catena in cui ogni
anello somiglia al vicino e la somiglianza svanisce in tre o quattro passi.

**Da non concludere**: che i confini (2, 7, 12, 17, 26) siano *i* confini. Sono i migliori su una
dose sola, un segno solo, due scene. Il fatto che il guadagno rispetto al caso sia grande (0.29
contro 0.14) dice che la struttura c'è; la posizione esatta va rimisurata prima di crederci.

## 4. Cosa cambia per i risultati già ottenuti

**Non cambia niente di ciò che è stato misurato.** Ogni esperimento fatto a livello di gruppo ha
misurato esattamente ciò che ha manipolato: un insieme dichiarato di tensori. Quei numeri restano.

**Cambia come vanno enunciati.** «Block_5 agisce sul fumo» non è sostenuto. Sostenuto è: «i
blocchi 20–23 presi insieme agiscono sul fumo». La differenza non è pedanteria — la prima frase
attribuisce al modello una struttura in sei parti che il dato non mostra.

**E apre un sospetto sui risultati di composizione.** `Previsione 02` misurava l'angolo fra le
direzioni di due gruppi. Se un gruppo è un fascio arbitrario che mescola blocchi appartenenti a
famiglie naturali diverse, la sua direzione è una media su una popolazione mista, e l'angolo fra
due medie così è più sfocato dell'angolo fra due direzioni vere. Il confine naturale a 17 cade
**dentro** `Block_4` (15–19), che è uno dei due gruppi della coppia che ha fallito.

Questa è un'ipotesi, non una spiegazione: dice che l'esperimento andrebbe rifatto sui gruppi
derivati dal dato invece che su quelli in uso, e che se la regola dell'angolo si affila allora
l'arbitrarietà della suddivisione era parte del rumore. Se non cambia nulla, la regola è debole di
suo.

## 5. Limiti

Una sola dose (0.200), un solo segno (positivo), due scene, un modello. La struttura dei gruppi
potrebbe dipendere dalla dose — un blocco che a guadagno basso fa una cosa può farne un'altra a
guadagno alto, e la matrice dei coseni sarebbe diversa. Tutto il §3 va considerato una prima
mappatura, non una tassonomia.
