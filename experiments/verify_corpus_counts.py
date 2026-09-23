# -*- coding: utf-8 -*-
"""
experiments/verify_corpus_counts.py
===================================
The corpus of a page, counted from its manifests instead of asserted in its front matter.

Page 01 published `corpus.renders: 940` for two days while every contrast on it came out of
`experiments/global_aggregation_corrected.py`, which loads five manifests totalling 1272. The
old README's 1272 was right and the page was wrong, and nothing in the repository could say so
because no file held the arithmetic. This script holds it.

For each corpus it knows about, it reports:

  rows            the sum of the manifests' row counts, which is what a naive count gives
  distinct_files  the same rows keyed by basename -- if this is lower, the sum double-counts
  prompts         distinct prompt_id across the manifests
  resolutions     every (width x height) recorded, so a contaminated bench cannot hide
  declared        the page's own corpus.renders
  verdict         MATCH or the difference

The manifest lists are not retyped here. For 01-mark-style they are imported from
`global_aggregation_corrected.py` itself, so if that script's inputs ever change, this count
changes with them instead of drifting away from them.

Nothing is rendered. Reads data/ and notebook/, writes data/corpus_reconstruction.csv.

Usage:
    python experiments/verify_corpus_counts.py
    python experiments/verify_corpus_counts.py --out data/corpus_reconstruction.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
NOTEBOOK = ROOT / "notebook"
sys.path.insert(0, str(HERE))


def manifests_of_page_01() -> list[str]:
    """The five files global_aggregation_corrected.py loads, read off that script."""
    src = (HERE / "global_aggregation_corrected.py").read_text(encoding="utf-8")
    names: list[str] = []
    for block in re.findall(r"MANIFEST_(?:COND|BASE)\s*=\s*\(([^)]*)\)", src, re.S):
        names += re.findall(r"[\"']([\w.]+\.csv)[\"']", block)
    if not names:
        sys.exit("could not read MANIFEST_COND / MANIFEST_BASE out of "
                 "global_aggregation_corrected.py -- the reconstruction would be a guess")
    seen, out = set(), []
    for n in names:                      # union, in first-seen order
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


CORPORA = {
    "01-mark-style": manifests_of_page_01,
}


def declared_renders(page: str) -> int | None:
    path = NOTEBOOK / f"{page}.md"
    if not path.exists():
        return None
    m = re.search(r"^\s*renders:\s*(\d+)\s*$", path.read_text(encoding="utf-8"), re.M)
    return int(m.group(1)) if m else None


def read(name: str) -> list[dict]:
    path = DATA / name
    if not path.exists():
        sys.exit(f"{name} is not in data/ -- the count cannot be reconstructed without it")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DATA / "corpus_reconstruction.csv"))
    a = ap.parse_args()

    rows_out = []
    for page, resolve in CORPORA.items():
        names = resolve()
        total = 0
        files: set[str] = set()
        prompts: set[str] = set()
        sizes: set[str] = set()
        per_manifest = []
        for n in names:
            rows = read(n)
            total += len(rows)
            for r in rows:
                files.add(os.path.basename(r["image_path"].replace("\\", "/")))
                prompts.add(r.get("prompt_id", ""))
                w = r.get("width") or r.get("width_px")
                h = r.get("height") or r.get("height_px")
                if w and h:
                    sizes.add(f"{w}x{h}")
            per_manifest.append(f"{n}={len(rows)}")
            print(f"  {n:30s} {len(rows):5d} rows")

        declared = declared_renders(page)
        verdict = ("no corpus.renders in the page" if declared is None
                   else "MATCH" if declared == total
                   else f"MISMATCH: page says {declared}, manifests give {total}")
        rows_out.append({
            "page": page,
            "manifests": " + ".join(per_manifest),
            "n_manifests": len(names),
            "rows": total,
            "distinct_files": len(files),
            "duplicates": total - len(files),
            "prompts": len(prompts),
            "resolutions": " ".join(sorted(sizes)) or "not recorded",
            "declared_corpus_renders": declared if declared is not None else "",
            "verdict": verdict,
        })
        print(f"\n{page}: {total} rows, {len(files)} distinct files, {len(prompts)} prompts, "
              f"resolutions {sorted(sizes)}\n  {verdict}\n")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    print(f"wrote {out}  ({len(rows_out)} rows)")
    if any(r["verdict"].startswith("MISMATCH") for r in rows_out):
        sys.exit(1)


if __name__ == "__main__":
    main()
