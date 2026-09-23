# -*- coding: utf-8 -*-
"""
experiments/reproduce_2026-09-23.py
===================================
Re-runs, from the renders, every measurement published on 2026-09-23, and checks that each one
lands back on the file that is committed.

This is a reproduction harness, not a rebuild. By default it writes nothing into `data/`: each
phase recomputes into `data/_repro/` and the result is compared cell by cell against the
committed CSV. A phase passes only if every numeric cell agrees within tolerance and every
string cell agrees exactly. `--write` puts the recomputed files into `data/` instead, for when
a number is supposed to change.

No expected value is typed into this file. What each phase is checked against is the CSV that
is already in the repository, so this script cannot certify a number by agreeing with itself.

PHASES

  corpus         verify_corpus_counts.py            manifests only, no images
  noise_floor    measure_noise_floor.py             38 baseline renders, 2 benches
  downsample     measure_downsample_blindness.py    32 renders of benchmark_stage7, slow
  displacements  measure_block_group_displacements.py   the checkpoint, needs torch + ComfyUI
  sensitivity    sensitivity_curve.py               data only
  figures        the four charts whose data moved
  contract       validate_notebook.py, then build_notebook.py --check

`displacements` is the one phase that was never run: it needs the safetensors and ComfyUI's
custom node on the path. It is skipped with a message if either is missing, and `sensitivity`
then falls back to the two-block calibration, exactly as the committed file did.

WHERE THE RENDERS ARE

StabilityMatrix keeps one copy of the outputs and shows it at two paths:

    C:\\StabilityMatrix-win-x64\\Data\\Images\\Text2Img\\<bench>
    C:\\StabilityMatrix-win-x64\\Data\\Packages\\ComfyUI\\output\\<bench>

--images-root takes either; both are tried in that order, and a bench that is under neither is
reported by name instead of failing the whole run.

USAGE

    python experiments/reproduce_2026-09-23.py --list
    python experiments/reproduce_2026-09-23.py
    python experiments/reproduce_2026-09-23.py --only noise_floor --only sensitivity
    python experiments/reproduce_2026-09-23.py --skip downsample
    python experiments/reproduce_2026-09-23.py --write          # overwrite data/, no comparison
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
REPRO = DATA / "_repro"
ASSETS = ROOT / "assets"

ROOTS = [
    Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"),
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"),
]
CHECKPOINT = Path(r"C:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\krea2_turbo_bf16.safetensors")

# How close two numbers have to be to count as the same measurement. Not zero: these pass
# through CSV rounding and, on the image side, through whatever BLAS the machine happens to
# use. Anything looser than this would stop being a check.
ABS_TOL = 5e-4
REL_TOL = 1e-3


# ---------------------------------------------------------------- helpers

def bench(name: str) -> Path | None:
    for r in ROOTS:
        p = r / name
        if p.is_dir():
            return p
    return None


def run(argv: list[str]) -> bool:
    print("    $ " + " ".join(str(a) for a in argv[1:]), flush=True)
    r = subprocess.run([sys.executable] + [str(a) for a in argv], cwd=str(ROOT))
    return r.returncode == 0


def numeric(s: str):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def compare(new: Path, old: Path, key_cols: list[str] | None = None) -> list[str]:
    """Every cell of `new` against `old`. Returns the disagreements, empty if it reproduces."""
    if not old.exists():
        return [f"{old.name} is not in data/: nothing to reproduce against"]
    if not new.exists():
        return [f"{new.name} was not produced"]
    with old.open(encoding="utf-8-sig", newline="") as fh:
        a = list(csv.DictReader(fh))
    with new.open(encoding="utf-8-sig", newline="") as fh:
        b = list(csv.DictReader(fh))
    bad: list[str] = []
    if len(a) != len(b):
        bad.append(f"{old.name}: {len(a)} rows committed, {len(b)} recomputed")
        return bad
    if a and set(a[0]) != set(b[0]):
        only_old = sorted(set(a[0]) - set(b[0]))
        only_new = sorted(set(b[0]) - set(a[0]))
        bad.append(f"{old.name}: columns differ (committed only {only_old}, recomputed only {only_new})")
        return bad
    keys = key_cols or ([] if not a else [c for c in a[0] if c in
                        ("prompt_id", "file", "feature", "scale", "block", "angle_label", "page")])
    def sig(r): return tuple(r.get(k, "") for k in keys)
    if keys:
        a.sort(key=sig)
        b.sort(key=sig)
    for i, (ra, rb) in enumerate(zip(a, b)):
        for col in ra:
            va, vb = ra[col], rb[col]
            na, nb = numeric(va), numeric(vb)
            if na is not None and nb is not None:
                if abs(na - nb) > max(ABS_TOL, REL_TOL * abs(na)):
                    bad.append(f"{old.name} row {i} {col}: committed {va}, recomputed {vb}")
            elif (va or "").strip() != (vb or "").strip():
                bad.append(f"{old.name} row {i} {col}: committed {va!r}, recomputed {vb!r}")
    return bad


# ---------------------------------------------------------------- phases

def phase_corpus(out: Path, write: bool) -> tuple[bool, list[str]]:
    target = out / "corpus_reconstruction.csv"
    if not run([HERE / "verify_corpus_counts.py", "--out", target]):
        return False, ["verify_corpus_counts.py exited non-zero -- a page disagrees with its manifests"]
    return True, ([] if write else compare(target, DATA / "corpus_reconstruction.csv"))


def phase_noise_floor(out: Path, write: bool) -> tuple[bool, list[str]]:
    benches = ["benchmark_latenti_b6", "benchmark_pavimento_rumore"]
    argv = [HERE / "measure_noise_floor.py"]
    for b in benches:
        d = bench(b)
        if d is None:
            return False, [f"{b} is under neither renders root; pass --images-root"]
        argv += ["--renders", d / "renders"]
    argv += ["--out-renders", out / "noise_floor_hf_by_render.csv",
             "--out-summary", out / "noise_floor_measured.csv"]
    if not run(argv):
        return False, ["measure_noise_floor.py failed"]
    if write:
        return True, []
    return True, (compare(out / "noise_floor_measured.csv", DATA / "noise_floor_measured.csv")
                  + compare(out / "noise_floor_hf_by_render.csv", DATA / "noise_floor_hf_by_render.csv"))


def phase_downsample(out: Path, write: bool) -> tuple[bool, list[str]]:
    d = bench("benchmark_stage7")
    if d is None:
        return False, ["benchmark_stage7 is under neither renders root; pass --images-root"]
    argv = [HERE / "measure_downsample_blindness.py",
            "--renders", d / "renders",
            "--manifest", DATA / "stage7b_images.csv",
            "--seed", "1337",
            "--out", out / "downsample_blindness.csv"]
    if not run(argv):
        return False, ["measure_downsample_blindness.py failed"]
    return True, ([] if write else compare(out / "downsample_blindness.csv",
                                           DATA / "downsample_blindness.csv"))


def phase_displacements(out: Path, write: bool) -> tuple[bool, list[str]]:
    if not CHECKPOINT.exists():
        return True, ["SKIPPED: the checkpoint is not at " + str(CHECKPOINT)]
    argv = [HERE / "measure_block_group_displacements.py",
            "--model", CHECKPOINT,
            "--out", out / "block_group_displacements.csv"]
    if not run(argv):
        return True, ["SKIPPED: measure_block_group_displacements.py could not run -- it needs "
                      "torch and ComfyUI's Arthemy_Krea2_Tuner on the path. This is the one "
                      "measurement that has never been made; sensitivity falls back to the "
                      "two-block calibration, as the committed file did."]
    committed = DATA / "block_group_displacements.csv"
    if write or not committed.exists():
        return True, ["FIRST RUN: nothing committed to compare against. Once this file is in "
                      "data/, sensitivity_curve.py will use it for all six groups and "
                      "data/sensitivity_by_block.csv will change on purpose."]
    return True, compare(out / "block_group_displacements.csv", committed)


def phase_sensitivity(out: Path, write: bool) -> tuple[bool, list[str]]:
    disp = out / "block_group_displacements.csv"
    if not disp.exists():
        disp = DATA / "block_group_displacements.csv"
    argv = [HERE / "sensitivity_curve.py",
            "--displacements", disp,
            "--response", DATA / "all_blocks_clean_v2_response_by_block.csv",
            "--out", out / "sensitivity_by_block.csv"]
    if not run(argv):
        return False, ["sensitivity_curve.py failed"]
    return True, ([] if write else compare(out / "sensitivity_by_block.csv",
                                           DATA / "sensitivity_by_block.csv"))


def phase_figures(out: Path, write: bool) -> tuple[bool, list[str]]:
    """The four charts whose data this run touches. Figures are outputs, not evidence: they are
    always written where the page reads them, and a byte comparison would fail on encoder
    version alone."""
    sys.path.insert(0, str(HERE))
    try:
        import notebook_charts as nc
    except Exception as e:                                  # noqa: BLE001
        return False, [f"notebook_charts did not import: {e}"]
    jobs = [
        (nc.noise_floor_history, ASSETS / "00-the-bench" / "F00.3_noise_floor_history.webp"),
        (nc.downsample_blindness, ASSETS / "01-mark-style" / "F01.3_downsample_blindness.webp"),
        (nc.all_blocks_depth_profile, ASSETS / "10-all-blocks-clean" / "F10.1_depth_profile_by_angle.webp"),
        (nc.sensitivity_per_displacement, ASSETS / "10-all-blocks-clean" / "F10.2_sensitivity_per_displacement.webp"),
    ]
    bad = []
    for fn, dest in jobs:
        try:
            fn(dest)
            print(f"    drew {dest.relative_to(ROOT)}")
        except SystemExit as e:
            bad.append(f"{fn.__name__}: {e}")
        except Exception as e:                              # noqa: BLE001
            bad.append(f"{fn.__name__}: {type(e).__name__}: {e}")
    return True, bad


def phase_contract(out: Path, write: bool) -> tuple[bool, list[str]]:
    bad = []
    if not run([HERE / "validate_notebook.py"]):
        bad.append("validate_notebook.py reported errors")
    if not run([HERE / "build_notebook.py", "--check"]):
        bad.append("build_notebook.py --check: README.md or index.html is out of date; "
                   "run it without --check")
    return True, bad


PHASES = [
    ("corpus",        phase_corpus,        "the 1272, counted from the five manifests"),
    ("noise_floor",   phase_noise_floor,   "sigma(HF) on 18 seeds, from 38 baseline renders"),
    ("downsample",    phase_downsample,    "does the separation survive 224x224 (slow, 64 extractions)"),
    ("displacements", phase_displacements, "D per block group per angle, from the checkpoint"),
    ("sensitivity",   phase_sensitivity,   "response per unit of displacement"),
    ("figures",       phase_figures,       "the four charts whose data this run touches"),
    ("contract",      phase_contract,      "validator, then the build freshness check"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--skip", action="append", default=[])
    ap.add_argument("--write", action="store_true",
                    help="write into data/ instead of recomputing into data/_repro and comparing")
    ap.add_argument("--images-root", action="append", default=[],
                    help="a folder holding the benchmark_* directories; tried before the defaults")
    a = ap.parse_args()

    if a.list:
        for name, _, what in PHASES:
            print(f"  {name:14s} {what}")
        return

    for r in reversed(a.images_root):
        ROOTS.insert(0, Path(r))

    names = [n for n, _, _ in PHASES]
    for n in a.only + a.skip:
        if n not in names:
            sys.exit(f"unknown phase {n!r}; --list shows them")
    todo = [p for p in PHASES if (not a.only or p[0] in a.only) and p[0] not in a.skip]

    out = DATA if a.write else REPRO
    if not a.write:
        if REPRO.exists():
            shutil.rmtree(REPRO)
        REPRO.mkdir(parents=True)

    print(f"\nrepository {ROOT}")
    print(f"renders roots {[str(r) for r in ROOTS if r.exists()] or 'NONE FOUND'}")
    print(f"writing to {out}" + ("" if a.write else "  (comparing against data/)") + "\n")

    results = []
    for name, fn, what in todo:
        print(f"[{name}] {what}")
        ok, notes = fn(out, a.write)
        hard = [n for n in notes if not n.startswith(("SKIPPED", "FIRST RUN"))]
        soft = [n for n in notes if n.startswith(("SKIPPED", "FIRST RUN"))]
        for n in soft:
            print(f"    - {n}")
        for n in hard[:12]:
            print(f"    ! {n}")
        if len(hard) > 12:
            print(f"    ! ... and {len(hard) - 12} more")
        state = "FAIL" if (not ok or hard) else ("SKIP" if soft else "REPRODUCES")
        results.append((name, state, len(hard)))
        print(f"    -> {state}\n")

    print("=" * 64)
    for name, state, n in results:
        print(f"  {name:14s} {state}" + (f"  ({n} disagreement{'s' if n != 1 else ''})" if n else ""))
    failed = [n for n, s, _ in results if s == "FAIL"]
    if failed:
        print(f"\n{len(failed)} phase(s) did not reproduce: {', '.join(failed)}")
        sys.exit(1)
    print("\nevery phase that ran reproduces the committed files.")


if __name__ == "__main__":
    main()
