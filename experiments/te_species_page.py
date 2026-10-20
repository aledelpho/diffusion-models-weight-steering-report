"""C107 - blind key and labelling page (docs/prereg_te_species.md, section 3). Written 2026-10-20 after the 40 renders,
before any label.

  python te_species_page.py --key  --img-root <Text2Img>   # data/te_species_key.csv
  python te_species_page.py --page --img-root <Text2Img>   # Text2Img/_grid_viewer/te_species/index.html + img/

One picture at a time, 40 pictures plus 6 repeats, random order (seed 10707). Pictures are copied under neutral
names (P01.jpg ...): nothing on the page says prompt, condition or seed. Two questions per picture: genre and
pointed ears. Keys: 1-6 genre, S / N ears, Backspace back. Export: te_species_labels.csv (id, genre, ears).
"""
import argparse, csv, json, random
from pathlib import Path
HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
PLAN = DATA / "te_species_plan.csv"
KEY = DATA / "te_species_key.csv"
FOLDER = "benchmark_te_species"
RNG_SEED = 10707
N_REPEAT = 6
MIN_GAP = 12
IMG_ROOT = Path(".")
GENRES = [("fumetto", "Fumetto occidentale"), ("anime", "Anime"), ("realist", "Realistico"),
          ("pittura", "Pittura"), ("cartoon", "Cartoon"), ("altro", "Altro")]


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def make_key():
    rng = random.Random(RNG_SEED)
    pics = [{"variant": r["variant"], "cond": r["cond"], "seed": r["seed"], "file": f"{FOLDER}/{r['expected_filename']}"}
            for r in rd(PLAN)]
    rng.shuffle(pics)
    order = [dict(p, repeat="0") for p in pics]
    reps = rng.sample(pics, N_REPEAT)
    for p in reps:
        first = next(i for i, q in enumerate(order) if q["file"] == p["file"])
        lo = first + MIN_GAP + 1
        pos = rng.randint(min(lo, len(order)), len(order))
        order.insert(pos, dict(p, repeat="1"))
    rows = [{"id": f"P{i + 1:02d}", **{k: p[k] for k in ("variant", "cond", "seed", "repeat", "file")}} for i, p in enumerate(order)]
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("key rows:", len(rows), "repeats:", sum(r["repeat"] == "1" for r in rows))


PAGE = """<!doctype html><html lang="it"><head><meta charset="utf-8"><title>C107 - occhio</title>
<style>
body{background:#1a1a19;color:#e8e6e1;font-family:system-ui,sans-serif;margin:0;display:flex;flex-direction:column;align-items:center}
#top{margin:10px;font-size:14px;color:#a8a6a1}
img{max-height:72vh;max-width:95vw;border:2px solid #333;cursor:zoom-in}
img.full{max-height:none;max-width:none;cursor:zoom-out}
.q{margin:10px 0 2px;font-size:15px}
.row{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:4px}
button{background:#2d4f7c;color:#fff;border:0;border-radius:6px;padding:9px 14px;font-size:15px;cursor:pointer}
button:hover{background:#3987e5}
button.on{background:#d95926}
#nav button{background:#444}
#done{display:none;margin:20px}
#done button{background:#199e70}
</style></head><body>
<div id="top"></div>
<img id="im" onclick="this.classList.toggle('full')">
<div class="q">Genere (tasti 1-6)</div><div class="row" id="g"></div>
<div class="q">Il personaggio ha le orecchie a punta? (S / N)</div><div class="row" id="e"></div>
<div class="row" id="nav"><button onclick="go(-1)">&larr; indietro</button><button onclick="go(1)">avanti &rarr;</button></div>
<div id="done"><button onclick="exp()">Scarica te_species_labels.csv</button></div>
<script>
const IDS=__IDS__, G=__GENRES__;
let i=0; const L={}; IDS.forEach(x=>L[x]={genre:"",ears:""});
const g=document.getElementById('g'), e=document.getElementById('e');
G.forEach((x,k)=>{const b=document.createElement('button');b.textContent=(k+1)+' · '+x[1];b.dataset.v=x[0];b.onclick=()=>set('genre',x[0]);g.appendChild(b)});
[['si','Sì (S)'],['no','No (N)']].forEach(x=>{const b=document.createElement('button');b.textContent=x[1];b.dataset.v=x[0];b.onclick=()=>set('ears',x[0]);e.appendChild(b)});
function set(k,v){L[IDS[i]][k]=v;show();if(L[IDS[i]].genre&&L[IDS[i]].ears&&i<IDS.length-1)setTimeout(()=>go(1),250)}
function go(d){i=Math.max(0,Math.min(IDS.length-1,i+d));show()}
function show(){const id=IDS[i];document.getElementById('im').src='img/'+id+'.jpg';
 const n=IDS.filter(x=>L[x].genre&&L[x].ears).length;
 document.getElementById('top').textContent='Immagine '+(i+1)+' di '+IDS.length+' · complete '+n;
 g.querySelectorAll('button').forEach(b=>b.classList.toggle('on',b.dataset.v===L[id].genre));
 e.querySelectorAll('button').forEach(b=>b.classList.toggle('on',b.dataset.v===L[id].ears));
 document.getElementById('done').style.display=n===IDS.length?'block':'none'}
function exp(){let s='id,genre,ears\\n';IDS.forEach(x=>s+=x+','+L[x].genre+','+L[x].ears+'\\n');
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([s],{type:'text/csv'}));a.download='te_species_labels.csv';a.click()}
document.addEventListener('keydown',ev=>{const k=ev.key.toLowerCase();
 if(k>='1'&&k<='6')set('genre',G[+k-1][0]);else if(k==='s')set('ears','si');else if(k==='n')set('ears','no');
 else if(k==='backspace'||k==='arrowleft'){ev.preventDefault();go(-1)}else if(k==='arrowright')go(1)});
show();
</script></body></html>"""


def make_page():
    from PIL import Image
    key = rd(KEY)
    out = IMG_ROOT / "_grid_viewer" / "te_species"
    (out / "img").mkdir(parents=True, exist_ok=True)
    for r in key:
        Image.open(IMG_ROOT / r["file"]).convert("RGB").resize((768, 960), Image.LANCZOS).save(out / "img" / f"{r['id']}.jpg", quality=90)
    html = PAGE.replace("__IDS__", json.dumps([r["id"] for r in key])).replace("__GENRES__", json.dumps(GENRES))
    (out / "index.html").write_text(html, encoding="utf-8")
    print("page:", out / "index.html", "pictures:", len(key))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", action="store_true"); ap.add_argument("--page", action="store_true")
    ap.add_argument("--img-root", default=".")
    a = ap.parse_args()
    IMG_ROOT = Path(a.img_root)
    if a.key: make_key()
    if a.page: make_page()
