"""C79 section C - blind labelling page (trait retention and skin), C75 protocol. Written 2026-10-18 after the renders,
before any label. Items: 72 C79 renders + 12 plain baselines (3 characters x 4 seeds) + 12 full edits (C65/C74,
L06 and L14 at the two seeds where they exist) = 96 pictures, + 4 repeats per character = 108 showings.
Questions: the C75 asked + common traits (data/te_traits_questions.csv, all in the positive), skin against the
same-seed baseline, same person. Condition, edit and seed are never shown.

  python te_tap_isolation_page.py --key                          # data/te_tap_key.csv, data/te_tap_schedule.csv
  python te_tap_isolation_page.py --page --img-root <Text2Img>   # Text2Img/_grid_viewer/te_tap/index.html
"""
import argparse, csv, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_traits_page as TP

DATA = HERE.parent / "data"
CHARS = TP.CHARS
SEEDS = ["2645751", "3316624", "3605551", "4123105"]
FULL_SEEDS = ["2645751", "3316624"]
RNG_SEED = 7979
N_REPEAT = 4
IMG_ROOT = Path(".")
TP.MIN_GAP = 12   # 32 pictures per character: a repeat comes back at least 12 pictures later


def pictures():
    out = []
    for c, ch in CHARS.items():
        for s in SEEDS:
            out.append({"char": c, "seed": s, "edit": "", "cond": "baseline",
                        "file": f"benchmark_portraits/phase_c/{ch}_baseline_krea2_seed{s}_00001_.png"})
        for L in ("06", "14"):
            for s in FULL_SEEDS:
                out.append({"char": c, "seed": s, "edit": f"L{L}_mlp_p1.00", "cond": "full",
                            "file": f"benchmark_te_characters/{ch}_L{L}_mlp_p1.00_krea2_seed{s}_00001_.png"})
            for s in SEEDS:
                for cond in ("taps_local", "taps_early_mid", "taps_late"):
                    out.append({"char": c, "seed": s, "edit": f"L{L}_mlp_p1.00", "cond": cond,
                                "file": f"benchmark_te_tap_isolation/{ch}_L{L}_mlp_p1.00_{cond}_krea2_seed{s}_00001_.png"})
    return out


def make_key():
    rng = random.Random(RNG_SEED)
    pics = pictures(); rng.shuffle(pics)
    for n, p in enumerate(pics, 1):
        p["item"] = f"T{n:03d}"
    reps = {}
    for c in CHARS:
        mine = [p for p in pics if p["char"] == c]
        first = rng.choice([p for p in mine if p["cond"] == "baseline"])
        reps[c] = [first["item"]] + [p["item"] for p in rng.sample([p for p in mine if p is not first], N_REPEAT - 1)]
    for p in pics:
        p["repeated"] = int(p["item"] in reps[p["char"]])
    with open(DATA / "te_tap_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item", "char", "seed", "edit", "cond", "repeated", "file"])
        w.writeheader(); w.writerows(sorted(pics, key=lambda p: p["item"]))
    per = TP.questions(); sched = []
    for c in CHARS:
        ids = [p["item"] for p in pics if p["char"] == c]
        qs = per[c][:]; rng.shuffle(qs)
        for q, kind in [(q, "trait") for q in qs] + [("skin", "skin"), ("person", "person")]:
            for k, (i, sh) in enumerate(TP.block_order(rng, ids, reps[c])):
                sched.append({"block": f"{c}:{q}", "char": c, "question": q, "kind": kind, "pos": k, "item": i, "showing": sh})
    with open(DATA / "te_tap_schedule.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sched[0])); w.writeheader(); w.writerows(sched)
    print("items", len(pics), "schedule rows", len(sched), "blocks", len({s['block'] for s in sched}))


def make_page():
    from PIL import Image
    key = {r["item"]: r for r in TP.rd(DATA / "te_tap_key.csv")}
    sched = TP.rd(DATA / "te_tap_schedule.csv")
    out = IMG_ROOT / "_grid_viewer" / "te_tap"; (out / "img").mkdir(parents=True, exist_ok=True)
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
    page = (TP.PAGE.replace("te_traits_A_v1", "te_tap_v1").replace("te_traits_alessandro.csv", "te_tap_alessandro.csv")
            .replace("C75 · tratti", "C79 · tratti").replace("__INTRO__", ""))
    html = page.replace("__SCHED__", json.dumps(S, separators=(",", ":"))).replace("__QUESTIONS__", json.dumps(qtext, ensure_ascii=False)).replace("__REF__", json.dumps(ref))
    (out / "index.html").write_text(html, encoding="utf-8")
    print("page", out / "index.html", "steps (before skin follow-ups)", len(S), "images", len(key))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", action="store_true"); ap.add_argument("--page", action="store_true"); ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: IMG_ROOT = Path(a.img_root)
    if a.key: make_key()
    if a.page: make_page()
