"""C64 — text-encoder pilot: what each layer of Qwen3-VL-4B does to a Krea-2 picture (docs/plan_te_pilot.md).
Written 2026-10-11, before any render. Exploratory; one prompt, one seed. Renders authorised by Alessandro.

  python te_pilot.py --plan            # data/te_pilot_plan.csv
  python te_pilot.py --queue --checks  # the 7 control renders only
  python te_pilot.py --check           # gates; nothing else runs unless they pass
  python te_pilot.py --queue           # everything else
  python te_pilot.py --count           # expected N missing 0
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
    html = TE_PAGE.replace("__SLOTS__", json.dumps(slots)).replace("__TRAITS__", json.dumps(TRAITS, ensure_ascii=False))
    (out / "eye_test.html").write_text(html, encoding="utf-8")
    print(len(items), "renders,", len(slots), "showings ->", out / "eye_test.html")


TE_PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>C64: tratti del prompt</title>
<style>
body{margin:0;background:#1d1d1f;color:#eee;font:14px system-ui,sans-serif}
#wrap{display:flex;gap:10px;padding:8px;box-sizing:border-box;height:100vh}
#view{flex:1;display:flex;gap:6px;overflow:auto;background:#000;border-radius:8px;cursor:zoom-in}
#view.zoom{cursor:zoom-out}#view figure{margin:0;flex:1;min-width:0}#view.zoom figure{flex:none}
#view img{width:100%;display:block}#view.zoom img{width:auto}
figcaption{position:sticky;top:0;background:#000c;padding:3px 8px;font-weight:700}
#side{width:470px;overflow:auto;background:#2a2a2d;border-radius:8px;padding:10px;box-sizing:border-box}
.g{color:#9ab;font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin:10px 0 2px}
.t{display:flex;align-items:center;gap:4px;padding:1px 0}.t span{flex:1;font-size:13px}
button{font:13px system-ui;padding:3px 7px;border-radius:6px;border:1px solid #555;background:#333;color:#ddd;cursor:pointer}
button.on.A{background:#7a2e2e;border-color:#c55}button.on.P{background:#2f4f3a;border-color:#6a8}button.on.X{background:#2e4a7a;border-color:#69c}
button.on.q{background:#3b6e4f;border-color:#6c6}.big{padding:6px 12px}
textarea{width:100%;box-sizing:border-box;background:#222;color:#eee;border:1px solid #555;border-radius:6px;font:13px system-ui}
#n{color:#aaa}small{color:#999}
</style></head><body><div id="wrap">
<div id="view"><figure><figcaption>ORIGINALE</figcaption><img src="base.jpg"></figure><figure><figcaption>MODIFICA</figcaption><img id="im"></figure></div>
<div id="side"><div id="n"></div><small>Ogni tratto parte da "presente": cambia solo ciò che è diverso dall'originale. Clic sulle immagini: zoom 100%.</small>
<div class="q"><button class="big" id="same">Identica all'originale</button> <button class="big" id="text">Diventata testo / scritte</button></div>
<div id="traits"></div>
<div class="g">Stile complessivo</div><div><button data-q="stile" data-v="inalterato">inalterato</button><button data-q="stile" data-v="cambiato">cambiato</button></div>
<textarea id="stilenote" rows="2" placeholder="se cambiato: come?"></textarea>
<div class="g">Superficie rispetto all'originale</div><div>__DMG__</div>
<div class="g">Altro (libero)</div><textarea id="note" rows="2"></textarea>
<div style="margin-top:8px"><button id="prev">&larr;</button><button id="next">avanti &rarr;</button> <button id="exp">Scarica le risposte</button></div></div></div>
<script>
const S=__SLOTS__,T=__TRAITS__,K="te_pilot_eye_v1";let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;try{i=Math.min(+localStorage.getItem(K+"_i")||0,S.length-1)}catch(e){}const $=q=>document.querySelector(q);
let g="";$("#traits").innerHTML=T.map(([gr,id,lab])=>{let h=gr!==g?`<div class="g">${gr}</div>`:"";g=gr;
 return h+`<div class="t"><span>${lab}</span>`+[["A","assente"],["P","presente"],["X","amplificato"]].map(([v,l])=>`<button class="${v}" data-t="${id}" data-v="${v}">${l}</button>`).join("")+`</div>`}).join("");
function cur(){const s=S[i];if(!A[s])A[s]={t:{},touched:false};return A[s]}
function save(){try{localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_i",i)}catch(e){}}
function show(){const a=A[S[i]]||{t:{}};$("#im").src=S[i].split("#")[0]+".jpg";
 $("#n").textContent=`immagine ${i+1} di ${S.length} · completate ${S.filter(s=>A[s]&&A[s].touched).length}`;
 document.querySelectorAll("button[data-t]").forEach(b=>b.classList.toggle("on",(a.t[b.dataset.t]||"P")===b.dataset.v));
 document.querySelectorAll("button[data-q]").forEach(b=>b.classList.toggle("on",a[b.dataset.q]===b.dataset.v));
 $("#same").classList.toggle("on",!!a.same);$("#text").classList.toggle("on",!!a.text);
 $("#stilenote").value=a.stilenote||"";$("#note").value=a.note||"";save()}
document.querySelectorAll("button[data-t]").forEach(b=>b.onclick=()=>{const a=cur();a.t[b.dataset.t]=b.dataset.v;a.same=false;a.touched=true;show()});
document.querySelectorAll("button[data-q]").forEach(b=>b.onclick=()=>{const a=cur();a[b.dataset.q]=b.dataset.v;a.touched=true;if(b.dataset.q==="stile"||b.dataset.q==="dmg")a.same=false;show()});
$("#same").onclick=()=>{const a=cur();a.same=!a.same;if(a.same){a.t={};a.text=false;a.stile="inalterato";a.dmg="come";}a.touched=true;show();if(a.same&&i<S.length-1){i++;show()}};
$("#text").onclick=()=>{const a=cur();a.text=!a.text;if(a.text){T.forEach(([,id])=>a.t[id]="A");a.same=false}a.touched=true;show()};
$("#stilenote").oninput=e=>{const a=cur();a.stilenote=e.target.value;a.touched=true;save()};$("#note").oninput=e=>{const a=cur();a.note=e.target.value;a.touched=true;save()};
$("#prev").onclick=()=>{if(i>0){i--;show()}};$("#next").onclick=()=>{const a=cur();a.touched=true;if(i<S.length-1){i++;show()}};
$("#view").onclick=()=>$("#view").classList.toggle("zoom");
const q=v=>'"'+String(v||"").replace(/"/g,'""').replace(/\n/g," ")+'"';
$("#exp").onclick=()=>{let t="slot,touched,same,text,"+T.map(x=>x[1]).join(",")+",stile,stilenote,dmg,note\n";
 S.forEach(s=>{const a=A[s]||{t:{}};t+=[s,a.touched?1:0,a.same?1:0,a.text?1:0,...T.map(x=>a.t[x[1]]||"P"),a.stile||"",q(a.stilenote),a.dmg||"",q(a.note)].join(",")+"\n"});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="te_pilot_eye_alessandro.csv";l.click()};
show();
</script></body></html>""".replace("__DMG__", "".join(f'<button data-q="dmg" data-v="{v}">{l}</button>' for v, l in
    [("pulito", "più pulita"), ("come", "come l'originale"), ("lieve", "peggio: lieve"), ("medio", "medio"), ("forte", "forte")]))


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "checks", "check", "count", "page"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.checks)
    if a.check: check()
    if a.count: count()
    if a.page: page()
