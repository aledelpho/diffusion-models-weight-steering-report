"""C73 - does each character fall back to its own genre when the style words are removed, and do strong text-encoder
edits send a character toward its own fallback? (docs/prereg_te_fallback.md). Written 2026-10-13, before any C73
render. Renders authorised by Alessandro on 2026-10-13.

  python te_fallback.py --plan             # data/te_fallback_plan.csv
  python te_fallback.py --queue --first 1  # the gate render
  python te_fallback.py --gate             # must equal the C52 baseline pixel for pixel
  python te_fallback.py --queue
  python te_fallback.py --count
  python te_fallback.py --selftest

The seven C65 characters (C52 frame "Western comics style, close-up portrait, frontal view."), with the clause
"Western comics style" removed and nothing else changed, at the four C52 phase-C seeds, plain model and encoder.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_fallback_plan.csv"
FOLDER = "benchmark_te_fallback"
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter", "G5_gnome_wizard", "H3_halfling_druid",
         "R6_dragonborn_cleric", "T7_tiefling_bard"]
SEEDS = ["2645751", "3316624", "3605551", "4123105"]
STYLE = "Western comics style"
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0", "width": "1024", "height": "1280"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def texts():
    t = {}
    for r in rd(DATA / "te_characters_plan.csv"):
        if r["char"] in CHARS and r["char"] not in t:
            t[r["char"]] = r["prompt_text"]
    return t


def drop_style(text):
    head, rest = text.split("\n", 1)
    parts = [p for p in head.rstrip(".").split(", ") if p.strip() != STYLE]
    assert len(parts) == len(head.rstrip(".").split(", ")) - 1, head
    return ", ".join(parts) + ".\n" + rest


def base_path(ch, seed):
    return c47.IMG_ROOT / "benchmark_portraits" / "phase_c" / f"{ch}_baseline_krea2_seed{seed}_00001_.png"


def make_plan():
    tx = texts(); rows = []
    def add(block, ch, cond, text, seed):
        prefix = f"{ch}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "block": block, "char": ch, "cond": cond, "prompt_text": text, "seed": seed,
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    add("gate", CHARS[0], "withstyle_repro", tx[CHARS[0]], SEEDS[0])
    for s in SEEDS:
        for ch in CHARS:
            add("A", ch, "nostyle", drop_style(tx[ch]), s)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = TP.workflow({**r, "te_granular_json": "", "vectors_override": ""})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(first):
    n = 0
    for r in rd(PLAN)[: first or None]:
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def _im(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def gate():
    r = rd(PLAN)[0]
    d = int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(base_path(r["char"], r["seed"]))).max())
    print("re-rendered C52 baseline vs existing: max abs diff", d)
    print("GATE", "PASS" if d == 0 else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def selftest():
    tx = texts()
    for ch in CHARS:
        t = drop_style(tx[ch]); assert "comics" not in t.lower() and t.startswith("close-up portrait, frontal view.\n"), t[:80]
    print(repr(drop_style(tx[CHARS[0]])[:90])); print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "gate", "count", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.gate: gate()
    if a.count: count()
    if a.selftest: selftest()
