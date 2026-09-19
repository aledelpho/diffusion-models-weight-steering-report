# Ricette di Riproducibilità — Esperimento Rotazioni Block_1 vs Block_6

Questa guida contiene tutte le **ricette complete e deterministiche** per rigenerare da zero qualsiasi immagine (o l'intero lotto di 210 render) dell'esperimento di rotazione ortogonale appaiata tra `Block_1` e `Block_6`.

---

## 1. Modelli e Checkpoint Richiesti

| Ruolo | File Checkpoint | Percorso Standard ComfyUI |
| :--- | :--- | :--- |
| **Diffusion Model** | `krea2_turbo_bf16.safetensors` | `models/diffusion_models/` (oppure `models/unet/`) |
| **Text Encoder** | `qwen3vl_4b_bf16.safetensors` | `models/clip/` |
| **VAE** | `qwen_image_vae.safetensors` | `models/vae/` |

---

## 2. Parametri Globali del Campionatore

Tutti i 210 render utilizzano le medesime impostazioni operative congelate nella pre-registrazione:

* **Sampler**: `euler_ancestral`
* **Scheduler**: `simple`
* **Passi (Steps)**: `9`
* **CFG Scale**: `1.0`
* **Denoise**: `1.0`
* **Risoluzione Immagine (Latent)**: `1024 x 1280` (EmptyLatentImage batch size 1)
* **Visualizer HUD**: nodo `ArthemyKrea2ModelVisualizer` (`scale = 5.0`, altezza HUD = `480 px`), cucito verticalmente con `ArthemyImageStitcher` (risoluzione file PNG finale: `1024 x 1760`).

---

## 3. La Matrice dei 3 Seed

Per ciascuno stile vengono testati 3 seed controllati:
1. `42`
2. `1337`
3. `4242145`

---

## 4. Ricetta dei Prompt: I 10 Stili e il Soggetto Fisso

Ciascun prompt è composto da `Style: [stile di resa]. Subject: [soggetto comune controllato]`.

**Soggetto comune controllato**:
> *"a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky."*

### I 10 Stili Stilistici (`S01` .. `S10`)

1. **`S01_oil` (Miglior vantaggio LOO, $V(p) = +1.1695$)**:
   ```text
   Style: classic oil painting on textured canvas, visible impasto brushwork, rich blending, fine art realism. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
2. **`S02_linocut`**:
   ```text
   Style: bold linocut print, sharp relief carving, graphic ink lines, high contrast black and white with select spot colors, hand-printed woodblock texture. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
3. **`S03_cyberpunk`**:
   ```text
   Style: neon cyberpunk digital art, glowing vibrant neon lights, dark moody reflections, futuristic atmosphere, sharp cinematic detail. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
4. **`S04_gouache`**:
   ```text
   Style: opaque gouache illustration, matte finish, flat brushstrokes, vibrant saturated palette, editorial poster design. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
5. **`S05_pencil`**:
   ```text
   Style: detailed graphite pencil drawing, fine cross-hatching, realistic paper grain texture, expressive monochrome sketch. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
6. **`S06_pastel`**:
   ```text
   Style: soft chalk pastel drawing, powdery texture, smudged colors, impressionistic light, artistic grain on dark paper. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
7. **`S07_comic`**:
   ```text
   Style: classic western comic book art, dynamic ink inking, bold black outlines, screentone shading, vintage retro comic printing. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
8. **`S08_papercraft`**:
   ```text
   Style: layered cut paper craft, 3D paper collage, visible edges, soft physical shadows, tactile depth, minimalist clean shapes. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
9. **`S09_fresco`**:
   ```text
   Style: ancient Renaissance fresco mural, weathered plaster texture, cracked mineral pigments, classical painted surface, historical patination. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
   ```
10. **`S10_synthwave` (Minor vantaggio LOO, $V(p) = +0.7282$)**:
    ```text
    Style: retro 80s synthwave vector art, glowing neon wireframe grid, purple and cyan sunset gradient, vintage chrome reflections, nostalgic aesthetic. Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.
    ```

---

## 5. Le 7 Condizioni Sperimentali e i Parametri dei Nodi

Per ciascuna cella (Stile $\times$ Seed), il modello pulito passa attraverso il nodo di reset `ArthemyKrea2ResetPatcher` e riceve uno dei 7 trattamenti:

### 1. `baseline` (Controllo Invariato)
* Nodo: `ArthemyKrea2ModelRotator`
* `target_block`: `"Block_1 (All 0-4)"`
* `structural_rot_x`: `0.0`
* $D_{\text{modello}} = 0.0$

### 2. `Block_1_pos` (+23.69°)
* Nodo: `ArthemyKrea2ModelRotator`
* `target_block`: `"Block_1 (All 0-4)"`
* `structural_rot_x`: `+23.69`
* $D_{\text{modello}} = 0.045002$

### 3. `Block_1_neg` (-23.69°)
* Nodo: `ArthemyKrea2ModelRotator`
* `target_block`: `"Block_1 (All 0-4)"`
* `structural_rot_x`: `-23.69`
* $D_{\text{modello}} = 0.045002$

### 4. `Block_6_pos` (+32.21°)
* Nodo: `ArthemyKrea2ModelRotator`
* `target_block`: `"Block_6 (All 24-27)"`
* `structural_rot_x`: `+32.21`
* $D_{\text{modello}} = 0.045001$

### 5. `Block_6_neg` (-32.21°)
* Nodo: `ArthemyKrea2ModelRotator`
* `target_block`: `"Block_6 (All 24-27)"`
* `structural_rot_x`: `-32.21`
* $D_{\text{modello}} = 0.045001$

### 6. `scramble_A` (Controllo Casuale Rademacher A)
* Nodo: `ArthemyKrea2ModelScrambleRotator`
* `control`: `"scramble_A"` (segni Rademacher congelati su seed `20260919`)
* `depth_reach`: `"Default"`
* $D_{\text{modello}} = 0.045001$

### 7. `scramble_B` (Controllo Casuale Rademacher B)
* Nodo: `ArthemyKrea2ModelScrambleRotator`
* `control`: `"scramble_B"` (segni Rademacher congelati su seed `20260920`)
* `depth_reach`: `"Default"`
* $D_{\text{modello}} = 0.045002$

---

## 6. Esecuzione Automatica One-Shot (Tutti i 210 Render)

Per chi dispone dell'ambiente ComfyUI configurato, l'intero lotto si rigenera automaticamente lanciando:

```powershell
python experiments/run_rotations_block1_vs_block6.py
```

Lo script compila il manifesto JSON/CSV e accoda istantaneamente i 210 task sull'endpoint HTTP `http://127.0.0.1:8188/prompt`.
