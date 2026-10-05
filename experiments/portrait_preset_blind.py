"""C52 amendment 1 — blind forced choice (docs/prereg_portrait_preset.md). Written 2026-10-05.

  python portrait_preset_blind.py --sheets   # 56 sheets (28 original + 28 mirrored) + data/portrait_preset_blind_key.csv
  python portrait_preset_blind.py --tally    # rules on data/portrait_preset_blind_answers.csv (model observers, 3 per sheet)
  python portrait_preset_blind.py --tally --answers data/portrait_preset_blind_answers_human.csv --observers 1 --tag human
  python portrait_preset_blind.py --page     # blind/test.html for a human observer (amendment 2)

Sheets go to Text2Img/benchmark_portraits/blind/sheet_XXXX.png with random ids, so neither the file
name nor the order says which character, seed, side or set a sheet belongs to.
Answers file columns: sheet, observer, q1 (LEFT/RIGHT), q2 (YES/NO).
"""
import argparse, csv, os, sys
from math import comb
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from portraits import CALIBRATION, HELD_OUT, SEEDS_C, FOLDER_C, IMG_ROOT

DATA = os.path.join(HERE, "..", "data")
KEY = os.path.join(DATA, "portrait_preset_blind_key.csv")
ANS = os.path.join(DATA, "portrait_preset_blind_answers.csv")
OUT = os.path.join(str(IMG_ROOT), "benchmark_portraits", "blind")


