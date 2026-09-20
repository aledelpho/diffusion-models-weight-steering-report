# La regola dell'angolo su nove coppie

**Data**: 2026-09-20 · **Materiale**: le 30 immagini di `benchmark_coppie_angolo` più le quattro
coppie già misurate. Nove coppie in tutto, dose 0.200, 2 prompt × 3 seed ciascuna.
**Verifica**: feature ri-estratte dalle immagini.

---

## 1. Esito

$\rho = \|\Delta(A{+}B)\| / \|\Delta(A) + \Delta(B)\|$ — 1.00 significa che due modifiche si
sommano esattamente, sotto 1 che si sprecano a vicenda.

| coppia | cos(A,B) | ρ | ES | origine |
|---|--:|--:|--:|---|
| B2+B6 | −0.43 | 1.007 | 0.019 | previsione 02 |
| B5+B1 | −0.34 | 0.929 | 0.055 | previsione 01 |
| **B1+B4** | −0.14 | **1.167** | 0.058 | nuova |
| B5+B6 | +0.16 | 0.980 | 0.015 | nuova |
| B3+B5 | +0.20 | 0.794 | 0.086 | nuova |
| B1+B2 | +0.56 | 0.864 | 0.033 | nuova |
| B4+B6 | +0.64 | 0.662 | 0.052 | nuova |
| B5+B4 | +0.77 | 0.687 | 0.067 | previsione 01 |
| B3+B6 | +0.80 | 0.740 | 0.021 | previsione 02 |

**Pearson r = −0.791, p = 0.011 · Spearman ρ = −0.833, p = 0.0053 (n = 9).**

Nessun punto regge la relazione da solo: escludendone uno alla volta, `r` resta fra −0.749 e
−0.831 e `p` fra 0.011 e 0.033. La pendenza stimata varia fra −0.228 e −0.327.

## 2. La pendenza si è replicata

| | retta |
|---|---|
| su 4 coppie (previsione 02, formulata al buio) | ρ = 0.892 − 0.282·cos |
| su 9 coppie | **ρ = 0.939 − 0.278·cos** |

La pendenza stimata su quattro punti — che avevo dichiarato inaffidabile — **è sopravvissuta
all'aggiunta di cinque coppie indipendenti**, cambiando di 0.004. L'intercetta è salita di 0.047.

## 3. Rilettura della previsione 02

La previsione 02 fu registrata come **smentita** perché chiedeva ρ > 0.85 per `B2B6` (rispettata,
1.007) e ρ < 0.70 per `B3B6` (violata, 0.740). Con la retta a nove punti:

| coppia | previsto dalla retta | osservato | scarto |
|---|--:|--:|--:|
| B2B6 | 1.058 | 1.007 | −0.051 |
| B3B6 | 0.716 | 0.740 | +0.024 |

**La relazione prevedeva `B3B6` a 0.716; è uscito 0.740.** L'errore stava nella **banda**, non
nella regola: avevo tradotto la retta in una soglia di 0.70 quando la retta stessa diceva 0.716,
lasciando 0.016 di margine su una grandezza con errore standard 0.021. Una soglia più stretta
dell'incertezza della previsione che la genera non è un test severo: è un sorteggio.

**Il verdetto di smentita resta agli atti e non va riscritto.** Quel che si aggiunge è la
diagnosi: la previsione fallì per come era stata tradotta in criterio, non per ciò che affermava.
Vedi pitfall 61.

## 4. Un fenomeno nuovo: super-additività

`B1+B4` dà **ρ = 1.167 ± 0.058**, cioè 2.9 errori standard **sopra** 1.00: le due modifiche
insieme spostano l'immagine **più** della somma dei loro effetti separati.

Non era previsto da niente. Con un punto solo non è un risultato — ma è l'unica coppia a cosine
lievemente negativo fra le nove, e se la super-additività fosse sistematica a quegli angoli la
retta sarebbe la corda di una curva. Serve almeno una seconda coppia fra cos −0.2 e 0.0 prima di
dirne qualcosa.

## 5. Limite che vale per tutto il documento

Tutte e nove le coppie sono a **dose 0.200**, che `docs/audit_metodologico_2026-09-20.md`
identifica come un regime dove metà dei blocchi giace al 73–99% sull'asse comune del degrado, e
dove i coseni fra blocchi correlano solo r = +0.42 con quelli a dose 0.050.

La relazione è quindi stabilita **fra spostamenti in regime degradato**. Che sia una proprietà
generale della composizione, o dell'interazione fra due contributi di grana, lo decide la replica
a dose bassa (punto 6 di `BRIEF_20sett_coda_lunga.md`).
