"""C52 amendment 1 — blind forced choice (docs/prereg_portrait_preset.md). Written 2026-10-05.

  python portrait_preset_blind.py --sheets   # 56 sheets (28 original + 28 mirrored) + data/portrait_preset_blind_key.csv
  python portrait_preset_blind.py --tally    # rules on data/portrait_preset_blind_answers.csv

Sheets go to Text2Img/benchmark_portraits/blind/sheet_XXXX.png with random ids, so neither the file
name nor the order says which character, seed, side or set a sheet belongs to.
Answers file columns: sheet, observer, q1 (LEFT/RIGHT), q2 (YES/NO).
"""
import argparse, csv, os, sys
from math import comb
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from portraits import CALIBRATION, HELD_OUT, SEEDS_C, FOLDER_C, IMG_ROOT

DATA = os.path.join(HERE, "..", "data")
KEY = os.path.join(DATA, "portrait_preset_blind_key.csv")
ANS = os.path.join(DATA, "portrait_preset_blind_answers.csv")
OUT = os.path.join(str(IMG_ROOT), "benchmark_portraits", "blind")


def sheets():
    from PIL import Image, ImageDraw, ImageFont
    rng = np.random.default_rng(52)
    pairs = [(g, c, s) for g, chars in (("held_out", HELD_OUT), ("calibration", CALIBRATION)) for c in chars for s in SEEDS_C]
    preset_left = rng.integers(0, 2, len(pairs)).astype(bool)
    ids = rng.permutation(np.arange(1000, 9999))[: 2 * len(pairs)]
    os.makedirs(OUT, exist_ok=True)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    rows = []
    for k, (g, c, s) in enumerate(pairs):
        for j, (st, pl) in enumerate((("original", preset_left[k]), ("mirrored", not preset_left[k]))):
            a = Image.open(os.path.join(str(IMG_ROOT), FOLDER_C, f"{c}_baseline_krea2_seed{s}_00001_.png")).convert("RGB").resize((512, 640), Image.LANCZOS)
            b = Image.open(os.path.join(str(IMG_ROOT), FOLDER_C, f"{c}_preset_krea2_seed{s}_00001_.png")).convert("RGB").resize((512, 640), Image.LANCZOS)
            L, R = (b, a) if pl else (a, b)
            S = Image.new("RGB", (512 * 2 + 24, 640 + 48), (128, 128, 128)); d = ImageDraw.Draw(S)
            S.paste(L, (0, 48)); S.paste(R, (512 + 24, 48))
            d.text((210, 8), "LEFT", fill=(0, 0, 0), font=font); d.text((512 + 24 + 200, 8), "RIGHT", fill=(0, 0, 0), font=font)
            sid = f"sheet_{ids[2 * k + j]}"
            S.save(os.path.join(OUT, sid + ".png"))
            rows.append({"sheet": sid, "set": st, "group": g, "char": c, "seed": s, "preset_side": "LEFT" if pl else "RIGHT"})
    with open(KEY, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("sheets", len(rows), "->", OUT)


def binom_p(k, n):
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def tally():
    key = {r["sheet"]: r for r in csv.DictReader(open(KEY))}
    votes = {}
    for r in csv.DictReader(open(ANS)):
        votes.setdefault(r["sheet"], []).append((r["q1"].strip().upper(), r["q2"].strip().upper()))
    maj = {}
    for sid, v in votes.items():
        assert len(v) == 3, (sid, len(v))
        side = max(("LEFT", "RIGHT"), key=lambda x: sum(a == x for a, _ in v))
        same = sum(b == "YES" for _, b in v) >= 2
        maj[sid] = (side, same)
    pair = lambda r: (r["char"], r["seed"])
    orig = {pair(r): (sid, r) for sid, r in key.items() if r["set"] == "original"}
    mirr = {pair(r): (sid, r) for sid, r in key.items() if r["set"] == "mirrored"}
    same_side = sum(maj[orig[p][0]][0] == maj[mirr[p][0]][0] for p in orig)
    gate = same_side / len(orig) <= 0.75
    out = [("position gate: pairs where both sets name the same side", f"{same_side}/{len(orig)}", "pass" if gate else "VOID")]
    for grp in ("held_out", "calibration"):
        P = [p for p in orig if orig[p][1]["group"] == grp]
        res = {}
        for st, D in (("original", orig), ("mirrored", mirr)):
            pick = sum(maj[D[p][0]][0] == D[p][1]["preset_side"] for p in P)
            yes = sum(maj[D[p][0]][1] for p in P)
            res[st] = (pick, yes)
            out.append((f"{grp} {st}: preset chosen", f"{pick}/{len(P)} (p = {binom_p(pick, len(P)):.4f})", ""))
            out.append((f"{grp} {st}: same character YES", f"{yes}/{len(P)}", ""))
        if grp == "held_out":
            lo4 = min(res["original"][0], res["mirrored"][0]); lo5 = min(res["original"][1], res["mirrored"][1])
            h4 = "void" if not gate else "supported" if lo4 >= 9 else "refuted" if lo4 <= 6 else "inconclusive"
            h5 = "void" if not gate else "supported" if lo5 >= 9 else "refuted" if lo5 <= 6 else "inconclusive"
            out += [("H4 look visible blind (>= 9/12 both sets; <= 6 either)", lo4, h4),
                    ("H5 character kept (>= 9/12 both sets; <= 6 either)", lo5, h5)]
    with open(os.path.join(DATA, "portrait_preset_blind_tests.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["test", "value", "verdict"]); w.writerows(out)
    for o in out:
        print(" | ".join(str(x) for x in o))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sheets", action="store_true"); ap.add_argument("--tally", action="store_true")
    a = ap.parse_args()
    if a.sheets: sheets()
    if a.tally: tally()
