"""C106 - two pairs and an odd one: can the eye sort pictures by the edit that made them? (docs/prereg_odd_one_out.md)
Written 2026-10-20 with the pre-registration, before the page and any label. No renders.

  python odd_one_out.py --selftest
  python odd_one_out.py --page      # data/odd_one_out_key.csv and Text2Img/occhio_C106.html
  python odd_one_out.py --rules     # data/odd_one_out_tests.csv
"""
import argparse, csv, itertools, json, math, os, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_depth_control as T

DATA = HERE.parent / "data"
KEY = DATA / "odd_one_out_key.csv"
LABELS = DATA / "odd_one_out_labels.csv"
TESTS = DATA / "odd_one_out_tests.csv"
TE_DIR, TE_SEEDS = "benchmark_te_depth_control2", ["2645751", "3316624", "2718281"]
TE_PERTS = {"D1_dwarf_paladin": ["L09_t", "L26_t", "R09a_t", "R09b_t", "R09c_t", "R26a_t", "R26b_t", "R26c_t"],
            "S1_rally": ["L09_t", "L26_t", "R09a_t", "R09b_t", "R09c_t", "R26a_t", "R26b_t", "R26c_t"],
            "C4_stilllife": ["L09_t", "L26_t", "R09a_t", "R09b_t", "R09c_t", "R26a_t", "R26b_t", "R26c_t"],
            "P5_comic_panels": ["L26_t", "R26a_t", "R26b_t", "R26c_t"]}
DIT_DIR, DIT_SEEDS = "benchmark_stage5/renders", ["42", "777", "1337", "9999", "4242145"]
DIT_PERTS = ["preset_pos", "preset_neg", "preset_half", "blockshuf_pos", "blockshuf_neg", "rand_pos", "rand_neg"]
DIT_PROMPTS = ["G1", "G2", "G3", "G4", "G5", "G6"]


def path(kind, p, c, s):
    return f"{TE_DIR}/{p}_{c}_krea2_seed{s}_00001_.png" if kind == "TE" else f"{DIT_DIR}/{p}_{c}_seed{s}_00001_.png"


def trials():
    rng = random.Random(20201); out = []
    for p, perts in TE_PERTS.items():
        for _ in range(4):
            a, b, c = rng.sample(perts, 3); s1, s2, s3 = rng.sample(TE_SEEDS, 3)
            out.append(("TE", p, a, b, c, s1, s2, s3))
    for p in DIT_PROMPTS:
        for _ in range(2):
            a, b, c = rng.sample(DIT_PERTS, 3); s1, s2, s3 = rng.sample(DIT_SEEDS, 3)
            out.append(("DiT", p, a, b, c, s1, s2, s3))
    rng.shuffle(out)
    reps = rng.sample(range(len(out)), 4); order = list(range(len(out)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 8, len(order)), len(order)), i)
    key = []; seen = set()
    for n, i in enumerate(order, 1):
        kind, p, a, b, c, s1, s2, s3 = out[i]
        imgs = [("A", a, s1), ("A", a, s2), ("B", b, s1), ("B", b, s2), ("C", c, s3)]
        rng.shuffle(imgs)
        key.append({"trial": f"T{n:02d}", "set": kind, "prompt": p, "A": a, "B": b, "C": c, "s1": s1, "s2": s2, "s3": s3,
                    "repeat": int(i in seen), "images": " ".join(f"{g}:{pp}:{s}" for g, pp, s in imgs)})
        seen.add(i)
    return key


