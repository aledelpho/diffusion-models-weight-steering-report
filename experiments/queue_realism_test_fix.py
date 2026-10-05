import json, urllib.request, time

PROMPTS = {
    "T1_base": "A portrait of a red fox sitting in a snowy forest, looking at the camera.",
    "T2_real": "realistic, photorealistic, highly detailed. A portrait of a red fox sitting in a snowy forest, looking at the camera.",
    "T3_paint": "painterly, visible brushstrokes, illustration. A portrait of a red fox sitting in a snowy forest, looking at the camera."
}
DOSES = [0.000, 0.550, -0.550]
SEED = 13371337
HOST = "http://127.0.0.1:8188"

wf_base = {
    "36": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_bf16.safetensors", "weight_dtype": "default"}},
    "47": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
    "48": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
    "45": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1280, "batch_size": 1}},
    "37": {"class_type": "ArthemyKrea2ResetPatcher", "inputs": {"model": ["36", 0], "clip": ["47", 0], "reset_model": True, "reset_clip": True}},
    "40": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["37", 1], "text": ""}},
    "43": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["40", 0]}},
    "42": {"class_type": "KSampler", "inputs": {"model": ["50", 0], "positive": ["40", 0], "negative": ["43", 0], "latent_image": ["45", 0], "seed": SEED, "steps": 9, "cfg": 1.0, "sampler_name": "euler_ancestral", "scheduler": "simple", "denoise": 1.0}},
    "46": {"class_type": "VAEDecode", "inputs": {"samples": ["42", 0], "vae": ["48", 0]}},
    "61": {"class_type": "SaveImage", "inputs": {"images": ["46", 0], "filename_prefix": ""}},
    "50": {"class_type": "ArthemyKrea2ModelTuner", "inputs": {"model": ["37", 0], "mode": "Real Value", "vectors_override": "", "granular_json": "", "Text_Fusion": 0.0, "Time_Embed": 0.0, "Projection": 0.0, "Block_1": 0.0, "Block_2": 0.0, "Block_3": 0.0, "Block_4": 0.0, "Block_5": 0.0, "Block_6": 0.0}}
}

count = 0
for pid, text in PROMPTS.items():
    for d in DOSES:
        wf = json.loads(json.dumps(wf_base))
        wf["40"]["inputs"]["text"] = text
        wf["50"]["inputs"]["Block_3"] = d
        
        if d == 0:
            sign = "baseline"
            # bypass tuner for baseline
            wf["42"]["inputs"]["model"] = ["37", 0]
        elif d > 0:
            sign = "pos"
        else:
            sign = "neg"
            
        d_str = f"{abs(d):.3f}" if d != 0 else "0.000"
        wf["61"]["inputs"]["filename_prefix"] = f"benchmark_realism_test/renders/{pid}_blk03_{sign}_d{d_str}_krea2_seed{SEED}"
        
        req = urllib.request.Request(f"{HOST}/prompt", data=json.dumps({"prompt": wf}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req)
        count += 1

print(f"Queued {count} tests correctly!")
