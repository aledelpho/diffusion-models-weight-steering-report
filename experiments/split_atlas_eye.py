"""C59 eye pass: which artefact, how strong, in each block x part x sign (docs/split_atlas_eye_protocol.md).
Written 2026-10-07, after the split atlas (exploratory). Seed 2718281 only (the one where the whole block exists).

  python split_atlas_eye.py --build [--img-root PATH]   # Text2Img/benchmark_split_atlas/eye_test/ + data/split_atlas_eye_key.csv
  python split_atlas_eye.py --tally                      # after data/split_atlas_eye_alessandro.csv is committed

One sheet = the same edit on the three prompts side by side, at full resolution (3072 x 1280), anonymous file
name. The page flips to the three baselines while Space is held. 168 sheets + 20 repeats, shuffled (rng 59).
"""
import argparse, csv, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
DATA = HERE.parent / "data"
KEY = DATA / "split_atlas_eye_key.csv"
LABELS = DATA / "split_atlas_eye_alessandro.csv"
SEED = "2718281"
CONDS = [("attn", "pos"), ("attn", "neg"), ("mlp", "pos"), ("mlp", "neg"), ("whole", "pos"), ("whole", "neg")]
CATS = [("chiazze", "Rumore a chiazze", "macchie multicolori di qualche decina di pixel sopra un'immagine ancora leggibile"),
        ("grana", "Grana fine", "puntinato leggero e diffuso, come grana di pellicola"),
        ("collasso", "Collasso in rumore", "l'immagine non si legge pi&ugrave;: resta solo rumore"),
        ("retino", "Retino / trama regolare", "una trama ordinata di puntini o righe, come un retino di stampa"),
        ("poster", "Posterizzazione / blocchi di colore", "tinte piatte e sature, contorni a colori, fino al mosaico"),
        ("sostituito", "Contenuto sostituito / astratto", "il soggetto diventa un'altra cosa o una forma astratta"),
        ("morbido", "Ammorbidimento / sfocatura", "si perdono linea e dettaglio, lo sfondo si sfoca"),
        ("tratteggio", "Tratteggio accentuato", "linee incise, texture pi&ugrave; dura e marcata")]
EXAMPLES = ["chiazze", "grana", "collasso", "retino", "poster", "sostituito"]


def build():
    import numpy as np
    from PIL import Image
    import split_atlas as s
    out = c47.IMG_ROOT / s.FOLDER / "eye_test"; out.mkdir(exist_ok=True)
    rng = np.random.default_rng(59)
    sheets = [{"block": b, "part": p, "sign": g} for b in range(28) for p, g in CONDS]
    ids = rng.permutation(np.arange(1000, 9999))[: len(sheets)]
    for sh, i in zip(sheets, ids):
        sh["id"] = f"s{i}"
        sh["paths"] = [s.f_atlas(pid, f"blk{sh['block']:02d}_{sh['sign']}_d0.350") if sh["part"] == "whole"
                       else s.f_split(pid, SEED, f"blk{sh['block']:02d}_{sh['part']}_{sh['sign']}_d0.350") for pid in s.PROMPTS]
    show = [sh["id"] for sh in sheets]; rng.shuffle(show)
    rep = list(rng.choice(show, 20, replace=False))
    for x in rep:
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), x)
    def strip(paths, dst):
        if dst.exists():
            return
        S = Image.new("RGB", (3 * 1024 + 2 * 8, 1280), (30, 30, 30))
        for k, p in enumerate(paths):
            S.paste(Image.open(p).convert("RGB"), (k * 1032, 0))
        S.save(dst, "JPEG", quality=92, subsampling=0)
    strip([s.f_base(pid, SEED) for pid in s.PROMPTS], out / "base.jpg")
    for sh in sheets:
        strip(sh["paths"], out / f"{sh['id']}.jpg")
    with open(KEY, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["sheet", "block", "part", "sign", "repeated"])
        for sh in sheets:
            w.writerow([sh["id"], sh["block"], sh["part"], sh["sign"], int(sh["id"] in rep)])
    slots = [f"{x}#{k}" for k, x in enumerate(show)]
    cats = [{"k": k, "n": n, "d": d, "ex": k in EXAMPLES} for k, n, d in CATS]
    (out / "eye_test.html").write_text(PAGE.replace("__SLOTS__", json.dumps(slots)).replace("__CATS__", json.dumps(cats)), encoding="utf-8")
    print(len(sheets), "sheets,", len(slots), "showings ->", out / "eye_test.html")


