"""MOSS1 gates - is the MOSS tuner exact, and does it do nothing at d = 0? (docs/moss_structure_reading.md)
Written 2026-10-25, before any MOSS render. Runs with ComfyUI's venv.

  python moss_gate.py --quant      # no ComfyUI server: loads the text encoder, checks the s_channel edit (gate B)
  python moss_gate.py --queue      # ComfyUI running with the MOSS tuner installed: queues the 6 gate renders
  python moss_gate.py --renders    # gates A and C on the renders

Gate A: plain render twice at one seed -> pixel-identical (determinism); the tuners with "{}" -> pixel-identical to
        plain. Gate B: for three quantised matrices and d = +0.10 and -0.50, the edited weight dequantised in float32
        equals the original dequantised weight x (1 + d) within 1e-5 relative; the conditioning with "{}" is bit-identical
        to the plain one. Gate C: a strong text-encoder edit (L06 MLP down x2) and a strong DiT edit (layer 20 MLP down
        x2) change the picture: mean absolute pixel difference > 5 of 255.
Sampling as the ComfyUI MOSS-Image SFT template (er_sde, simple, 25 steps, CFG 2.5), no SLG, no prompt enhancer,
1024 x 1280 as Krea-2.
"""
import argparse, dataclasses, importlib.util, json, sys, urllib.request
from pathlib import Path
import numpy as np

COMFY_DIR = Path(r"D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI")
MODELS = Path(r"D:\StabilityMatrix-win-x64\Data\Models")
IMG = Path(r"D:\StabilityMatrix-win-x64\Data\Images\Text2Img")
TE = MODELS / "TextEncoders" / "qwen3.5_9b_w4a8_gptq.safetensors"
FOLDER = "benchmark_moss_gate"
URL = "http://127.0.0.1:8188"
SEED = 2645751
PROMPT = ("Western comics style, close-up portrait, frontal view.\nfemale paladin mountain dwarf, middle-aged, resolute "
          "stern expression, thick braided copper hair pinned back, dark brown eyes, a battle-scarred wide nose, polished "
          "steel gorget over a navy blue gambeson, high brass collar, a vertical scar running through one eyebrow. white "
          "background, simple background.")
TE_KEYS = ["layers.6.mlp.down_proj.weight", "layers.7.self_attn.o_proj.weight", "layers.0.linear_attn.out_proj.weight"]
RENDERS = {"plain_a": ("", ""), "plain_b": ("", ""), "empty_json": ("{}", "{}"),
           "te_L06_mlp_down_x2": (json.dumps({"layers.6.mlp.down_proj.weight": 1.0}), ""),
           "dit_L20_ffn_down_x2": ("", json.dumps({"layers.20.proj.ffn_down.weight": 1.0})),
           "plain_c": ("", "")}


def tuner_module():
    p = COMFY_DIR / "custom_nodes" / "Arthemy_MOSS_Tuner" / "__init__.py"
    spec = importlib.util.spec_from_file_location("arthemy_moss_tuner", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def quant():
    sys.path.insert(0, str(COMFY_DIR))
    import torch, comfy.sd
    T = tuner_module()
    clip = comfy.sd.load_clip(ckpt_paths=[str(TE)], clip_type=comfy.sd.CLIPType.MOSS_IMAGE, model_options={})
    root = clip.patcher.model
    ok = True
    for key in TE_KEYS:
        name = T._resolve(root, key, ["language_model.", "model."])   # same anchors as the node (fix 2026-10-25: ComfyUI maps the TE under qwen35_9b.transformer.model.)
        w = T._get(root, name).data
        p32 = dataclasses.replace(w._params, orig_dtype=torch.float32)
        base = type(w)(w._qdata, w._layout_cls, p32).dequantize().float().cpu()
        for d in (0.10, -0.50):
            e = T.scaled_weight(w, d).data
            got = type(e)(e._qdata, e._layout_cls, dataclasses.replace(e._params, orig_dtype=torch.float32)).dequantize().float().cpu()
            rel = float((got - base * (1 + d)).abs().max() / (base * (1 + d)).abs().max())
            print(f"{name} d={d:+.2f}: max relative error {rel:.2e}")
            ok = ok and rel < 1e-5
    toks = clip.tokenize(PROMPT)
    a = clip.encode_from_tokens(toks, return_pooled=False, return_dict=True)["cond"]
    c2 = T.ArthemyMossCLIPTuner().tune(clip, "{}")[0]
    b = c2.encode_from_tokens(c2.tokenize(PROMPT), return_pooled=False, return_dict=True)["cond"]
    same = bool(torch.equal(a, b)); print("conditioning with '{}' bit-identical:", same, tuple(a.shape))
    ok = ok and same
    print("GATE B", "PASS" if ok else "FAIL - stop")


def workflow(name, te_json, dit_json):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "moss_image_sft_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3.5_9b_w4a8_gptq.safetensors", "type": "moss_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "flux2-vae_small.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["2", 0]}},
        "6": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": 1024, "height": 1280, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"seed": SEED, "steps": 25, "cfg": 2.5, "sampler_name": "er_sde",
                                                   "scheduler": "simple", "denoise": 1.0, "model": ["1", 0],
                                                   "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"{FOLDER}/{name}"}},
    }
    if te_json:
        wf["10"] = {"class_type": "ArthemyMossCLIPTuner", "inputs": {"clip": ["2", 0], "granular_json": te_json}}
        wf["4"]["inputs"]["clip"] = ["10", 0]; wf["5"]["inputs"]["clip"] = ["10", 0]
    if dit_json:
        wf["11"] = {"class_type": "ArthemyMossModelTuner", "inputs": {"model": ["1", 0], "granular_json": dit_json}}
        wf["7"]["inputs"]["model"] = ["11", 0]
    return wf


def queue():
    for name, (te, dit) in RENDERS.items():
        if (IMG / FOLDER / f"{name}_00001_.png").exists():
            continue
        req = urllib.request.Request(f"{URL}/prompt", data=json.dumps({"prompt": workflow(name, te, dit)}).encode(),
                                     headers={"Content-Type": "application/json"})
        print(name, json.loads(urllib.request.urlopen(req, timeout=10).read()).get("prompt_id"))


def renders():
    from PIL import Image
    im = {n: np.asarray(Image.open(IMG / FOLDER / f"{n}_00001_.png").convert("RGB"), dtype=np.int16) for n in RENDERS}
    d = lambda a, b: (int(np.abs(im[a] - im[b]).max()), float(np.abs(im[a] - im[b]).mean()))
    a1, a2, a3 = d("plain_a", "plain_b"), d("plain_a", "plain_c"), d("plain_a", "empty_json")
    c1, c2 = d("empty_json", "te_L06_mlp_down_x2"), d("empty_json", "dit_L20_ffn_down_x2")   # against the same route (fix 2026-10-25)
    print("A plain twice: max", a1[0], "| plain again later: max", a2[0], "| tuners with '{}': max", a3[0])
    print(f"C text-encoder edit: mean {c1[1]:.1f} | DiT edit: mean {c2[1]:.1f}")
    print("GATE A", "PASS" if a1[0] == 0 and a2[0] == 0 and a3[0] == 0 else "FAIL - stop")
    print("GATE C", "PASS" if c1[1] > 5 and c2[1] > 5 else "FAIL - stop")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("quant", "queue", "renders"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.quant: quant()
    if a.queue: queue()
    if a.renders: renders()
