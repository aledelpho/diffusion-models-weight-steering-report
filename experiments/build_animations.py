# -*- coding: utf-8 -*-
"""
experiments/build_animations.py  --  the animated figures, rebuilt from the renders

A still frame shows that two images differ. It does not show a reader what to look at, and it
cannot show the same edit landing the same way on five different seeds. The animations do:
the eye holds the layout fixed and the change is the only thing that moves. The old monolithic
README leaned on them and the migrated notebook lost them, because they lived in assets/hero/
and assets/motion/ with no registry entry and no script behind them.

This is the script. Each builder reads a manifest under data/, finds the renders on disk,
composes the frames on the notebook's own dark surface, and writes an animated GIF into
assets/<page>/. Every label it draws is read out of a measurement file -- the seed from the
manifest, the verdict from the blind scoring -- so a caption cannot contradict the data
(pitfall 40).

The frames are whole renders. No crop: a crop is an assertion about where to look, and this
project has already published five crops out of twenty that did not contain what their
captions said.

Builders:

    headlights_switch   F02.7, page 02. The rally car: one prompt, the same five seeds, and
                        every one of the bench's seven arms. --prompt builds it on another
                        style, which is how you find out whether the one you picked is
                        representative.

Usage:
    python experiments/build_animations.py --list
    python experiments/build_animations.py --only headlights_switch \
        --renders "C:/StabilityMatrix-win-x64/Data/Images/Text2Img"
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

RENDER_ROOTS = [
    Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"),
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"),
]

# The palette of experiments/notebook_charts.py, as AUTHORING section 4.4 declares it.
SURFACE = (0x1A, 0x1A, 0x19)
BAND = (0x22, 0x22, 0x20)
GRID = (0x2E, 0x2E, 0x2C)
INK = (0xE3, 0xE7, 0xEE)
DIM = (0x98, 0xA2, 0xB2)
POS = (0x19, 0x9E, 0x70)
NEG = (0xD9, 0x59, 0x26)
ACC = (0x39, 0x87, 0xE5)

CELL_W = 196
GAP = 4
PAD = 8
HEAD_H = 46
LABEL_H = 24
STRIP_H = 18
FRAME_MS = 1900


def font(size: int, bold: bool = False):
    try:
        from matplotlib import font_manager
        name = "DejaVu Sans" + (":bold" if bold else "")
        return ImageFont.truetype(font_manager.findfont(name.split(":")[0]), size)
    except Exception:
        return ImageFont.load_default()


def bench(name: str, extra: list[Path]) -> Path:
    for r in extra + RENDER_ROOTS:
        p = r / name / "renders"
        if p.is_dir():
            return p
        p = r / name
        if p.is_dir():
            return p
    sys.exit(f"{name} is under none of {[str(x) for x in extra + RENDER_ROOTS]}")


def read(name: str) -> list[dict]:
    path = DATA / name
    if not path.exists():
        sys.exit(f"data/{name} is missing; the animation cannot be built without its manifest")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def compose(cells: list[tuple[Path, str, tuple[int, int, int]]],
            title: str, subtitle: str) -> Image.Image:
    """One frame: a header, a row of whole renders, a label under each."""
    thumbs = []
    for path, _, _ in cells:
        im = Image.open(path).convert("RGB")
        h = round(im.height * CELL_W / im.width)
        thumbs.append(im.resize((CELL_W, h), Image.LANCZOS))
    cell_h = max(t.height for t in thumbs)
    w = PAD * 2 + len(thumbs) * CELL_W + (len(thumbs) - 1) * GAP
    h = HEAD_H + cell_h + LABEL_H + STRIP_H

    frame = Image.new("RGB", (w, h), SURFACE)
    d = ImageDraw.Draw(frame)
    d.rectangle([0, 0, w, HEAD_H - 1], fill=BAND)
    d.text((PAD, 7), title, font=font(12, True), fill=INK)
    d.text((PAD, 25), subtitle, font=font(11), fill=DIM)

    x = PAD
    for (path, label, colour), t in zip(cells, thumbs):
        frame.paste(t, (x, HEAD_H))
        d.rectangle([x, HEAD_H + cell_h, x + CELL_W - 1, HEAD_H + cell_h + LABEL_H - 1],
                    fill=BAND)
        seed_txt, _, verdict = label.partition("|")
        f10 = font(10)
        d.text((x + 5, HEAD_H + cell_h + 7), seed_txt, font=f10, fill=DIM)
        if verdict:
            fb = font(10, True)
            tw = d.textlength(verdict, font=fb)
            bx = x + CELL_W - 7 - tw - 10
            by = HEAD_H + cell_h + 4
            d.rectangle([bx, by, bx + tw + 10, by + LABEL_H - 9], fill=colour)
            d.text((bx + 5, by + 3), verdict, font=fb,
                   fill=SURFACE if colour != DIM else (0x1A, 0x1A, 0x19))
        x += CELL_W + GAP
    d.line([0, HEAD_H + cell_h + LABEL_H, w, HEAD_H + cell_h + LABEL_H], fill=GRID)
    return frame


def save_gif(frames: list[Image.Image], out: Path, strip: str, ms: int = FRAME_MS) -> Path:
    f9 = font(9)
    for f in frames:
        d = ImageDraw.Draw(f)
        text = strip
        # A provenance strip that runs off the edge is a provenance strip nobody can check.
        while text and d.textlength(text, font=f9) > f.width - 12:
            text = text.rsplit(" ", 1)[0]
        if text != strip:
            sys.exit(f"the provenance strip does not fit {f.width}px and would be cut: {strip!r}")
        d.text((6, f.height - STRIP_H + 3), text, font=f9, fill=DIM)
    out.parent.mkdir(parents=True, exist_ok=True)
    quant = [f.quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
             for f in frames]
    quant[0].save(out, save_all=True, append_images=quant[1:], duration=ms, loop=0,
                  optimize=True, disposal=2)
    print(f"wrote {out}  ({len(frames)} frames, {out.stat().st_size / 1e6:.2f} MB, "
          f"{frames[0].width}x{frames[0].height})")
    return out


# ---------------------------------------------------------------- F02.7

HEADLIGHT_CODE = {"0": ("UNLIT", DIM), "1": ("AMBIGUOUS", NEG), "2": ("LIT", POS)}
# 0 / 1 / 2 are the blind scorer's keystrokes. The legend is not written down anywhere, so it
# is recovered here and checked: on blockshuf_neg_2x the results file records 0 lit and 1
# ambiguous, and exactly one cell of that arm carries code 1 and none carries code 2. The
# assertion below fails if a rescoring ever breaks that correspondence.

CONDITIONS = [
    ("baseline", "no edit"),
    ("preset_pos_1x", "calibrated preset, single amplitude"),
    ("preset_pos_2x", "calibrated preset, double amplitude"),
    ("blockshuf_neg_1x", "block derangement, negative, single"),
    ("blockshuf_neg_2x", "block derangement, negative, double"),
    ("rand_pos_1x", "sign scramble, single, the norm-matched control"),
    ("rand_pos_2x", "sign scramble, double, the norm-matched control"),
]
SEEDS = ["42", "777", "1337", "9999", "4242145"]


def _verdicts() -> dict[tuple[str, str, str], str]:
    key = {r["hash_id"]: r for r in read("stage9_headlights_key.csv")}
    out: dict[tuple[str, str, str], str] = {}
    for r in read("stage9_headlights_raw.csv"):
        m = key.get(r["hash_id"])
        if m:
            out[(m["prompt_id"], m["cond_name"], m["seed"])] = r["code"]
    lit = sum(1 for (_, c, _), v in out.items() if c == "blockshuf_neg_2x" and v == "2")
    if lit:
        sys.exit("the code legend no longer holds: blockshuf_neg_2x has a cell scored 2, "
                 "while data/stage9_headlights_results.csv records 0 lit for that arm")
    return out


def headlights_switch(out: Path, extra_roots: list[Path], prompt: str = "S2_watercolor") -> Path:
    """One prompt, one set of five seeds, every arm of the bench.

    The layout never moves: same scene, same five seeds, seven frames. Only the edit changes.
    That is the whole argument -- if the lamps come on in one arm and in no other, a reader
    can see it without being told, and can also see the arms where nothing happens, which is
    most of them.

    The prompt is a parameter and the figure names it, because the eight styles do not behave
    alike: data/stage9_headlights_by_style.csv is the census, and three styles never light a
    lamp in any condition. A single style is an illustration of the effect, never its measure.
    """
    renders = bench("benchmark_stage9", extra_roots)
    verdict = _verdicts()
    rates = {r["condition"]: r for r in read("stage9_headlights_results.csv")}
    # The preset darkens the whole frame. A reader deciding whether a lamp is lit or merely
    # brighter than a darker scene needs that number on the figure, not in a footnote.
    lum = {r["condition"]: r["paired_mean"] for r in read("stage9_preset_shift.csv")
           if r["feature"] == "L_star"}

    frames, tally = [], []
    for cond, cond_label in CONDITIONS:
        cells = []
        for seed in SEEDS:
            path = renders / f"{prompt}_{cond}_seed{seed}_00001_.png"
            if not path.exists():
                sys.exit(f"{path} is not on disk")
            code = verdict.get((prompt, cond, seed))
            if code is None:
                sys.exit(f"no blind score for {prompt} {cond} seed {seed}")
            word, colour = HEADLIGHT_CODE[code]
            cells.append((path, f"seed {seed}|{word}", colour))
        here = sum(1 for s in SEEDS if verdict.get((prompt, cond, s)) == "2")
        tally.append((cond, here))
        whole = rates.get(cond, {})
        across = (f"{whole['lit']} of {whole['n_valid']} across all eight styles"
                  if whole else "")
        dl = lum.get(cond)
        shift = ""
        if dl and dl != "not computable":
            shift = f"  \u2014  mean L* {float(dl):+.2f}, the frame moves too"
        frames.append(compose(
            cells,
            f"THE HEADLIGHTS NOBODY ASKED FOR  \u00b7  {prompt}  \u00b7  "
            f"one prompt, five seeds, every arm",
            f"{cond_label}  \u2014  {here} of {len(SEEDS)} lit here"
            + (f", {across}" if across else "") + shift))

    majority = [c for c, n in tally if n > len(SEEDS) / 2]
    verdict_line = (f"{len(majority)} arm of {len(tally)} lights a majority: {majority[0]}"
                    if len(majority) == 1 else
                    f"{len(majority)} arms of {len(tally)} light a majority: "
                    f"{', '.join(majority) or 'none'}")
    return save_gif(frames, out,
                    f"{prompt}  \u00b7  {verdict_line}  \u00b7  blind scores in "
                    f"data/stage9_headlights_key.csv + _raw.csv  \u00b7  whole frames, no crop",
                    ms=1600)


def headlights_switch_lowpoly(out: Path, extra_roots: list[Path], prompt: str = "S3_lowpoly") -> Path:
    """F02.8: the same seven frames on the style that does NOT behave like the headline case.

    It is committed beside F02.7, not instead of it. Two arms of seven reach a majority here
    rather than one, and the untouched model already lights a seed. A reader who sees only the
    clean style has been shown an illustration; the pair is the argument that the census in
    data/stage9_headlights_by_style.csv is the measure.
    """
    return headlights_switch(out, extra_roots, prompt)


BUILDERS = {
    "headlights_switch": (headlights_switch,
                          ASSETS / "02-attribute-emergence" / "F02.7_headlights_switch.gif",
                          "F02.7 - the car, one prompt, five seeds, all seven arms"),
    "headlights_switch_lowpoly": (headlights_switch_lowpoly,
                                  ASSETS / "02-attribute-emergence"
                                  / "F02.8_headlights_switch_lowpoly.gif",
                                  "F02.8 - the same, on the style that behaves differently"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--renders", action="append", default=[],
                    help="a folder holding the benchmark_* directories; tried first")
    ap.add_argument("--out-dir", default=None, help="write here instead of assets/<page>/")
    ap.add_argument("--prompt", default=None,
                    help="override the style the figure is built on, to inspect another one")
    a = ap.parse_args()

    if a.list:
        for name, (_, dest, what) in BUILDERS.items():
            print(f"  {name:20s} {what}\n  {'':20s} -> {dest.relative_to(ROOT)}")
        return

    extra = [Path(r) for r in a.renders]
    todo = [n for n in BUILDERS if not a.only or n in a.only]
    if not todo:
        sys.exit(f"no builder matches {a.only}; --list shows them")
    for name in todo:
        fn, dest, _ = BUILDERS[name]
        if a.out_dir:
            dest = Path(a.out_dir) / dest.name
        print(f"[{name}]")
        if a.prompt:
            fn(dest, extra, a.prompt)
        else:
            fn(dest, extra)


if __name__ == "__main__":
    main()
