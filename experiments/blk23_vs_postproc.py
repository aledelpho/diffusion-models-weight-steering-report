"""C53 — block 23 against a saturation slider applied afterwards (docs/prereg_blk23_vs_postproc.md).
Written 2026-10-06, committed with the pre-registration before any sheet is shown or measure computed.

  python blk23_vs_postproc.py --build     # post-processed copies of the C47 baselines + data/blk23_postproc_match.csv
  python blk23_vs_postproc.py --sheets    # 64 blind sheets + data/blk23_postproc_blind_key.csv
  python blk23_vs_postproc.py --page      # blind_pp/test.html (Italian, one sheet at a time, CSV export)
  python blk23_vs_postproc.py --tally --answers data/blk23_postproc_blind_answers_<obs>.csv --tag <obs>
  python blk23_vs_postproc.py --measure   # Part B1 (layout r) and B2 -> data/blk23_postproc_measures.csv
  python blk23_vs_postproc.py --measure --deep   # adds LPIPS and DINOv2 as in standard_metrics.py (needs torch, piq)

Post-processed images: Text2Img/benchmark_blk23_colorful/postproc/{prompt}_{method}_{target}_seed{seed}.png
  method: slider (PIL ImageEnhance.Color, primary) or chroma (CIELAB a*, b* x k)
  target: the C47 condition whose chroma change it matches (b23_m0.450 ... txtneg)
"""
import argparse, csv, json, os, sys
from math import comb
import numpy as np
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")
ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt")
SRC = os.path.join(ROOT, "benchmark_blk23_colorful")
PP = os.path.join(SRC, "postproc")
BLIND = os.path.join(SRC, "blind_pp")
MATCH = os.path.join(DATA, "blk23_postproc_match.csv")
KEY = os.path.join(DATA, "blk23_postproc_blind_key.csv")
PROMPTS = ["E1_cartoon", "E3_oil", "E7_sepiaphoto", "C2_rally", "C3_fox", "C4_stilllife", "P3_archerforest", "P4_selfie"]
SEEDS = {"E1_cartoon": ["2718281", "4669201"], "E3_oil": ["2718281", "4669201"], "E7_sepiaphoto": ["2718281", "4669201"],
         "C2_rally": ["2718281", "4669201"], "C3_fox": ["2718281", "4669201"], "C4_stilllife": ["2718281", "4669201"],
         "P3_archerforest": ["3141592", "4669201"], "P4_selfie": ["1618033", "4669201"]}
TARGETS = ["b23_m0.450", "b23_m0.300", "b23_m0.150", "b23_p0.150", "b23_p0.300", "txtpos", "txtneg"]
METHODS = ["slider", "chroma"]


def src(p, c, s):
    return os.path.join(SRC, f"{p}_{c}_krea2_seed{s}_00001_.png")


def ppath(p, m, t, s):
    return os.path.join(PP, f"{p}_{m}_{t}_seed{s}.png")


# ---------------------------------------------------------------- colour
M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
WHITE = np.array([0.95047, 1.0, 1.08883])


def rgb2lab(a):
    a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    xyz = a @ M.T / WHITE
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab2rgb(L):
    fy = (L[..., 0] + 16) / 116; fx = fy + L[..., 1] / 500; fz = fy - L[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f > 0.206893, f ** 3, (f - 16 / 116) / 7.787) * WHITE
    a = xyz @ np.linalg.inv(M).T
    a = np.clip(a, 0, 1)
    return np.clip(np.where(a > 0.0031308, 1.055 * a ** (1 / 2.4) - 0.055, 12.92 * a), 0, 1)


def lab_small(im):
    """The C47 metric: CIELAB of the image box-resized to 64x80 (block_effect_overlap.lab)."""
    return rgb2lab(np.asarray(im.convert("RGB").resize((64, 80), Image.BOX), dtype=np.float64) / 255.0)


def mean_chroma(im):
    L = lab_small(im); return float(np.hypot(L[..., 1], L[..., 2]).mean())


def apply(base, method, f):
    if method == "slider":
        return ImageEnhance.Color(base).enhance(f)
    L = rgb2lab(np.asarray(base, dtype=np.float64) / 255.0)
    L[..., 1:] *= f
    return Image.fromarray((lab2rgb(L) * 255 + 0.5).astype(np.uint8))


def match(base, method, target_dc, c0):
    """Bisection on the factor so that mean chroma - c0 == target_dc (within 0.05)."""
    lo, hi = (1.0, 4.0) if target_dc > 0 else (0.0, 1.0)
    if (mean_chroma(apply(base, method, hi if target_dc > 0 else lo)) - c0 - target_dc) * (1 if target_dc > 0 else -1) < 0:
        return None, None
    for _ in range(40):
        mid = (lo + hi) / 2
        d = mean_chroma(apply(base, method, mid)) - c0
        if abs(d - target_dc) <= 0.05:
            return mid, d
        if d < target_dc:
            lo = mid
        else:
            hi = mid
    return mid, d


