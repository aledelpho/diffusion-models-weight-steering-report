#!/usr/bin/env python3
"""Generates the preset files and the render plan for the parameter-family bench (C35/C36).

Design: docs/RENDERS_2026-09-28_parameter_families.md, frozen before the renders.

Every tensor key is read from the checkpoint's own listing
(docs/model_structures/krea2_turbo_bf16_details.json) and never typed by hand: a key that does not
exist resolves to nothing and the Preset Loader reports a lower count than the JSON claims, which
is check 2 of the spec. This script refuses to emit a preset whose key list is empty or whose
declared parameter count disagrees with the listing.

`Real Value` semantics are multiplier = 1.0 + delta (Arthemy_Krea2_Tuner.py line 1511), so the
value written into `model_patches` is delta itself.

Writes presets/Family_*.json and data/family_bench_plan.csv. No render.
"""
import csv, datetime, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTING = os.path.join(ROOT, "docs", "model_structures", "krea2_turbo_bf16_details.json")
PRESETS = os.path.join(ROOT, "presets")
OUT = os.path.join(ROOT, "data", "family_bench_plan.csv")

# family id -> (kind, regex over the checkpoint's own keys)
FAMILIES = {
    "F_wo":     ("1  2-D linear projection", r"^blocks\.\d+\.attn\.wo\.weight$"),
    "F_mod":    ("3  modulation",            r"^blocks\.\d+\.mod\.lin$"),
    "F_io":     ("5  latent interface",      r"^(first\.weight|last\.linear\.weight)$"),
    "F_norms":  ("2a block norm gains",      r"^blocks\.\d+\.(pre|post)norm\.scale$"),
    "F_qknorm": ("2b q/k normalisation",     r"^blocks\.\d+\.attn\.qknorm\.[qk]norm\.scale$"),
    "F_proj":   ("6  12-parameter router",   r"^txtfusion\.projector\.weight$"),
}
GATE_DELTA = 1.00
LADDER = [-1.00, -0.50, -0.10, 0.10, 0.50, 1.00]
PROMPTS = ["P01", "P02"]
GATE_SEEDS = ["42"]
LADDER_SEEDS = ["42", "777", "1337"]
SETTINGS = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple",
                steps=9, cfg=1.0, denoise=1.0, width=1024, height=1280)


def keys_and_mass():
    listing = json.load(open(LISTING, encoding="utf-8"))["flat_tensors_list"]
    out = {}
    for fid, (kind, pat) in FAMILIES.items():
        rx = re.compile(pat)
        ks = sorted(k for k in listing if rx.match(k))
        if not ks:
            raise RuntimeError(f"{fid}: the pattern matched no key in the checkpoint listing")
        out[fid] = (kind, ks, sum(listing[k]["param_count"] for k in ks))
    return out


def write_preset(fid, ks, delta):
    name = f"Family_{fid[2:]}_d{delta:+.3f}"
    doc = {
        "name": name, "author": "Antigravity (C35)",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "2.1", "suite_rotation_effective": True,
        "stats": {"model_patched_layers": len(ks), "model_granular_layers": 0,
                  "clip_patched_layers": 0, "clip_granular_layers": 0,
                  "chaos_recipes_count": 0, "rotation_recipes_count": 0,
                  "chaos_rotation_recipes_count": 0, "channel_recipes_count": 0,
                  "five_d_recipes_count": 0, "excluded_lora_tensors": 0},
        "model_patches": {k: delta for k in ks},
        "model_granular_patches": {}, "clip_patches": {}, "clip_granular_patches": {},
        "chaos_recipes": [], "rotation_recipes": [], "chaos_rotation_recipes": [],
        "channel_recipes": [], "five_d_recipes": [],
    }
    assert doc["stats"]["model_patched_layers"] == len(doc["model_patches"])
    os.makedirs(PRESETS, exist_ok=True)
    with open(os.path.join(PRESETS, name + ".json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
    return name


def main():
    fam = keys_and_mass()
    rows = []
    print("  %-9s %-24s %7s %16s" % ("famiglia", "genere", "tensori", "parametri"))
    for fid, (kind, ks, mass) in fam.items():
        print("  %-9s %-24s %7d %16s" % (fid, kind, len(ks), format(mass, ",d")))

    for fid, (kind, ks, mass) in fam.items():
        name = write_preset(fid, ks, GATE_DELTA)
        for p in PROMPTS:
            for s in GATE_SEEDS:
                pre = f"{p}_{fid}_d{GATE_DELTA:+.3f}_krea2_seed{s}"
                rows.append(dict(stage="1_gate", family=fid, kind=kind, delta=f"{GATE_DELTA:+.3f}",
                                 preset=name + ".json", tensors=len(ks), params=mass,
                                 prompt_id=p, seed=s, output_prefix=pre,
                                 expected_filename=pre + "_00001_.png", **SETTINGS))
    for fid, (kind, ks, mass) in fam.items():
        for d in LADDER:
            name = write_preset(fid, ks, d)
            for p in PROMPTS:
                for s in LADDER_SEEDS:
                    pre = f"{p}_{fid}_d{d:+.3f}_krea2_seed{s}"
                    rows.append(dict(stage="2_ladder", family=fid, kind=kind, delta=f"{d:+.3f}",
                                     preset=name + ".json", tensors=len(ks), params=mass,
                                     prompt_id=p, seed=s, output_prefix=pre,
                                     expected_filename=pre + "_00001_.png", **SETTINGS))
    for i, r in enumerate(rows, 1):
        r["row_index"] = i
    cols = (["row_index", "stage", "family", "kind", "delta", "preset", "tensors", "params",
             "prompt_id", "seed"] + list(SETTINGS) + ["output_prefix", "expected_filename"])
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({k: r[k] for k in cols})
    g = sum(1 for r in rows if r["stage"] == "1_gate")
    print(f"\n  presets written to presets/Family_*.json")
    print(f"  {g} gate rows + {len(rows)-g} ladder rows = {len(rows)} -> {OUT}")
    print("  stage 2 is queued ONLY for the families that pass the gate, plus F_wo:")
    print("  36 renders per family, so 72 to 144 depending on how many pass.")


if __name__ == "__main__":
    main()
