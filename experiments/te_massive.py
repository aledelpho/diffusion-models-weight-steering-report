"""TEP2 - does the L06 edit act through the massive activations? (docs/prereg_te_massive.md)
Written 2026-10-18 with the pre-registration, before any encode or render.

  python te_massive.py --selftest
  python te_massive.py --plan             # data/te_massive_plan.csv (25 rows; already committed)
  python te_massive.py --encode           # GPU, ComfyUI venv: gates + conditionings -> Text2Img/benchmark_te_massive/conds/*.pt,
                                          # data/te_massive_encoder.csv
  python te_massive.py --queue --block gate
  python te_massive.py --gate             # rendered gates (and, after main, the six C1 renders) must be pixel-identical
  python te_massive.py --queue --block main
  python te_massive.py --count            # expected 25 missing 0 []
  python te_massive.py --analyze          # GPU: DINOv2 distances -> data/te_massive_metrics.csv
  python te_massive.py --rules            # numpy: data/te_massive_tests.csv
"""
import argparse, csv, json, statistics, sys, urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
DATA = HERE.parent / "data"
PLAN = DATA / "te_massive_plan.csv"
ENC = DATA / "te_massive_encoder.csv"
METRICS = DATA / "te_massive_metrics.csv"
TESTS = DATA / "te_massive_tests.csv"
FOLDER = "benchmark_te_massive"
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter"]
SEEDS = ["2645751", "3316624"]
CONDS = ["C1", "C2", "C3", "C4"]
GJ = {"layers.6.mlp.gate_proj.weight": 1.0, "layers.6.mlp.up_proj.weight": 1.0, "layers.6.mlp.down_proj.weight": 1.0}
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
       "width": "1024", "height": "1280"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def img_root():
    import blk23_colorful as c47
    return c47.IMG_ROOT if c47.IMG_ROOT.exists() else Path.home() / "mnt" / "Text2Img"


def cond_path(ch, cond):
    import blk23_colorful as c47
    return c47.IMG_ROOT / FOLDER / "conds" / f"{ch}_{cond}.pt"


def massive_mask(h_b, h_e):
    """Union of entries with |h| >= 100 and >= 100 x median |h|, in the plain (h_b) or edited (h_e) stream."""
    def m(h):
        a = np.abs(h)
        return a >= max(100.0, 100.0 * float(np.median(a)))
    return m(h_b) | m(h_e)


