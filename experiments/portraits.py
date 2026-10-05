"""Portrait atlas (phase A, exploratory) and portrait preset test (phase C, C52).
Written by Claude, 2026-10-05. Pre-registration of phase C: docs/prereg_portrait_preset.md.

Phase A — every single block, both signs, at the v4 doses, on four calibration characters:
  python experiments/portraits.py --plan               # data/portraits_atlas_plan.csv (457 rows)
  python experiments/portraits.py --queue --first 1    # the REPRO row only
  python experiments/portraits.py --repro              # REPRO must equal the existing prompt-family baseline
  python experiments/portraits.py --queue              # the rest (skips files that exist)
  python experiments/portraits.py --count              # 457 files expected

Output: Text2Img/benchmark_portraits/renders/{char}_{cond}_krea2_seed{seed}_00001_.png
Workflow: blk23_colorful.workflow (the Tuner node only on rows with a vector).
Phase C — the frozen preset (presets/portrait_preset_alessandro.json, commit 4da5117) on all seven
characters, four new seeds, baseline and preset:
  python experiments/portraits.py --plan-c             # data/portraits_preset_plan.csv (57 rows)
  python experiments/portraits.py --queue-c --first 1  # the REPRO row only
  python experiments/portraits.py --repro-c            # REPRO must equal the phase A baseline
  python experiments/portraits.py --queue-c            # the rest
  python experiments/portraits.py --count-c            # 57 files expected
Output: Text2Img/benchmark_portraits/phase_c/{char}_{cond}_krea2_seed{seed}_00001_.png
"""
import argparse, csv, json, os, urllib.request
from pathlib import Path
from blk23_colorful import workflow, COMFY

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "data" / "portraits_atlas_plan.csv"
IMG_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img")
if not IMG_ROOT.exists():
    IMG_ROOT = Path(os.path.expanduser("~/mnt"))
FOLDER = "benchmark_portraits/renders"

HEAD = "Western comics style, close-up portrait, frontal view."
TAIL = "white background, simple background."
# Calibration characters (phase A). Texts as given by Alessandro on 2026-10-05.
CALIBRATION = {
    "D1_dwarf_paladin": "female paladin mountain dwarf, middle-aged, resolute stern expression, thick braided copper hair pinned back, dark brown eyes, a battle-scarred wide nose, polished steel gorget over a navy blue gambeson, high brass collar, a vertical scar running through one eyebrow.",
    "E2_elf_rogue": "non-binary rogue wood elf, young adult, smug lopsided smirk, undercut asymmetrical raven hair, sharp amber eyes, prominent cheekbones, dark forest green hooded leather cowl, brass buckles, high-collared charcoal tunic, a single dangling feather earring.",
    "O4_halforc_fighter": "female fighter half-orc, young adult, fierce defiant snarl, shorn faded undercut with a tight black warrior knot, piercing pale grey eyes, lower tusks jutting past chiseled lips, oxidized bronze scale-mail collar over a burgundy quilted jack, fresh dirt smudges across the bridge of the nose.",
    "G5_gnome_wizard": "male wizard forest gnome, elderly, wide-eyed manic curiosity, swept-back pointed white eyebrows and bristling pointed goatee, vivid turquoise eyes magnified behind round brass-rimmed spectacles, plum purple velvet scholar robes, stiff embroidered gold filigree collar, faintly glowing arcane chalk dust on cheekbones.",
}
# Held-out characters (phase C only). Never rendered before the preset is frozen.
# T7: "jellow" corrected to "yellow" (2026-10-05, before any render).
HELD_OUT = {
    "H3_halfling_druid": "male druid lightfoot halfling, elderly, serene contemplative expression, unruly white curls and bushy mutton chops, warm hazel eyes framed by deep crow's feet, a button nose, coarse woven ochre wool poncho, woven vine neckpiece, small dried sprigs tucked behind rounded ears.",
    "R6_dragonborn_cleric": "female cleric bronze dragonborn, middle-aged, calm dignified gaze, blunt horned crests swept backward over metallic bronze-scaled brow, slit-pupil golden eyes, blunt draconic snout, ivory ceremonial stole draped over an ornate teal mantle, heavy iron holy symbol resting at the throat collar.",
    "T7_tiefling_bard": "male bard tiefling, old, annoyed expression, short curling horns swept flat against cropped silver hair, heavy-lidded violet eyes narrowed in judgment, a sharply hooked nose, yellow fancy jacket, red scarf, faint smoke curling from one nostril.",
}
SEEDS_A = ["2236067", "1732050"]                         # new to the project
SEEDS_C = ["2645751", "3316624", "3605551", "4123105"]   # reserved for phase C, new to the project
SETTINGS = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0",
            "denoise": "1.0", "width": "1024", "height": "1280"}


