"""C69 — the bridge in the DiT: where and when does the same text-encoder push send different word orders to
different pictures? (docs/prereg_te_bridge.md). Written 2026-10-12, before any C69 render. Renders authorised by
Alessandro (25: 5 word orders x {baseline + 4 edits}, seed 3141592; they re-render existing images with the probe on).

  python te_bridge.py --plan             # data/te_bridge_plan.csv
  python te_bridge.py --queue --first 1  # one render, for the reproduction gate
  python te_bridge.py --repro            # every rendered image must equal the existing one pixel for pixel
  python te_bridge.py --queue            # the rest
  python te_bridge.py --count
  python te_bridge.py --analyze          # data/te_bridge_*.csv and the readings (Claude)
  python te_bridge.py --selftest

Attention maps: tools/comfyui_krea2_attnprobe (Krea2AttentionProbe) patched onto the model before the sampler. Units
= the clauses of the prompt (te_regions.units, from the C67 baseline token ids of each order).
"""
import argparse, csv, itertools, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP
import te_conditioning as T
import te_regions as RG

DATA = HERE.parent / "data"
PLAN = DATA / "te_bridge_plan.csv"
FOLDER = "benchmark_te_bridge"
SEED = "3141592"
ORDERS = RG.ORDERS
EDITS = {"L06_mlp_p1.00": "strong", "L12_mlp_p1.00": "strong", "L10_mlp_m1.00": "mild", "L19_attn_m1.00": "mild"}
CONDS = ["baseline"] + list(EDITS)
# the clauses that name the style; P5 (added 2026-10-12, before any render, after Alessandro's remark that weakening the
# "comics" words can let a default style - anime - take over: a dataset prior, or a fall into stereotypes)
STYLE_UNITS = ["realistic western comics style", "bold ink outlines", "hatched shadows"]


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def ref_image(v, cond):
    if cond == "baseline":
        return c47.IMG_ROOT / "benchmark_prompt_order" / f"{v}_baseline_krea2_seed{SEED}_00001_.png"
    return c47.IMG_ROOT / "benchmark_te_characters" / f"{v}_{cond}_krea2_seed{SEED}_00001_.png"


def attn_dir(v, cond):
    return c47.IMG_ROOT / FOLDER / "attn" / f"{v}_{cond}"


def make_plan():
    inv = T.vocab()
    ch = {(r["char"], r["cond"]): r for r in rd(DATA / "te_characters_plan.csv") if r["seed"] == SEED and r["phase"] == "order"}
    texts = {}
    for r in rd(DATA / "te_conditioning_plan.csv"):
        if r["set"] == "order" and r["cond"] == "baseline":
            texts[r["prompt_id"]] = r["prompt_text"]
    for (v, k), r in ch.items():   # the text the C65 images were rendered with must be the one C67 tokenised
        assert r["prompt_text"] == texts[v], (v, k)
        for x, y in TP_SETTINGS.items():
            assert r[x] == y, (v, k, x)
    rows = []
    for v in ORDERS:
        ids = np.load(T.out_path("order", v, "baseline"))["ids"]
        units = RG.units(ids, inv, "clause")
        spans = [[u["pos"][0], u["pos"][-1] + 1] for u in units]
        for k in CONDS:
            src = ch.get((v, k))
            gj = src["te_granular_json"] if src else ""
            prefix = f"{v}_{k}_krea2_seed{SEED}"
            rows.append({"row": len(rows), "prompt_id": v, "cond": k, "kind": EDITS.get(k, "baseline"), "te_granular_json": gj,
                         "prompt_text": texts[v], "units": json.dumps(spans), "unit_texts": json.dumps([u["text"] for u in units]),
                         "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", "attn_rel": f"attn/{v}_{k}",
                         "seed": SEED, **TP_SETTINGS})
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


TP_SETTINGS = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
               "width": "1024", "height": "1280"}


def workflow(r):
    wf = TP.workflow({**r, "vectors_override": ""})
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    wf["92"] = {"class_type": "Krea2AttentionProbe", "inputs": {"model": wf["42"]["inputs"]["model"], "out_dir": str(attn_dir(r["prompt_id"], r["cond"])),
                                                               "units": r["units"], "grid": "80,64", "pool": 2}}
    wf["42"]["inputs"]["model"] = ["92", 0]
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


