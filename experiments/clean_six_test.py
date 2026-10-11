"""C63 — are the six middle-block edits that came out clean in C60 really free? (docs/prereg_clean_six.md)
Written 2026-10-11, before any render. Renders authorised by Alessandro.

  python clean_six_test.py --plan            # data/clean_six_plan.csv: 1 check + 12 baselines + 96 edits
  python clean_six_test.py --queue --checks  # the check only
  python clean_six_test.py --check           # must equal the C60 file to the pixel
  python clean_six_test.py --queue           # everything else
  python clean_six_test.py --count           # expected 109 missing 0
  (after the renders, separately committed: --page; after the labels: --tally)

CLEAN set = the six C60 FORM edits with 0 of 9 pairs damaged; CONTROL = two C60 SURFACE edits (positive control).
Dose 0.35, Real Value, granular_json. Four illustration prompts never used in C59 or C60, three new seeds.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "clean_six_plan.csv"
KEY = DATA / "clean_six_eye_key.csv"
LABELS = DATA / "clean_six_eye_alessandro.csv"
FOLDER = "benchmark_clean_six"
DOSE = 0.35
SEEDS = ["1325719", "2193847", "3047581"]
PROMPTS = {"C3_fox": "blk23_colorful_plan.csv", "F1cartoon_lighthouse": "prompt_family_plan.csv",
           "E5_childrensbook": "single_blocks_styles_plan.csv", "P5_comic_panels": "single_blocks_conservative_plan.csv"}
CLEAN = [(2, "whole", "neg"), (8, "mlp", "pos"), (8, "whole", "pos"), (9, "attn", "pos"), (9, "whole", "pos"), (18, "mlp", "neg")]
CONTROL = [(22, "mlp", "pos"), (27, "mlp", "pos")]
ATTN = ["attn.wq", "attn.wk", "attn.wv", "attn.gate", "attn.wo"]; MLP = ["mlp.gate", "mlp.up", "mlp.down"]
MATS = {"attn": ATTN, "mlp": MLP, "whole": ATTN + MLP}
ZERO = ",".join(["0.0"] * 34)


def gj(b, part, sign):
    d = DOSE if sign == "pos" else -DOSE
    return json.dumps({f"blocks.{b}.{m}.weight": d for m in MATS[part]})


def cond(b, part, sign):
    return f"blk{b:02d}_{part}_{sign}_d{DOSE:.3f}"


def f(pid, seed, c, folder=FOLDER):
    return c47.IMG_ROOT / folder / f"{pid}_{c}_krea2_seed{seed}_00001_.png"


def make_plan():
    rows = []
    def add(pid, text, s, seed, c, g, phase, group):
        prefix = f"{pid}_{c}_krea2_seed{seed}"
        rows.append({"row": len(rows), "phase": phase, "group": group, "prompt_id": pid, "seed": seed, "cond": c,
                     "vectors_override": ZERO if g else "", "granular_json": g, "prompt_text": text, "output_prefix": prefix,
                     "expected_filename": f"{prefix}_00001_.png", **s})
    keys = ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")
    elf = next(r for r in csv.DictReader(open(DATA / "comic_form_plan.csv", encoding="utf-8")) if r["prompt_id"] == "P1_elfbrawler")
    add("P1_elfbrawler", elf["prompt_text"], {k: elf[k] for k in keys}, "1618033", "CHK_" + cond(8, "mlp", "pos"), gj(8, "mlp", "pos"), "check", "check")
    base = {pid: next(r for r in csv.DictReader(open(DATA / fn, encoding="utf-8")) if (r.get("prompt_id") or r.get("prompt")) == pid)
            for pid, fn in PROMPTS.items()}
    for seed in SEEDS:
        for pid in PROMPTS:
            b = base[pid]; s = {k: b[k] for k in keys}
            add(pid, b["prompt_text"], s, seed, "baseline", "", "main", "baseline")
            for grp, lst in (("clean", CLEAN), ("control", CONTROL)):
                for e in lst:
                    add(pid, b["prompt_text"], s, seed, cond(*e), gj(*e), "main", grp)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["granular_json"]:
        wf["50"]["inputs"]["granular_json"] = r["granular_json"]
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
    from PIL import Image
    im = lambda p: np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
    c = cond(8, "mlp", "pos")
    a = int(np.abs(im(f("P1_elfbrawler", "1618033", "CHK_" + c)) - im(f("P1_elfbrawler", "1618033", c, "benchmark_comic_form"))).max())
    print(f"REPRO C60 elf, seed 1618033, block 8 MLP +0.35: max abs diff {a}")
    print("CHECK", "PASS" if a == 0 else "FAIL - stop")


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "checks", "check", "count"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.checks)
    if a.check: check()
    if a.count: count()
