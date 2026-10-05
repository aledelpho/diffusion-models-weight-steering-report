import csv
import json
import urllib.request
import urllib.error
import time
from pathlib import Path

DATA_DIR = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data")
CSV_PLAN = DATA_DIR / "prompt_order_experiment_plan_full.csv"
WORKFLOW_PATH = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments\workflows\workflow_benchmark_api.json")

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
    req.add_header("Content-Type", "application/json")
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.URLError as e:
        print(f"Error queueing: {e}")
        return None

def main():
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow_template = json.load(f)
        
    with open(CSV_PLAN, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        tasks = list(reader)
        
    queued_count = 0
    for task in tasks:
        # Clone workflow
        wf = json.loads(json.dumps(workflow_template))
        
        # Le key nodes nel tuo workflow_benchmark_api.json:
        # 6: test prompt
        # 77: negative prompt
        # 71: noise seed
        # 16: KSampler (seed, steps, cfg)
        # 42: Model Surgeon
        # 19: Save Image (filename_prefix)
        
        # Update Prompt
        wf["6"]["inputs"]["text"] = task["prompt"]
        
        # Update Seed
        seed_val = int(task["base_seed"])
        wf["71"]["inputs"]["noise_seed"] = seed_val
        wf["16"]["inputs"]["seed"] = seed_val
        
        # Update Model Surgeon (if perturbation)
        if task["type"] == "perturbation":
            wf["42"]["inputs"]["weights_override"] = task["override_dict"]
        else:
            wf["42"]["inputs"]["weights_override"] = "{}"
            
        # Update Output Prefix
        # Importante: ComfyUI aggiunge roba, quindi salviamo in una cartella specifica
        out_prefix = f"benchmark_prompt_order/renders/{task['filename_prefix']}"
        wf["19"]["inputs"]["filename_prefix"] = out_prefix
        
        res = queue_prompt(wf)
        if res:
            queued_count += 1
            
        # Optional short sleep to not flood the server
        time.sleep(0.02)
        
    print(f"Coda inviata con successo: {queued_count} task.")
    
if __name__ == "__main__":
    main()
