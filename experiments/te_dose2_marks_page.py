"""C113 amendment 2 - non-blind marking page: every edit x level x seed for both prompts, a verdict and a note per row,
an opinion per edit, prompts switchable. Writes Text2Img/calibra_C113.html; export -> data/te_dose2_marks.csv.
Written 2026-10-28 at Alessandro's request ("permettimi di selezionare le righe in un file html e scrivere opinioni")."""
import json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_depth_control as T


def main(root=None):
    if root:
        T.img_root = lambda: Path(root)
    import te_dose2 as S
    from eye_grid_page import thumb
    R = str(T.img_root())
    NAMES = {"S1_bluetree": "Albero blu", "S3_evilhelmet": "Elmo"}
    data = {"prompts": [{"id": p, "name": NAMES[p], "text": S.PROMPTS[p]} for p in S.SUBJECTS], "edits": [], "seeds": len(S.SEEDS)}
    def cells(p, c):
        out = []
        for s in S.SEEDS:
            t, f = thumb(str(S.path(p, c, s)), R); out.append([t, f])
        return out
    data["plain"] = {p: cells(p, "C0") for p in S.SUBJECTS}
    for n, xs in S.LADDERS.items():
        data["edits"].append({"id": n, "levels": [{"level": l + 1, "dose": x, "img": {p: cells(p, S.tag(n, l)) for p in S.SUBJECTS}} for l, x in enumerate(xs)]})
    html = PAGE.replace("__DATA__", json.dumps(data))
    out = os.path.join(R, "calibra_C113.html")
    open(out, "w", encoding="utf-8").write(html); print("wrote", out)


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calibrazione C113</title><style>
:root{--bg:#f5f4ef;--card:#fff;--fg:#1d1d1b;--mut:#6b6b66;--line:#ddd9cf;--acc:#2f6fb0;
--up:#2e7d4f;--ok:#2f6fb0;--down:#b07d1a;--br:#a63d3d}
@media (prefers-color-scheme:dark){:root{--bg:#1b1b1a;--card:#252523;--fg:#ecebe6;--mut:#a3a29c;--line:#3a3a37}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.4 system-ui,sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
h1{font-size:17px;margin:0 12px 0 0}button{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}
button.on{background:var(--acc);color:#fff;border-color:var(--acc)}.mut{color:var(--mut);font-size:13px}
main{padding:12px 16px 80px;max-width:1700px;margin:auto}
nav.edits{display:flex;gap:6px;flex-wrap:wrap}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;margin:14px 0}
section h2{margin:0 0 6px;font-size:18px}.ptext{font-size:13px;color:var(--mut);margin:0 0 8px}
.row{display:grid;grid-template-columns:110px repeat(8,minmax(0,1fr));gap:4px;align-items:center;margin:4px 0}
.row img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:4px;cursor:zoom-in;display:block}
.lab{font-size:13px}.lab b{display:block;font-size:14px}
.ctl{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:2px 0 10px 114px}
.ctl button[data-v=alzare].on{background:var(--up);border-color:var(--up)}.ctl button[data-v=giusta].on{background:var(--ok);border-color:var(--ok)}
.ctl button[data-v=abbassare].on{background:var(--down);border-color:var(--down)}.ctl button[data-v=rotta].on{background:var(--br);border-color:var(--br)}
.ctl input{flex:1 1 260px;font:inherit;padding:4px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
textarea{width:100%;min-height:60px;font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
.pblock{border-top:1px dashed var(--line);padding-top:8px;margin-top:8px}.pblock h3{margin:0 0 4px;font-size:15px}
#ov{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;flex-direction:column;z-index:20}
#ov .bar{color:#ddd;padding:8px 14px;display:flex;gap:14px;align-items:center;font-size:14px}#ov .bar b{color:#fff}
#ov .im{flex:1;display:flex;align-items:center;justify-content:center;min-height:0}#ov img{max-width:98vw;max-height:100%;object-fit:contain}
@media (max-width:800px){.row{grid-template-columns:70px repeat(4,minmax(0,1fr))}.ctl{margin-left:0}}
</style></head><body>
<header><h1>Calibrazione C113</h1>
<span class="mut">Prompt:</span><span id="pbtn"></span>
<span class="mut">Preset:</span><nav class="edits" id="ebtn"></nav>
<span id="prog" class="mut"></span><button id="exp">Esporta CSV</button>
<span class="mut">clic su un'immagine = schermo intero · lì ← → seed, ↑ ↓ livello, P cambia prompt, Esc chiude</span></header>
<main id="m"></main>
<div id="ov"><div class="bar"><button id="ovx">✕ chiudi</button><b id="ovt"></b></div><div class="im"><img id="ovi"></div></div>
<script>
const D=__DATA__,KEY="c113_marks_v1";
const VER=[["alzare","si può alzare"],["giusta","giusta"],["abbassare","troppo, abbassare"],["rotta","rotta"]];
let M={};try{M=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(M))}catch(e){}prog()};
let VIEW="both",EDIT=D.edits[0].id;
const ps=()=>VIEW==="both"?D.prompts:D.prompts.filter(p=>p.id===VIEW);
const k=(p,e,l)=>`${p}|${e}|${l}`;
function prog(){const tot=D.edits.length*4*D.prompts.length;const n=Object.entries(M).filter(([a,v])=>a.split("|").length===3&&v.v).length;
 document.getElementById("prog").textContent=`${n} / ${tot} righe giudicate`}
function btns(){
 document.getElementById("pbtn").innerHTML=[...D.prompts.map(p=>[p.id,p.name]),["both","Entrambi"]].map(([id,n])=>`<button data-p="${id}" class="${VIEW===id?'on':''}">${n}</button>`).join(" ");
 document.getElementById("ebtn").innerHTML=D.edits.map(e=>`<button data-e="${e.id}" class="${EDIT===e.id?'on':''}">${e.id}</button>`).join("");
 document.querySelectorAll("#pbtn button").forEach(b=>b.onclick=()=>{VIEW=b.dataset.p;render()});
 document.querySelectorAll("#ebtn button").forEach(b=>b.onclick=()=>{EDIT=b.dataset.e;render();scrollTo(0,0)});}
function imgs(list,p,l){return list.map((c,i)=>`<img loading="lazy" src="${c[0]}" data-p="${p}" data-l="${l}" data-s="${i}">`).join("")}
function render(){btns();const e=D.edits.find(x=>x.id===EDIT);let h=`<section><h2>${e.id}</h2>`;
 for(const p of ps()){h+=`<div class="pblock"><h3>${p.name}</h3><p class="ptext">${p.text}</p>`;
  h+=`<div class="row"><div class="lab"><b>originale</b></div>${imgs(D.plain[p.id],p.id,0)}</div>`;
  for(const L of e.levels){const m=M[k(p.id,e.id,L.level)]||{};
   h+=`<div class="row"><div class="lab"><b>livello ${L.level}</b>d = ${L.dose}</div>${imgs(L.img[p.id],p.id,L.level)}</div>`;
   h+=`<div class="ctl">`+VER.map(([v,t])=>`<button data-k="${k(p.id,e.id,L.level)}" data-v="${v}" class="${m.v===v?'on':''}">${t}</button>`).join("")+
      `<input data-k="${k(p.id,e.id,L.level)}" placeholder="appunto su questa riga…" value="${(m.n||"").replace(/"/g,'&quot;')}"></div>`}
  h+=`</div>`}
 const op=(M["op|"+e.id]||{}).n||"";
 h+=`<div class="pblock"><h3>Opinione sul preset ${e.id}</h3><textarea data-op="${e.id}" placeholder="che cosa fa, fin dove si può spingere, su quali soggetti…">${op.replace(/</g,"&lt;")}</textarea></div></section>`;
 document.getElementById("m").innerHTML=h;
 document.querySelectorAll(".ctl button").forEach(b=>b.onclick=()=>{const m=M[b.dataset.k]=M[b.dataset.k]||{};m.v=m.v===b.dataset.v?"":b.dataset.v;save();
  b.parentNode.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x.dataset.v===m.v))});
 document.querySelectorAll(".ctl input").forEach(t=>t.oninput=()=>{(M[t.dataset.k]=M[t.dataset.k]||{}).n=t.value;save()});
 document.querySelectorAll("textarea[data-op]").forEach(t=>t.oninput=()=>{M["op|"+t.dataset.op]={n:t.value};save()});
 document.querySelectorAll(".row img").forEach(im=>im.onclick=()=>openOv(im.dataset.p,+im.dataset.l,+im.dataset.s));prog()}
