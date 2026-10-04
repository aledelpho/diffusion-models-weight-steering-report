"""Score the residual probe (docs/prereg_residual_probe.md). Code fixed before data.

  python experiments/analyze_residual_probe.py --repro   # probe images == existing baselines?
  python experiments/analyze_residual_probe.py           # per-block table + pre-registered tests
Reads data/residual_probe_raw.csv; writes data/residual_probe_blocks.csv and
data/residual_probe_test.csv.
"""
import argparse, csv, glob, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt")


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def resid(y, x):
    X = np.column_stack([np.ones_like(x), x, x ** 2])
    return y - X @ np.linalg.lstsq(X, y, rcond=None)[0]


def repro():
    from PIL import Image
    src = {"styles": "benchmark_single_blocks_styles", "v3": "benchmark_single_blocks_v3", "v4": "benchmark_single_blocks_v4"}
    probe = glob.glob(os.path.join(ROOT, "benchmark_residual_probe", "PROBE_*.png"))
    bad = 0
    for p in sorted(probe):
        label = os.path.basename(p)[len("PROBE_"):].rsplit("_", 2)[0]  # <prompt>_seed<seed>
        pid, seed = label.rsplit("_seed", 1)
        ref = [f for d in src.values() for f in glob.glob(os.path.join(ROOT, d, "renders", f"{pid}_baseline_krea2_seed{seed}_*.png"))]
        if not ref:
            print("no reference for", label); bad += 1; continue
        a = np.asarray(Image.open(p), dtype=np.int16); b = np.asarray(Image.open(ref[0]), dtype=np.int16)
        mx = int(np.abs(a - b).max()) if a.shape == b.shape else -1
        print(label, "max abs diff", mx); bad += mx != 0
    print("REPRO", "PASS" if bad == 0 and probe else "FAIL", len(probe), "images")


def main():
    raw = list(csv.DictReader(open(os.path.join(DATA, "residual_probe_raw.csv"))))
    keys = ["stream", "write", "ratio", "attn_write", "mlp_write", "cos_write_stream"]
    agg = {b: {k: [] for k in keys} for b in range(28)}
    for r in raw:
        for k in keys:
            agg[int(r["block"])][k].append(float(r[k]))
    out = []
    for b in range(28):
        row = {"block": b}
        for k in keys:
            row[k] = round(float(np.mean(agg[b][k])), 6)
        row["attn_ratio"] = round(row["attn_write"] / row["stream"], 6)
        row["mlp_ratio"] = round(row["mlp_write"] / row["stream"], 6)
        out.append(row)
    with open(os.path.join(DATA, "residual_probe_blocks.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    lay = {}
    for r in csv.DictReader(open(os.path.join(DATA, "block_colour_layout.csv"))):
        lay.setdefault(int(r["block"][3:]), []).append(float(r["layout_r"]))
    stab = np.array([np.mean(lay[b]) for b in range(28)])
    blk = np.arange(28.0)
    ratio = np.array([o["ratio"] for o in out]); stream = np.array([o["stream"] for o in out])
    mlp = np.array([o["mlp_ratio"] for o in out])
    t = []
    rho1 = spearman(ratio, stab)
    t.append(["P1 ratio vs stability (raw)", round(rho1, 3),
              "supported" if rho1 <= -0.5 else ("refuted" if rho1 > -0.3 else "inconclusive")])
    t.append(["P1b ratio vs stability (depth removed, reported)", round(spearman(resid(ratio, blk), resid(stab, blk)), 3), ""])
    mid = list(range(2, 21)); top = max(mid, key=lambda b: mlp[b])
    t.append(["P2 block with largest mlp_ratio among 02-20", top, "supported" if top in (8, 9) else "refuted"])
    rho3 = spearman(stream, blk)
    t.append(["P3 stream norm vs depth", round(rho3, 3), "supported" if rho3 >= 0.8 else "refuted"])
    with open(os.path.join(DATA, "residual_probe_test.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["test", "value", "verdict"]); w.writerows(t)
    for r in t:
        print(r)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--repro", action="store_true")
    repro() if ap.parse_args().repro else main()
