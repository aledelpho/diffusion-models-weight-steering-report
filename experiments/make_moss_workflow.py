"""Write a ComfyUI UI workflow for MOSS-Image SFT with every node exposed (experiments/workflows/moss_base.json)."""
import json, sys
from pathlib import Path

N, L = [], []
def node(i, typ, pos, size, widgets, inputs=(), outputs=(), mode=0, title=None):
    n = {"id": i, "type": typ, "pos": pos, "size": size, "flags": {}, "order": len(N), "mode": mode,
         "inputs": [{"name": a, "type": t, "link": None} for a, t in inputs],
         "outputs": [{"name": a, "type": t, "links": []} for a, t in outputs],
         "properties": {"Node name for S&R": typ}, "widgets_values": widgets}
    if title:
        n["title"] = title
    N.append(n); return n
def link(a, sa, b, sb, typ):
    lid = len(L) + 1
    L.append([lid, a["id"], sa, b["id"], sb, typ])
    a["outputs"][sa]["links"].append(lid); b["inputs"][sb]["link"] = lid

M, C, V = ("MODEL", "MODEL"), ("CLIP", "CLIP"), ("VAE", "VAE")
unet = node(1, "UNETLoader", [0, 0], [330, 82], ["moss_image_sft_bf16.safetensors", "default"], outputs=[M])
lora = node(2, "LoraLoaderModelOnly", [0, 130], [330, 82], ["Moss\\lodestones-8-steps-dmd2-lora.safetensors", 1.0],
            inputs=[("model", "MODEL")], outputs=[M], mode=4, title="LoRA turbo (bypass = modello normale)")
shift = node(3, "ModelSamplingAuraFlow", [0, 260], [330, 58], [5.0], inputs=[("model", "MODEL")], outputs=[M],
             title="Shift (MOSS: 5)")
slg = node(4, "SkipLayerGuidanceDiTSimple", [0, 360], [330, 130], ["", "22", 0.0, 0.5], inputs=[("model", "MODEL")],
           outputs=[M], mode=4, title="SLG layer 22 (ufficiale; solo con CFG > 1)")
mtune = node(5, "ArthemyMossModelTuner", [0, 530], [330, 120], ["{}"], inputs=[("model", "MODEL")], outputs=[M], mode=4,
             title="MOSS Model Tuner (bypass)")
clip = node(6, "CLIPLoader", [380, 0], [330, 106], ["qwen3.5_9b_w4a8_gptq.safetensors", "moss_image", "default"], outputs=[C])
ctune = node(7, "ArthemyMossCLIPTuner", [380, 150], [330, 120], ["{}"], inputs=[("clip", "CLIP")], outputs=[C], mode=4,
             title="MOSS CLIP Tuner (bypass)")
pos = node(8, "CLIPTextEncode", [380, 310], [400, 200],
           ["Western comics style, bold ink outlines, hatched shadows, medium wide shot. A blacksmith woman stands behind a heavy oak workbench, facing the viewer."],
           inputs=[("clip", "CLIP")], outputs=[("CONDITIONING", "CONDITIONING")], title="Prompt")
neg = node(9, "CLIPTextEncode", [380, 550], [400, 120], [""], inputs=[("clip", "CLIP")], outputs=[("CONDITIONING", "CONDITIONING")],
           title="Negativo (vuoto)")
lat = node(10, "EmptyFlux2LatentImage", [820, 0], [300, 106], [1024, 1280, 1], outputs=[("LATENT", "LATENT")])
ks = node(11, "KSampler", [820, 150], [300, 262], [2718281, "fixed", 50, 3.0, "euler", "simple", 1.0],
          inputs=[("model", "MODEL"), ("positive", "CONDITIONING"), ("negative", "CONDITIONING"), ("latent_image", "LATENT")],
          outputs=[("LATENT", "LATENT")])
vae = node(12, "VAELoader", [820, 460], [300, 58], ["flux2-vae_small.safetensors"], outputs=[V])
dec = node(13, "VAEDecode", [1160, 0], [200, 46], [], inputs=[("samples", "LATENT"), ("vae", "VAE")], outputs=[("IMAGE", "IMAGE")])
save = node(14, "SaveImage", [1160, 90], [420, 500], ["moss_test/img"], inputs=[("images", "IMAGE")])
note = node(15, "MarkdownNote", [1620, 0], [420, 520], ["""## MOSS-Image SFT — banco di prova

**Riferimento (ufficiale):** euler, 50 step, CFG 3, shift 5, SLG layer 22 (0–0,5).
**Turbo (lavoro):** attiva il nodo LoRA, 10 step, **CFG 1**, euler; con CFG 1 SLG e negativo non servono.
**Template ComfyUI:** er_sde, 25 step, CFG 2,5.

Cose da provare contro gli artefatti:
1. SLG attivo / spento (nei nostri esperimenti era **spento**).
2. Shift 3 / 5 / 7.
3. Sampler: euler, er_sde, dpmpp_2m, res_multistep; scheduler: simple, beta, sgm_uniform.
4. Risoluzione 1024×1024 (default) contro 1024×1280.
5. Prompt corto contro prompt lungo (il prompt della fabbra completo è nel piano degli atlanti).

I due tuner MOSS sono in bypass: attivali solo per provare un edit (JSON `{"layers.20.proj.ffn_down.weight": 1.0}`).
"""])

link(unet, 0, lora, 0, "MODEL"); link(lora, 0, shift, 0, "MODEL"); link(shift, 0, slg, 0, "MODEL"); link(slg, 0, mtune, 0, "MODEL")
link(mtune, 0, ks, 0, "MODEL"); link(clip, 0, ctune, 0, "CLIP"); link(ctune, 0, pos, 0, "CLIP"); link(ctune, 0, neg, 0, "CLIP")
link(pos, 0, ks, 1, "CONDITIONING"); link(neg, 0, ks, 2, "CONDITIONING"); link(lat, 0, ks, 3, "LATENT")
link(ks, 0, dec, 0, "LATENT"); link(vae, 0, dec, 1, "VAE"); link(dec, 0, save, 0, "IMAGE")

wf = {"last_node_id": len(N), "last_link_id": len(L), "nodes": N, "links": L, "groups": [], "config": {}, "extra": {}, "version": 0.4}
for out in sys.argv[1:]:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(wf, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out)