def tally():
    import pandas as pd
    k = pd.read_csv(KEY); a = pd.read_csv(LABELS)
    a["sheet"] = a.slot.str.split("#").str[0]
    first = a.drop_duplicates("sheet", keep="first"); second = a[a.duplicated("sheet", keep="first")]
    cols = [c for c, _, _ in CATS]
    if len(second):
        m = first.set_index("sheet").loc[second.sheet]
        same_any = ((m[cols].fillna(0) > 0).values == (second.set_index("sheet")[cols].fillna(0) > 0).values)
        print("self-agreement presence per category:", dict(zip(cols, same_any.mean(0).round(2))))
        print("self-agreement exact intensity:", dict(zip(cols, (m[cols].fillna(0).values == second.set_index("sheet")[cols].fillna(0).values).mean(0).round(2))))
    t = first.merge(k, on="sheet")
    t.to_csv(DATA / "split_atlas_eye_tally_alessandro.csv", index=False)
    print(t.pivot_table(index="block", columns=["part", "sign"], values=cols, aggfunc="max").fillna(0).astype(int).to_string())


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Atlante diviso: artefatti</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#1d1d1f;--panel:#2a2a2d;--fg:#eee;--mut:#aaa;--on:#3b6e4f;--onb:#6c6}
body{margin:0;background:var(--bg);color:var(--fg);font:15px system-ui,sans-serif}
#wrap{display:flex;gap:12px;padding:8px;box-sizing:border-box;height:100vh}
#view{flex:1;overflow:auto;background:#000;border-radius:8px;position:relative;cursor:zoom-in}
#view.zoom{cursor:zoom-out}#view img{width:100%;display:block}#view.zoom img{width:auto;max-width:none}
#tag{position:sticky;top:0;left:0;background:#000a;padding:4px 10px;font-weight:600;display:inline-block;z-index:2}
#side{width:390px;overflow:auto;background:var(--panel);border-radius:8px;padding:10px;box-sizing:border-box}
.c{border-top:1px solid #444;padding:5px 0;overflow:hidden}.c small{color:var(--mut);display:block;clear:right}.bt{float:right}.bt button{padding:4px 8px;margin:1px}
button{font:14px system-ui;padding:5px 10px;margin:3px 2px;border-radius:7px;border:1px solid #666;background:#333;color:#eee;cursor:pointer}
button.on{background:var(--on);border-color:var(--onb)}button.big{padding:8px 14px}
textarea{width:100%;box-sizing:border-box;background:#222;color:#eee;border:1px solid #555;border-radius:6px;font:14px system-ui}
#n{color:var(--mut);margin-bottom:6px}a{color:#8cf}
#intro{position:fixed;inset:0;background:var(--bg);overflow:auto;padding:20px;z-index:9}
#intro img{max-width:100%;border-radius:6px}.ex{margin:14px 0 22px}
</style></head><body>
<div id="intro"><h2>Atlante diviso — quali artefatti, quanto forti</h2>
<p>Ogni scheda mostra la stessa modifica sui tre prompt (fabbro, primo piano, rally), seme 2718281, a piena risoluzione.
Tieni premuto <b>Spazio</b> (o il tasto &laquo;Baseline&raquo;) per vedere i tre originali. Clic sull'immagine: zoom al 100%.</p>
<p>Per ogni categoria presente scegli <b>lieve, medio o forte</b>; se non c'&egrave; nessun artefatto premi &laquo;Nessun artefatto&raquo;.
Spunta &laquo;non in tutti e tre&raquo; se l'artefatto compare solo in uno o due prompt. Il campo libero &egrave; per tutto il resto
(altri attributi, dubbi, dove sta l'artefatto). Le risposte si salvano nel browser; alla fine &laquo;Scarica le risposte&raquo;.</p>
<p>Esempi (da altri semi o da altri test, non dalle schede del test): baseline intera, modifica intera, poi gli stessi ritagli al 100%.</p>
<div id="exs"></div><button class="big" id="go">Inizia</button></div>
<div id="wrap"><div id="view"><span id="tag"></span><img id="im"></div>
<div id="side"><div id="n"></div>
<button class="big" id="flip">Baseline (Spazio)</button>
<div class="c"><button class="big" id="none">Nessun artefatto</button></div>
<div id="cats"></div>
<div class="c"><label><input type="checkbox" id="partial"> non in tutti e tre i prompt</label></div>
<div class="c"><b>Altri attributi / note</b><textarea id="note" rows="3"></textarea></div>
<div class="c"><button id="prev">&larr; indietro</button><button id="next">avanti &rarr;</button>
<button id="exp">Scarica le risposte</button> <a href="#" id="help">esempi</a></div></div></div>
<script>
const S=__SLOTS__,C=__CATS__,K="split_atlas_eye_v1",LV=["","lieve","medio","forte"];
let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
const $=q=>document.querySelector(q);let i=0;try{i=Math.min(+localStorage.getItem(K+"_i")||0,S.length-1)}catch(e){}
$("#exs").innerHTML=C.map(c=>`<div class="ex"><b>${c.n}</b> — <span>${c.d}</span>`+(c.ex?`<br><img src="examples/${c.k==="poster"?"posterizzazione":c.k}.jpg">`:`<br><small>(nessun esempio affidabile: solo descrizione)</small>`)+`</div>`).join("");
$("#cats").innerHTML=C.map(c=>`<div class="c"><span class="bt">`+[1,2,3].map(v=>`<button data-k="${c.k}" data-v="${v}">${LV[v]}</button>`).join("")+`</span><b>${c.n}</b><small>${c.d}</small></div>`).join("");
function save(){try{localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_i",i)}catch(e){}}
function done(a){return a&&(a.none||C.some(c=>a[c.k]))}
function show(){const s=S[i],a=A[s]||{};$("#im").src=s.split("#")[0]+".jpg";$("#tag").textContent="modifica";
 $("#n").textContent=`scheda ${i+1} di ${S.length} · completate ${S.filter(x=>done(A[x])).length}`;
 $("#none").classList.toggle("on",!!a.none);
 document.querySelectorAll("button[data-k]").forEach(b=>b.classList.toggle("on",+(a[b.dataset.k]||0)===+b.dataset.v));
 $("#partial").checked=!!a.partial;$("#note").value=a.note||"";save()}
function cur(){const s=S[i];return A[s]=A[s]||{}}
document.querySelectorAll("button[data-k]").forEach(b=>b.onclick=()=>{const a=cur(),k=b.dataset.k,v=+b.dataset.v;a[k]=(a[k]===v?0:v);if(a[k])a.none=false;show()});
$("#none").onclick=()=>{const a=cur();a.none=!a.none;if(a.none)C.forEach(c=>a[c.k]=0);show()};
$("#partial").onchange=e=>{cur().partial=e.target.checked;save()};$("#note").oninput=e=>{cur().note=e.target.value;save()};
$("#prev").onclick=()=>{if(i>0){i--;show()}};$("#next").onclick=()=>{if(i<S.length-1){i++;show();$("#view").scrollTo(0,0)}};
const base=on=>{$("#im").src=on?"base.jpg":S[i].split("#")[0]+".jpg";$("#tag").textContent=on?"BASELINE":"modifica"};
$("#flip").onmousedown=()=>base(1);$("#flip").onmouseup=$("#flip").onmouseleave=()=>base(0);
addEventListener("keydown",e=>{if(e.code==="Space"&&e.target.tagName!=="TEXTAREA"){e.preventDefault();if(!e.repeat)base(1)}});
addEventListener("keyup",e=>{if(e.code==="Space"&&e.target.tagName!=="TEXTAREA")base(0)});
$("#view").onclick=()=>$("#view").classList.toggle("zoom");
$("#go").onclick=()=>$("#intro").style.display="none";$("#help").onclick=e=>{e.preventDefault();$("#intro").style.display="block"};
const q=v=>'"'+String(v||"").replace(/"/g,'""').replace(/\n/g," ")+'"';
$("#exp").onclick=()=>{let t="slot,none,"+C.map(c=>c.k).join(",")+",partial,note\n";
 S.forEach(s=>{const a=A[s]||{};t+=[s,a.none?1:0,...C.map(c=>a[c.k]||0),a.partial?1:0,q(a.note)].join(",")+"\n"});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="split_atlas_eye_alessandro.csv";l.click()};
show();
</script></body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true"); ap.add_argument("--tally", action="store_true"); ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.build: build()
    if a.tally: tally()
