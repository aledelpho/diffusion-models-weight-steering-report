"""Write the Krea-2 Split Mixer lab workflow (UI format) for ComfyUI."""
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
    lid = len(L) + 1; L.append([lid, a["id"], sa, b["id"], sb, typ])
    a["outputs"][sa]["links"].append(lid); b["inputs"][sb]["link"] = lid

unet = node(1, "UNETLoader", [0, 0], [330, 82], ["krea2_turbo_bf16.safetensors", "default"], outputs=[("MODEL", "MODEL")])
clip = node(2, "CLIPLoader", [0, 130], [330, 106], ["qwen3vl_4b_bf16.safetensors", "krea2", "default"], outputs=[("CLIP", "CLIP")])
vae = node(3, "VAELoader", [0, 280], [330, 58], ["qwen_image_vae.safetensors"], outputs=[("VAE", "VAE")])
mm = node(4, "ArthemyKrea2SplitMixerModel", [380, 0], [360, 1600], [1.0] + [0.0] * 56 + [""],
          inputs=[("model", "MODEL")], outputs=[("MODEL", "MODEL"), ("granular_json", "STRING"), ("info", "STRING")],
          title="Split Mixer - modello (attn / MLP per blocco)")
mc = node(5, "ArthemyKrea2SplitMixerCLIP", [780, 0], [360, 2000], [1.0] + [0.0] * 72 + [""],
          inputs=[("clip", "CLIP")], outputs=[("CLIP", "CLIP"), ("granular_json", "STRING"), ("info", "STRING")],
          title="Split Mixer - text encoder (attn / MLP per layer)")
pos = node(6, "CLIPTextEncode", [1180, 0], [420, 220],
           ["Western comics style, bold ink outlines, hatched shadows, medium wide shot. A blacksmith woman stands behind a heavy oak workbench, facing the viewer."],
           inputs=[("clip", "CLIP")], outputs=[("CONDITIONING", "CONDITIONING")], title="Prompt")
zero = node(7, "ConditioningZeroOut", [1180, 260], [240, 26], [], inputs=[("conditioning", "CONDITIONING")],
            outputs=[("CONDITIONING", "CONDITIONING")])
lat = node(8, "EmptyLatentImage", [1180, 330], [300, 106], [1024, 1280, 1], outputs=[("LATENT", "LATENT")])
ks = node(9, "KSampler", [1180, 480], [300, 262], [2718281, "randomize", 9, 1.0, "euler_ancestral", "simple", 1.0],
          inputs=[("model", "MODEL"), ("positive", "CONDITIONING"), ("negative", "CONDITIONING"), ("latent_image", "LATENT")],
          outputs=[("LATENT", "LATENT")])
dec = node(10, "VAEDecode", [1520, 0], [200, 46], [], inputs=[("samples", "LATENT"), ("vae", "VAE")], outputs=[("IMAGE", "IMAGE")])
save = node(11, "SaveImage", [1520, 90], [460, 560], ["krea2_mixer/img"], inputs=[("images", "IMAGE")])
show = node(12, "PreviewAny", [1520, 700], [460, 200], [], inputs=[("source", "*")], title="JSON modello (salvalo come preset)")
show2 = node(13, "PreviewAny", [1520, 940], [460, 200], [], inputs=[("source", "*")], title="JSON text encoder")
note = node(14, "MarkdownNote", [0, 400], [340, 760], ["""## Krea-2 Split Mixer — laboratorio

Impostazioni degli esperimenti: euler_ancestral, 9 step, CFG 1, simple, 1024×1280, negativo azzerato.
Ogni cursore è un **d**: il peso diventa peso × (1 + d) (modalità *Real Value* del tuner).
Passa il mouse su un cursore: la nota riporta la guida della pagina 21 (blocco intero) o il risultato del report (encoder).
`scale` moltiplica tutto: utile per una scala di dose con un solo comando.

**Cosa abbiamo imparato (punti di partenza, non regole):**
- Blocchi finali (23–27): colore, grana, morbidezza; dosi piccole (±0,05–0,30). Se fanno rumore, prova solo l'**attn** (il rumore sta soprattutto nell'MLP).
- Blocchi centrali (5–18): contenuto e forma; ±0,3–0,55; possono ridisegnare il soggetto.
- 23 negativo / positivo: saturazione su / giù (pag. 22).
- Encoder: dosi grandi (MLP ×2 = 1,0). L06 e L14 tolgono tratti al personaggio e schiariscono la pelle; L26–L28 tengono il fumetto e il personaggio; L05 porta l'elfo verso l'anime.
- Un edit lascia una firma riconoscibile tra seed (pag. 31): prova lo stesso preset su 3–4 seed prima di giudicarlo.
- Presets leggeri su più layer non sono più coerenti di uno solo forte (C109): conta *quale* combinazione.
"""])
link(unet, 0, mm, 0, "MODEL"); link(clip, 0, mc, 0, "CLIP"); link(mc, 0, pos, 0, "CLIP"); link(pos, 0, zero, 0, "CONDITIONING")
link(mm, 0, ks, 0, "MODEL"); link(pos, 0, ks, 1, "CONDITIONING"); link(zero, 0, ks, 2, "CONDITIONING"); link(lat, 0, ks, 3, "LATENT")
link(ks, 0, dec, 0, "LATENT"); link(vae, 0, dec, 1, "VAE"); link(dec, 0, save, 0, "IMAGE")
link(mm, 1, show, 0, "STRING"); link(mc, 1, show2, 0, "STRING")
wf = {"last_node_id": len(N), "last_link_id": len(L), "nodes": N, "links": L, "groups": [], "config": {}, "extra": {}, "version": 0.4}
for out in sys.argv[1:]:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(wf, indent=1, ensure_ascii=False), encoding="utf-8"); print("wrote", out)
