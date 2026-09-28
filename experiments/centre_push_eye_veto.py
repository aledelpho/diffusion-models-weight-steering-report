# -*- coding: utf-8 -*-
"""
experiments/centre_push_eye_veto.py
===================================
G_eye of docs/prereg_centre_push.md, which `analyze_centre_push.py` does not implement.

    python experiments/centre_push_eye_veto.py --build   # 12 blind pairs + sealed key
    python experiments/centre_push_eye_veto.py --score   # Alessandro's answers vs the ordering of L

The pre-registration, verbatim:

    G_eye. Twelve pairs, each a central and an end unit with the closest V in the range 1.5-3,
    shown at 1:1 crops (a 512-px centre crop), unlabelled, in random order. Alessandro marks which
    of the two is more broken, or "neither".
    If his answer agrees with the ordering of L in fewer than 8 of the 12 pairs (ties excluded),
    the primary is reported as "L not validated by eye" next to its number, and is not called
    supported.

Three things the pre-registration left open are fixed HERE, before any crop was cut or looked at,
and are reported as such:

  (a) Only 10 end units fall in V in [1.5, 3] against 16 central ones, so twelve pairs cannot be
      built from distinct end units. An end unit may be used TWICE, never more, and never with the
      same seed, so no image appears in two pairs.
  (b) A unit is three renders (three seeds). The one shown is the render whose own L is closest to
      the unit's mean L; a unit used a second time shows the second-closest. The choice does not
      look at the other side of the pair.
  (c) Pairs are matched on V only, as written. Matching within prompt was NOT imposed: it is not in
      the deposited text, and the number of cross-prompt pairs is reported instead so the reader can
      discount them.

`--build` also drops `centre_push_eye_veto.html` next to the sheets as `veto.html`: a self-contained
page that shows one pair at a time at 1:1, carries a 4x nearest-neighbour loupe reading the SAME
region of both crops at once, takes A / B / neither from the keyboard, and writes out the answer CSV.
It loads the PNGs from its own folder and contains no part of the key.

No render is generated. Crops are cut from renders already on disk.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))

import groove_or_hole as G  # noqa: E402

BENCH = "benchmark_centre_push"
PLAN = DATA / "centre_push_plan.csv"
CACHE = DATA / "centre_push_measures.csv"
UNITS = DATA / "centre_push_units.csv"
KEY = DATA / "centre_push_veto_key.csv"
ANSWERS = DATA / "centre_push_veto_answers.csv"
RESULT = DATA / "centre_push_veto_result.csv"

ENDS = {"Block_1", "Block_6"}
V_LO, V_HI = 1.5, 3.0
N_PAIRS = 12
MAX_REUSE = 2
CROP = 512
SEED = 20260928


def cell_L() -> dict:
    """L per render: structure coherence over the baseline of its own prompt and seed.
    Same definition as analyze_centre_push.py, read from the same cache."""
    plan = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    meas = {r["file"]: r for r in csv.DictReader(open(CACHE, encoding="utf-8"))}
    base = {(r["prompt_id"], r["seed"]): r["expected_filename"] for r in plan if r["arm"] == "baseline"}
    out = {}
    for r in plan:
        if r["arm"] != "push":
            continue
        fn, bfn = r["expected_filename"], base[(r["prompt_id"], r["seed"])]
        if fn not in meas or bfn not in meas:
            continue
        key = (r["block_input"], "pos" if float(r["gain"]) > 0 else "neg",
               f"{abs(float(r['gain'])):.3f}", r["prompt_id"])
        out.setdefault(key, []).append(
            {"file": fn, "seed": r["seed"],
             "L": float(meas[fn]["coherence"]) / float(meas[bfn]["coherence"])})
    return out


def build() -> None:
    from PIL import Image

    units = [u for u in csv.DictReader(open(UNITS, encoding="utf-8")) if V_LO <= float(u["V"]) <= V_HI]
    for u in units:
        u["id"] = f"{u['group']}_{u['sign']}_{u['dose']}_{u['prompt']}"
    centres = [u for u in units if u["position"] == "centre"]
    ends = [u for u in units if u["position"] == "end"]
    print(f"  units in V[{V_LO},{V_HI}]: {len(centres)} centre, {len(ends)} end")

    cand = sorted(((abs(float(c["V"]) - float(e["V"])), c["id"], e["id"], c, e)
                   for c in centres for e in ends), key=lambda t: t[:3])
    used_c, used_e, pairs = set(), {}, []
    for dv, cid, eid, c, e in cand:
        if len(pairs) == N_PAIRS:
            break
        if cid in used_c or used_e.get(eid, 0) >= MAX_REUSE:
            continue
        used_c.add(cid)
        used_e[eid] = used_e.get(eid, 0) + 1
        pairs.append((dv, c, e, used_e[eid]))
    if len(pairs) < N_PAIRS:
        sys.exit(f"only {len(pairs)} pairs available")

    cells = cell_L()
    picked = set()

    def pick(u, nth):
        cs = cells[(u["group"], u["sign"], u["dose"], u["prompt"])]
        mu = statistics.fmean(c["L"] for c in cs)
        order = sorted(cs, key=lambda c: (abs(c["L"] - mu), c["seed"]))
        for c in order:
            if c["file"] not in picked:
                picked.add(c["file"])
                return c
        sys.exit(f"no unused render for {u['id']}")

    rng = random.Random(SEED)
    out_dir = G.RENDER_ROOTS[0] / BENCH / "_eye_veto"
    for r in G.RENDER_ROOTS:
        if (r / BENCH).is_dir():
            out_dir = r / BENCH / "_eye_veto"
            break
    out_dir.mkdir(parents=True, exist_ok=True)

    def crop(fn):
        p = G.find_render(BENCH, fn)
        if p is None:
            sys.exit(f"render not found: {fn}")
        im = Image.open(p).convert("RGB")
        w, h = im.size
        x, y = (w - CROP) // 2, (h - CROP) // 2
        return im.crop((x, y, x + CROP, y + CROP))  # 1:1, never resampled

    rows = []
    for i, (dv, c, e, nth) in enumerate(pairs, 1):
        cc, ec = pick(c, nth), pick(e, nth)
        sides = [("centre", c, cc), ("end", e, ec)]
        rng.shuffle(sides)
        (pa, ua, ca), (pb, ub, cb) = sides
        sheet = Image.new("RGB", (CROP * 2 + 24, CROP), (255, 255, 255))
        sheet.paste(crop(ca["file"]), (0, 0))
        sheet.paste(crop(cb["file"]), (CROP + 24, 0))
        name = f"pair{i:02d}.png"
        sheet.save(out_dir / name)
        dL = ca["L"] - cb["L"]
        rows.append({
            "pair": f"{i:02d}", "sheet": name, "dV": f"{dv:.4f}",
            "cross_prompt": str(ua["prompt"] != ub["prompt"]),
            "A_position": pa, "A_unit": ua["id"], "A_file": ca["file"],
            "A_V": f"{float(ua['V']):.4f}", "A_L": f"{ca['L']:.4f}",
            "B_position": pb, "B_unit": ub["id"], "B_file": cb["file"],
            "B_V": f"{float(ub['V']):.4f}", "B_L": f"{cb['L']:.4f}",
            "dL_A_minus_B": f"{dL:+.4f}",
            "L_says_more_broken": "A" if dL < 0 else "B",
        })

    with open(KEY, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    if not ANSWERS.exists():
        with open(ANSWERS, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["pair", "more_broken"])  # A | B | neither
            for r in rows:
                w.writerow([r["pair"], ""])
    page = ROOT / "experiments" / "centre_push_eye_veto.html"
    if page.is_file():
        (out_dir / "veto.html").write_text(page.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  veto.html -> {out_dir} (open it in a browser at 100 % zoom)")
    print(f"  {len(rows)} sheets -> {out_dir}")
    print(f"  sealed key -> {KEY}")
    print(f"  blank answer form -> {ANSWERS}")
    print(f"  cross-prompt pairs: {sum(r['cross_prompt'] == 'True' for r in rows)}/{len(rows)}")


def score() -> None:
    key = {r["pair"]: r for r in csv.DictReader(open(KEY, encoding="utf-8"))}
    ans = {r["pair"]: r["more_broken"].strip().upper() for r in csv.DictReader(open(ANSWERS, encoding="utf-8"))}
    rows, agree, judged = [], 0, 0
    for p in sorted(key):
        a, k = ans.get(p, ""), key[p]
        ok = ""
        if a in ("A", "B"):
            judged += 1
            ok = str(a == k["L_says_more_broken"])
            agree += a == k["L_says_more_broken"]
        rows.append({"pair": p, "answer": a or "(blank)", "L_says": k["L_says_more_broken"],
                     "dL_A_minus_B": k["dL_A_minus_B"], "agrees": ok})
    # exact two-sided sign test against chance on the judged pairs
    def C(n, k):
        return math.comb(n, k)
    pv = ""
    if judged:
        tail = sum(C(judged, i) for i in range(agree, judged + 1)) / 2 ** judged
        pv = f"{min(1.0, 2 * tail):.4f}"
    verdict = "L validated by eye" if agree >= 8 else "L not validated by eye"
    rows.append({"pair": "TOTAL", "answer": f"{judged} judged", "L_says": f"{agree} agree",
                 "dL_A_minus_B": f"p={pv}", "agrees": verdict})
    with open(RESULT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print("  " + "  ".join(f"{v}" for v in r.values()))
    print(f"  -> {RESULT}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.build:
        build()
    if a.score:
        score()
    if not (a.build or a.score):
        ap.error("--build or --score")


if __name__ == "__main__":
    main()
