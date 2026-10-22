"""C108 - blind keys and labelling pages (docs/prereg_te_gender.md, section 3). Written 2026-10-22 after the 96 renders,
before any label.

  python te_gender_page.py --key  --img-root <Text2Img>   # data/te_gender_key_{single,panels,pairs}.csv
  python te_gender_page.py --page --img-root <Text2Img>   # Text2Img/_grid_viewer/te_gender_{single,panels,pairs}/index.html

Single (blocks A and B, 80 + 6 repeats): genre. Panels (block C, 16 + 2 repeats): four panels yes/no, then the genre
of each panel by position. Pairs (block C, 8): plain and L06 page side by side, sides random, "same / similar /
different". Pictures are copied under neutral names; nothing on a page says prompt, word, order, seed or condition.
Each page exports its own CSV.
"""
import argparse, csv, json, random
from pathlib import Path
HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
PLAN = DATA / "te_gender_plan.csv"
FOLDER = "benchmark_te_gender"
IMG_ROOT = Path(".")
GENRES = [["fumetto", "Fumetto occidentale"], ["anime", "Anime"], ["realist", "Realistico"],
          ["pittura", "Pittura"], ["cartoon", "Cartoon"], ["altro", "Altro"]]
POS = ["in alto a sinistra", "in alto a destra", "in basso a sinistra", "in basso a destra"]


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def write(p, rows):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def with_repeats(pics, rng, n_rep, gap):
    order = [dict(p, repeat="0") for p in pics]
    for p in rng.sample(pics, n_rep):
        first = next(i for i, q in enumerate(order) if q["file"] == p["file"])
        order.insert(rng.randint(min(first + gap + 1, len(order)), len(order)), dict(p, repeat="1"))
    return order


def make_keys():
    plan = rd(PLAN)
    def pic(r):
        return {k: r[k] for k in ("block", "item", "word", "cond", "seed")} | {"file": f"{FOLDER}/{r['expected_filename']}"}
    rng = random.Random(10808)
    single = [pic(r) for r in plan if r["block"] in ("A", "B")]; rng.shuffle(single)
    single = with_repeats(single, rng, 6, 20)
    write(DATA / "te_gender_key_single.csv", [{"id": f"S{i + 1:02d}", **p} for i, p in enumerate(single)])
    pages = [pic(r) for r in plan if r["block"] == "C"]; rng.shuffle(pages)
    pages = with_repeats(pages, rng, 2, 6)
    write(DATA / "te_gender_key_panels.csv", [{"id": f"Q{i + 1:02d}", **p} for i, p in enumerate(pages)])
    pairs = []
    for r in plan:
        if r["block"] == "C" and r["cond"] == "plain":
            l06 = next(x for x in plan if x["block"] == "C" and x["item"] == r["item"] and x["seed"] == r["seed"] and x["cond"] == "L06")
            a, b = f"{FOLDER}/{r['expected_filename']}", f"{FOLDER}/{l06['expected_filename']}"
            left_plain = rng.random() < 0.5
            pairs.append({"item": r["item"], "seed": r["seed"], "left": a if left_plain else b, "right": b if left_plain else a,
                          "repeat": "0", "file": a})
    rng.shuffle(pairs)
    write(DATA / "te_gender_key_pairs.csv", [{"id": f"C{i + 1:02d}", **p} for i, p in enumerate(pairs)])
    print("keys:", len(single), len(pages), len(pairs))


HEAD = """<!doctype html><html lang="it"><head><meta charset="utf-8"><title>__TITLE__</title><style>
body{background:#1a1a19;color:#e8e6e1;font-family:system-ui,sans-serif;margin:0;display:flex;flex-direction:column;align-items:center}
#top{margin:10px;font-size:14px;color:#a8a6a1}
img{max-height:66vh;max-width:95vw;border:2px solid #333;cursor:zoom-in}
img.full{max-height:none;max-width:none;cursor:zoom-out}
.pair img{max-width:47vw}
.q{margin:8px 0 2px;font-size:15px}
.row{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:3px}
button{background:#2d4f7c;color:#fff;border:0;border-radius:6px;padding:8px 12px;font-size:14px;cursor:pointer}
button:hover{background:#3987e5} button.on{background:#d95926}
#nav button{background:#444} #done{display:none;margin:16px} #done button{background:#199e70}
</style></head><body><div id="top"></div>"""

