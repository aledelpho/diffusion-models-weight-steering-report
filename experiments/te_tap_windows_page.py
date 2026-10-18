"""C87 blind control (docs/prereg_te_tap_windows.md, section 3): 36 of the 156 renders (RNG 8787, 12 forward, 12
backward, 12 single windows; also balanced by character: 4 per family and character) + the 6 plain baselines, with
2 repeats per character, labelled blind with C75's positive questions (as C79). Written 2026-10-18 after the renders,
before any label and before any C87 count.

  python te_tap_windows_page.py --key                          # data/te_tap_windows_key.csv, _schedule.csv
  python te_tap_windows_page.py --page --img-root <Text2Img>   # Text2Img/_grid_viewer/te_tap_windows/index.html
"""
import argparse, csv, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_traits_page as TP
import te_tap_windows as W

DATA = HERE.parent / "data"
CHARS = TP.CHARS                       # {"D1": "D1_dwarf_paladin", ...}
RNG_SEED = 8787
N_REPEAT = 2
IMG_ROOT = Path(".")
TP.MIN_GAP = 6     # 14 pictures per character


def pictures(rng):
    plan = [r for r in W.TI.rd(W.PLAN)]
    out = []
    short = {v: k for k, v in CHARS.items()}
    for fam in ("F", "B", "S"):
        for ch in W.CHARS:
            pool = [r for r in plan if r["char"] == ch and r["cond_tag"].startswith(fam)]
            for r in rng.sample(pool, 4):
                out.append({"char": short[ch], "seed": r["seed"], "cond": r["cond_tag"], "taps": r["taps"],
                            "file": f"{W.FOLDER}/{r['expected_filename']}"})
    for ch in W.CHARS:
        for s in W.SEEDS:
            out.append({"char": short[ch], "seed": s, "cond": "baseline", "taps": "",
                        "file": f"benchmark_portraits/phase_c/{ch}_baseline_krea2_seed{s}_00001_.png"})
    return out


def make_key():
    rng = random.Random(RNG_SEED)
    pics = pictures(rng); rng.shuffle(pics)
    for n, p in enumerate(pics, 1):
        p["item"] = f"W{n:03d}"
    reps = {}
    for c in CHARS:
        mine = [p for p in pics if p["char"] == c]
        first = rng.choice([p for p in mine if p["cond"] == "baseline"])
        reps[c] = [first["item"]] + [p["item"] for p in rng.sample([p for p in mine if p is not first], N_REPEAT - 1)]
    for p in pics:
        p["repeated"] = int(p["item"] in reps[p["char"]])
    with open(DATA / "te_tap_windows_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item", "char", "seed", "cond", "taps", "repeated", "file"])
        w.writeheader(); w.writerows(sorted(pics, key=lambda p: p["item"]))
    per = TP.questions(); sched = []
    for c in CHARS:
        ids = [p["item"] for p in pics if p["char"] == c]
        qs = per[c][:]; rng.shuffle(qs)
        for q, kind in [(q, "trait") for q in qs] + [("skin", "skin"), ("person", "person")]:
            for k, (i, sh) in enumerate(TP.block_order(rng, ids, reps[c])):
                sched.append({"block": f"{c}:{q}", "char": c, "question": q, "kind": kind, "pos": k, "item": i, "showing": sh})
    with open(DATA / "te_tap_windows_schedule.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sched[0])); w.writeheader(); w.writerows(sched)
    from collections import Counter
    print("items", len(pics), Counter(p["cond"][0] if p["cond"] != "baseline" else "base" for p in pics),
          "schedule rows", len(sched), "blocks", len({s['block'] for s in sched}))


def make_page():
    from PIL import Image
    key = {r["item"]: r for r in TP.rd(DATA / "te_tap_windows_key.csv")}
    sched = TP.rd(DATA / "te_tap_windows_schedule.csv")
    out = IMG_ROOT / "_grid_viewer" / "te_tap_windows"; (out / "img").mkdir(parents=True, exist_ok=True)
    def jpg(src, dst):
        if not dst.exists():
            im = Image.open(IMG_ROOT / src).convert("RGB"); im.thumbnail((720, 900), Image.LANCZOS); im.save(dst, "JPEG", quality=88)
    ref = {}
    for it, r in key.items():
        jpg(r["file"], out / "img" / f"{it}.jpg")
        name = f"ref_{r['char']}_{r['seed']}.jpg"
        jpg(f"benchmark_portraits/phase_c/{CHARS[r['char']]}_baseline_krea2_seed{r['seed']}_00001_.png", out / "img" / name)
        ref[it] = name
    qtext = {q["id"]: q["question_it"] for q in TP.rd(DATA / "te_traits_questions.csv")}
    S = [{"block": s["block"], "pos": int(s["pos"]), "item": s["item"], "showing": int(s["showing"]),
          "question": s["question"], "kind": s["kind"]} for s in sched]
    page = (TP.PAGE.replace("te_traits_A_v1", "te_tap_windows_v1").replace("te_traits_alessandro.csv", "te_tap_windows_alessandro.csv")
            .replace("C75 · tratti", "C87 · tratti").replace("__INTRO__", ""))
    html = page.replace("__SCHED__", json.dumps(S, separators=(",", ":"))).replace("__QUESTIONS__", json.dumps(qtext, ensure_ascii=False)).replace("__REF__", json.dumps(ref))
    (out / "index.html").write_text(html, encoding="utf-8")
    print("page", out / "index.html", "steps (before skin follow-ups)", len(S), "images", len(key))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", action="store_true"); ap.add_argument("--page", action="store_true"); ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root:
        IMG_ROOT = Path(a.img_root)
    if a.key: make_key()
    if a.page: make_page()
