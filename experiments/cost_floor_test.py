"""C61 — does every push cost fine texture? An attempt to overturn the general wording of notebook page 05.
Pre-registration: docs/prereg_cost_floor.md. Written 2026-10-07, before any render.

  python cost_floor_test.py --plan            # data/cost_floor_plan.csv: 1 check + 16 baselines + 896 edits
  python cost_floor_test.py --queue --checks  # the check only
  python cost_floor_test.py --check           # must be identical to the pixel to page 05's own render
  python cost_floor_test.py --queue           # everything else (baselines first, then seed by seed)
  python cost_floor_test.py --count           # expected 913 missing 0
  (after the renders: --measure; the eye page and --tally are separate, committed before any label)

Every whole block 0-27 at +-0.200 (page 05's dose and path: vectors_override, Real Value), four prompts
(page 05's P01 and P02, two photographic), four new seeds. HF = std(gray - GaussianBlur(gray, (0,0), 1.5)), as
page 05 and docs/noise_floor_provenance_2026-09-23.md.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "cost_floor_plan.csv"
FOLDER = "benchmark_cost_floor"
DOSE = 0.200
SEEDS = ["1259921", "1732050", "2645751", "3162277"]
PROMPTS = {"P01": "blk16_ladder_plan.csv", "P02": "blk16_ladder_plan.csv",
           "S1_rally": "single_blocks_atlas_plan.csv", "P4_selfie": "blk23_colorful_plan.csv"}
FAMILY = {"P01": "comic", "P02": "comic", "S1_rally": "photo", "P4_selfie": "photo"}


def vo(block, d):
    v = ["0.000"] * 34; v[block] = f"{d:.3f}"; return ",".join(v)


def f(pid, seed, cond):
    return c47.IMG_ROOT / FOLDER / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"


def make_plan():
    base = {}
    for pid, fn in PROMPTS.items():
        base[pid] = next(r for r in csv.DictReader(open(DATA / fn, encoding="utf-8")) if r["prompt_id"] == pid)
    rows = []
    def add(pid, seed, cond, v, phase):
        b = base[pid]; prefix = f"{pid}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "phase": phase, "prompt_id": pid, "family": FAMILY[pid], "seed": seed, "cond": cond,
                     "vectors_override": v, "granular_json": "", "prompt_text": b["prompt_text"], "output_prefix": prefix,
                     "expected_filename": f"{prefix}_00001_.png",
                     **{k: b[k] for k in ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")}})
    add("P01", "42", "CHK_page05_blk09pos_0.200", vo(9, DOSE), "check")
    for seed in SEEDS:
        for pid in PROMPTS:
            add(pid, seed, "baseline", "", "main")
    for seed in SEEDS:
        for pid in PROMPTS:
            for blk in range(28):
                for sign, d in (("pos", DOSE), ("neg", -DOSE)):
                    add(pid, seed, f"blk{blk:02d}_{sign}_d{DOSE:.3f}", vo(blk, d), "main")
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(checks_only):
    n = 0
    for r in csv.DictReader(open(PLAN, encoding="utf-8")):
        if (checks_only and r["phase"] != "check") or (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def check():
    import numpy as np
    from PIL import Image
    im = lambda p: np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
    ref = c47.IMG_ROOT / "benchmark_profondita" / "renders" / "P01_blk09pos_0.200_krea2_seed42_00001_.png"
    a = int(np.abs(im(f("P01", "42", "CHK_page05_blk09pos_0.200")) - im(ref)).max())
    print(f"REPRO page 05 render (P01, seed 42, block 9, +0.200): max abs diff {a}")
    print("CHECK", "PASS" if a == 0 else "FAIL - stop")


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5])


def hf(p):
    import cv2, numpy as np
    g = cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2GRAY).astype(np.float64)
    return float((g - cv2.GaussianBlur(g, (0, 0), 1.5)).std())


def measure():
    """data/cost_floor_measures.csv: per prompt, seed, block: r+, r-, common mode c, swing."""
    import numpy as np
    out = []
    for seed in SEEDS:
        for pid in PROMPTS:
            hb = hf(f(pid, seed, "baseline"))
            for blk in range(28):
                rp = hf(f(pid, seed, f"blk{blk:02d}_pos_d{DOSE:.3f}")) / hb
                rn = hf(f(pid, seed, f"blk{blk:02d}_neg_d{DOSE:.3f}")) / hb
                out.append({"prompt": pid, "family": FAMILY[pid], "seed": seed, "block": blk, "r_pos": round(rp, 5),
                            "r_neg": round(rn, 5), "common_mode": round(float(np.sqrt(rp * rn)), 5), "swing": round(rp / rn, 5)})
    with open(DATA / "cost_floor_measures.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(len(out), "block-cells measured")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "checks", "check", "count", "measure"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.checks)
    if a.check: check()
    if a.count: count()
    if a.measure: measure()
