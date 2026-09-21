# -*- coding: utf-8 -*-
"""experiments/extract_repro.py -- prove a reproducibility block against the repository.

AUTHORING.md section 5 has told an author since the contract was written to print this block
rather than type it from memory, and named this script. The script did not exist. Every block
in the notebook was therefore typed by hand, and an audit on 2026-09-21 found four fields
wrong -- including a resolution on a page that had been published for a day.

WHAT THIS CAN AND CANNOT DO. The renders live outside the repository, so this cannot read a
PNG's embedded graph. What it can do is read the manifests and feature tables in `data/`,
which record, per image, the sampler configuration and the pixel dimensions the render
actually had. Where a field is recorded there, it is provable and this script proves it.
Where it is not, the script says so rather than guessing, and the honest thing in the block
is a `not recorded` marker naming what would record it.

USE
    python experiments/extract_repro.py                 # audit every page
    python experiments/extract_repro.py 08-block1-vs-block6
    python experiments/extract_repro.py --check         # exit 1 on any mismatch
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                       # pragma: no cover
    sys.exit("extract_repro.py needs PyYAML:  pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
NOTEBOOK = ROOT / "notebook"

# Which files in data/ record the renders of each bench, and why that association holds.
# This map is the one hand-written thing here, so it is written once, in the open, and every
# entry names the evidence rather than a belief.
EVIDENCE: dict[str, dict] = {
    "00-the-bench": {
        # bench_checks.csv is a ledger of checks, not a render manifest: no per-image row,
        # no dimensions, no sampler. Nothing in the repository records this bench's renders.
        "dims": [],
        "manifest": None,
    },
    "02-attribute-emergence": {
        # The barnacle arm has no dimension column. The headlight arm rides on the stage 9
        # renders, whose manifest does record them.
        "dims": ["stage9_images.csv"],
        "manifest": "attribute_emergence.csv",
    },
    "03-what-ends-up-in-the-picture": {
        "dims": ["stage12_images.csv", "palette_features_stage12.csv",
                 "style_features_stage12.csv"],
        "manifest": "stage12_images.csv",
    },
    "04-where-in-the-model": {
        # The nine source reports are outside the repository; the features harvested from
        # their images are not, and they carry the dimensions.
        "dims": ["pilot_rotations_style_features.csv", "pilot_rotations_palette_features.csv"],
        "manifest": "pilot_rotations.csv",
    },
    "05-knob-or-cost": {
        # direzioni_blocchi_singoli.jsonl holds the positive arm of the 28-block sweep
        # (168 images = 28 blocks x 2 prompts x 3 seeds, plus 6 baselines) with dimensions.
        "dims": ["direzioni_blocchi_singoli.jsonl"],
        "manifest": None,
    },
    "06-the-hatching-axis": {
        "dims": ["stage7b_images.csv", "palette_features_stage7_all.csv"],
        "manifest": "stage7b_images.csv",
    },
    "07-chromatic-signatures": {
        "dims": ["stage7b_images.csv", "palette_features_stage7_all.csv"],
        "manifest": "stage7b_images.csv",
    },
    "08-block1-vs-block6": {
        "dims": ["rotations_block1_vs_block6_style_features.csv",
                 "rotations_block1_vs_block6_palette_features.csv"],
        "manifest": "rotations_block1_vs_block6_manifest.csv",
    },
    "09-style-direction": {
        "dims": ["stage9_images.csv", "palette_features_stage9.csv"],
        "manifest": "stage9_images.csv",
    },
}

MANIFEST_FIELDS = {"sampler": ["sampler"], "steps": ["steps"], "cfg": ["cfg"]}


def _rows(name: str) -> list[dict]:
    f = DATA / name
    if not f.exists():
        return []
    if f.suffix == ".jsonl":
        out = []
        for line in f.open(encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return out
    return list(csv.DictReader(f.open(encoding="utf-8-sig", newline="")))


def dimensions(page: str) -> tuple[set[str], list[str]]:
    """Every (width x height) recorded for this bench, and the files that recorded it."""
    seen, sources = set(), []
    for name in EVIDENCE.get(page, {}).get("dims", []):
        rows = _rows(name)
        if not rows:
            continue
        keys = rows[0].keys()
        w = "width" if "width" in keys else ("width_px" if "width_px" in keys else None)
        h = "height" if "height" in keys else ("height_px" if "height_px" in keys else None)
        if not (w and h):
            continue
        before = len(seen)
        seen |= {f"{r[w]}x{r[h]}" for r in rows}
        sources.append(f"{name} ({len(rows)} rows{', new value' if len(seen) > before else ''})")
    return seen, sources


def sampling(page: str) -> tuple[dict, str | None]:
    """Sampler, steps and cfg as the bench's own manifest records them."""
    name = EVIDENCE.get(page, {}).get("manifest")
    rows = _rows(name) if name else []
    if not rows:
        return {}, name
    out = {}
    for field, cols in MANIFEST_FIELDS.items():
        for c in cols:
            if c in rows[0]:
                out[field] = sorted({(r[c] or "").strip() for r in rows})
                break
    return out, name


