"""C65 — do text-encoder edits move different characters the same way? (docs/prereg_te_characters.md)
Written 2026-10-11, before any render. Renders authorised by Alessandro.

  python te_characters.py --plan            # data/te_characters_plan.csv (the 20 edits are chosen by rule from C64 phase 1)
  python te_characters.py --queue --first 1 # the reproduction render only
  python te_characters.py --repro           # must print REPRO PASS max abs diff 0
  python te_characters.py --queue           # everything else
  python te_characters.py --count           # expected N missing 0
  python te_characters.py --features        # data/te_characters_style_features.csv (23 style statistics)
  python te_characters.py --faces           # data/te_characters_faces.csv (ArcFace buffalo_l, BRISQUE, CLIP-IQA; GPU PC)
  python te_characters.py --page            # eye page + data/te_characters_eye_key.csv (key committed before labels)
  python te_characters.py --test            # the decision rules (Claude runs it)
  python te_characters.py --selftest        # the rules on synthetic data

Characters, prompt frame and baselines are those of C52 (experiments/portraits.py, benchmark_portraits/phase_c):
seven Western-comics portraits, seeds 2645751 and 3316624. The baselines are reused, after one render through
this script's workflow reproduces one of them pixel for pixel.
"""
import argparse, csv, itertools, json, os, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import portraits as P
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_characters_plan.csv"
FEAT = DATA / "te_characters_style_features.csv"
FACES = DATA / "te_characters_faces.csv"
KEY = DATA / "te_characters_eye_key.csv"
LABELS = DATA / "te_characters_eye_alessandro.csv"
RESULT = DATA / "te_characters_tests.csv"
FOLDER = "benchmark_te_characters"
BASE_FOLDER = P.FOLDER_C
CHARS = list(P.CALIBRATION) + list(P.HELD_OUT)
SEEDS = P.SEEDS_C[:2]          # 2645751, 3316624
ID_SEEDS = P.SEEDS_C           # all four phase C baselines, for ID_seed
PARTS = {"attn": TP.ATTN, "mlp": TP.MLP}


def select_edits():
    """The rule, fixed in the pre-registration: C64 phase-1 layer edits (attention or MLP, dose +-1.00) that Alessandro
    judged a medium or strong change, with the overall style changed, and the surface as the original or cleaner."""
    out = []
    for r in csv.DictReader(open(DATA / "te_pilot_phase1_joined.csv", encoding="utf-8")):
        if (r["phase"] == "main" and r["part"] in PARTS and r["entita"] in ("media", "forte")
                and r["stile"] == "cambiato" and r["dmg"] in ("pulito", "come")):
            out.append((int(r["unit"][1:]), r["part"], 1.0 if r["sign"] == "+" else -1.0, r["cond"]))
    return sorted(out)


def path(ch, cond, seed):
    if cond == "baseline":
        return c47.IMG_ROOT / BASE_FOLDER / f"{ch}_baseline_krea2_seed{seed}_00001_.png"
    return c47.IMG_ROOT / FOLDER / f"{ch}_{cond}_krea2_seed{seed}_00001_.png"


def make_plan():
    edits = select_edits()
    rows = []
    def add(ch, seed, cond, te_json, phase, unit="", part="", dose=0.0):
        prefix = f"{ch}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "phase": phase, "char": ch, "seed": seed, "cond": cond, "unit": unit, "part": part,
                     "dose": dose, "te_granular_json": te_json, "vectors_override": "",
                     "prompt_text": P.text({**P.CALIBRATION, **P.HELD_OUT}[ch]), "output_prefix": prefix,
                     "expected_filename": f"{prefix}_00001_.png", **P.SETTINGS})
    add(CHARS[0], SEEDS[0], "REPRO_baseline", "", "check")
    for ch in CHARS:
        add(ch, SEEDS[0], "CHK_null_L35_both_p1.00", TP.gj_te(35, TP.ATTN + TP.MLP, 1.0), "check", "L35", "both", 1.0)
    for L, part, d, cond in edits:
        for ch in CHARS:
            for seed in SEEDS:
                add(ch, seed, cond, TP.gj_te(L, PARTS[part], d), "main", f"L{L:02d}", part, d)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("edits:", len(edits), [e[3] for e in edits])
    print("plan rows:", len(rows))


