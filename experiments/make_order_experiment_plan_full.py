import csv
from pathlib import Path

DATA_DIR = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data")
OUT_CSV = DATA_DIR / "prompt_order_experiment_plan_full.csv"

ST = "realistic western comics style, bold ink outlines, hatched shadows"
INQ = "smug grin with half-closed eye, seen from a high angle, from above, top view, dynamic, upper body portrait, close-up on gauntlet, dynamic pose, dramatic angle, strong perspective."
SOG = "female antlered elf brawler, tousled green hair fading to teal at the tips, thick green eyebrows, an eyepatch over one eye, pointed ears, tan sun-kissed skin gradient, small pair of pale antlers, young adult, a sharp bright green visible eye, wide reckless grin."
OUT = "fur-collared dark navy jacket with a gold wood-textured pauldron, black uniform, brown leather arm straps. looking to her left, wearing a heavy silver gauntlet crackling with blue electric energy, showing fist to viewer, wildly smug expression."
BG = "Background: white empty background, flat background. Lighting: warm light, deep amber shadows and sharp blue highlights along her electrified gauntlet."

prompts = {
    "V1_Original": f"{ST}, {INQ} {SOG} {OUT} {BG}",
    "V2_SubjectFirst": f"{SOG} {OUT} {ST}, {INQ} {BG}",
    "V3_BGFirst": f"{BG} {INQ} {ST}, {SOG} {OUT}",
    "V4_ActionFirst": f"{OUT} {INQ} {SOG} {BG} {ST}.",
    "V5_Inverse": f"{BG} {OUT} {SOG} {INQ} {ST}."
}

# Blocks already done: 0, 10, 16, 24, 27
done_blocks = [0, 10, 16, 24, 27]
remaining_blocks = [b for b in range(28) if b not in done_blocks]

FIXES = []
for b in remaining_blocks:
    if b in [1, 25, 26]:
        dose = 0.200
    else:
        dose = 0.350
        
    FIXES.append((b, dose, 'pos'))
    FIXES.append((b, -dose, 'neg'))

seeds = ["3141592", "1234567"]

def make_plan():
    header = [
        "id","type","cond_id","block","dose","sign","status",
        "prompt_id","base_seed","override_dict","vector",
        "filename_prefix","expected_filename","prompt",
        "checkpoint","sampler","scheduler","steps","cfg","denoise","width","height"
    ]
    
    rows = []
    idx = 0
    
    for base_seed in seeds:
        for pid, prompt_text in prompts.items():
            # We skip baselines since they are already generated for these 2 seeds!
            # Perturbations
            for block_idx, dose, sign in FIXES:
                abs_dose = abs(dose)
                vec = ["0.000"] * 34
                vec[block_idx] = f"{dose:.3f}"
                vec_str = ",".join(vec)
                
                override_dict = f'{{"{block_idx}": {dose}}}'
                cond_id = f"blk{block_idx:02d}_{sign}_d{abs_dose:.3f}"
                filename_prefix = f"{pid}_{cond_id}_krea2_seed{base_seed}"
                
                row = [
                    str(idx), "perturbation", cond_id, str(block_idx), f"{abs_dose:.3f}", sign, "",
                    pid, base_seed, override_dict, vec_str,
                    filename_prefix, f"{filename_prefix}_00001_.png",
                    prompt_text, "Real Value", "euler_ancestral", "simple", "9", "1.0", "1.0", "1024", "1280"
                ]
                rows.append(row)
                idx += 1

    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
        
    print(f"Generato plan con {len(rows)} righe (23 blocchi, pos/neg, 5 prompt, 2 seed) in {OUT_CSV}")

if __name__ == "__main__":
    make_plan()
