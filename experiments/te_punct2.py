"""C78 amendment 3 - punctuation on complex four-character prompts (Alessandro's 07456 'totem' and 07459 'prison
break'), pilot only. Written 2026-10-15, before any of these renders. Pilot authorised by Alessandro on 2026-10-15.

  python te_punct2.py --plan     # reads the two prompts verbatim from the PNG metadata, writes data/te_punct2_plan.csv
  python te_punct2.py --queue --block pilot2
  python te_punct2.py --count

Plain Krea-2 (no preset, no 5D tuner), the C78 sampling (euler_ancestral, simple, 9 steps, cfg 1.0), 1024x1536.
"""
import argparse, csv, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_punct as P

DATA = HERE.parent / "data"
PLAN = DATA / "te_punct2_plan.csv"
SOURCES = {"P3_totem": "ComfyUI_07456_.png", "P4_prison": "ComfyUI_07459_.png"}


def source_text(png):
    from PIL import Image
    d = json.loads(Image.open(c47.IMG_ROOT / png).info["prompt"])
    return d["93"]["inputs"]["value"]


def make_plan():
    rows = []
    for pid, png in SOURCES.items():
        text = source_text(png)
        for s in P.SEEDS8:
            prefix = f"{pid}_original_krea2_seed{s}"
            rows.append({"row": len(rows), "block": "pilot2", "prompt_id": pid, "version": "original", "source_png": png,
                         "prompt_text": text, "seed": s, "output_prefix": prefix,
                         "expected_filename": f"{prefix}_00001_.png", **{**P.SET, "height": "1536"}})
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "count"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--block", default="pilot2")
    a = ap.parse_args()
    P.PLAN = PLAN
    if a.plan: make_plan()
    if a.queue: P.queue(a.block)
    if a.count: P.count()