TAIL = """<div class="row" id="nav"><button onclick="go(-1)">&larr; indietro</button><button onclick="go(1)">avanti &rarr;</button></div>
<div id="done"><button onclick="exp()">Scarica __CSV__</button></div>
<script>
const IDS=__IDS__, Q=__QUESTIONS__, CSV='__CSV__';
let i=0; const L={}; IDS.forEach(x=>{L[x]={};Q.forEach(q=>L[x][q.k]='')});
const box=document.getElementById('qs');
Q.forEach(q=>{const d=document.createElement('div');d.className='q';d.textContent=q.t;box.appendChild(d);
 const r=document.createElement('div');r.className='row';r.id='r_'+q.k;
 q.o.forEach(o=>{const b=document.createElement('button');b.textContent=o[1];b.dataset.v=o[0];b.onclick=()=>set(q.k,o[0]);r.appendChild(b)});box.appendChild(r)});
function complete(x){return Q.every(q=>L[x][q.k])}
function set(k,v){L[IDS[i]][k]=v;show();if(complete(IDS[i])&&i<IDS.length-1)setTimeout(()=>go(1),300)}
function go(d){i=Math.max(0,Math.min(IDS.length-1,i+d));show();window.scrollTo(0,0)}
function show(){const id=IDS[i];showImg(id);const n=IDS.filter(complete).length;
 document.getElementById('top').textContent='Elemento '+(i+1)+' di '+IDS.length+' · completi '+n;
 Q.forEach(q=>document.querySelectorAll('#r_'+q.k+' button').forEach(b=>b.classList.toggle('on',b.dataset.v===L[id][q.k])));
 document.getElementById('done').style.display=n===IDS.length?'block':'none'}
function exp(){let s='id,'+Q.map(q=>q.k).join(',')+'\\n';IDS.forEach(x=>s+=x+','+Q.map(q=>L[x][q.k]).join(',')+'\\n');
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([s],{type:'text/csv'}));a.download=CSV;a.click()}
document.addEventListener('keydown',ev=>{if(ev.key==='ArrowLeft'||ev.key==='Backspace'){ev.preventDefault();go(-1)}else if(ev.key==='ArrowRight')go(1)});
show();
</script></body></html>"""


def build(name, title, csvname, body, show_js, ids, questions, images):
    from PIL import Image
    out = IMG_ROOT / "_grid_viewer" / name
    (out / "img").mkdir(parents=True, exist_ok=True)
    for dst, src in images:
        Image.open(IMG_ROOT / src).convert("RGB").resize((768, 960), Image.LANCZOS).save(out / "img" / dst, quality=90)
    html = (HEAD.replace("__TITLE__", title) + body + '<div id="qs"></div>' + "<script>" + show_js + "</script>" + TAIL)
    html = html.replace("__IDS__", json.dumps(ids)).replace("__QUESTIONS__", json.dumps(questions)).replace("__CSV__", csvname)
    (out / "index.html").write_text(html, encoding="utf-8")
    print("page:", out / "index.html", len(ids))


def make_pages():
    ks = rd(DATA / "te_gender_key_single.csv")
    build("te_gender_single", "C108 - immagini", "te_gender_labels_single.csv",
          '<img id="im" onclick="this.classList.toggle(\'full\')">',
          "function showImg(id){document.getElementById('im').src='img/'+id+'.jpg'}",
          [r["id"] for r in ks], [{"k": "genre", "t": "Genere", "o": GENRES}],
          [(f"{r['id']}.jpg", r["file"]) for r in ks])
    kp = rd(DATA / "te_gender_key_panels.csv")
    qs = [{"k": "four", "t": "L'immagine ha quattro pannelli separati?", "o": [["si", "Sì"], ["no", "No"]]}]
    qs += [{"k": f"g{j + 1}", "t": f"Genere del pannello {POS[j]}", "o": GENRES} for j in range(4)]
    build("te_gender_panels", "C108 - pagine", "te_gender_labels_panels.csv",
          '<img id="im" onclick="this.classList.toggle(\'full\')">',
          "function showImg(id){document.getElementById('im').src='img/'+id+'.jpg'}",
          [r["id"] for r in kp], qs, [(f"{r['id']}.jpg", r["file"]) for r in kp])
    kq = rd(DATA / "te_gender_key_pairs.csv")
    imgs = []
    for r in kq:
        imgs += [(f"{r['id']}_L.jpg", r["left"]), (f"{r['id']}_R.jpg", r["right"])]
    build("te_gender_pairs", "C108 - coppie", "te_gender_labels_pairs.csv",
          '<div class="row pair"><img id="a" onclick="this.classList.toggle(\'full\')"><img id="b" onclick="this.classList.toggle(\'full\')"></div>',
          "function showImg(id){document.getElementById('a').src='img/'+id+'_L.jpg';document.getElementById('b').src='img/'+id+'_R.jpg'}",
          [r["id"] for r in kq],
          [{"k": "answer", "t": "Nei quattro pannelli il cambiamento è dello stesso tipo?",
            "o": [["stesso", "Stesso"], ["simile", "Qualcosa di simile"], ["diversi", "Diversi"]]}], imgs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", action="store_true"); ap.add_argument("--page", action="store_true")
    ap.add_argument("--img-root", default=".")
    a = ap.parse_args()
    IMG_ROOT = Path(a.img_root)
    if a.key: make_keys()
    if a.page: make_pages()
