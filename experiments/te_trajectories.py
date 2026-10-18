"""C89 - does the push of a text-encoder edit keep its direction as the dose grows? (docs/prereg_te_trajectories.md)
Written 2026-10-18 with the pre-registration, before any computation. No renders: C64 encodes of the elf.

  python te_trajectories.py            # writes data/te_trajectories.csv, data/te_trajectories_tests.csv
  python te_trajectories.py --selftest
"""
import argparse, csv, re, statistics, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
sys.path.insert(0, str(HERE))
DOSES = ["0.10", "0.35", "1.00"]


def ang(a, b):
    return float(np.degrees(np.arccos(np.clip(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12), -1, 1))))


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def measure(P, Pm=None):
    """P: dict dose -> normalised push vector (sign +), Pm: same for the opposite sign at 0.10 (optional)."""
    c = cos(P["0.10"], P["1.00"])
    a = ang(P["0.10"], P["0.35"]) + ang(P["0.35"], P["1.00"]); b = ang(P["0.10"], P["1.00"])
    return {"bend_c": round(c, 4), "path_a": round(a, 2), "chord_b": round(b, 2),
            "arc": int(a <= 1.2 * b or b < 1.0),  # b < 1 degree: no turn at all, counted as an arc
            "norm_1": round(float(np.linalg.norm(P["1.00"])), 4),
            "sym": round(cos(P["0.10"], -Pm), 4) if Pm is not None else ""}


def verdict(rows):
    use = [r for r in rows if r["used"]]
    med = statistics.median(r["norm_1"] for r in use)
    strong = [r for r in use if r["norm_1"] > med]
    mc = statistics.median(r["bend_c"] for r in strong)
    low = [r for r in strong if r["bend_c"] <= 0.50]
    arcs = sum(r["arc"] for r in low)
    if mc >= 0.90: v = "straight"
    elif mc <= 0.50 and low and arcs >= 2 / 3 * len(low): v = "curved, in arcs"
    else: v = "in between"
    out = [{"test": "Rule: median bend c, strong trajectories", "value": f"{mc:.3f} over {len(strong)} (all used: {statistics.median(r['bend_c'] for r in use):.3f} over {len(use)}); arcs among c<=0.50: {arcs} of {len(low)}", "verdict": v}]
    for half in ("attn", "mlp"):
        for sg in ("p", "m"):
            s = [r["bend_c"] for r in use if r["half"] == half and r["sign"] == sg]
            if s:
                out.append({"test": f"median c, {half}, sign {sg} (reported)", "value": f"{statistics.median(s):.3f} (n {len(s)}, min {min(s):.3f})", "verdict": ""})
    sy = [r["sym"] for r in use if r["sym"] != ""]
    if sy:
        out.append({"test": "sign symmetry cos(p(+0.10), -p(-0.10)) (reported)", "value": f"median {statistics.median(sy):.3f}, min {min(sy):.3f}, n {len(sy)}", "verdict": ""})
    worst = sorted(use, key=lambda r: r["bend_c"])[:8]
    out.append({"test": "most bent trajectories (reported)", "value": " ".join(f"L{r['layer']:02d}{r['half']}{r['sign']}:{r['bend_c']:.2f}" for r in worst), "verdict": ""})
    return out


def run():
    import blk23_colorful as c47
    root = (c47.IMG_ROOT if c47.IMG_ROOT.exists() else Path.home() / "mnt" / "Text2Img") / "benchmark_te_conditioning" / "elf"
    base = np.load(root / "P1_elfbrawler_baseline.npz")["cond"].astype(np.float32)
    scale = np.linalg.norm(base, axis=-1).mean(0)            # mean token norm per tap, (12,)
    def vec(f):
        d = np.load(f)["dmean"].astype(np.float32)
        return (d / scale[:, None]).reshape(-1)
    rows = []
    for layer in range(35):
        for half in ("attn", "mlp"):
            for sg, og in (("p", "m"), ("m", "p")):
                fs = {d: root / f"P1_elfbrawler_L{layer:02d}_{half}_{sg}{d}.npz" for d in DOSES}
                if not all(f.exists() for f in fs.values()):
                    continue
                P = {d: vec(f) for d, f in fs.items()}
                fo = root / f"P1_elfbrawler_L{layer:02d}_{half}_{og}0.10.npz"
                used = bool(np.any(P["0.10"] != 0))
                r = {"layer": layer, "half": half, "sign": sg, "used": int(used)}
                r.update(measure(P, vec(fo) if fo.exists() else None) if used else {"bend_c": "", "path_a": "", "chord_b": "", "arc": "", "norm_1": "", "sym": ""})
                rows.append(r)
    out = verdict(rows)
    # reported: 1 - c against C64's intensity of change by eye at dose 1.00
    lev = {"nessuna": 0, "lieve": 1, "media": 2, "forte": 3}
    eye = {r["cond"]: lev.get(r["entita"]) for r in csv.DictReader(open(DATA / "te_pilot_phase1_joined.csv", encoding="utf-8"))}
    xy = [(1 - r["bend_c"], eye[k]) for r in rows if r["used"]
          for k in [f"L{r['layer']:02d}_{r['half']}_{r['sign']}1.00"] if eye.get(k) is not None]
    if len(xy) >= 5:
        from scipy.stats import spearmanr
        rho = float(spearmanr([a for a, _ in xy], [b for _, b in xy]).correlation)
        out.append({"test": "Spearman(1 - c, C64 intensity by eye at 1.00) (reported, lead only)", "value": f"{rho:+.3f} (n {len(xy)})", "verdict": ""})
    with open(DATA / "te_trajectories.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(DATA / "te_trajectories_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    print("trajectories", len(rows), "used", sum(r["used"] for r in rows))
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


def selftest():
    rng = np.random.default_rng(1); u = rng.normal(size=50); v = rng.normal(size=50)
    straight = {d: float(d) * u for d in DOSES}
    curved = {d: np.cos(float(d) * 2) * u + np.sin(float(d) * 2) * v for d in DOSES}
    assert measure(straight)["bend_c"] > 0.99 and measure(straight)["arc"] == 1
    m = measure(curved); assert m["bend_c"] < 0.5 and m["arc"] == 1, m
    rows = [{"layer": i, "half": "mlp", "sign": "p", "used": 1, **measure(straight), "norm_1": float(i)} for i in range(10)]
    assert verdict(rows)[0]["verdict"] == "straight"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    selftest() if ap.parse_args().selftest else run()
