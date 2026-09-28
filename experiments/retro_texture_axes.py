#!/usr/bin/env python3
"""The two axes added on 2026-09-28, applied to every render this project has ever made.

Both are functions of a single image -- structure coherence (is what is left still a drawing?) and
the energy at each scale of detail (what size is the texture that changed?). Neither needs a
baseline to be computed, so every render already on disk can be re-measured for the cost of reading
it. The published corpora were scored with statistics that sum over scale and cannot tell a move
from a collapse; this table is what lets any of those readings be checked without a GPU.

ABSOLUTE values only. Ratios need a baseline and every bench names its baselines differently, so
the joins live in the per-bench analyses that sit on top of this file, not here.

Columns per render:
  coherence      (l1-l2)/(l1+l2) of the gradient structure tensor over 9x9, averaged
  band0..band4   energy at 1-2, 2-4, 4-8, 8-16, 16-32 px, from a Gaussian pyramid
  variance       of the luminance -- contrast
  chroma         mean saturation
  hue_deg        saturation-weighted circular mean hue

Resumable: B is a seconds budget, the file is appended, and a rerun picks up where it stopped.
Writes data/retro_texture_axes.csv. No render.
"""
import csv, math, os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage

H = os.environ.get("COMFY_OUTPUT_ROOT", os.path.expanduser("~/mnt"))
OUT = "data/retro_texture_axes.csv"
BENCHES = [
    "benchmark_mappa--renders", "benchmark_profondita/renders", "benchmark_profondita_neg/renders",
    "benchmark_rectified_masks/renders", "benchmark_blk16_ladder/renders",
    "benchmark_leaf_collapse/renders", "benchmark_colour_binding--renders",
    "benchmark_atlas_phase1--renders", "benchmark_qkvo_atlas--renders",
    "benchmark_stage4_preset/renders", "benchmark_stage5/renders", "benchmark_stage7/renders",
    "benchmark_stage9/renders", "benchmark_latenti_b6/renders",
    "benchmark_pavimento_rumore/renders",
    "benchmark_stage7a/renders", "benchmark_stage2_family/renders",
]
FIELDS = ["bench", "file", "coherence", "band0", "band1", "band2", "band3", "band4",
          "variance", "chroma", "hue_deg"]
K = np.array([1, 4, 6, 4, 1], dtype=np.float32) / 16.0


def measure(path):
    im = Image.open(path)
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0

    gy, gx = np.gradient(g)
    jxx = ndimage.uniform_filter(gx * gx, 9)
    jyy = ndimage.uniform_filter(gy * gy, 9)
    jxy = ndimage.uniform_filter(gx * gy, 9)
    tr = jxx + jyy
    root = np.sqrt(np.maximum((jxx - jyy) ** 2 + 4 * jxy ** 2, 0.0))
    coh = float(np.mean(np.where(tr > 1e-8, root / np.maximum(tr, 1e-8), 0.0)))

    bands, cur = [], g
    for _ in range(5):
        lo = ndimage.convolve1d(ndimage.convolve1d(cur, K, axis=0, mode="nearest"),
                                K, axis=1, mode="nearest")
        bands.append(float(((lo - cur) ** 2).mean()))
        cur = lo[::2, ::2]

    mx, mn = a.max(2), a.min(2)
    d = mx - mn
    sat = np.where(mx > 1e-5, d / np.maximum(mx, 1e-5), 0.0)
    r, gg, b = a[..., 0], a[..., 1], a[..., 2]
    hue = np.zeros_like(mx)
    m = (mx == r) & (d > 1e-5); hue[m] = (60 * ((gg[m] - b[m]) / d[m]) + 360) % 360
    m = (mx == gg) & (d > 1e-5); hue[m] = (60 * ((b[m] - r[m]) / d[m]) + 120) % 360
    m = (mx == b) & (d > 1e-5); hue[m] = (60 * ((r[m] - gg[m]) / d[m]) + 240) % 360
    rad = np.deg2rad(hue)
    hm = float(np.rad2deg(math.atan2(float((sat * np.sin(rad)).sum()),
                                     float((sat * np.cos(rad)).sum()))) % 360)
    return coh, bands, float(g.var()), float(sat.mean()), hm


def main():
    budget = float(os.environ.get("B", "160"))
    t0 = time.time()
    done = set()
    if os.path.exists(OUT):
        done = {(r["bench"], r["file"]) for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    todo = []
    for b in BENCHES:
        d = os.path.join(H, b)
        if not os.path.isdir(d):
            print(f"  (missing, skipped) {b}")
            continue
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(".png") and (b, f) not in done:
                todo.append((b, f, os.path.join(d, f)))
    print(f"done {len(done)}, todo {len(todo)}")
    rows = []
    for b, f, p in todo:
        if time.time() - t0 > budget:
            break
        try:
            coh, bands, var, ch, hm = measure(p)
        except Exception as exc:                      # a truncated or unreadable file
            print(f"  SKIP {f}: {exc}")
            continue
        rows.append(dict(bench=b, file=f, coherence=f"{coh:.6f}",
                         **{f"band{i}": f"{bands[i]:.8f}" for i in range(5)},
                         variance=f"{var:.6f}", chroma=f"{ch:.5f}", hue_deg=f"{hm:.2f}"))
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    left = len(todo) - len(rows)
    print(f"wrote {len(rows)}, total {len(done)+len(rows)}, {left} left"
          + ("  -- rerun to continue" if left else "  -- COMPLETE"))


if __name__ == "__main__":
    main()