def plan():
    return list(csv.DictReader(open(PLAN, encoding="utf-8")))


def workflow(r):
    wf = TP.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(first):
    n = 0
    for r in plan()[: first or None]:
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
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


def repro():
    r = plan()[0]
    d = int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(path(r["char"], "baseline", r["seed"]))).max())
    print("REPRO", "PASS" if d == 0 else "FAIL - stop", "max abs diff", d)
    nulls = [r for r in plan() if r["cond"].startswith("CHK_null")]
    have = [r for r in nulls if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    if have:
        dn = [int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(path(r["char"], "baseline", r["seed"]))).max()) for r in have]
        print("null L35 (reported):", len(have), "renders, max abs diff", dn)


def count():
    rows = plan()
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    base_miss = [str(path(c, "baseline", s)) for c in CHARS for s in ID_SEEDS if not path(c, "baseline", s).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5], "| reused baselines missing", len(base_miss))


def main_conds():
    seen = []
    for r in plan():
        if r["phase"] == "main" and r["cond"] not in seen:
            seen.append(r["cond"])
    return seen


# ---------------------------------------------------------------- measurement
def features():
    from style_features import extract_all_features
    done = set()
    if FEAT.exists():
        done = {(r["char"], r["cond"], r["seed"]) for r in csv.DictReader(open(FEAT))}
    items = [(c, "baseline", s) for c in CHARS for s in SEEDS] + [(c, k, s) for k in main_conds() for c in CHARS for s in SEEDS]
    new = not FEAT.exists()
    with open(FEAT, "a", newline="") as fh:
        w = None
        for ch, cond, seed in items:
            if (ch, cond, seed) in done:
                continue
            f = extract_all_features(str(path(ch, cond, seed)))
            row = {"char": ch, "cond": cond, "seed": seed, **{k: v for k, v in f.items() if k not in ("file", "width_px", "height_px")}}
            if w is None:
                w = csv.DictWriter(fh, fieldnames=list(row))
                if new:
                    w.writeheader()
            w.writerow(row); fh.flush()
    print("features ok")


def faces():
    import torch, piq
    from PIL import Image
    from insightface.app import FaceAnalysis
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    app.prepare(ctx_id=0 if dev == "cuda" else -1, det_size=(640, 640))
    ciqa = piq.CLIPIQA(data_range=1.).to(dev)
    items = [(c, "baseline", s) for c in CHARS for s in ID_SEEDS] + [(c, k, s) for k in main_conds() for c in CHARS for s in SEEDS]
    out = []
    for ch, cond, seed in items:
        im = Image.open(path(ch, cond, seed)).convert("RGB")
        fs = app.get(np.asarray(im)[:, :, ::-1].copy())
        if fs:
            f = max(fs, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
            emb, det, sc = f.normed_embedding, 1, float(f.det_score)
        else:
            emb, det, sc = np.zeros(512), 0, 0.0
        x = torch.from_numpy(np.asarray(im.resize((512, 640), Image.BICUBIC), dtype=np.float32) / 255.).permute(2, 0, 1)[None].to(dev)
        out.append({"char": ch, "cond": cond, "seed": seed, "detected": det, "det_score": round(sc, 4),
                    "brisque": round(float(piq.brisque(x, data_range=1.)), 4), "clipiqa": round(float(ciqa(x).mean()), 5),
                    "emb": " ".join(f"{v:.6f}" for v in emb)})
    with open(FACES, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("faces ok:", sum(r["detected"] for r in out), "of", len(out), "with a face")


# ---------------------------------------------------------------- rules (fixed in the pre-registration)
cos = lambda x, y: float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-12))


