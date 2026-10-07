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
<div class="q"><b>Degrado di superficie in A</b>__DA__</div>
<div class="q"><b>Degrado di superficie in B</b>__DB__</div>
<div class="q"><b>Quanto &egrave; cambiata l'immagine tra A e B?</b>__CH__</div>
<div class="q"><button id="prev">&larr;</button><button id="next">&rarr;</button><button id="exp">Scarica le risposte</button></div></div></div>
<script>
const S=__SLOTS__,K="comic_form_eye_v1",Q=["dA","dB","ch"];let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
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
$("#exp").onclick=()=>{let t="slot,damage_A,damage_B,change\n";S.forEach(s=>{const a=A[s]||{};t+=[s,a.dA||"",a.dB||"",a.ch||""].join(",")+"\n"});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="comic_form_eye_alessandro.csv";l.click()};
show();
</script></body></html>"""
_btn = lambda q, vals: "".join(f'<button data-q="{q}" data-v="{v}">{v}</button>' for v in vals)
PAGE = (PAGE.replace("__DA__", _btn("dA", ["nessuno", "lieve", "medio", "forte"]))
        .replace("__DB__", _btn("dB", ["nessuno", "lieve", "medio", "forte"])).replace("__CH__", _btn("ch", ["poco", "medio", "molto"])))


def measure():
    """P1: layout r (C47 metric: correlation of CIELAB L at 64x80) of each edit with its baseline."""
    import numpy as np
    from PIL import Image
    from blk23_vs_postproc import lab_small
    L = lambda p: lab_small(Image.open(p).convert("RGB"))[..., 0].ravel()
    out = []
    for r in csv.DictReader(open(PLAN, encoding="utf-8")):
        if r["group"] not in ("form", "surface"):
            continue
        a, b = L(f(r["prompt_id"], r["seed"], r["cond"])), L(f(r["prompt_id"], r["seed"], "baseline"))
        out.append({"prompt": r["prompt_id"], "seed": r["seed"], "cond": r["cond"], "group": r["group"],
                    "layout_r": round(float(np.corrcoef(a, b)[0, 1]), 4)})
    with open(DATA / "comic_form_layout.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(len(out), "edits measured")


def tally():
    import numpy as np, pandas as pd
    from scipy.stats import mannwhitneyu, fisher_exact
    k = pd.read_csv(KEY); a = pd.read_csv(LABELS); lay = pd.read_csv(DATA / "comic_form_layout.csv")
    a["pair"] = a.slot.str.split("#").str[0]
    D = {"nessuno": 0, "lieve": 1, "medio": 2, "forte": 3}; C = {"poco": 0, "medio": 1, "molto": 2}
    a = a.merge(k, on="pair")
    a["d_edit"] = np.where(a.left == "edit", a.damage_A.map(D), a.damage_B.map(D))
    a["d_base"] = np.where(a.left == "edit", a.damage_B.map(D), a.damage_A.map(D))
    a["ch"] = a.change.map(C)
    first = a.drop_duplicates("pair", keep="first"); sec = a[a.duplicated("pair", keep="first")]
    m = first.set_index("pair").loc[sec.pair]; s = sec.set_index("pair")
    agree = float(np.mean((m.d_edit.values >= 2) == (s.d_edit.values >= 2)) * 0.5 + np.mean((m.d_base.values >= 2) == (s.d_base.values >= 2)) * 0.5)
    agree_edit = float(np.mean((m.d_edit.values >= 2) == (s.d_edit.values >= 2)))
    ch_agree = float(np.mean(m.ch.fillna(-1).values == s.ch.fillna(-1).values))
    print(f"GATE presence agreement damage>=medio: edit side {agree_edit:.2f}, both sides {agree:.2f} (n={len(sec)}); change exact agreement {ch_agree:.2f}")
    res = {"gate_edit": agree_edit, "gate_both": agree}
    per = lay.groupby(["cond", "group"]).layout_r.mean().reset_index()
    F, S = per[per.group == "form"].layout_r, per[per.group == "surface"].layout_r
    p1 = mannwhitneyu(F, S, alternative="less").pvalue
    print(f"P1 layout r per edit: FORM median {F.median():.3f} mean {F.mean():.3f}; SURFACE median {S.median():.3f} mean {S.mean():.3f}; one-sided MWU p = {p1:.4g}")
    for lab, fill in (("primary (empties excluded)", None), ("sensitivity (empties = molto)", 2)):
        x = first.copy(); x["chs"] = x.ch if fill is None else x.ch.fillna(fill)
        e = x.groupby(["cond", "group"]).chs.mean().reset_index().dropna()
        Fe, Se = e[e.group == "form"].chs, e[e.group == "surface"].chs
        print(f"P2 {lab}: FORM mean {Fe.mean():.2f} (n={len(Fe)}), SURFACE mean {Se.mean():.2f} (n={len(Se)}); one-sided MWU p = {mannwhitneyu(Fe, Se, alternative='greater').pvalue:.4g}")
    print("empty change answers by group:", first[first.ch.isna()].group.value_counts().to_dict())
    base_hits = int((first.d_base >= 2).sum()); n = len(first)
    for g in ("surface", "form"):
        x = first[first.group == g]; hits = int((x.d_edit >= 2).sum()); nn = len(x)
        bh = int((x.d_base >= 2).sum())
        print(f"P4 {g}: edit damage>=medio {hits}/{nn} = {hits/nn:.3f}; baseline side in the same pairs {bh}/{nn} = {bh/nn:.3f}")
        if g == "surface":
            print("   Fisher one-sided p =", f"{fisher_exact([[hits, nn - hits], [bh, nn - bh]], alternative='greater')[1]:.3g}")
        else:
            p_e, p_b = hits / nn, bh / nn
            l1, u1 = confint_wilson(hits, nn); l2, u2 = confint_wilson(bh, nn)
            d = p_e - p_b
            lo = d - np.sqrt((p_e - l1) ** 2 + (u2 - p_b) ** 2); hi = d + np.sqrt((u1 - p_e) ** 2 + (p_b - l2) ** 2)
            print(f"   difference {d:.3f}, Newcombe 95% [{lo:.3f}, {hi:.3f}] -> {'NO DETECTABLE COST' if hi < 0.10 else ('COST' if lo > 0 else 'cost not excluded')}")
    print("baseline sides overall damage>=medio:", base_hits, "/", n)
    first.to_csv(DATA / "comic_form_eye_tally_alessandro.csv", index=False)
    print(first.groupby(["group", "cond"]).agg(dmg_edit=("d_edit", "mean"), dmg_ge2=("d_edit", lambda v: int((v >= 2).sum())), change=("ch", "mean")).round(2).to_string())


def confint_wilson(k, n, z=1.959964):
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


import numpy as np


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "checks", "check", "count", "page", "measure", "tally"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.checks)
    if a.check: check()
    if a.count: count()
    if a.page: page()
    if a.measure: measure()
    if a.tally: tally()
