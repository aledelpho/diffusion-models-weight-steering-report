"""C96 - micro-watersheds: do minimal edits flip the same small regions? (docs/prereg_micro_watersheds.md)
Written 2026-10-18 with the pre-registration, before any computation. No renders.

  python micro_watersheds.py            # data/micro_watersheds_edits.csv, _pairs.csv, _tests.csv; maps in Text2Img/_micro_watersheds
  python micro_watersheds.py --selftest
"""
import argparse, csv, itertools, statistics, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
sys.path.insert(0, str(HERE))
P = 16          # token size in pixels
FLIP = 32       # flip threshold, 0-255


def img_root():
    import blk23_colorful as c47
    return c47.IMG_ROOT if c47.IMG_ROOT.exists() else Path.home() / "mnt" / "D:--StabilityMatrix-win-x64--Data--Images--Text2Img"


def load(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def files():
    r = img_root(); L = r / "benchmark_hood_threshold"; N = r / "benchmark_null_patch"
    base = L / "P3_archerforest_baseline_krea2_seed3141592_00001_.png"
    small, large = [], []
    for b in ("00", "10", "20", "23"):
        for s in ("neg", "pos"):
            for d in ("0.010", "0.020", "0.040"):
                small.append((f"blk{b}_{s}_{d}", L / f"P3_archerforest_blk{b}_{s}_d{d}_krea2_seed3141592_00001_.png"))
            for d in ("0.080", "0.160"):
                large.append((f"blk{b}_{s}_{d}", L / f"P3_archerforest_blk{b}_{s}_d{d}_krea2_seed3141592_00001_.png"))
    small += [("blk27_pos_0.004", N / "P3_archerforest_N3_blk27_p0.004_krea2_seed3141592_00001_.png"),
              ("blk27_neg_0.004", N / "P3_archerforest_N4_blk27_m0.004_krea2_seed3141592_00001_.png")]
    return base, N / "P3_archerforest_N0_baseline_krea2_seed3141592_00001_.png", small, large


def patches(a):
    h, w = a.shape[0] // P * P, a.shape[1] // P * P
    return a[:h, :w].reshape(h // P, P, w // P, P).mean(axis=(1, 3))


def texture(base):
    y = (0.299 * base[..., 0] + 0.587 * base[..., 1] + 0.114 * base[..., 2]).astype(np.float32)
    gx = np.zeros_like(y); gy = np.zeros_like(y)
    gx[1:-1, 1:-1] = (y[:-2, 2:] + 2 * y[1:-1, 2:] + y[2:, 2:]) - (y[:-2, :-2] + 2 * y[1:-1, :-2] + y[2:, :-2])
    gy[1:-1, 1:-1] = (y[2:, :-2] + 2 * y[2:, 1:-1] + y[2:, 2:]) - (y[:-2, :-2] + 2 * y[:-2, 1:-1] + y[:-2, 2:])
    return patches(np.hypot(gx, gy))


def ranks(v):
    from scipy.stats import rankdata
    return rankdata(v)


def partial_rho(x, y, z):
    """Pearson correlation of log(1 + patch energy) after a linear regression on log(1 + texture).
    (Changed before any real data was read: Spearman over all patches was dominated by the ordering of the
    near-zero shimmer and missed sparse flips in the selftest.)"""
    lx, ly, lz = np.log1p(x), np.log1p(y), np.log1p(z)
    A = np.vstack([lz, np.ones_like(lz)]).T
    ex = lx - A @ np.linalg.lstsq(A, lx, rcond=None)[0]
    ey = ly - A @ np.linalg.lstsq(A, ly, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


def bimodality(v):
    from scipy.stats import skew, kurtosis
    n = len(v)
    g, k = skew(v), kurtosis(v)          # excess kurtosis
    return float((g ** 2 + 1) / (k + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))))


def analyze(base_img, edits, tex, large=()):
    """edits/large: [(name, image array)]. Returns per-edit rows, pair rows, test rows."""
    rows, E = [], {}
    for name, im in list(edits) + list(large):
        d = np.abs(im - base_img).max(axis=2).astype(np.float32)
        tot = float((d ** 2).sum())
        share = float((d[d >= FLIP] ** 2).sum() / tot) if tot else 0.0
        E[name] = patches(d ** 2).ravel()
        from scipy.ndimage import label
        lab, n = label(d >= FLIP, structure=np.ones((3, 3)))
        sizes = np.bincount(lab.ravel())[1:] if n else np.array([])
        rows.append({"edit": name, "set": "small" if name in dict(edits) else "large", "pixels_changed": round(float((d > 0).mean()), 4),
                     "mean_delta": round(float(d.mean()), 3), "flip_share": round(share, 4), "flip_regions": int(n),
                     "median_region_px": int(np.median(sizes)) if n else 0, "max_delta": int(d.max())})
    t = tex.ravel(); pairs = []
    names = [n for n, _ in edits]
    for a, b in itertools.combinations(names, 2):
        sa, sb = a.split("_"), b.split("_")
        pairs.append({"a": a, "b": b, "rho_partial": round(partial_rho(E[a], E[b], t), 4),
                      "rho_raw": round(float(np.corrcoef(np.log1p(E[a]), np.log1p(E[b]))[0, 1]), 4),
                      "same_block": int(sa[0] == sb[0]), "opposite_sign": int(sa[1] != sb[1])})
    out = []
    sh = [r["flip_share"] for r in rows if r["set"] == "small"]
    hi, lo = sum(s >= 0.5 for s in sh), sum(s <= 0.2 for s in sh)
    v1 = "supported" if hi >= 2 / 3 * len(sh) else ("refuted" if lo >= 2 / 3 * len(sh) else "inconclusive")
    out.append({"test": "T1 flips carry the change (share of squared change at delta >= 32)", "value": f"share >= 0.50 in {hi} of {len(sh)}, <= 0.20 in {lo}; median {statistics.median(sh):.3f}", "verdict": v1})
    mp = statistics.median(p["rho_partial"] for p in pairs)
    v2 = "supported" if mp >= 0.30 else ("refuted" if mp <= 0.10 else "inconclusive")
    out.append({"test": "T2 the same places flip, texture removed (median partial correlation of log patch energy over pairs)", "value": f"{mp:.3f} over {len(pairs)} pairs; raw {statistics.median(p['rho_raw'] for p in pairs):.3f}", "verdict": v2})
    for lab_, sel in (("different blocks", lambda p: not p["same_block"]), ("opposite signs", lambda p: p["opposite_sign"]),
                      ("same block, same sign", lambda p: p["same_block"] and not p["opposite_sign"])):
        s = [p["rho_partial"] for p in pairs if sel(p)]
        if s:
            out.append({"test": f"T2 partial rho, {lab_} (reported)", "value": f"median {statistics.median(s):.3f} (n {len(s)})", "verdict": ""})
    return rows, pairs, out, E


def t3(base_img, all_edits, out):
    D = [np.abs(im - base_img).max(axis=2).astype(np.float32) for _, im in all_edits]
    pm = np.array([patches(d) for d in D])                          # edits x H x W patch means of delta
    rec = np.argwhere((pm >= FLIP).mean(0) >= 0.25)
    if len(rec) < 10:
        out.append({"test": "T3 two solutions (bimodality of recurring patches)", "value": f"{len(rec)} recurring patches (< 10)", "verdict": "not reported (too few)"})
        return
    stack = [base_img] + [im for _, im in all_edits]
    bc = []
    for i, j in rec:
        X = np.array([s[i * P:(i + 1) * P, j * P:(j + 1) * P].reshape(-1).astype(np.float32) for s in stack])
        X -= X.mean(0)
        u, sv, vt = np.linalg.svd(X, full_matrices=False)
        bc.append(bimodality(u[:, 0] * sv[0]))
    k = sum(b > 0.555 for b in bc)
    out.append({"test": "T3 two solutions: recurring patches with bimodality coefficient > 0.555", "value": f"{k} of {len(bc)} ({k / len(bc):.2f}); median BC {statistics.median(bc):.3f}",
                "verdict": "supported" if k >= 0.5 * len(bc) else "not supported"})


def save_maps(base_img, edits, E, shape, outdir):
    from PIL import Image
    outdir.mkdir(parents=True, exist_ok=True)
    h, w = shape[0] // P, shape[1] // P
    freq = np.mean([(E[n].reshape(h, w) >= FLIP ** 2) for n, _ in edits], axis=0)
    hm = (255 * freq / max(freq.max(), 1e-9)).astype(np.uint8)
    Image.fromarray(hm).resize((w * P, h * P), Image.NEAREST).save(outdir / "flip_frequency_small.png")
    ov = base_img[: h * P, : w * P].astype(np.float32) * 0.5
    up = np.kron(freq, np.ones((P, P)))
    ov[..., 0] += 127 * up / max(up.max(), 1e-9)
    Image.fromarray(np.clip(ov, 0, 255).astype(np.uint8)).save(outdir / "flip_frequency_overlay.png")


def run():
    base_p, n0_p, small, large = files()
    base = load(base_p)
    d0 = int(np.abs(base - load(n0_p)).max())
    print("baseline vs C55 N0: max abs diff", d0)
    if d0 != 0:
        sys.exit("STOP: the two baselines differ")
    S = [(n, load(p)) for n, p in small]; L = [(n, load(p)) for n, p in large]
    rows, pairs, out, E = analyze(base, S, texture(base), L)
    t3(base, S + L, out)
    for name, fn, data in (("edits", "micro_watersheds_edits.csv", rows), ("pairs", "micro_watersheds_pairs.csv", pairs), ("tests", "micro_watersheds_tests.csv", out)):
        with open(DATA / fn, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    save_maps(base, S, E, base.shape, img_root() / "_micro_watersheds")
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


def selftest():
    """Synthetic: a textured base; every edit flips the same 6 non-textured blobs to one of two states."""
    rng = np.random.default_rng(0)
    base = np.full((256, 256, 3), 100, np.int16); base[:, :128] += rng.integers(0, 60, (256, 128, 3)).astype(np.int16)
    blobs = [(i * 32 + 8, 160 + (i % 3) * 30) for i in range(6)]
    edits = []
    for e in range(8):
        im = base.copy()
        for (y, x) in blobs:
            if rng.random() < 0.7:
                im[y:y + 16, x:x + 16] = 100 + (120 if rng.random() < 0.5 else -80)
        im += rng.integers(-2, 3, im.shape).astype(np.int16)
        edits.append((f"blk0{e % 4}_{'pos' if e % 2 else 'neg'}_0.01", im))
    rows, pairs, out, E = analyze(base, edits, texture(base))
    assert out[0]["verdict"] == "supported", out[0]
    assert out[1]["verdict"] == "supported", out[1]
    # negative control: each edit flips 6 blobs at its own random places -> T2 must not be supported
    edits2 = []
    for e in range(8):
        im = base.copy()
        for _ in range(6):
            y, x = int(rng.integers(0, 240)), int(rng.integers(128, 240))
            im[y:y + 16, x:x + 16] = 220
        im += rng.integers(-2, 3, im.shape).astype(np.int16)
        edits2.append((f"blk0{e % 4}_{'pos' if e % 2 else 'neg'}_0.01", im))
    _, _, out2, _ = analyze(base, edits2, texture(base))
    assert out2[1]["verdict"] != "supported", out2[1]
    print("selftest ok", out[1]["value"], "| control:", out2[1]["value"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    selftest() if ap.parse_args().selftest else run()
