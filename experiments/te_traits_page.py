"""C75 part A - blind key, schedule and labelling page for the trait test (docs/prereg_te_traits.md, amendment 1).
Written 2026-10-13, before any C75 label.

  python te_traits_page.py --key   --img-root <Text2Img>   # data/te_traits_key_A.csv, data/te_traits_schedule_A.csv
  python te_traits_page.py --page  --img-root <Text2Img>   # Text2Img/_grid_viewer/te_traits/index.html + img/

One question at a time over every picture of one character (question-major). Right arrow = yes, left = no,
down = cannot tell, Backspace = back. Item numbers, edits, doses and seeds are not shown.
"""
import argparse, csv, json, random
from pathlib import Path
HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
CHARS = {"D1": "D1_dwarf_paladin", "E2": "E2_elf_rogue", "O4": "O4_halforc_fighter"}
SEEDS = ["2645751", "3316624"]
LAYERS = [6, 14, 28]
DOSES = ["0.10", "0.25", "0.40", "0.50", "0.60", "0.70", "0.75", "0.80", "0.85", "0.90", "0.95", "1.00"]
RNG_SEED = 7475
N_REPEAT = 8
MIN_GAP = 30
IMG_ROOT = Path(".")


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def pictures():
    out = []
    for c, ch in CHARS.items():
        for s in SEEDS:
            out.append({"char": c, "seed": s, "edit": "", "dose": "0.00",
                        "file": f"benchmark_portraits/phase_c/{ch}_baseline_krea2_seed{s}_00001_.png"})
            for L in LAYERS:
                for d in DOSES:
                    folder = "benchmark_te_characters" if d == "1.00" else "benchmark_te_dose"
                    out.append({"char": c, "seed": s, "edit": f"L{L:02d}_mlp", "dose": d,
                                "file": f"{folder}/{ch}_L{L:02d}_mlp_p{d}_krea2_seed{s}_00001_.png"})
    return out


def questions():
    q = rd(DATA / "te_traits_questions.csv")
    per = {}
    for c in CHARS:
        trait = [x["id"] for x in q if x["char"] in (c, "ALL") and x["kind"] in ("asked", "common")]
        per[c] = trait
    return per


def block_order(rng, ids, reps):
    """ids shuffled, then each repeated id inserted again at least MIN_GAP positions after its first showing."""
    for _ in range(10000):
        seq = [(i, 1) for i in ids]; rng.shuffle(seq)
        pos = {i: k for k, (i, _) in enumerate(seq)}
        ok = True
        for i in reps:
            lo = pos[i] + MIN_GAP + 1
            if lo > len(seq):
                ok = False; break
            k = rng.randint(lo, len(seq)); seq.insert(k, (i, 2))
            pos = {j: n for n, (j, sh) in enumerate(seq) if sh == 1}
        if ok and all(next(n for n, x in enumerate(seq) if x == (i, 2)) - next(n for n, x in enumerate(seq) if x == (i, 1)) > MIN_GAP for i in reps):
            return seq
    raise RuntimeError("no schedule")