def repro():
    ok, n = True, 0
    for r in rd(PLAN):
        new = c47.IMG_ROOT / FOLDER / r["expected_filename"]
        if not new.exists():
            continue
        d = int(np.abs(_im(new) - _im(ref_image(r["prompt_id"], r["cond"]))).max()); n += 1
        steps = len(list(attn_dir(r["prompt_id"], r["cond"]).glob("step*.npz")))
        if d != 0 or steps != 9:
            ok = False; print("  ", r["prompt_id"], r["cond"], "max abs diff", d, "attention steps", steps)
    print(f"REPRO {'PASS' if ok and n else 'FAIL - stop'}: {n} renders checked (pixel-identical to the existing images, 9 attention files each)")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


# ---------------------------------------------------------------- analysis
def load(v, cond):
    d = attn_dir(v, cond)
    fs = sorted(d.glob("step*.npz"))
    A = np.stack([np.load(f)["attn"].astype(np.float32) for f in fs])          # (steps, blocks, H, W, units)
    return A


def load_tt(v, cond):
    fs = sorted(attn_dir(v, cond).glob("step*.npz"))
    return np.stack([np.load(f)["text_total"].astype(np.float32) for f in fs])  # (steps, blocks, H, W)


def style_mass(keyed):
    """P5/P6: per cond, mean over orders, steps, blocks and image regions of (a) the share of the attention on text that
    goes to the style clauses, (b) the attention mass on all text."""
    out = []
    for c in CONDS:
        share, tot = [], []
        for v in ORDERS:
            A, T_ = load(v, c), load_tt(v, c)
            js = [keyed[v][(u, 0)] for u in STYLE_UNITS]
            sty = A[..., js].sum(-1)
            share.append(float((sty / (T_ + 1e-9)).mean())); tot.append(float(T_.mean()))
        out.append({"cond": c, "kind": EDITS.get(c, "baseline"), "style_share_of_text_attention": round(float(np.mean(share)), 5),
                    "text_attention_mass": round(float(np.mean(tot)), 5),
                    "per_order_style_share": json.dumps([round(x, 5) for x in share])})
    with open(DATA / "te_bridge_style.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    return out


def cos_maps(a, b):
    a = a.ravel(); b = b.ravel()
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def divergence(maps):
    """maps: {order: (H, W)}; 1 - mean pairwise cosine."""
    ks = sorted(maps)
    return 1 - float(np.mean([cos_maps(maps[a], maps[b]) for a, b in itertools.combinations(ks, 2)]))


def analyze():
    plan = rd(PLAN)
    utexts = {r["prompt_id"]: json.loads(r["unit_texts"]) for r in plan}
    # units present (same text, same occurrence) in all five orders
    keyed = {}
    for v in ORDERS:
        seen = {}; keyed[v] = {}
        for j, t in enumerate(utexts[v]):
            key = (t, seen.get(t, 0)); seen[t] = key[1] + 1; keyed[v][key] = j
    shared = sorted(set.intersection(*[set(keyed[v]) for v in ORDERS]))
    A = {(v, c): load(v, c) for v in ORDERS for c in CONDS}
    S, B = A[(ORDERS[0], "baseline")].shape[:2]
    rows = []
    for c in CONDS:
        for s in range(S):
            for b in range(B):
                div = np.mean([divergence({v: A[(v, c)][s, b, :, :, keyed[v][u]] for v in ORDERS}) for u in shared])
                chg = np.nan if c == "baseline" else np.mean([1 - cos_maps(A[(v, c)][s, b, :, :, keyed[v][u]], A[(v, "baseline")][s, b, :, :, keyed[v][u]])
                                                            for v in ORDERS for u in shared])
                rows.append({"cond": c, "kind": EDITS.get(c, "baseline"), "step": s, "block": b, "order_divergence": round(float(div), 5),
                             "change_vs_baseline": round(float(chg), 5) if not np.isnan(chg) else ""})
    with open(DATA / "te_bridge_maps.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    # per unit: which regions move most under the strong edits (mean over orders, steps, blocks)
    urows = []
    for u in shared:
        for c in EDITS:
            ch = np.mean([1 - cos_maps(A[(v, c)][s, :, :, :, keyed[v][u]], A[(v, "baseline")][s, :, :, :, keyed[v][u]]) for v in ORDERS for s in range(S)])
            urows.append({"unit": u[0], "occurrence": u[1], "cond": c, "kind": EDITS[c], "change_vs_baseline": round(float(ch), 5)})
    with open(DATA / "te_bridge_units.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(urows[0])); w.writeheader(); w.writerows(urows)
    readings(rows, style_mass(keyed))


def readings(rows, sm=None):
    """The pre-registered readings (P1-P4)."""
    by = {}
    for r in rows:
        by.setdefault(r["cond"], {}).setdefault(int(r["step"]), []).append(float(r["order_divergence"]))
    steps = sorted(by["baseline"])
    D = {c: np.array([np.mean(by[c][s]) for s in steps]) for c in by}
    dD = {c: D[c] - D["baseline"] for c in EDITS}
    strong = [c for c in EDITS if EDITS[c] == "strong"]; mild = [c for c in EDITS if EDITS[c] == "mild"]
    out = []
    p1 = min(dD[c].mean() for c in strong) > max(dD[c].mean() for c in mild)
    out.append({"reading": "P1 strong edits raise the order divergence of the attention maps more than mild ones (mean over steps and blocks)",
                "value": "; ".join(f"{c} {dD[c].mean():+.4f}" for c in EDITS), "holds": bool(p1)})
    sep = next((s for s in steps if min(dD[c][s] for c in strong) > max(dD[c][s] for c in mild)), None)
    out.append({"reading": "P2 first step (0-8) at which both strong edits exceed both mild ones in order divergence",
                "value": f"step {sep}" if sep is not None else "never", "holds": sep is not None and sep <= 2})
    blk = {}
    for r in rows:
        if r["cond"] in strong:
            blk.setdefault(int(r["block"]), []).append(float(r["order_divergence"]))
    base_blk = {}
    for r in rows:
        if r["cond"] == "baseline":
            base_blk.setdefault(int(r["block"]), []).append(float(r["order_divergence"]))
    gain = {b: np.mean(blk[b]) - np.mean(base_blk[b]) for b in blk}
    top = sorted(gain, key=lambda b: -gain[b])[:5]
    out.append({"reading": "P3 blocks where the strong edits raise the order divergence most (top 5)", "value": ", ".join(f"{b}:{gain[b]:+.4f}" for b in top), "holds": ""})
    ch = {}
    for r in rows:
        if r["change_vs_baseline"] != "":
            ch.setdefault(r["cond"], []).append(float(r["change_vs_baseline"]))
    p4 = min(np.mean(ch[c]) for c in strong) > max(np.mean(ch[c]) for c in mild)
    out.append({"reading": "P4 strong edits move the attention maps away from the baseline more than mild ones",
                "value": "; ".join(f"{c} {np.mean(ch[c]):.4f}" for c in EDITS), "holds": bool(p4)})
    if sm:
        sh = {r["cond"]: r["style_share_of_text_attention"] for r in sm}; tm = {r["cond"]: r["text_attention_mass"] for r in sm}
        d5 = {c: sh[c] - sh["baseline"] for c in EDITS}
        p5 = max(d5[c] for c in strong) < min(d5[c] for c in mild)
        out.append({"reading": "P5 strong edits lower the share of text attention that goes to the style clauses more than mild ones",
                    "value": "; ".join(f"{c} {d5[c]:+.5f}" for c in EDITS) + f" (baseline share {sh['baseline']:.5f})", "holds": bool(p5)})
        out.append({"reading": "P6 attention mass on all text, by condition (reported)",
                    "value": "; ".join(f"{c} {tm[c]:.5f}" for c in CONDS), "holds": ""})
    with open(DATA / "te_bridge_readings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["reading", "value", "holds"]); w.writeheader(); w.writerows(out)
    for r in out:
        print(r)
    print("order divergence by step:", {c: np.round(D[c], 4).tolist() for c in D})


def selftest():
    rng = np.random.default_rng(0)
    m = rng.random((40, 32))
    assert abs(divergence({v: m for v in "abcde"})) < 1e-6
    assert divergence({v: rng.random((40, 32)) for v in "abcde"}) > 0.05
    # pooling convention of the node: row-major tokens (rows, cols)
    gh, gw, p = 8, 6, 2
    x = np.arange(gh * gw, dtype=float).reshape(gh * gw, 1)
    pooled = x.reshape(gh // p, p, gw // p, p, 1).mean(axis=(1, 3))
    assert pooled[0, 0, 0] == np.mean([0, 1, 6, 7])
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "repro", "count", "analyze", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root"); ap.add_argument("--vocab")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.vocab: T.VOCAB = Path(a.vocab)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.repro: repro()
    if a.count: count()
    if a.analyze: analyze()
    if a.selftest: selftest()