def page():
    from PIL import Image
    R = T.img_root(); key = trials(); data = []
    tdir = R / "_thumbs_c106"; tdir.mkdir(exist_ok=True)
    for k in key:
        ims = []
        for j, it in enumerate(k["images"].split()):
            g, c, s = it.split(":"); src = path(k["set"], k["prompt"], c, s)
            th = tdir / f"{k['trial']}_{j}.jpg"
            if not th.exists():
                im = Image.open(R / src).convert("RGB"); im.thumbnail((420, 525)); im.save(th, quality=88)
            ims.append({"t": f"_thumbs_c106/{th.name}", "f": src})
        data.append({"id": k["trial"], "ims": ims})
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    (R / "occhio_C106.html").write_text(PAGE.replace("__DATA__", json.dumps(data)), encoding="utf-8")
    print("trials", len(key), "->", R / "occhio_C106.html")


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>C106 · due coppie e una sola</title><style>
:root{--bg:#f6f5f2;--fg:#1d1d1b;--mut:#6b6a66;--line:#d9d6cf;--card:#fff;--g1:#2a78d6;--g2:#d95926;--g3:#6d6a8a}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe7;--mut:#9b9a95;--line:#34332f;--card:#1f1f1d}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;z-index:2}
button,select{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}
main{padding:12px 16px 40px;max-width:1800px;margin:auto}.row{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.c{background:var(--card);border:3px solid var(--line);border-radius:8px;padding:6px}.c img{width:100%;display:block;border-radius:4px;cursor:zoom-in}
.c.g1{border-color:var(--g1)}.c.g2{border-color:var(--g2)}.c.g3{border-color:var(--g3)}
.b{display:flex;gap:6px;margin-top:6px;justify-content:center}.b button.on[data-v="1"]{background:var(--g1);color:#fff}.b button.on[data-v="2"]{background:var(--g2);color:#fff}.b button.on[data-v="sola"]{background:var(--g3);color:#fff}
.hint{color:var(--mut);font-size:12px}.ok{color:#2e7d4f}.bad{color:#a63d3d}textarea{width:100%;margin-top:10px;min-height:40px;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px}
#ov{position:fixed;inset:0;background:#0b0b0b;display:none;align-items:center;justify-content:center;z-index:5}#ov img{max-width:98vw;max-height:98vh}
@media (max-width:900px){.row{grid-template-columns:repeat(2,1fr)}}
</style></head><body><header><b>C106 · due coppie e una sola</b><button id="p">←</button><select id="s"></select><button id="n">→</button>
<span id="st" class="hint"></span><button id="e">Esporta CSV</button>
<span class="hint">Due coppie fatte con la stessa modifica e un'immagine da sola: segna 1, 1, 2, 2 e "sola". Clic sull'immagine = schermo intero (← → per scorrere, Esc chiude).</span></header>
<main id="m"></main><div id="ov"><img id="oi"></div><script>
const D=__DATA__,K="c106_labels_v1";let M={};try{M=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
const save=()=>{try{localStorage.setItem(K,JSON.stringify(M))}catch(e){}},valid=a=>a&&a.filter(x=>x=="1").length==2&&a.filter(x=>x=="2").length==2&&a.filter(x=>x=="sola").length==1;
let i=0,ov=-1;const S=document.getElementById("s");D.forEach((d,k)=>{const o=document.createElement("option");o.value=k;S.appendChild(o)});
function lab(){[...S.options].forEach((o,k)=>o.textContent=(valid((M[D[k].id]||{}).a)?"✓ ":"")+"Prova "+(k+1));document.getElementById("st").textContent=D.filter(d=>valid((M[d.id]||{}).a)).length+" / "+D.length+" complete"}
function show(k){i=(k+D.length)%D.length;S.value=i;const d=D[i],m=M[d.id]=M[d.id]||{a:[null,null,null,null,null],note:""};
let h=`<h2>Prova ${i+1}</h2><div class="row">`;d.ims.forEach((im,j)=>{const v=m.a[j];h+=`<div class="c ${v=="1"?"g1":v=="2"?"g2":v=="sola"?"g3":""}"><img src="${im.t}" data-j="${j}"><div class="b">`+["1","2","sola"].map(x=>`<button data-j="${j}" data-v="${x}" class="${v==x?"on":""}">${x}</button>`).join("")+`</div></div>`});
h+=`</div><p class="${valid(m.a)?"ok":"bad"}">${valid(m.a)?"risposta completa":"servono due «1», due «2» e una «sola»"}</p><textarea placeholder="appunti…">${m.note||""}</textarea>`;
document.getElementById("m").innerHTML=h;document.querySelectorAll(".b button").forEach(b=>b.onclick=()=>{m.a[+b.dataset.j]=b.dataset.v;save();show(i)});
document.querySelectorAll(".c img").forEach(im=>im.onclick=()=>{ov=+im.dataset.j;paint()});document.querySelector("textarea").oninput=e=>{m.note=e.target.value;save()};lab()}
function paint(){const O=document.getElementById("ov");if(ov<0){O.style.display="none";return}O.style.display="flex";document.getElementById("oi").src=D[i].ims[ov].f}
document.getElementById("ov").onclick=()=>{ov=-1;paint()};
document.addEventListener("keydown",e=>{if(e.target.tagName=="TEXTAREA")return;if(ov>=0){if(e.key=="Escape"){ov=-1}else if(e.key=="ArrowRight"){ov=(ov+1)%5}else if(e.key=="ArrowLeft"){ov=(ov+4)%5}paint();return}
if(e.key=="ArrowRight")show(i+1);if(e.key=="ArrowLeft")show(i-1)});
document.getElementById("p").onclick=()=>show(i-1);document.getElementById("n").onclick=()=>show(i+1);S.onchange=()=>show(+S.value);
document.getElementById("e").onclick=()=>{let t="trial,a1,a2,a3,a4,a5,note\n";D.forEach(d=>{const m=M[d.id]||{a:[]};t+=[d.id,...[0,1,2,3,4].map(j=>m.a[j]||""),'"'+String(m.note||"").replace(/"/g,'""')+'"'].join(",")+"\n"});
const l=document.createElement("a");l.href=URL.createObjectURL(new Blob([t],{type:"text/csv"}));l.download="odd_one_out_labels.csv";l.click()};show(0);
</script></body></html>"""


def partition(labels):
    g1 = frozenset(j for j, x in enumerate(labels) if x == "1"); g2 = frozenset(j for j, x in enumerate(labels) if x == "2")
    single = [j for j, x in enumerate(labels) if x == "sola"]
    return frozenset([g1, g2]), (single[0] if single else None)


def binom_p(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def score(key, labels):
    lab = {r["trial"]: [r[f"a{j}"].strip() for j in range(1, 6)] for r in labels}
    res = []
    for k in key:
        a = lab.get(k["trial"])
        imgs = [it.split(":") for it in k["images"].split()]
        if not a or sorted(a) != ["1", "1", "2", "2", "sola"]:
            continue
        pairs, single = partition(a)
        truth = frozenset([frozenset(j for j, it in enumerate(imgs) if it[0] == "A"), frozenset(j for j, it in enumerate(imgs) if it[0] == "B")])
        bys = frozenset([frozenset(j for j, it in enumerate(imgs) if it[2] == k["s1"] and it[0] != "C"), frozenset(j for j, it in enumerate(imgs) if it[2] == k["s2"] and it[0] != "C")])
        cidx = [j for j, it in enumerate(imgs) if it[0] == "C"][0]
        res.append({**k, "exact": int(pairs == truth), "by_seed": int(pairs == bys), "single": int(single == cidx),
                    "pairs_ok": sum(p in truth for p in pairs)})
    return res


def kind_of(r):
    a, b = r["A"], r["B"]
    if r["set"] == "TE":
        if a[0] == "R" and b[0] == "R" and a[:3] == b[:3]:
            return "TE two random pushes, same layer"
        if (a[0] == "L") != (b[0] == "L"):
            return "TE edit against random"
        return "TE other"
    fa, fb = a.split("_")[0], b.split("_")[0]
    return "DiT same family" if fa == fb else "DiT different families"


def rules(key, labels):
    R = score(key, labels); first = [r for r in R if str(r["repeat"]) == "0"]; out = []
    def line(sel, name, thr, alpha):
        x = [r for r in first if sel(r)]; n = len(x); k = sum(r["exact"] for r in x)
        if not n:
            return
        p = binom_p(k, n, 1 / 15); share = k / n
        out.append({"test": f"Rule 1 {name}: exact sorting", "value": f"{k}/{n} = {share:.2f}; binomial p {p:.2g} vs 1/15",
                    "verdict": ("the eye sorts by perturbation" if share >= thr and p < alpha else "not shown")})
    line(lambda r: True, "all", 0.50, 0.001); line(lambda r: r["set"] == "TE", "TE set", 0.40, 0.01); line(lambda r: r["set"] == "DiT", "DiT set", 0.40, 0.01)
    n = len(first)
    out.append({"test": "Rule 2 answers equal to the seed partition (reported)", "value": f"{sum(r['by_seed'] for r in first)}/{n} (chance 1/15)", "verdict": ""})
    out.append({"test": "Rule 3 single picture found (reported)", "value": f"{sum(r['single'] for r in first)}/{n} (chance 1/5)", "verdict": ""})
    out.append({"test": "Rule 3 pairs correct (reported)", "value": f"{sum(r['pairs_ok'] for r in first)}/{2 * n}", "verdict": ""})
    kinds = {}
    for r in first:
        kinds.setdefault(kind_of(r), []).append(r["exact"])
    out.append({"test": "Rule 3 exact by kind of A-B pair (reported)", "value": "; ".join(f"{k} {sum(v)}/{len(v)}" for k, v in sorted(kinds.items())), "verdict": ""})
    reps = [r for r in R if str(r["repeat"]) == "1"]
    if reps:
        firsts = {(r["set"], r["prompt"], r["A"], r["B"], r["C"], r["s1"], r["s2"], r["s3"]): r for r in first}
        same = sum(firsts.get((r["set"], r["prompt"], r["A"], r["B"], r["C"], r["s1"], r["s2"], r["s3"]), {}).get("exact") == r["exact"] for r in reps)
        out.append({"test": "Rule 3 test-retest, exact (reported)", "value": f"{same}/{len(reps)} same outcome", "verdict": ""})
    return out


def selftest():
    key = trials(); assert len(key) == 32 and sum(int(k["repeat"]) for k in key) == 4
    assert abs(binom_p(1, 1, 1 / 15) - 1 / 15) < 1e-12
    # all partitions of 5 into 2 pairs + 1: 15
    parts = set()
    for lab in set(itertools.permutations(["1", "1", "2", "2", "sola"])):
        parts.add(partition(list(lab)))
    assert len(parts) == 15, len(parts)
    def answer(k, how):
        imgs = [it.split(":") for it in k["images"].split()]
        if how == "truth":
            return ["1" if g == "A" else "2" if g == "B" else "sola" for g, _, _ in imgs]
        return ["sola" if g == "C" else ("1" if s == k["s1"] else "2") for g, _, s in imgs]
    for how, want in (("truth", "the eye sorts by perturbation"), ("seed", "not shown")):
        lab = [{"trial": k["trial"], **{f"a{j + 1}": x for j, x in enumerate(answer(k, how))}} for k in key]
        o = rules(key, lab); assert o[0]["verdict"] == want, (how, o[0])
        if how == "seed":
            assert o[3]["value"].startswith("28/28"), o[3]
    for k in key:
        for it in k["images"].split():
            g, c, s = it.split(":")
            assert (T.img_root() / path(k["set"], k["prompt"], c, s)).exists(), (k, it)
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "page", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.page: page()
    if a.rules:
        out = rules(list(csv.DictReader(open(KEY, encoding="utf-8"))), list(csv.DictReader(open(LABELS, encoding="utf-8"))))
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
