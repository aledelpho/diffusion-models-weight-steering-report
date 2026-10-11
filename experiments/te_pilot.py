"""C64 — text-encoder pilot: what each layer of Qwen3-VL-4B does to a Krea-2 picture (docs/plan_te_pilot.md).
Written 2026-10-11, before any render. Exploratory; one prompt, one seed. Renders authorised by Alessandro.

  python te_pilot.py --plan            # data/te_pilot_plan.csv
  python te_pilot.py --queue --checks  # the 7 control renders only
  python te_pilot.py --check           # gates; nothing else runs unless they pass
  python te_pilot.py --queue           # everything else
  python te_pilot.py --count           # expected N missing 0
  python te_pilot.py --measure         # data/te_pilot_measures.csv (after the renders)
  python te_pilot.py --sheets          # contact sheets in Text2Img/benchmark_te_pilot/sheets

Text-encoder edits go through ArthemyKrea2CLIPTuner (Real Value, granular_json, x(1+d)) placed between the
ResetPatcher's CLIP and CLIPTextEncode. Language layer L, attention = self_attn.{q,k,v,o}_proj, MLP =
mlp.{gate,up,down}_proj. Krea-2 taps hidden_states[2,5,...,35] (comfy/text_encoders/krea2.py), and comfy's
tap k is the input of layer k: layer 35 is never read (null control), layers 0-34 are.
The DiT-side text adapter (txtfusion, slots 28-33 of the Model Tuner vector) is swept too.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "te_pilot_plan.csv"
FOLDER = "benchmark_te_pilot"
PID, SEED = "P1_elfbrawler", "1618033"
DOSES = [-1.0, -0.35, -0.1, 0.1, 0.35, 1.0]
ATTN = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj"]
MLP = ["mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]
TXT_SLOTS = ["txtfusion_layerwise0", "txtfusion_layerwise1", "txtfusion_refiner0", "txtfusion_refiner1",
             "txtfusion_projector", "txtmlp"]


def gj_te(layer, mats, d):
    return json.dumps({f"layers.{layer}.{m}.weight": d for m in mats})


def vo_slot(slot, d):
    v = ["0.0"] * 34; v[28 + slot] = f"{d:.3f}"; return ",".join(v)


def tag(d):
    return f"{'p' if d > 0 else 'm'}{abs(d):.2f}"


def f(cond, folder=FOLDER, pid=PID, seed=SEED):
    return c47.IMG_ROOT / folder / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"


def make_plan():
    elf = next(r for r in csv.DictReader(open(DATA / "comic_form_plan.csv", encoding="utf-8")) if r["prompt_id"] == PID)
    keys = ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")
    rows = []
    def add(cond, te_json, vo, phase, unit, part, dose):
        prefix = f"{PID}_{cond}_krea2_seed{SEED}"
        rows.append({"row": len(rows), "phase": phase, "unit": unit, "part": part, "dose": dose, "prompt_id": PID, "seed": SEED,
                     "cond": cond, "te_granular_json": te_json, "vectors_override": vo, "prompt_text": elf["prompt_text"],
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **{k: elf[k] for k in keys}})
    # controls
    add("CHK_repro_baseline", "", "", "check", "", "", 0)
    add("CHK_null_L35_both_p1.00", gj_te(35, ATTN + MLP, 1.0), "", "check", "L35", "both", 1.0)
    add("CHK_null_visual4_p1.00", json.dumps({f"visual.blocks.4.{m}.weight": 1.0 for m in ("attn.qkv", "attn.proj", "mlp.linear_fc1", "mlp.linear_fc2")}),
        "", "check", "V4", "both", 1.0)
    add("CHK_active_L02_mlp_p1.00", gj_te(2, MLP, 1.0), "", "check", "L02", "mlp", 1.0)
    for L in (5, 17, 29):
        add(f"CHK_qk_L{L:02d}_p1.00", gj_te(L, ATTN[:2], 1.0), "", "check", f"L{L:02d}", "qk", 1.0)
    # main: every read layer, attention and MLP apart, six doses
    for L in range(35):
        for part, mats in (("attn", ATTN), ("mlp", MLP)):
            for d in DOSES:
                add(f"L{L:02d}_{part}_{tag(d)}", gj_te(L, mats, d), "", "main", f"L{L:02d}", part, d)
    # the DiT-side text adapter
    for s, name in enumerate(TXT_SLOTS):
        for d in DOSES:
            add(f"{name}_{tag(d)}", "", vo_slot(s, d), "main", name, "slot", d)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["te_granular_json"]:
        wf["51"] = {"class_type": "ArthemyKrea2CLIPTuner", "inputs": {
            "clip": ["37", 1], "mode": "Real Value", "vectors_override": "", "granular_json": r["te_granular_json"],
            "Embedding": 0.0, "Layer_1": 0.0, "Layer_2": 0.0, "Layer_3": 0.0, "Layer_4": 0.0, "Layer_5": 0.0,
            "Layer_6": 0.0, "Layer_7": 0.0}}
        wf["40"]["inputs"]["clip"] = ["51", 0]
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


def _im(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def check():
    base = _im(f("baseline", "benchmark_comic_form"))
    d = lambda c: int(np.abs(_im(f(c)) - base).max())
    res = {"repro": d("CHK_repro_baseline"), "null_L35": d("CHK_null_L35_both_p1.00"), "null_visual": d("CHK_null_visual4_p1.00"),
           "active_L02": d("CHK_active_L02_mlp_p1.00")}
    qk = {L: d(f"CHK_qk_L{L:02d}_p1.00") for L in (5, 17, 29)}
    for k, v in res.items():
        print(f"{k}: max abs diff against the C60 baseline = {v}")
    print("q+k only (QK-norm prediction, reported, not a gate):", qk)
    ok = res["repro"] == 0 and res["active_L02"] > 0
    print("CHECK", "PASS" if ok else "FAIL - stop",
          "| structure:", "layer 35 unread as predicted" if res["null_L35"] == 0 else "layer 35 CHANGES the image (prediction wrong)",
          "/", "visual tower inert" if res["null_visual"] == 0 else "visual tower CHANGES the image")


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