def rules(F, E, det, conds, chars=CHARS, seeds=SEEDS, id_seeds=ID_SEEDS):
    B = np.array([F[(c, "baseline", s)] for c in chars for s in seeds])
    sd = B.std(axis=0, ddof=1); sd[sd == 0] = 1
    per = []
    for k in conds:
        dF = {(c, s): (F[(c, k, s)] - F[(c, "baseline", s)]) / sd for c in chars for s in seeds}
        S = [cos(dF[(c, seeds[0])], dF[(c, seeds[1])]) for c in chars]
        W = [cos(dF[(a, s)], dF[(b, s)]) for s in seeds for a, b in itertools.combinations(chars, 2)]
        mS, mW = float(np.median(S)), float(np.median(W))
        verdict = "uninformative" if mS < 0.50 else ("coherent" if mW >= 0.40 else "incoherent" if mW < 0.25 else "unclear")
        # identity, reported: characters with a face in all their images
        idrow = []
        for c in chars:
            imgs = [(c, "baseline", s) for s in id_seeds] + [(c, k, s) for s in seeds]
            if not all(det.get(x, 0) for x in imgs):
                continue
            id_seed = np.mean([float(E[(c, "baseline", a)] @ E[(c, "baseline", b)]) for a, b in itertools.combinations(id_seeds, 2)])
            id_edit = np.median([float(E[(c, "baseline", s)] @ E[(c, k, s)]) for s in seeds])
            idrow.append(id_edit > id_seed)
        per.append({"cond": k, "median_S": round(mS, 3), "median_W": round(mW, 3), "verdict": verdict,
                    "id_eligible": len(idrow), "id_kept": int(sum(idrow))})
    n = len(per)
    inf = [p for p in per if p["verdict"] != "uninformative"]
    coh = sum(p["verdict"] == "coherent" for p in per)
    if len(inf) < n / 2:
        overall = "uninformative (more than half the edits disagree with themselves across seeds)"
    else:
        overall = "supported" if coh >= np.ceil(2 * n / 3) else "refuted" if coh <= np.floor(n / 3) else "inconclusive"
    return per, {"n_edits": n, "informative": len(inf), "coherent": coh,
                 "incoherent": sum(p["verdict"] == "incoherent" for p in per), "H1": overall}


def load():
    F = {(r["char"], r["cond"], r["seed"]): np.array([float(v) for k, v in r.items() if k not in ("char", "cond", "seed")])
         for r in csv.DictReader(open(FEAT))}
    E, det = {}, {}
    for r in csv.DictReader(open(FACES)):
        key = (r["char"], r["cond"], r["seed"])
        E[key] = np.array([float(v) for v in r["emb"].split()]); det[key] = int(r["detected"])
    return F, E, det


def test():
    F, E, det = load()
    per, tot = rules(F, E, det, main_conds())
    with open(RESULT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(per[0])); w.writeheader(); w.writerows(per)
    for p in per:
        print(p)
    print(tot)


def selftest():
    rng = np.random.default_rng(0)
    chars, seeds, ids = [f"c{i}" for i in range(7)], ["s1", "s2"], ["s1", "s2", "s3", "s4"]
    F, E, det = {}, {}, {}
    for c in chars:
        for s in ids:
            F[(c, "baseline", s)] = rng.normal(size=23); E[(c, "baseline", s)] = (v := rng.normal(size=512)) / np.linalg.norm(v); det[(c, "baseline", s)] = 1
    shared = rng.normal(size=23) * 3
    for k, kind in (("same", "shared"), ("random", "random")):
        for c in chars:
            for s in seeds:
                F[(c, k, s)] = F[(c, "baseline", s)] + (shared + rng.normal(size=23) * 0.3 if kind == "shared" else rng.normal(size=23) * 3)
                E[(c, k, s)] = E[(c, "baseline", s)]; det[(c, k, s)] = 1
    per, tot = rules(F, E, det, ["same", "random"], chars, seeds, ids)
    assert per[0]["verdict"] == "coherent" and per[1]["verdict"] in ("incoherent", "uninformative"), per
    assert per[0]["id_kept"] == 7, per
    print("selftest ok", per, tot)


