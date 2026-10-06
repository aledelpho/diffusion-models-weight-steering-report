"""C58 — block 23 split into its attention and its MLP (docs/prereg_blk23_split.md). Written 2026-10-06.

  python blk23_split.py --plan              # data/blk23_split_plan.csv (7 check-phase rows + 158)
  python blk23_split.py --queue --checks    # the check-phase renders only
  python blk23_split.py --check             # REPRO and SPLIT = WHOLE, pixel for pixel
  python blk23_split.py --queue             # the 64
  python blk23_split.py --count             # expected 165 missing 0
  python blk23_split.py --page              # blind eye page (64 sheets + 6 repeats) + data/blk23_split_eye_key.csv
  python blk23_split.py --measure           # after the eye pass: data/blk23_split_measures.csv + data/blk23_split_tests.csv

Renders: Text2Img/benchmark_blk23_split/{prompt}_{cond}_krea2_seed{seed}_00001_.png
  cond: attn_m0.450, mlp_m0.450, attn_p0.300, mlp_p0.300; checks: CHK_whole_m0.450 (vector path),
  CHK_all8_m0.450, CHK_all8_p0.300 (granular, all eight matrices)
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
PLAN = DATA / "blk23_split_plan.csv"
EYEKEY = DATA / "blk23_split_eye_key.csv"
FOLDER = "benchmark_blk23_split"
ATTN = ["attn.wq", "attn.wk", "attn.wv", "attn.gate", "attn.wo"]
MLP = ["mlp.gate", "mlp.up", "mlp.down"]
DOSES_C47 = [("m0.450", -0.45), ("p0.300", 0.30)]          # whole block already in C47
DOSES_HI = [("m1.000", -1.0), ("p1.000", 1.0)]             # amendment 1: whole block rendered here
DOSES = DOSES_C47 + DOSES_HI
ZERO = ",".join(["0.0"] * 34)
CHECK_CELL = ("E1_cartoon", "2718281")


def gj(mats, d):
    return json.dumps({f"blocks.23.{m}.weight": d for m in mats})


def vec23(d):
    v = ["0.0"] * 34; v[23] = repr(float(d)); return ",".join(v)


def cells():
    base = [r for r in csv.DictReader(open(c47.PLAN, encoding="utf-8")) if r["cond"] == "baseline"]
    return [(r["prompt_id"], r["seed"], r) for r in base]


def make_plan():
    rows = []
    def add(pid, seed, b, cond, vo, g, phase):
        prefix = f"{pid}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "phase": phase, "prompt_id": pid, "seed": seed, "cond": cond, "vectors_override": vo,
                     "granular_json": g, "prompt_text": b["prompt_text"], "output_prefix": prefix,
                     "expected_filename": f"{prefix}_00001_.png",
                     **{k: b[k] for k in ("sampler", "scheduler", "steps", "cfg", "denoise", "width", "height")}})
    cs = cells()
    b0 = next(b for p, s, b in cs if (p, s) == CHECK_CELL)
    add(*CHECK_CELL, b0, "CHK_whole_m0.450", vec23(-0.45), "", "check")
    for tag, d in DOSES_HI:
        add(*CHECK_CELL, b0, f"whole_{tag}", vec23(d), "", "check")
    for tag, d in DOSES:
        add(*CHECK_CELL, b0, f"CHK_all8_{tag}", ZERO, gj(ATTN + MLP, d), "check")
    for pid, seed, b in cs:
        for tag, d in DOSES:
            if tag in dict(DOSES_HI) and (pid, seed) != CHECK_CELL:
                add(pid, seed, b, f"whole_{tag}", vec23(d), "", "main")
            add(pid, seed, b, f"attn_{tag}", ZERO, gj(ATTN, d), "main")
            add(pid, seed, b, f"mlp_{tag}", ZERO, gj(MLP, d), "main")
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows), "(check:", sum(r["phase"] == "check" for r in rows), ")")


def workflow(r):
    wf = c47.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    if r["granular_json"]:
        wf["50"]["inputs"]["granular_json"] = r["granular_json"]
    return wf


def queue(checks_only):
    n = 0
    for r in csv.DictReader(open(PLAN, encoding="utf-8")):
        if checks_only and r["phase"] != "check":
            continue
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1; print("queued", r["output_prefix"])
    print("queued", n)


def _img(path):
    import numpy as np
    from PIL import Image
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)


def c47_file(pid, seed, cond):
    return c47.IMG_ROOT / c47.FOLDER / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"


def split_file(pid, seed, cond):
    return c47.IMG_ROOT / FOLDER / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"


def whole_file(pid, seed, tag):
    """The whole block: the C47 render at -0.45 / +0.30, the one rendered here at -1.0 / +1.0."""
    return c47_file(pid, seed, f"b23_{tag}") if tag in dict(DOSES_C47) else split_file(pid, seed, f"whole_{tag}")


def check():
    import numpy as np
    p, s = CHECK_CELL
    res = []
    d = int(np.abs(_img(split_file(p, s, "CHK_whole_m0.450")) - _img(c47_file(p, s, "b23_m0.450"))).max())
    res.append(("REPRO whole -0.45 (vector) vs C47", d))
    for tag, _ in DOSES:
        d = int(np.abs(_img(split_file(p, s, f"CHK_all8_{tag}")) - _img(whole_file(p, s, tag))).max())
        res.append((f"SPLIT=WHOLE all eight (granular) {tag} vs whole block (vector)", d))
    for name, d in res:
        print(f"{name}: max abs diff {d}")
    print("CHECK", "PASS" if all(d == 0 for _, d in res) else "FAIL - stop the bench")


def count():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5])


def page():
    import base64, io, numpy as np
    from PIL import Image, ImageDraw, ImageFont
    rng = np.random.default_rng(58)
    sheets = []
    for pid, seed, _ in cells():
        for tag, _ in DOSES:
            paths = {"B": c47_file(pid, seed, "baseline"), "W": whole_file(pid, seed, tag),
                     "A": split_file(pid, seed, f"attn_{tag}"), "M": split_file(pid, seed, f"mlp_{tag}")}
            order = list(rng.permutation(["B", "W", "A", "M"]))
            sheets.append({"pid": pid, "seed": seed, "dose": tag, "order": order, "paths": paths})
    ids = rng.permutation(np.arange(1000, 9999))[: len(sheets)]
    for sh, i in zip(sheets, ids):
        sh["id"] = f"s{i}"
    show = [sh["id"] for sh in sheets]; rng.shuffle(show)
    rep = list(rng.choice(show, 6, replace=False))
    for x in rep:
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), x)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    imgs = {}
    for sh in sheets:
        S = Image.new("RGB", (2 * 520 + 10, 2 * 650 + 10), (60, 60, 60)); d = ImageDraw.Draw(S)
        for k, lab in enumerate(sh["order"]):
            im = Image.open(sh["paths"][lab]).convert("RGB").resize((520, 650), Image.LANCZOS)
            x, y = (k % 2) * 530, (k // 2) * 660
            S.paste(im, (x, y)); d.rectangle((x, y, x + 46, y + 42), fill=(0, 0, 0)); d.text((x + 10, y + 4), "ABCD"[k], fill=(255, 255, 0), font=font)
        b = io.BytesIO(); S.save(b, "JPEG", quality=85)
        imgs[sh["id"]] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    with open(EYEKEY, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["sheet", "prompt", "seed", "dose", "pos_A", "pos_B", "pos_C", "pos_D", "repeated"])
        for sh in sheets:
            w.writerow([sh["id"], sh["pid"], sh["seed"], sh["dose"], *sh["order"], int(sh["id"] in rep)])
    slots = [f"{s}#{k}" for k, s in enumerate(show)]
    html = PAGE.replace("__SLOTS__", json.dumps(slots)).replace("__IMG__", json.dumps(imgs))
    out = c47.IMG_ROOT / FOLDER / "eye_test.html"
    out.write_text(html, encoding="utf-8"); print(len(sheets), "sheets,", len(slots), "showings ->", out)


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Confronto a quattro</title>
<style>body{margin:0;background:#202020;color:#eee;font:16px system-ui,sans-serif;text-align:center}
img{max-width:98vw;max-height:74vh;display:block;margin:6px auto}.q{margin:8px}
button{font:16px system-ui;padding:8px 22px;margin:0 4px;border-radius:8px;border:1px solid #666;background:#333;color:#eee;cursor:pointer}
button.on{background:#3b6e4f;border-color:#6c6}#n{color:#aaa}</style></head><body>
<div id="n"></div><img id="im">
<div class="q">Quale delle quattro ha pi&ugrave; rumore / grana?
<span>__B1__</span></div>
<div class="q">Quale ha i colori pi&ugrave; saturi? <span>__B2__</span></div>
<div class="q"><button id="prev">&larr;</button><button id="next">&rarr;</button><button id="exp">Fine: scarica le risposte</button></div>
<script>
const S=__SLOTS__,IMG=__IMG__,K="blk23_split_eye";let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;const $=s=>document.querySelector(s);
function show(){$("#im").src=IMG[S[i].split("#")[0]];const a=A[S[i]]||{};
 $("#n").textContent=`${i+1} di ${S.length} · completate ${S.filter(s=>A[s]&&A[s].noise&&A[s].sat).length}`;
 document.querySelectorAll("button[data-q]").forEach(b=>b.classList.toggle("on",a[b.dataset.q]===b.dataset.v))}
document.querySelectorAll("button[data-q]").forEach(b=>b.onclick=()=>{const s=S[i];A[s]=A[s]||{};A[s][b.dataset.q]=b.dataset.v;
 try{localStorage.setItem(K,JSON.stringify(A))}catch(e){};show();if(A[s].noise&&A[s].sat&&i<S.length-1)setTimeout(()=>{i++;show()},250)});
$("#prev").onclick=()=>{if(i>0){i--;show()}};$("#next").onclick=()=>{if(i<S.length-1){i++;show()}};
$("#exp").onclick=()=>{let t="slot,sheet,noise,sat\n";S.forEach(s=>{const a=A[s]||{};t+=`${s},${s.split("#")[0]},${a.noise||""},${a.sat||""}\n`});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="blk23_split_eye_alessandro.csv";l.click()};
show();
</script></body></html>""".replace("__B1__", "".join(f'<button data-q="noise" data-v="{c}">{c}</button>' for c in "ABCD")).replace(
    "__B2__", "".join(f'<button data-q="sat" data-v="{c}">{c}</button>' for c in "ABCD"))


