"""C64 — text-encoder pilot: what each layer of Qwen3-VL-4B does to a Krea-2 picture (docs/plan_te_pilot.md).
Written 2026-10-11, before any render. Exploratory; one prompt, one seed. Renders authorised by Alessandro.

  python te_pilot.py --plan            # data/te_pilot_plan.csv
  python te_pilot.py --queue --checks  # the 7 control renders only
  python te_pilot.py --check           # gates; nothing else runs unless they pass
  python te_pilot.py --queue           # everything else
  python te_pilot.py --count           # expected N missing 0
  python te_pilot.py --page            # full eye page (all doses) + data/te_pilot_eye_key.csv
  python te_pilot.py --page1           # eye page, phase 1: doses +-1.00 only + data/te_pilot_eye_key_phase1.csv
  python te_pilot.py --measure         # data/te_pilot_measures.csv (after the renders)
  python te_pilot.py --sheets          # contact sheets in Text2Img/benchmark_te_pilot/sheets

Text-encoder edits go through ArthemyKrea2CLIPTuner (Real Value, granular_json, x(1+d)) placed between the
ResetPatcher's CLIP and CLIPTextEncode. Language layer L, attention = self_attn.{q,k,v,o}_proj, MLP =
mlp.{gate,up,down}_proj. Krea-2 taps hidden_states[2,5,...,35] (comfy/text_encoders/krea2.py), and comfy's
tap k is the input of layer k: layer 35 is never read (null control), layers 0-34 are.
The DiT-side text adapter (txtfusion, slots 28-33 of the Model Tuner vector) is swept too.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "te_pilot_plan.csv"
FOLDER = "benchmark_te_pilot"
PID, SEED = "P1_elfbrawler", "1618033"
DOSES = [-1.0, -0.35, -0.1, 0.1, 0.35, 1.0]
ATTN = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj"]
MLP = ["mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]
TXT_SLOTS = ["txtfusion_layerwise0", "txtfusion_layerwise1", "txtfusion_refiner0", "txtfusion_refiner1",
             "txtfusion_projector", "txtmlp"]


def gj_te(layer, mats, d):
    return json.dumps({f"layers.{layer}.{m}.weight": d for m in mats})


def vo_slot(slot, d):
    v = ["0.0"] * 34; v[28 + slot] = f"{d:.3f}"; return ",".join(v)


def tag(d):
    return f"{'p' if d > 0 else 'm'}{abs(d):.2f}"


def f(cond, folder=FOLDER, pid=PID, seed=SEED):
    return c47.IMG_ROOT / folder / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"


def make_plan():
    elf = next(r for r in csv.DictReader(open(DATA / "comic_form_plan.csv", encoding="utf-8")) if r["prompt_id"] == PID)
    keys = ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")
    rows = []
    def add(cond, te_json, vo, phase, unit, part, dose):
        prefix = f"{PID}_{cond}_krea2_seed{SEED}"
        rows.append({"row": len(rows), "phase": phase, "unit": unit, "part": part, "dose": dose, "prompt_id": PID, "seed": SEED,
                     "cond": cond, "te_granular_json": te_json, "vectors_override": vo, "prompt_text": elf["prompt_text"],
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **{k: elf[k] for k in keys}})
    # controls
    add("CHK_repro_baseline", "", "", "check", "", "", 0)
    add("CHK_null_L35_both_p1.00", gj_te(35, ATTN + MLP, 1.0), "", "check", "L35", "both", 1.0)
    add("CHK_null_visual4_p1.00", json.dumps({f"visual.blocks.4.{m}.weight": 1.0 for m in ("attn.qkv", "attn.proj", "mlp.linear_fc1", "mlp.linear_fc2")}),
        "", "check", "V4", "both", 1.0)
    add("CHK_active_L02_mlp_p1.00", gj_te(2, MLP, 1.0), "", "check", "L02", "mlp", 1.0)
    for L in (5, 17, 29):
        add(f"CHK_qk_L{L:02d}_p1.00", gj_te(L, ATTN[:2], 1.0), "", "check", f"L{L:02d}", "qk", 1.0)
    # main: every read layer, attention and MLP apart, six doses
    for L in range(35):
        for part, mats in (("attn", ATTN), ("mlp", MLP)):
            for d in DOSES:
                add(f"L{L:02d}_{part}_{tag(d)}", gj_te(L, mats, d), "", "main", f"L{L:02d}", part, d)
    # the DiT-side text adapter
    for s, name in enumerate(TXT_SLOTS):
        for d in DOSES:
            add(f"{name}_{tag(d)}", "", vo_slot(s, d), "main", name, "slot", d)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["te_granular_json"]:
        wf["51"] = {"class_type": "ArthemyKrea2CLIPTuner", "inputs": {
            "clip": ["37", 1], "mode": "Real Value", "vectors_override": "", "granular_json": r["te_granular_json"],
            "Embedding": 0.0, "Layer_1": 0.0, "Layer_2": 0.0, "Layer_3": 0.0, "Layer_4": 0.0, "Layer_5": 0.0,
            "Layer_6": 0.0, "Layer_7": 0.0}}
        wf["40"]["inputs"]["clip"] = ["51", 0]
    return wf


def queue(checks_only):
    n = 0
    for r in csv.DictReader(open(PLAN, encoding="utf-8")):
        if (checks_only and r["phase"] != "check") or (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def _im(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def check():
    base = _im(f("baseline", "benchmark_comic_form"))
    d = lambda c: int(np.abs(_im(f(c)) - base).max())
    res = {"repro": d("CHK_repro_baseline"), "null_L35": d("CHK_null_L35_both_p1.00"), "null_visual": d("CHK_null_visual4_p1.00"),
           "active_L02": d("CHK_active_L02_mlp_p1.00")}
    qk = {L: d(f"CHK_qk_L{L:02d}_p1.00") for L in (5, 17, 29)}
    for k, v in res.items():
        print(f"{k}: max abs diff against the C60 baseline = {v}")
    print("q+k only (QK-norm prediction, reported, not a gate):", qk)
    ok = res["repro"] == 0 and res["active_L02"] > 0
    print("CHECK", "PASS" if ok else "FAIL - stop",
          "| structure:", "layer 35 unread as predicted" if res["null_L35"] == 0 else "layer 35 CHANGES the image (prediction wrong)",
          "/", "visual tower inert" if res["null_visual"] == 0 else "visual tower CHANGES the image")


KEY = DATA / "te_pilot_eye_key.csv"
LABELS = DATA / "te_pilot_eye_alessandro.csv"
TRAITS = [  # (group, id, label) — from the prompt of P1_elfbrawler, in the order it describes them
    ("Personaggio", "donna", "donna, giovane adulta"), ("Personaggio", "elfa", "elfa: orecchie a punta"),
    ("Personaggio", "corna", "piccole corna chiare"), ("Personaggio", "capelli", "capelli verdi arruffati, punte turchesi"),
    ("Personaggio", "sopracciglia", "sopracciglia verdi spesse"), ("Personaggio", "benda", "benda su un occhio"),
    ("Personaggio", "occhio", "occhio verde brillante"), ("Personaggio", "pelle", "pelle abbronzata"),
    ("Personaggio", "espressione", "sorriso spavaldo, espressione compiaciuta"),
    ("Abiti", "giacca", "giacca blu scuro con collo di pelliccia"), ("Abiti", "spallaccio", "spallaccio dorato effetto legno"),
    ("Abiti", "uniforme", "uniforme nera"), ("Abiti", "cinghie", "cinghie di cuoio marrone"),
    ("Abiti", "guanto", "guanto d'arme argentato"), ("Abiti", "elettricita", "elettricità blu sul guanto"),
    ("Posa", "pugno", "pugno mostrato allo spettatore"), ("Posa", "sguardo", "sguardo verso la sua sinistra"),
    ("Posa", "dallalto", "vista dall'alto, prospettiva forte"), ("Posa", "inquadratura", "mezzo busto, primo piano sul guanto"),
    ("Scena", "sfondo", "sfondo bianco piatto"), ("Scena", "luce", "luce calda, ombre ambra, riflessi blu"),
    ("Stile", "fumetto", "fumetto western realistico"), ("Stile", "inchiostro", "contorni a inchiostro marcati"),
    ("Stile", "tratteggio", "ombre tratteggiate")]

# Traits the baseline itself does not show (Alessandro, 2026-10-11): their starting value is "absent".
BASE_ABSENT = ["espressione", "sguardo"]


def page(out_dir=None, write_key=True):
    """Exploratory eye page: baseline (left, fixed) against one edit (right); every render once, shuffled (rng 64),
    20 repeats; condition hidden behind an anonymous id."""
    import shutil
    rng = np.random.default_rng(64)
    out = Path(out_dir) if out_dir else c47.IMG_ROOT / FOLDER / "eye_test"; out.mkdir(parents=True, exist_ok=True)
    rows = [r for r in csv.DictReader(open(PLAN, encoding="utf-8")) if r["cond"] != "CHK_repro_baseline"
            and (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    ids = rng.permutation(np.arange(1000, 9999))[: len(rows)]
    items = [{"id": f"t{i}", **{k: r[k] for k in ("cond", "unit", "part", "dose", "phase")}, "file": r["expected_filename"]} for r, i in zip(rows, ids)]
    show = [x["id"] for x in items]; rng.shuffle(show)
    rep = list(rng.choice(show, min(20, len(show)), replace=False))
    for x in rep:
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), x)
    from PIL import Image
    for x in items:
        dst = out / f"{x['id']}.jpg"
        if not dst.exists():
            Image.open(c47.IMG_ROOT / FOLDER / x["file"]).convert("RGB").save(dst, "JPEG", quality=92, subsampling=0)
    b = out / "base.jpg"
    if not b.exists():
        Image.open(f("baseline", "benchmark_comic_form")).convert("RGB").save(b, "JPEG", quality=92, subsampling=0)
    if write_key:
        with open(KEY, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["item", "cond", "unit", "part", "dose", "phase", "repeated"])
            for x in items:
                w.writerow([x["id"], x["cond"], x["unit"], x["part"], x["dose"], x["phase"], int(x["id"] in rep)])
    slots = [f"{s}#{k}" for k, s in enumerate(show)]
    html = TE_PAGE.replace("__SLOTS__", json.dumps(slots)).replace("__TRAITS__", json.dumps(TRAITS, ensure_ascii=False)).replace("__BASEABS__", json.dumps(BASE_ABSENT))
    (out / "eye_test.html").write_text(html, encoding="utf-8")
    print(len(items), "renders,", len(slots), "showings ->", out / "eye_test.html")


TE_PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>C64: tratti del prompt</title>
<style>
body{margin:0;background:#1d1d1f;color:#eee;font:14px system-ui,sans-serif}
#wrap{display:flex;gap:10px;padding:8px;box-sizing:border-box;height:100vh}
#view{flex:1;display:flex;gap:6px;overflow:auto;background:#000;border-radius:8px;cursor:zoom-in}
#view.zoom{cursor:zoom-out}#view figure{margin:0;flex:1;min-width:0}#view.zoom figure{flex:none}
#view img{width:100%;display:block}#view.zoom img{width:auto}#view.single #fb{display:none}
figcaption{position:sticky;top:0;background:#000c;padding:3px 8px;font-weight:700;z-index:2}
#fe.isbase figcaption{background:#8a2b2b}
#side{width:480px;overflow:auto;background:#2a2a2d;border-radius:8px;padding:10px;box-sizing:border-box}
#n{color:#aaa}#help{font-size:12px;color:#bbb;margin:4px 0 6px}
.g{color:#9ab;font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin:8px 0 2px}
.r{display:flex;align-items:center;gap:4px;padding:2px 4px;border-radius:6px;border:2px solid transparent}
.r>span{flex:1;font-size:13px}.r.chg>span{color:#ffd27a}
.r.cur{border-color:#ffcc55;background:#3a3524}
button{font:13px system-ui;padding:3px 7px;border-radius:6px;border:1px solid #555;background:#333;color:#ddd;cursor:pointer}
button.on{background:#2f4f3a;border-color:#6a8;color:#fff}button.on.A{background:#7a2e2e;border-color:#c55}button.on.X{background:#2e4a7a;border-color:#69c}
textarea{flex:1;box-sizing:border-box;background:#222;color:#eee;border:1px solid #555;border-radius:6px;font:13px system-ui}
.r.txt{align-items:stretch;flex-direction:column}.r.txt textarea{width:100%}
kbd{font:12px ui-monospace,monospace;background:#444;border:1px solid #666;border-bottom-width:2px;border-radius:4px;padding:0 4px;color:#fff}
</style></head><body><div id="wrap">
<div id="view" class="single"><figure id="fb"><figcaption>ORIGINALE</figcaption><img src="base.jpg"></figure><figure id="fe"><figcaption id="cap">MODIFICA</figcaption><img id="im"></figure></div>
<div id="side"><div id="n"></div>
<div id="help"><kbd>↑</kbd><kbd>↓</kbd> voce · <kbd>←</kbd><kbd>→</kbd> valore · <kbd>spazio</kbd> tieni premuto = originale · <kbd>Invio</kbd> avanti · <kbd>⌫</kbd> indietro<br>
Tutto parte da "nulla è cambiato": tocca solo ciò che vedi diverso. Nelle note, <kbd>→</kbd> per scrivere, <kbd>Esc</kbd> per uscire.</div>
<div id="rows"></div>
<div style="margin-top:8px"><button id="prev">&larr; indietro</button><button id="next">avanti &rarr;</button> <button id="lay">affiancate / una sola</button> <button id="exp">Scarica le risposte</button></div></div></div>
<script>
const S=__SLOTS__,T=__TRAITS__,K="te_pilot_eye_v1";let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;try{i=Math.min(+localStorage.getItem(K+"_i")||0,S.length-1)}catch(e){}const $=q=>document.querySelector(q);
const TR=[["A","assente"],["P","presente"],["X","amplificato"]];const BA=__BASEABS__;const TD=id=>BA.includes(id)?"A":"P";
if(!localStorage.getItem(K+"_mig1")){for(const s in A){const a=A[s];if(a&&a.touched&&!a.text){a.t=a.t||{};BA.forEach(id=>{if(!(id in a.t))a.t[id]="P"})}}try{localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_mig1","1")}catch(e){}}
const R=[{k:"text",g:"",lab:"diventata testo / scritte",o:[["no","no"],["si","sì"]],d:"no"}];
let gp="";T.forEach(([gr,id,lab])=>{R.push({k:"t."+id,g:gr!==gp?gr:"",lab:lab+(BA.includes(id)?" <small>(assente nell'originale)</small>":""),o:TR,d:TD(id)});gp=gr});
R.push({k:"braccio",g:"Posa del guanto",lab:"braccio del guanto rispetto all'originale",o:[["stesso","stesso"],["altro","l'altro"],["ambiguo","ambiguo / a metà"]],d:"stesso"});
R.push({k:"stile",g:"Insieme",lab:"stile complessivo",o:[["inalterato","inalterato"],["cambiato","cambiato"]],d:"inalterato"});
R.push({k:"stilenote",g:"",lab:"se lo stile è cambiato: come?",txt:1});
R.push({k:"dmg",g:"",lab:"superficie rispetto all'originale",o:[["pulito","più pulita"],["come","come l'originale"],["lieve","peggio: lieve"],["medio","medio"],["forte","forte"]],d:"come"});
R.push({k:"note",g:"",lab:"altro (libero)",txt:1});
let c=0;
$("#rows").innerHTML=R.map((r,j)=>(r.g?`<div class="g">${r.g}</div>`:"")+(r.txt?`<div class="r txt" id="r${j}"><span>${r.lab}</span><textarea rows="2" data-j="${j}"></textarea></div>`:
 `<div class="r" id="r${j}"><span>${r.lab}</span>`+r.o.map(([v,l])=>`<button class="${v}" data-j="${j}" data-v="${v}">${l}</button>`).join("")+`</div>`)).join("");
function cur(){const s=S[i];if(!A[s])A[s]={t:{},touched:false};return A[s]}
function get(a,r){if(r.k==="text")return a.text?"si":"no";if(r.k.startsWith("t."))return a.t[r.k.slice(2)]||TD(r.k.slice(2));
 if(r.k==="braccio")return a.braccio||(a.text?"":"stesso");return a[r.k]||r.d}
function set(r,v){const a=cur();a.touched=true;a.same=false;
 if(r.k==="text"){a.text=v==="si";if(a.text)T.forEach(([,id])=>a.t[id]="A");else T.forEach(([,id])=>{if(a.t[id]==="A"&&TD(id)==="P")delete a.t[id]})}
 else if(r.k.startsWith("t."))a.t[r.k.slice(2)]=v;else a[r.k]=v;show()}
function save(){try{localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_i",i)}catch(e){}}
const PRE=new Image();
function show(){const a=A[S[i]]||{t:{}};
 if($("#im").dataset.s!==S[i]){$("#im").dataset.s=S[i];$("#im").src=S[i].split("#")[0]+".jpg";if(i<S.length-1)PRE.src=S[i+1].split("#")[0]+".jpg"}
 $("#n").textContent=`immagine ${i+1} di ${S.length} · completate ${S.filter(s=>A[s]&&A[s].touched).length}`;
 R.forEach((r,j)=>{const el=$("#r"+j);el.classList.toggle("cur",j===c);
  if(r.txt){const ta=el.querySelector("textarea");if(document.activeElement!==ta)ta.value=a[r.k]||"";return}
  const v=get(a,r);el.classList.toggle("chg",v!==r.d&&v!=="");el.querySelectorAll("button").forEach(b=>b.classList.toggle("on",b.dataset.v===v))});
 save()}
function move(d){c=Math.max(0,Math.min(R.length-1,c+d));show();$("#r"+c).scrollIntoView({block:"nearest"})}
function step(d){const r=R[c];if(r.txt){if(d>0)$("#r"+c+" textarea").focus();return}
 const vs=r.o.map(x=>x[0]);let k=vs.indexOf(get(cur(),r));if(k<0)k=vs.indexOf(r.d);k=Math.max(0,Math.min(vs.length-1,k+d));set(r,vs[k])}
function next(){const a=cur();a.touched=true;if(i<S.length-1){i++;c=0;show();$("#side").scrollTop=0}}
function prev(){if(i>0){i--;c=0;show();$("#side").scrollTop=0}}
function base(on){$("#im").src=on?"base.jpg":S[i].split("#")[0]+".jpg";$("#fe").classList.toggle("isbase",on);$("#cap").textContent=on?"ORIGINALE":"MODIFICA"}
document.querySelectorAll("button[data-j]").forEach(b=>b.onclick=()=>{c=+b.dataset.j;set(R[c],b.dataset.v)});
document.querySelectorAll("textarea").forEach(t=>{t.onfocus=()=>{c=+t.dataset.j;show()};t.oninput=()=>{const a=cur();a[R[+t.dataset.j].k]=t.value;a.touched=true;save()}});
$("#prev").onclick=prev;$("#next").onclick=next;$("#lay").onclick=()=>$("#view").classList.toggle("single");
$("#view").onclick=()=>$("#view").classList.toggle("zoom");
addEventListener("keydown",e=>{
 if(e.target.tagName==="TEXTAREA"){if(e.key==="Escape"||e.key==="ArrowUp"&&!e.target.value.includes("\n")||e.key==="ArrowDown"&&!e.target.value.includes("\n")){e.preventDefault();e.target.blur();if(e.key!=="Escape")move(e.key==="ArrowDown"?1:-1)}return}
 if(e.ctrlKey||e.metaKey||e.altKey)return;
 if(e.key===" "){e.preventDefault();if(!e.repeat)base(true);return}
 if(e.key==="ArrowDown"){e.preventDefault();move(1)}else if(e.key==="ArrowUp"){e.preventDefault();move(-1)}
 else if(e.key==="ArrowRight"){e.preventDefault();step(1)}else if(e.key==="ArrowLeft"){e.preventDefault();step(-1)}
 else if(e.key==="Enter"){e.preventDefault();next()}else if(e.key==="Backspace"){e.preventDefault();prev()}
 else if(e.key.toLowerCase()==="z")$("#view").classList.toggle("zoom");
});
addEventListener("keyup",e=>{if(e.key===" ")base(false)});
const q=v=>'"'+String(v||"").replace(/"/g,'""').replace(/\n/g," ")+'"';
function isSame(a){return !!a.same||(a.touched&&!a.text&&T.every(([,id])=>(a.t[id]||TD(id))===TD(id))&&(a.braccio||"stesso")==="stesso"&&(a.stile||"inalterato")==="inalterato"&&(a.dmg||"come")==="come")}
$("#exp").onclick=()=>{let t="slot,touched,same,text,"+T.map(x=>x[1]).join(",")+",braccio,stile,stilenote,dmg,note\n";
 S.forEach(s=>{const a=A[s]||{t:{}};t+=[s,a.touched?1:0,isSame(a)?1:0,a.text?1:0,...T.map(x=>a.t[x[1]]||TD(x[1])),a.braccio||(a.text?"":"stesso"),a.stile||"inalterato",q(a.stilenote),a.dmg||"come",q(a.note)].join(",")+"\n"});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="te_pilot_eye_alessandro.csv";l.click()};
show();
</script></body></html>"""