def text(body: str) -> str:
    return f"{HEAD}\n{body} {TAIL}"


def v4_doses() -> dict:
    """The per-block doses of the v4 bench, read from its committed plan (not retyped)."""
    d = {}
    for r in csv.DictReader(open(REPO / "data" / "single_blocks_v4_plan.csv", encoding="utf-8-sig")):
        if r["block_idx"] and r["prompt_id"] == "P1_crown_topdown":
            d[(int(r["block_idx"]), r["sign"])] = float(r["dose"])
    assert len(d) == 56, len(d)
    return d


def vec(slot: int, v: float) -> str:
    x = [0.0] * 34
    x[slot] = v
    return ",".join(f"{a:.3f}" for a in x)


def make_plan():
    ref = next(r for r in csv.DictReader(open(REPO / "data" / "prompt_family_plan.csv", encoding="utf-8"))
               if r["prompt_id"] == "F1cartoon_fox" and r["seed"] == "5772156" and r["cond"] == "baseline")
    rows = [{"row": 0, "char": "REPRO_F1cartoon_fox", "seed": "5772156", "cond": "baseline", "block": "", "sign": "",
             "dose": "0.000", "vectors_override": "", "prompt_text": ref["prompt_text"], **SETTINGS,
             "output_prefix": "REPRO_F1cartoon_fox_baseline_krea2_seed5772156",
             "expected_filename": "REPRO_F1cartoon_fox_baseline_krea2_seed5772156_00001_.png"}]
    doses = v4_doses()
    for ch, body in CALIBRATION.items():
        for seed in SEEDS_A:
            conds = [("baseline", "", "", 0.0, "")]
            for b in range(28):
                for s in ("neg", "pos"):
                    d = doses[(b, s)]
                    conds.append((f"blk{b:02d}_{s}_d{d:.3f}", b, s, d, vec(b, d if s == "pos" else -d)))
            for cond, b, s, d, vo in conds:
                op = f"{ch}_{cond}_krea2_seed{seed}"
                rows.append({"row": len(rows), "char": ch, "seed": seed, "cond": cond, "block": b, "sign": s,
                             "dose": f"{d:.3f}", "vectors_override": vo, "prompt_text": text(body), **SETTINGS,
                             "output_prefix": op, "expected_filename": f"{op}_00001_.png"})
    assert len(rows) == 1 + 4 * 2 * 57, len(rows)
    assert not set(SEEDS_A) & set(SEEDS_C)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))
    print("[D1_dwarf_paladin]", text(CALIBRATION["D1_dwarf_paladin"]))


def _wf(r, folder=None):
    r = dict(r)
    wf = workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{folder or FOLDER}/{r['output_prefix']}"
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
    new = IMG_ROOT / FOLDER / "REPRO_F1cartoon_fox_baseline_krea2_seed5772156_00001_.png"
    ref = IMG_ROOT / "benchmark_prompt_family" / "F1cartoon_fox_baseline_krea2_seed5772156_00001_.png"
    a = np.asarray(Image.open(new).convert("RGB"), dtype=np.int16); b = np.asarray(Image.open(ref).convert("RGB"), dtype=np.int16)
    mx = int(np.abs(a - b).max()) if a.shape == b.shape else -1
    print("REPRO", "PASS" if mx == 0 else "FAIL", "max abs diff", mx)


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    d = IMG_ROOT / FOLDER
    miss = [r["expected_filename"] for r in rows if not (d / r["expected_filename"]).exists()]
    dup = [f for f in os.listdir(d) if "_00002_" in f] if d.exists() else []
    print("expected", len(rows), "missing", len(miss), miss[:5], "duplicates", len(dup))



