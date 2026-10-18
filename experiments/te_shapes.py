"""C93 - shapes of the push along the dose, against random pushes of the same size (docs/prereg_te_shapes.md).
Written 2026-10-18 with the pre-registration, before any encode. No renders.

  python te_shapes.py --selftest     # shape rules on synthetic trajectories (numpy only)
  python te_shapes.py --run          # GPU, ComfyUI venv: gates, encodes, shapes -> data/te_shapes_*.csv, Text2Img/benchmark_te_shapes/*.npz
  python te_shapes.py --rules        # numpy: decision rules from data/te_shapes_trajectories.csv
"""
import argparse, csv, json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
DATA = HERE.parent / "data"
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter"]
EDITS = {"L06_mlp": (6, "mlp"), "L14_mlp": (14, "mlp"), "L28_mlp": (28, "mlp"), "L06_attn": (6, "attn"), "L14_attn": (14, "attn")}
POS = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.25, 1.50, 1.75, 2.00, 2.50, 3.00]
NEG = [d for d in POS if d <= 1.00]
OUT_TRAJ = DATA / "te_shapes_trajectories.csv"
OUT_TEST = DATA / "te_shapes_tests.csv"


# ---------------------------------------------------------------- shape measures (numpy)
def _ang(a, b):
    return float(np.degrees(np.arccos(np.clip(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12), -1, 1))))


def measures(P):
    """P: (n doses, D) pushes in dose order. Returns the measures of section 3."""
    P = np.asarray(P, dtype=np.float64)
    U = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-12)
    theta = _ang(U[0], U[-1])
    # plane of the directions themselves (uncentred: directions live on the sphere around the origin)
    _, s, vt = np.linalg.svd(U, full_matrices=False)
    planar = float((s[:2] ** 2).sum() / max((s ** 2).sum(), 1e-24))
    x, y = U @ vt[0], (U @ vt[1] if len(vt) > 1 else np.zeros(len(U)))
    phi = np.degrees(np.unwrap(np.arctan2(y, x)))
    inc = np.diff(phi); big = inc[np.abs(inc) > 2.0]
    signs = np.sign(big)
    rev = int((signs[1:] != signs[:-1]).sum()) if len(signs) > 1 else 0
    segs, cur = [], 0.0
    for k, v in enumerate(big):
        if k and np.sign(v) != np.sign(big[k - 1]):
            segs.append(abs(cur)); cur = 0.0
        cur += v
    segs.append(abs(cur))
    swing = float(min(segs)) if segs else 0.0
    steps = [_ang(U[i], U[i + 1]) for i in range(len(U) - 1)]
    clip = float(max(steps)) if steps else 0.0             # largest turn in one dose step
    # acceleration against the length of the push |p| (not the dose, not the path, which rotation itself lengthens)
    n = np.linalg.norm(P, axis=1); n_mid = (n[1:] + n[:-1]) / 2
    cut = n[0] + 2 / 3 * (n[-1] - n[0])
    tot = sum(steps)
    acc = float(sum(a for a, m in zip(steps, n_mid) if m >= cut) / tot) if tot > 0 else 0.0
    return {"theta": round(theta, 2), "planar": round(planar, 3), "rotation": round(float(abs(phi[-1] - phi[0])), 1),
            "reversals": rev, "swing": round(swing, 1), "max_step": round(clip, 1), "accel": round(acc, 3)}


def shapes(m):
    out = []
    if m["theta"] < 20:
        return ["straight"]
    if m["planar"] >= 0.80 and m["reversals"] <= 1 and m["rotation"] >= 90 and m["max_step"] < 90:
        out.append("spiral")
    if m["reversals"] >= 2 and m["swing"] >= 10:
        out.append("wave")
    if m["max_step"] >= 90:
        out.append("clip")
    if m["accel"] >= 0.60:
        out.append("accelerating")
    return out or ["other"]


# ---------------------------------------------------------------- encodes (GPU)
def _layers(clip):
    for name, mod in clip.cond_stage_model.named_modules():
        if name.endswith("model.layers") and hasattr(mod, "__len__") and len(mod) == 36:
            return mod
    raise RuntimeError("36-layer ModuleList not found")


