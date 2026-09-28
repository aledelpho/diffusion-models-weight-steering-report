#!/usr/bin/env python3
"""How much style does an edit buy, and how much of the picture does it cost?

Alessandro's observation on two `Block_4` renders: "changed the style noticeably and did not ruin
the image". This makes that measurable over every bench already on disk and asks whether `Block_4`
is actually special or just happened to be the pair he looked at.

Corpus, all against the benchmark_mappa baselines, prompts P01/P02, seeds 42/777/1337:
  benchmark_mappa            6 groups x 2 arms x 6 doses
  benchmark_profondita/_neg  28 single blocks x 2 arms, dose 0.200
  benchmark_rectified_masks  6 mask conditions x 2 arms, dose 0.200

Two quantities per render, deliberately built from different parts of the image:
  style_shift  -- how far the look moved: the norm of (ln contrast, ln grain, ln chroma,
                  hue shift / 90 deg). Four axes, each already validated elsewhere in the project.
  layout_cost  -- how far the picture moved: RMS difference against the baseline on the 8x
                  downsampled luminance. Low-passed, so grain and film-grain-like texture (which
                  is style) do not count as damage, and composition change does.
  layout_cost_z -- the same after z-scoring both downsampled images. This is the one to argue
                  from. Plain layout_cost is contaminated: a pure change of contrast or brightness
                  moves every pixel and scores as damage, and contrast is already counted as style.
                  Standardising removes tone and leaves composition.

They are NOT divided by one another. A ratio here would put a quantity that can approach zero in
the denominator, which this project has now got wrong three times in one day. Conditions are
ranked by Pareto dominance instead: a condition is on the frontier when no other condition moves
the style further AND costs less layout.

Writes data/style_damage_cells.csv (one row per render) and data/style_damage_frontier.csv
(one row per condition, with the frontier flag). Resumable: set B to a seconds budget.
No render.
"""
import csv, os, time
import numpy as np
from PIL import Image

H = os.path.expanduser("~/mnt")
BASE = f"{H}/benchmark_mappa--renders"
OUT = "data/style_damage_cells.csv"
OUT_F = "data/style_damage_frontier.csv"
P = ["P01", "P02"]
S = ["42", "777", "1337"]
FIELDS = ["family", "condition", "dose", "arm", "prompt", "seed",
          "contrast", "grain", "chroma", "hue_shift_deg", "style_shift", "layout_cost",
          "layout_cost_z"]


def jobs():
    """(family, condition, arm, dose, path template) for every render in the corpus."""
    out = []
    for g in range(1, 7):
        for arm in ("pos", "neg"):
            for d in ("0.020", "0.035", "0.050", "0.080", "0.120", "0.200"):
                out.append(("group", f"Block_{g}", arm, d,
                            f"{BASE}/{{p}}_Block_{g}{arm}_{d}_krea2_seed{{s}}_00001_.png"))
    for b in range(28):
        for arm in ("pos", "neg"):
            root = f"{H}/benchmark_profondita" + ("" if arm == "pos" else "_neg") + "/renders"
            out.append(("subblock", f"blk{b:02d}", arm, "0.200",
                        f"{root}/{{p}}_blk{b:02d}{arm}_0.200_krea2_seed{{s}}_00001_.png"))
    for c in ("B4_mask", "B4_anti", "B6_mask", "B6_anti", "B4B6_mask", "B4B6_anti"):
        for arm in ("pos", "neg"):
            out.append(("mask", c, arm, "0.200",
                        f"{H}/benchmark_rectified_masks/renders/{{p}}_{c}_{arm}_seed{{s}}_00001_.png"))
    return out


