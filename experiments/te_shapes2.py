"""C100 - the push's shape with very different prompts and heavier edits (docs/prereg_te_shapes2.md).
Written 2026-10-18 with the pre-registration, before any encode. Reuses C93's measures and shape rules.

  python te_shapes2.py --selftest
  python te_shapes2.py --run      # GPU, ComfyUI venv: data/te_shapes2_trajectories.csv, Text2Img/benchmark_te_shapes2/*.npz
  python te_shapes2.py --rules    # numpy: data/te_shapes2_tests.csv
"""
import argparse, csv, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_shapes as TS

DATA = HERE.parent / "data"
OUT = DATA / "te_shapes2_trajectories.csv"
TESTS = DATA / "te_shapes2_tests.csv"
PROMPTS = {"D1_dwarf_paladin": "te_characters_plan.csv", "S1_rally": "single_blocks_atlas_plan.csv",
           "P2_lotuscanoe": "single_blocks_v3_plan.csv", "P5_comic_panels": "single_blocks_v4_plan.csv",
           "C4_stilllife": "single_blocks_styles_plan.csv", "LN": "colour_object_sweep_plan_0.050.csv"}
EDITS = {"L06_mlp": [(6, "mlp")], "L14_mlp": [(14, "mlp")], "L28_mlp": [(28, "mlp")],
         "L06_block": [(6, "mlp"), (6, "attn")], "L06+L14+L28_mlp": [(6, "mlp"), (14, "mlp"), (28, "mlp")]}
POS = TS.POS + [4.0, 5.0, 7.0, 10.0]
NEG = TS.NEG + [1.5, 2.0, 3.0]
TAPS = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]


def texts():
    t = {}
    for p, f in PROMPTS.items():
        for r in csv.DictReader(open(DATA / f, encoding="utf-8")):
            k = r.get("char") or r.get("prompt_id")
            if k == p and r.get("prompt_text"):
                t[p] = r["prompt_text"]; break
    assert set(t) == set(PROMPTS), set(PROMPTS) - set(t)
    return t


def gj(edit, d):
    out = {}
    for L, half in EDITS[edit]:
        mats = ("gate", "up", "down") if half == "mlp" else ("q", "k", "v", "o")
        pre = f"layers.{L}.mlp." if half == "mlp" else f"layers.{L}.self_attn."
        out.update({f"{pre}{m}_proj.weight": d for m in mats})
    return out


def first_layer(edit):
    return min(L for L, _ in EDITS[edit])


def finite_prefix(A, doses):
    """Amendment 1 (2026-10-18): a dose whose conditioning leaves the fp16 range (inf after the probe's fp16 cast) ends
    the trajectory; the trajectory is measured on the doses before it, and the dropped doses are reported."""
    k = 0
    while k < len(A) and np.isfinite(A[k]).all():
        k += 1
    return A[:k], k, [float(d) for d in list(doses)[k:]]


