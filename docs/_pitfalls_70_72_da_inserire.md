# Pitfall 70–72, da inserire in `errors_log.md` (proposta, 2026-09-23)

Fonte: `docs/prereg_rotations_block1_vs_block6_emendamento_v3.md` e `_v4.md`. Numerazione proposta,
da confermare dall'autore come per 64–69. Due righe sono **ricorrenze**, non trappole nuove.

| # | Pitfall | Meccanismo | Conseguenza silenziosa | Prevenzione |
|---|---|---|---|---|
| **70** | Un cancello eseguito e riassunto a parole da chi ha interesse a proseguire | Il cancello del pilota v3 era scritto in prosa nel brief; l'esecutore lo ha calcolato correttamente e poi ha deciso e riportato da sé | Il CSV diceva 18/24 e `scrB` a \|dL\| 29–37; il log diceva «100% di superamento, \|dL\| ≤ 7.88». 270 render alla dose sbagliata, e un campo `measured_D_node` riempito col valore obiettivo invece che misurato | Il cancello è uno **script scritto da chi analizza**, termina con codice di uscita non nullo, e il log ne incolla l'output integralmente. Fermate obbligatorie con verifica esterna fra le fasi. Famiglia D1 |
| **71** | Pilota su 3 prompt per un cancello «tutte passano» su 10 | **Ricorrenza del 52**. Il caso peggiore (`S06_pastel`, \|dL\| 40.4) non era nel pilota | Il pilota sottostimava il fallimento proprio come nel 52 | Il pilota di un cancello «tutte» copre tutti i prompt, su un seed fuori dal test. Famiglia C5 |
| **72** | La fedeltà in **direzione** di una modifica piccola in bf16, mai misurata | **Ricorrenza del 46**, nuova nella forma: il 46 guardava la norma, qui la norma regge (±2.4%) e cede la direzione | A D = 0.0018 la modifica applicata ha cos 0.955 con quella voluta: circa il 30% di ciò che si rende è arrotondamento, identico a ogni seed e diverso per braccio | Per ogni dose e braccio, misura D **e** cos(ΔW_bf16, ΔW_fp32) sui pesi dopo il cast che il motore esegue davvero (`comfy/float.py`). Famiglia C3 |

Nota a margine, non un pitfall: il cancello \|dL\| ≤ 20 misura quanto si muove l'esposizione, non se
l'immagine si rompe (`scrB` a 0.0071 ha grad_ratio normale). Averlo scelto come criterio di integrità
è ciò che ha reso vuota la regione ammissibile; cambiarlo dopo il fallimento sarebbe stato il pitfall 68.
