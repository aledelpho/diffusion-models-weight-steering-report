#!/usr/bin/env python3
"""Three-way energy decomposition of the signed block map, and viewable c/m maps.

Follow-up to experiments/sign_decomposition_pixels.py, same corpus, same
pre-registration (docs/prereg_sign_decomposition_pixels.md). This is the part the
cosines of that script could only be inferred from: it splits the pixel change into

    G        the global mode   -- identical for every block and every sign
    c_b - G  the block mode    -- says which block was touched, not which way
    m_b      the signed mode   -- the only part the sign controls

computed on the vectors themselves, not inferred from pairwise cosines.

Declared post-hoc: this decomposition was written after reading the cosines, because
the cosine table did not close (different-block 0.411 < F 0.673, which the two-term
model forbids). It is exploratory and is labelled as such.
"""
import os, csv, collections
import numpy as np
from PIL import Image

RENDERS = os.environ.get("MAPPA_RENDERS", os.path.expanduser("~/mnt/benchmark_mappa--renders"))
OUT = "data/sign_decomposition_variance.csv"
MAPDIR = os.path.expanduser("~/mnt/outputs/sign_maps")

PROMPTS = ["P01", "P02"]
SEEDS = ["42", "777", "1337"]
DOSES = ["0.020", "0.035", "0.050", "0.080", "0.120", "0.200"]
BLOCKS = ["Block_1", "Block_2", "Block_3", "Block_4", "Block_5", "Block_6"]
EXTRA = ["Projection", "Text_Fusion", "Time_Embed"]
FIELDS = ["prompt", "seed", "dose", "n_blocks", "E_total", "E_global", "E_block", "E_signed",
          "frac_global", "frac_block", "frac_signed", "hf_global", "hf_block", "hf_signed"]


def load(p):
    im = Image.open(p)
    assert im.size == (1024, 1280) and im.mode == "RGB", (p, im.size, im.mode)
    return np.asarray(im, dtype=np.float32) / 255.0


def e(x):
    return float(np.sum(x.astype(np.float64) ** 2))


def hf(x):
    d = e(x)
    if d == 0:
        return float("nan")
    lap = (4.0 * x[1:-1, 1:-1, :] - x[:-2, 1:-1, :] - x[2:, 1:-1, :]
           - x[1:-1, :-2, :] - x[1:-1, 2:, :])
    return e(lap) / d


def savemap(arr, path, gain):
    """Signed difference map -> viewable PNG. Grey 128 = no change. Gain is printed in the name."""
    v = np.clip(arr * gain * 127.5 + 127.5, 0, 255).astype(np.uint8)
    Image.fromarray(v).save(path)


def main():
    os.makedirs(MAPDIR, exist_ok=True)
    have = set()
    if os.path.exists(OUT):
        have = {(r["prompt"], r["seed"], r["dose"]) for r in csv.DictReader(open(OUT))}
    rows = []
    import time
    t0 = time.time()
    for p in PROMPTS:
        for s in SEEDS:
            base = None
            for d in DOSES:
                if (p, s, d) in have:
                    continue
                if time.time() - t0 > float(os.environ.get("CHUNK_BUDGET_S", "140")):
                    print("budget reached, rerun")
                    _flush(rows); return
                if base is None:
                    base = load(os.path.join(RENDERS, f"{p}_baseline_krea2_seed{s}_00001_.png"))
                D = {}
                for b in BLOCKS:
                    for sg in ("pos", "neg"):
                        D[(b, sg)] = load(os.path.join(
                            RENDERS, f"{p}_{b}{sg}_{d}_krea2_seed{s}_00001_.png")) - base
                G = sum(D.values()) / len(D)
                Eg = e(G)
                Eb = np.mean([e(0.5 * (D[(b, "pos")] + D[(b, "neg")]) - G) for b in BLOCKS])
                Em = np.mean([e(0.5 * (D[(b, "pos")] - D[(b, "neg")])) for b in BLOCKS])
                Et = Eg + Eb + Em
                hb = np.mean([hf(0.5 * (D[(b, "pos")] + D[(b, "neg")]) - G) for b in BLOCKS])
                hm = np.mean([hf(0.5 * (D[(b, "pos")] - D[(b, "neg")])) for b in BLOCKS])
                rows.append(dict(prompt=p, seed=s, dose=d, n_blocks=len(BLOCKS),
                                 E_total=f"{Et:.6f}", E_global=f"{Eg:.6f}",
                                 E_block=f"{Eb:.6f}", E_signed=f"{Em:.6f}",
                                 frac_global=f"{Eg/Et:.6f}", frac_block=f"{Eb/Et:.6f}",
                                 frac_signed=f"{Em/Et:.6f}",
                                 hf_global=f"{hf(G):.6f}", hf_block=f"{hb:.6f}",
                                 hf_signed=f"{hm:.6f}"))
                print(f"  {p} seed{s} d={d}: global {Eg/Et:.3f} block {Eb/Et:.3f} signed {Em/Et:.3f}")
                # viewable maps for one reference cell only
                if p == "P01" and s == "42" and d == "0.200":
                    savemap(G, f"{MAPDIR}/{p}_s{s}_d{d}_GLOBAL_gain8.png", 8)
                    for b in ("Block_1", "Block_6"):
                        cb = 0.5 * (D[(b, "pos")] + D[(b, "neg")])
                        mb = 0.5 * (D[(b, "pos")] - D[(b, "neg")])
                        savemap(cb, f"{MAPDIR}/{p}_s{s}_d{d}_{b}_COMMON_gain8.png", 8)
                        savemap(mb, f"{MAPDIR}/{p}_s{s}_d{d}_{b}_SIGNED_gain8.png", 8)
                        savemap(cb - G, f"{MAPDIR}/{p}_s{s}_d{d}_{b}_BLOCKONLY_gain16.png", 16)
                del D
    _flush(rows)


def _flush(rows):
    if not rows:
        return
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} rows")


if __name__ == "__main__":
    main()
