"""Annotation page for the C45 eye pass (docs/prereg_prompt_writing.md, "The eye").

One arm per screen (left/right arrows): for each subject, rows W1 original, W2 reordered,
W3 tags, W4 synonyms, C1 content change; columns seed 3141592 baseline | arm | seed
1234567 baseline | arm. Two questions per arm (yes / partly / no) and a note. Marks are
kept in the browser and exported with "Esporta CSV" -> save as
data/prompt_writing_eye_alessandro.csv. No measured number appears on the page.

  python experiments/build_prompt_writing_eye_page.py
  -> benchmark_prompt_writing/occhio_C45.html (+ _thumbs/)
"""
import json, os
from PIL import Image
from analyze_prompt_writing import WRIT, CONTENT, SEEDS, PW, path, plan

ROWS = [("W1 originale", 0), ("W2 riordinato", 1), ("W3 tag", 2), ("W4 sinonimi", 3)]


def thumb(src):
    out = os.path.join(PW, "_thumbs", os.path.basename(src).replace(".png", ".jpg"))
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        Image.open(src).convert("RGB").resize((360, 450), Image.LANCZOS).save(out, quality=86)
    return os.path.relpath(out, PW).replace(os.sep, "/"), os.path.relpath(src, PW).replace(os.sep, "/")


