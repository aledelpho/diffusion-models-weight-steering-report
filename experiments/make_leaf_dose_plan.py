#!/usr/bin/env python3
"""Render plan for C23 -- the dose ladder on the twenty seeds of arm A. 80 renders.

Origin: docs/leaf_collapse_predictors_result.md. C22 ruled out the endpoint: nothing in the
unperturbed image, in twelve features or jointly, says which seeds lose their colour. What is left
is the trajectory, and the cheapest handle on it is dose -- if the switch has a per-seed threshold,
that threshold is the bifurcation parameter.

Nothing here is re-rendered that already exists. The twenty baselines and the twenty cells at dose
0.200 are on disk in benchmark_leaf_collapse and are reused as they are. Only four new doses.

Drive identical to arm A, verified from those renders' metadata: tuner named group input
`Block_4 = -dose`, `vectors_override` EMPTY, `granular_json` empty, mode Real Value. Not a 34-slot
vector. Same prompt string, character for character, and the same sampler settings.

Writes data/leaf_dose_plan.csv. No render is generated here.
"""
import csv

OUT = "data/leaf_dose_plan.csv"
PROMPT = ("a single leaf centred on a plain light grey background, macro photograph, "
          "sharp focus, even studio lighting, no other objects")
FIRE = [2001, 2003, 2005, 2006, 2008, 2011, 2013, 2014, 2017]
QUIET = [2002, 2004, 2007, 2009, 2010, 2012, 2015, 2016, 2018, 2019, 2020]
# 0.200 already exists for all twenty; 0.280 is above it, and it is the dose that decides D2.
DOSES = ["0.050", "0.080", "0.120", "0.280"]
SETTINGS = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple",
                steps=9, cfg=1.0, denoise=1.0, width=1024, height=1280)


def main():
    rows = []
    for dose in DOSES:
        for group, seeds in (("fire", FIRE), ("quiet", QUIET)):
            for s in seeds:
                pre = f"LN_B4neg_{dose}_krea2_seed{s}"
                rows.append(dict(
                    group_at_0200=group, seed=s, dose=dose,
                    treatment=f"Block_4=-{dose}", block_input="Block_4", gain=f"-{dose}",
                    vectors_override="", granular_json="",
                    output_prefix=pre, expected_filename=f"{pre}_00001_.png",
                    prompt_text=PROMPT, **SETTINGS))
    for i, x in enumerate(rows, 1):
        x["row_index"] = i
    cols = ["row_index", "group_at_0200", "seed", "dose", "treatment", "block_input", "gain",
            "mode", "vectors_override", "granular_json", "sampler", "scheduler", "steps",
            "cfg", "denoise", "width", "height", "output_prefix", "expected_filename",
            "prompt_text"]
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for x in rows: w.writerow({k: x[k] for k in cols})
    print(f"{len(rows)} rows -> {OUT}")
    print(f"  {len(DOSES)} new doses x {len(FIRE)+len(QUIET)} seeds")
    print("  reused, not re-rendered: 20 baselines and 20 cells at dose 0.200")


if __name__ == "__main__":
    main()
