import csv
from pathlib import Path

DATA_DIR = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data")
IN_CSV = DATA_DIR / "single_blocks_v4_plan.csv"
OUT_CSV = DATA_DIR / "single_blocks_conservative_plan.csv"

FIXES = [
    (7, 0.30, 'pos'),
    (11, 0.25, 'pos'),
    (17, 0.25, 'pos'),
    (18, 0.20, 'pos'),
    (23, 0.15, 'pos'),
    (8, -0.30, 'neg'),
    (27, -0.075, 'neg'),
    (4, -0.30, 'neg'),
    (3, -0.30, 'neg'),
]

def make_plan():
    prompts = {}
    header = []
    
    with open(IN_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row[1] == 'baseline':
                prompts[row[7]] = row

    rows = []
    idx = 0
        
    for pid, prow in prompts.items():
        base_seed = prow[8]
        base_prompt = prow[13]
        
        for block_idx, dose, sign in FIXES:
            abs_dose = abs(dose)
            vec = ["0.000"] * 34
            vec[block_idx] = f"{dose:.3f}"
            vec_str = ",".join(vec)
            
            override_dict = f'{{"{block_idx}": {dose}}}'
            
            cond_id = f"blk{block_idx:02d}_{sign}_d{abs_dose:.3f}"
            filename_prefix = f"{pid}_{cond_id}_krea2_seed{base_seed}"
            expected_filename = f"{filename_prefix}_00001_.png"
            
            row = [
                str(idx),
                "perturbation",
                cond_id,
                str(block_idx),
                f"{abs_dose:.3f}",
                sign,
                "",
                pid,
                base_seed,
                override_dict,
                vec_str,
                filename_prefix,
                expected_filename,
                base_prompt,
                "Real Value",
                "euler_ancestral",
                "simple",
                "9",
                "1.0",
                "1.0",
                "1024",
                "1280"
            ]
            rows.append(row)
            idx += 1

    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
        
    print(f"Generato plan con {len(rows)} righe in {OUT_CSV}")

if __name__ == "__main__":
    make_plan()
