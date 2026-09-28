#!/usr/bin/env python3
"""Render plan for the achromatic-leaf follow-up. Three arms, 142 renders.

Origin: docs/colour_gate_and_chroma_audit.md section 4 -- one cell in 108 kept its object and lost
96% of its chroma (LN_Block_4neg_0.200, seed 1337), and it replicates on neither of its own two
sibling seeds. Alessandro's two questions: does it come back on other prompts with the same preset,
and does it come back on other subjects with the same prompt structure and seed.

THE DRIVE MUST MATCH THE ORIGINAL EXACTLY. The colour sweep did NOT use vectors_override: it set
the tuner's named group input, `Block_4 = -0.2`, with `vectors_override` and `granular_json` both
empty (verified from the metadata of the very render in question). A replication driven by a
34-slot vector would not be the same treatment, and this project has already learned that the
mechanism is not interchangeable.

Every perturbed cell gets its own unperturbed baseline at the same prompt and seed, because the
statistic is a ratio to that baseline. The 20 baselines of arm A are also the control that can kill
the whole thing: if an unperturbed render collapses, the edit is not the cause.

Writes data/leaf_collapse_plan.csv. No render is generated here.
"""
import csv

OUT = "data/leaf_collapse_plan.csv"
TPL = ("a single {what} centred on a plain light grey background, macro photograph, "
       "sharp focus, even studio lighting, no other objects")
SEEDS3 = [42, 777, 1337]
SEEDS20 = list(range(2001, 2021))
SETTINGS = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple",
                steps=9, cfg=1.0, denoise=1.0, width=1024, height=1280)

# Arm B: the same subject and the same "no colour declared", five other ways of asking.
ARM_B = {
    "W1": "a single leaf centred on a plain light grey background, studio photograph, sharp focus,"
          " soft even lighting, no other objects",
    "W2": "one leaf lying flat on a plain light grey backdrop, macro photograph, high detail,"
          " diffuse lighting",
    "W3": "a single leaf on a neutral pale background, close-up photograph, crisp focus,"
          " uniform illumination",
    "W4": "a leaf, isolated on a light grey surface, macro shot, shallow depth of field,"
          " studio softbox lighting",
    "W5": "a single leaf centred on a plain white background, macro photograph, sharp focus,"
          " even studio lighting, no other objects",
}
# Arm C: other subjects with a strong colour prior. The unusual colour is held at purple for all
# four, the same unusual colour the original experiment used, so it is not a new free variable.
ARM_C = {
    "MU": ("mushroom", "brown"),
    "TO": ("tomato", "red"),
    "PC": ("pinecone", "brown"),
    "BA": ("banana", "yellow"),
}


def rows():
    out = []
    def add(arm, pid, text, seed, perturbed):
        out.append(dict(
            arm=arm, prompt_id=pid, seed=seed,
            treatment="Block_4=-0.2" if perturbed else "none",
            block_input="Block_4" if perturbed else "",
            gain=-0.2 if perturbed else "",
            vectors_override="", granular_json="",
            output_prefix=f"{pid}_{'B4neg_0.200' if perturbed else 'baseline'}_krea2_seed{seed}",
            expected_filename=f"{pid}_{'B4neg_0.200' if perturbed else 'baseline'}"
                              f"_krea2_seed{seed}_00001_.png",
            prompt_text=text, **SETTINGS))
    # Arm A -- 20 fresh seeds on the exact original prompt
    ln = TPL.format(what="leaf")
    for s in SEEDS20:
        add("A_seeds", "LN", ln, s, True)
        add("A_seeds", "LN", ln, s, False)
    # Arm B -- five other wordings, no colour declared, the three standard seeds
    for pid, text in ARM_B.items():
        for s in SEEDS3:
            add("B_wording", pid, text, s, True)
            add("B_wording", pid, text, s, False)
    # Arm C -- four other subjects x prototypical / unusual / undeclared
    for code, (subj, proto) in ARM_C.items():
        for tag, what in (("P", f"{proto} {subj}"), ("U", f"purple {subj}"), ("N", subj)):
            for s in SEEDS3:
                add("C_subject", f"{code}{tag}", TPL.format(what=what), s, True)
                add("C_subject", f"{code}{tag}", TPL.format(what=what), s, False)
    return out


def main():
    r = rows()
    for i, x in enumerate(r, 1):
        x["row_index"] = i
    cols = ["row_index", "arm", "prompt_id", "seed", "treatment", "block_input", "gain",
            "mode", "vectors_override", "granular_json", "sampler", "scheduler", "steps",
            "cfg", "denoise", "width", "height", "output_prefix", "expected_filename",
            "prompt_text"]
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for x in r: w.writerow({k: x[k] for k in cols})
    import collections
    c = collections.Counter(x["arm"] for x in r)
    print(f"{len(r)} rows -> {OUT}")
    for k, v in c.items():
        print(f"  {k}: {v}")
    print(f"  perturbed {sum(1 for x in r if x['treatment'] != 'none')}, "
          f"baseline {sum(1 for x in r if x['treatment'] == 'none')}")


if __name__ == "__main__":
    main()
