# -*- coding: utf-8 -*-
"""
experiments/build_parameter_families_page.py
============================================
A local page for reading `benchmark_parameter_families` by eye: every preset of every live family,
laid out from its most negative dose to its most positive, with a notes field under each.

    python experiments/build_parameter_families_page.py

Writes `presets.html` and `_thumbs/` into the bench folder. It scans `renders/` and `archive_d100/`
rather than trusting a plan, so the ladder it shows is the one that exists on disk. The thumbnails
are for navigation only; clicking one opens the real PNG at 1:1.

The analyst's own reading of these renders is deliberately NOT in the page. Alessandro is being
asked what he sees; telling him first is how an observer gets anchored.

No render is generated.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BENCH = None
for c in (Path("/sessions/rcw-01fzmivsryy2r8cd26detdrb/mnt/benchmark_parameter_families"),
          Path("C:/StabilityMatrix-win-x64/Data/Images/Text2Img/benchmark_parameter_families")):
    if c.is_dir():
        BENCH = c
        break
if BENCH is None:
    sys.exit("bench folder not found")

PAT = re.compile(r"^(P\d\d)_F_([a-z]+)_d([+-][\d.]+)_krea2_seed(\d+)_")
INERT = ("norms", "qknorm", "mod")
BASE = {"P01": "archive_d100/P01_F_norms_d+1.000_krea2_seed42_00001_.png",
        "P02": "archive_d100/P02_F_norms_d+1.000_krea2_seed42_00001_.png"}
FAMILIES = {
    "wo":   {"title": "F_wo — attention output projection", "tensors": 28, "params": 1056964608,
             "keys": "blocks.N.attn.wo.weight", "shape": "[6144, 6144]"},
    "io":   {"title": "F_io — latent interface", "tensors": 2, "params": 786432,
             "keys": "first.weight, last.linear.weight", "shape": "[6144, 64], [64, 6144]"},
    "proj": {"title": "F_proj — the twelve-parameter router", "tensors": 1, "params": 12,
             "keys": "txtfusion.projector.weight", "shape": "[1, 12]"},
}


def thumbs(files: set[str]) -> None:
    from PIL import Image
    out = BENCH / "_thumbs"
    out.mkdir(exist_ok=True)
    n = 0
    for rel in sorted(files):
        dst = out / (rel.replace("/", "__").rsplit(".", 1)[0] + ".jpg")
        if dst.exists():
            continue
        im = Image.open(BENCH / rel).convert("RGB")
        im.thumbnail((360, 360 * im.height // im.width), Image.LANCZOS)
        im.save(dst, quality=86)
        n += 1
    print(f"  {n} new thumbnails ({len(files)} total) -> {out}")


def main() -> None:
    lad = {}
    f = DATA / "parameter_families_ladder.csv"
    if f.is_file():
        for r in csv.DictReader(open(f, encoding="utf-8")):
            lad[(r["prompt"], r["family"], f"{float(r['dose']):+.3f}")] = {
                "L": r["L_vs_baseline"], "d": r["mean_abs_diff"],
                "b0": r.get("band0_ratio", ""), "sat": r.get("sat_ratio", "")}

    idx: dict = {}
    files = set()
    for folder in ("renders", "archive_d100"):
        for p in sorted((BENCH / folder).glob("*.png")):
            m = PAT.match(p.name)
            if not m:
                continue
            P, fam, dose, seed = m.groups()
            if fam in INERT:
                continue
            rel = f"{folder}/{p.name}"
            idx.setdefault(P, {}).setdefault(seed, {}).setdefault(fam, {})[f"{float(dose):+.3f}"] = rel
            files.add(rel)
    files |= set(BASE.values())
    thumbs(files)

    manifest = {"idx": idx, "base": BASE, "fam": FAMILIES, "stats": {
        "|".join(k): v for k, v in lad.items()}}
    html = TEMPLATE.replace("/*__MANIFEST__*/", json.dumps(manifest, separators=(",", ":")))
    (BENCH / "presets.html").write_text(html, encoding="utf-8")
    print(f"  presets.html -> {BENCH} (open it in a browser)")
    for P in sorted(idx):
        for s in sorted(idx[P]):
            print(f"    {P} seed {s}: " + ", ".join(
                f"{fam} {len(idx[P][s][fam])} rungs" for fam in sorted(idx[P][s])))


TEMPLATE = r"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Preset per famiglia — appunti</title>
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
</style>
</head>
<body>
<div class="wrap">
  <h1>Preset per famiglia — dal più negativo al più positivo</h1>
  <p class="sub">benchmark_parameter_families · le tre famiglie che lo strumento riesce davvero a toccare</p>

  <div class="card" style="margin-top:16px">
    <p style="margin:0 0 9px"><b>Clicca una miniatura per aprire il render vero a 1:1.</b>
      Nell'ingrandimento: <kbd>←</kbd> <kbd>→</kbd> scorrono la scala, <kbd>B</kbd> alterna con il
      baseline (tienilo premuto e rilascialo per vedere cosa cambia), <kbd>Esc</kbd> chiude. Puoi
      scrivere gli appunti anche da lì.</p>
    <p style="margin:0 0 9px" class="hint">Le miniature sono ridotte: servono solo a navigare. Su
      grana, tratto e artefatti decide solo il 1:1 — è il difetto 78, e il rimedio è tuo.</p>
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
  for (const fam of ["wo", "io", "proj"]) {
    const rungs = M.idx[P][S][fam]; if (!rungs) continue;
    const info = M.fam[fam];
    const card = document.createElement("div"); card.className = "card";
    const doses = Object.keys(rungs).sort((a, b) => parseFloat(a) - parseFloat(b));
    const items = [];
    let inserted = false;
    for (const d of doses) {
      if (!inserted && parseFloat(d) > 0) { items.push(["BASE", M.base[P]]); inserted = true; }
      items.push([d, rungs[d]]);
    }
    const hasBase = S === "42";
    const shown = hasBase ? items : items.filter(i => i[0] !== "BASE");

    card.innerHTML = `<div class="famhead">
        <div><h2>${info.title}</h2>
          <p class="sub">${shown.length} gradini${hasBase ? ", baseline al centro" : " — nessun baseline a questo seme"}</p></div>
        <div class="meta">${info.tensors} tensori · ${info.params.toLocaleString("it")} parametri<br>
          <code>${info.keys}</code> · ${info.shape}</div></div>`;
    const lad = document.createElement("div"); lad.className = "ladder";

    shown.forEach(([d, rel]) => {
      const isB = d === "BASE";
      const el = document.createElement("div");
      el.className = "rung" + (isB ? " isbase" : "");
      const cls = isB ? "bas" : (parseFloat(d) < 0 ? "neg" : "pos");
      const st = M.stats[[P, fam, d].join("|")];
      el.innerHTML = `<div class="lab"><span class="d ${cls}">${isB ? "BASELINE" : d}</span>
          <span class="hint">${isB ? "non perturbato" : fam}</span></div>
        <img loading="lazy" src="${thumb(rel)}" alt="">
        ${st && !isB ? `<div class="stats ${showStats ? "" : "hide"}">L ${st.L} · |d| ${st.d} · sat ${st.sat}</div>` : ""}`;
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
    fta.placeholder = "la famiglia nel suo insieme: che cosa compra, e a che prezzo…";
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
function openOv(items, i, fam) {
  flat = items.map(([d, rel]) => ({ d, rel, fam }));
  ovi = i; fit = false; $("#ov").classList.add("show"); drawOv();
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
    im.style.left = ((innerWidth - im.naturalWidth) / 2) + "px";
    im.style.top = ((innerHeight - 90 - im.naturalHeight) / 2) + "px";
  }
}
$("#ovfit").onclick = () => { fit = !fit; place(); };
$("#ovclose").onclick = () => $("#ov").classList.remove("show");
$("#ovnote").oninput = () => { const it = flat[ovi]; if (it && it.d !== "BASE") {
  notes[nkey(it.fam, it.d)] = $("#ovnote").value; save(); } };
let baseHeld = null;
$("#ovbase").onmousedown = () => { baseHeld = $("#ovimg").src; $("#ovimg").src = M.base[P]; };
$("#ovbase").onmouseup = $("#ovbase").onmouseleave = () => { if (baseHeld) { $("#ovimg").src = baseHeld; baseHeld = null; } };

// drag to pan
(function () {
  const ov = $("#ov"); let dx = 0, dy = 0, down = false;
  ov.addEventListener("mousedown", e => { if (e.target.id !== "ovimg") return;
    down = true; dx = e.clientX - parseFloat($("#ovimg").style.left || 0);
    dy = e.clientY - parseFloat($("#ovimg").style.top || 0); $("#ovimg").style.cursor = "grabbing"; });
  addEventListener("mousemove", e => { if (!down) return;
    $("#ovimg").style.left = (e.clientX - dx) + "px"; $("#ovimg").style.top = (e.clientY - dy) + "px"; });
  addEventListener("mouseup", () => { down = false; $("#ovimg").style.cursor = "grab"; });
})();

addEventListener("keydown", e => {
  if (!$("#ov").classList.contains("show")) return;
  if (document.activeElement === $("#ovnote") && e.key !== "Escape") return;
  if (e.key === "Escape") $("#ov").classList.remove("show");
  else if (e.key === "ArrowLeft" && ovi > 0) { ovi--; drawOv(); }
  else if (e.key === "ArrowRight" && ovi < flat.length - 1) { ovi++; drawOv(); }
  else if (e.key.toLowerCase() === "b" && !e.repeat) {
    baseHeld = $("#ovimg").src; $("#ovimg").src = M.base[P]; }
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
  let out = "# Appunti sui preset — benchmark_parameter_families\n\n";
  for (const fam of ["wo", "io", "proj"]) {
    const info = M.fam[fam];
    out += `## ${info.title}\n\n- tensori: ${info.tensors}, parametri: ${info.params}, forma: ${info.shape}\n`;
    out += `- chiavi: \`${info.keys}\`\n\n`;
    const seen = new Set();
    for (const p of Object.keys(M.idx)) for (const s of Object.keys(M.idx[p]))
      for (const d of Object.keys((M.idx[p][s] || {})[fam] || {})) seen.add(d);
    for (const d of [...seen].sort((a, b) => parseFloat(a) - parseFloat(b))) {
      const t = (notes[nkey(fam, d)] || "").trim();
      out += `**${d}** — ${t || "_(nessun appunto)_"}\n\n`;
    }
    const f = (notes[fkey(fam)] || "").trim();
    if (f) out += `**La famiglia nel suo insieme** — ${f}\n\n`;
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
