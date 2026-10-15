"""C78 - does the punctuation between parts of a prompt (comma, period, semicolon) keep concepts apart?
(docs/prereg_te_punct.md). Written 2026-10-15, before any C78 render. Renders authorised by Alessandro on 2026-10-15.

  python te_punct.py --plan               # data/te_punct_plan.csv
  python te_punct.py --queue --block gate # 2 renders that must equal existing pictures
  python te_punct.py --gate
  python te_punct.py --queue --block pilot
  python te_punct.py --queue --block main     # only after Claude's go (pilot rule)
  python te_punct.py --queue --block natural
  python te_punct.py --count
  python te_punct.py --selftest
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_punct_plan.csv"
FOLDER = "benchmark_te_punct"
SEPS = {"comma": ", ", "period": ". ", "semicolon": "; "}
SEEDS8 = ["2645751", "3316624", "3605551", "4123105", "1618033", "3141592", "2718281", "1234567"]
SEEDS_D1 = ["2645751", "3316624", "3605551", "4123105"]
SEEDS_ELF = ["1618033", "3141592", "2718281", "1234567"]
BUILT = {
    "P1_three_styles": ["a samurai drawn as a flat 2D cartoon", "a robot rendered as low-poly 3D",
                        "both sitting at a wooden table", "inside a photorealistic old pub"],
    "P2_held_clothes": ["a man wearing a plain white t-shirt", "holding a red leather jacket in his left hand",
                        "holding a blue wool cap in his right hand", "grey background"],
}
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
       "width": "1024", "height": "1280"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def natural_texts():
    d1 = next(r["prompt_text"] for r in rd(DATA / "te_characters_plan.csv") if r["char"] == "D1_dwarf_paladin")
    elf = next(r["prompt_text"] for r in rd(DATA / "te_pilot_plan.csv") if r["cond"] == "CHK_repro_baseline")
    return {"D1_dwarf_paladin": d1, "P1_elfbrawler": elf}


def swap_commas(text, sep):
    """Natural prompts: every ', ' becomes the separator; existing periods and words stay."""
    return text if sep == ", " else text.replace(", ", sep)


def make_plan():
    nat = natural_texts(); rows = []
    def add(block, pid, version, text, seed):
        prefix = f"{pid}_{version}_krea2_seed{seed}"
        rows.append({"row": len(rows), "block": block, "prompt_id": pid, "version": version, "prompt_text": text,
                     "seed": seed, "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    add("gate", "D1_dwarf_paladin", "comma", nat["D1_dwarf_paladin"], "2645751")
    add("gate", "P1_elfbrawler", "comma", nat["P1_elfbrawler"], "1618033")
    for pid, parts in BUILT.items():
        for s in SEEDS8:
            add("pilot", pid, "comma", SEPS["comma"].join(parts), s)
    for pid, parts in BUILT.items():
        for v in ("period", "semicolon"):
            for s in SEEDS8:
                add("main", pid, v, SEPS[v].join(parts), s)
    for v in ("period", "semicolon"):
        for s in SEEDS_D1:
            add("natural", "D1_dwarf_paladin", v, swap_commas(nat["D1_dwarf_paladin"], SEPS[v]), s)
    for v in ("comma", "period", "semicolon"):
        for s in SEEDS_ELF:
            if v == "comma" and s == "1618033":
                continue  # already the gate render
            add("natural", "P1_elfbrawler", v, swap_commas(nat["P1_elfbrawler"], SEPS[v]), s)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("plan rows:", len(rows), dict(Counter(r["block"] for r in rows)))


def workflow(r):
    wf = TP.workflow({**r, "te_granular_json": "", "vectors_override": ""})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(block):
    n = 0
    for r in rd(PLAN):
        if r["block"] != block or (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n, "block", block)


def _im(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def gate():
    old = {"D1_dwarf_paladin": c47.IMG_ROOT / "benchmark_portraits" / "phase_c" / "D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png",
           "P1_elfbrawler": c47.IMG_ROOT / "benchmark_te_pilot" / "P1_elfbrawler_CHK_repro_baseline_krea2_seed1618033_00001_.png"}
    ok = True
    for r in rd(PLAN):
        if r["block"] != "gate":
            continue
        d = int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(old[r["prompt_id"]])).max())
        print(r["prompt_id"], "re-render vs existing: max abs diff", d); ok &= d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def selftest():
    nat = natural_texts()
    for v, s in SEPS.items():
        t = swap_commas(nat["D1_dwarf_paladin"], s)
        o = nat["D1_dwarf_paladin"]; assert t.count(s) == o.count(s) + (o.count(", ") if v != "comma" else 0), v
        assert (", " in t) == (v == "comma"), v
    for pid, parts in BUILT.items():
        assert all("," not in p and "." not in p and ";" not in p for p in parts), pid
    print(repr(SEPS["period"].join(BUILT["P2_held_clothes"])))
    print(repr(swap_commas(nat["D1_dwarf_paladin"], "; ")[:120]))
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "gate", "count", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--block", default="")
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue(a.block)
    if a.gate: gate()
    if a.count: count()
    if a.selftest: selftest()
