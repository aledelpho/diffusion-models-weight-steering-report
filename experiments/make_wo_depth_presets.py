#!/usr/bin/env python3
"""Presets and render plan for C41 — `wo` cut by depth, and the whole against the sum of its parts.

Design: docs/prereg_wo_depth.md, frozen before any render of this bench exists.

`Family_wo_d±0.100` patches one tensor in each of the 28 blocks. This bench splits that same set
into the six positional groups and renders each slice on its own, plus the union, so the union can
be tested against the composition of its parts instead of assumed equal to it.

Every key is read from the checkpoint's own listing and never typed by hand. The script refuses to
emit anything unless the six slices are pairwise disjoint and their union is EXACTLY the key set of
the existing `Family_wo_d+0.100.json` — if that fails, the parts are not parts of that whole.

`Arthemy_QKVO_wo_b1_*` and `_b6_*` already exist from benchmark_qkvo_atlas. They are reused rather
than duplicated, after checking they carry exactly the keys and delta this script would have
written.

Writes presets/WO_b{2..5}_{pos,neg}.json and data/wo_depth_plan.csv. No render.
"""
import csv, datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTING = os.path.join(ROOT, "docs", "model_structures", "krea2_turbo_bf16_details.json")
PRESETS = os.path.join(ROOT, "presets")
CP_PLAN = os.path.join(ROOT, "data", "centre_push_plan.csv")
OUT = os.path.join(ROOT, "data", "wo_depth_plan.csv")

KEY_RE = r"^blocks\.(\d+)\.attn\.wo\.weight$"
GROUPS = {"b1": range(0, 5), "b2": range(5, 10), "b3": range(10, 15),
          "b4": range(15, 20), "b5": range(20, 24), "b6": range(24, 28)}
DELTA = 0.100
SEEDS = ["1618033", "2718281", "3141592"]          # the three of benchmark_centre_push
PROMPTS = ["P01", "P02"]
SETTINGS = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple",
                steps=9, cfg=1.0, denoise=1.0, width=1024, height=1280)
REUSE = {"b1": "Arthemy_QKVO_wo_b1", "b6": "Arthemy_QKVO_wo_b6"}
UNION = "Family_wo_d{s}0.100"


def checkpoint_keys():
    fl = json.load(open(LISTING, encoding="utf-8"))["flat_tensors_list"]
    it = fl.items() if isinstance(fl, dict) else ((t["name"], t) for t in fl)
    out = {}
    for n, t in it:
        m = re.match(KEY_RE, n)
        if m:
            out[n] = (int(m.group(1)), t["param_count"])
    return out


