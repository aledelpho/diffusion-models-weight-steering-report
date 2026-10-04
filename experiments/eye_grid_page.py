"""Shared builder for eye-pass pages (C45, C47): grids of images with full-screen review.

Full-screen overlay keys: left/right = previous/next column, up/down = previous/next row,
hold SPACE = show the cell's baseline (cell key 'b', default column 0) in place, release = back (flicker compare),
PageUp/PageDown = previous/next unit, Esc = close. With the overlay closed, left/right change
unit. Answers: buttons under each group; in the overlay, keys 1-4 answer question 1 and
Q/W/E/R question 2 for the group being viewed. Marks live in localStorage and are exported
as CSV. No measured number is shown, except where a unit's data says so explicitly.
"""
import json, os
from PIL import Image


def thumb(src, root):
    out = os.path.join(root, "_thumbs", os.path.basename(src).rsplit(".", 1)[0] + ".jpg")
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        Image.open(src).convert("RGB").resize((360, 450), Image.LANCZOS).save(out, quality=86)
    rel = lambda p: os.path.relpath(p, root).replace(os.sep, "/")
    return rel(out), rel(src)


def build(out_html, title, units, questions, options, key, export_name, migrate=None):
    """units: [{id, title, groups:[{id, name, cols:[str], rows:[{label, cells:[{t,f,hl}]}]}]}]
    questions: [(qid, text)] or [(qid, text, options)] (two), options: default [(value, label)]"""
    html = (PAGE.replace("__DATA__", json.dumps(units)).replace("__Q__", json.dumps(questions))
            .replace("__OPT__", json.dumps(options)).replace("__KEY__", key).replace("__TITLE__", title)
            .replace("__EXPORT__", export_name).replace("__MIGRATE__", json.dumps(migrate)))
    with open(out_html, "w", encoding="utf-8") as fh:
        fh.write(html)


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
:root{--bg:#f6f5f2;--fg:#1d1d1b;--mut:#6b6a66;--line:#d9d6cf;--card:#fff;--acc:#2f5d8a;--y:#2e7d4f;--p:#b07d1a;--n:#a63d3d;--w:#6d6a8a}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe7;--mut:#9b9a95;--line:#34332f;--card:#1f1f1d;--acc:#7fb0de}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;z-index:2}
header h1{font-size:16px;margin:0 8px 0 0}
button,select{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}
main{padding:12px 16px 40px;max-width:1600px;margin:auto}
.groups{display:grid;grid-template-columns:repeat(auto-fit,minmax(560px,1fr));gap:16px}
.g{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px}
table{border-collapse:collapse;width:100%}
th,td{padding:3px;text-align:center;font-weight:500;font-size:12px;color:var(--mut)}
td.l{text-align:left;white-space:nowrap;color:var(--fg);font-size:12px}
td img{width:100%;max-width:150px;display:block;margin:auto;border-radius:3px;cursor:zoom-in}
td.hl img{outline:3px solid var(--acc);outline-offset:-3px}
.q{margin:8px 0 4px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.q span{flex:1 1 280px}
.q button.on{color:#fff}.q button.on[data-v=si]{background:var(--y)}.q button.on[data-v=inparte]{background:var(--p)}.q button.on[data-v=no]{background:var(--n)}.q button.on[data-v=debole]{background:var(--w)}
.q button.on[data-v=testo]{background:var(--n)}.q button.on[data-v=blk23]{background:var(--y)}.q button.on[data-v=pari]{background:var(--p)}
textarea{width:100%;min-height:44px;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;font:inherit;box-sizing:border-box}
#ov{position:fixed;inset:0;background:#0b0b0b;display:none;flex-direction:column;z-index:5;color:#eee}
#ov .im{flex:1;display:flex;align-items:center;justify-content:center;min-height:0}
#ov img{max-width:98vw;max-height:100%;object-fit:contain}
#ov .bar{padding:6px 12px;font-size:13px;display:flex;gap:16px;flex-wrap:wrap;background:#151515}
#ov .bar b{color:#fff}#ov .ans{color:#9fd3a8}
.hint{color:var(--mut);font-size:12px}
</style></head><body>
<header><h1>__TITLE__</h1>
<button id="prev">←</button><select id="sel"></select><button id="next">→</button>
<span id="prog" class="hint"></span><button id="exp">Esporta CSV</button>
<span class="hint">clic = schermo intero · lì: ← → colonne, ↑ ↓ righe, SPAZIO tenuto = base, PagSu/PagGiù = unità, 1–4 e Q–R = risposte, Esc chiude</span></header>
<main id="m"></main>
<div id="ov"><div class="bar"><b id="ovt"></b><span id="ovs"></span><span class="ans" id="ova"></span></div><div class="im"><img id="ovi"></div></div>
<script>
const D=__DATA__,Q=__Q__,O0=__OPT__,OP=k=>Q[k][2]||O0,KEY="__KEY__",MIG=__MIGRATE__;
let M={};try{M=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
if(MIG){try{const old=JSON.parse(localStorage.getItem(MIG)||"{}");for(const [u,v] of Object.entries(old)){M[u]=M[u]||{};
 for(const g of (D.find(x=>x.id===u)||{groups:[]}).groups){M[u][g.id]=M[u][g.id]||{};for(const [q] of Q){if(v[q]&&!M[u][g.id][q])M[u][g.id][q]=v[q]}
 if(v.note&&!M[u][g.id].note)M[u][g.id].note=v.note}}}catch(e){}}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(M))}catch(e){}prog()};
const mk=(u,g)=>{M[u]=M[u]||{};M[u][g]=M[u][g]||{};return M[u][g]};
let i=0;const sel=document.getElementById("sel");
D.forEach((a,k)=>{const o=document.createElement("option");o.value=k;sel.appendChild(o)});
const done=u=>u.groups.every(g=>{const m=(M[u.id]||{})[g.id]||{};return Q.every(([q])=>m[q])});
function prog(){document.getElementById("prog").textContent=D.filter(done).length+" / "+D.length+" completati";
 [...sel.options].forEach((o,k)=>o.textContent=(done(D[k])?"✓ ":"")+D[k].title)}
function show(k){i=(k+D.length)%D.length;sel.value=i;const u=D[i];
 let h=`<h2>${u.title}</h2><div class="groups">`;
 u.groups.forEach((g,gi)=>{const m=mk(u.id,g.id);h+=`<div class="g"><table><tr><th>${g.name}</th>`+g.cols.map(c=>`<th>${c}</th>`).join("")+`</tr>`;
  g.rows.forEach((r,ri)=>{h+=`<tr><td class="l">${r.label}</td>`+r.cells.map((c,ci)=>`<td class="${c.hl?'hl':''}"><img loading="lazy" src="${c.t}" data-g="${gi}" data-r="${ri}" data-c="${ci}"></td>`).join("")+`</tr>`});
  h+=`</table>`;Q.forEach(([q,t],k)=>{h+=`<div class="q"><span>${t}</span>`+OP(k).map(([v,l])=>`<button data-g="${g.id}" data-q="${q}" data-v="${v}" class="${m[q]===v?'on':''}">${l}</button>`).join("")+`</div>`});
  h+=`<textarea data-g="${g.id}" placeholder="appunti…">${m.note||""}</textarea></div>`});
 h+=`</div>`;document.getElementById("m").innerHTML=h;
 document.querySelectorAll(".q button").forEach(b=>b.onclick=()=>{mk(u.id,b.dataset.g)[b.dataset.q]=b.dataset.v;save();show(i)});
 document.querySelectorAll("textarea").forEach(t=>t.oninput=()=>{mk(u.id,t.dataset.g).note=t.value;save()});
 document.querySelectorAll("td img").forEach(im=>im.onclick=()=>openOv(+im.dataset.g,+im.dataset.r,+im.dataset.c));
 u.groups.forEach(g=>g.rows.forEach(r=>r.cells.forEach(c=>{const p=new Image();p.src=c.f})));
 prog();if(!ov)window.scrollTo(0,0)}
let ov=null,held=false;const OV=document.getElementById("ov");
function openOv(g,r,c){ov={g,r,c};OV.style.display="flex";paint()}
function paint(){ov.c=Math.min(ov.c,D[i].groups[ov.g].cols.length-1);const u=D[i],g=u.groups[ov.g],row=g.rows[ov.r],c=held?(row.cells[ov.c].b||0):ov.c,cell=row.cells[c];
 document.getElementById("ovi").src=cell.f;
 document.getElementById("ovt").textContent=[u.title,g.name,row.label,g.cols[c]].filter(x=>x).join(" · ")+(held?"  [BASE]":"");
 document.getElementById("ovs").textContent=`riga ${ov.r+1}/${g.rows.length} · colonna ${ov.c+1}/${g.cols.length}`;
 const m=mk(u.id,g.id);document.getElementById("ova").textContent=Q.map(([q],k)=>`D${k+1}: ${(OP(k).find(o=>o[0]===m[q])||["","—"])[1]}`).join("   ")}
function close(){ov=null;OV.style.display="none";show(i)}
document.addEventListener("keydown",e=>{if(e.target.tagName==="TEXTAREA")return;
 if(ov){const u=D[i],g=u.groups[ov.g];
  if(e.key==="Escape")return close();
  if(e.key==="ArrowRight"){ov.c=(ov.c+1)%g.cols.length;e.preventDefault()}
  else if(e.key==="ArrowLeft"){ov.c=(ov.c-1+g.cols.length)%g.cols.length;e.preventDefault()}
  else if(e.key==="ArrowDown"){ov.r++;if(ov.r>=g.rows.length){ov.r=0;ov.g=(ov.g+1)%u.groups.length}e.preventDefault()}
  else if(e.key==="ArrowUp"){ov.r--;if(ov.r<0){ov.g=(ov.g-1+u.groups.length)%u.groups.length;ov.r=u.groups[ov.g].rows.length-1}e.preventDefault()}
  else if(e.key==="PageDown"){show(i+1);ov.g=0;ov.r=Math.min(ov.r,D[i].groups[0].rows.length-1);e.preventDefault()}
  else if(e.key==="PageUp"){show(i-1);ov.g=0;ov.r=Math.min(ov.r,D[i].groups[0].rows.length-1);e.preventDefault()}
  else if(e.key===" "){held=true;e.preventDefault()}
  else{const a="1234".indexOf(e.key),b="qwer".indexOf(e.key.toLowerCase());
   if(a>=0&&OP(0)[a]){mk(u.id,g.id)[Q[0][0]]=OP(0)[a][0];save()}
   if(b>=0&&Q[1]&&OP(1)[b]){mk(u.id,g.id)[Q[1][0]]=OP(1)[b][0];save()}}
  paint();return}
 if(e.key==="ArrowLeft")show(i-1);if(e.key==="ArrowRight")show(i+1)});
document.addEventListener("keyup",e=>{if(e.key===" "&&ov){held=false;paint()}});
document.getElementById("prev").onclick=()=>show(i-1);document.getElementById("next").onclick=()=>show(i+1);sel.onchange=()=>show(+sel.value);
document.getElementById("exp").onclick=()=>{const q=s=>'"'+String(s||"").replace(/"/g,'""')+'"';
 let t="unit,group,"+Q.map(x=>x[0]).join(",")+",note\n";
 D.forEach(u=>u.groups.forEach(g=>{const m=(M[u.id]||{})[g.id]||{};t+=[u.id,g.id,...Q.map(([x])=>m[x]||""),q(m.note)].join(",")+"\n"}));
 const l=document.createElement("a");l.href=URL.createObjectURL(new Blob([t],{type:"text/csv"}));l.download="__EXPORT__";l.click()};
show(0);
</script></body></html>"""
