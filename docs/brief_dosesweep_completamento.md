# BRIEF — Completare la sweep di dose su Anima: 30 immagini

**Esecutore**: Antigravity, pilotando ComfyUI.
**Cartella esistente**: `benchmark_anima_dosesweep\renders` — 56 immagini già generate, tutte
valide, nessuna da rifare.
**Da aggiungere**: **30 immagini**, in due gruppi indipendenti.

---

## 1. Cosa ha detto la sweep finora

Le 56 immagini sono state analizzate. Due risultati e un buco.

**Nessuna immagine collassa**, nemmeno a dose 30: tutte passano le quattro soglie del cancello
(`edge_density` > 0.02, `glcm_contrast` > 2.0, `color_n_effective` > 2.5,
`contour_n_components` > 50). Ma i margini si chiudono in modo regolare:

| condizione | `glcm_contrast` min | `edge_density` min |
|---|---:|---:|
| baseline | 9.26 | 0.059 |
| preset 10 | 8.67 | 0.057 |
| preset 15 | 6.28 | 0.045 |
| preset 20 | 4.89 | 0.041 |
| preset 30 | **3.36** | **0.027** |
| *soglia* | *2.0* | *0.02* |

Estrapolando, il cancello si chiude intorno a **dose 40–45**. Non è verificato: è una retta
tirata su quattro punti.

**Il buco: un solo seed.** La pre-registrazione (`docs/prereg_stage2_corpus_nativo.md` §5)
sceglie la dose come la più piccola che produce uno spostamento $\ge 3\sigma_{\text{seed}}$
senza collasso. Con un solo seed $\sigma_{\text{seed}}$ non è calcolabile, quindi il criterio
non è applicabile e la dose non è decidibile.

Stimando $\sigma_{\text{seed}}$ dai 50 baseline dello stage 1 — stesso modello ma **corpus
diverso**, quindi ordine di grandezza e non il numero giusto — viene $\sigma \approx 1.98$, e
lo spostamento misurato è 1.19 / 1.69 / 2.00 / 2.92 alle dosi 10 / 15 / 20 / 30: da 0.60σ a
1.47σ. **Nessuna dose provata arriva vicino a 3σ**, e per estrapolazione servirebbe dose ~60
— oltre il punto in cui il cancello si chiude. Le due condizioni della pre-registrazione
potrebbero quindi essere **reciprocamente insoddisfacibili** su questo modello.

Le due aggiunte servono a decidere questo con numeri misurati invece che estrapolati.

---

## 2. Aggiunta A — baseline a due seed in più (14 immagini)

**Lo scopo**: misurare $\sigma_{\text{seed}}$ **sul corpus giusto**, invece di importarlo da
un altro. È il metro senza il quale nessuno dei numeri della sweep ha una scala.

| | |
|---|---|
| prompt | tutti e 7, `P01` … `P07` |
| condizione | **solo `baseline`** |
| seed | **777** e **1337** |
| immagini | 7 × 2 = **14** |

**Vincolo assoluto**: impostazioni **identiche** ai baseline già presenti — stesso checkpoint,
stessi passi, stesso CFG, stesso sampler, stesso scheduler, stessa risoluzione. Se anche un
solo parametro cambia, la variazione fra seed si mescola alla variazione fra impostazioni e
$\sigma_{\text{seed}}$ misura due cose insieme. Nel dubbio, ricaricare il workflow che ha
prodotto i 56 render invece di ricostruirlo.

Nomi file, **esattamente** nella forma già in uso:

```
P01_elf_brawler_baseline_seed777_00001_.png
P01_elf_brawler_baseline_seed1337_00001_.png
...
P07_<tag>_baseline_seed1337_00001_.png
```

Il `<tag>` è quello che ciascun prompt ha già nei file esistenti: non inventarlo, copiarlo.

## 3. Aggiunta B — estendere la dose verso l'alto (16 immagini)

**Lo scopo**: trovare **dove il cancello si chiude davvero**, invece di dedurlo da una retta
su quattro punti.

| | |
|---|---|
| prompt | **`P03`** e **`P06`** |
| condizione | **solo `preset`** |
| dosi | **40**, **50**, **60**, **80** |
| seed | **42** e **777** |
| immagini | 2 × 4 × 2 = **16** |

I due prompt non sono scelti a caso: nella sweep esistente `P06` è il più reattivo
(spostamento da 0.64 a 4.30 fra dose 10 e 30) e `P03` il meno (da 0.68 a 1.31). Insieme
racchiudono l'intervallo di risposta del corpus, quindi la dose di rottura trovata su questi
due è un intervallo, non un punto singolo di dubbia generalità.

Nomi file nella stessa forma:

```
P03_orc_wizard_preset_40_seed42_00001_.png
P06_<tag>_preset_80_seed777_00001_.png
```

**Non fermarsi al primo collasso.** Se dose 50 produce un campo uniforme, generare comunque
60 e 80: serve sapere se il collasso è una soglia netta o una degradazione progressiva, e
sono due comportamenti diversi. Le immagini collassate **non vanno scartate**: sono il dato.

**Servono i preset a quelle dosi.** Se non esistono già, si producono con lo stesso comando
che ha prodotto quelli a 10/15/20/30, cambiando solo il fattore di scala. Se il metodo usato
è stato un `--match-d` con il valore moltiplicato, usare lo stesso e annotare il
`achieved_D_model` risultante — serve per la tabella finale.

---

## 4. Cosa NON fare

* **Non rigenerare le 56 immagini esistenti.** Sono valide e servono come sono.
* **Non cambiare prompt, risoluzione, sampler, scheduler, passi o CFG** rispetto alla sweep
  esistente. L'intero esercizio è un confronto appaiato: cambiare un parametro lo annulla.
* **Non scartare immagini degradate o collassate.**
* **Non aggiungere condizioni** oltre a quelle elencate. `blockshuf_neg` e `randsign` alle
  dosi alte sono una domanda successiva e separata; qui si cerca solo il tetto del preset.
* **Non rinominare i file esistenti.**

## 5. Cosa succede dopo

Con l'aggiunta A, $\sigma_{\text{seed}}$ diventa misurato e il criterio della
pre-registrazione diventa applicabile o dimostrabilmente inapplicabile. Con l'aggiunta B, il
tetto del cancello diventa misurato invece che estrapolato.

Se i due intervalli non si sovrappongono — cioè se la dose che raggiunge $3\sigma$ è sopra la
dose che rompe la generazione — **la pre-registrazione va emendata prima di generare il corpus
dello stage 2**, e l'emendamento va scritto e datato prima di guardare altri dati. Le due
opzioni sono già sul tavolo: abbassare la soglia a un multiplo più basso di $\sigma$,
motivandolo con il fatto che la statistica aggrega su 50 immagini e non su una; oppure
dichiarare che il disegno poggia sull'aggregazione e non sulla dimensione dell'effetto per
immagine, e togliere del tutto il criterio in $\sigma$.

In entrambi i casi il fatto che la finestra sia stretta o vuota **è un risultato sulla
portabilità del metodo**, non un fallimento della calibrazione, e va registrato come tale.
