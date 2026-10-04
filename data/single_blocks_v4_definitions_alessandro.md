# Alessandro's per-block definitions, from looking at the v4 renders (crowns and comic page)

Received in chat on 2026-10-04, verbatim below (only the emoji in the four band headings removed). The list was condensed from his
`+`/`-` annotations by another assistant before he sent it (its own preamble is kept
as the first paragraph). He describes each entry as "the most evident change; Style
blocks do many other things, these were the most coherent ones".

These are observations, not measurements. Where a measurement in this repository
touches one of them, it is recorded in `docs/block_groups_and_prompt_order.md` §4,
and a disagreement is read first as a defect of the measurement (pitfall 90).

---

Ecco la lista pulita e sintetizzata, estratta esattamente dalle tue ultime annotazioni a punti (`+` e `-`) che hai scritto guardando i render della v4 (corone e fumetti). 

Ho raggruppato gli effetti per **Valori Negativi** e **Valori Positivi** per ogni blocco, scartando i vecchi appunti e tenendo solo la tua nuova sintesi:

### Fascia Base (Block_1)
*   **blk00**
    *   **Negativo:** + Grana, + Dettagli, + Varietà cromatica, + Coriandoli
    *   **Positivo:** + Sfumato e nebuloso (- Grana, - Dettagli, - Varietà cromatica)
*   **blk01** (Effetto opposto al blocco 0)
    *   **Negativo:** + Colori più sfumati, + Texture sottili
    *   **Positivo:** + Colori a chiazze, + Tinte piatte, + Grana, + Dettagli

### Fascia Style (Transizione verso macro e posa)
*   **blk02**
    *   **Negativo:** + Texture fini / micro dettagli, - Controllo di camera
    *   **Positivo:** + Campiture piatte, + Orientamento al macro, + Controllo di camera / colori a blocchi
*   **blk03**
    *   **Negativo:** - Luci naturali, - Tridimensionalità nelle luci
    *   **Positivo:** + Luci naturali, + Tridimensionalità nelle luci *(L'effetto muta molto in base al prompt)*
*   **blk04**
    *   **Negativo:** + Dettagli a grana fine, - Semplificazione/Astrazione
    *   **Positivo:** + Dettagli a grana grossa (dettagli fusi), + Semplificazione/Astrazione
*   **blk05**
    *   **Negativo:** + Scuro, + Sporco/Disordinato
    *   **Positivo:** + Luminosità, - Sporco/Disordinato
*   **blk06**
    *   **Negativo:** + Volumi, + Organico, - Colori, - Stilizzazione
    *   **Positivo:** + Colori, + Stilizzazione, + Artificiale, - Volumi
*   **blk07**
    *   **Negativo:** - Fusione degli elementi (riduce il concept bleeding), - Deformazioni
    *   **Positivo:** + Fusione degli elementi (amplifica il concept bleeding), + Deformazioni
*   **blk08**
    *   **Negativo:** + Espressioni (espressività e naturalezza delle pose), - Realismo delle texture, - Appiattimento
    *   **Positivo:** + Realismo delle texture, + Deformazioni/Appiattimento, - Espressioni e naturalezza delle pose
*   **blk09**
    *   **Negativo:** - Realismo nei volumi, - Realismo nei materiali
    *   **Positivo:** + Realismo nei volumi, + Realismo nei materiali
*   **blk10** *(Effetto variabile a seconda del prompt)*
    *   **Negativo:** + Espressioni
    *   **Positivo:** - Espressioni
*   **blk11**
    *   **Negativo:** + Controllo di camera, + Stile evidenziato, - Deformazioni/Astrazione
    *   **Positivo:** + Deformazioni/Astrazione, - Controllo di camera, - Stile (si perde)
*   **blk12**
    *   **Negativo:** + Controllo di camera, + Prospettiva, + Imperfezioni, - Deformazioni
    *   **Positivo:** + Deformazione, - Controllo di camera, - Prospettiva, - Imperfezioni
*   **blk13**
    *   **Negativo:** + Organico
    *   **Positivo:** + Geometrico
*   **blk14**
    *   **Negativo:** + Distinzione ed evidenziazione dettagli, - Contrasto cromatico (meno colori), - Profondità texture
    *   **Positivo:** + Contrasto cromatico, + Profondità texture, - Distinzione ed evidenziazione dettagli
*   **blk15**
    *   **Negativo:** + Profondità (luci, ombre, riflessi, traslucenze), + Realismo nei dettagli
    *   **Positivo:** - Profondità (soggetti semplificati e appiattiti), - Realismo nei dettagli
*   **blk16**
    *   **Negativo:** - Semplificazione texture (texture più complesse), - Sintesi delle forme (più dettagli, meno astrazione)
    *   **Positivo:** + Semplificazione texture (si ovattano), + Sintesi delle forme (meno dettagli, più astrazione)
*   **blk17**
    *   **Negativo:** - Sintesi del soggetto (meno stilizzati, più aderenti e specifici al prompt)
    *   **Positivo:** + Sintesi del soggetto (tutto reso più semplice, meno aderente al prompt)
*   **blk18**
    *   **Negativo:** + Profondità e tridimensionalità (volumi)
    *   **Positivo:** - Profondità e tridimensionalità (volumi)

### Fascia Details (Proprietà macro dell'immagine)
*   **blk19**
    *   **Negativo:** + Soggetti plasmati attraverso forme, + Complessità nei dettagli
    *   **Positivo:** + Soggetti plasmati attraverso luci, - Complessità nei dettagli
*   **blk20**
    *   **Negativo:** - Contrasto di elementi (parti dei soggetti più uniformi e mescolate)
    *   **Positivo:** + Contrasto di elementi (parti dei soggetti più distinte e separate cromaticamente)
*   **blk21**
    *   **Negativo:** + Grana fine dei dettagli (imperfezioni e texture più fini)
    *   **Positivo:** + Grana grossa dei dettagli (imperfezioni e texture accentuate)
*   **blk22** (A cavallo con Correction)
    *   **Negativo:** - Evidenzia e appiattisce texture *(ndr: testuale dai tuoi appunti)*
    *   **Positivo:** + Sfoca e ammorbidisce texture

### Fascia Correction (Proprietà fisiche/cromatiche globali)
*   **blk23**
    *   **Negativo:** + Saturazione
    *   **Positivo:** - Saturazione
*   **blk24**
    *   **Negativo:** + Contrasto cromatico (colori più piatti e distinti), + Texture aggressive
    *   **Positivo:** - Contrasto cromatico (colori più sfumati e complessi), - Texture aggressive
*   **blk25**
    *   **Negativo:** - Sfocatura dei colori
    *   **Positivo:** + Sfocatura dei colori
*   **blk26**
    *   **Negativo:** - Fine textures
    *   **Positivo:** + Fine textures (aggiunge grana)
*   **blk27**
    *   **Negativo:** + Sfoca l'immagine, + Scurisce i colori
    *   **Positivo:** + Aggiunge grana all'immagine, + Schiarisce i colori *(simile a un filtro "nitidezza/sharpen" aggressivo di Photoshop)*
