"""C101 - the push's shape at every layer of the text encoder (docs/prereg_te_shapes_layers.md).
Written 2026-10-18 with the pre-registration, before any encode. Reuses C93's measures and shape labels, C100's doses.

  python te_shapes_layers.py --selftest
  python te_shapes_layers.py --run      # GPU, ComfyUI venv: data/te_shapes_layers_trajectories.csv, Text2Img/benchmark_te_shapes_layers/*.npz
  python te_shapes_layers.py --rules    # numpy: data/te_shapes_layers_tests.csv
"""
import argparse, csv, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_shapes as TS
import te_shapes2 as TS2

DATA = HERE.parent / "data"
OUT = DATA / "te_shapes_layers_trajectories.csv"
TESTS = DATA / "te_shapes_layers_tests.csv"
PROMPT = "D1_dwarf_paladin"
TAPS = TS2.TAPS
LAYERS = [L for L in range(36) if any(t > L for t in TAPS)]          # 0..34: an edit at 35 reaches no tap
HALVES = ("mlp", "attn")
POS, NEG = TS2.POS, TS2.NEG
SUB = "benchmark_te_shapes_layers"


def name(L, half):
    return f"L{L:02d}_{half}"


def gj(L, half, d):
    mats = ("gate", "up", "down") if half == "mlp" else ("q", "k", "v", "o")
    pre = f"layers.{L}.mlp." if half == "mlp" else f"layers.{L}.self_attn."
    return {f"{pre}{m}_proj.weight": d for m in mats}


