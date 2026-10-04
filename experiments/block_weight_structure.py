"""C46: per-block weight statistics of Krea-2 (read-only), and the pre-registered test.

Pre-registration: docs/prereg_block_weight_structure.md (commit ec03c89), written
before any weight was read for this question.

  python experiments/block_weight_structure.py --measure [--blocks 0-27]   (resumable)
  python experiments/block_weight_structure.py --test

No torch / safetensors needed: the header is parsed by hand, BF16 is widened to F32.
Outputs: data/block_weight_structure.csv, data/block_weight_structure_test.csv
"""
import argparse, csv, json, os, struct
import numpy as np

CKPT = r"C:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\krea2_turbo_bf16.safetensors"
if not os.path.exists(CKPT):
    CKPT = os.path.expanduser("~/mnt/DiffusionModels/krea2_turbo_bf16.safetensors")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(DATA, "block_weight_structure.csv")
TWO_D = ["attn.wq", "attn.wk", "attn.wv", "attn.wo", "attn.gate", "mlp.up", "mlp.gate", "mlp.down"]
ONE_D = ["attn.qknorm.qnorm.scale", "attn.qknorm.knorm.scale", "prenorm.scale", "postnorm.scale"]


def header():
    f = open(CKPT, "rb")
    n = struct.unpack("<Q", f.read(8))[0]
    return f, 8 + n, json.loads(f.read(n))


def load(f, base, info):
    a, b = info["data_offsets"]
    f.seek(base + a)
    buf = f.read(b - a)
    if info["dtype"] == "BF16":
        x = (np.frombuffer(buf, dtype=np.uint16).astype(np.uint32) << 16).view(np.float32)
    elif info["dtype"] == "F32":
        x = np.frombuffer(buf, dtype=np.float32).copy()
    else:
        raise ValueError(info["dtype"])
    return x.reshape(info["shape"])


def sigma1(W, steps=50):
    rng = np.random.default_rng(0)
    v = rng.standard_normal(W.shape[1]).astype(np.float32)
    v /= np.linalg.norm(v)
    s = 0.0
    for _ in range(steps):
        u = W @ v
        s = float(np.linalg.norm(u))
        v = W.T @ (u / s)
        v /= np.linalg.norm(v)
    return float(np.linalg.norm(W @ v))


def measure(blocks):
    f, base, h = header()
    done = set()
    if os.path.exists(OUT):
        done = {int(r["block"]) for r in csv.DictReader(open(OUT))}
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="") as fh:
        w = None
        for b in blocks:
            if b in done:
                continue
            row = {"block": b}
            for t in TWO_D:
                W = load(f, base, h[f"blocks.{b}.{t}.weight"])
                fro = float(np.linalg.norm(W))
                s1 = sigma1(W)
                row[f"{t}.fro"] = round(fro, 5)
                row[f"{t}.sigma1"] = round(s1, 5)
                row[f"{t}.stable_rank"] = round(fro ** 2 / s1 ** 2, 3)
                del W
            for t in ONE_D:
                x = load(f, base, h[f"blocks.{b}.{t}"])
                row[f"{t}.mean"] = round(float(x.mean()), 6)
                row[f"{t}.sd"] = round(float(x.std()), 6)
            m = load(f, base, h[f"blocks.{b}.mod.lin"]).reshape(6, -1)
            for i in range(6):
                row[f"mod.lin.chunk{i}.norm"] = round(float(np.linalg.norm(m[i])), 5)
            row["attn_write_proxy"] = round(row["attn.wo.sigma1"] * row["attn.wv.sigma1"], 5)
            row["mlp_write_proxy"] = round(row["mlp.down.sigma1"] * max(row["mlp.up.sigma1"], row["mlp.gate.sigma1"]), 5)
            if w is None:
                w = csv.DictWriter(fh, fieldnames=list(row))
                if new:
                    w.writeheader()
            w.writerow(row)
            fh.flush()
            print("block", b, "done", flush=True)


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def resid(y, x):
    X = np.column_stack([np.ones_like(x), x, x ** 2])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def test():
    W = sorted(csv.DictReader(open(OUT)), key=lambda r: int(r["block"]))
    assert len(W) == 28, len(W)
    lay = {}
    for r in csv.DictReader(open(os.path.join(DATA, "block_colour_layout.csv"))):
        lay.setdefault(int(r["block"][3:]), []).append(float(r["layout_r"]))
    blk = np.arange(28, dtype=float)
    stab = np.array([np.mean(lay[b]) for b in range(28)])
    stats = [k for k in W[0] if k != "block" and not k.startswith("mod.lin.chunk")]
    assert len(stats) == 34, len(stats)
    rs = resid(stab, blk)
    rows = []
    for k in stats:
        v = np.array([float(r[k]) for r in W])
        rows.append([k, round(spearman(v, stab), 3), round(spearman(resid(v, blk), rs), 3)])
    rows.sort(key=lambda r: -abs(r[2]))
    best = abs(rows[0][2])
    verdict = "H_struct supported" if best >= 0.57 else ("H_depth supported" if best < 0.40 else "inconclusive")
    with open(os.path.join(DATA, "block_weight_structure_test.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["statistic", "rho_raw", "rho_depth_removed"])
        w.writerows(rows)
        w.writerow(["VERDICT", verdict, round(best, 3)])
    for r in rows[:8]:
        print(r)
    print("best |rho| depth removed:", round(best, 3), "->", verdict)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--blocks", default="0-27")
    a = ap.parse_args()
    lo, hi = map(int, a.blocks.split("-"))
    if a.measure:
        measure(range(lo, hi + 1))
    if a.test:
        test()
