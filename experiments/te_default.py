"""C72 - what does Krea-2 draw when the style words are missing, what does each word draw alone, and do random pushes
of the conditioning, as large as a text-encoder edit, also send the picture to anime? (docs/prereg_te_default.md)
Written 2026-10-12, before any C72 render. Renders authorised by Alessandro on 2026-10-12.

  python te_default.py --plan            # data/te_default_plan.csv
  python te_default.py --queue --first 4 # the four gate renders
  python te_default.py --gate            # zero push = plain render, pixel for pixel; real push close to the edit's render
  python te_default.py --queue           # the rest
  python te_default.py --count
  python te_default.py --selftest

Block A: the elf in five word orders without the three style clauses (2 seeds) and the empty prompt (4 seeds).
Block B: each of the 36 clauses of the elf prompt alone, plus 7 extra words, at 4 seeds.
Block C: random pushes of the conditioning (tools/comfyui_krea2_condpush), matched tap by tap to the real push of
L05, L06 and L28 MLP doubled: permuted / shared / token, five orders, two seeds. No weight is edited in block C.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP
import te_conditioning as T
import te_regions as RG

DATA = HERE.parent / "data"
PLAN = DATA / "te_default_plan.csv"
FOLDER = "benchmark_te_default"
ORDERS = RG.ORDERS
STYLE = ["realistic western comics style", "bold ink outlines", "hatched shadows"]
SEEDS_AC = ["3141592", "1234567"]
SEEDS_B = ["3141592", "1234567", "1618033", "2718281"]
EXTRA_WORDS = ["dwarf", "female dwarf", "female paladin mountain dwarf", "elf", "female elf", "uniform", "brawler"]
PUSH_EDITS = ["L05_mlp_p1.00", "L06_mlp_p1.00", "L28_mlp_p1.00"]
VARIANTS = ["permuted", "shared", "token"]
NOISE_SEED = 7
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0", "width": "1024", "height": "1280"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def texts():
    return {r["prompt_id"]: r["prompt_text"] for r in rd(DATA / "te_conditioning_plan.csv") if r["set"] == "order" and r["cond"] == "baseline"}


def drop_style(text):
    """Remove the three style clauses (comma-separated, inside one sentence); drop a sentence left empty."""
    out = []
    for sent in text.split(". "):
        end = sent.endswith(".")
        body = sent[:-1] if end else sent
        keep = [c for c in body.split(", ") if c.strip() not in STYLE]
        if keep:
            out.append(", ".join(keep) + ("." if end else ""))
    t = ". ".join(out)
    if text.endswith(".") and not t.endswith("."):
        t += "."
    assert not any(s in t for s in STYLE), t
    return t


def clauses():
    r = [x for x in rd(DATA / "te_bridge_plan.csv") if x["prompt_id"] == ORDERS[0] and x["cond"] == "baseline"][0]
    return json.loads(r["unit_texts"])


def make_plan():
    tx = texts(); rows = []
    def add(block, pid, cond, text, seed, **kw):
        prefix = f"{pid}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "block": block, "prompt_id": pid, "cond": cond, "prompt_text": text, "seed": seed,
                     "push_edit": kw.get("edit", ""), "variant": kw.get("variant", ""), "noise_seed": kw.get("ns", ""),
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    add("gate", ORDERS[0], "push_zero", tx[ORDERS[0]], "3141592", edit=PUSH_EDITS[0], variant="zero", ns=NOISE_SEED)
    for e in PUSH_EDITS:
        add("gate", ORDERS[0], f"{e}_real", tx[ORDERS[0]], "3141592", edit=e, variant="real", ns=NOISE_SEED)
    for s in SEEDS_AC:
        for v in ORDERS:
            add("A", v, "nostyle", drop_style(tx[v]), s)
    for s in SEEDS_B:
        add("A", "EMPTY", "empty", "", s)
    for e in PUSH_EDITS:
        for var in VARIANTS:
            for s in SEEDS_AC:
                for v in ORDERS:
                    add("C", v, f"{e}_{var}", tx[v], s, edit=e, variant=var, ns=NOISE_SEED)
    words = clauses() + [w for w in EXTRA_WORDS if w not in clauses()]
    for i, w in enumerate(words):
        for s in SEEDS_B:
            add("B", f"W{i:02d}", "word", w, s)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("plan rows:", len(rows), dict(Counter(r["block"] for r in rows)))


def workflow(r):
    wf = TP.workflow({**r, "te_granular_json": "", "vectors_override": ""})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["variant"]:
        wf["93"] = {"class_type": "Krea2ConditioningPush", "inputs": {
            "conditioning": ["40", 0], "baseline_path": str(T.out_path("order", r["prompt_id"], "baseline")),
            "edit_path": str(RG.out_path("order", r["prompt_id"], r["push_edit"])), "variant": r["variant"],
            "noise_seed": int(r["noise_seed"])}}
        wf["42"]["inputs"]["positive"] = ["93", 0]
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
    g = [r for r in rd(PLAN) if r["block"] == "gate"]
    base = _im(c47.IMG_ROOT / "benchmark_prompt_order" / f"{ORDERS[0]}_baseline_krea2_seed3141592_00001_.png")
    ok = True
    z = _im(c47.IMG_ROOT / FOLDER / g[0]["expected_filename"])
    dz = int(np.abs(z - base).max()); print("zero push vs plain render: max abs diff", dz); ok &= dz == 0
    for r in g[1:]:
        e = r["push_edit"]
        ref = _im(c47.IMG_ROOT / "benchmark_te_characters" / f"{ORDERS[0]}_{e}_krea2_seed3141592_00001_.png")
        new = _im(c47.IMG_ROOT / FOLDER / r["expected_filename"])
        a, b = float(np.abs(new - ref).mean()), float(np.abs(base - ref).mean())
        print(f"real push {e}: mean abs diff to the edit's render {a:.2f}, plain render to the edit's render {b:.2f}, ratio {a / b:.3f}")
        ok &= a <= 0.25 * b
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def selftest():
    tx = texts()
    for v in ORDERS:
        t = drop_style(tx[v]); assert len(t) < len(tx[v]) and "comics" not in t
    print(drop_style(tx[ORDERS[0]])[:120]); print(drop_style(tx[ORDERS[2]])[-160:])
    print("selftest ok")


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
