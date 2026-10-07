"""C60 — form edits vs surface edits on comic prompts (docs/prereg_comic_form_test.md).
Written 2026-10-07, before any render. Renders authorised by Alessandro bench by bench.

  python comic_form_test.py --plan            # data/comic_form_plan.csv: 2 checks + 9 baselines + 180 edits
  python comic_form_test.py --queue --checks  # the two checks only
  python comic_form_test.py --check           # both must be identical to the pixel
  python comic_form_test.py --queue           # everything else
  python comic_form_test.py --count           # expected 191 missing 0
  (after the renders, separately committed: --page, --measure, --tally)

FORM set = the 10 sheets of the C59 eye pass praised for the comic (fixed rule, docs/split_atlas_eye_result.md
addendum). SURFACE set = 10 drawn with rng 60 from the 16 C59 sheets labelled noise >= medio with no structural
class, block >= 20, not partial. Both at dose 0.35, Real Value, through granular_json. New prompts, new seeds.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import split_atlas as sa

DATA = HERE.parent / "data"
PLAN = DATA / "comic_form_plan.csv"
FOLDER = "benchmark_comic_form"
DOSE = 0.35
SEEDS = ["1618033", "1414213", "2236067"]
PROMPTS = {"P02": "blk16_ladder_plan.csv", "P1_elfbrawler": "single_blocks_v3_conservative_plan.csv",
           "F1cartoon_fisherman": "prompt_family_plan.csv"}
MATS = {"attn": sa.PARTS["attn"], "mlp": sa.PARTS["mlp"], "whole": sa.PARTS["attn"] + sa.PARTS["mlp"]}
ZERO = sa.ZERO


def edit_sets():
    import numpy as np
    g = list(csv.DictReader(open(DATA / "split_atlas_eye_praise_vs_layout.csv", encoding="utf-8")))
    t = {r["sheet"]: r for r in csv.DictReader(open(DATA / "split_atlas_eye_tally_alessandro.csv", encoding="utf-8"))}
    form = [(int(r["block"]), r["part"], r["sign"]) for r in g if r["group"] == "praised"]
    pool = [(int(r["block"]), r["part"], r["sign"]) for r in g
            if r["group"] == "noise_ge2_only" and int(r["block"]) >= 20 and t[r["sheet"]]["partial"] == "0"]
    pool.sort()
    idx = np.random.default_rng(60).choice(len(pool), 10, replace=False)
    surface = [pool[i] for i in sorted(idx)]
    return sorted(form), surface, pool


def gj(block, part, sign):
    d = DOSE if sign == "pos" else -DOSE
    return json.dumps({f"blocks.{block}.{m}.weight": d for m in MATS[part]})


def make_plan():
    form, surface, pool = edit_sets()
    print("FORM", form); print("SURFACE", surface); print("pool", len(pool))
    base = {}
    for pid, f in PROMPTS.items():
        for r in csv.DictReader(open(DATA / f, encoding="utf-8")):
            if (r.get("prompt_id") or r.get("prompt")) == pid:
                base[pid] = r; break
    ref = list(csv.DictReader(open(sa.PLAN, encoding="utf-8")))[0]
    rows = []
    def add(pid, text, seed, cond, g, phase, group):
        prefix = f"{pid}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "phase": phase, "group": group, "prompt_id": pid, "seed": seed, "cond": cond,
                     "vectors_override": ZERO if g else "", "granular_json": g, "prompt_text": text, "output_prefix": prefix,
                     "expected_filename": f"{prefix}_00001_.png",
                     **{k: ref[k] for k in ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")}})
    f4 = next(r for r in csv.DictReader(open(sa.PLAN, encoding="utf-8")) if r["prompt_id"] == "F4_closeup")["prompt_text"]
    add("F4_closeup", f4, "2718281", "CHK_split_blk19_mlp_pos_d0.350", gj(19, "mlp", "pos"), "check", "check")
    add("F4_closeup", f4, "2718281", "CHK_whole_blk08_pos_d0.350", gj(8, "whole", "pos"), "check", "check")
    for seed in SEEDS:
        for pid in PROMPTS:
            add(pid, base[pid]["prompt_text"], seed, "baseline", "", "main", "baseline")
            for grp, lst in (("form", form), ("surface", surface)):
                for b, p, s in lst:
                    add(pid, base[pid]["prompt_text"], seed, f"blk{b:02d}_{p}_{s}_d{DOSE:.3f}", gj(b, p, s), "main", grp)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["granular_json"]:
        wf["50"]["inputs"]["granular_json"] = r["granular_json"]
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


def check():
    import numpy as np
    from PIL import Image
    im = lambda p: np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
    f = lambda c: c47.IMG_ROOT / FOLDER / f"F4_closeup_{c}_krea2_seed2718281_00001_.png"
    a = int(np.abs(im(f("CHK_split_blk19_mlp_pos_d0.350")) - im(sa.f_split("F4_closeup", "2718281", "blk19_mlp_pos_d0.350"))).max())
    b = int(np.abs(im(f("CHK_whole_blk08_pos_d0.350")) - im(sa.f_atlas("F4_closeup", "blk08_pos_d0.350"))).max())
    print(f"REPRO split blk19 mlp + vs C59: max abs diff {a}")
    print(f"WHOLE via granular blk08 + vs equal-dose atlas: max abs diff {b}")
    print("CHECK", "PASS" if a == 0 and b == 0 else "FAIL - stop")


KEY = DATA / "comic_form_eye_key.csv"
LABELS = DATA / "comic_form_eye_alessandro.csv"


def f(pid, seed, cond):
    return c47.IMG_ROOT / FOLDER / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"


def page():
    """Blind pairs: edit vs its baseline, side random (rng 61), 180 pairs + 15 repeats."""
    import numpy as np
    from PIL import Image
    rng = np.random.default_rng(61)
    out = c47.IMG_ROOT / FOLDER / "eye_test"; out.mkdir(exist_ok=True)
    rows = [r for r in csv.DictReader(open(PLAN, encoding="utf-8")) if r["group"] in ("form", "surface")]
    ids = rng.permutation(np.arange(1000, 9999))[: len(rows)]
    pairs = []
    for r, i in zip(rows, ids):
        left = rng.choice(["edit", "base"])
        pairs.append({"id": f"p{i}", "prompt": r["prompt_id"], "seed": r["seed"], "cond": r["cond"], "group": r["group"], "left": left})
    show = [p["id"] for p in pairs]; rng.shuffle(show)
    rep = list(rng.choice(show, 15, replace=False))
    for x in rep:
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), x)
    for p in pairs:
        dst = out / f"{p['id']}.jpg"
        if dst.exists():
            continue
        e, b = f(p["prompt"], p["seed"], p["cond"]), f(p["prompt"], p["seed"], "baseline")
        L, R = (e, b) if p["left"] == "edit" else (b, e)
        S = Image.new("RGB", (2 * 1024 + 12, 1280), (30, 30, 30))
        S.paste(Image.open(L).convert("RGB"), (0, 0)); S.paste(Image.open(R).convert("RGB"), (1036, 0))
        S.save(dst, "JPEG", quality=92, subsampling=0)
    with open(KEY, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["pair", "prompt", "seed", "cond", "group", "left", "repeated"])
        for p in pairs:
            w.writerow([p["id"], p["prompt"], p["seed"], p["cond"], p["group"], p["left"], int(p["id"] in rep)])
    slots = [f"{x}#{k}" for k, x in enumerate(show)]
    (out / "eye_test.html").write_text(PAGE.replace("__SLOTS__", json.dumps(slots)), encoding="utf-8")
    print(len(pairs), "pairs,", len(slots), "showings ->", out / "eye_test.html")


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Fumetto: A contro B</title>
<style>
body{margin:0;background:#1d1d1f;color:#eee;font:15px system-ui,sans-serif}
#wrap{display:flex;gap:12px;padding:8px;box-sizing:border-box;height:100vh}
#view{flex:1;overflow:auto;background:#000;border-radius:8px;cursor:zoom-in;position:relative}
#view.zoom{cursor:zoom-out}#view img{width:100%;display:block}#view.zoom img{width:auto;max-width:none}
#lab{display:flex;justify-content:space-around;font-weight:700;font-size:20px;padding:4px;background:#000;position:sticky;top:0}
#side{width:360px;overflow:auto;background:#2a2a2d;border-radius:8px;padding:12px;box-sizing:border-box}
.q{border-top:1px solid #444;padding:8px 0}.q b{display:block;margin-bottom:4px}
button{font:14px system-ui;padding:6px 11px;margin:2px;border-radius:7px;border:1px solid #666;background:#333;color:#eee;cursor:pointer}
button.on{background:#3b6e4f;border-color:#6c6}#n{color:#aaa;margin-bottom:6px}small{color:#aaa}
</style></head><body><div id="wrap"><div id="view"><div id="lab"><span>A</span><span>B</span></div><img id="im"></div>
<div id="side"><div id="n"></div><small>Clic sull'immagine: zoom 100%. Degrado = grana, chiazze, retino, collasso.</small>
<div class="q"><b>Quale preferisci per questo stile?</b>__P__</div>
<div class="q"><b>Degrado di superficie in A</b>__DA__</div>
<div class="q"><b>Degrado di superficie in B</b>__DB__</div>
<div class="q"><b>Quanto &egrave; cambiata l'immagine tra A e B?</b>__CH__</div>
<div class="q"><button id="prev">&larr;</button><button id="next">&rarr;</button><button id="exp">Scarica le risposte</button></div></div></div>
<script>
const S=__SLOTS__,K="comic_form_eye_v1",Q=["pref","dA","dB","ch"];let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;try{i=Math.min(+localStorage.getItem(K+"_i")||0,S.length-1)}catch(e){}const $=q=>document.querySelector(q);
function save(){try{localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_i",i)}catch(e){}}
const done=a=>a&&Q.every(q=>a[q]);
function show(){const a=A[S[i]]||{};$("#im").src=S[i].split("#")[0]+".jpg";
 $("#n").textContent=`coppia ${i+1} di ${S.length} · completate ${S.filter(s=>done(A[s])).length}`;
 document.querySelectorAll("button[data-q]").forEach(b=>b.classList.toggle("on",a[b.dataset.q]===b.dataset.v));save()}
document.querySelectorAll("button[data-q]").forEach(b=>b.onclick=()=>{const s=S[i];A[s]=A[s]||{};A[s][b.dataset.q]=b.dataset.v;show();
 if(done(A[s])&&i<S.length-1)setTimeout(()=>{i++;show();$("#view").scrollTo(0,0)},300)});
$("#prev").onclick=()=>{if(i>0){i--;show()}};$("#next").onclick=()=>{if(i<S.length-1){i++;show()}};
$("#view").onclick=()=>$("#view").classList.toggle("zoom");
$("#exp").onclick=()=>{let t="slot,pref,damage_A,damage_B,change\n";S.forEach(s=>{const a=A[s]||{};t+=[s,a.pref||"",a.dA||"",a.dB||"",a.ch||""].join(",")+"\n"});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="comic_form_eye_alessandro.csv";l.click()};
show();
</script></body></html>"""
_btn = lambda q, vals: "".join(f'<button data-q="{q}" data-v="{v}">{v}</button>' for v in vals)
PAGE = (PAGE.replace("__P__", _btn("pref", ["A", "B", "uguale"])).replace("__DA__", _btn("dA", ["nessuno", "lieve", "medio", "forte"]))
        .replace("__DB__", _btn("dB", ["nessuno", "lieve", "medio", "forte"])).replace("__CH__", _btn("ch", ["poco", "medio", "molto"])))


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
