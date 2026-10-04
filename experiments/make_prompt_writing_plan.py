import csv
import json
from pathlib import Path

def main():
    data_dir = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data")
    docs_dir = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\docs")
    out_csv = data_dir / "prompt_writing_plan.csv"
    
    prereg = docs_dir / "prereg_prompt_writing.md"
    with open(prereg, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    extracted_prompts = {}
    current_key = None
    in_fence = False
    buffer = []
    for line in lines:
        if line.startswith("**S") and "W" in line and "=" not in line:
            current_key = line.strip().strip('*')
        elif line.startswith("`"):
            if not in_fence:
                in_fence = True
                buffer = []
            else:
                in_fence = False
                if current_key:
                    extracted_prompts[current_key] = "".join(buffer).strip()
                    current_key = None
        elif in_fence:
            buffer.append(line)
            
    S1_W1 = None
    S1_W2 = None
    with open(data_dir / 'prompt_order_experiment_plan.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['prompt_id'] == 'V1_Original' and S1_W1 is None:
                S1_W1 = row['prompt']
            if row['prompt_id'] == 'V5_Inverse' and S1_W2 is None:
                S1_W2 = row['prompt']
                
    S2_W1 = None
    with open(data_dir / 'single_blocks_v3_plan.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['prompt_id'] == 'P2_lotuscanoe' and S2_W1 is None:
                S2_W1 = row['prompt_text']
                
    S1_C1 = S1_W1.replace('a heavy silver gauntlet crackling with blue electric energy', 'a heavy bronze gauntlet wreathed in orange flames')
    S1_C1 = S1_C1.replace('sharp blue highlights along her electrified gauntlet', 'sharp orange highlights along her flaming gauntlet')

    S2_C1 = S2_W1.replace('a young woman sleeps peacefully on her back', 'an old bearded man sleeps peacefully on his back')
    S2_C1 = S2_C1.replace('Her head is turned gently to one side, long dark wavy hair spread across the wooden boards', 'His head is turned gently to one side, long grey beard spread across the wooden boards')
    S2_C1 = S2_C1.replace('holding a small closed book', 'holding a small wooden flute')
    S2_C1 = S2_C1.replace('She wears a flowing ivory dress with soft layered fabric cascading around her legs, her bare feet visible near the stern', 'He wears a loose grey robe with heavy folds of fabric around his legs, his bare feet visible near the stern')

    prompts = {
        'S1_W1_original': S1_W1,
        'S1_W2_reordered': S1_W2,
        'S1_W3_tags': extracted_prompts['S1_W3'],
        'S1_W4_synonyms': extracted_prompts['S1_W4'],
        'S1_C1_flamegauntlet': S1_C1,
        'S2_W1_original': S2_W1,
        'S2_W2_reordered': extracted_prompts['S2_W2'],
        'S2_W3_tags': extracted_prompts['S2_W3'],
        'S2_W4_synonyms': extracted_prompts['S2_W4'],
        'S2_C1_oldman': S2_C1
    }
    
    target_blocks = ['0', '2', '5', '8', '9', '12', '13', '15', '17', '19', '23', '27']
    conditions = {}
    for file_name in ['prompt_order_experiment_plan.csv', 'prompt_order_experiment_plan_full.csv']:
        with open(data_dir / file_name, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['prompt_id'] == 'V1_Original':
                    if row['block'] in target_blocks or row['cond_id'] == 'baseline':
                        seed = row['base_seed']
                        cond = row['cond_id']
                        if seed not in conditions:
                            conditions[seed] = {}
                        if cond not in conditions[seed]:
                            conditions[seed][cond] = {
                                'block': row['block'],
                                'dose': row['dose'],
                                'sign': row['sign'],
                                'override_dict': row['override_dict'],
                                'vector': row['vector'],
                                'sampler': row['sampler'],
                                'scheduler': row['scheduler'],
                                'steps': row['steps'],
                                'cfg': row['cfg'],
                                'denoise': row['denoise'],
                                'width': row['width'],
                                'height': row['height']
                            }
                            
    # Create 1234567 for blocks that only have 3141592
    if '1234567' not in conditions:
        conditions['1234567'] = {}
    for cond_id, c in conditions['3141592'].items():
        if cond_id not in conditions['1234567']:
            conditions['1234567'][cond_id] = c.copy()
            
    assert len(conditions['3141592']) == 25
    assert len(conditions['1234567']) == 25
    for cond in conditions['3141592']:
        c1 = conditions['3141592'][cond]
        c2 = conditions['1234567'][cond]
        assert c1['dose'] == c2['dose']
        assert c1['sign'] == c2['sign']
        assert c1['vector'] == c2['vector']
        assert c1['override_dict'] == c2['override_dict']
        assert c1['sampler'] == 'euler_ancestral'
        assert c1['scheduler'] == 'simple'
        assert c1['steps'] == '9'
        assert c1['cfg'] == '1.0'
        assert c1['denoise'] == '1.0'
        assert c1['width'] == '1024'
        assert c1['height'] == '1280'
        
    header = [
        "id","type","cond_id","block","dose","sign","status",
        "prompt_id","base_seed","override_dict","vector",
        "filename_prefix","expected_filename","prompt",
        "checkpoint","sampler","scheduler","steps","cfg","denoise","width","height"
    ]
    rows = []
    
    c_base = conditions['3141592']['baseline']
    prefix = "REPRO_V1_Original_baseline_krea2_seed3141592"
    rows.append([
        "0", "repro", "baseline", c_base['block'], c_base['dose'], c_base['sign'], "",
        "V1_Original", "3141592", c_base['override_dict'], c_base['vector'],
        prefix, f"{prefix}_00001_.png", prompts['S1_W1_original'],
        "Real Value", c_base['sampler'], c_base['scheduler'], c_base['steps'], c_base['cfg'], c_base['denoise'], c_base['width'], c_base['height']
    ])
    
    idx = 1
    target_prompts = [
        'S1_W3_tags', 'S1_W4_synonyms', 'S1_C1_flamegauntlet',
        'S2_W1_original', 'S2_W2_reordered', 'S2_W3_tags', 'S2_W4_synonyms', 'S2_C1_oldman'
    ]
    
    for seed in ['3141592', '1234567']:
        for pid in target_prompts:
            for cond_id, c in conditions[seed].items():
                p_type = "baseline" if cond_id == "baseline" else "perturbation"
                prefix = f"{pid}_{cond_id}_krea2_seed{seed}"
                
                rows.append([
                    str(idx), p_type, cond_id, c['block'], c['dose'], c['sign'], "",
                    pid, seed, c['override_dict'], c['vector'],
                    prefix, f"{prefix}_00001_.png", prompts[pid],
                    "Real Value", c['sampler'], c['scheduler'], c['steps'], c['cfg'], c['denoise'], c['width'], c['height']
                ])
                idx += 1
                
    assert len(rows) == 8 * 25 * 2 + 1, f"Expected 401 rows, got {len(rows)}"
    with open(out_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} rows successfully.")
    
if __name__ == '__main__':
    main()