# ----------------------------------------------------------------- phase C
PLAN_C = REPO / "data" / "portraits_preset_plan.csv"
FOLDER_C = "benchmark_portraits/phase_c"
PRESET = REPO / "presets" / "portrait_preset_alessandro.json"


def preset_vector() -> str:
    v = json.load(open(PRESET, encoding="utf-8"))["vectors_override"]
    assert len(v) == 34 and any(v)
    return ",".join(f"{a:.3f}" for a in v)


def make_plan_c():
    ch0, s0 = "D1_dwarf_paladin", SEEDS_A[0]
    rows = [{"row": 0, "char": f"REPRO_{ch0}", "set": "", "seed": s0, "cond": "baseline", "vectors_override": "",
             "prompt_text": text(CALIBRATION[ch0]), **SETTINGS,
             "output_prefix": f"REPRO_{ch0}_baseline_krea2_seed{s0}",
             "expected_filename": f"REPRO_{ch0}_baseline_krea2_seed{s0}_00001_.png"}]
    vp = preset_vector()
    for group, chars in (("calibration", CALIBRATION), ("held_out", HELD_OUT)):
        for ch, body in chars.items():
            for seed in SEEDS_C:
                for cond, vo in (("baseline", ""), ("preset", vp)):
                    op = f"{ch}_{cond}_krea2_seed{seed}"
                    rows.append({"row": len(rows), "char": ch, "set": group, "seed": seed, "cond": cond,
                                 "vectors_override": vo, "prompt_text": text(body), **SETTINGS,
                                 "output_prefix": op, "expected_filename": f"{op}_00001_.png"})
    assert len(rows) == 1 + 7 * 4 * 2, len(rows)
    with open(PLAN_C, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("phase C plan rows:", len(rows), "| preset", vp)


def queue_c(first):
    rows = list(csv.DictReader(open(PLAN_C, encoding="utf-8")))
    rows = rows[:first] if first else rows
    n = 0
    for r in rows:
        if (IMG_ROOT / FOLDER_C / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{COMFY}/prompt", data=json.dumps({"prompt": _wf(r, FOLDER_C)}).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10).read()
        n += 1
    print("queued", n, "of", len(rows))


def repro_c():
    import numpy as np
    from PIL import Image
    ch0, s0 = "D1_dwarf_paladin", SEEDS_A[0]
    new = IMG_ROOT / FOLDER_C / f"REPRO_{ch0}_baseline_krea2_seed{s0}_00001_.png"
    ref = IMG_ROOT / FOLDER / f"{ch0}_baseline_krea2_seed{s0}_00001_.png"
    a = np.asarray(Image.open(new).convert("RGB"), dtype=np.int16); b = np.asarray(Image.open(ref).convert("RGB"), dtype=np.int16)
    mx = int(np.abs(a - b).max()) if a.shape == b.shape else -1
    print("REPRO", "PASS" if mx == 0 else "FAIL", "max abs diff", mx)


def count_c():
    rows = list(csv.DictReader(open(PLAN_C, encoding="utf-8")))
    d = IMG_ROOT / FOLDER_C
    miss = [r["expected_filename"] for r in rows if not (d / r["expected_filename"]).exists()]
    dup = [f for f in os.listdir(d) if "_00002_" in f] if d.exists() else []
    print("expected", len(rows), "missing", len(miss), miss[:5], "duplicates", len(dup))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for f in ("plan", "queue", "repro", "count", "plan-c", "queue-c", "repro-c", "count-c"):
        ap.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.repro: repro()
    if a.count: count()
    if a.plan_c: make_plan_c()
    if a.queue_c: queue_c(a.first)
    if a.repro_c: repro_c()
    if a.count_c: count_c()
