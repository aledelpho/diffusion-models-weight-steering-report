# Pre-registrazione — Rotazioni: Block_1 vs Block_6 nello Spazio Tessitura

**Data di congelamento**: 2026-09-18  
**Stato**: Congelato prima del lancio del campionamento su ComfyUI.  
**File di calibrazione allegato**: [`data/matched_rotation_calibration.json`](../data/matched_rotation_calibration.json)  
**Script di calibrazione**: [`experiments/calibrate_matched_rotation_angles.py`](../experiments/calibrate_matched_rotation_angles.py)  

---

## 1. Ipotesi Primaria (Unica, Senza Alternative)

Nello spazio di misura **Tessitura** (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy`), calcolato sulla componente antisimmetrica:
$$A_b(p) = \frac{1}{3} \sum_{s=1}^3 \frac{\Delta_{b, s}(+\theta_b) - \Delta_{b, s}(-\theta_b)}{2}$$
dove $\Delta_{b, s}(\theta) = \vec{f}_{b, s}(\theta) - \vec{f}_{\text{base}, s}$ è il vettore delle 3 feature di tessitura z-standardizzate rispetto alla distribuzione congiunta dell'esperimento, la direzione impressa da `Block_1` e `Block_6` è **statisticamente separabile e coerente**: il vantaggio stesso-blocco è positivo.

### Formula Registrata (Leave-One-Out Cross-Prompt)
Per ciascuno dei 10 prompt $p \in \{1 \dots 10\}$:
1. Si calcolano i centroidi leave-one-out sugli altri 9 prompt:
   $$\bar{A}_{1, -p} = \frac{1}{9} \sum_{q \neq p} A_1(q), \qquad \bar{A}_{6, -p} = \frac{1}{9} \sum_{q \neq p} A_6(q)$$
2. Si calcola il vantaggio stesso-blocco simmetrizzato per il prompt $p$:
   $$V(p) = \frac{1}{2} \left[ \Big(\cos(A_1(p), \bar{A}_{1, -p}) - \cos(A_1(p), \bar{A}_{6, -p})\Big) + \Big(\cos(A_6(p), \bar{A}_{6, -p}) - \cos(A_6(p), \bar{A}_{1, -p})\Big) \right]$$
3. Statistica del test: $\bar{V} = \frac{1}{10} \sum_{p=1}^{10} V(p)$.
4. **Test di significatività**: Test di permutazione esatta a scambio di segno (sign-flip test) sui 10 valori $V(p)$ a due code, $\alpha = 0.05$.  
   Pavimento teorico esatto: $2 / 2^{10} = 2 / 1024 = \mathbf{0.001953} \approx 0.00195$.

---

## 2. Spazio di Misura Primario e Stime Pilota

Lo spazio primario è formato da **3 feature di tessitura** estratte da `style_features.py`:
- `glcm_contrast` (contrasto matrice di co-occorrenza a scala fine)
- `glcm_homogeneity` (omogeneità locale)
- `lbp_entropy` (entropia dei Local Binary Patterns a raggio 1 e 2)

### Dichiarazione di Trasparenza Metodologica
La restrizione dalle 23 feature complessive alle 3 feature di tessitura viene dichiarata a priori basandosi sulle stime ottenute sul corpus pilota:
- Sulle **23 feature globali**: vantaggio stesso-blocco = **$+0.689$**, coerenza intra-blocco $0.65$ (`Block_1`) e $0.90$ (`Block_6`).
- Nel **sottospazio a 3 feature di tessitura**: l'effetto è più pulito e focalizzato sulla micro-grana, con vantaggio stesso-blocco = **$+0.798$**, e coerenze intra-blocco pari a **$0.85$** (`Block_1`) e **$0.93$** (`Block_6`).
- **Famiglie secondarie (esplorative, corrette Holm)**: Linework (3 feature), Shadow Hardness (2 feature), Frequenze spaziali (2 feature), Palette (6 feature LAB/C).

---

## 3. Calibrazione di $D$ Appaiato per Costruzione

Poiché $D$ scala come $2 \sin(\theta/2)$ e non linearmente con $\theta$, gli angoli sono stati risolti numericamente su `krea2_turbo_bf16.safetensors` per eguagliare $D_{\text{modello}} = 0.04500$:
- **`Block_1`**: $\theta_1 = \mathbf{23.69^\circ} \implies \|\Delta W\| = 225.4332, \quad D_{\text{modello}} = 0.045002$
- **`Block_6`**: $\theta_6 = \mathbf{32.21^\circ} \implies \|\Delta W\| = 225.4305, \quad D_{\text{modello}} = 0.045001$
- **Differenza residua**: $|D_1 - D_6| = \mathbf{0.0000006}$ (supera ampiamente il cancello $|D_1 - D_6| \le 0.0002$).

---

## 4. Doppio Braccio di Controllo a Segni Scambiati (`scramble_A` e `scramble_B`)

Per escludere che la separazione tra blocchi sia un artefatto dovuto al fatto che due perturbazioni casuali qualsiasi si separano nello spazio di misura, il disegno include **due controlli scramble indipendenti allo stesso identico $D$**:
- `scramble_A`: Rotazione casuale su `Block_1` a $\theta_1 = 23.69^\circ$ con segni Rademacher casuali per tensore (seed generator `20260919`): $\|\Delta W\| = 225.4316, D_{\text{modello}} = 0.045001$.
- `scramble_B`: Seconda realizzazione casuale indipendente con segni Rademacher (seed generator `20260920`): $\|\Delta W\| = 225.4334, D_{\text{modello}} = 0.045002$.

### Criterio Nullo di Falsificazione (What Would Kill It)
Sui due scramble viene calcolata la medesima statistica di vantaggio cross-leave-one-out:
$$V_{\text{scramble}}(p) = \frac{1}{2} \left[ \Big(\cos(A_{\text{scrA}}(p), \bar{A}_{\text{scrA}, -p}) - \cos(A_{\text{scrA}}(p), \bar{A}_{\text{scrB}, -p})\Big) + \Big(\cos(A_{\text{scrB}}(p), \bar{A}_{\text{scrB}, -p}) - \cos(A_{\text{scrB}}(p), \bar{A}_{\text{scrA}, -p})\Big) \right]$$
- **Condizione necessaria**: l'ipotesi di specificità anatomica/topografica è confermata solo se:
  $$\bar{V} > \bar{V}_{\text{scramble}}$$
  Se $\bar{V} \le \bar{V}_{\text{scramble}}$, l'effetto riflette la generica incoerenza tra perturbazioni arbitrarie e non una proprietà di posizione dei blocchi.

---

## 5. Matrice di Campionamento e Condizioni Operative

### I 10 Prompt di Stile (Stage 12)
1. `S01_oil`: Classic oil painting on textured canvas, visible impasto brushwork
2. `S02_linocut`: Bold linocut print, sharp relief carving, graphic ink lines
3. `S03_cyberpunk`: Neon cyberpunk digital art, glowing vibrant neon lights
4. `S04_gouache`: Opaque gouache illustration, matte finish, flat brushstrokes
5. `S05_pencil`: Detailed graphite pencil drawing, fine cross-hatching
6. `S06_pastel`: Soft chalk pastel drawing, powdery texture, smudged colors
7. `S07_comic`: Classic western comic book art, dynamic ink inking, halftones
8. `S08_papercraft`: Layered cut paper craft, 3D paper collage, tactile depth
9. `S09_fresco`: Ancient Renaissance fresco mural, weathered plaster texture
10. `S10_synthwave`: Retro 80s synthwave vector art, wireframe grid

> **Dichiarazione sull'Unità di Generalizzazione**: Il test generalizza su **10 regimi stilistici distinti** (ciascuno caratterizzato da una micro-tessitura fisica radicalmente diversa: pittura a olio, linoleografia, intonaco, matita, pastello, ecc.) su un soggetto controllato.

### Matrice delle 7 Condizioni per Cella
Per ciascuno dei 10 prompt e per ciascuno dei 3 seed (`42`, `1337`, `4242145`):
1. `baseline`: Modello stock pulito (0.0)
2. `Block_1_pos`: `Block_1` ruotato a $+23.69^\circ$
3. `Block_1_neg`: `Block_1` ruotato a $-23.69^\circ$
4. `Block_6_pos`: `Block_6` ruotato a $+32.21^\circ$
5. `Block_6_neg`: `Block_6` ruotato a $-32.21^\circ$
6. `scramble_A`: Controllo casuale A a $D = 0.04500$
7. `scramble_B`: Controllo casuale B a $D = 0.04500$

**Totale generazioni**: $10 \times 3 \times 7 = \mathbf{210 \text{ immagini}}$.  
- Campionatore: `euler_ancestral`, **9 passi**, CFG 1.0, risoluzione 1024 $\times$ 1760.

---

## 6. Cancelli di Accettazione

1. [x] Calibrazione offline verificata con $|D_1 - D_6| \le 0.0002$ (raggiunto $0.0000006$);
2. [ ] 210 task registrati correttamente nella coda di ComfyUI (`/queue`) prima dell'elaborazione;
3. [ ] 210 immagini estratte da `style_features.py` con zero fallimenti della maschera del soggetto;
4. [ ] Statistica primaria calcolata con la formula congelata al §1, senza deviazioni;
5. [ ] $p$-value riportato con il pavimento esatto $0.00195$;
6. [ ] Criterio nullo di falsificazione contro `scramble_A` vs `scramble_B` calcolato e riportato;
7. [ ] Risultato integrato in `docs/rotations_block1_vs_block6_results.md` prima di qualsiasi aggiornamento al README.
