"""C54 — the archer's half-formed hood (docs/prereg_hood_watershed.md). Written 2026-10-06.

  python hood_watershed.py --page                     # data/hood_key.csv + Text2Img/benchmark_single_blocks_v3/hood/test.html
  python hood_watershed.py --tally --answers data/hood_labels_alessandro.csv --tag alessandro
"""
import argparse, base64, csv, glob, hashlib, io, json, os, re
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt")
OUT = os.path.join(ROOT, "benchmark_single_blocks_v3", "hood")
KEY = os.path.join(DATA, "hood_key.csv")
LABELS = ["completo", "a metà", "assente", "non riesco a dirlo"]


def condition(name):
    n = name.replace("P3_archerforest_", "").split("_krea2_")[0]
    m = re.match(r"blk(\d\d)_(neg|pos)_d(\d\.\d+)", n)
    if m:
        return f"blk{m[1]}", ("-" if m[2] == "neg" else "+"), m[3]
    m = re.match(r"b23_([mp])(\d\.\d+)", n)   # C47 naming: m = negative dose = more colour
    if m:
        return "blk23", ("-" if m[1] == "m" else "+"), m[2]
    return n, "", ""


def corpus():
    fs = sorted(glob.glob(os.path.join(ROOT, "benchmark_single_blocks_v3", "renders", "P3_archer*.png")) +
                glob.glob(os.path.join(ROOT, "benchmark_blk23_colorful", "P3_archer*.png")))
    seen, items = set(), []
    for f in fs:
        h = hashlib.md5(np.asarray(Image.open(f).convert("RGB")).tobytes()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        b = os.path.basename(f)
        seed = re.search(r"seed(\d+)", b)[1]
        blk, sign, dose = condition(b)
        items.append({"file": os.path.relpath(f, ROOT).replace(os.sep, "/"), "seed": seed, "cond": blk, "sign": sign, "dose": dose})
    return items


def jpg(im, q=86):
    b = io.BytesIO(); im.save(b, "JPEG", quality=q); return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def page():
    rng = np.random.default_rng(54)
    items = corpus()
    ids = rng.permutation(np.arange(100, 999))[: len(items)]
    for it, i in zip(items, ids):
        it["item"] = f"h{i}"
    order = [it["item"] for it in items]
    rng.shuffle(order)
    repeats = list(rng.choice(order, 12, replace=False))
    show = list(order)
    for r in repeats:                      # second showing at a random later place
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), r)
    with open(KEY, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["item", "file", "seed", "cond", "sign", "dose", "repeated"])
        w.writeheader()
        for it in items:
            w.writerow({**it, "repeated": int(it["item"] in repeats)})
    imgs = {}
    for it in items:
        im = Image.open(os.path.join(ROOT, it["file"])).convert("RGB")
        imgs[it["item"]] = [jpg(im.resize((512, 640), Image.LANCZOS)), jpg(im.crop((112, 0, 912, 800)).resize((640, 640), Image.LANCZOS))]
    os.makedirs(OUT, exist_ok=True)
    slots = [f"{s}#{k}" for k, s in enumerate(show)]
    html = PAGE.replace("__SLOTS__", json.dumps(slots)).replace("__IMG__", json.dumps(imgs)).replace("__LABELS__", json.dumps(LABELS))
    with open(os.path.join(OUT, "test.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print(len(items), "images,", len(slots), "showings ->", os.path.join(OUT, "test.html"))


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Cappuccio</title>
<style>body{margin:0;background:#202020;color:#eee;font:16px system-ui,sans-serif;text-align:center}
.row{display:flex;gap:10px;justify-content:center;align-items:flex-start;margin:8px}
.row img{max-height:68vh;max-width:48vw;border-radius:4px}
button{font:16px system-ui;padding:10px 20px;margin:4px;border-radius:8px;border:1px solid #666;background:#333;color:#eee;cursor:pointer}
button.on{background:#3b6e4f;border-color:#6c6}#n{color:#aaa;margin-top:6px}</style></head><body>
<div id="n"></div>
<div class="row"><img id="w"><img id="c"></div>
<div>Il cappuccio è&hellip;<br><span id="b"></span></div>
<div><button id="prev">&larr; indietro</button><button id="next">avanti &rarr;</button><button id="exp">Fine: scarica le risposte</button></div>
<script>
const S=__SLOTS__,IMG=__IMG__,L=__LABELS__,K="cappuccio_v1";let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;const $=s=>document.querySelector(s);
$("#b").innerHTML=L.map(l=>`<button data-v="${l}">${l}</button>`).join("");
function show(){const id=S[i].split("#")[0];$("#w").src=IMG[id][0];$("#c").src=IMG[id][1];
 $("#n").textContent=`${i+1} di ${S.length} · completate ${S.filter(s=>A[s]).length}`;
 document.querySelectorAll("button[data-v]").forEach(b=>b.classList.toggle("on",A[S[i]]===b.dataset.v))}
document.querySelectorAll("button[data-v]").forEach(b=>b.onclick=()=>{A[S[i]]=b.dataset.v;try{localStorage.setItem(K,JSON.stringify(A))}catch(e){};
 show();if(i<S.length-1)setTimeout(()=>{i++;show()},200)});
$("#prev").onclick=()=>{if(i>0){i--;show()}};$("#next").onclick=()=>{if(i<S.length-1){i++;show()}};
$("#exp").onclick=()=>{let t="slot,item,label\n";S.forEach(s=>{t+=`${s},${s.split("#")[0]},${A[s]||""}\n`});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const a=document.createElement("a");a.href=u;a.download="hood_labels.csv";a.click()};
show();
</script></body></html>"""


def tally(answers, tag):
    key = {r["item"]: r for r in csv.DictReader(open(KEY))}
    rows = list(csv.DictReader(open(answers, encoding="utf-8")))
    by = {}
    for r in rows:
        by.setdefault(r["item"], []).append(r["label"])
    rep = [v for it, v in by.items() if key[it]["repeated"] == "1" and len(v) == 2]
    agree = sum(v[0] == v[1] for v in rep)
    reliable = agree >= 10
    out = []
    base = {key[it]["seed"]: by[it][0] for it in key if key[it]["cond"] == "baseline"}
    for it, k in key.items():
        lab = by[it][0]
        b = base[k["seed"]]
        verdict = ""
        if k["cond"] != "baseline":
            if b == "a metà":
                verdict = "completes" if lab == "completo" else "removes" if lab == "assente" else "unchanged" if lab == "a metà" else "unclear"
            elif b == "completo":
                verdict = "breaks" if lab in ("a metà", "assente") else "unchanged" if lab == "completo" else "unclear"
        out.append({**{x: k[x] for x in ("item", "seed", "cond", "sign", "dose")}, "label": lab,
                    "second_label": by[it][1] if len(by[it]) > 1 else "", "vs_baseline": verdict})
    out.sort(key=lambda r: (r["seed"], r["cond"], r["sign"], r["dose"]))
    with open(os.path.join(DATA, f"hood_tally_{tag}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(f"self-agreement {agree}/{len(rep)} -> {'reliable' if reliable else 'UNRELIABLE: no table'}")
    print("baselines:", base)
    if reliable:
        from collections import Counter
        for s in sorted(base):
            print(s, Counter(r["vs_baseline"] for r in out if r["seed"] == s and r["cond"] != "baseline"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", action="store_true"); ap.add_argument("--tally", action="store_true")
    ap.add_argument("--answers"); ap.add_argument("--tag")
    a = ap.parse_args()
    if a.page: page()
    if a.tally: tally(a.answers, a.tag)