def features(path):
    im = Image.open(path)
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
    lp = (4*g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:])**2
    mx = a.max(2); mn = a.min(2); d = mx - mn
    sat = np.where(mx > 1e-5, d / np.maximum(mx, 1e-5), 0.0)
    r, gg, b = a[..., 0], a[..., 1], a[..., 2]
    hue = np.zeros_like(mx)
    m = (mx == r) & (d > 1e-5); hue[m] = (60 * ((gg[m] - b[m]) / d[m]) + 360) % 360
    m = (mx == gg) & (d > 1e-5); hue[m] = (60 * ((b[m] - r[m]) / d[m]) + 120) % 360
    m = (mx == b) & (d > 1e-5); hue[m] = (60 * ((r[m] - gg[m]) / d[m]) + 240) % 360
    w = sat
    ang = np.rad2deg(np.arctan2((w * np.sin(np.deg2rad(hue))).sum(),
                                (w * np.cos(np.deg2rad(hue))).sum())) % 360
    small = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize(
        (g.shape[1] // 8, g.shape[0] // 8), Image.BOX), dtype=np.float32) / 255.0
    return float(lp.mean()), float(g.var()), float(sat.mean()), float(ang), small


def circ(a, b):
    d = abs(a - b) % 360.0
    return d if d <= 180 else 360 - d


def main():
    budget = float(os.environ.get("B", "150")); t0 = time.time()
    done = set()
    if os.path.exists(OUT):
        done = {(r["family"], r["condition"], r["arm"], r["dose"], r["prompt"], r["seed"])
                for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    cache = {}
    def base(p, s):
        if (p, s) not in cache:
            cache[(p, s)] = features(f"{BASE}/{p}_baseline_krea2_seed{s}_00001_.png")
        return cache[(p, s)]
    todo = [(f, c, a, d, t, p, s) for (f, c, a, d, t) in jobs() for p in P for s in S
            if (f, c, a, d, p, s) not in done]
    print(f"done {len(done)}, todo {len(todo)}")
    rows, missing = [], 0
    for (fam, cond, arm, dose, tpl, p, s) in todo:
        if time.time() - t0 > budget:
            print("budget reached, rerun to continue"); break
        f = tpl.format(p=p, s=s)
        if not os.path.exists(f):
            missing += 1; continue
        hb, vb, cb, ab, sb = base(p, s)
        h, v, c, ang, sm = features(f)
        contrast = v / vb
        grain = (h / v) / (hb / vb)
        chroma = c / cb
        dh = circ(ang, ab)
        style = float(np.sqrt(np.log(contrast)**2 + np.log(grain)**2 +
                              np.log(chroma)**2 + (dh / 90.0)**2))
        cost = float(np.sqrt(((sm - sb)**2).mean()))
        za = (sm - sm.mean()) / (sm.std() + 1e-9)
        zb = (sb - sb.mean()) / (sb.std() + 1e-9)
        cost_z = float(np.sqrt(((za - zb)**2).mean()))
        rows.append(dict(family=fam, condition=cond, dose=dose, arm=arm, prompt=p, seed=s,
                         contrast=f"{contrast:.5f}", grain=f"{grain:.5f}", chroma=f"{chroma:.5f}",
                         hue_shift_deg=f"{dh:.2f}", style_shift=f"{style:.5f}",
                         layout_cost=f"{cost:.5f}", layout_cost_z=f"{cost_z:.5f}"))
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new: w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote {len(rows)} rows ({missing} missing), total {len(done)+len(rows)}")





def frontier():
    """Aggregate to conditions and flag the Pareto-non-dominated ones. No ratios."""
    import statistics
    rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
    agg = {}
    for r in rows:
        k = (r["family"], r["condition"], r["arm"], r["dose"])
        agg.setdefault(k, {"style": [], "cost": [], "costz": [], "contrast": [], "grain": [],
                           "chroma": [], "hue": []})
        agg[k]["style"].append(float(r["style_shift"]))
        agg[k]["cost"].append(float(r["layout_cost"]))
        agg[k]["costz"].append(float(r["layout_cost_z"]))
        agg[k]["contrast"].append(float(r["contrast"]))
        agg[k]["grain"].append(float(r["grain"]))
        agg[k]["chroma"].append(float(r["chroma"]))
        agg[k]["hue"].append(float(r["hue_shift_deg"]))
    out = []
    for k, v in agg.items():
        out.append(dict(family=k[0], condition=k[1], arm=k[2], dose=k[3], n=len(v["style"]),
                        style_shift=statistics.fmean(v["style"]),
                        layout_cost=statistics.fmean(v["cost"]),
                        layout_cost_z=statistics.fmean(v["costz"]),
                        contrast=statistics.fmean(v["contrast"]),
                        grain=statistics.fmean(v["grain"]),
                        chroma=statistics.fmean(v["chroma"]),
                        hue_shift_deg=statistics.fmean(v["hue"])))
    for a in out:
        a["on_frontier"] = int(not any(
            b is not a and b["style_shift"] >= a["style_shift"]
            and b["layout_cost_z"] <= a["layout_cost_z"]
            and (b["style_shift"] > a["style_shift"] or b["layout_cost_z"] < a["layout_cost_z"])
            for b in out))
    out.sort(key=lambda r: (-r["on_frontier"], -r["style_shift"]))
    with open(OUT_F, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["family", "condition", "arm", "dose", "n",
                                           "style_shift", "layout_cost", "layout_cost_z",
                                           "contrast", "grain", "chroma", "hue_shift_deg",
                                           "on_frontier"])
        w.writeheader()
        for r in out:
            w.writerow({k: (f"{v:.5f}" if isinstance(v, float) else v) for k, v in r.items()})
    fr = [r for r in out if r["on_frontier"]]
    print(f"{len(out)} conditions, {len(fr)} on the frontier -> {OUT_F}")
    for r in fr:
        print("  %-9s %-11s %-4s %-6s style %.4f  cost_z %.4f  (contrast %.3f grain %.3f "
              "chroma %.3f hue %.1f)" % (r["family"], r["condition"], r["arm"], r["dose"],
                                         r["style_shift"], r["layout_cost_z"], r["contrast"],
                                         r["grain"], r["chroma"], r["hue_shift_deg"]))


if __name__ == "__main__":
    if os.environ.get("FRONTIER_ONLY"):
        frontier()
    else:
        main()
        frontier()
