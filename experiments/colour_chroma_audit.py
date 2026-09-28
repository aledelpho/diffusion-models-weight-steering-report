#!/usr/bin/env python3
"""Re-measures the Stage 2b colour sweep with a foreground that does not depend on colour.

Why. evaluate_colour_object_sweep.py defines the foreground as `sat > 0.15` and then calls a cell
"object destroyed" when that foreground is small:

    fg_mask = (sat > 0.15) & (val > 0.08) & (val < 0.98)
    object_intact = (fg_share >= 0.030) and (mean_sat >= 0.15)

An achromatic object therefore has no foreground by construction and is filed as a broken object.
The one outcome the experiment was looking for -- object kept, colour removed -- is the one outcome
that criterion cannot represent. It is also the reason `mean_sat` in that file is censored: it is
averaged over pixels selected for being saturated.

This script replaces the foreground with a value-based one (deviation from the background value
measured on the border ring), which is blind to chroma. The value channel is low-passed 8x and the
mask reduced to its largest connected component FIRST: a plain per-pixel threshold is defeated by
grain, which floods the background with value deviation and triples the foreground -- on
`Block_6 pos` it took the region from 0.10 to 0.30 of the frame and dragged the measured chroma
down with the grey noise it had swallowed. That is the same failure this script was written to
expose, committed by this script's first version. See colour_gate_and_chroma_audit.md section 7.

It reports for every render:
  fg_share  -- size of the object region
  iou       -- overlap of that region with the same prompt/seed baseline: structure kept or not
  chroma    -- mean saturation inside it, uncensored
  hue       -- saturation-weighted circular mean hue inside it

The pre-registered verdict is not touched: it was a prediction about hue rotation and it fell on
hue rotation. This is a separate reading of the same renders, and anything it suggests needs its
own pre-registration before it counts.

Writes data/colour_chroma_audit.csv, data/colour_chroma_audit_summary.csv and
data/colour_chroma_audit_tests.csv. No render.
"""
import csv, math, os, statistics
import numpy as np
from PIL import Image
from scipy import ndimage

REN = os.environ.get("REN", os.path.expanduser(
    "~/mnt/benchmark_colour_binding--renders"))
# On the rendering machine this directory is
# C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_colour_binding\renders
OUT = "data/colour_chroma_audit.csv"
OUT_S = "data/colour_chroma_audit_summary.csv"
OUT_T = "data/colour_chroma_audit_tests.csv"
DOSE = "0.200"
PROBES = ["LP", "LG", "LN"]
BLOCKS = [f"Block_{i}" for i in range(1, 7)]
SIGNS = ["pos", "neg"]
SEEDS = ["42", "777", "1337"]


