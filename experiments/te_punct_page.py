"""C78 amendment 4 - blind labelling page for the complex prompts (P3 totem, P4 prison break). Written 2026-10-15,
after the renders and before any label. Questions: data/te_punct_questions.csv (12 primary per prompt, fixed in
amendment 3; secondary ones from amendment 4). Same page and keys as C75; version and seed never shown.

  python te_punct_page.py --key                         # data/te_punct_key.csv, data/te_punct_schedule.csv
  python te_punct_page.py --page --img-root <Text2Img>  # Text2Img/_grid_viewer/te_punct/index.html
"""
import argparse, csv, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_traits_page as TP

DATA = HERE.parent / "data"
RNG_SEED = 7878
N_REPEAT = 4
IMG_ROOT = Path(".")


def make_key():
    rng = random.Random(RNG_SEED)
    plan = TP.rd(DATA / "te_punct2_plan.csv")
    pics = [{"prompt": r["prompt_id"], "version": r["version"], "seed": r["seed"],
             "file": f"benchmark_te_punct/{r['expected_filename']}"} for r in plan]
    rng.shuffle(pics)
    for n, p in enumerate(pics, 1):
        p["item"] = f"C{n:03d}"
    reps = {pr: [p["item"] for p in rng.sample([p for p in pics if p["prompt"] == pr], N_REPEAT)]
            for pr in ("P3_totem", "P4_prison")}
    for p in pics:
        p["repeated"] = int(p["item"] in reps[p["prompt"]])
    with open(DATA / "te_punct_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item", "prompt", "seed", "version", "repeated", "file"])
        w.writeheader(); w.writerows(sorted(pics, key=lambda p: p["item"]))
    qs = TP.rd(DATA / "te_punct_questions.csv"); sched = []
    for pr in ("P3_totem", "P4_prison"):
        ids = [p["item"] for p in pics if p["prompt"] == pr]
        mine = [q["id"] for q in qs if q["prompt"] == pr]; rng.shuffle(mine)
        for q in mine:
            for k, (i, sh) in enumerate(TP.block_order(rng, ids, reps[pr])):
                sched.append({"block": f"{pr}:{q}", "char": pr, "question": q, "kind": "trait", "pos": k, "item": i, "showing": sh})
    with open(DATA / "te_punct_schedule.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sched[0])); w.writeheader(); w.writerows(sched)
    print("items", len(pics), "schedule rows", len(sched), "blocks", len({s['block'] for s in sched}))


def make_page():
    from PIL import Image
    key = TP.rd(DATA / "te_punct_key.csv"); sched = TP.rd(DATA / "te_punct_schedule.csv")
    out = IMG_ROOT / "_grid_viewer" / "te_punct"; (out / "img").mkdir(parents=True, exist_ok=True)
    for r in key:
        dst = out / "img" / f"{r['item']}.jpg"
        if not dst.exists():
            im = Image.open(IMG_ROOT / r["file"]).convert("RGB"); im.thumbnail((720, 1000), Image.LANCZOS); im.save(dst, "JPEG", quality=88)
    qtext = {q["id"]: q["question_it"] for q in TP.rd(DATA / "te_punct_questions.csv")}
    S = [{"block": s["block"], "pos": int(s["pos"]), "item": s["item"], "showing": int(s["showing"]),
          "question": s["question"], "kind": s["kind"]} for s in sched]
    page = (TP.PAGE.replace("te_traits_A_v1", "te_punct_v1").replace("te_traits_alessandro.csv", "te_punct_alessandro.csv")
            .replace("C75 · tratti", "C78 · scene").replace("di questo personaggio", "di questa scena").replace("__INTRO__", ""))
    html = page.replace("__SCHED__", json.dumps(S, separators=(",", ":"))).replace("__QUESTIONS__", json.dumps(qtext, ensure_ascii=False)).replace("__REF__", "{}")
    (out / "index.html").write_text(html, encoding="utf-8")
    print("page", out / "index.html", "steps", len(S), "images", len(key))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", action="store_true"); ap.add_argument("--page", action="store_true"); ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: IMG_ROOT = Path(a.img_root)
    if a.key: make_key()
    if a.page: make_page()
