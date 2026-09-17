# -*- coding: utf-8 -*-
"""Foglio visivo delle palette: una riga per condizione, un blocco per prompt."""
import csv, os, html
import numpy as np, cv2
from collections import defaultdict

SRC = os.path.expanduser("~/palette_features_01_steering.csv")
OUT = os.path.expanduser("~/mnt/comfyui-pilot/experiments/palette_sheet.html")
ORDER = ['baseline','preset','preset_half','preset_neg',
         'blockshuffle','blockshuffle_neg','randsign','randsign_neg']

def hexof(L, a, b):
    lab = np.array([[[L, a, b]]], dtype=np.float32)
    bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR).reshape(3)
    bb, g, r = np.clip(bgr, 0, 1) * 255
    return "#{:02x}{:02x}{:02x}".format(int(round(r)), int(round(g)), int(round(bb)))

def circmean(degs):
    h = np.deg2rad(degs)
    return np.arctan2(np.mean(np.sin(h)), np.mean(np.cos(h)))

rows = list(csv.DictReader(open(SRC, encoding='utf-8')))
by = defaultdict(lambda: defaultdict(list))
for r in rows:
    by[r['prompt_dir']][r['condition']].append(r)

def agg(sub, pre):
    """media di L*, C, tinta (circolare) su un gruppo di render -> (hex, L, C, h)"""
    L = np.mean([float(r[pre + '_L']) for r in sub if r[pre + '_L'] != ''])
    C = np.mean([float(r[pre + '_C']) for r in sub if r[pre + '_C'] != ''])
    h = circmean([float(r[pre + '_hue_deg']) for r in sub if r[pre + '_hue_deg'] != ''])
    return hexof(L, C * np.cos(h), C * np.sin(h)), L, C, np.degrees(h) % 360

def chip(hx, L, C, h, label):
    txt = '#111' if L > 55 else '#f5f5f5'
    return (f'<div class="chip" style="background:{hx};color:{txt}">'
            f'<span class="cl">{label}</span>'
            f'<span class="cv">L {L:.0f}</span>'
            f'<span class="cv">C {C:.0f}</span>'
            f'<span class="cv">h {h:.0f}&deg;</span>'
            f'<span class="cx">{hx}</span></div>')

blocks = []
for pd in sorted(by):
    lines = []
    base = by[pd].get('baseline')
    for c in ORDER:
        sub = by[pd].get(c)
        if not sub:
            continue
        cells = [chip(*agg(sub, 'paper'), 'carta')]
        for i in range(1, 7):
            cells.append(chip(*agg(sub, f'sw{i}'), f'sw{i}'))
        cells.append(chip(*agg(sub, 'ink'), 'inchiostro'))
        cs = np.mean([float(r['chroma_spread']) for r in sub])
        d = ''
        if base and c != 'baseline':
            dd = cs - np.mean([float(r['chroma_spread']) for r in base])
            d = f'<span class="d {"up" if dd>0 else "dn"}">{dd:+.1f}</span>'
        lines.append(
            f'<div class="row"><div class="name">{html.escape(c)}'
            f'<span class="n">{len(sub)} seed</span></div>'
            f'<div class="strip">{"".join(cells)}</div>'
            f'<div class="num">{cs:.1f}{d}</div></div>')
    blocks.append(f'<section><h2>{html.escape(pd)}</h2>'
                  f'<div class="sheet">{"".join(lines)}</div></section>')

page = f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Palette per preset</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<style>
:root{{--bg:#fbfaf8;--fg:#1a1815;--mut:#6f6a62;--line:#e3ded6;--card:#fff;--up:#a8442e;--dn:#2f6b56}}
:root:not([data-theme="light"]){{}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#151412;--fg:#ece8e2;--mut:#9a938a;--line:#2e2b27;--card:#1d1b18;--up:#e08a72;--dn:#6fc3a3}}}}
:root[data-theme="dark"]{{--bg:#151412;--fg:#ece8e2;--mut:#9a938a;--line:#2e2b27;--card:#1d1b18;--up:#e08a72;--dn:#6fc3a3}}
*{{box-sizing:border-box}}
body{{margin:0;padding:32px 16px 64px;background:var(--bg);color:var(--fg);
 font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;font-size:14px;line-height:1.5}}
.wrap{{max-width:1180px;margin:0 auto;display:flex;flex-direction:column;gap:36px}}
header p{{color:var(--mut);max-width:62ch;margin:6px 0 0}}
h1{{font-size:26px;font-weight:700;letter-spacing:-.02em;margin:0;text-wrap:balance}}
h2{{font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;
 color:var(--mut);margin:0 0 10px;font-variant-numeric:tabular-nums}}
.warn{{border-left:3px solid var(--up);padding:10px 14px;background:var(--card);
 border-radius:0 6px 6px 0;color:var(--mut);max-width:74ch}}
.sheet{{display:flex;flex-direction:column;gap:6px;background:var(--card);
 border:1px solid var(--line);border-radius:10px;padding:12px;overflow-x:auto}}
.row{{display:grid;grid-template-columns:150px 1fr 74px;gap:12px;align-items:center;min-width:760px}}
.name{{font-weight:500;font-size:13px;display:flex;flex-direction:column}}
.n{{color:var(--mut);font-size:11px;font-weight:400;font-variant-numeric:tabular-nums}}
.strip{{display:grid;grid-template-columns:repeat(8,1fr);gap:3px}}
.chip{{aspect-ratio:1/1.05;border-radius:5px;padding:5px 6px;display:flex;flex-direction:column;
 justify-content:flex-start;font-size:9.5px;line-height:1.3;font-variant-numeric:tabular-nums;
 border:1px solid rgba(128,128,128,.22);overflow:hidden}}
.cl{{font-weight:600;font-size:10px;margin-bottom:2px}}
.cv{{opacity:.82}} .cx{{opacity:.62;margin-top:auto;font-size:9px}}
.num{{text-align:right;font-variant-numeric:tabular-nums;font-weight:600;font-size:13px}}
.d{{display:block;font-weight:500;font-size:11px}} .up{{color:var(--up)}} .dn{{color:var(--dn)}}
@media(max-width:560px){{body{{padding:20px 16px 48px}} h1{{font-size:21px}}}}
</style></head><body><div class="wrap">
<header>
<h1>Palette per preset</h1>
<p>Sei swatch per render &mdash; il pi&ugrave; scuro, il pi&ugrave; chiaro e i quattro pi&ugrave; distanti
in saturazione e tinta &mdash; pi&ugrave; la carta e l&rsquo;inchiostro stimati. Ogni riga &egrave; la media
dei seed di quel prompt in quella condizione. La colonna a destra &egrave; <em>chroma_spread</em>,
con lo scarto rispetto al baseline.</p>
</header>
<div class="warn"><strong>Esplorativo.</strong> Misurato sui webp q82 del repository, non sui PNG
originali, e su 7 prompt &times; 5 seed. Aggregando per prompt (n&nbsp;=&nbsp;7) nessun contrasto
sopravvive alla correzione di Holm: quello che si vede qui va guardato, non ancora creduto.</div>
{''.join(blocks)}
</div></body></html>"""
open(OUT, 'w', encoding='utf-8').write(page)
print("->", OUT, len(page), "byte")