# ---------------------------------------------------------------- eye page: one sheet per edit x seed
def page():
    """Sheet = the 7 characters, baseline row above, edit row below; anonymous id, shuffled (rng 66), 6 repeats.
    Questions: do the seven change in the same direction (yes / partly / no); which direction (free);
    surface against the originals (cleaner / as / slight / medium / strong). Key written before any label."""
    from PIL import Image
    rng = np.random.default_rng(66)
    out = c47.IMG_ROOT / FOLDER / "eye_test"; out.mkdir(parents=True, exist_ok=True)
    sheets = [(k, s) for k in main_conds() for s in SEEDS]
    ids = rng.permutation(np.arange(100, 999))[: len(sheets)]
    items = [{"id": f"x{i}", "cond": k, "seed": s} for (k, s), i in zip(sheets, ids)]
    W, H = 300, 375
    for x in items:
        dst = out / f"{x['id']}.jpg"
        if dst.exists():
            continue
        canvas = Image.new("RGB", (W * 7, H * 2), "white")
        for j, ch in enumerate(CHARS):
            canvas.paste(Image.open(path(ch, "baseline", x["seed"])).convert("RGB").resize((W, H), Image.LANCZOS), (j * W, 0))
            canvas.paste(Image.open(path(ch, x["cond"], x["seed"])).convert("RGB").resize((W, H), Image.LANCZOS), (j * W, H))
        canvas.save(dst, quality=90)
    show = [x["id"] for x in items]; rng.shuffle(show)
    rep = list(rng.choice(show, 6, replace=False))
    for x in rep:
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), x)
    with open(KEY, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["item", "cond", "seed", "repeated"])
        for x in items:
            w.writerow([x["id"], x["cond"], x["seed"], int(x["id"] in rep)])
    slots = [f"{s}#{k}" for k, s in enumerate(show)]
    (out / "eye_test.html").write_text(EYE.replace("__SLOTS__", json.dumps(slots)), encoding="utf-8")
    print(len(items), "sheets,", len(slots), "showings ->", out / "eye_test.html")