def main():
    arms = [c for c in plan() if c != "baseline"]
    data = []
    for c in arms:
        subj = []
        for s in ("S1", "S2"):
            rows = []
            for label, k in ROWS + [("C1 contenuto cambiato", None)]:
                pid = WRIT[s][k] if k is not None else CONTENT[s]
                cells = []
                for cond, seed in [("baseline", SEEDS[0]), (c, SEEDS[0]), ("baseline", SEEDS[1]), (c, SEEDS[1])]:
                    t, f = thumb(path(pid, cond, seed))
                    cells.append({"t": t, "f": f})
                rows.append({"label": label, "pid": pid, "cells": cells})
            subj.append({"name": "S1 · elfa" if s == "S1" else "S2 · canoa", "rows": rows})
        data.append({"arm": c, "subj": subj})
    html = PAGE.replace("__DATA__", json.dumps(data))
    with open(os.path.join(PW, "occhio_C45.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print("written", os.path.join(PW, "occhio_C45.html"))


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Occhio C45</title>
<style>
:root{--bg:#f6f5f2;--fg:#1d1d1b;--mut:#6b6a66;--line:#d9d6cf;--card:#fff;--acc:#2f5d8a;--y:#2e7d4f;--p:#b07d1a;--n:#a63d3d}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe7;--mut:#9b9a95;--line:#34332f;--card:#1f1f1d;--acc:#7fb0de}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;z-index:2}
header h1{font-size:16px;margin:0 8px 0 0}
button,select{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}
main{padding:12px 16px 40px;max-width:1500px;margin:auto}
.subj{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:1100px){.subj{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);border-radius:8px}
th,td{padding:4px;text-align:center;font-weight:500;font-size:12px;color:var(--mut)}
td.l{text-align:left;white-space:nowrap;color:var(--fg)}
td img{width:100%;max-width:150px;display:block;margin:auto;border-radius:3px}
td.arm img{outline:2px solid var(--acc);outline-offset:-2px}
tr.c1 td{border-top:1px dashed var(--line)}
.q{margin:14px 0 6px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.q span{min-width:330px}
.q button.on[data-v=si]{background:var(--y);color:#fff}.q button.on[data-v=inparte]{background:var(--p);color:#fff}.q button.on[data-v=no]{background:var(--n);color:#fff}
textarea{width:100%;min-height:60px;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;font:inherit}
#ov{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;align-items:center;justify-content:center;z-index:5}
#ov img{max-width:96vw;max-height:94vh}
.hint{color:var(--mut);font-size:12px}
</style></head><body>
<header><h1>C45 · stessa modifica, scritture diverse</h1>
<button id="prev">←</button><select id="sel"></select><button id="next">→</button>
<span id="prog" class="hint"></span><button id="exp">Esporta CSV</button>
<span class="hint">clic su un'immagine = piena risoluzione · ← → cambia braccio</span></header>
<main id="m"></main><div id="ov"><img id="ovi"></div>
<script>
const D=__DATA__;const KEY="occhio_C45_v1";let M={};try{M=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(M))}catch(e){}prog()};
let i=0;const sel=document.getElementById("sel");
D.forEach((a,k)=>{const o=document.createElement("option");o.value=k;o.textContent=a.arm;sel.appendChild(o)});
function prog(){const n=D.filter(a=>M[a.arm]&&M[a.arm].q1&&M[a.arm].q2).length;document.getElementById("prog").textContent=n+" / "+D.length+" bracci segnati";
[...sel.options].forEach((o,k)=>{const m=M[D[k].arm];o.textContent=(m&&m.q1&&m.q2?"✓ ":"")+D[k].arm})}
function show(k){i=(k+D.length)%D.length;sel.value=i;const a=D[i];M[a.arm]=M[a.arm]||{};const m=M[a.arm];
let h=`<h2>${a.arm}</h2><div class="subj">`;
a.subj.forEach(s=>{h+=`<table><tr><th>${s.name}</th><th>base · 3141592</th><th>braccio</th><th>base · 1234567</th><th>braccio</th></tr>`;
s.rows.forEach(r=>{h+=`<tr class="${r.label.startsWith('C1')?'c1':''}"><td class="l">${r.label}</td>`+r.cells.map((c,j)=>`<td class="${j%2?'arm':''}"><img loading="lazy" src="${c.t}" data-f="${c.f}"></td>`).join("")+`</tr>`});h+=`</table>`});
h+=`</div>`;
const Q=[["q1","Fa la stessa cosa al variare della scrittura (W1–W4)?"],["q2","Fa la stessa cosa dopo il cambio di contenuto (C1)?"]];
Q.forEach(([q,t])=>{h+=`<div class="q"><span>${t}</span>`+["si","inparte","no"].map(v=>`<button data-q="${q}" data-v="${v}" class="${m[q]===v?'on':''}">${v==="inparte"?"in parte":v}</button>`).join("")+`</div>`});
h+=`<textarea id="nt" placeholder="appunti su questo braccio…">${m.note||""}</textarea>`;
document.getElementById("m").innerHTML=h;
document.querySelectorAll(".q button").forEach(b=>b.onclick=()=>{m[b.dataset.q]=b.dataset.v;save();show(i)});
document.getElementById("nt").oninput=e=>{m.note=e.target.value;save()};
document.querySelectorAll("td img").forEach(im=>im.onclick=()=>{document.getElementById("ovi").src=im.dataset.f;document.getElementById("ov").style.display="flex"});
prog();window.scrollTo(0,0)}
document.getElementById("ov").onclick=()=>document.getElementById("ov").style.display="none";
document.getElementById("prev").onclick=()=>show(i-1);document.getElementById("next").onclick=()=>show(i+1);sel.onchange=()=>show(+sel.value);
document.addEventListener("keydown",e=>{if(e.target.tagName==="TEXTAREA")return;if(e.key==="ArrowLeft")show(i-1);if(e.key==="ArrowRight")show(i+1);if(e.key==="Escape")document.getElementById("ov").style.display="none"});
document.getElementById("exp").onclick=()=>{const q=s=>'"'+String(s||"").replace(/"/g,'""')+'"';
let t="arm,same_across_writing,same_after_content_change,note\n"+D.map(a=>{const m=M[a.arm]||{};return [a.arm,m.q1||"",m.q2||"",q(m.note)].join(",")}).join("\n")+"\n";
const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="prompt_writing_eye_alessandro.csv";l.click()};
show(0);
</script></body></html>"""

if __name__ == "__main__":
    main()
