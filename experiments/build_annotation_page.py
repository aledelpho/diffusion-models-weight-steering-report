# -*- coding: utf-8 -*-
"""
experiments/build_annotation_page.py
====================================
A local page for reading a bench by eye: every preset of every arm, laid out from its most negative
dose to its most positive, with a notes field under each.

    python experiments/build_annotation_page.py parameter_families
    python experiments/build_annotation_page.py centre_push

Writes `presets.html` and `_thumbs/` into that bench's folder. It scans the render folders rather
than trusting a plan, so the ladder it shows is the one that exists on disk. The thumbnails are for
navigation only; clicking one opens the real PNG at 1:1, and the pan position is kept while stepping
along the ladder, which is the only way small differences stay visible.

The analyst's own reading of the renders is deliberately NOT in the page, and the measured numbers
are behind a switch that starts off. Alessandro is being asked what he sees; telling him first is
how an observer gets anchored.

No render is generated.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ROOTS = [Path("/sessions/rcw-01fzmivsryy2r8cd26detdrb/mnt"),
         Path("C:/StabilityMatrix-win-x64/Data/Images/Text2Img")]


def bench_dir(name: str) -> Path:
    for r in ROOTS:
        if (r / name).is_dir():
            return r / name
    sys.exit(f"bench folder not found: {name}")


# ----------------------------------------------------------------- parameter_families
PF_PAT = re.compile(r"^(P\d\d)_F_([a-z]+)_d([+-][\d.]+)_krea2_seed(\d+)_")
PF_INERT = ("norms", "qknorm", "mod")


def scan_parameter_families(B: Path) -> dict:
    groups = {
        "wo":   {"title": "F_wo — attention output projection", "meta":
                 "28 tensori · 1.056.964.608 parametri<br><code>blocks.N.attn.wo.weight</code> · [6144, 6144]"},
        "io":   {"title": "F_io — latent interface", "meta":
                 "2 tensori · 786.432 parametri<br><code>first.weight, last.linear.weight</code> · [6144, 64], [64, 6144]"},
        "proj": {"title": "F_proj — il router da dodici parametri", "meta":
                 "1 tensore · 12 parametri<br><code>txtfusion.projector.weight</code> · [1, 12]"},
    }
    idx: dict = {}
    for folder in ("renders", "archive_d100"):
        d = B / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.png")):
            m = PF_PAT.match(p.name)
            if not m:
                continue
            P, fam, dose, seed = m.groups()
            if fam in PF_INERT:
                continue
            idx.setdefault(P, {}).setdefault(seed, {}).setdefault(fam, {})[f"{float(dose):+.3f}"] = f"{folder}/{p.name}"
    # the bench rendered no baseline; the inert families are one (parameter_families_first_result.md §1)
    base = {}
    for P in ("P01", "P02"):
        f = B / "archive_d100" / f"{P}_F_norms_d+1.000_krea2_seed42_00001_.png"
        if f.is_file():
            base[P] = {"42": f"archive_d100/{f.name}"}
    stats = {}
    f = DATA / "parameter_families_ladder.csv"
    if f.is_file():
        for r in csv.DictReader(open(f, encoding="utf-8")):
            stats["|".join((r["prompt"], r["seed"], r["family"], f"{float(r['dose']):+.3f}"))] = \
                f"L {r['L_vs_baseline']} · |d| {r['mean_abs_diff']} · sat {r.get('sat_ratio','')}"
    return {"idx": idx, "base": base, "groups": groups, "order": ["wo", "io", "proj"], "stats": stats,
            "unit": "la famiglia",
            "title": "Preset per famiglia — dal più negativo al più positivo",
            "sub": "benchmark_parameter_families · le tre famiglie che lo strumento riesce davvero a toccare",
            "note": "Il <b>baseline</b> non è un render di questo bench: il bench non ne ha reso nessuno. "
                    "È il modello non perturbato che regalano le tre famiglie inerti, ed esiste al solo "
                    "seme 42 — sugli altri semi la scala non ce l'ha."}


# ----------------------------------------------------------------- centre_push
CP_PAT = re.compile(r"^(P\d\d)_(Block_\d)(pos|neg)_([\d.]+)_krea2_seed(\d+)_")
CP_BASE = re.compile(r"^(P\d\d)_baseline_krea2_seed(\d+)_")
CP_BLOCKS = {"Block_1": "blocchi 0–4", "Block_2": "blocchi 5–9", "Block_3": "blocchi 10–14",
             "Block_4": "blocchi 15–19", "Block_5": "blocchi 20–23", "Block_6": "blocchi 24–27"}
CP_POS = {"Block_1": "estremo (inizio)", "Block_2": "centro", "Block_3": "centro",
          "Block_4": "centro", "Block_5": "centro", "Block_6": "estremo (fine)"}


def scan_centre_push(B: Path) -> dict:
    d = B / "renders"
    idx: dict = {}
    base: dict = {}
    for p in sorted(d.glob("*.png")):
        m = CP_PAT.match(p.name)
        if m:
            P, blk, sign, dose, seed = m.groups()
            v = (-1 if sign == "neg" else 1) * float(dose)
            idx.setdefault(P, {}).setdefault(seed, {}).setdefault(blk, {})[f"{v:+.3f}"] = f"renders/{p.name}"
            continue
        m = CP_BASE.match(p.name)
        if m:
            P, seed = m.groups()
            base.setdefault(P, {})[seed] = f"renders/{p.name}"
    # the determinism row is a single render on a seed of its own, with no baseline: it is a guard,
    # not a rung, and it would show up as an almost empty seed in the picker.
    for P in list(idx):
        for seed in list(idx[P]):
            if seed not in base.get(P, {}):
                del idx[P][seed]
    groups = {b: {"title": f"{b} — {CP_BLOCKS[b]}",
                  "meta": f"{CP_POS[b]}<br><code>gruppo nominale, raggruppamento posizionale</code>"}
              for b in CP_BLOCKS}
    # per-render L, from the cache the pre-registered analysis already built
    stats = {}
    plan, meas = DATA / "centre_push_plan.csv", DATA / "centre_push_measures.csv"
    if plan.is_file() and meas.is_file():
        M = {r["file"]: r for r in csv.DictReader(open(meas, encoding="utf-8"))}
        rows = list(csv.DictReader(open(plan, encoding="utf-8")))
        bf = {(r["prompt_id"], r["seed"]): r["expected_filename"] for r in rows if r["arm"] == "baseline"}
        for r in rows:
            if r["arm"] != "push":
                continue
            fn, b = r["expected_filename"], bf.get((r["prompt_id"], r["seed"]))
            if fn in M and b in M:
                L = float(M[fn]["coherence"]) / float(M[b]["coherence"])
                stats["|".join((r["prompt_id"], r["seed"], r["block_input"], f"{float(r['gain']):+.3f}"))] = \
                    f"L {L:.4f}"
    return {"idx": idx, "base": base, "groups": groups, "order": sorted(CP_BLOCKS), "stats": stats,
            "unit": "il blocco",
            "title": "Preset per blocco — dal più negativo al più positivo",
            "sub": "benchmark_centre_push · sei gruppi di blocchi, otto dosi da −0.500 a +0.500",
            "note": "Il <b>baseline</b> è un render vero di questo bench, uno per prompt e per seme. "
                    "<b>Su questo bench il tuo veto a occhio ha già bocciato <code>L</code></b> "
                    "(7 accordi su 9, soglia 8) e su <code>Block_6 pos 0.080</code> e "
                    "<code>Block_1 neg 0.500</code> l'ha trovata invertita: se accendi i numeri, "
                    "tienilo presente."}


BENCHES = {"parameter_families": scan_parameter_families, "centre_push": scan_centre_push}


def thumbs(B: Path, files: set[str]) -> None:
    from PIL import Image
    out = B / "_thumbs"
    out.mkdir(exist_ok=True)
    n = 0
    for rel in sorted(files):
        dst = out / (rel.replace("/", "__").rsplit(".", 1)[0] + ".jpg")
        if dst.exists():
            continue
        im = Image.open(B / rel).convert("RGB")
        im.thumbnail((360, 360 * im.height // im.width), Image.LANCZOS)
        im.save(dst, quality=86)
        n += 1
    print(f"  {n} nuove miniature ({len(files)} in totale) -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bench", choices=sorted(BENCHES))
    a = ap.parse_args()
    B = bench_dir("benchmark_" + a.bench)
    cfg = BENCHES[a.bench](B)

    files = set()
    for P in cfg["idx"]:
        for s in cfg["idx"][P]:
            for g in cfg["idx"][P][s]:
                files |= set(cfg["idx"][P][s][g].values())
    for P in cfg["base"]:
        files |= set(cfg["base"][P].values())
    if not files:
        sys.exit("no renders found")
    thumbs(B, files)

    html = (TEMPLATE
            .replace("/*__MANIFEST__*/", json.dumps(cfg, separators=(",", ":")))
            .replace("__TITLE__", cfg["title"])
            .replace("__SUB__", cfg["sub"])
            .replace("__NOTE__", cfg["note"]))
    (B / "presets.html").write_text(html, encoding="utf-8")
    print(f"  presets.html -> {B}")
    for P in sorted(cfg["idx"]):
        for s in sorted(cfg["idx"][P]):
            print(f"    {P} seme {s}: " + ", ".join(
                f"{g} {len(cfg['idx'][P][s][g])} gradini" for g in cfg["order"] if g in cfg["idx"][P][s])
                + ("" if cfg["base"].get(P, {}).get(s) else "  (nessun baseline a questo seme)"))


TEMPLATE = r"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root{--bg:#131316;--panel:#1d1d21;--line:#32323a;--ink:#e9e9ec;--dim:#9797a1;
        --surround:#6e6e73;--neg:#d9744a;--pos:#5b9dd9;--base:#4caf7d;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
  .wrap{max-width:1500px;margin:0 auto;padding:22px 18px 120px}
  h1{font-size:23px;margin:0 0 4px;letter-spacing:-.01em}
  h2{font-size:18px;margin:0 0 2px}
  .sub{color:var(--dim);font-size:13px;margin:0}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px}
  code{font:13px ui-monospace,Menlo,Consolas,monospace;background:#2a2a30;padding:1px 5px;border-radius:4px}
  kbd{background:#33333a;border:1px solid #45454d;border-bottom-width:2px;border-radius:4px;padding:1px 6px;
      font:12px ui-monospace,monospace}
  button,select{font:inherit;color:inherit;background:#2c2c34;border:1px solid var(--line);
                border-radius:8px;padding:8px 14px;cursor:pointer}
  button:hover{background:#383842}
  button.on{background:#3d4a44;border-color:#4caf7d}
  .bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:0 0 18px}
  .bar .grow{flex:1}
  .ladder{display:flex;gap:10px;flex-wrap:wrap;padding:4px 0 10px;align-items:flex-start}
  .ladder.onerow{flex-wrap:nowrap;overflow-x:auto}
  .rung{flex:0 0 var(--rw,260px);background:#191920;border:1px solid var(--line);border-radius:9px;overflow:hidden}
  .rung.isbase{border-color:#3d6b56}
  .rung img{width:100%;display:block;cursor:zoom-in;background:var(--surround)}
  .lab{display:flex;justify-content:space-between;align-items:center;padding:7px 9px;
       font:600 13px ui-monospace,monospace;border-bottom:1px solid var(--line)}
  .lab .d{font-size:14px}
  .neg{color:var(--neg)} .pos{color:var(--pos)} .bas{color:var(--base)}
  .stats{font:11px ui-monospace,monospace;color:var(--dim);padding:5px 9px;border-top:1px solid var(--line)}
  textarea{width:100%;border:0;border-top:1px solid var(--line);background:#111116;color:var(--ink);
           padding:9px;font:13px/1.5 ui-sans-serif,system-ui,sans-serif;resize:vertical;min-height:84px}
  textarea:focus{outline:2px solid #4a4a58;outline-offset:-2px}
  textarea.filled{background:#121a16}
  .famhead{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin:0 0 10px;flex-wrap:wrap}
  .meta{font:12px ui-monospace,monospace;color:var(--dim);text-align:right}
  .hint{color:var(--dim);font-size:13px}
  .hide{display:none}
  #ov{position:fixed;inset:0;background:#000;z-index:50;display:none}
  #ov.show{display:block}
  #ovimg{position:absolute;image-rendering:auto;cursor:grab}
  #ovbar{position:fixed;left:0;right:0;bottom:0;background:#0d0d10ee;border-top:1px solid var(--line);
         padding:10px 14px;display:flex;gap:12px;align-items:center;z-index:51;flex-wrap:wrap}
  #ovbar textarea{flex:1;min-width:280px;min-height:52px;border:1px solid var(--line);border-radius:7px}
  #ovlab{font:600 14px ui-monospace,monospace;min-width:190px}
  .nav{position:fixed;top:0;bottom:90px;width:96px;z-index:52;border:0;border-radius:0;
       background:linear-gradient(90deg,#000a,#0000);display:flex;flex-direction:column;
       align-items:center;justify-content:center;gap:8px;opacity:.35;transition:opacity .12s;padding:0}
  .nav:hover{opacity:1;background:linear-gradient(90deg,#000c,#0004)}
  .nav.r{left:auto;right:0;background:linear-gradient(270deg,#000a,#0000)}
  .nav.r:hover{background:linear-gradient(270deg,#000c,#0004)}
  .nav{left:0}
  .nav .ar{font-size:46px;line-height:1;font-weight:300}
  .nav .to{font:600 13px ui-monospace,monospace;color:#cfcfd6;text-align:center;padding:0 6px}
  .nav[disabled]{opacity:.08;cursor:default;background:none}
  #ov.show .nav{display:flex}
</style>
</head>
<body>
<div class="wrap">
  <h1>__TITLE__</h1>
  <p class="sub">__SUB__</p>

  <div class="card" style="margin-top:16px">
    <p style="margin:0 0 9px"><b>Clicca una miniatura per aprire il render vero a 1:1.</b>
      Nell'ingrandimento: le <b>frecce ai due lati</b> — o <kbd>←</kbd> <kbd>→</kbd> — passano al
      preset vicino e ne mostrano il valore, <kbd>B</kbd> alterna con il baseline (tienilo premuto e
      rilascialo), <kbd>Esc</kbd> chiude. Puoi scrivere gli appunti anche da lì.</p>
    <p style="margin:0 0 9px" class="hint"><b>Il punto in cui hai trascinato l'immagine non si
      muove quando cambi preset:</b> la stessa regione resta sotto l'occhio, ed è l'unico modo di
      vedere le differenze piccole — se l'immagine si ricentrasse a ogni passo non staresti
      confrontando niente.</p>
    <p style="margin:0 0 9px" class="hint">Le miniature sono ridotte: servono solo a navigare. Su
      grana, tratto e artefatti decide solo il 1:1 — è il difetto 78, e il rimedio è tuo.</p>
    <p style="margin:0 0 9px" class="hint">__NOTE__</p>
    <p style="margin:0" class="hint"><b>La mia lettura di questi render non è in questa pagina, apposta.</b>
      Ti sto chiedendo cosa vedi; dirtelo prima è il modo di ancorare un osservatore. I numeri
      misurati stanno dietro l'interruttore qui sotto, spenti per la stessa ragione — e uno di quei
      numeri, <code>L</code>, ieri ha sbagliato segno su unità che sei tu ad aver chiamato rotte.</p>
  </div>

  <div class="bar">
    <label>prompt <select id="prompt"></select></label>
    <label>seme <select id="seed"></select></label>
    <button id="tstats">Mostra i numeri misurati</button>
    <label>miniature <select id="size"><option value="200">piccole</option><option value="260" selected>medie</option><option value="340">grandi</option></select></label>
    <button id="onerow">Una riga sola</button>
    <span class="grow"></span>
    <span class="hint" id="count"></span>
    <button id="exp">Esporta gli appunti</button>
  </div>

  <div id="fams"></div>

  <div class="card hide" id="expcard">
    <div class="bar" style="margin:0 0 10px">
      <button id="copy">Copia</button><button id="dl">Scarica .md</button>
      <button id="closeexp">Chiudi</button>
    </div>
    <textarea id="expbox" style="min-height:320px;border:1px solid var(--line);border-radius:8px;
              font:13px ui-monospace,Menlo,Consolas,monospace"></textarea>
  </div>
</div>

<div id="ov">
  <img id="ovimg" alt="">
  <button class="nav" id="ovprev"><span class="ar">&#8249;</span><span class="to"></span></button>
  <button class="nav r" id="ovnext"><span class="ar">&#8250;</span><span class="to"></span></button>
  <div id="ovbar">
    <span id="ovlab"></span>
    <button id="ovbase">baseline (B)</button>
    <button id="ovfit">adatta / 1:1</button>
    <textarea id="ovnote" placeholder="cosa sta succedendo qui…"></textarea>
    <button id="ovclose">chiudi (Esc)</button>
  </div>
</div>

<script>
const M = /*__MANIFEST__*/;
const store = "param_families_notes_v1";
let notes = {};
try { notes = JSON.parse(localStorage.getItem(store) || "{}"); } catch (e) { notes = {}; }
const save = () => { try { localStorage.setItem(store, JSON.stringify(notes)); } catch (e) {} };

const $ = s => document.querySelector(s);
const thumb = rel => "_thumbs/" + rel.replace(/\//g, "__").replace(/\.png$/, ".jpg");
const nkey = (fam, dose) => fam + "|" + dose;              // the note belongs to the PRESET
const fkey = fam => fam + "|__family__";
let showStats = false, P = "P01", S = "42", flat = [], ovi = -1, fit = false;

for (const p of Object.keys(M.idx).sort()) $("#prompt").add(new Option(p, p));
function seedOpts() {
  $("#seed").innerHTML = "";
  for (const s of Object.keys(M.idx[P]).sort((a, b) => a - b)) $("#seed").add(new Option("seed " + s, s));
  if (!M.idx[P][S]) S = Object.keys(M.idx[P]).sort((a, b) => a - b)[0];
  $("#seed").value = S;
}

function nTotal() {
  const all = new Set();
  for (const p of Object.keys(M.idx)) for (const s of Object.keys(M.idx[p]))
    for (const f of Object.keys(M.idx[p][s])) for (const d of Object.keys(M.idx[p][s][f])) all.add(f + "|" + d);
  let n = 0; for (const k of all) if ((notes[k] || "").trim()) n++;
  return [n, all.size];
}

function render() {
  const host = $("#fams"); host.innerHTML = "";
  for (const fam of M.order) {
    const rungs = (M.idx[P][S] || {})[fam]; if (!rungs) continue;
    const info = M.groups[fam];
    const card = document.createElement("div"); card.className = "card";
    const doses = Object.keys(rungs).sort((a, b) => parseFloat(a) - parseFloat(b));
    const bRel = (M.base[P] || {})[S] || null;
    const items = [];
    let inserted = false;
    for (const d of doses) {
      if (!inserted && bRel && parseFloat(d) > 0) { items.push(["BASE", bRel]); inserted = true; }
      items.push([d, rungs[d]]);
    }
    const hasBase = !!bRel;
    const shown = hasBase ? items : items.filter(i => i[0] !== "BASE");

    card.innerHTML = `<div class="famhead">
        <div><h2>${info.title}</h2>
          <p class="sub">${shown.length} gradini${hasBase ? ", baseline al centro" : " — nessun baseline a questo seme"}</p></div>
        <div class="meta">${info.meta}</div></div>`;
    const lad = document.createElement("div"); lad.className = "ladder";

    shown.forEach(([d, rel]) => {
      const isB = d === "BASE";
      const el = document.createElement("div");
      el.className = "rung" + (isB ? " isbase" : "");
      const cls = isB ? "bas" : (parseFloat(d) < 0 ? "neg" : "pos");
      const st = M.stats[[P, S, fam, d].join("|")];
      el.innerHTML = `<div class="lab"><span class="d ${cls}">${isB ? "BASELINE" : d}</span>
          <span class="hint">${isB ? "non perturbato" : fam}</span></div>
        <img loading="lazy" src="${thumb(rel)}" alt="">
        ${st && !isB ? `<div class="stats ${showStats ? "" : "hide"}">${st}</div>` : ""}`;
      const im = el.querySelector("img");
      im.onclick = () => openOv(shown, shown.indexOf(shown.find(x => x[0] === d)), fam);
      if (!isB) {
        const ta = document.createElement("textarea");
        ta.placeholder = "cosa sta succedendo qui…";
        ta.value = notes[nkey(fam, d)] || "";
        if (ta.value.trim()) ta.classList.add("filled");
        ta.oninput = () => { notes[nkey(fam, d)] = ta.value; save();
                             ta.classList.toggle("filled", !!ta.value.trim()); tally(); };
        el.appendChild(ta);
      }
      lad.appendChild(el);
    });
    card.appendChild(lad);
    const fta = document.createElement("textarea");
    fta.placeholder = M.unit + " nel suo insieme: che cosa compra, e a che prezzo…";
    fta.style.marginTop = "10px"; fta.style.border = "1px solid var(--line)"; fta.style.borderRadius = "8px";
    fta.value = notes[fkey(fam)] || "";
    fta.oninput = () => { notes[fkey(fam)] = fta.value; save(); };
    card.appendChild(fta);
    host.appendChild(card);
  }
  tally();
  const on = $("#onerow").classList.contains("on");
  if (on) document.querySelectorAll(".ladder").forEach(l => l.classList.add("onerow"));
}

function tally() { const [n, t] = nTotal(); $("#count").textContent = n + " preset annotati su " + t; }

// ---------------------------------------------------------------- 1:1 overlay
let pos = null;                 // pan offset, KEPT across steps: the same region must stay
                                // under the eye, otherwise flicking between two doses compares
                                // nothing and the small differences are exactly what is lost.
function openOv(items, i, fam) {
  flat = items.map(([d, rel]) => ({ d, rel, fam }));
  ovi = i; fit = false; pos = null; $("#ov").classList.add("show"); drawOv();
}
function step(n) { const j = ovi + n; if (j < 0 || j >= flat.length) return; ovi = j; drawOv(); }
function arrows() {
  const lab = k => { const it = flat[k]; return it ? (it.d === "BASE" ? "BASELINE" : it.d) : ""; };
  $("#ovprev").disabled = ovi <= 0;
  $("#ovnext").disabled = ovi >= flat.length - 1;
  $("#ovprev").querySelector(".to").textContent = lab(ovi - 1);
  $("#ovnext").querySelector(".to").textContent = lab(ovi + 1);
}
function drawOv() {
  const it = flat[ovi]; if (!it) return;
  const im = $("#ovimg");
  im.src = it.rel;
  im.onload = () => place();
  im.onerror = () => { $("#ovlab").textContent += "  — immagine non trovata"; };
  $("#ovlab").textContent = (it.d === "BASE" ? "BASELINE" : it.fam + "  " + it.d);
  const dis = it.d === "BASE";
  $("#ovnote").disabled = dis;
  $("#ovnote").value = dis ? "" : (notes[nkey(it.fam, it.d)] || "");
  $("#ovnote").placeholder = dis ? "il baseline non si annota" : "cosa sta succedendo qui…";
  arrows();
}
function place() {
  const im = $("#ovimg");
  if (fit) {
    // never above 1:1 - "fit" may shrink to show the whole frame, it must never invent pixels
    const k = Math.min(1, innerWidth / im.naturalWidth, (innerHeight - 90) / im.naturalHeight);
    im.style.width = (im.naturalWidth * k) + "px"; im.style.height = "auto";
    im.style.left = ((innerWidth - im.naturalWidth * k) / 2) + "px"; im.style.top = "0px";
  } else {
    im.style.width = im.naturalWidth + "px"; im.style.height = "auto";
    if (pos === null) pos = {left: (innerWidth - im.naturalWidth) / 2,
                             top: (innerHeight - 90 - im.naturalHeight) / 2};
    im.style.left = pos.left + "px"; im.style.top = pos.top + "px";
  }
}
$("#ovfit").onclick = () => { fit = !fit; if (!fit) pos = null; place(); };
$("#ovprev").onclick = () => step(-1);
$("#ovnext").onclick = () => step(1);
$("#ovclose").onclick = () => $("#ov").classList.remove("show");
$("#ovnote").oninput = () => { const it = flat[ovi]; if (it && it.d !== "BASE") {
  notes[nkey(it.fam, it.d)] = $("#ovnote").value; save(); } };
let baseHeld = null;
const baseRel = () => (M.base[P] || {})[S] || null;
$("#ovbase").onmousedown = () => { const b = baseRel(); if (!b) return;
  baseHeld = $("#ovimg").src; $("#ovimg").src = b; };
$("#ovbase").onmouseup = $("#ovbase").onmouseleave = () => { if (baseHeld) { $("#ovimg").src = baseHeld; baseHeld = null; } };

// Drag to pan. Pointer events with capture, and the browser's own image drag suppressed:
// a plain mousedown/mousemove/mouseup on an <img> starts native HTML5 drag-and-drop, which eats
// the mouseup, leaves the handler stuck in "down" and makes the image jump on the next click.
(function () {
  const im = $("#ovimg");
  im.draggable = false;
  im.addEventListener("dragstart", e => e.preventDefault());
  let drag = null;
  im.addEventListener("pointerdown", e => {
    if (fit || pos === null) return;
    e.preventDefault();
    im.setPointerCapture(e.pointerId);
    drag = {x: e.clientX - pos.left, y: e.clientY - pos.top};
    im.style.cursor = "grabbing";
  });
  im.addEventListener("pointermove", e => {
    if (!drag) return;
    pos = {left: e.clientX - drag.x, top: e.clientY - drag.y};
    im.style.left = pos.left + "px"; im.style.top = pos.top + "px";
  });
  const end = e => { if (!drag) return; drag = null; im.style.cursor = "grab";
                     try { im.releasePointerCapture(e.pointerId); } catch (_) {} };
  im.addEventListener("pointerup", end);
  im.addEventListener("pointercancel", end);
})();

addEventListener("keydown", e => {
  if (!$("#ov").classList.contains("show")) return;
  if (document.activeElement === $("#ovnote") && e.key !== "Escape") return;
  if (e.key === "Escape") $("#ov").classList.remove("show");
  else if (e.key === "ArrowLeft") step(-1);
  else if (e.key === "ArrowRight") step(1);
  else if (e.key.toLowerCase() === "b" && !e.repeat) {
    const b = baseRel(); if (!b) return;
    baseHeld = $("#ovimg").src; $("#ovimg").src = b; }
});
addEventListener("keyup", e => { if (e.key.toLowerCase() === "b" && baseHeld) {
  $("#ovimg").src = baseHeld; baseHeld = null; } });

// ---------------------------------------------------------------- controls
$("#prompt").onchange = () => { P = $("#prompt").value; seedOpts(); render(); };
$("#seed").onchange = () => { S = $("#seed").value; render(); };
$("#size").onchange = () => document.documentElement.style.setProperty("--rw", $("#size").value + "px");
$("#onerow").onclick = () => { const on = !document.querySelector(".ladder").classList.contains("onerow");
  document.querySelectorAll(".ladder").forEach(l => l.classList.toggle("onerow", on));
  $("#onerow").classList.toggle("on", on); };
$("#tstats").onclick = () => { showStats = !showStats;
  $("#tstats").classList.toggle("on", showStats);
  $("#tstats").textContent = showStats ? "Nascondi i numeri misurati" : "Mostra i numeri misurati";
  render(); };

$("#exp").onclick = () => {
  let out = "# Appunti sui preset — " + M.sub + "\n\n";
  for (const fam of M.order) {
    const info = M.groups[fam];
    out += `## ${info.title}\n\n- ${info.meta.replace(/<br>/g, " · ").replace(/<\/?code>/g, "`")}\n\n`;
    const seen = new Set();
    for (const p of Object.keys(M.idx)) for (const s of Object.keys(M.idx[p]))
      for (const d of Object.keys((M.idx[p][s] || {})[fam] || {})) seen.add(d);
    for (const d of [...seen].sort((a, b) => parseFloat(a) - parseFloat(b))) {
      const t = (notes[nkey(fam, d)] || "").trim();
      out += `**${d}** — ${t || "_(nessun appunto)_"}\n\n`;
    }
    const f = (notes[fkey(fam)] || "").trim();
    if (f) out += `**${M.unit.charAt(0).toUpperCase() + M.unit.slice(1)} nel suo insieme** — ${f}\n\n`;
  }
  $("#expbox").value = out; $("#expcard").classList.remove("hide");
  $("#expcard").scrollIntoView({behavior: "smooth"});
};
$("#closeexp").onclick = () => $("#expcard").classList.add("hide");
$("#copy").onclick = () => { $("#expbox").select(); document.execCommand("copy"); $("#copy").textContent = "copiato"; };
$("#dl").onclick = () => { const b = new Blob([$("#expbox").value], {type: "text/markdown"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(b);
  a.download = "appunti_parameter_families.md"; a.click(); };

P = $("#prompt").value; seedOpts(); render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
