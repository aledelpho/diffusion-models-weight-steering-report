# Monotonia con la profondità — ESITO: smentita, ed è un gradino

**Data**: 2026-09-20 · **Materiale**: 168 render (`benchmark_profondita`), 28 blocchi singoli ×
2 prompt sonda × 3 seed, dose 0.200, baseline riusati da `benchmark_mappa`.
**Verifica**: coerenza ri-calcolata dalle immagini, senza riusare i numeri dell'esecutore.

---

## 1. L'ipotesi sotto test

Da `docs/coerenza_traiettoria.md` §5: un blocco iniziale altera la previsione del modello e
l'errore si propaga attraverso i venti e più blocchi successivi, spostando la traiettoria; un
blocco finale agisce vicino all'uscita e non viene rielaborato.

**Previsione dichiarata**: la coerenza di traiettoria cresce **monotonamente** con l'indice del
blocco. Dichiarato anche il criterio di lettura: *«Curva liscia e crescente → l'ipotesi regge e
si ha un meccanismo. Gradino o picco isolato → l'ipotesi cade, e il blocco che sporge fa qualcosa
di specifico, che è un risultato più interessante.»*

## 2. Esito: SMENTITA

| test | risultato |
|---|---|
| correlazione indice ↔ coerenza, tutti e 28 | r = +0.577, p = 0.0013 · Spearman ρ = +0.420, p = 0.026 |
| **correlazione sui soli blocchi 0–19** | **r = −0.331, p = 0.154** — nessuna salita |
| passi consecutivi in salita | 16 su 27 (per caso: 13.5) |
| retta contro gradino, somma dei quadrati residui | retta 0.01573 · **gradino 0.00561** |
| punto di rottura migliore | **blocco 23** |

**Attraverso i primi venti blocchi la coerenza non sale affatto**: resta fra 0.072 e 0.118 con una
pendenza leggermente *negativa*. Tutto l'effetto è un gradino verso la fine, e un modello a
gradino descrive i 28 punti **2.8 volte meglio** di una retta.

La correlazione complessiva positiva, presa da sola, avrebbe fatto sembrare l'ipotesi confermata.
È il gradino a produrla, non una crescita.

## 3. Il gradino però è reale

Media dei blocchi 0–19 = **0.091**; media dei blocchi 20–27 = **0.139**. Differenza appaiata sulle
sei celle prompt × seed: **+0.0473**, dello stesso segno in tutte e sei, test dei segni esatto
**p = 0.031**.

| blocco | coerenza ± ES | \|diff\| |
|---:|--:|--:|
| 0 | 0.081 ± 0.018 | 0.1370 |
| 10 | 0.072 ± 0.009 | 0.1442 |
| 16 | 0.072 ± 0.008 | 0.1460 |
| 20 | 0.093 ± 0.011 | 0.1227 |
| 23 | 0.138 ± 0.020 | 0.1060 |
| 24 | 0.165 ± 0.027 | 0.1024 |
| **26** | **0.187 ± 0.026** | 0.1403 |
| 27 | 0.163 ± 0.022 | 0.1492 |

Il punto di rottura cade al blocco **23**, che è l'*ultimo* di `Block_5` (20–23), non al confine
fra `Block_5` e `Block_6`. Vicino al confine dei gruppi ma non coincidente: la soglia è una
proprietà dei blocchi, non della suddivisione scelta.

## 4. Cosa muore e cosa resta

**Muore il meccanismo come formulato.** Se l'errore si accumulasse propagandosi attraverso i
blocchi successivi, il blocco 5 dovrebbe conservare più del blocco 0, e il 15 più del 5. Non
succede: fino al blocco 19 non c'è alcun ordine. La profondità, di per sé, non spiega niente.

**Resta un risultato più stretto**: gli ultimi cinque blocchi (23–27) fanno qualcosa di specifico
che gli altri ventitré non fanno. Non è «essere profondi», è «essere quei blocchi».

**E resta il dato pratico**, che è quello che serve al caso d'uso reale. Il blocco **26** sposta
il contenuto quanto il blocco 0 (\|diff\| 0.140 contro 0.137) conservando **2.3 volte** più
traiettoria originale (0.187 contro 0.081). Per correggere un'immagine senza perderla, i blocchi
26 e 27 sono le manopole migliori misurate finora, e la ragione non è la profondità.

## 5. Dipendenza dal prompt, dichiarata

La relazione non è ugualmente forte sulle due scene: su `P02` Spearman ρ = +0.57 … +0.64 con
p ≤ 0.0016 in tutti e tre i seed; su `P01` ρ = +0.28 … +0.30 con p ≈ 0.12–0.15, non
significativa. Il test sul gradino (§3) è appaiato sulle sei celle ed è 6/6, quindi più robusto
della correlazione presa cella per cella — ma la differenza fra le due scene va registrata e non
spiegata a posteriori.

## 6. Accordo con il calcolo indipendente dell'esecutore

`docs/report_monotonia_profondita.md` riporta Spearman +0.457 contro il +0.420 calcolato qui, e
valori di coerenza più alti del 5–10% (blocco 26: 0.210 contro 0.187). La differenza è compatibile
con una maschera delle zone piatte o una sfocatura leggermente diverse. **L'ordinamento, il punto
di rottura e la conclusione qualitativa coincidono**, e l'esecutore era arrivato allo stesso
verdetto in autonomia.