# ---------------------------------------------------------------- eye pass, phase 1 (doses +-1.00 only)
KEY1 = DATA / "te_pilot_eye_key_phase1.csv"
LABELS1 = DATA / "te_pilot_eye_alessandro_phase1.csv"


def page_phase1():
    """Phase 1 of the eye pass (2026-10-11): only the renders at dose +-1.00 (chosen by dose, before looking), plus the
    six checks, in a new shuffle (rng 65) with 10 unannounced repeats. Same anonymous ids and jpgs as the full page, so
    the page lives beside it in eye_test/. Basic questions only: how much it changed, style, gauntlet arm, surface,
    free note (the 24 traits were dropped, 2026-10-11, before any phase-1 label)."""
    rng = np.random.default_rng(65)
    key = list(csv.DictReader(open(KEY, encoding="utf-8")))
    items = [r for r in key if r["repeated"] in ("0", "1") and r["dose"] in ("1.0", "-1.0")]
    items = list({r["item"]: r for r in items}.values())
    show = [r["item"] for r in items]; rng.shuffle(show)
    rep = list(rng.choice(show, 10, replace=False))
    for x in rep:
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), x)
    with open(KEY1, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["item", "cond", "unit", "part", "dose", "phase", "repeated"])
        for r in items:
            w.writerow([r["item"], r["cond"], r["unit"], r["part"], r["dose"], r["phase"], int(r["item"] in rep)])
    slots = [f"{s}#{k}" for k, s in enumerate(show)]
    out = c47.IMG_ROOT / FOLDER / "eye_test"
    html = (TE_PAGE1.replace("__SLOTS__", json.dumps(slots)).replace("__TRAITS__", json.dumps(TRAITS, ensure_ascii=False))
            .replace("__BASEABS__", json.dumps(BASE_ABSENT)))
    (out / "eye_test_fase1.html").write_text(html, encoding="utf-8")
    print(len(items), "renders,", len(slots), "showings ->", out / "eye_test_fase1.html")