def make_key():
    rng = random.Random(RNG_SEED)
    pics = pictures(); rng.shuffle(pics)
    for n, p in enumerate(pics, 1):
        p["item"] = f"A{n:03d}"
    reps = {}
    for c in CHARS:
        mine = [p for p in pics if p["char"] == c]
        orig = [p for p in mine if p["dose"] == "0.00"]
        first = rng.choice(orig)
        rest = rng.sample([p for p in mine if p is not first], N_REPEAT - 1)
        reps[c] = [first["item"]] + [p["item"] for p in rest]
    for p in pics:
        p["repeated"] = int(p["item"] in reps[p["char"]])
    with open(DATA / "te_traits_key_A.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item", "char", "seed", "edit", "dose", "repeated", "file"])
        w.writeheader(); w.writerows(sorted(pics, key=lambda p: p["item"]))
    per = questions(); sched = []
    for c in CHARS:
        ids = [p["item"] for p in pics if p["char"] == c]
        qs = per[c][:]; rng.shuffle(qs)
        blocks = [(q, "trait") for q in qs] + [("skin", "skin"), ("person", "person")]
        for q, kind in blocks:
            for k, (i, sh) in enumerate(block_order(rng, ids, reps[c])):
                sched.append({"block": f"{c}:{q}", "char": c, "question": q, "kind": kind, "pos": k, "item": i, "showing": sh})
    with open(DATA / "te_traits_schedule_A.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sched[0])); w.writeheader(); w.writerows(sched)
    print("items", len(pics), "schedule rows", len(sched), "blocks", len({s['block'] for s in sched}))


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>C75 · tratti</title><style>
:root{--bg:#141414;--ink:#eee;--mut:#9a9a9a;--yes:#3fa46a;--no:#d0573f;--unk:#7a7a7a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.4 system-ui,sans-serif;height:100vh;display:flex;flex-direction:column}
#top{display:flex;gap:16px;align-items:center;padding:8px 16px;color:var(--mut);font-size:13px}#top button{margin-left:auto}
#q{font-size:clamp(20px,2.6vw,30px);font-weight:600;text-align:center;padding:6px 24px 10px}
#stage{flex:1;display:flex;justify-content:center;align-items:center;gap:18px;min-height:0;padding:0 16px}
#stage figure{margin:0;height:100%;display:flex;flex-direction:column;align-items:center}
#stage img{max-height:calc(100% - 22px);max-width:44vw;object-fit:contain;border-radius:4px}
#stage figcaption{color:var(--mut);font-size:13px;height:22px}
#keys{display:flex;justify-content:center;gap:12px;padding:10px 16px 14px}
button{background:#262626;color:var(--ink);border:1px solid #3a3a3a;border-radius:6px;padding:8px 16px;font-size:15px;cursor:pointer}
.k-no{border-color:var(--no)}.k-yes{border-color:var(--yes)}.k-unk{border-color:var(--unk)}
#card{position:fixed;inset:0;background:var(--bg);display:none;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:24px;gap:18px}
#card h1{font-size:clamp(22px,3vw,34px);max-width:900px;margin:0}#card p{color:var(--mut);max-width:760px;margin:0}
#flash{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);font-size:64px;font-weight:700;opacity:0;transition:opacity .25s;pointer-events:none}
</style></head><body>
<div id="top"><span id="prog"></span><span id="bprog"></span><button id="dl">Scarica CSV</button></div>
<div id="q"></div><div id="stage"></div>
<div id="keys"><button class="k-no" data-a="no">← no</button><button class="k-unk" data-a="non so">↓ non si vede</button><button class="k-yes" data-a="sì">sì →</button><button id="back">⌫ indietro</button></div>
<div id="card"><h1 id="ct"></h1><p id="cp"></p><button id="go">Inizia (spazio)</button></div><div id="flash"></div>
<script>
const S=__SCHED__, Q=__QUESTIONS__, REF=__REF__, KEY='te_traits_A_v1';
// steps: one per (schedule row, sub-question). Skin rows expand on the fly.
let A={};try{A=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){A={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(A))}catch(e){}}
function subs(r){ // questions to ask for this schedule row, given answers so far
  if(r.kind!=='skin')return[r.question];
  const k=r.block+'|'+r.pos, s=A[k+'|skin_same'], l=A[k+'|skin_lighter'];
  const out=['skin_same']; if(s==='no'){out.push('skin_lighter'); if(l==='no')out.push('skin_darker')} return out}
let i=0, sub=0, shownCard=null;
function firstOpen(){for(let n=0;n<S.length;n++){const r=S[n],L=subs(r);for(let m=0;m<L.length;m++){if(A[r.block+'|'+r.pos+'|'+L[m]]===undefined)return[n,m]}}return[S.length,0]}
[i,sub]=firstOpen();
function qid(r){return subs(r)[sub]}
function render(){
  if(i>=S.length){document.getElementById('q').textContent='Finito. Scarica il CSV.';document.getElementById('stage').innerHTML='';return}
  const r=S[i];
  if(shownCard!==r.block && r.pos===0 && sub===0 && A[r.block+'|0|'+subs(r)[0]]===undefined){showCard(r);return}
  const q=qid(r);document.getElementById('q').textContent=Q[q];
  const st=document.getElementById('stage');st.innerHTML='';
  if(r.kind!=='trait'){st.appendChild(fig('img/'+REF[r.item],'riferimento'))}
  st.appendChild(fig('img/'+r.item+'.jpg',r.kind!=='trait'?'immagine':''));
  const bl=S.filter(x=>x.block===r.block).length;
  document.getElementById('prog').textContent=`totale ${i+1} / ${S.length}`;
  document.getElementById('bprog').textContent=`domanda ${blockIndex(r.block)} / ${BLOCKS.length} · immagine ${r.pos+1} / ${bl}`;
  for(let n=1;n<=3;n++){if(S[i+n]){const im=new Image();im.src='img/'+S[i+n].item+'.jpg'}}}
const BLOCKS=[...new Set(S.map(x=>x.block))];function blockIndex(b){return BLOCKS.indexOf(b)+1}
function fig(src,cap){const f=document.createElement('figure');const im=document.createElement('img');im.src=src;f.appendChild(im);const c=document.createElement('figcaption');c.textContent=cap;f.appendChild(c);return f}
function showCard(r){const c=document.getElementById('card');c.style.display='flex';
  const q=r.kind==='skin'?'skin_same':r.question;
  document.getElementById('ct').textContent=r.kind==='skin'?'Pelle: confronto con il riferimento':Q[q];
  document.getElementById('cp').textContent=(r.kind==='trait'?'Una sola domanda per tutte le immagini di questo personaggio. Sì solo se tutto ciò che la domanda dice è vero. ':'Accanto a ogni immagine vedrai il riferimento. ')+'→ sì · ← no · ↓ non si vede · ⌫ indietro.';
  c.dataset.block=r.block}
function closeCard(){const c=document.getElementById('card');shownCard=c.dataset.block;c.style.display='none';render()}
function answer(a){if(document.getElementById('card').style.display==='flex'){return}
  if(i>=S.length)return;const r=S[i],q=qid(r);A[r.block+'|'+r.pos+'|'+q]=a;
  if(r.kind==='skin'){ // clear deeper answers that no longer apply
    const k=r.block+'|'+r.pos; if(q==='skin_same'&&a!=='no'){delete A[k+'|skin_lighter'];delete A[k+'|skin_darker']}
    if(q==='skin_lighter'&&a!=='no'){delete A[k+'|skin_darker']}}
  save();flash(a);
  if(sub+1<subs(r).length){sub++}else{i++;sub=0}render()}
function back(){if(sub>0){sub--}else if(i>0){i--;sub=subs(S[i]).length-1}shownCard=S[i]?S[i].block:null;render()}
function flash(a){const f=document.getElementById('flash');f.textContent=a;f.style.color=a==='sì'?'var(--yes)':a==='no'?'var(--no)':'var(--unk)';f.style.opacity=.9;setTimeout(()=>f.style.opacity=0,180)}
addEventListener('keydown',e=>{if(document.getElementById('card').style.display==='flex'){if(e.key===' '||e.key==='Enter'){e.preventDefault();closeCard()}return}
  if(e.key==='ArrowRight'){e.preventDefault();answer('sì')}else if(e.key==='ArrowLeft'){e.preventDefault();answer('no')}
  else if(e.key==='ArrowDown'){e.preventDefault();answer('non so')}else if(e.key==='Backspace'){e.preventDefault();back()}});
document.querySelectorAll('#keys button[data-a]').forEach(b=>b.onclick=()=>answer(b.dataset.a));
document.getElementById('back').onclick=back;document.getElementById('go').onclick=closeCard;
document.getElementById('dl').onclick=()=>{let t='block,pos,item,showing,question,answer\n';
  S.forEach(r=>{const L=r.kind==='skin'?['skin_same','skin_lighter','skin_darker']:[r.question];
    L.forEach(q=>{const a=A[r.block+'|'+r.pos+'|'+q];if(a!==undefined)t+=[r.block,r.pos,r.item,r.showing,q,a].join(',')+'\n'})});
  const u=URL.createObjectURL(new Blob(['﻿'+t],{type:'text/csv'}));const l=document.createElement('a');l.href=u;l.download='te_traits_alessandro.csv';l.click()};
render();
</script></body></html>"""


def make_page():
    from PIL import Image
    key = {r["item"]: r for r in rd(DATA / "te_traits_key_A.csv")}
    sched = rd(DATA / "te_traits_schedule_A.csv")
    out = IMG_ROOT / "_grid_viewer" / "te_traits"; (out / "img").mkdir(parents=True, exist_ok=True)
    def jpg(src, dst):
        if not dst.exists():
            im = Image.open(IMG_ROOT / src).convert("RGB"); im.thumbnail((720, 900), Image.LANCZOS); im.save(dst, "JPEG", quality=88)
    for it, r in key.items():
        jpg(r["file"], out / "img" / f"{it}.jpg")
    ref = {}
    for it, r in key.items():
        name = f"ref_{r['char']}_{r['seed']}.jpg"
        jpg(f"benchmark_portraits/phase_c/{CHARS[r['char']]}_baseline_krea2_seed{r['seed']}_00001_.png", out / "img" / name)
        ref[it] = name
    qtext = {q["id"]: q["question_it"] for q in rd(DATA / "te_traits_questions.csv")}
    S = [{"block": s["block"], "pos": int(s["pos"]), "item": s["item"], "showing": int(s["showing"]),
          "question": s["question"], "kind": s["kind"]} for s in sched]
    html = PAGE.replace("__SCHED__", json.dumps(S, separators=(",", ":"))).replace("__QUESTIONS__", json.dumps(qtext, ensure_ascii=False)).replace("__REF__", json.dumps(ref))
    (out / "index.html").write_text(html, encoding="utf-8")
    print("page", out / "index.html", "steps (before skin follow-ups)", len(S), "images", len(key))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", action="store_true"); ap.add_argument("--page", action="store_true"); ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: IMG_ROOT = Path(a.img_root)
    if a.key: make_key()
    if a.page: make_page()
