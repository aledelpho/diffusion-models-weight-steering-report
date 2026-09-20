# -*- coding: utf-8 -*-
"""
experiments/notebook_figures.py

The figure module the authoring contract names (notebook/AUTHORING.md section 4.2).

Until 2026-09-21 this file did not exist, while every entry in experiments/figures.yaml
named a builder function inside it. The eight figures already on disk were therefore built
by other means and could not be regenerated. This module starts closing that gap: one
builder, written to the rules the contract states, with the rest still to come.

The rules a builder here obeys:

  * it reads its numbers out of a measurement file under data/, never out of its own source;
  * it derives every caption from the row it is drawing, so a label cannot contradict the
    measurement (pitfall 40);
  * it raises rather than draws a panel whose measured role it cannot look up;
  * it shows whole frames -- a crop is an assertion about where to look, and this project has
    already published five crops out of twenty that did not contain what their captions said;
  * it draws on the dark surface #1a1a19 that validate_notebook.py checks for.

Run directly to rebuild what it can:

    python experiments/notebook_figures.py
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

# The surface validate_notebook.py samples for, and the palette of notebook_charts.py as
# AUTHORING section 4.4 declares it.
SURFACE = (0x1A, 0x1A, 0x19)
BORDER = (0x2E, 0x2E, 0x2C)
INK = (0xE3, 0xE7, 0xEE)
DIM = (0x98, 0xA2, 0xB2)
POS = (0x19, 0x9E, 0x70)
NEG = (0xD9, 0x59, 0x26)
ACC = (0x39, 0x87, 0xE5)

PANEL_W, PANEL_H = 150, 188
GAP = 2
CAPTION_H = 20
LABEL_W = 156
NCOLS = 10


def _wrap(text: str, width: int) -> list[str]:
    out, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if len(candidate) > width and line:
            out.append(line)
            line = word
        else:
            line = candidate
    if line:
        out.append(line)
    return out


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for p in (
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
    ):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------- measurements


def load_attribute_emergence() -> dict:
    """data/attribute_emergence.csv keyed by (set_id, seed).

    The only source of every number this module prints about the barnacle corpus.
    """
    src = DATA / "attribute_emergence.csv"
    if not src.exists():
        raise FileNotFoundError(f"measurement file missing: {src}")
    out = {}
    with src.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            out[(row["set_id"], str(row["seed"]))] = row
    if not out:
        raise ValueError(f"{src} is empty")
    return out


SCORE_LABEL = {"1": ("present", POS), "0": ("absent", DIM), "ambiguous": ("ambiguous", ACC)}


def _score(rows: dict, set_id: str, seed: str) -> tuple[str, tuple[int, int, int]]:
    row = rows.get((set_id, seed))
    if row is None:
        raise KeyError(
            f"no scored row for set {set_id} seed {seed} in data/attribute_emergence.csv -- "
            "a panel whose measured role cannot be looked up is not drawn"
        )
    val = row["barnacles"]
    if val not in SCORE_LABEL:
        raise ValueError(f"unexpected score {val!r} for {set_id}/{seed}")
    return SCORE_LABEL[val]


def _render_path(rows: dict, set_id: str, seed: str) -> Path:
    row = rows[(set_id, seed)]
    folder = ASSETS / "02_attribute_emergence" / row["folder"]
    stem = Path(row["image_file"]).stem
    for ext in (".webp", ".png", ".jpg"):
        p = folder / f"{stem}{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(f"render missing for {set_id}/{seed}: {folder}/{stem}.*")


def _rate(rows: dict, set_id: str) -> tuple[int, int, int]:
    present = absent = amb = 0
    for (sid, _), row in rows.items():
        if sid != set_id:
            continue
        v = row["barnacles"]
        present += v == "1"
        absent += v == "0"
        amb += v == "ambiguous"
    return present, absent, amb


# ---------------------------------------------------------------- builders


def barnacle_census(set_a: str, set_b: str, out_path: Path, title: str) -> Path:
    """Paired whole-frame census of two arms of the attribute-emergence corpus.

    Every panel is captioned with the blind score recorded for that exact (set, seed) in
    data/attribute_emergence.csv. No crop, no hand-written label, no panel without a score.
    """
    rows = load_attribute_emergence()
    seeds = sorted(
        {s for (sid, s) in rows if sid == set_a} & {s for (sid, s) in rows if sid == set_b},
        key=int,
    )
    if not seeds:
        raise ValueError(f"{set_a} and {set_b} share no seed")

    label_a = rows[(set_a, seeds[0])]["condition"]
    label_b = rows[(set_b, seeds[0])]["condition"]
    pa, na, aa = _rate(rows, set_a)
    pb, nb, ab = _rate(rows, set_b)

    bands = [seeds[i:i + NCOLS] for i in range(0, len(seeds), NCOLS)]
    row_h = PANEL_H + CAPTION_H + GAP
    band_h = 2 * row_h + 16
    width = LABEL_W + NCOLS * (PANEL_W + GAP)
    height = 64 + len(bands) * band_h + 40

    fig = Image.new("RGB", (width, height), SURFACE)
    d = ImageDraw.Draw(fig)
    f_title, f_lab, f_cap, f_small = font(21, True), font(14, True), font(13), font(12)

    d.text((14, 16), title, font=f_title, fill=INK)
    d.text((14, 42), f"whole frames, nothing cropped; every caption is the score recorded "
                     f"for that image in data/attribute_emergence.csv",
           font=f_small, fill=DIM)

    y = 64
    for band in bands:
        for r, (sid, lab, tally) in enumerate(
            ((set_a, label_a, (pa, na, aa)), (set_b, label_b, (pb, nb, ab)))
        ):
            ytop = y + r * row_h
            d.text((14, ytop + 6), sid, font=f_lab, fill=INK)
            for i, part in enumerate(_wrap(lab, 22)[:2]):
                d.text((14, ytop + 26 + 15 * i), part, font=f_small, fill=DIM)
            d.text((14, ytop + 58), f"{tally[0]} / {tally[0] + tally[1]} present"
                                    + (f" ({tally[2]} ambiguous)" if tally[2] else ""),
                   font=f_small, fill=POS if tally[0] > tally[1] else DIM)
            for c, seed in enumerate(band):
                x = LABEL_W + c * (PANEL_W + GAP)
                im = Image.open(_render_path(rows, sid, seed)).convert("RGB")
                im = im.resize((PANEL_W, PANEL_H), Image.LANCZOS)
                fig.paste(im, (x, ytop))
                d.rectangle([x, ytop, x + PANEL_W - 1, ytop + PANEL_H - 1], outline=BORDER)
                text, colour = _score(rows, sid, seed)
                d.text((x + 3, ytop + PANEL_H + 3), f"{seed} · {text}", font=f_cap, fill=colour)
        y += band_h

    strip = (f"prompt {rows[(set_a, seeds[0])]['prompt_key']} · {set_a} vs {set_b} · "
             f"{len(seeds)} seeds · n = {pa + na + aa + pb + nb + ab} · "
             f"source data/attribute_emergence.csv")
    d.text((14, height - 28), strip, font=f_small, fill=DIM)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.save(out_path, "WEBP", quality=82, method=6)
    return out_path


def main() -> int:
    out = ASSETS / "02-attribute-emergence"
    built = [
        barnacle_census("A1", "A5", out / "F02.4_barnacle_census_A1_A5.webp",
                        "The attribute the prompt asks for: block permutation against the stock model"),
        barnacle_census("A1", "A7", out / "F02.5_barnacle_census_A1_A7.webp",
                        "The same displacement, scrambled instead of permuted"),
    ]
    for p in built:
        print(f"built {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