def run():
    import torch
    import te_punct_encoder as TPE
    import te_layer0_encoder as TLE
    import blk23_colorful as c47
    import te_conditioning as TC
    base = TPE.gate()                                                     # gate (a): bit-identical elf baseline
    tx0 = texts()["D1_dwarf_paladin"]                                     # gate (b): as C93
    c0, _, _ = TPE.encode_taps(base, tx0)
    c1, _, _ = TPE.encode_taps(TLE.apply_te_edit(base, gj("L06_mlp", 1.0)), tx0)
    rel = np.linalg.norm(c1 - c0, axis=-1) / (np.linalg.norm(c0, axis=-1) + 1e-6)
    ref = np.load(TC.out_path("chars", "D1_dwarf_paladin", "L06_mlp_p1.00"))["rel"]
    err = float(np.abs(rel - ref).max()); print(f"GATE b L06 MLP 1.00 dwarf vs C67: max rel err {err:.6f} (limit {2 * TC.FP16_FLOOR:.6f})")
    if err > 2 * TC.FP16_FLOOR:
        sys.exit("GATE b FAIL - stop")
    layers = TS._layers(base)
    outdir = c47.IMG_ROOT / "benchmark_te_shapes2"; outdir.mkdir(parents=True, exist_ok=True)
    tx = texts(); rows = []
    for p, text in tx.items():
        cb, _, _ = TPE.encode_taps(base, text)
        scale = np.linalg.norm(cb, axis=-1).mean(0)
        push = lambda c: (c - cb) / scale[None, :, None]
        cap = {}
        def grab(key):
            def h(mod, args, out):
                cap[key] = (out[0] if isinstance(out, tuple) else out).detach().float().clone()
            return h
        hs = [layers[L].mlp.register_forward_hook(grab(("base", L))) for L in (6, 14, 28)]
        TPE.encode_taps(base, text)
        for h in hs:
            h.remove()
        hz = layers[6].mlp.register_forward_hook(lambda m, a, o: o + 0 * o)  # gate (c): zero-length control
        cz, _, _ = TPE.encode_taps(base, text); hz.remove()
        if float(np.abs(cz - cb).max()) != 0.0:
            sys.exit(f"GATE c FAIL on {p} - stop")
        for edit in EDITS:
            single = len(EDITS[edit]) == 1 and EDITS[edit][0][1] == "mlp"
            L0 = first_layer(edit)
            for sign, doses in (("p", POS), ("m", NEG)):
                Ps, Pc, lens = [], [], []
                for d in doses:
                    clip_e = TLE.apply_te_edit(base, gj(edit, d if sign == "p" else -d))
                    if single and sign == "p":
                        h = layers[L0].mlp.register_forward_hook(grab(("edit", L0)))
                        ce, _, _ = TPE.encode_taps(clip_e, text); h.remove()
                        lens.append(torch.linalg.vector_norm(cap[("edit", L0)] - cap[("base", L0)], dim=-1))
                    else:
                        ce, _, _ = TPE.encode_taps(clip_e, text)
                    Ps.append(push(ce))
                if single and sign == "p":
                    g = torch.Generator(device="cpu").manual_seed(9393)
                    R = torch.randn(cap[("base", L0)].shape, generator=g); R = R / torch.linalg.vector_norm(R, dim=-1, keepdim=True)
                    for n in lens:
                        add = R.to(n.device) * n.unsqueeze(-1)
                        h = layers[L0].mlp.register_forward_hook(lambda m, a, o, add=add: o + add.to(o.dtype).to(o.device))
                        cc, _, _ = TPE.encode_taps(base, text); h.remove()
                        Pc.append(push(cc))
                for kind, PP in (("edit", Ps), ("control", Pc)):
                    if not PP:
                        continue
                    A = np.stack(PP).mean(1)                                # (n doses, 12, 2560), mean over tokens
                    np.savez_compressed(outdir / f"{p}_{edit}_{sign}_{kind}.npz", dmean=A.astype(np.float16), doses=np.array(doses))
                    base_row = {"prompt": p, "edit": edit, "sign": sign, "kind": kind}
                    A, used, over = finite_prefix(A, doses)                 # amendment 1: drop doses that leave the fp16 range
                    base_row = {**base_row, "n_doses": used, "overflow": " ".join(f"{d:g}" for d in over)}
                    if over:
                        print("overflow", base_row, flush=True)
                    lim = 3.0 if sign == "p" else 1.0
                    k3 = min(sum(1 for d in doses if d <= lim), len(A))
                    for rng, sub in (("full", A), ("upto_C93", A[:k3])):
                        m = TS.measures(sub.reshape(len(sub), -1))
                        rows.append({**base_row, "level": "whole", "range": rng, "unit": "", **m, "shapes": "+".join(TS.shapes(m))})
                    for t in range(12):
                        if TAPS[t] > L0:
                            m = TS.measures(A[:, t, :])
                            rows.append({**base_row, "level": "tap", "range": "full", "unit": t, **m, "shapes": "+".join(TS.shapes(m))})
                print("done", p, edit, sign, len(rows))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("wrote", OUT, len(rows))


