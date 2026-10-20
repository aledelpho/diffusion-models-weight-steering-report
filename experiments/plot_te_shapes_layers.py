"""C101 figures: the push's shape at every layer of the text encoder (dwarf, MLP and attention, both signs).
Reads Text2Img/benchmark_te_shapes_layers/*.npz (mean push over tokens, per dose, scaled per tap).

  python plot_te_shapes_layers.py [root] [outdir]

C101_overview.png  total turn against layer (edits, random controls, attention), and the turning curve of every MLP
                   layer coloured by depth.
C101_grid_<half>_<sign>.png  one small panel per layer: the direction of the push in its own plane, radius = log of the
                   push length (as the C93 figure); MLP positive panels carry the random control in grey.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

PROMPT = "D1_dwarf_paladin"
LAYERS = list(range(35))
# the report's dark figure style (notebook_charts.py): categorical slots 1-2, a neutral for the controls
MLP, ATTN, CTRL = "#3987e5", "#d95926", "#8b8a84"
INK, MUTED, GRID, SURF = "#e3e7ee", "#98a2b2", "#2e2e2c", "#1a1a19"
# sequential blue ramp, shallow (dark step 600) to deep (light step 100)
DEPTH = LinearSegmentedColormap.from_list("depth", ["#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4", "#cde2fb"])
TITLES = {("mlp", "p"): "MLP, positive doses (0.05 to 10)", ("mlp", "m"): "MLP, negative doses (-0.05 to -3)",
          ("attn", "p"): "attention, positive doses (0.05 to 10)", ("attn", "m"): "attention, negative doses (-0.05 to -3)"}


def load(root, L, half, sign, kind):
    f = Path(root) / f"{PROMPT}_L{L:02d}_{half}_{sign}_{kind}.npz"
    if not f.exists():
        return None, None
    z = np.load(f)
    P = z["dmean"].astype(np.float64).reshape(len(z["doses"]), -1)
    k = 0
    while k < len(P) and np.isfinite(P[k]).all():                         # amendment 1: stop where fp16 overflowed
        k += 1
    return z["doses"][:k], P[:k]


def turned(P):
    U = P / np.linalg.norm(P, axis=1, keepdims=True)
    return np.degrees(np.arccos(np.clip(U @ U[0], -1, 1)))


def plane(P):
    U = P / np.linalg.norm(P, axis=1, keepdims=True)
    _, _, vt = np.linalg.svd(U, full_matrices=False)
    ang = np.unwrap(np.arctan2(U @ vt[1], U @ vt[0])); ang = ang - ang[0]
    if np.mean(ang) < 0:
        ang = -ang
    n = np.log(np.linalg.norm(P, axis=1)); r = 0.12 + 0.88 * (n - n[0]) / (n[-1] - n[0])
    return r * np.cos(ang), r * np.sin(ang)


def style():
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                         "ytick.color": MUTED, "font.family": "DejaVu Sans", "axes.facecolor": SURF})


def overview(root, out):
    fig = plt.figure(figsize=(14, 8.6), facecolor=SURF)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1], hspace=0.38, wspace=0.18)
    for row, sign in enumerate(("p", "m")):
        a = fig.add_subplot(gs[row, 0])
        series = [("mlp", "edit", MLP, "MLP edit"), ("attn", "edit", ATTN, "attention edit")]
        if sign == "p":
            series.insert(1, ("mlp", "control", CTRL, "random push at the MLP, same size"))
        for half, kind, col, lab in series:
            xs, ys = [], []
            for L in LAYERS:
                _, P = load(root, L, half, sign, kind)
                if P is not None:
                    xs.append(L); ys.append(turned(P)[-1])
            if xs:
                a.plot(xs, ys, color=col, lw=2, zorder=3 if kind == "edit" else 2, solid_capstyle="round", label=lab)
                a.scatter(xs, ys, s=22, color=col, edgecolors=SURF, linewidths=1.2, zorder=4)
        a.set_xlim(-0.8, 34.8); a.set_ylim(0, 180); a.set_yticks([0, 45, 90, 135, 180])
        a.set_xticks([0, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 34])
        a.grid(True, axis="y", color=GRID, lw=0.8)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.set_ylabel("total turn, smallest to largest dose (deg)")
        a.set_title("positive doses (0.05 to 10)" if sign == "p" else "negative doses (-0.05 to -3)", color=INK, loc="left", fontsize=12)
        if row == 1:
            a.set_xlabel("edited layer of the text encoder")
        a.legend(frameon=False, loc="upper right", labelcolor=INK, fontsize=9)
    b = fig.add_subplot(gs[:, 1])
    norm = Normalize(0, 34)
    for L in LAYERS:
        _, P = load(root, L, "mlp", "p", "edit")
        if P is None:
            continue
        n = np.linalg.norm(P, axis=1)
        b.plot(n / n[-1], turned(P), color=DEPTH(norm(L)), lw=1.6, solid_capstyle="round")
    b.set_xscale("log"); b.set_ylim(0, 180); b.set_yticks([0, 45, 90, 135, 180])
    b.grid(True, color=GRID, lw=0.8)
    for s in ("top", "right"):
        b.spines[s].set_visible(False)
    b.set_xlabel("push length (share of its length at d = 10, log)")
    b.set_ylabel("degrees turned since d = 0.05")
    b.set_title("MLP, positive: how each layer's push turns", color=INK, loc="left", fontsize=12)
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=DEPTH), ax=b, fraction=0.04, pad=0.02)
    cb.set_label("edited layer", color=MUTED); cb.ax.tick_params(colors=MUTED); cb.outline.set_visible(False)
    fig.suptitle("C101 · the push of a text-encoder edit, at every layer", x=0.01, ha="left", color=INK, fontsize=14)
    fig.text(0.01, 0.01, "Qwen3-VL-4B, dwarf prompt, one layer edited at a time (layer 35 reaches no tap), mean push over "
             "tokens, 12 taps scaled to the unedited size · data: Text2Img/benchmark_te_shapes_layers, "
             "data/te_shapes_layers_trajectories.csv", color=MUTED, fontsize=8.5)
    fig.savefig(out, dpi=150, facecolor=SURF, bbox_inches="tight")
    print("wrote", out)


def grid(root, half, sign, out):
    col = MLP if half == "mlp" else ATTN
    fig, ax = plt.subplots(5, 7, figsize=(15, 9.6), facecolor=SURF)
    th = np.linspace(0, np.pi, 100)
    for i, L in enumerate(LAYERS):
        b = ax.ravel()[i]
        b.plot(np.cos(th), np.sin(th), color=GRID, lw=0.8, zorder=0)
        b.plot(-np.cos(th), -np.sin(th), color=GRID, lw=0.8, zorder=0)
        b.axhline(0, color=GRID, lw=0.8, zorder=0)
        head, ylo = {"edit": "", "control": ""}, -0.15
        for kind, c, lw, z in (("control", CTRL, 1.2, 1), ("edit", col, 1.8, 2)):
            _, P = load(root, L, half, sign, kind)
            if P is None:
                continue
            x, y = plane(P)
            b.plot(x, y, color=c, lw=lw, zorder=z, solid_capstyle="round")
            b.scatter(x[[0, -1]], y[[0, -1]], s=14, color=c, zorder=z + 1, edgecolors=SURF, linewidths=0.8)
            head[kind] = f"  {turned(P)[-1]:.0f}°" if kind == "edit" else f"  ({turned(P)[-1]:.0f}°)"
            ylo = min(ylo, float(y.min()) - 0.08)
        b.set_title(f"L{L:02d}" + head["edit"] + head["control"], color=INK, fontsize=9.5, loc="left", pad=2)
        b.set_aspect("equal"); b.set_xlim(-1.08, 1.08); b.set_ylim(max(ylo, -1.08), 1.08)
        b.set_xticks([]); b.set_yticks([])
        for s in b.spines.values():
            s.set_visible(False)
    leg = f"{'MLP' if half == 'mlp' else 'attention'} edit" + ("; grey and (deg) in brackets: random push at the MLP, same size" if (half, sign) == ("mlp", "p") else "")
    fig.suptitle(f"C101 · {TITLES[(half, sign)]}: the direction of the push in its own plane, layer by layer",
                 x=0.01, ha="left", color=INK, fontsize=14)
    fig.text(0.01, 0.955, f"{leg}. Angle 0 = smallest dose, pointing right; radius = log of the push length, unit circle "
             "at the largest dose; the number is the total turn.", color=MUTED, fontsize=9.5)
    fig.text(0.01, 0.005, "Qwen3-VL-4B, dwarf prompt, mean push over tokens · data: Text2Img/benchmark_te_shapes_layers",
             color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.015, 1, 0.945))
    fig.savefig(out, dpi=150, facecolor=SURF)
    print("wrote", out)


def fake(root):
    """Synthetic trajectories for testing the figures (not data)."""
    rng = np.random.default_rng(1); root = Path(root); root.mkdir(parents=True, exist_ok=True)
    pos = np.array([0.05, .1, .15, .2, .3, .4, .5, .6, .7, .8, .9, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5, 7, 10])
    neg = np.array([d for d in pos if d <= 1] + [1.5, 2, 3])
    for L in LAYERS:
        for half in ("mlp", "attn"):
            for sign, ds in (("p", pos), ("m", neg)):
                for kind in (("edit", "control") if (half, sign) == ("mlp", "p") else ("edit",)):
                    e1, e2 = rng.standard_normal((2, 12 * 64))
                    bend = np.radians((80 - L) if kind == "edit" else 85 - L / 2)
                    a = bend * (1 - np.exp(-ds / 0.3))
                    P = (np.cos(a)[:, None] * e1 + np.sin(a)[:, None] * e2) * ds[:, None]
                    np.savez_compressed(root / f"{PROMPT}_L{L:02d}_{half}_{sign}_{kind}.npz",
                                        dmean=P.reshape(len(ds), 12, 64).astype(np.float16), doses=ds)


if __name__ == "__main__":
    style()
    if len(sys.argv) > 1 and sys.argv[1] == "--fake":
        fake(sys.argv[2]); sys.exit()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
    else:
        import blk23_colorful as c47
        root = c47.IMG_ROOT / "benchmark_te_shapes_layers"
        if not root.exists():
            root = Path.home() / "mnt" / "D:--StabilityMatrix-win-x64--Data--Images--Text2Img" / "benchmark_te_shapes_layers"
    outdir = Path(sys.argv[2]) if len(sys.argv) > 2 else root.parent / "_te_shapes"
    outdir.mkdir(parents=True, exist_ok=True)
    overview(root, outdir / "C101_overview.png")
    for half in ("mlp", "attn"):
        for sign in ("p", "m"):
            grid(root, half, sign, outdir / f"C101_grid_{half}_{sign}.png")
