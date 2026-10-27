# Renders & Analysis — MOSS3b, confirmations at 50 steps and follow-ups (160 renders)

Esecuzione automatizzata condotta da Antigravity seguendo le direttive prescritte in [docs/directives_antigravity_moss_atlas2.md](directives_antigravity_moss_atlas2.md) e la pre-registrazione [docs/prereg_moss_atlas2.md](prereg_moss_atlas2.md).

## Step 1 — Esecuzione e Conteggio File

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& $PY moss_atlas2.py --queue
```

```text
queued 160
```

### Verifica Conteggio

```powershell
& $PY moss_atlas2.py --count
```

```text
expected 160 missing 0 []
```

### Tempi di Rendering Misurati

* **Render R50 (50 step, no LoRA, euler, CFG 3, 15 intervalli)**: Media: 167.3 s | Mediana: 166.4 s | Min: 165.1 s | Max: 172.3 s
* **Render T10 (10 step, DMD2 LoRA, euler, CFG 1, 144 intervalli)**: Media: 22.2 s | Mediana: 21.6 s | Min: 20.9 s | Max: 29.1 s
* **Arco temporale totale**: 1h 39m 51s (5991s, avviato alle 23:49:36 del 2026-10-26, concluso alle 01:29:27 del 2026-10-27; nessuna interruzione).
* **Dimensioni cartella**: `Text2Img\benchmark_moss_atlas2`: 160 files, 322.64 MB (338317741 bytes)

---

## Step 2 — Analisi DINOv2

```powershell
& $PY moss_atlas2.py --analyze
```

```text
A te22_attn_p (reported) | D R50 0.055 / T10 0.028 | -
A dit21_mlp_m (reported) | D R50 0.104 / T10 0.048 | -
A dit38_mlp_p (reported) | D R50 0.123 / T10 0.093 | -
A dit07_attn_p (reported) | D R50 0.058 / T10 0.030 | -
A dit26_attn_p (reported) | D R50 0.125 / T10 0.069 | -
A dit23_attn_p (reported) | D R50 0.037 / T10 0.045 | -
A dit40_attn_m (reported) | D R50 0.141 / T10 0.115 | -
A dit13_mlp_p (reported) | D R50 0.027 / T10 0.013 | -
A te29_mlp_p (reported) | D R50 0.067 / T10 0.040 | -
A te12_mlp_m (reported) | D R50 0.039 / T10 0.027 | -
A te00_mlp_p (reported) | D R50 0.072 / T10 0.036 | -
A te00_attn_m (reported) | D R50 0.885 / T10 0.806 | -
A te00_attn_pp (reported) | D R50 0.873 / T10 0.807 | -
A dit24_mlp_pp (reported) | D R50 0.184 / T10 0.195 | -
A dit32_attn_m (reported) | D R50 1.019 / T10 1.046 | -
A style: R50 plain against T10 plain, blacksmith (reported) | D 0.128 | -
B te_all_mlp_p | median D 0.892 vs single TE MLP +1 0.026 | additive (>= 3x)
B te_all_mlp_p0p5 | median D 0.060 vs single TE MLP +1 0.026 | not additive
B te_all_mlp_m0p5 | median D 0.130 vs single TE MLP +1 0.026 | additive (>= 3x)
B te_all_attn_p | median D 0.197 vs single TE MLP +1 0.026 | additive (>= 3x)
C text embedder vs DiT blocks (reported) | median D 0.068 vs 0.075; max 0.166 | -
D dit mlp_pp at seed 3141592 | Spearman with depth +0.83; with seed 2718281 per layer +0.83 | replicated
D te attn_m at seed 3141592 | Spearman with depth -0.17; with seed 2718281 per layer +0.24 | not replicated
```

I dataset prodotti sono stati salvati in `data/moss_atlas2_metrics.csv` e `data/moss_atlas2_tests.csv`.

---

## Vincoli di Riservatezza Visiva

In conformità al protocollo del banco MOSS3 e alle regole operative del progetto, nessuna immagine generata è stata aperta o descritta visivamente dall'agente.