def rules(rows):
    S = lambda r: set(r["shapes"].split("+"))
    W = [r for r in rows if r["level"] == "whole" and r["range"] == "full"]
    out = []
    single = ("L06_mlp", "L14_mlp", "L28_mlp")
    me = [S(r) for r in W if r["kind"] == "edit" and r["sign"] == "p" and r["edit"] in single]
    mc = [S(r) for r in W if r["kind"] == "control"]
    for sh in ("straight", "spiral", "wave", "clip", "accelerating", "other"):
        ne, nc = sum(sh in s for s in me), sum(sh in s for s in mc)
        v = "belongs to the edits" if ne >= 10 and nc <= 4 else ("belongs to the network" if ne >= 10 and nc >= 10 else "")
        out.append({"test": f"Rule 1 {sh}: edits vs controls", "value": f"{ne} of {len(me)} vs {nc} of {len(mc)}", "verdict": v})
    th = defaultdict(list)
    for r in W:
        if r["kind"] == "edit":
            th[(r["edit"], r["sign"])].append(float(r["theta"]))
    rngs = {k: max(v) - min(v) for k, v in th.items()}
    small, big = sum(x <= 15 for x in rngs.values()), sum(x >= 30 for x in rngs.values())
    v2 = ("a property of the edit" if small >= 2 / 3 * len(rngs) else ("depends on the prompt" if big >= len(rngs) / 2 else "mixed"))
    out.append({"test": "Rule 2 range of total turn over the 6 prompts, per edit x sign",
                "value": " ".join(f"{e}/{s}:{x:.0f}" for (e, s), x in sorted(rngs.items())) + f"; <=15 in {small}/{len(rngs)}, >=30 in {big}/{len(rngs)}",
                "verdict": v2})
    pairs = defaultdict(dict)
    for r in rows:
        if r["level"] == "whole" and r["kind"] == "edit":
            pairs[(r["prompt"], r["edit"], r["sign"])][r["range"]] = S(r)
    ch = sum(v.get("full") != v.get("upto_C93") for v in pairs.values())
    clip = sum("clip" in v.get("full", set()) and "clip" not in v.get("upto_C93", set()) for v in pairs.values())
    out.append({"test": "Rule 3 heavy doses: label changes when doses beyond 3 / -1 are added (reported)", "value": f"{ch} of {len(pairs)}; new clips {clip}", "verdict": ""})
    for e in EDITS:
        t = [float(r["theta"]) for r in W if r["kind"] == "edit" and r["edit"] == e and r["sign"] == "p"]
        out.append({"test": f"median total turn, {e}, positive (reported)", "value": f"{statistics.median(t):.1f} deg (min {min(t):.0f}, max {max(t):.0f})", "verdict": ""})
    ov = sorted({f"{r['prompt']}/{r['edit']}/{r['sign']}/{r['kind']}" + " from " + r["overflow"].split()[0] for r in rows if r.get("overflow")})
    out.append({"test": "Amendment 1 trajectories cut where the conditioning leaves the fp16 range (reported)", "value": "; ".join(ov) or "none", "verdict": ""})
    return out


def selftest():
    rows = []
    for i, p in enumerate(PROMPTS):
        for e in EDITS:
            for s in ("p", "m"):
                rows.append({"prompt": p, "edit": e, "sign": s, "kind": "edit", "level": "whole", "range": "full", "theta": 60 + i, "shapes": "other"})
                rows.append({"prompt": p, "edit": e, "sign": s, "kind": "edit", "level": "whole", "range": "upto_C93", "theta": 60 + i, "shapes": "other"})
                if e in ("L06_mlp", "L14_mlp", "L28_mlp") and s == "p":
                    rows.append({"prompt": p, "edit": e, "sign": s, "kind": "control", "level": "whole", "range": "full", "theta": 70, "shapes": "other"})
    out = rules(rows)
    d = {o["test"].split(":")[0]: o for o in out}
    assert d["Rule 1 other"]["verdict"] == "belongs to the network", d
    assert [o for o in out if o["test"].startswith("Rule 2")][0]["verdict"] == "a property of the edit"
    assert set(texts()) == set(PROMPTS) and gj("L06_block", 1.0) and len(gj("L06+L14+L28_mlp", 1.0)) == 9
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "run", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.run: run()
    if a.rules:
        out = rules(list(csv.DictReader(open(OUT, encoding="utf-8"))))
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