TE_PAGE1 = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>C64 fase 1: dosi forti</title>
<style>
body{margin:0;background:#1d1d1f;color:#eee;font:14px system-ui,sans-serif}
#wrap{display:flex;gap:10px;padding:8px;box-sizing:border-box;height:100vh}
#view{flex:1;display:flex;gap:6px;overflow:auto;background:#000;border-radius:8px;cursor:zoom-in}
#view.zoom{cursor:zoom-out}#view figure{margin:0;flex:1;min-width:0}#view.zoom figure{flex:none}
#view img{width:100%;display:block}#view.zoom img{width:auto}#view.single #fb{display:none}
figcaption{position:sticky;top:0;background:#000c;padding:3px 8px;font-weight:700;z-index:2}
#fe.isbase figcaption{background:#8a2b2b}
#side{width:480px;overflow:auto;background:#2a2a2d;border-radius:8px;padding:10px;box-sizing:border-box}
#n{color:#aaa}#help{font-size:12px;color:#bbb;margin:4px 0 6px}
.g{color:#9ab;font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin:8px 0 2px}
.r{display:flex;align-items:center;gap:4px;padding:2px 4px;border-radius:6px;border:2px solid transparent;flex-wrap:wrap}
.r>span{flex:1;font-size:13px;min-width:130px}.r.chg>span{color:#ffd27a}
.r.cur{border-color:#ffcc55;background:#3a3524}
button{font:13px system-ui;padding:3px 7px;border-radius:6px;border:1px solid #555;background:#333;color:#ddd;cursor:pointer}
button.on{background:#2f4f3a;border-color:#6a8;color:#fff}button.on.A{background:#7a2e2e;border-color:#c55}button.on.X{background:#2e4a7a;border-color:#69c}
textarea{box-sizing:border-box;background:#222;color:#eee;border:1px solid #555;border-radius:6px;font:13px system-ui}
.r.txt{align-items:stretch;flex-direction:column}.r.txt textarea{width:100%}
kbd{font:12px ui-monospace,monospace;background:#444;border:1px solid #666;border-bottom-width:2px;border-radius:4px;padding:0 4px;color:#fff}
</style></head><body><div id="wrap">
<div id="view" class="single"><figure id="fb"><figcaption>ORIGINALE</figcaption><img src="base.jpg"></figure><figure id="fe"><figcaption id="cap">MODIFICA</figcaption><img id="im"></figure></div>
<div id="side"><div id="n"></div>
<div id="help"><kbd>↑</kbd><kbd>↓</kbd> voce · <kbd>←</kbd><kbd>→</kbd> valore · <kbd>spazio</kbd> tieni premuto = originale · <kbd>Invio</kbd> avanti · <kbd>⌫</kbd> indietro<br>
Un'immagine uguale all'originale: basta <kbd>Invio</kbd>.</div>
<div id="rows"></div>
<div style="margin-top:8px"><button id="prev">&larr; indietro</button><button id="next">avanti &rarr;</button> <button id="lay">affiancate / una sola</button> <button id="exp">Scarica le risposte</button></div></div></div>
<script>
const S=__SLOTS__,T=__TRAITS__,BA=__BASEABS__,K="te_pilot_eye_fase1";const TD=id=>BA.includes(id)?"A":"P";
let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
// one-off import of answers already given on the full page (first showings only), same anonymous ids
try{if(!localStorage.getItem(K+"_imp")){const O=JSON.parse(localStorage.getItem("te_pilot_eye_v1")||"{}");const first={};
 Object.keys(O).sort((x,y)=>+x.split("#")[1]-+y.split("#")[1]).forEach(s=>{const id=s.split("#")[0];if(!(id in first))first[id]=O[s]});
 const done=new Set();S.forEach(s=>{const id=s.split("#")[0];const o=first[id];if(o&&o.touched&&!done.has(id)&&!A[s]){
  const a=JSON.parse(JSON.stringify(o));a.tv=true;a.imported=true;BA.forEach(t=>{if(!(t in a.t))a.t[t]="P"});
  a.entita=a.text?"testo":(a.same?"nessuna":"");A[s]=a;done.add(id)}});
 localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_imp","1")}}catch(e){}
let i=0;try{i=Math.min(+localStorage.getItem(K+"_i")||0,S.length-1)}catch(e){}const $=q=>document.querySelector(q);
const TR=[["A","assente"],["P","presente"],["X","amplificato"]];
const R=[{k:"entita",g:"Giudizio rapido",lab:"quanto è cambiata rispetto all'originale",o:[["nessuna","nessuna"],["lieve","lieve"],["media","media"],["forte","forte"],["testo","diventata testo"]],d:"nessuna"},
 {k:"stile",g:"",lab:"stile complessivo",o:[["inalterato","inalterato"],["cambiato","cambiato"]],d:"inalterato"},
 {k:"stilenote",g:"",lab:"se lo stile è cambiato: come?",txt:1},
 {k:"braccio",g:"",lab:"braccio del guanto",o:[["stesso","stesso"],["altro","l'altro"],["ambiguo","ambiguo / a metà"]],d:"stesso"},
 {k:"dmg",g:"",lab:"superficie",o:[["pulito","più pulita"],["come","come l'originale"],["lieve","peggio: lieve"],["medio","medio"],["forte","forte"]],d:"come"},
 {k:"note",g:"",lab:"altro (libero)",txt:1}];
let c=0;
$("#rows").innerHTML=R.map((r,j)=>(r.g?`<div class="g">${r.g}</div>`:"")+(r.txt?`<div class="r txt" id="r${j}"><span>${r.lab}</span><textarea rows="2" data-j="${j}"></textarea></div>`:
 `<div class="r" id="r${j}"><span>${r.lab}</span>`+r.o.map(([v,l])=>`<button class="${v}" data-j="${j}" data-v="${v}">${l}</button>`).join("")+`</div>`)).join("");
function cur(){const s=S[i];if(!A[s])A[s]={t:{},touched:false};return A[s]}
function ent(a){return a.entita||(a.text?"testo":(a.imported?"":"nessuna"))}
function get(a,r){if(r.k==="entita")return ent(a);if(r.k.startsWith("t."))return a.t[r.k.slice(2)]||TD(r.k.slice(2));
 if(r.k==="braccio")return a.braccio||(a.text?"":"stesso");return a[r.k]||r.d}
function set(r,v){const a=cur();a.touched=true;
 if(r.k==="entita"){a.entita=v;const was=a.text;a.text=v==="testo";if(a.text&&!was)T.forEach(([,id])=>a.t[id]="A");if(!a.text&&was)a.t={}}
 else if(r.k.startsWith("t.")){a.t[r.k.slice(2)]=v;a.tv=true}else a[r.k]=v;show()}
function save(){try{localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_i",i)}catch(e){}}
const PRE=new Image();
function show(){const a=A[S[i]]||{t:{}};
 if($("#im").dataset.s!==S[i]){$("#im").dataset.s=S[i];$("#im").src=S[i].split("#")[0]+".jpg";if(i<S.length-1)PRE.src=S[i+1].split("#")[0]+".jpg"}
 $("#n").textContent=`immagine ${i+1} di ${S.length} · completate ${S.filter(s=>A[s]&&A[s].touched).length}`+(a.imported?" · (risposta ripresa dalla pagina completa)":"");
 R.forEach((r,j)=>{const el=$("#r"+j);el.classList.toggle("cur",j===c);
  if(r.txt){const ta=el.querySelector("textarea");if(document.activeElement!==ta)ta.value=a[r.k]||"";return}
  const v=get(a,r);el.classList.toggle("chg",v!==r.d&&v!=="");el.querySelectorAll("button").forEach(b=>b.classList.toggle("on",b.dataset.v===v))});
 save()}
function move(d){c=Math.max(0,Math.min(R.length-1,c+d));show();$("#r"+c).scrollIntoView({block:"nearest"})}
function step(d){const r=R[c];if(r.txt){if(d>0)$("#r"+c+" textarea").focus();return}
 const vs=r.o.map(x=>x[0]);let k=vs.indexOf(get(cur(),r));if(k<0)k=vs.indexOf(r.d);k=Math.max(0,Math.min(vs.length-1,k+d));set(r,vs[k])}
function next(){const a=cur();a.touched=true;if(i<S.length-1){i++;c=0;show();$("#side").scrollTop=0}}
function prev(){if(i>0){i--;c=0;show();$("#side").scrollTop=0}}
function base(on){$("#im").src=on?"base.jpg":S[i].split("#")[0]+".jpg";$("#fe").classList.toggle("isbase",on);$("#cap").textContent=on?"ORIGINALE":"MODIFICA"}
document.querySelectorAll("button[data-j]").forEach(b=>b.onclick=()=>{c=+b.dataset.j;set(R[c],b.dataset.v)});
document.querySelectorAll("textarea").forEach(t=>{t.onfocus=()=>{c=+t.dataset.j;show()};t.oninput=()=>{const a=cur();a[R[+t.dataset.j].k]=t.value;a.touched=true;save()}});
$("#prev").onclick=prev;$("#next").onclick=next;$("#lay").onclick=()=>$("#view").classList.toggle("single");
$("#view").onclick=()=>$("#view").classList.toggle("zoom");
addEventListener("keydown",e=>{
 if(e.target.tagName==="TEXTAREA"){if(e.key==="Escape"||e.key==="ArrowUp"&&!e.target.value.includes("\n")||e.key==="ArrowDown"&&!e.target.value.includes("\n")){e.preventDefault();e.target.blur();if(e.key!=="Escape")move(e.key==="ArrowDown"?1:-1)}return}
 if(e.ctrlKey||e.metaKey||e.altKey)return;
 if(e.key===" "){e.preventDefault();if(!e.repeat)base(true);return}
 if(e.key==="ArrowDown"){e.preventDefault();move(1)}else if(e.key==="ArrowUp"){e.preventDefault();move(-1)}
 else if(e.key==="ArrowRight"){e.preventDefault();step(1)}else if(e.key==="ArrowLeft"){e.preventDefault();step(-1)}
 else if(e.key==="Enter"){e.preventDefault();next()}else if(e.key==="Backspace"){e.preventDefault();prev()}
 else if(e.key.toLowerCase()==="z")$("#view").classList.toggle("zoom");
});
addEventListener("keyup",e=>{if(e.key===" ")base(false)});
const q=v=>'"'+String(v||"").replace(/"/g,'""').replace(/\n/g," ")+'"';
$("#exp").onclick=()=>{let t="slot,touched,entita,text,imported,braccio,stile,stilenote,dmg,note\n";
 S.forEach(s=>{const a=A[s]||{t:{}};t+=[s,a.touched?1:0,a.touched?ent(a):"",a.text?1:0,a.imported?1:0,a.braccio||(a.text?"":"stesso"),a.stile||"inalterato",q(a.stilenote),a.dmg||"come",q(a.note)].join(",")+"\n"});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="te_pilot_eye_alessandro_phase1.csv";l.click()};
show();
</script></body></html>"""


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "checks", "check", "count", "page", "page1"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.checks)
    if a.check: check()
    if a.count: count()
    if a.page: page()
    if a.page1: page_phase1()