def immerkaer(gray):
    """Immerkaer (1996) fast noise sigma: sqrt(pi/2) / (6 (W-2)(H-2)) * sum |I * M|, M = [[1,-2,1],[-2,4,-2],[1,-2,1]]."""
    import numpy as np
    g = gray.astype(np.float64)
    c = (g[:-2, :-2] - 2 * g[:-2, 1:-1] + g[:-2, 2:] - 2 * g[1:-1, :-2] + 4 * g[1:-1, 1:-1] - 2 * g[1:-1, 2:]
         + g[2:, :-2] - 2 * g[2:, 1:-1] + g[2:, 2:])
    h, w = g.shape
    return float(np.sqrt(np.pi / 2) * np.abs(c).sum() / (6 * (w - 2) * (h - 2)))


def measure():
    import numpy as np
    from PIL import Image
    from blk23_vs_postproc import lab_small
    def feats(p):
        im = Image.open(p).convert("RGB")
        L = lab_small(im)
        gray = np.asarray(im.convert("L"))
        e = np.abs(np.diff(np.asarray(im.convert("L").resize((512, 640)), dtype=float), axis=1)).mean()
        return immerkaer(gray), float(np.hypot(L[..., 1], L[..., 2]).mean()), L[..., 0].ravel(), e
    rows = []
    for pid, seed, _ in cells():
        nB, cB, lB, eB = feats(c47_file(pid, seed, "baseline"))
        for tag, _ in DOSES:
            for arm, path in (("W", whole_file(pid, seed, tag)), ("A", split_file(pid, seed, f"attn_{tag}")),
                              ("M", split_file(pid, seed, f"mlp_{tag}"))):
                n, c, l, e = feats(path)
                rows.append({"prompt": pid, "seed": seed, "dose": tag, "arm": arm, "dN": round(n - nB, 4),
                             "dC": round(c - cB, 4), "layout_r": round(float(np.corrcoef(l, lB)[0, 1]), 4), "edge_ratio": round(e / eB, 4)})
    with open(DATA / "blk23_split_measures.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    out = []
    for tag, _ in DOSES:
        by = {}
        for r in rows:
            if r["dose"] == tag:
                by.setdefault((r["prompt"], r["seed"]), {})[r["arm"]] = r
        cs = list(by.values()); n = len(cs)
        gate = sum(c["W"]["dN"] > 0 for c in cs)
        h1 = sum(c["M"]["dN"] > c["A"]["dN"] for c in cs)
        h2 = sum(abs(c["M"]["dN"] - c["W"]["dN"]) < abs(c["A"]["dN"] - c["W"]["dN"]) for c in cs)
        sg = lambda x: (x > 0) - (x < 0)
        h3 = sum(sg(c["A"]["dC"]) == sg(c["W"]["dC"]) and abs(c["A"]["dC"]) > abs(c["M"]["dC"]) for c in cs)
        h4 = sum(c["A"]["dN"] < c["W"]["dN"] and sg(c["A"]["dC"]) == sg(c["W"]["dC"]) for c in cs)
        h1_ref = sum(c["A"]["dN"] >= c["M"]["dN"] for c in cs)
        h3_ref = sum(abs(c["M"]["dC"]) >= abs(c["A"]["dC"]) for c in cs)
        g_ok = gate >= 10
        v = lambda k: "supported" if k >= 12 else "not supported"
        out += [(f"{tag} gate: W adds noise (>= 10/16)", f"{gate}/{n}", "pass" if g_ok else "VOID for H1, H2, H4"),
                (f"{tag} H1 MLP noisier than attention (>= 12/16)", f"{h1}/{n}", v(h1) if g_ok else "void"),
                (f"{tag} H2 MLP closer to the whole block's noise (>= 12/16)", f"{h2}/{n}", v(h2) if g_ok else "void"),
                (f"{tag} H3 attention carries the colour (>= 12/16)", f"{h3}/{n}", v(h3)),
                (f"{tag} H4 attention: colour with less noise than the whole (>= 12/16)", f"{h4}/{n}", v(h4) if g_ok else "void")]
        thesis = ("HOLDS" if g_ok and h1 >= 12 and h3 >= 12 else
                  "REFUTED" if (g_ok and h1_ref >= 12) or h3_ref >= 12 else "not decided")
        out.append((f"{tag} THESIS (H1 and H3)", "", thesis))
        for arm in "WAM":
            out.append((f"{tag} median dN / dC / layout r, {arm}", " / ".join(
                f"{np.median([c[arm][k] for c in cs]):+.3f}" for k in ("dN", "dC", "layout_r")), ""))
    with open(DATA / "blk23_split_tests.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["test", "value", "verdict"]); w.writerows(out)
    for o in out:
        print(" | ".join(str(x) for x in o))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "checks", "check", "count", "page", "measure"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.plan: make_plan()
    if a.queue: queue(a.checks)
    if a.check: check()
    if a.count: count()
    if a.page: page()
    if a.measure: measure()
