import urllib.request
import json
import time

PROMPTS = {
    "No_Style": "A portrait of a red fox sitting in a snowy forest, looking at the camera.",
    "Realistic": "hyperrealistic, highly detailed, realistic photograph. A portrait of a red fox sitting in a snowy forest, looking at the camera.",
    "Painterly": "painterly, visible brushstrokes, oil painting. A portrait of a red fox sitting in a snowy forest, looking at the camera."
}

DOSES = [-0.500, 0.000, 0.500]
SEED = 12345

WORKFLOW_PATH = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments\workflow_api.json"

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
    urllib.request.urlopen(req)

with open(WORKFLOW_PATH, "r") as f:
    base_wf = json.load(f)

for p_name, p_text in PROMPTS.items():
    for dose in DOSES:
        wf = json.loads(json.dumps(base_wf))
        
        # Imposta Seed e Prompt
        wf["3"]["inputs"]["seed"] = SEED
        wf["6"]["inputs"]["text"] = p_text
        
        # Cerca il nodo ModelSurgeon e impostalo su blk03
        for node_id, node in wf.items():
            if node["class_type"] == "ModelSurgeon":
                node["inputs"]["target_blocks"] = "3"
                node["inputs"]["dose"] = dose
            if node["class_type"] == "SaveImage":
                sign = "base" if dose == 0 else ("pos" if dose > 0 else "neg")
                dose_str = f"{abs(dose):.3f}"
                wf[node_id]["inputs"]["filename_prefix"] = f"realism_test/blk03_{p_name}_{sign}_{dose_str}"

        queue_prompt(wf)

print("9 task inviati in coda per il test del Realismo su Blk03!")