def load(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    mx = a.max(2); mn = a.min(2)
    sat = np.where(mx > 1e-5, (mx - mn) / np.maximum(mx, 1e-5), 0.0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = mx - mn
    hue = np.zeros_like(mx)
    m = (mx == r) & (d > 1e-5); hue[m] = (60 * ((g[m] - b[m]) / d[m]) + 360) % 360
    m = (mx == g) & (d > 1e-5); hue[m] = (60 * ((b[m] - r[m]) / d[m]) + 120) % 360
    m = (mx == b) & (d > 1e-5); hue[m] = (60 * ((r[m] - g[m]) / d[m]) + 240) % 360
    # Foreground by departure from the background value -- blind to chroma, and low-passed so
    # that grain cannot manufacture foreground. Largest connected component only.
    small = np.asarray(Image.fromarray((mx * 255).astype(np.uint8)).resize(
        (mx.shape[1] // 8, mx.shape[0] // 8), Image.BOX), dtype=np.float32) / 255.0
    ring = np.concatenate([small[:5].ravel(), small[-5:].ravel(),
                           small[:, :5].ravel(), small[:, -5:].ravel()])
    m = np.abs(small - float(np.median(ring))) > 0.06
    m = ndimage.binary_opening(m, np.ones((3, 3)))
    lab, n = ndimage.label(m)
    if n:
        m = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
    fg = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(
        (mx.shape[1], mx.shape[0]), Image.NEAREST)) > 127
    return fg, sat, hue


def describe(fg, sat, hue):
    if not fg.any():
        return 0.0, 0.0, 0.0
    s = sat[fg]
    w = s
    if w.sum() < 1e-6:
        h = 0.0
    else:
        rad = np.deg2rad(hue[fg])
        h = float(np.rad2deg(np.arctan2((w * np.sin(rad)).sum(), (w * np.cos(rad)).sum())) % 360)
    return float(fg.mean()), float(s.mean()), h


def circ_diff(a, b):
    d = abs(a - b) % 360.0
    return d if d <= 180 else 360 - d


def main():
    rows = []
    base = {}
    for p in PROBES:
        for s in SEEDS:
            f = f"{REN}/{p}_baseline_krea2_seed{s}_00001_.png"
            fg, sat, hue = load(f)
            sh, ch, hu = describe(fg, sat, hue)
            base[(p, s)] = (fg, sh, ch, hu)
            rows.append(dict(kind="baseline", probe=p, block="none", sign="none", seed=s,
                             fg_share=f"{sh:.5f}", iou="1.00000", chroma=f"{ch:.4f}",
                             hue_deg=f"{hu:.2f}", chroma_ratio="1.0000", hue_shift_deg="0.00"))
    for p in PROBES:
        for blk in BLOCKS:
            for sg in SIGNS:
                for s in SEEDS:
                    f = f"{REN}/{p}_{blk}{sg}_{DOSE}_krea2_seed{s}_00001_.png"
                    if not os.path.exists(f):
                        print(f"  MISSING {os.path.basename(f)}"); continue
                    fg, sat, hue = load(f)
                    sh, ch, hu = describe(fg, sat, hue)
                    bfg, bsh, bch, bhu = base[(p, s)]
                    inter = float((fg & bfg).sum()); union = float((fg | bfg).sum())
                    rows.append(dict(kind="perturbed", probe=p, block=blk, sign=sg, seed=s,
                                     fg_share=f"{sh:.5f}",
                                     iou=f"{(inter/union if union else 0):.5f}",
                                     chroma=f"{ch:.4f}", hue_deg=f"{hu:.2f}",
                                     chroma_ratio=f"{ch/bch:.4f}",
                                     hue_shift_deg=f"{circ_diff(hu, bhu):.2f}"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote {len(rows)} rows to {OUT}")

    pert = [r for r in rows if r["kind"] == "perturbed"]
    out = []
    for p in PROBES:
        sel = [r for r in pert if r["probe"] == p]
        cr = [float(r["chroma_ratio"]) for r in sel]
        iou = [float(r["iou"]) for r in sel]
        out.append(dict(probe=p, n=len(sel),
                        chroma_ratio_mean=f"{statistics.fmean(cr):.4f}",
                        chroma_ratio_min=f"{min(cr):.4f}",
                        cells_chroma_below_0_5=sum(1 for x in cr if x < 0.5),
                        iou_mean=f"{statistics.fmean(iou):.4f}",
                        cells_iou_below_0_5=sum(1 for x in iou if x < 0.5),
                        cells_kept_and_bleached=sum(1 for r in sel
                                                    if float(r["iou"]) >= 0.70
                                                    and float(r["chroma_ratio"]) < 0.50)))
    # Paired test on the declared/undeclared asymmetry, with the unit the tool's condition
    # (block x sign, 12 of them) and not the render -- pitfall 17. Hue is undefined where the
    # chroma is gone, so cells below 20% of the baseline chroma are dropped from the hue test.
    def cond_mean(probe, blk, sg):
        v = [float(r["hue_shift_deg"]) for r in pert
             if r["probe"] == probe and r["block"] == blk and r["sign"] == sg
             and float(r["chroma_ratio"]) >= 0.20]
        return statistics.fmean(v) if v else None
    pairs = []
    for blk in BLOCKS:
        for sg in SIGNS:
            ln, lp, lg = (cond_mean(x, blk, sg) for x in ("LN", "LP", "LG"))
            if None not in (ln, lp, lg):
                pairs.append((blk, sg, ln, lp, lg))
    def sign_test(wins, n):
        p = 2 * sum(math.comb(n, i) for i in range(wins, n + 1)) / 2**n
        return min(p, 1.0)
    w_lp = sum(1 for _, _, ln, lp, _ in pairs if ln > lp)
    w_lg = sum(1 for _, _, ln, _, lg in pairs if ln > lg)
    tests = [
        dict(test="LN>LP", detail="conditions where the undeclared probe moves more than declared purple",
             n=len(pairs), value=f"{w_lp}/{len(pairs)}", p=f"{sign_test(w_lp, len(pairs)):.5f}"),
        dict(test="LN>LG", detail="conditions where the undeclared probe moves more than declared green",
             n=len(pairs), value=f"{w_lg}/{len(pairs)}", p=f"{sign_test(w_lg, len(pairs)):.5f}"),
    ]
    for p_ in PROBES:
        v = [float(r["hue_shift_deg"]) for r in pert
             if r["probe"] == p_ and float(r["chroma_ratio"]) >= 0.20]
        tests.append(dict(test=f"{p_} hue shift", detail="mean over cells with hue still defined",
                          n=len(v), value=f"{statistics.fmean(v):.1f} deg",
                          p=f"max {max(v):.1f} deg"))
    # Chroma is a separate axis from hue and nothing pre-registered looked at it. Per block:
    # does the chroma ratio sit on opposite sides of 1 for the two arms, in every cell?
    for blk in BLOCKS:
        cell = {sg: [float(r["chroma_ratio"]) for r in pert
                     if r["block"] == blk and r["sign"] == sg] for sg in SIGNS}
        up = sum(1 for v in cell["pos"] if v > 1) + sum(1 for v in cell["neg"] if v < 1)
        dn = sum(1 for v in cell["pos"] if v < 1) + sum(1 for v in cell["neg"] if v > 1)
        n = len(cell["pos"]) + len(cell["neg"])
        k = max(up, dn)
        tests.append(dict(
            test=f"{blk} chroma antisymmetry",
            detail=f"pos x{statistics.fmean(cell['pos']):.3f}, neg x{statistics.fmean(cell['neg']):.3f}"
                   f" -- cells on the consistent side of 1",
            n=n, value=f"{k}/{n}",
            p=f"{min(1.0, 2*sum(math.comb(n, i) for i in range(k, n+1))/2**n):.5f}"))
    # Hue against chroma: which of the two actually moves.
    hs = [float(r["hue_shift_deg"]) for r in pert if float(r["chroma_ratio"]) >= 0.20]
    cr = [abs(math.log(float(r["chroma_ratio"]))) for r in pert if float(r["chroma_ratio"]) >= 0.20]
    tests.append(dict(test="hue vs chroma", n=len(hs),
                      detail="mean |hue shift| in degrees against mean |log chroma ratio| in percent",
                      value=f"{statistics.fmean(hs):.1f} deg",
                      p=f"{100*(math.exp(statistics.fmean(cr))-1):.1f} pct"))
    with open(OUT_T, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["test", "detail", "n", "value", "p"]); w.writeheader()
        for r in tests: w.writerow(r)
    with open(OUT_S, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader()
        for r in out: w.writerow(r)
    for r in out + tests:
        print("  " + "  ".join(f"{k}={v}" for k, v in r.items() if v != ""))


if __name__ == "__main__":
    main()