def main():
    keys = checkpoint_keys()
    if len(keys) != 28:
        sys.exit(f"expected 28 wo tensors in the checkpoint, found {len(keys)}")
    slices = {g: sorted(k for k, (b, _) in keys.items() if b in rng) for g, rng in GROUPS.items()}

    # --- checks that must pass before a single file is written
    flat = [k for g in slices for k in slices[g]]
    if len(flat) != len(set(flat)):
        sys.exit("the six slices are not pairwise disjoint")
    for s in "+-":
        u = json.load(open(os.path.join(PRESETS, UNION.format(s=s) + ".json"), encoding="utf-8"))
        if set(u["model_patches"]) != set(flat):
            sys.exit(f"the union of the slices is not the key set of {UNION.format(s=s)}")
        if sorted({abs(v) for v in u["model_patches"].values()}) != [DELTA]:
            sys.exit(f"{UNION.format(s=s)} does not carry delta {DELTA}")
    for g, stem in REUSE.items():
        for sign, s in (("pos", "+"), ("neg", "-")):
            p = os.path.join(PRESETS, f"{stem}_{sign}.json")
            d = json.load(open(p, encoding="utf-8"))["model_patches"]
            want = {k: (DELTA if s == "+" else -DELTA) for k in slices[g]}
            if d != want:
                sys.exit(f"{p} is not the slice this script would write: cannot be reused")
    print(f"  checks passed: 6 disjoint slices, union == {UNION.format(s='+')}, b1/b6 reusable")

    # --- the eight presets that do not exist yet
    made = []
    for g in ("b2", "b3", "b4", "b5"):
        for sign, s in (("pos", 1.0), ("neg", -1.0)):
            name = f"WO_{g}_{sign}"
            body = {
                "name": name, "author": "Claude (C41)",
                "created_at": datetime.date.today().isoformat(), "version": 1,
                "suite_rotation_effective": False,
                "stats": {"model_patched_layers": len(slices[g]), "model_granular_layers": 0,
                          "clip_patched_layers": 0, "clip_granular_layers": 0,
                          "chaos_recipes_count": 0, "rotation_recipes_count": 0,
                          "chaos_rotation_recipes_count": 0, "channel_recipes_count": 0,
                          "five_d_recipes_count": 0, "excluded_lora_tensors": 0},
                "model_patches": {k: s * DELTA for k in slices[g]},
                "model_granular_patches": {}, "clip_patches": {}, "clip_granular_patches": {},
                "chaos_recipes": {}, "rotation_recipes": {}, "chaos_rotation_recipes": {},
                "channel_recipes": {}, "five_d_recipes": {},
            }
            with open(os.path.join(PRESETS, name + ".json"), "w", encoding="utf-8") as fh:
                json.dump(body, fh, indent=2)
            made.append((name, len(slices[g]), sum(keys[k][1] for k in slices[g])))
    for n, t, p in made:
        print(f"    {n}: {t} tensori, {p:,} parametri")

    # --- the plan
    cp = list(csv.DictReader(open(CP_PLAN, encoding="utf-8")))
    sha = {r["prompt_id"]: r["prompt_sha1"] for r in cp}
    text = {r["prompt_id"]: r["prompt_text"] for r in cp}
    base = {(r["prompt_id"], r["seed"]): r["expected_filename"] for r in cp if r["arm"] == "baseline"}

    conds = []
    for g in GROUPS:
        for sign in ("pos", "neg"):
            conds.append((f"slice_{g}_{sign}",
                          f"{REUSE[g]}_{sign}.json" if g in REUSE else f"WO_{g}_{sign}.json",
                          len(slices[g])))
    for sign, s in (("pos", "+"), ("neg", "-")):
        conds.append((f"union_{sign}", UNION.format(s=s) + ".json", 28))

    rows, i = [], 0
    # two determinism rows: re-render a BORROWED baseline and prove it reproduces
    for p in PROMPTS:
        i += 1
        fn = f"{p}_baseline_krea2_seed2718281"
        rows.append(dict(row_index=i, arm="determinism", condition="baseline", preset_file="",
                         tensors=0, prompt_id=p, seed="2718281",
                         output_prefix=fn + "_C41", expected_filename=fn + "_C41_00001_.png",
                         borrowed_from=f"benchmark_centre_push/renders/{base[(p,'2718281')]}",
                         prompt_sha1=sha[p], prompt_text=text[p], **SETTINGS))
    for cond, preset, nt in conds:
        for p in PROMPTS:
            for sd in SEEDS:
                i += 1
                fn = f"{p}_{cond}_krea2_seed{sd}"
                rows.append(dict(row_index=i, arm="push", condition=cond, preset_file=preset,
                                 tensors=nt, prompt_id=p, seed=sd,
                                 output_prefix=fn, expected_filename=fn + "_00001_.png",
                                 borrowed_from="", prompt_sha1=sha[p], prompt_text=text[p],
                                 **SETTINGS))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"  {len(rows)} righe ({sum(r['arm']=='push' for r in rows)} render + "
          f"{sum(r['arm']=='determinism' for r in rows)} determinismo) -> {OUT}")
    print(f"  baseline NON resi: {len(base)} presi in prestito da benchmark_centre_push")


if __name__ == "__main__":
    main()