def build(only=None):
    """only: one prompt id (the build is long; it can run one prompt at a time and merges the table)."""
    os.makedirs(PP, exist_ok=True)
    rows = []
    for p in ([only] if only else PROMPTS):
        for s in SEEDS[p]:
            base = Image.open(src(p, "baseline", s)).convert("RGB")
            c0 = mean_chroma(base)
            for t in TARGETS:
                dc = mean_chroma(Image.open(src(p, t, s))) - c0
                for m in METHODS:
                    f, got = match(base, m, dc, c0)
                    if f is not None:
                        apply(base, m, f).save(ppath(p, m, t, s))
                    rows.append({"prompt": p, "seed": s, "target": t, "method": m, "target_d_chroma": round(dc, 4),
                                 "factor": "" if f is None else round(f, 5),
                                 "achieved_d_chroma": "" if got is None else round(got, 4),
                                 "reachable": int(f is not None)})
            print(p, s, flush=True)
    if only and os.path.exists(MATCH):
        rows = [r for r in csv.DictReader(open(MATCH)) if r["prompt"] != only] + rows
        rows.sort(key=lambda r: (PROMPTS.index(r["prompt"]), r["seed"], TARGETS.index(r["target"]), METHODS.index(r["method"])))
    with open(MATCH, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("match table", len(rows), "rows ->", MATCH)


# ---------------------------------------------------------------- blind sheets
def sheets():
    from PIL import ImageDraw, ImageFont
    rng = np.random.default_rng(53)
    pairs = [(d, p, s) for d, t in (("S", "b23_m0.450"), ("D", "b23_p0.300")) for p in PROMPTS for s in SEEDS[p]]
    blk_left = rng.integers(0, 2, len(pairs)).astype(bool)
    ids = rng.permutation(np.arange(1000, 9999))[: 2 * len(pairs)]
    os.makedirs(BLIND, exist_ok=True)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    rows = []
    for k, (d, p, s) in enumerate(pairs):
        t = "b23_m0.450" if d == "S" else "b23_p0.300"
        pp = ppath(p, "slider", t, s)
        assert os.path.exists(pp), f"unreachable or not built: {pp}"
        a = Image.open(src(p, t, s)).convert("RGB").resize((512, 640), Image.LANCZOS)
        b = Image.open(pp).convert("RGB").resize((512, 640), Image.LANCZOS)
        for j, (st, bl) in enumerate((("original", blk_left[k]), ("mirrored", not blk_left[k]))):
            L, R = (a, b) if bl else (b, a)
            S = Image.new("RGB", (512 * 2 + 24, 640 + 48), (128, 128, 128)); dr = ImageDraw.Draw(S)
            S.paste(L, (0, 48)); S.paste(R, (512 + 24, 48))
            dr.text((210, 8), "LEFT", fill=(0, 0, 0), font=font); dr.text((512 + 24 + 200, 8), "RIGHT", fill=(0, 0, 0), font=font)
            sid = f"sheet_{ids[2 * k + j]}"
            S.save(os.path.join(BLIND, sid + ".png"))
            rows.append({"sheet": sid, "set": st, "direction": d, "prompt": p, "seed": s, "blk23_side": "LEFT" if bl else "RIGHT"})
    with open(KEY, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("sheets", len(rows), "->", BLIND)


def page(observer_b=False):
    import base64, io
    rng = np.random.default_rng(5353)
    sh = sorted(f[:-4] for f in os.listdir(BLIND) if f.startswith("sheet_") and f.endswith(".png"))
    order = [sh[i] for i in rng.permutation(len(sh))]
    imgs = {}
    for sid in order:
        b = io.BytesIO(); Image.open(os.path.join(BLIND, sid + ".png")).convert("RGB").save(b, "JPEG", quality=88)
        imgs[sid] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    html = PAGE.replace("__ORDER__", json.dumps(order)).replace("__IMG__", json.dumps(imgs))
    name = "test.html"
    if observer_b:   # amendment 1: one instruction, nothing else changes
        html = html.replace('<div id="n"></div>', '<p style="margin:10px auto;max-width:60em;color:#fc6">Le due immagini possono '
                            'differire anche in piccoli dettagli o forme: ignora queste differenze e giudica solo i colori.</p><div id="n"></div>')
        html = html.replace("cieco_blk23_pp_v1", "cieco_blk23_pp_B").replace("blk23_postproc_blind_answers.csv", "blk23_postproc_blind_answers_B.csv")
        name = "test_B.html"
    with open(os.path.join(BLIND, name), "w", encoding="utf-8") as fh:
        fh.write(html)
    print("page", len(order), "sheets ->", os.path.join(BLIND, name))


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Confronto</title>
<style>body{margin:0;background:#202020;color:#eee;font:16px system-ui,sans-serif;text-align:center}
img{max-width:98vw;max-height:70vh;display:block;margin:8px auto}
.q{margin:10px}button{font:16px system-ui;padding:10px 26px;margin:0 6px;border-radius:8px;border:1px solid #666;background:#333;color:#eee;cursor:pointer}
button.on{background:#3b6e4f;border-color:#6c6}#n{color:#aaa}</style></head><body>
<div id="n"></div><img id="im">
<div class="q">In quale delle due immagini i colori sembrano pi&ugrave; naturali, come se l'immagine fosse nata cos&igrave;?<br>
<button data-q="q1" data-v="LEFT">SINISTRA</button><button data-q="q1" data-v="RIGHT">DESTRA</button></div>
<div class="q">Quale delle due preferisci?<br>
<button data-q="q2" data-v="LEFT">SINISTRA</button><button data-q="q2" data-v="RIGHT">DESTRA</button></div>
<div class="q"><button id="prev">&larr; indietro</button><button id="next">avanti &rarr;</button>
<button id="exp">Fine: scarica le risposte</button></div>
<script>
const O=__ORDER__;const IMG=__IMG__;const K="cieco_blk23_pp_v1";let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;const $=s=>document.querySelector(s);
function show(){const s=O[i];$("#im").src=IMG[s];const a=A[s]||{};
 const done=O.filter(x=>A[x]&&A[x].q1&&A[x].q2).length;$("#n").textContent=`${i+1} di ${O.length} \u00b7 completate ${done}`;
 document.querySelectorAll("button[data-q]").forEach(b=>b.classList.toggle("on",a[b.dataset.q]===b.dataset.v))}
document.querySelectorAll("button[data-q]").forEach(b=>b.onclick=()=>{const s=O[i];A[s]=A[s]||{};A[s][b.dataset.q]=b.dataset.v;
 try{localStorage.setItem(K,JSON.stringify(A))}catch(e){};show();if(A[s].q1&&A[s].q2&&i<O.length-1)setTimeout(()=>{i++;show()},250)});
$("#prev").onclick=()=>{if(i>0){i--;show()}};$("#next").onclick=()=>{if(i<O.length-1){i++;show()}};
$("#exp").onclick=()=>{let t="sheet,q1,q2\n";O.forEach(s=>{const a=A[s]||{};t+=`${s},${a.q1||""},${a.q2||""}\n`});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="blk23_postproc_blind_answers.csv";l.click()};
show();
</script></body></html>"""


# ---------------------------------------------------------------- Part A
def binom_p(k, n):
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def tally(answers, tag):
    key = {r["sheet"]: r for r in csv.DictReader(open(KEY))}
    ans = {r["sheet"]: r for r in csv.DictReader(open(answers))}
    assert set(ans) == set(key), "answers must cover all 64 sheets"
    pair = lambda r: (r["direction"], r["prompt"], r["seed"])
    orig = {pair(r): sid for sid, r in key.items() if r["set"] == "original"}
    mirr = {pair(r): sid for sid, r in key.items() if r["set"] == "mirrored"}
    same = sum(ans[orig[p]]["q1"].upper() == ans[mirr[p]]["q1"].upper() for p in orig)
    gate = same / len(orig) <= 0.75
    out = [("position gate (q1): pairs where both sets name the same side", f"{same}/{len(orig)}", "pass" if gate else "VOID")]
    for d, h in (("S", "H1 adding colour"), ("D", "H2 removing colour")):
        P = [p for p in orig if p[0] == d]
        res = {}
        for st, D in (("original", orig), ("mirrored", mirr)):
            for q in ("q1", "q2"):
                n = sum(ans[D[p]][q].upper() == key[D[p]]["blk23_side"] for p in P)
                res[(st, q)] = n
                out.append((f"{d} {st}: blk23 chosen on {q}", f"{n}/{len(P)} (p = {binom_p(n, len(P)):.4f})", ""))
        lo = min(res[("original", "q1")], res[("mirrored", "q1")])
        v = "void" if not gate else ("blk23 more natural" if lo >= 12 else "slider more natural" if lo <= 4 or
             max(len(P) - res[("original", "q1")], len(P) - res[("mirrored", "q1")]) >= 12 else "no difference shown")
        out.append((f"{h} (>= 12/16 both sets; <= 4/16 either)", lo, v))
    with open(os.path.join(DATA, f"blk23_postproc_blind_tests_{tag}.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["test", "value", "verdict"]); w.writerows(out)
    for o in out:
        print(" | ".join(str(x) for x in o))


# ---------------------------------------------------------------- Part B
def b2(base, x):
    """What an image does beyond the baseline, at full resolution downsampled to 256x320."""
    B = rgb2lab(np.asarray(base.resize((256, 320), Image.BOX), dtype=np.float64) / 255.0)
    X = rgb2lab(np.asarray(x.resize((256, 320), Image.BOX), dtype=np.float64) / 255.0)
    cb, cx = np.hypot(B[..., 1], B[..., 2]), np.hypot(X[..., 1], X[..., 2])
    m = cb > 10
    ratio = np.log((cx[m] + 1) / (cb[m] + 1))
    slope = float(np.polyfit(np.log(cb[m] + 1), ratio, 1)[0]) if m.sum() > 50 else float("nan")
    hb, hx = np.arctan2(B[..., 2], B[..., 1]), np.arctan2(X[..., 2], X[..., 1])
    dh = np.degrees(np.abs(np.angle(np.exp(1j * (hx - hb)))))[m]
    ab, ax = np.asarray(base, dtype=np.uint8), np.asarray(x, dtype=np.uint8)
    clip = lambda a: float(((a == 0) | (a == 255)).any(-1).mean())
    return {"selectivity_slope": round(slope, 4), "hue_shift_deg": round(float(dh.mean()) if m.any() else float("nan"), 3),
            "d_L_mean": round(float(X[..., 0].mean() - B[..., 0].mean()), 3),
            "d_L_std": round(float(X[..., 0].std() - B[..., 0].std()), 3),
            "d_clipped": round(clip(ax) - clip(ab), 5)}


def measure(deep=False):
    if deep:
        import torch, piq
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        lp = piq.LPIPS().to(dev)
        dino = torch.hub.load("facebookresearch/dinov2", "dinov2_vitb14").to(dev).eval()
        mean = torch.tensor([0.485, 0.456, 0.406], device=dev)[:, None, None]; std = torch.tensor([0.229, 0.224, 0.225], device=dev)[:, None, None]
        T = lambda im, size: torch.from_numpy(np.asarray(im.convert("RGB").resize(size, Image.BICUBIC), dtype=np.float32) / 255.0).permute(2, 0, 1)[None].to(dev)
        def emb(im):
            with torch.no_grad():
                d = dino(((T(im, (224, 280))[0] - mean) / std)[None])[0]
            return d / d.norm()
    rows = []
    for p in PROMPTS:
        for s in SEEDS[p]:
            base = Image.open(src(p, "baseline", s)).convert("RGB")
            LB = lab_small(base)
            if deep:
                xb, eb = T(base, (512, 640)), emb(base)
            for t in TARGETS:
                cands = [("model", src(p, t, s))] + [(m, ppath(p, m, t, s)) for m in METHODS]
                imgs = {k: Image.open(f).convert("RGB") for k, f in cands if os.path.exists(f)}
                for k, x in imgs.items():
                    LX = lab_small(x)
                    r = {"prompt": p, "seed": s, "target": t, "image": k,
                         "d_chroma": round(float(np.hypot(LX[..., 1], LX[..., 2]).mean() - np.hypot(LB[..., 1], LB[..., 2]).mean()), 4),
                         "layout_r": round(float(np.corrcoef(LX[..., 0].ravel(), LB[..., 0].ravel())[0, 1]), 4), **b2(base, x)}
                    if deep:
                        with torch.no_grad():
                            r["lpips"] = round(float(lp(T(x, (512, 640)), xb)), 5)
                            r["dino_cos"] = round(float(emb(x) @ eb), 5)
                            if k == "model" and "slider" in imgs:
                                r["lpips_to_slider"] = round(float(lp(T(x, (512, 640)), T(imgs["slider"], (512, 640)))), 5)
                    rows.append(r)
    name = "blk23_postproc_measures_deep.csv" if deep else "blk23_postproc_measures.csv"
    fields = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 99)
    with open(os.path.join(DATA, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(len(rows), "rows ->", name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for f in ("build", "sheets", "page", "tally", "measure", "deep", "observer-b"):
        ap.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--answers"); ap.add_argument("--tag"); ap.add_argument("--prompt")
    a = ap.parse_args()
    if a.build: build(a.prompt)
    if a.sheets: sheets()
    if a.page: page(a.observer_b)
    if a.tally: tally(a.answers, a.tag)
    if a.measure: measure(a.deep)
