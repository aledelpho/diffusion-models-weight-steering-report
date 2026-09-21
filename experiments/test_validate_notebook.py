#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_validate_notebook.py -- does the validator actually fail?

Rule 4 of docs/errors_log.md: a control that cannot fail noisily is not a control. A
validator that has only ever been run on a clean tree has not been shown to work; it has
been shown to be quiet. So this injects one violation at a time into a copy of the tree and
asserts the matching check fires.

    python experiments/test_validate_notebook.py

Exit code 0 when every injected fault was caught.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = "notebook/05-knob-or-cost.md"
REG = "experiments/figures.yaml"


def run(tree: Path) -> str:
    proc = subprocess.run([sys.executable, "experiments/validate_notebook.py"],
                          cwd=tree, capture_output=True, text=True)
    return proc.stdout + proc.stderr


def patch(tree: Path, rel: str, old: str, new: str) -> None:
    f = tree / rel
    t = f.read_text(encoding="utf-8")
    assert t.count(old) >= 1, f"anchor not found in {rel}: {old[:60]!r}"
    f.write_text(t.replace(old, new, 1), encoding="utf-8")


def patch_re(tree: Path, rel: str, pattern: str, new: str) -> None:
    """Replace the first regex match. Anchors written as literal prose go stale every time
    the page is edited; the faults these tests inject are structural, so match structure."""
    f = tree / rel
    t = f.read_text(encoding="utf-8")
    m = re.search(pattern, t, re.M)
    assert m, f"pattern not found in {rel}: {pattern!r}"
    f.write_text(t[:m.start()] + new + t[m.end():], encoding="utf-8")


def _duplicate_a_column(tree: Path, rel: str) -> None:
    """Copy one numeric column under a second name -- pitfall 69 in miniature."""
    import csv
    f = tree / rel
    rows = list(csv.DictReader(f.open(encoding="utf-8-sig", newline="")))
    assert rows, f"{rel} is empty"
    src = [c for c in rows[0] if c][1]
    for r in rows:
        r[src + "_copy"] = r[src]
    with f.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


