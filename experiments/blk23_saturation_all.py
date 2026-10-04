"""Does blk23 move saturation the same way on every image we have?

Every bench that contains blk23 arms: single_blocks_atlas (3 prompts, +-0.350),
prompt_order (5 orders x 2 seeds, +-0.350), single_blocks_styles (12 prompts, +-0.300),
single_blocks_v3 / v4 (11 prompts, -0.300, +0.150, +0.300).
For every arm of every block (not only blk23, so blk23 can be compared with the
rest): change of mean HSV saturation and of mean CIELAB chroma against the baseline of
the same prompt and seed, at 256x320.
Writes data/blk23_saturation_all.csv (one row per image).
"""
import csv, glob, os, re
import numpy as np
from PIL import Image

ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt")
BENCH = {
    "atlas": os.path.join(ROOT, "benchmark_single_blocks_atlas", "renders"),
    "prompt_order": os.path.join(ROOT, "benchmark_prompt_order"),
    "styles": os.path.join(ROOT, "benchmark_single_blocks_styles", "renders"),
    "v3": os.path.join(ROOT, "benchmark_single_blocks_v3", "renders"),
    "v4": os.path.join(ROOT, "benchmark_single_blocks_v4", "renders"),
}
PAT = re.compile(r"^(.+?)_(blk\d\d)_(pos|neg)_d([\d.]+)_krea2_seed(\d+)_")
BASE = re.compile(r"^(.+?)_baseline_krea2_seed(\d+)_")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "blk23_saturation_all.csv")


def stats(path):
    im = Image.open(path).convert("RGB").resize((256, 320), Image.BOX)
    s = np.asarray(im.convert("HSV"), dtype=np.float64)[..., 1].mean() / 255.0
    a = np.asarray(im, dtype=np.float64) / 255.0
    a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    xyz = a @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    chroma = np.hypot(500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])).mean()
    return s, chroma


def main():
    rows = []
    for bench, d in BENCH.items():
        files = [os.path.basename(f) for f in glob.glob(os.path.join(d, "*.png"))]
        base = {}
        for f in files:
            m = BASE.match(f)
            if m:
                base[(m[1], m[2])] = stats(os.path.join(d, f))
        for f in files:
            m = PAT.match(f)
            if not m or (m[1], m[5]) not in base:
                continue
            s, c = stats(os.path.join(d, f))
            s0, c0 = base[(m[1], m[5])]
            rows.append([bench, m[1], m[5], m[2], m[3], m[4], round(s - s0, 5), round(c - c0, 4)])
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["bench", "prompt", "seed", "block", "sign", "dose", "d_hsv_sat", "d_chroma"])
        w.writerows(rows)
    print(len(rows), "images")


if __name__ == "__main__":
    main()