def sheets():
    from PIL import Image, ImageDraw, ImageFont
    rng = np.random.default_rng(52)
    pairs = [(g, c, s) for g, chars in (("held_out", HELD_OUT), ("calibration", CALIBRATION)) for c in chars for s in SEEDS_C]
    preset_left = rng.integers(0, 2, len(pairs)).astype(bool)
    ids = rng.permutation(np.arange(1000, 9999))[: 2 * len(pairs)]
    os.makedirs(OUT, exist_ok=True)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    rows = []
    for k, (g, c, s) in enumerate(pairs):
        for j, (st, pl) in enumerate((("original", preset_left[k]), ("mirrored", not preset_left[k]))):
            a = Image.open(os.path.join(str(IMG_ROOT), FOLDER_C, f"{c}_baseline_krea2_seed{s}_00001_.png")).convert("RGB").resize((512, 640), Image.LANCZOS)
            b = Image.open(os.path.join(str(IMG_ROOT), FOLDER_C, f"{c}_preset_krea2_seed{s}_00001_.png")).convert("RGB").resize((512, 640), Image.LANCZOS)
            L, R = (b, a) if pl else (a, b)
            S = Image.new("RGB", (512 * 2 + 24, 640 + 48), (128, 128, 128)); d = ImageDraw.Draw(S)
            S.paste(L, (0, 48)); S.paste(R, (512 + 24, 48))
            d.text((210, 8), "LEFT", fill=(0, 0, 0), font=font); d.text((512 + 24 + 200, 8), "RIGHT", fill=(0, 0, 0), font=font)
            sid = f"sheet_{ids[2 * k + j]}"
            S.save(os.path.join(OUT, sid + ".png"))
            rows.append({"sheet": sid, "set": st, "group": g, "char": c, "seed": s, "preset_side": "LEFT" if pl else "RIGHT"})
    with open(KEY, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("sheets", len(rows), "->", OUT)


def binom_p(k, n):
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def tally(ans=ANS, n_obs=3, tag="model"):
    key = {r["sheet"]: r for r in csv.DictReader(open(KEY))}
    votes = {}
    for r in csv.DictReader(open(ans)):
        votes.setdefault(r["sheet"], []).append((r["q1"].strip().upper(), r["q2"].strip().upper()))
    maj = {}
    for sid, v in votes.items():
        assert len(v) == n_obs, (sid, len(v))
        side = max(("LEFT", "RIGHT"), key=lambda x: sum(a == x for a, _ in v))
        same = sum(b == "YES" for _, b in v) > n_obs / 2
        maj[sid] = (side, same)
    pair = lambda r: (r["char"], r["seed"])
    orig = {pair(r): (sid, r) for sid, r in key.items() if r["set"] == "original"}
    mirr = {pair(r): (sid, r) for sid, r in key.items() if r["set"] == "mirrored"}
    same_side = sum(maj[orig[p][0]][0] == maj[mirr[p][0]][0] for p in orig)
    gate = same_side / len(orig) <= 0.75
    out = [("position gate: pairs where both sets name the same side", f"{same_side}/{len(orig)}", "pass" if gate else "VOID")]
    for grp in ("held_out", "calibration"):
        P = [p for p in orig if orig[p][1]["group"] == grp]
        res = {}
        for st, D in (("original", orig), ("mirrored", mirr)):
            pick = sum(maj[D[p][0]][0] == D[p][1]["preset_side"] for p in P)
            yes = sum(maj[D[p][0]][1] for p in P)
            res[st] = (pick, yes)
            out.append((f"{grp} {st}: preset chosen", f"{pick}/{len(P)} (p = {binom_p(pick, len(P)):.4f})", ""))
            out.append((f"{grp} {st}: same character YES", f"{yes}/{len(P)}", ""))
        if grp == "held_out":
            lo4 = min(res["original"][0], res["mirrored"][0]); lo5 = min(res["original"][1], res["mirrored"][1])
            h4 = "void" if not gate else "supported" if lo4 >= 9 else "refuted" if lo4 <= 6 else "inconclusive"
            h5 = "void" if not gate else "supported" if lo5 >= 9 else "refuted" if lo5 <= 6 else "inconclusive"
            out += [("H4 look visible blind (>= 9/12 both sets; <= 6 either)", lo4, h4),
                    ("H5 character kept (>= 9/12 both sets; <= 6 either)", lo5, h5)]
    with open(os.path.join(DATA, f"portrait_preset_blind_tests_{tag}.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["test", "value", "verdict"]); w.writerows(out)
    for o in out:
        print(" | ".join(str(x) for x in o))



def page():
    """One sheet at a time, in a fixed random order, two questions, CSV export. No hint of the hypothesis."""
    import json
    rng = np.random.default_rng(5252)
    sh = sorted(f[:-4] for f in os.listdir(OUT) if f.startswith("sheet_") and f.endswith(".png"))
    order = [sh[i] for i in rng.permutation(len(sh))]
    html = """<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Confronto</title>
<style>body{margin:0;background:#202020;color:#eee;font:16px system-ui,sans-serif;text-align:center}
img{max-width:98vw;max-height:72vh;display:block;margin:8px auto}
.q{margin:10px}button{font:16px system-ui;padding:10px 26px;margin:0 6px;border-radius:8px;border:1px solid #666;background:#333;color:#eee;cursor:pointer}
button.on{background:#3b6e4f;border-color:#6c6}#n{color:#aaa}</style></head><body>
<div id="n"></div><img id="im">
<div class="q">Quale dei due ritratti sembra di più un fumetto americano con un'inclinazione verso l'animazione &mdash; colori più piatti e linee più pulite?<br>
<button data-q="q1" data-v="LEFT">SINISTRA</button><button data-q="q1" data-v="RIGHT">DESTRA</button></div>
<div class="q">I due ritratti mostrano lo stesso personaggio (la stessa persona, anche se disegnata in modo diverso)?<br>
<button data-q="q2" data-v="YES">S&Igrave;</button><button data-q="q2" data-v="NO">NO</button></div>
<div class="q"><button id="prev">&larr; indietro</button><button id="next">avanti &rarr;</button>
<button id="exp">Fine: scarica le risposte</button></div>
<script>
const O=__ORDER__;const K="cieco_ritratti_v1";let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;const $=s=>document.querySelector(s);
function show(){const s=O[i];$("#im").src=s+".png";const a=A[s]||{};
 const done=O.filter(x=>A[x]&&A[x].q1&&A[x].q2).length;$("#n").textContent=`${i+1} di ${O.length} · completate ${done}`;
 document.querySelectorAll("button[data-q]").forEach(b=>b.classList.toggle("on",a[b.dataset.q]===b.dataset.v))}
document.querySelectorAll("button[data-q]").forEach(b=>b.onclick=()=>{const s=O[i];A[s]=A[s]||{};A[s][b.dataset.q]=b.dataset.v;
 try{localStorage.setItem(K,JSON.stringify(A))}catch(e){};show();if(A[s].q1&&A[s].q2&&i<O.length-1)setTimeout(()=>{i++;show()},250)});
$("#prev").onclick=()=>{if(i>0){i--;show()}};$("#next").onclick=()=>{if(i<O.length-1){i++;show()}};
$("#exp").onclick=()=>{let t="sheet,observer,q1,q2\n";O.forEach(s=>{const a=A[s]||{};t+=`${s},human1,${a.q1||""},${a.q2||""}\n`});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="portrait_preset_blind_answers_human.csv";l.click()};
show();
</script></body></html>"""
    with open(os.path.join(OUT, "test.html"), "w", encoding="utf-8") as fh:
        fh.write(html.replace("__ORDER__", json.dumps(order)))
    print("page", len(order), "sheets ->", os.path.join(OUT, "test.html"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for f in ("sheets", "tally", "page"):
        ap.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--answers", default=ANS); ap.add_argument("--observers", type=int, default=3); ap.add_argument("--tag", default="model")
    a = ap.parse_args()
    if a.sheets: sheets()
    if a.page: page()
    if a.tally: tally(a.answers, a.observers, a.tag)