EYE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>C65: stessi cambi su personaggi diversi?</title>
<style>body{margin:0;background:#1d1d1f;color:#eee;font:14px system-ui,sans-serif}#wrap{display:flex;flex-direction:column;height:100vh}
#view{flex:1;overflow:auto;background:#000;text-align:center}#view img{max-width:100%;max-height:100%}#view.zoom img{max-width:none;max-height:none}
#side{background:#2a2a2d;padding:8px 12px}.r{display:flex;align-items:center;gap:6px;padding:3px 6px;border-radius:6px;border:2px solid transparent;flex-wrap:wrap}
.r>span{min-width:330px}.r.cur{border-color:#ffcc55;background:#3a3524}button{font:13px system-ui;padding:3px 8px;border-radius:6px;border:1px solid #555;background:#333;color:#ddd}
button.on{background:#2f4f3a;border-color:#6a8;color:#fff}textarea{flex:1;min-width:300px;background:#222;color:#eee;border:1px solid #555;border-radius:6px;font:13px system-ui}
kbd{font:12px ui-monospace,monospace;background:#444;border:1px solid #666;border-radius:4px;padding:0 4px}#n{color:#aaa}</style></head><body><div id="wrap">
<div id="view"><img id="im"></div><div id="side"><div id="n"></div>
<small>Riga sopra: i 7 originali. Riga sotto: la stessa modifica su ciascuno. <kbd>↑</kbd><kbd>↓</kbd> voce · <kbd>←</kbd><kbd>→</kbd> valore · <kbd>Invio</kbd> avanti · <kbd>⌫</kbd> indietro · <kbd>z</kbd> zoom</small>
<div id="rows"></div><button id="exp">Scarica le risposte</button></div></div>
<script>
const S=__SLOTS__,K="te_characters_eye_v1";let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;try{i=Math.min(+localStorage.getItem(K+"_i")||0,S.length-1)}catch(e){}const $=q=>document.querySelector(q);
const R=[{k:"stessa",lab:"i 7 personaggi cambiano nella stessa direzione?",o:[["si","sì"],["parte","in parte"],["no","no"]],d:""},
 {k:"direzione",lab:"quale direzione (stile, colori, forme…)",txt:1},
 {k:"dmg",lab:"superficie rispetto agli originali",o:[["pulito","più pulita"],["come","come"],["lieve","peggio: lieve"],["medio","medio"],["forte","forte"]],d:"come"},
 {k:"note",lab:"altro (libero)",txt:1}];
let c=0;$("#rows").innerHTML=R.map((r,j)=>r.txt?`<div class="r" id="r${j}"><span>${r.lab}</span><textarea rows="1" data-j="${j}"></textarea></div>`:
 `<div class="r" id="r${j}"><span>${r.lab}</span>`+r.o.map(([v,l])=>`<button data-j="${j}" data-v="${v}">${l}</button>`).join("")+`</div>`).join("");
function cur(){return A[S[i]]||(A[S[i]]={})}
function save(){try{localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_i",i)}catch(e){}}
function show(){const a=A[S[i]]||{};$("#im").src=S[i].split("#")[0]+".jpg";
 $("#n").textContent=`foglio ${i+1} di ${S.length} · completati ${S.filter(s=>A[s]&&A[s].stessa).length}`;
 R.forEach((r,j)=>{const el=$("#r"+j);el.classList.toggle("cur",j===c);if(r.txt){const t=el.querySelector("textarea");if(document.activeElement!==t)t.value=a[r.k]||"";return}
  el.querySelectorAll("button").forEach(b=>b.classList.toggle("on",(a[r.k]||r.d)===b.dataset.v))});save()}
function step(d){const r=R[c];if(r.txt){if(d>0)$("#r"+c+" textarea").focus();return}const vs=r.o.map(x=>x[0]);let k=vs.indexOf(cur()[r.k]||r.d);
 k=k<0?(d>0?0:vs.length-1):Math.max(0,Math.min(vs.length-1,k+d));cur()[r.k]=vs[k];show()}
document.querySelectorAll("button[data-j]").forEach(b=>b.onclick=()=>{c=+b.dataset.j;cur()[R[c].k]=b.dataset.v;show()});
document.querySelectorAll("textarea").forEach(t=>{t.onfocus=()=>{c=+t.dataset.j;show()};t.oninput=()=>{cur()[R[+t.dataset.j].k]=t.value;save()}});
addEventListener("keydown",e=>{if(e.target.tagName==="TEXTAREA"){if(["Escape","ArrowUp","ArrowDown"].includes(e.key)){e.preventDefault();e.target.blur();
  if(e.key!=="Escape"){c=Math.max(0,Math.min(R.length-1,c+(e.key==="ArrowDown"?1:-1)));show()}}return}
 if(e.key==="ArrowDown"){e.preventDefault();c=Math.min(R.length-1,c+1);show()}else if(e.key==="ArrowUp"){e.preventDefault();c=Math.max(0,c-1);show()}
 else if(e.key==="ArrowRight"){e.preventDefault();step(1)}else if(e.key==="ArrowLeft"){e.preventDefault();step(-1)}
 else if(e.key==="Enter"){e.preventDefault();if(i<S.length-1){i++;c=0;show()}}else if(e.key==="Backspace"){e.preventDefault();if(i>0){i--;c=0;show()}}
 else if(e.key.toLowerCase()==="z")$("#view").classList.toggle("zoom")});
const q=v=>'"'+String(v||"").replace(/"/g,'""').replace(/\n/g," ")+'"';
$("#exp").onclick=()=>{let t="slot,stessa,direzione,dmg,note\n";S.forEach(s=>{const a=A[s]||{};t+=[s,a.stessa||"",q(a.direzione),a.stessa?(a.dmg||"come"):"",q(a.note)].join(",")+"\n"});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="te_characters_eye_alessandro.csv";l.click()};
show();
</script></body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "repro", "count", "features", "faces", "page", "test", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.repro: repro()
    if a.count: count()
    if a.features: features()
    if a.faces: faces()
    if a.page: page()
    if a.test: test()
    if a.selftest: selftest()