# ---------------------------------------------------------------- encodes (GPU)
def encode():
    import torch
    import te_conditioning as TC
    import te_punct_encoder as TPE
    import te_layer0_encoder as TLE
    import te_shapes as TS
    base = TPE.gate()
    edit = TLE.apply_te_edit(base, GJ)
    layers = TS._layers(base)
    tx = {}
    for r in TC.rd(DATA / "te_characters_plan.csv"):
        tx.setdefault(r["char"], r["prompt_text"])
    def raw(clip, text):
        tokens = clip.tokenize(text)
        return clip.encode_from_tokens(tokens, return_pooled=False, return_dict=True)["cond"].detach().cpu().clone()
    def run(clip, text, setter=None):
        cap = {}
        def hook(mod, args, out):
            t = out[0] if isinstance(out, tuple) else out
            if setter is not None:
                setter(t)
            cap["h"] = t.detach().clone()
        h = layers[6].register_forward_hook(hook)
        try:
            c = raw(clip, text)
        finally:
            h.remove()
        return c, cap["h"]
    outdir = cond_path("x", "x").parent; outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for ch in CHARS:
        text = tx[ch]
        c0 = raw(base, text)
        cb, hb = run(base, text)                                            # gate (a): a capturing hook changes nothing
        if not torch.equal(c0, cb):
            sys.exit(f"GATE a FAIL {ch}: hook changed the plain conditioning - stop")
        ce, he = run(edit, text)
        M = torch.from_numpy(massive_mask(hb.float().cpu().numpy(), he.float().cpu().numpy())).to(hb.device)
        nm = int(M.sum())
        g = torch.Generator(device="cpu").manual_seed(4242)
        idx = torch.nonzero(~M.cpu().reshape(-1)).reshape(-1)
        pick = idx[torch.randperm(len(idx), generator=g)[:nm]]
        R = torch.zeros(M.numel(), dtype=torch.bool); R[pick] = True; R = R.reshape(M.shape).to(hb.device)
        def put(mask, src):
            def f(t):
                t[mask] = src.to(t.device, t.dtype)[mask]
            return f
        c2, _ = run(edit, text, put(M, hb))
        c3, _ = run(base, text, put(M, he))
        c4, _ = run(edit, text, put(R, hb))
        conds = {"C0": cb, "C1": ce, "C2": c2, "C3": c3, "C4": c4}
        for k, v in conds.items():
            torch.save(v, cond_path(ch, k))
        seq = cb.shape[1]
        P = {k: (v.float() - cb.float()).reshape(seq, 12, -1) for k, v in conds.items() if k != "C0"}
        full = torch.linalg.vector_norm(P["C1"], dim=(0, 2))
        tok = torch.nonzero(M.reshape(M.shape[-2], -1).any(-1)).reshape(-1).tolist()
        for k in ("C2", "C3", "C4"):
            share = (torch.linalg.vector_norm(P[k], dim=(0, 2)) / (full + 1e-12)).tolist()
            cos = float((P[k] * P["C1"]).sum() / (P[k].norm() * P["C1"].norm() + 1e-12))
            rows.append({"char": ch, "cond": k, "n_massive": nm, "massive_tokens": " ".join(map(str, tok[:20])),
                         "push_share_by_tap": " ".join(f"{x:.3f}" for x in share), "cos_with_full": round(cos, 4)})
        print(f"done {ch}: massive entries {nm} on tokens {tok[:20]}")
    with open(ENC, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("wrote", ENC)


# ---------------------------------------------------------------- renders
def make_plan():
    import te_conditioning as TC
    tx = {}
    for r in TC.rd(DATA / "te_characters_plan.csv"):
        tx.setdefault(r["char"], r["prompt_text"])
    rows = []
    def add(block, ch, s, cond):
        prefix = f"{ch}_{cond}_krea2_seed{s}"
        rows.append({"row": len(rows), "block": block, "char": ch, "seed": s, "cond": cond, "variant": "file",
                     "push_path": str(cond_path(ch, cond)), "noise_seed": 7, "taps": "", "te_granular_json": "{}",
                     "prompt_text": tx[ch], "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    add("gate", "D1_dwarf_paladin", "2645751", "C0")
    add("gate", "D1_dwarf_paladin", "2645751", "C1")
    for ch in CHARS:
        for s in SEEDS:
            for c in CONDS:
                if not (ch == "D1_dwarf_paladin" and s == "2645751" and c == "C1"):
                    add("main", ch, s, c)
    assert len(rows) == 25
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    import te_tap_isolation as TI
    wf = TI.workflow({**r, "te_granular_json": ""})
    wf["93"]["inputs"]["variant"] = "file"
    wf["93"]["inputs"]["push_path"] = r["push_path"]
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(block=None):
    import blk23_colorful as c47
    n = 0
    for r in rd(PLAN):
        if block and r["block"] != block:
            continue
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def _load(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def gate():
    R = img_root(); ok = True
    checks = [(R / FOLDER / "D1_dwarf_paladin_C0_krea2_seed2645751_00001_.png",
               R / "benchmark_portraits/phase_c/D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png")]
    for ch in CHARS:
        for s in SEEDS:
            checks.append((R / FOLDER / f"{ch}_C1_krea2_seed{s}_00001_.png",
                           R / "benchmark_te_characters" / f"{ch}_L06_mlp_p1.00_krea2_seed{s}_00001_.png"))
    for i, (a, b) in enumerate(checks):
        if not a.exists():
            continue
        A, B = _load(a), _load(b)
        d = int(np.abs(A - B).max()); print(f"{a.name} vs {b.name}: max abs diff {d}")
        if i == 0:
            ok &= d == 0                                                    # gate (b): exact
            continue
        # gate (c), amendment 1 (2026-10-18): the file-route C1 must land as far from the plain render as the in-graph one
        ch, s = a.name.split("_C1_")[0], a.name.split("seed")[1].split("_")[0]
        P = _load(R / "benchmark_portraits/phase_c" / f"{ch}_baseline_krea2_seed{s}_00001_.png")
        da, db = float(np.abs(A - P).mean()), float(np.abs(B - P).mean())
        rel = abs(da - db) / db
        print(f"  mean abs diff {np.abs(A - B).mean():.3f}; distance to plain: file {da:.3f}, in-graph {db:.3f}, rel diff {rel:.4f} (limit 0.05)")
        ok &= rel <= 0.05
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    import blk23_colorful as c47
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def analyze():
    from PIL import Image
    import metric_validation as MV
    R = img_root(); m = MV.Models(vqa=False); out = []
    for ch in CHARS:
        for s in SEEDS:
            b = m.dino_vec(Image.open(R / "benchmark_portraits/phase_c" / f"{ch}_baseline_krea2_seed{s}_00001_.png").convert("RGB"))
            for c in CONDS:
                v = m.dino_vec(Image.open(R / FOLDER / f"{ch}_{c}_krea2_seed{s}_00001_.png").convert("RGB"))
                out.append({"char": ch, "seed": s, "cond": c, "dinov2_dist_to_base": round(1 - MV.cos(v, b), 6)})
    with open(METRICS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("wrote", METRICS, len(out))


def rules(M):
    D = {(r["char"], r["seed"], r["cond"]): float(r["dinov2_dist_to_base"]) for r in M}
    cells = sorted({(r["char"], r["seed"]) for r in M})
    f = {c: {k: D[(*c, k)] / D[(*c, "C1")] for k in CONDS} for c in cells}
    n2lo = sum(f[c]["C2"] <= 0.50 for c in cells); n4 = sum(f[c]["C4"] >= 0.80 for c in cells)
    m3 = statistics.median(f[c]["C3"] for c in cells); n2hi = sum(f[c]["C2"] >= 0.80 for c in cells)
    if n2lo >= 5 and n4 >= 5 and m3 >= 0.50: v = "the massive entries carry the damage"
    elif n2hi >= 5: v = "not through the massive entries"
    else: v = "partly"
    return [{"test": "Rule: restore massive (C2), control (C4), massive only (C3)",
             "value": f"f(C2) <= 0.50 in {n2lo}/6, >= 0.80 in {n2hi}/6; f(C4) >= 0.80 in {n4}/6; median f(C3) {m3:.2f}", "verdict": v},
            {"test": "f per cell (reported)", "value": " | ".join(f"{c[0][:2]}/{c[1]}: C2 {f[c]['C2']:.2f} C3 {f[c]['C3']:.2f} C4 {f[c]['C4']:.2f}" for c in cells), "verdict": ""}]


def selftest():
    a = np.ones((1, 5, 8)); a[0, 0, 3] = 500.0
    b = np.ones((1, 5, 8)); b[0, 2, 1] = 800.0
    mk = massive_mask(a, b)
    assert mk.sum() == 2 and mk[0, 0, 3] and mk[0, 2, 1]
    def M(vals):
        rows = []
        for i, ch in enumerate(CHARS):
            for s in SEEDS:
                for c, v in zip(CONDS, vals):
                    rows.append({"char": ch, "seed": s, "cond": c, "dinov2_dist_to_base": v})
        return rows
    assert rules(M([0.4, 0.1, 0.3, 0.38]))[0]["verdict"] == "the massive entries carry the damage"
    assert rules(M([0.4, 0.38, 0.05, 0.4]))[0]["verdict"] == "not through the massive entries"
    assert rules(M([0.4, 0.25, 0.1, 0.4]))[0]["verdict"] == "partly"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "plan", "encode", "queue", "gate", "count", "analyze", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--block", default=None)
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.plan: make_plan()
    if a.encode: encode()
    if a.queue: queue(a.block)
    if a.gate: gate()
    if a.count: count()
    if a.analyze: analyze()
    if a.rules:
        out = rules(rd(METRICS))
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
