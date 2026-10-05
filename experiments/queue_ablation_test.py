import json, urllib.request

PROMPTS = {
    "A1_ablation": "a beautiful realistic dark fantasy illustration of a red dragon flying over a medieval castle. highly detailed, cinematic lighting, dramatic shadows."
}

DOSES = [("baseline", 0, 0.0), ("skip_B1", 1, -1.0), ("skip_B3", 3, -1.0), ("skip_B5", 5, -1.0)]
SEED = 7777777
HOST = "http://127.0.0.1:8188"

wf_base = {
    "36": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_bf16.safetensors", "weight_dtype": "default"}},
    "47": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
    "48": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
    "45": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
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
    for label, block_idx, d in DOSES:
        wf = json.loads(json.dumps(wf_base))
        wf["40"]["inputs"]["text"] = text
        
        if label == "baseline":
            wf["42"]["inputs"]["model"] = ["37", 0]
        else:
            wf["50"]["inputs"][f"Block_{block_idx}"] = d
            
        wf["61"]["inputs"]["filename_prefix"] = f"benchmark_ablation_test/renders/{pid}_{label}_krea2_seed{SEED}"
        
        req = urllib.request.Request(f"{HOST}/prompt", data=json.dumps({"prompt": wf}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req)
        count += 1

print(f"Queued {count} ablation tests correctly!")
