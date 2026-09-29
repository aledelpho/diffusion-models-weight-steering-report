# -*- coding: utf-8 -*-
"""Measures for docs/prereg_late_blocks_render_controls.md (deposited ff06640).
Computes, resumably: RMS contrast, focus concentration, layout similarity to baseline for the 171
atlas renders; and all six measures for benchmark_profondita blocks 22-27 at seed 42 (P01, P02)
plus their seed-42 baselines from benchmark_latenti_b6. No render."""
import csv, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT = Path(__file__).resolve().parent.parent; DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_single_blocks as S

def grey(p):
    return np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0

def contrast(g): return float(g.std())

def focus_cv(g, ty=20, tx=16):
    lap = np.abs(ndimage.laplace(g))
    h, w = g.shape; th, tw = h // ty, w // tx
    t = lap[:th * ty, :tw * tx].reshape(ty, th, tx, tw).mean(axis=(1, 3))
    return float(t.std() / t.mean())

def small(g):
    s = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((g.shape[1] // 16, g.shape[0] // 16), Image.BOX), dtype=np.float32)
    return (s - s.mean()) / s.std()

def layout_sim(g, gb):
    a, b = small(g), small(gb)
    return float((a * b).mean())

def atlas(budget=150):
    t0 = time.time(); out = DATA / "late_blocks_atlas_extra.csv"
    rows = G.read_csv(out) if out.exists() else []; done = {r["file"] for r in rows}
    plan = G.read_csv(S.PLAN)
    base = {r["prompt_id"]: r["expected_filename"] for r in plan if r["arm"] == "baseline"}
    gbase = {}
    for r in plan:
        fn = r["expected_filename"]
        if fn in done: continue
        g = grey(S.rp(fn))
        if r["prompt_id"] not in gbase: gbase[r["prompt_id"]] = grey(S.rp(base[r["prompt_id"]]))
        rows.append({"file": fn, "contrast": contrast(g), "focus_cv": focus_cv(g),
                     "layout_sim": layout_sim(g, gbase[r["prompt_id"]])})
        if time.time() - t0 > budget: break
    G.write_csv(out, rows); print(f"atlas: {len(rows)}/171")

def profondita():
    from style_features import extract_all_features
    from retro_texture_axes import measure
    out = DATA / "late_blocks_profondita.csv"; rows = []
    base = {p: G.find_render("benchmark_latenti_b6", f"{p}_baseline_lat_krea2_seed42_00001_.png") for p in ("P01", "P02")}
    for p, b in base.items():
        rec = G.png_record(b); print(f"  baseline {p}: {rec.get('sha')} steps {rec.get('steps')} {rec.get('sampler')} {rec.get('scheduler')} cfg {rec.get('cfg')} {rec.get('size')}")
    todo = [(p, None, None, base[p]) for p in base]
    for p in ("P01", "P02"):
        for blk in range(22, 28):
            for sign in ("pos", "neg"):
                fn = f"{p}_blk{blk:02d}{sign}_0.200_krea2_seed42_00001_.png"
                path = G.find_render("benchmark_profondita", fn) or G.find_render("benchmark_profondita_neg", fn)
                todo.append((p, blk, sign, path))
    r0 = G.png_record(todo[2][3]); print(f"  profondita campione: {r0.get('sha')} steps {r0.get('steps')} {r0.get('sampler')} {r0.get('scheduler')} cfg {r0.get('cfg')} {r0.get('size')}")
    gb = {p: grey(base[p]) for p in base}
    for p, blk, sign, path in todo:
        f = extract_all_features(str(path)); _, _, _, sat, _ = measure(str(path)); g = grey(path)
        rows.append({"prompt": p, "block": "" if blk is None else blk, "sign": sign or "baseline",
                     "colorfulness_hs": f["colorfulness_hs"], "sat": sat, "contrast": contrast(g),
                     "lbp_entropy": f["lbp_entropy"], "fft_high_freq_share": f["fft_high_freq_share"],
                     "focus_cv": focus_cv(g), "layout_sim": layout_sim(g, gb[p])})
    G.write_csv(out, rows); print(f"profondita: {len(rows)} righe")

if __name__ == "__main__":
    atlas() if sys.argv[1] == "atlas" else profondita()
