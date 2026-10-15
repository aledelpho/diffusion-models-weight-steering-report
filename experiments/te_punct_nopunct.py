"""C78 exploration - Continuous unpunctuated stream of words (no commas, periods, semicolons, or BREAK).
Requested by Alessandro on 2026-10-15.
3 prompts x 8 seeds = 24 renders.
Prefix: EXTRA_nopunct_{prompt_id}_krea2_seed{seed}
"""
import argparse, csv, json, re, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_punct_nopunct_plan.csv"
FOLDER = "benchmark_te_punct"
SEEDS8 = ["2645751", "3316624", "3605551", "4123105", "1618033", "3141592", "2718281", "1234567"]

BUILT = {
    "P1_three_styles": ["a samurai drawn as a flat 2D cartoon", "a robot rendered as low-poly 3D",
                        "both sitting at a wooden table", "inside a photorealistic old pub"],
    "P2_held_clothes": ["a man wearing a plain white t-shirt", "holding a red leather jacket in his left hand",
                        "holding a blue wool cap in his right hand", "grey background"],
}

SET = {
    "sampler": "euler_ancestral",
    "scheduler": "simple",
    "steps": "9",
    "cfg": "1.0",
    "denoise": "1.0",
    "width": "1024",
    "height": "1280",
}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def clean_text_nopunct(text):
    # Remove commas, periods, semicolons, colons, newlines, and collapse spaces
    t = re.sub(r"[,.;:\n\r]+", " ", text)
    return " ".join(t.split())


def make_plan():
    d1_raw = next(r["prompt_text"] for r in rd(DATA / "te_characters_plan.csv") if r["char"] == "D1_dwarf_paladin")
    prompts = {
        "D1_dwarf_paladin": clean_text_nopunct(d1_raw),
        "P1_three_styles": " ".join(BUILT["P1_three_styles"]),
        "P2_held_clothes": " ".join(BUILT["P2_held_clothes"]),
    }

    rows = []
    for pid, ptext in prompts.items():
        for s in SEEDS8:
            prefix = f"EXTRA_nopunct_{pid}_krea2_seed{s}"
            rows.append({
                "row": len(rows),
                "prompt_id": pid,
                "version": "nopunct",
                "prompt_text": ptext,
                "seed": s,
                "output_prefix": prefix,
                "expected_filename": f"{prefix}_00001_.png",
                **SET,
            })
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("plan rows:", len(rows))
    for pid, t in prompts.items():
        print(f"[{pid}] -> {t[:80]}...")


def workflow(r):
    wf = TP.workflow({**r, "te_granular_json": "", "vectors_override": ""})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue():
    n = 0
    for r in rd(PLAN):
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(
            f"{c47.COMFY}/prompt",
            data=json.dumps({"prompt": workflow(r)}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "count"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.plan:
        make_plan()
    if a.queue:
        queue()
    if a.count:
        count()