def run():
    import torch
    import te_conditioning as TC
    import te_punct_encoder as TPE
    import te_layer0_encoder as TLE
    import blk23_colorful as c47
    base = TPE.gate()                                                     # gate (a): bit-identical elf baseline
    tx = {}
    for r in TC.rd(DATA / "te_characters_plan.csv"):
        tx.setdefault(r["char"], r["prompt_text"])
    def gj(edit, d):
        L, half = EDITS[edit]
        mats = ("gate", "up", "down") if half == "mlp" else ("q", "k", "v", "o")
        pre = f"layers.{L}.mlp." if half == "mlp" else f"layers.{L}.self_attn."
        return {f"{pre}{m}_proj.weight": d for m in mats}
    # gate (b): L06 MLP at 1.00 on the dwarf against the C67 encode
    c0, _, _ = TPE.encode_taps(base, tx["D1_dwarf_paladin"])
    c1, _, _ = TPE.encode_taps(TLE.apply_te_edit(base, gj("L06_mlp", 1.0)), tx["D1_dwarf_paladin"])
    rel = np.linalg.norm(c1 - c0, axis=-1) / (np.linalg.norm(c0, axis=-1) + 1e-6)
    ref = np.load(TC.out_path("chars", "D1_dwarf_paladin", "L06_mlp_p1.00"))["rel"]
    err = float(np.abs(rel - ref).max()); print(f"GATE b L06 MLP 1.00 dwarf vs C67: max rel err {err:.6f} (limit {2 * TC.FP16_FLOOR:.6f})")
    if err > 2 * TC.FP16_FLOOR:
        sys.exit("GATE b FAIL - stop")
    layers = _layers(base)
    outdir = c47.IMG_ROOT / "benchmark_te_shapes"; outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for ch in CHARS:
        text = tx[ch]
        cb, _, ids = TPE.encode_taps(base, text)
        scale = np.linalg.norm(cb, axis=-1).mean(0)                       # (12,)
        def push(c):
            return (c - cb) / scale[None, :, None]
        # capture the unedited MLP outputs once
        cap = {}
        def grab(key):
            def h(mod, args, out):
                cap[key] = (out[0] if isinstance(out, tuple) else out).detach().float().clone()
            return h
        hs = [layers[L].mlp.register_forward_hook(grab(("base", L))) for L in (6, 14, 28)]
        TPE.encode_taps(base, text)
        for h in hs:
            h.remove()
        # gate (c): zero-length control leaves the conditioning bit-identical
        hz = layers[6].mlp.register_forward_hook(lambda m, a, o: o + 0 * o)
        cz, _, _ = TPE.encode_taps(base, text); hz.remove()
        if float(np.abs(cz - cb).max()) != 0.0:
            sys.exit(f"GATE c FAIL on {ch} - stop")
        for edit in EDITS:
            L, half = EDITS[edit]
            for sign, doses in (("p", POS), ("m", NEG)):
                Ps, Pc, lens = [], [], []
                for d in doses:
                    dd = d if sign == "p" else -d
                    clip_e = TLE.apply_te_edit(base, gj(edit, dd))
                    if half == "mlp" and sign == "p":
                        h = layers[L].mlp.register_forward_hook(grab(("edit", L)))
                        ce, _, _ = TPE.encode_taps(clip_e, text); h.remove()
                        lens.append(torch.linalg.vector_norm(cap[("edit", L)] - cap[("base", L)], dim=-1))
                    else:
                        ce, _, _ = TPE.encode_taps(clip_e, text)
                    Ps.append(push(ce))
                if half == "mlp" and sign == "p":                         # random control, same lengths, same place
                    g = torch.Generator(device="cpu").manual_seed(9393)
                    shp = cap[("base", L)].shape
                    R = torch.randn(shp, generator=g); R = R / torch.linalg.vector_norm(R, dim=-1, keepdim=True)
                    for n in lens:
                        add = (R.to(n.device) * n.unsqueeze(-1))
                        h = layers[L].mlp.register_forward_hook(lambda m, a, o, add=add: o + add.to(o.dtype).to(o.device))
                        cc, _, _ = TPE.encode_taps(base, text); h.remove()
                        Pc.append(push(cc))
                for kind, PP in (("edit", Ps), ("control", Pc)):
                    if not PP:
                        continue
                    A = np.stack(PP)                                      # (n, seq, 12, 2560)
                    np.savez_compressed(outdir / f"{ch}_{edit}_{sign}_{kind}.npz", dmean=A.mean(1).astype(np.float16),
                                        doses=np.array(doses))
                    base_row = {"char": ch, "edit": edit, "sign": sign, "kind": kind}
                    m = measures(A.mean(1).reshape(len(PP), -1))
                    rows.append({**base_row, "level": "whole", "unit": "", **m, "shapes": "+".join(shapes(m))})
                    for t in range(12):
                        m = measures(A.mean(1)[:, t, :])
                        rows.append({**base_row, "level": "tap", "unit": t, **m, "shapes": "+".join(shapes(m))})
                    for k in range(A.shape[1]):
                        if np.linalg.norm(A[0, k]) == 0:
                            continue
                        m = measures(A[:, k].reshape(len(PP), -1))
                        rows.append({**base_row, "level": "token", "unit": k, **m, "shapes": "+".join(shapes(m))})
                print("done", ch, edit, sign, len(rows))
    with open(OUT_TRAJ, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("wrote", OUT_TRAJ, len(rows))


# ---------------------------------------------------------------- rules (numpy)
def rules(rows):
    out = []
    S = lambda r: set(r["shapes"].split("+"))
    whole = [r for r in rows if r["level"] == "whole"]
    me = {(r["char"], r["edit"]): S(r) for r in whole if r["kind"] == "edit" and r["sign"] == "p" and r["edit"].endswith("mlp")}
    mc = {(r["char"], r["edit"]): S(r) for r in whole if r["kind"] == "control"}
    for sh in ("straight", "spiral", "wave", "clip", "accelerating", "other"):
        ne = sum(sh in v for v in me.values()); nc = sum(sh in v for v in mc.values())
        v = ("belongs to the edits" if ne >= 5 and nc <= 2 else ("belongs to the network" if ne >= 5 and nc >= 5 else ""))
        out.append({"test": f"Rule 1 {sh}: edits vs controls (whole, MLP, positive)", "value": f"{ne} of {len(me)} vs {nc} of {len(mc)}", "verdict": v})
    ed = [r for r in whole if r["kind"] == "edit"]
    taps = defaultdict(dict)
    for r in rows:
        if r["level"] == "tap" and r["kind"] == "edit":
            taps[(r["char"], r["edit"], r["sign"])][int(r["unit"])] = S(r)
    diff = early_late = 0
    for r in ed:
        t = taps[(r["char"], r["edit"], r["sign"])]
        diff += any(t[k] != S(r) for k in t)
        mj = lambda ks: Counter(min(t[k]) for k in ks if k in t).most_common(1)[0][0]
        early_late += mj(range(2, 9)) != mj(range(9, 12))
    v2 = "the shape lives in the taps" if diff >= 2 / 3 * len(ed) and early_late >= len(ed) / 2 else "one shape for the whole encoder"
    out.append({"test": "Rule 2 per-tap shapes differ from the whole / early vs late majority differs", "value": f"{diff} of {len(ed)} / {early_late} of {len(ed)}", "verdict": v2})
    tok = [r for r in rows if r["level"] == "token"]
    for kind in ("edit", "control"):
        c = Counter(s for r in tok if r["kind"] == kind and r["sign"] == "p" and r["edit"].endswith("mlp") for s in S(r))
        n = sum(1 for r in tok if r["kind"] == kind and r["sign"] == "p" and r["edit"].endswith("mlp"))
        out.append({"test": f"Rule 3 per-token shapes, {kind}s (MLP, positive; reported)", "value": " ".join(f"{k}:{v / max(n, 1):.2f}" for k, v in c.most_common()) + f" (n {n})", "verdict": ""})
    return out


def selftest():
    rng = np.random.default_rng(0); D = 60
    e = np.linalg.qr(rng.normal(size=(D, 4)))[0].T
    d = np.array(POS)
    def mk(f):
        return np.array([f(x) for x in d]) + rng.normal(0, 1e-4, (len(d), D))
    straight = mk(lambda x: x * e[0])
    spiral = mk(lambda x: x * (np.cos(1.2 * x) * e[0] + np.sin(1.2 * x) * e[1]))
    wave = mk(lambda x: x * (e[0] + 0.6 * np.sin(4 * x) * e[1]))
    clip = mk(lambda x: x * (e[0] + 0.2 * e[1] if x < 1.5 else -e[0] + 0.3 * e[1]))        # jumps across at 1.5
    accel = mk(lambda x: x * (np.cos(0.06 * x ** 3) * e[0] + np.sin(0.06 * x ** 3) * e[1]))  # turns mostly at the end
    got = {k: shapes(measures(v)) for k, v in dict(straight=straight, spiral=spiral, wave=wave, clip=clip, accel=accel).items()}
    assert got["straight"] == ["straight"], got
    assert "spiral" in got["spiral"], got
    assert "wave" in got["wave"], got
    assert "clip" in got["clip"], got
    assert "accelerating" in got["accel"], got
    assert "wave" not in got["spiral"] and "spiral" not in got["wave"], got
    print("selftest ok", got)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a in ("selftest", "run", "rules"):
        ap.add_argument(f"--{a}", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.run: run()
    if a.rules:
        out = rules(list(csv.DictReader(open(OUT_TRAJ, encoding="utf-8"))))
        with open(OUT_TEST, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
