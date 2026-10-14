"""C76 - blind key, schedule and labelling page for the colour-binding test (docs/prereg_te_bind.md).
Written 2026-10-14, before any C76 label. Reuses the C75 page and its protocol (te_traits_page.py).

  python te_bind_page.py --key  --img-root <Text2Img>   # data/te_bind_key.csv, data/te_bind_schedule.csv
  python te_bind_page.py --page --img-root <Text2Img>   # Text2Img/_grid_viewer/te_bind/index.html + img/
"""
import argparse, csv, json, random
from pathlib import Path
import te_traits_page as TP
DATA = TP.DATA
RNG_SEED = 7478
N_REPEAT = 4


def pictures():
    """The 222 C75 part A pictures, plus the B2 random pushes and the B0 plain portraits (no duplicate files)."""
    out = [{**p, "variant": "original" if p["dose"] == "0.00" else "real", "source": "A"} for p in TP.pictures()]
    seen = {p["file"] for p in out}
    for p in TP.pictures_B2():
        if p["variant"] in ("token", "permuted", "plain_B0") and p["file"] not in seen:
            out.append({**p, "source": "B2"}); seen.add(p["file"])
    return out


def make_key():
    rng = random.Random(RNG_SEED)
    pics = pictures(); rng.shuffle(pics)
    for n, p in enumerate(pics, 1):
        p["item"] = f"C{n:03d}"
    reps = {}
    for c in TP.CHARS:
        mine = [p for p in pics if p["char"] == c]
        first = rng.choice([p for p in mine if p["variant"] == "original"])
        reps[c] = [first["item"]] + [p["item"] for p in rng.sample([p for p in mine if p is not first], N_REPEAT - 1)]
    for p in pics:
        p["repeated"] = int(p["item"] in reps[p["char"]])
    with open(DATA / "te_bind_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item", "char", "seed", "edit", "dose", "variant", "source", "repeated", "file"])
        w.writeheader(); w.writerows(sorted(pics, key=lambda p: p["item"]))
    qs = TP.rd(DATA / "te_bind_questions.csv"); sched = []
    for c in TP.CHARS:
        ids = [p["item"] for p in pics if p["char"] == c]
        mine = [q["id"] for q in qs if q["char"] == c]; rng.shuffle(mine)
        for q in mine:
            for k, (i, sh) in enumerate(TP.block_order(rng, ids, reps[c])):
                sched.append({"block": f"{c}:{q}", "char": c, "question": q, "kind": "trait", "pos": k, "item": i, "showing": sh})
    with open(DATA / "te_bind_schedule.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sched[0])); w.writeheader(); w.writerows(sched)
    print("items", len(pics), "schedule rows", len(sched), "blocks", len({s['block'] for s in sched}))


def make_page():
    from PIL import Image
    key = {r["item"]: r for r in TP.rd(DATA / "te_bind_key.csv")}
    sched = TP.rd(DATA / "te_bind_schedule.csv")
    out = TP.IMG_ROOT / "_grid_viewer" / "te_bind"; (out / "img").mkdir(parents=True, exist_ok=True)
    for it, r in key.items():
        dst = out / "img" / f"{it}.jpg"
        if not dst.exists():
            im = Image.open(TP.IMG_ROOT / r["file"]).convert("RGB"); im.thumbnail((720, 900), Image.LANCZOS); im.save(dst, "JPEG", quality=88)
    qtext = {q["id"]: q["question_it"] for q in TP.rd(DATA / "te_bind_questions.csv")}
    S = [{"block": s["block"], "pos": int(s["pos"]), "item": s["item"], "showing": int(s["showing"]),
          "question": s["question"], "kind": "trait"} for s in sched]
    intro = TP.INTRO_B2.replace("""<p>In alcuni blocchi vedrai a sinistra un'immagine di <b>riferimento</b>: la domanda chiede un confronto con quella.</p>
""", """<p>Le domande riguardano i <b>colori</b>. Quando chiedono di pelle, capelli o occhi, conta solo il corpo del personaggio, non i vestiti, l'armatura o lo sfondo, e conta solo una <b>tinta che una persona normale non avrebbe</b>: un'abbronzatura, una guancia rossa o delle lentiggini non contano.</p>
<p>Se la domanda nomina un oggetto che nell'immagine non c'è (per esempio un cappuccio o un'armatura), giudica <b>quello che c'è al suo posto</b>. Usa "non si vede" solo se quella zona è tagliata fuori o coperta.</p>
""").replace("Se la domanda dice \"folti, intrecciati e raccolti indietro\" e i capelli sono intrecciati ma sciolti, la risposta è no.",
             "Se un colore c'è solo in parte o è molto vicino, decidi tu: non esiste una risposta perfetta.")
    assert "colori" in intro
    page = (TP.PAGE.replace("te_traits_A_v1", "te_bind_v2").replace("te_traits_alessandro.csv", "te_bind_rater.csv")
            .replace("C75 · tratti", "Ritratti · colori").replace("__INTRO__", intro))
    html = page.replace("__SCHED__", json.dumps(S, separators=(",", ":"))).replace("__QUESTIONS__", json.dumps(qtext, ensure_ascii=False)).replace("__REF__", "{}")
    (out / "index.html").write_text(html, encoding="utf-8")
    print("page", out / "index.html", "steps", len(S), "images", len(key))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", action="store_true"); ap.add_argument("--page", action="store_true"); ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: TP.IMG_ROOT = Path(a.img_root)
    if a.key: make_key()
    if a.page: make_page()
