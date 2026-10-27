"""Benchmark_te_tree_2: rerun tree edits with half-strength for confetti perts and prompt:
'a photo of a tall torted tree with large leaves'.
"""
import argparse, csv, gc, json, math, os, statistics, sys, time, urllib.request
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import te_depth_control as T
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "te_tree_2_plan.csv"
METRICS = DATA / "te_tree_2_saturation.csv"
FOLDER = "Benchmark_te_tree_2"
PROMPT = "a photo of a tall torted tree with large leaves"
SUBJECTS = ["T1_tree"]

PRESETS = {
    "P01": {"7": 0.3, "9": -0.3, "11": 0.3, "17": 0.3},
    "P06": {"9": 0.3, "11": -0.3, "20": -0.3, "22": 0.3},
    "P10": {"14": 0.3, "15": 0.3, "29": 0.3, "30": -0.3}
}
EDITS = ["E05", "E06", "E14", "E26", "E28"]
ORDER = ["E05", "E06", "E14", "E26", "E28", "P01", "P06", "P10"]
PERTS = {**{e: ("edit", int(e[1:])) for e in EDITS}, **{n: ("preset", None) for n in PRESETS}}

# Option 1: halve the collapsing perts, keep non-collapsing
ADJUSTED_STRENGTHS = {
    "E05": 0.28285,
    "E06": 0.40000,
    "E14": 0.40000,
    "E26": 0.53033,
    "E28": 1.06066,
    "P01": 0.70710,
    "P06": 0.84090,
    "P10": 1.00000,
}

TEST_SEEDS = ["2645751", "3316624", "1414213", "1732050", "2236067", "3141592", "1234567", "5772156"]
SET = T.SET
TX = {"T1_tree": PROMPT}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def tag(n, x):
    return f"{n}_{x:g}".replace(".", "p")


def cpath(p, t):
    return T.img_root() / FOLDER / "conds" / f"{p}_{t}.pt"


def fname(p, t, s):
    return f"{p}_{t}_krea2_seed{s}_00001_.png"


def row(block, p, s, t, variant="file"):
    prefix = f"{p}_{t}_krea2_seed{s}"
    return {
        "block": block,
        "char": p,
        "seed": s,
        "cond": t,
        "variant": variant,
        "push_path": str(cpath(p, t)) if variant == "file" else "",
        "noise_seed": 7,
        "taps": "",
        "te_granular_json": "{}",
        "prompt_text": TX[p],
        "output_prefix": prefix,
        "expected_filename": f"{prefix}_00001_.png",
        **SET
    }


def write(path, rows):
    for i, r in enumerate(rows):
        r["row"] = i
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["row"] + [k for k in rows[0] if k != "row"])
        w.writeheader()
        w.writerows(rows)


class Enc:
    def __init__(self):
        import torch
        import te_punct_encoder as TPE, te_layer0_encoder as TLE, te_shapes as TS
        self.torch, self.TLE = torch, TLE
        self.base = TPE.gate()
        self.layers = TS._layers(self.base)
        self.cap = {}

    def raw(self, clip, text):
        tokens = clip.tokenize(text)
        return clip.encode_from_tokens(tokens, return_pooled=False, return_dict=True)["cond"].detach().cpu().clone()

    def cond(self, p, n, x):
        kind, L = PERTS[n] if n in PERTS else (None, None)
        text = TX[p]
        if n == "C0":
            return self.raw(self.base, text)
        if kind == "edit":
            return self.raw(self.TLE.apply_te_edit(self.base, T.gj(L, x)), text)
        if kind == "preset":
            g = {}
            for Ls, d in PRESETS[n].items():
                g.update(T.gj(int(Ls), d * x))
            return self.raw(self.TLE.apply_te_edit(self.base, g), text)
        raise ValueError(f"Unknown pert {n}")

    def save(self, p, n, x):
        t = "C0" if n == "C0" else tag(n, x)
        cp = cpath(p, t)
        if not cp.exists():
            c = self.cond(p, n, x)
            if not bool(self.torch.isfinite(c.float()).all()):
                return None
            self.torch.save(c, cp)
        return t


def free():
    gc.collect()
    try:
        import torch
        torch.cuda.empty_cache()
    except Exception:
        pass


def make_plan():
    (T.img_root() / FOLDER / "conds").mkdir(parents=True, exist_ok=True)
    E = Enc()
    rows = []
    p = SUBJECTS[0]
    # Gate render
    rows.append(row("gate", p, TEST_SEEDS[0], "TEXT", variant="text"))
    # Save C0
    c0_tag = E.save(p, "C0", 0)
    print("Saved conditioning:", c0_tag)
    # Save adjusted perts
    cond_tags = {}
    for n in ORDER:
        x = ADJUSTED_STRENGTHS[n]
        t = E.save(p, n, x)
        cond_tags[n] = t
        print(f"Saved conditioning: {n} (strength={x}) -> {t}")
    del E
    free()

    for s in TEST_SEEDS:
        rows.append(row("main", p, s, "C0"))
        for n in ORDER:
            rows.append(row("main", p, s, cond_tags[n]))

    write(PLAN, rows)
    print(f"Plan created with {len(rows)} rows at {PLAN}")
    return rows