def run():
    import torch
    import te_conditioning as TC
    import te_punct_encoder as TPE
    import te_layer0_encoder as TLE
    import blk23_colorful as c47
    base = TPE.gate()                                                     # gate (a)
    text = TS2.texts()[PROMPT]
    c0, _, _ = TPE.encode_taps(base, text)                                # gate (b), as C93
    c1, _, _ = TPE.encode_taps(TLE.apply_te_edit(base, gj(6, "mlp", 1.0)), text)
    rel = np.linalg.norm(c1 - c0, axis=-1) / (np.linalg.norm(c0, axis=-1) + 1e-6)
    ref = np.load(TC.out_path("chars", PROMPT, "L06_mlp_p1.00"))["rel"]
    err = float(np.abs(rel - ref).max()); print(f"GATE b L06 MLP 1.00 dwarf vs C67: max rel err {err:.6f} (limit {2 * TC.FP16_FLOOR:.6f})")
    if err > 2 * TC.FP16_FLOOR:
        sys.exit("GATE b FAIL - stop")
    layers = TS._layers(base)
    outdir = c47.IMG_ROOT / SUB; outdir.mkdir(parents=True, exist_ok=True)
    ref93 = c47.IMG_ROOT / "benchmark_te_shapes"
    cb, _, _ = TPE.encode_taps(base, text)
    scale = np.linalg.norm(cb, axis=-1).mean(0)
    push = lambda c: (c - cb) / scale[None, :, None]
    cap = {}
    def grab(key):
        def h(mod, args, out):
            cap[key] = (out[0] if isinstance(out, tuple) else out).detach().float().clone()
        return h
    hs = [layers[L].mlp.register_forward_hook(grab(("base", L))) for L in LAYERS]
    TPE.encode_taps(base, text)
    for h in hs:
        h.remove()
    hz = layers[6].mlp.register_forward_hook(lambda m, a, o: o + 0 * o)  # gate (c)
    cz, _, _ = TPE.encode_taps(base, text); hz.remove()
    if float(np.abs(cz - cb).max()) != 0.0:
        sys.exit("GATE c FAIL - stop")
    print("GATE c PASS")
    rows = []
    for half in HALVES:
        for L in LAYERS:
            for sign, doses in (("p", POS), ("m", NEG)):
                ctrl = half == "mlp" and sign == "p"
                Ps, Pc, lens = [], [], []
                for d in doses:
                    clip_e = TLE.apply_te_edit(base, gj(L, half, d if sign == "p" else -d))
                    if ctrl:
                        h = layers[L].mlp.register_forward_hook(grab(("edit", L)))
                        ce, _, _ = TPE.encode_taps(clip_e, text); h.remove()
                        lens.append(torch.linalg.vector_norm(cap[("edit", L)] - cap[("base", L)], dim=-1))
                    else:
                        ce, _, _ = TPE.encode_taps(clip_e, text)
                    Ps.append(push(ce))
                    del clip_e
                if ctrl:
                    g = torch.Generator(device="cpu").manual_seed(9393)
                    R = torch.randn(cap[("base", L)].shape, generator=g); R = R / torch.linalg.vector_norm(R, dim=-1, keepdim=True)
                    for n in lens:
                        add = R.to(n.device) * n.unsqueeze(-1)
                        h = layers[L].mlp.register_forward_hook(lambda m, a, o, add=add: o + add.to(o.dtype).to(o.device))
                        cc, _, _ = TPE.encode_taps(base, text); h.remove()
                        Pc.append(push(cc))
                for kind, PP in (("edit", Ps), ("control", Pc)):
                    if not PP:
                        continue
                    A = np.stack(PP).mean(1)                                # (n doses, 12, 2560), mean over tokens
                    A16 = A.astype(np.float16)
                    np.savez_compressed(outdir / f"{PROMPT}_{name(L, half)}_{sign}_{kind}.npz", dmean=A16, doses=np.array(doses))
                    f93 = ref93 / f"{PROMPT}_{name(L, half)}_{sign}_{kind}.npz"   # gate (d)
                    if f93.exists():
                        R93 = np.load(f93)["dmean"].astype(np.float64); k = len(R93)
                        e = float(np.linalg.norm(A16[:k].astype(np.float64) - R93) / np.linalg.norm(R93))
                        print(f"GATE d {name(L, half)} {sign} {kind} vs C93: rel err {e:.6f} (limit {2 * TC.FP16_FLOOR:.6f})")
                        if e > 2 * TC.FP16_FLOOR:
                            sys.exit("GATE d FAIL - stop")
                    base_row = {"layer": L, "half": half, "sign": sign, "kind": kind}
                    lim = 3.0 if sign == "p" else 1.0
                    k3 = sum(1 for d in doses if d <= lim)
                    for rng, sub in (("full", A), ("upto_C93", A[:k3])):
                        m = TS.measures(sub.reshape(len(sub), -1))
                        rows.append({**base_row, "level": "whole", "range": rng, "unit": "", **m, "shapes": "+".join(TS.shapes(m))})
                    for t in range(12):
                        if TAPS[t] > L:
                            m = TS.measures(A[:, t, :])
                            rows.append({**base_row, "level": "tap", "range": "full", "unit": t, **m, "shapes": "+".join(TS.shapes(m))})
                print("done", name(L, half), sign, len(rows), flush=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("wrote", OUT, len(rows))


def _rank(x):
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); r[o] = np.arange(len(x))
    for v in np.unique(x):                                                  # average ties
        i = x == v; r[i] = r[i].mean()
    return r


