"""C49 — presets per prompt family (docs/prereg_prompt_family.md). Written by Claude, 2026-10-04.

  python experiments/prompt_family.py --plan             # data/prompt_family_plan.csv (289 rows)
  python experiments/prompt_family.py --queue --first 1  # the REPRO row only
  python experiments/prompt_family.py --repro            # REPRO must equal the existing C3_fox baseline
  python experiments/prompt_family.py --queue            # the rest (skips files that exist)
  python experiments/prompt_family.py --count            # 289 files expected

Output: Text2Img/benchmark_prompt_family/{prompt_id}_{cond}_krea2_seed{seed}_00001_.png
Workflow identical to blk23_colorful.py (Tuner only on rows with a vector).
"""
import argparse, csv, json, os, urllib.request
from pathlib import Path
from blk23_colorful import workflow, COMFY

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "data" / "prompt_family_plan.csv"
IMG_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img")
FOLDER = "benchmark_prompt_family"

FAMILIES = {"F1cartoon": "Cartoon style illustration.", "F2oil": "Oil painting.", "F3photo": "Photograph."}
_styles = {r["prompt_id"]: r["prompt_text"] for r in csv.DictReader(open(REPO / "data" / "single_blocks_styles_plan.csv", encoding="utf-8-sig"))
           if r["condition"] == "baseline"}
_strip = lambda t: t[len("Cartoon style illustration. "):] if t.startswith("Cartoon style illustration. ") else None
SUBJECTS = {
    "blacksmith": _strip(_styles["C1_blacksmith"]),
    "rally": _strip(_styles["C2_rally"]),
    "fox": _strip(_styles["C3_fox"]),
    "stilllife": _strip(_styles["C4_stilllife"]),
    "fisherman": "an old fisherman with a grey beard mending a fishing net on a wooden pier, harbour boats behind him, overcast afternoon light.",
    "lighthouse": "a white lighthouse on a rocky coast at dusk, waves breaking on the rocks, a few seagulls in the sky.",
}
SEEDS = ["5772156", "1414213"]
# arm id -> {slot: signed dose}. Single-block doses are Alessandro's calibrated styles doses.
ARMS = {
    "baseline": {},
    "blk16_pos_d0.300": {16: 0.30},
    "blk20_pos_d0.450": {20: 0.45},
    "blk23_neg_d0.300": {23: -0.30},
    "blk26_pos_d0.150": {26: 0.15},
    "blk27_neg_d0.250": {27: -0.25},
    "blk09_pos_d0.450": {9: 0.45},          # control: a middle block, expected NOT family-coherent
    "combo": {16: 0.20, 20: 0.30, 23: -0.20, 27: -0.10},
}
SETTINGS = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0",
            "denoise": "1.0", "width": "1024", "height": "1280"}


def vec(d):
    v = [0.0] * 34
    for k, x in d.items():
        v[k] = x
    return ",".join(f"{x:.3f}" for x in v) if d else ""


def make_plan():
    assert all(SUBJECTS.values()), "a styles prompt did not start with the cartoon prefix"
    rows = [{"row": 0, "prompt_id": "REPRO_C3_fox", "family": "", "subject": "fox", "seed": "2718281", "cond": "baseline",
             "vectors_override": "", "prompt_text": _styles["C3_fox"], **SETTINGS,
             "output_prefix": "REPRO_C3_fox_baseline_krea2_seed2718281",
             "expected_filename": "REPRO_C3_fox_baseline_krea2_seed2718281_00001_.png"}]
    for fam, prefix in FAMILIES.items():
        for subj, text in SUBJECTS.items():
            pid = f"{fam}_{subj}"
            for seed in SEEDS:
                for arm, d in ARMS.items():
                    op = f"{pid}_{arm}_krea2_seed{seed}"
                    rows.append({"row": len(rows), "prompt_id": pid, "family": fam, "subject": subj, "seed": seed,
                                 "cond": arm, "vectors_override": vec(d), "prompt_text": f"{prefix} {text}", **SETTINGS,
                                 "output_prefix": op, "expected_filename": f"{op}_00001_.png"})
    assert len(rows) == 1 + 3 * 6 * 2 * 8, len(rows)
    assert rows[0]["prompt_text"] == f"{FAMILIES['F1cartoon']} {SUBJECTS['fox']}"
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[1])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))
    for fam in FAMILIES:
        print(f"[{fam}_fisherman] {FAMILIES[fam]} {SUBJECTS['fisherman']}")


def _wf(r):
    r = dict(r); r["output_prefix"] = r["output_prefix"]
    wf = workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(first):
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    rows = rows[:first] if first else rows
    n = 0
    for r in rows:
        if (IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{COMFY}/prompt", data=json.dumps({"prompt": _wf(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10).read()
        n += 1
    print("queued", n, "of", len(rows))


def repro():
    import numpy as np
    from PIL import Image
    new = IMG_ROOT / FOLDER / "REPRO_C3_fox_baseline_krea2_seed2718281_00001_.png"
    ref = IMG_ROOT / "benchmark_single_blocks_styles" / "renders" / "C3_fox_baseline_krea2_seed2718281_00001_.png"
    a = np.asarray(Image.open(new).convert("RGB"), dtype=np.int16); b = np.asarray(Image.open(ref).convert("RGB"), dtype=np.int16)
    mx = int(np.abs(a - b).max()) if a.shape == b.shape else -1
    print("REPRO", "PASS" if mx == 0 else "FAIL", "max abs diff", mx)


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    d = IMG_ROOT / FOLDER
    miss = [r["expected_filename"] for r in rows if not (d / r["expected_filename"]).exists()]
    dup = [f for f in os.listdir(d) if "_00002_" in f]
    print("expected", len(rows), "missing", len(miss), miss[:5], "duplicates", len(dup))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for f in ("plan", "queue", "repro", "count"):
        ap.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.repro: repro()
    if a.count: count()