def post(r):
    if r.get("variant") == "text":
        wf = c47.workflow({**r, "vectors_override": ""})
    else:
        wf = T.workflow({**r})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    req = urllib.request.Request(
        f"{c47.COMFY}/prompt",
        data=json.dumps({"prompt": wf}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        json.loads(resp.read())


def queue_all():
    rows = rd(PLAN)
    n = 0
    target_dir = T.img_root() / FOLDER
    for r in rows:
        if (target_dir / r["expected_filename"]).exists():
            continue
        post(r)
        n += 1
    print(f"Queued {n} tasks to ComfyUI")
    return n


def wait_all(timeout_sec=7200):
    rows = rd(PLAN)
    target_dir = T.img_root() / FOLDER
    t0 = time.time()
    last_count = -1
    while True:
        existing = [r for r in rows if (target_dir / r["expected_filename"]).exists()]
        curr_count = len(existing)
        if curr_count != last_count:
            print(f"Progress: {curr_count}/{len(rows)} rendered ({len(rows) - curr_count} remaining)", flush=True)
            last_count = curr_count
        if curr_count == len(rows):
            print("All renders completed!", flush=True)
            break
        if time.time() - t0 > timeout_sec:
            sys.exit(f"TIMEOUT waiting for renders after {timeout_sec}s")
        time.sleep(20)


def gate_check():
    p, s = SUBJECTS[0], TEST_SEEDS[0]
    R = T.img_root() / FOLDER
    a, b = R / fname(p, "C0", s), R / fname(p, "TEXT", s)
    if not (a.exists() and b.exists()):
        print(f"GATE missing files: a={a.exists()}, b={b.exists()}")
        return False
    arr_a = np.asarray(Image.open(a).convert("RGB"), dtype=np.int16)
    arr_b = np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)
    diff = int(np.abs(arr_a - arr_b).max())
    print(f"GATE CHECK: max abs diff = {diff} -> {'PASS' if diff == 0 else 'FAIL'}")
    return diff == 0


def analyze_saturation():
    target_dir = T.img_root() / FOLDER
    pngs = sorted([p for p in target_dir.glob("*.png") if not p.name.endswith("_stitch.png")])
    print(f"Analyzing saturation for {len(pngs)} images in {target_dir}...")
    
    records = []
    for p in pngs:
        img = Image.open(p).convert("HSV")
        # In PIL HSV, H is 0-255, S is 0-255, V is 0-255
        h, s, v = img.split()
        s_arr = np.array(s, dtype=np.float32)
        mean_s = float(np.mean(s_arr))
        std_s = float(np.std(s_arr))
        p95_s = float(np.percentile(s_arr, 95))
        high_ratio = float(np.mean(s_arr > 240))
        is_confetti = (mean_s > 150) or (high_ratio > 0.20)
        records.append({
            "filename": p.name,
            "mean_s": round(mean_s, 2),
            "std_s": round(std_s, 2),
            "p95_s": round(p95_s, 2),
            "high_sat_ratio": round(high_ratio, 4),
            "is_confetti": int(is_confetti)
        })

    with open(METRICS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    means = [r["mean_s"] for r in records]
    confetti_count = sum(r["is_confetti"] for r in records)
    print("\n=== SATURATION ANALYSIS SUMMARY ===")
    print(f"Total images analyzed: {len(records)}")
    print(f"Mean saturation: min={min(means):.1f}, mean={statistics.mean(means):.1f}, max={max(means):.1f}")
    print(f"Confetti images detected (>150 mean S or >20% pixels S>240): {confetti_count} / {len(records)}")
    print(f"Metrics saved to {METRICS}")
    return confetti_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", action="store_true", help="Generate conditionings and plan")
    parser.add_argument("--queue", action="store_true", help="Queue all renders to ComfyUI")
    parser.add_argument("--wait", action="store_true", help="Wait for all renders to finish")
    parser.add_argument("--gate", action="store_true", help="Check gate bit-exact match")
    parser.add_argument("--saturation", action="store_true", help="Analyze saturation across all images")
    parser.add_argument("--finish", action="store_true", help="Wait for queue to finish, check gate, analyze saturation")
    parser.add_argument("--all", action="store_true", help="Run full pipeline: plan, queue, wait, gate, saturation")
    args = parser.parse_args()

    if args.plan:
        make_plan()
    elif args.queue:
        queue_all()
    elif args.wait:
        wait_all()
    elif args.gate:
        gate_check()
    elif args.saturation:
        analyze_saturation()
    elif args.finish:
        wait_all()
        gate_check()
        analyze_saturation()
    elif args.all:
        make_plan()
        queue_all()
        wait_all()
        gate_check()
        analyze_saturation()
    else:
        parser.print_help()