# (name, mutation, substring that must appear in the output)
CASES = [
    ("id does not match filename",
     lambda t: patch(t, PAGE, "id: 05-knob-or-cost", "id: 99-wrong-name"),
     "does not match the filename"),

    ("an exploratory result claims to hold",
     lambda t: patch(t, PAGE, "stage: confirmatory", "stage: exploratory"),
     "an exploratory result cannot hold"),

    ("confirmatory with no pre-registration",
     lambda t: patch(t, PAGE,
                     "preregistration: docs/prereg_punto7_simmetria_segno.md",
                     "preregistration: null"),
     "requires a preregistration"),

    ("the pre-registration names a file that is not in the repository",
     lambda t: patch(t, PAGE, "preregistration: docs/prereg_punto7_simmetria_segno.md",
                     "preregistration: docs/prereg_that_was_never_committed.md"),
     "does not exist in the repository"),

    ("a results CSV the page cites has two columns with identical content",
     lambda t: _duplicate_a_column(t, "data/punto7_blocks.csv"),
     "identical on all"),

    ("a claim points at a heading that does not exist",
     lambda t: patch(t, PAGE, 'anchor: "#the-tail-is-rectified"',
                     'anchor: "#a-heading-that-does-not-exist"'),
     "which is not a heading on this page"),

    ("a claim has no evidence",
     lambda t: patch_re(t, PAGE, r'^    evidence: ".*"$', '    evidence: ""'),
     "is missing 'evidence'"),

    ("the opening block loses one of its three lines",
     lambda t: patch(t, PAGE, "**What would kill it.**", "**What might go wrong.**"),
     "is missing '**What would kill it.**'"),

    ("the reproducibility block contradicts the bench's own feature file",
     lambda t: patch(t, PAGE, "  resolution: 1024x1280", "  resolution: 1024x1760"),
     "the bench's own files record"),

    ("the reproducibility block names a manifest that is not in the repository",
     lambda t: patch(t, PAGE, "  manifest: no per-render manifest exists",
                     "  manifest: data/a_manifest_that_was_never_committed.csv\n  unused: no"),
     "is not in the repository"),

    ("corpus.renders disagrees with the benches the page itemises",
     lambda t: patch(t, PAGE, "  renders: 368", "  renders: 999"),
     "itemises"),

    ("the status line and the front matter disagree on the render count",
     lambda t: patch(t, PAGE, "> **Holds** \u00b7 368 renders",
                     "> **Holds** \u00b7 999 renders"),
     "the status line says 999 renders"),

    ("a page rests on HUD-contaminated renders without saying so",
     lambda t: patch(t, "notebook/08-block1-vs-block6.md",
                     "data/hud_contaminated_images.csv", "data/some_other_file.csv"),
     "does not carry the contamination banner"),

    ("a required section is gone",
     lambda t: patch(t, PAGE, "## Why I might be wrong", "## Some other heading"),
     "missing required section '## Why I might be wrong'"),

    ("the sections are out of order",
     lambda t: patch(t, PAGE, "## The verdict", "## Provenance") or
               patch(t, PAGE, "## Provenance\n\n* Pre-registration:", "## The verdict\n\n* x:"),
     "out of order"),

    ("a condition has no measured displacement",
     lambda t: patch_re(t, PAGE, r"^    measured_D: .*\n", ""),
     "never the nominal one"),

    ("the reproducibility block loses a key",
     lambda t: patch(t, PAGE, "sampling:\n  sampler: euler_ancestral", "sampling_:\n  sampler: x"),
     "missing 'sampling'"),

    ("the page slips into Italian",
     lambda t: patch(t, PAGE, "The answer came out in two halves.",
                     "Il risultato non e' quello che pensavo, perche' i blocchi "
                     "sono diversi."),
     "written in English"),

    ("a crop is a hard-coded pixel rectangle",
     lambda t: patch(t, REG, "    crop: whole\n    control: baseline_pair_seed42_seed777",
                     "    crop: 512,384,256,256\n    control: baseline_pair_seed42_seed777"),
     "looks like a pixel rectangle"),

    ("a toggle has no control pair",
     lambda t: patch_re(t, REG, r"^    control: [a-z0-9_]+\n", ""),
     "a toggle needs a control pair"),

    ("a schema carries a measurement source",
     lambda t: patch(t, REG,
                     "  - id: F05.5\n    page: 05-knob-or-cost\n    kind: schema\n"
                     "    builder: null\n    source: null",
                     "  - id: F05.5\n    page: 05-knob-or-cost\n    kind: schema\n"
                     "    builder: null\n    source: data/punto7_amplitudes.csv"),
     "a schema must not have a measurement source"),

    ("an evidence figure writes its own caption",
     lambda t: patch_re(t, REG, r"^    caption_from: source$", "    caption_from: static"),
     "caption_from must be 'source'"),

    ("a figure on the page is not registered",
     lambda t: patch(t, PAGE, "F05.3_rectification.webp", "F09.9_unregistered.webp"),
     "is not registered in experiments/figures.yaml"),

    ("an image has empty alt text",
     lambda t: patch(t, PAGE,
                     "![Twenty-eight blocks placed by how much they steer against how much "
                     "they cost. The first block and the last few sit at opposite ends of the "
                     "steering axis; the whole tail sits low on the cost axis.](",
                     "![]("),
     "empty alt text"),

    ("a figure is built in a light theme",
     lambda t: _write_light_figure(t),
     "not the dark surface"),
]


def _write_light_figure(tree: Path) -> None:
    from PIL import Image
    d = tree / "assets" / "05-knob-or-cost"
    d.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 48), (255, 255, 255)).save(d / "F05.3_rectification.png")


def main() -> int:
    src = ROOT
    results = []

    # The clean tree must pass, or nothing below means anything.
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp) / "repo"
        shutil.copytree(src, tree, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        out = run(tree)
        clean_ok = "PASS" in out and re.search(r"0 error", out) is not None
        results.append(("the clean tree passes", clean_ok, "" if clean_ok else out[-400:]))

    for name, mutate, expected in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / "repo"
            shutil.copytree(src, tree, ignore=shutil.ignore_patterns("__pycache__", ".git"))
            try:
                mutate(tree)
            except AssertionError as exc:
                results.append((name, False, f"could not inject the fault: {exc}"))
                continue
            out = run(tree)
            caught = expected in out
            results.append((name, caught,
                            "" if caught else f"expected {expected!r}, got:\n{out[-500:]}"))

    width = max(len(n) for n, _, _ in results)
    print()
    for name, ok, detail in results:
        print(f"  {'caught ' if ok else 'MISSED '} {name.ljust(width)}")
        if detail:
            print(f"      {detail}")
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n  {passed}/{len(results)} checks fire when they should\n")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
