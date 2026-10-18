"""C93 figure: how a text-encoder edit's push bends along the dose, against a random push of the same size injected at
the same place. Reads Text2Img/benchmark_te_shapes/*.npz (mean push over tokens, per dose, scaled per tap).

  python plot_te_shapes.py [out.png]

Top row: degrees turned since the smallest dose, against the length of the push (as a share of its length at the
largest dose). Bottom row: the direction of the push in the plane where it moves most (0 = the smallest dose, pointing right), at a
radius growing with the log of the push length, so the small doses, where the bend happens, are visible; dots at
every dose.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path.home() / "mnt" / "Text2Img" / "benchmark_te_shapes"
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter"]
EDITS = [("L06_mlp", "Layer 6 MLP"), ("L14_mlp", "Layer 14 MLP"), ("L28_mlp", "Layer 28 MLP")]
EDIT, CTRL = "#2a78d6", "#8a8986"              # categorical slot 1; neutral for the control
INK, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def load(ch, edit, kind):
    z = np.load(ROOT / f"{ch}_{edit}_p_{kind}.npz")
    P = z["dmean"].astype(np.float64).reshape(len(z["doses"]), -1)
    return z["doses"], P


def turned(P):
    U = P / np.linalg.norm(P, axis=1, keepdims=True)
    return np.degrees(np.arccos(np.clip(U @ U[0], -1, 1)))


def plane(P):
    """Direction: angle in the plane where it moves most, 0 at the smallest dose, counter-clockwise.
    Radius: log of the push length, from the smallest dose (inner) to the largest (unit circle)."""
    U = P / np.linalg.norm(P, axis=1, keepdims=True)
    _, _, vt = np.linalg.svd(U, full_matrices=False)
    ang = np.unwrap(np.arctan2(U @ vt[1], U @ vt[0]))
    ang = ang - ang[0]
    if np.mean(ang) < 0:
        ang = -ang
    n = np.log(np.linalg.norm(P, axis=1)); r = 0.12 + 0.88 * (n - n[0]) / (n[-1] - n[0])
    return r * np.cos(ang), r * np.sin(ang)


def main(out):
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                         "ytick.color": MUTED, "font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(2, 3, figsize=(13, 8.4), facecolor=SURF)
    for j, (edit, title) in enumerate(EDITS):
        a, b = ax[0, j], ax[1, j]
        for k, (kind, col, lw, z) in enumerate((("control", CTRL, 1.4, 1), ("edit", EDIT, 2.0, 2))):
            for ch in CHARS:
                d, P = load(ch, edit, kind)
                n = np.linalg.norm(P, axis=1); t = turned(P)
                a.plot(n / n[-1], t, color=col, lw=lw, zorder=z, solid_capstyle="round")
                x, y = plane(P)
                b.plot(x, y, color=col, lw=lw, zorder=z, solid_capstyle="round")
                b.scatter(x, y, s=12, color=col, zorder=z + 1, edgecolors=SURF, linewidths=0.6)
                if ch == CHARS[0] and kind == "edit":
                    for dd, xx, yy in zip(d, x, y):
                        if dd in (0.05, 0.3, 1.0, 3.0):
                            b.annotate(f"d {dd:g}", (xx, yy), textcoords="offset points", xytext=(7, -4), color=INK, fontsize=8.5)
        a.set_title(title, color=INK, fontsize=12, loc="left")
        a.set_xlim(0, 1.02); a.set_ylim(0, 100)
        a.set_xlabel("push length (share of its length at d = 3)")
        if j == 0:
            a.set_ylabel("degrees turned since d = 0.05")
        a.grid(True, color=GRID, lw=0.8); a.set_facecolor(SURF)
        th = np.linspace(0, np.pi, 200)
        b.plot(np.cos(th), np.sin(th), color=GRID, lw=0.8, zorder=0)
        b.axhline(0, color=GRID, lw=0.8, zorder=0); b.plot([0], [0], "o", color=MUTED, ms=3)
        b.set_aspect("equal"); b.set_xlim(-0.75, 1.2); b.set_ylim(-0.12, 1.1)
        b.set_xticks([]); b.set_yticks([]); b.set_facecolor(SURF)
        for s in b.spines.values():
            s.set_visible(False)
        if j == 0:
            b.set_ylabel("direction in its own plane\n(radius: log of push length)", color=MUTED)
    ax[0, 0].plot([], [], color=EDIT, lw=2, label="real edit (3 characters)")
    ax[0, 0].plot([], [], color=CTRL, lw=1.4, label="random push, same size, same place")
    ax[0, 0].legend(frameon=False, loc="lower right", labelcolor=INK)
    fig.suptitle("C93 · the push of a text-encoder edit bends once, early, then goes straight; random pushes bend too",
                 x=0.01, ha="left", color=INK, fontsize=13)
    fig.text(0.01, 0.005, "Qwen3-VL-4B, MLP doubled up to d = 3 (18 doses), mean push over tokens, 12 taps scaled to the "
             "unedited size · data: Text2Img/benchmark_te_shapes, data/te_shapes_trajectories.csv", color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(out, dpi=150, facecolor=SURF)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT.parent / "_te_shapes" / "C93_shapes.png"))