let ov=null;const OV=document.getElementById("ov");
const cell=(p,l,s)=>{const e=D.edits.find(x=>x.id===EDIT);return l===0?D.plain[p][s]:e.levels[l-1].img[p][s]};
function openOv(p,l,s){ov={p,l,s};OV.style.display="flex";paint()}
function paint(){const e=D.edits.find(x=>x.id===EDIT),pn=D.prompts.find(x=>x.id===ov.p).name;
 document.getElementById("ovi").src=cell(ov.p,ov.l,ov.s)[1];
 document.getElementById("ovt").textContent=`${pn} · ${e.id} · ${ov.l===0?"originale":"livello "+ov.l+" (d = "+e.levels[ov.l-1].dose+")"} · seed ${ov.s+1}/8`}
function close(){ov=null;OV.style.display="none"}
document.getElementById("ovx").onclick=close;OV.querySelector(".im").onclick=close;
document.addEventListener("keydown",ev=>{if(!ov)return;
 if(ev.key==="Escape")return close();
 if(ev.key==="ArrowRight")ov.s=(ov.s+1)%8;else if(ev.key==="ArrowLeft")ov.s=(ov.s+7)%8;
 else if(ev.key==="ArrowDown")ov.l=Math.min(4,ov.l+1);else if(ev.key==="ArrowUp")ov.l=Math.max(0,ov.l-1);
 else if(ev.key.toLowerCase()==="p"){const i=D.prompts.findIndex(x=>x.id===ov.p);ov.p=D.prompts[(i+1)%D.prompts.length].id}
 else return;ev.preventDefault();paint()});
document.getElementById("exp").onclick=()=>{const q=s=>'"'+String(s||"").replace(/"/g,'""')+'"';let t="type,prompt,edit,level,dose,verdict,note\n";
 for(const e of D.edits){for(const p of D.prompts)for(const L of e.levels){const m=M[k(p.id,e.id,L.level)]||{};t+=["row",p.id,e.id,L.level,L.dose,m.v||"",q(m.n)].join(",")+"\n"}
  t+=["opinion","",e.id,"","","",q((M["op|"+e.id]||{}).n)].join(",")+"\n"}
 const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([t],{type:"text/csv"}));a.download="te_dose2_marks.csv";a.click()};
render();
</script></body></html>"""

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