def spearman(a, b):
    ra, rb = _rank(a), _rank(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def rules(rows):
    W = [r for r in rows if r["level"] == "whole" and r["range"] == "full"]
    th = {(int(r["layer"]), r["half"], r["sign"], r["kind"]): float(r["theta"]) for r in W}
    lab = {(int(r["layer"]), r["half"], r["sign"], r["kind"]): r["shapes"] for r in W}
    out = []
    Ls = sorted({k[0] for k in th if k[1:] == ("mlp", "p", "edit")})
    te = [th[(L, "mlp", "p", "edit")] for L in Ls]
    rho = spearman(Ls, te)
    rng = np.random.default_rng(0)
    perm = [spearman(Ls, rng.permutation(te)) for _ in range(10000)]
    p = (1 + sum(abs(x) >= abs(rho) for x in perm)) / 10001
    way = "deeper bends less" if rho < 0 else "deeper bends more"
    v1 = f"depth orders the bend ({way})" if abs(rho) >= 0.5 and p < 0.01 else ("no order" if abs(rho) < 0.3 else "weak")
    out.append({"test": "Rule 1 Spearman layer vs total turn, MLP edits, positive", "value": f"rho {rho:+.3f}, p {p:.4f}, n {len(Ls)}", "verdict": v1})
    less = [L for L in Ls if (L, "mlp", "p", "control") in th and th[(L, "mlp", "p", "edit")] < th[(L, "mlp", "p", "control")]]
    nc = sum((L, "mlp", "p", "control") in th for L in Ls)
    v2 = "everywhere" if len(less) >= 28 else ("the opposite" if len(less) <= 7 else "depends on the layer")
    notless = [L for L in Ls if L not in less]
    out.append({"test": "Rule 2 layers where the edit bends less than its random control (MLP, positive)",
                "value": f"{len(less)} of {nc}; not less at layers {notless}", "verdict": v2})
    for kind in ("edit", "control"):
        c = Counter(s for (L, h, sg, k), v in lab.items() if h == "mlp" and sg == "p" and k == kind for s in v.split("+"))
        out.append({"test": f"Rule 3 shape counts over layers, MLP positive, {kind} (reported)", "value": dict(sorted(c.items())), "verdict": ""})
    for sh in ("spiral", "wave", "clip"):
        where = sorted(f"{name(L, h)}/{sg}/{k}" for (L, h, sg, k), v in lab.items() if sh in v.split("+"))
        out.append({"test": f"Rule 3 where a {sh} appears (reported)", "value": " ".join(where) or "nowhere", "verdict": ""})
    for sg in ("p", "m"):
        pairs = [(th[(L, "mlp", sg, "edit")], th[(L, "attn", sg, "edit")]) for L in Ls if (L, "attn", sg, "edit") in th]
        if pairs:
            out.append({"test": f"Rule 4 median total turn MLP vs attention, sign {sg} (reported)",
                        "value": f"{statistics.median(a for a, _ in pairs):.1f} vs {statistics.median(b for _, b in pairs):.1f} deg; attention bends more at {sum(b > a for a, b in pairs)} of {len(pairs)} layers",
                        "verdict": ""})
    full = {(int(r["layer"]), r["half"], r["sign"]): r["shapes"] for r in W if r["kind"] == "edit"}
    upto = {(int(r["layer"]), r["half"], r["sign"]): r["shapes"] for r in rows if r["level"] == "whole" and r["range"] == "upto_C93" and r["kind"] == "edit"}
    ch = sum(full[k] != upto.get(k) for k in full)
    out.append({"test": "Rule 4 label changes when doses beyond 3 / -1 are added (reported)", "value": f"{ch} of {len(full)}", "verdict": ""})
    return out


def selftest():
    assert LAYERS == list(range(35)) and len(gj(0, "mlp", 1.0)) == 3 and len(gj(34, "attn", 1.0)) == 4
    assert TS2.texts()[PROMPT]
    rows = []
    for L in LAYERS:
        for h in HALVES:
            for s in ("p", "m"):
                for rng in ("full", "upto_C93"):
                    rows.append({"layer": L, "half": h, "sign": s, "kind": "edit", "level": "whole", "range": rng,
                                 "theta": 80 - L, "shapes": "other" if L != 20 else "clip"})
                    if h == "mlp" and s == "p":
                        rows.append({"layer": L, "half": h, "sign": s, "kind": "control", "level": "whole", "range": rng,
                                     "theta": 85 - L + (10 if L < 30 else -10), "shapes": "other"})
    d = {o["test"]: o for o in rules(rows)}
    assert d["Rule 1 Spearman layer vs total turn, MLP edits, positive"]["verdict"] == "depth orders the bend (deeper bends less)", d
    assert d["Rule 2 layers where the edit bends less than its random control (MLP, positive)"]["verdict"] == "everywhere"
    assert "L20_mlp/p/edit" in d["Rule 3 where a clip appears (reported)"]["value"]
    for r in rows:                                                          # flat theta: no order
        r["theta"] = 60 + (int(r["layer"]) * 7919) % 5
    d = {o["test"]: o for o in rules(rows)}
    assert d["Rule 1 Spearman layer vs total turn, MLP edits, positive"]["verdict"] in ("no order", "weak"), d
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