def displacements() -> dict[str, float]:
    out = {}
    for r in _rows("preset_displacements.csv"):
        out[r["preset_name"]] = float(r["d_model_relative"])
    cal = DATA / "matched_rotation_calibration.json"
    if cal.exists():
        d = json.loads(cal.read_text(encoding="utf-8"))
        for k, v in d.items():
            if isinstance(v, dict) and "d_model" in v:
                out[k] = float(v["d_model"])
    return out


def published(page: str) -> dict | None:
    f = NOTEBOOK / f"{page}.md"
    if not f.exists():
        return None
    m = re.search(r"###\s+Reproducing this\s*\n+```ya?ml\n(.*?)```",
                  f.read_text(encoding="utf-8"), re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None


def mismatches(page: str, block: dict | None = None) -> list[str]:
    """What the published block asserts that the repository contradicts."""
    block = block if block is not None else published(page)
    if not block:
        return []
    bad = []

    dims, _ = dimensions(page)
    claimed = str((block.get("sampling") or {}).get("resolution", "")).strip()
    if dims:
        if len(dims) > 1:
            bad.append(f"the bench's own files record more than one resolution: "
                       f"{sorted(dims)} -- a single value cannot be published")
        elif claimed.replace(" ", "").lower() not in {d.lower() for d in dims}:
            only = sorted(dims)[0]
            bad.append(f"resolution says '{claimed}', the bench's own files record {only}")

    samp, manifest_name = sampling(page)
    for field, values in samp.items():
        if len(values) != 1:
            bad.append(f"{field} is not constant across {manifest_name}: {values}")
            continue
        got, want = str((block.get("sampling") or {}).get(field, "")).strip(), values[0]
        if got and got.rstrip("0").rstrip(".") != want.rstrip("0").rstrip("."):
            bad.append(f"{field} says '{got}', {manifest_name} records '{want}'")

    for key in ("manifest",):
        named = str((block.get("outputs") or {}).get(key, "")).strip()
        # A field that opens by declaring no manifest exists is allowed to go on and name the
        # file it used to name, and the files that stand in for one.
        if named.lower().startswith(("no ", "none")):
            continue
        for f in re.findall(r"data/[\w./-]+", named):
            if not (ROOT / f).exists():
                bad.append(f"outputs.{key} names '{f}', which is not in the repository")

    known = displacements()
    for cond in block.get("conditions") or []:
        preset = str(cond.get("preset") or "").replace(".json", "")
        d = cond.get("measured_D")
        if preset and preset in known and isinstance(d, (int, float)):
            if abs(float(d) - known[preset]) > 1e-8:
                bad.append(f"condition '{cond.get('name')}' says D = {d}, "
                           f"preset_displacements.csv records {known[preset]}")
    return bad


def report() -> int:
    worst = 0
    for page in sorted(EVIDENCE):
        block = published(page)
        dims, sources = dimensions(page)
        samp, manifest_name = sampling(page)
        print(f"\n== {page}")
        print(f"   resolution  : {sorted(dims) or 'NOT RECORDED anywhere in data/'}")
        for s in sources:
            print(f"                 from {s}")
        if samp:
            print(f"   sampling    : "
                  f"{ {k: (v[0] if len(v) == 1 else v) for k, v in samp.items()} }"
                  f"  from {manifest_name}")
        else:
            print(f"   sampling    : NOT RECORDED"
                  f"{f' in {manifest_name}' if manifest_name else ' -- no manifest named'}")
        if block is None:
            print("   published   : no reproducibility block found")
            continue
        bad = mismatches(page, block)
        worst = max(worst, len(bad))
        for b in bad:
            print(f"   MISMATCH    : {b}")
        if not bad:
            print("   published   : agrees with the repository on every provable field")
    print()
    return 1 if worst else 0


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    if args:
        page = args[0].removesuffix(".md")
        dims, sources = dimensions(page)
        samp, manifest_name = sampling(page)
        print(f"# provable fields for {page}, read out of data/")
        print("sampling:")
        for k, v in samp.items():
            print(f"  {k}: {v[0] if len(v) == 1 else v}")
        print(f"  resolution: {sorted(dims)[0] if len(dims) == 1 else (sorted(dims) or 'not recorded')}")
        for s in sources:
            print(f"# resolution source: {s}")
        for b in mismatches(page):
            print(f"# MISMATCH: {b}")
        return 0
    return report()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
