# Anima DiT (Cosmos-Predict2 / Anima Pencil v10) — Full Architectural Decomposition

## Checkpoints di Riferimento

| Checkpoint | Path / Nome File | Precisione | Tensori | Parametri Totali | Prefisso Chiavi | Buffer `sigmas` |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Anima Base** | `anima_baseV10.safetensors` | **100% BF16** | **685** | **2,091,068,928** | `net.` | Assente (Clean) |
| **Anima v2.0** | `arthemyComicsAnima_v20.safetensors` | **100% F32** | **686** | **2,091,069,928** | `model.diffusion_model.` | Presente (`[1000]`) |

> [!NOTE]
> La topologia interna dei due checkpoint è **perfettamente identica al 100%** su tutte le 685 matrici dei pesi. `arthemyComicsAnima_v20.safetensors` possiede esattamente 1 tensore in più (per un totale di 1.000 parametri in più) dovuto all'inclusione del buffer di runtime `model_sampling.sigmas` generato e serializzato durante un salvataggio da ComfyUI. Inoltre, la versione Base è in precisione nativa **bfloat16** (3.89 GB), mentre la v2.0 è salvata in **float32** (7.79 GB).

---

## Level 0 — Macro Architecture Overview

```mermaid
graph TD
    INPUT["Input Latent<br/>(B×64×H×W + 4 pos channels = 68)"]
    XEMB["x_embedder — Input Projection<br/>68→2048 | BF16"]
    TEMB["t_embedder — Timestep Embedder<br/>2048→2048→6144 | BF16"]
    
    subgraph LLMADAPTER["LLM Adapter Pipeline (6 blocks × 16.78M params)"]
        LLMEMB["llm_adapter.embed<br/>32128→1024 | BF16"]
        LLMB0["llm_adapter.blocks.0"]
        LLMDOTS["..."]
        LLMB5["llm_adapter.blocks.5"]
        LLMNORM["llm_adapter.norm (1024)"]
        LLMPROJ["llm_adapter.out_proj (1024→1024)"]
    end

    subgraph BACKBONE["Transformer Backbone (28 blocks × 69.21M params each)"]
        B0["blocks.0"]
        B1["blocks.1"]
        BDOTS["..."]
        B27["blocks.27"]
    end

    FINAL["final_layer — Output Projection & AdaLN<br/>2048→64 | BF16"]
    OUTPUT["Output Latent<br/>(B×64×H×W)"]

    INPUT --> XEMB
    XEMB --> BACKBONE
    TEMB -->|"adaptive conditioning (AdaLN)"| BACKBONE
    TEMB -->|"adaptive conditioning"| FINAL
    LLMEMB --> LLMB0 --> LLMDOTS --> LLMB5 --> LLMNORM --> LLMPROJ
    LLMPROJ -->|"text context (1024-dim)"| BACKBONE
    BACKBONE --> FINAL
    FINAL --> OUTPUT

    B0 --> B1 --> BDOTS --> B27
```

### Parameter Distribution (Anima Base — Exact & Unapproximated)

| Componente | Parametri Esatti | % del Totale | Conteggio Tensori |
|---|---|---|---|
| **Transformer Backbone** (`blocks.0`–`27`) | 1,937,782,784 | 92.67% | 560 |
| **LLM Adapter Blocks** (`llm_adapter.blocks.0`–`5`) | 100,713,984 | 4.82% | 114 |
| **LLM Adapter Head & Embed** (`embed`, `norm`, `out_proj`) | 33,949,696 | 1.62% | 4 |
| **Time Embedder** (`t_embedder`, `t_embedding_norm`) | 16,779,264 | 0.80% | 3 |
| **Final Layer** (`final_layer.linear`, `adaln_modulation`) | 1,703,936 | 0.08% | 3 |
| **Input Embedder** (`x_embedder.proj.1`) | 139,264 | 0.01% | 1 |
| **TOTALE ANIMA BASE** | **2,091,068,928** | **100.00%** | **685** |

---

## Level 1 — Main Transformer Block Anatomy (×28 identical)

Ogni blocco `blocks.N` contiene esattamente **20 tensori** per complessivi **69,206,528 parametri**:

```mermaid
graph TB
    subgraph BLOCK["blocks.N (69.21M params, 20 tensori)"]
        subgraph ADALN["AdaLN Modulation (1.57M params)"]
            MSA1["adaln_modulation_self_attn.1 [256×2048]"]
            MSA2["adaln_modulation_self_attn.2 [6144×256]"]
            MCA1["adaln_modulation_cross_attn.1 [256×2048]"]
            MCA2["adaln_modulation_cross_attn.2 [6144×256]"]
            MMLP1["adaln_modulation_mlp.1 [256×2048]"]
            MMLP2["adaln_modulation_mlp.2 [6144×256]"]
        end
        subgraph SELFA["Self-Attention (16.78M params)"]
            SQ["self_attn.q_proj [2048×2048]"]
            SK["self_attn.k_proj [2048×2048]"]
            SV["self_attn.v_proj [2048×2048]"]
            SO["self_attn.output_proj [2048×2048]"]
            SQN["self_attn.q_norm [128]"]
            SKN["self_attn.k_norm [128]"]
        end
        subgraph CROSSA["Cross-Attention (12.58M params)"]
            CQ["cross_attn.q_proj [2048×2048]"]
            CK["cross_attn.k_proj [2048×1024]"]
            CV["cross_attn.v_proj [2048×1024]"]
            CO["cross_attn.output_proj [2048×2048]"]
            CQN["cross_attn.q_norm [128]"]
            CKN["cross_attn.k_norm [128]"]
        end
        subgraph MLP["Feed-Forward MLP (33.55M params)"]
            L1["mlp.layer1.weight [8192×2048]"]
            L2["mlp.layer2.weight [2048×8192]"]
        end
    end
```

### Confronto Iperparametri: Anima vs Krea2

| Iperparametro | Anima Base (`anima_baseV10`) | Krea-2 Turbo (`krea2_turbo_bf16`) |
|---|---|---|
| **Architettura Base** | DiT (Cosmos-Predict2) | DiT |
| **Dimensione Nascosta ($d_{model}$)** | 2048 | 6144 |
| **Dimensione Intermedia MLP ($d_{ff}$)** | 8192 (x4.0) | 16384 (SwiGLU, x2.67) |
| **Dimensione Testa Attenzione** | 128 | 128 |
| **Teste Query** | 16 teste | 48 teste |
| **Teste Key/Value** | 16 teste (MHA) | 12 teste (GQA 4:1) |
| **Condizionamento Contesto** | Cross-Attention (dimensione 1024 da LLM Adapter) | txtfusion & txtmlp (modulazione adattiva a 12 scale) |
| **Adattatore Testuale** | 6 blocchi dedicati (`llm_adapter`) | 4 blocchi (`txtfusion`) |
| **Canali Input Latente** | 68 (64 latenti + 4 posizionali) | 64 |
| **Canali Output Latente** | 64 | 64 |
