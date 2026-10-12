"""Grid viewer: many edits of one prompt and seed side by side.

Rows are blocks (or block parts), columns are doses or edit kinds, the baseline sits in the middle
column. One zoom and pan state is shared by every cell, so the same region is compared everywhere.
Three display modes: the render itself, |edit - baseline| as a heat map, and the signed luminance
change (orange = lighter, blue = darker). A focus view scrubs or animates one row (dose axis) or one
column (block axis) and flickers against the baseline.

Display aid only. The numbers it shows (mean |delta| on 0-255, mean signed luminance change, the
high-frequency ratio std(gray - blur1.5) edit/baseline) are computed for the viewer from the renders
and are NOT published measures; nothing here changes a claim.

  python grid_viewer.py --build [--set ranger|split_atlas|te_pilot|te_order|te_genre|te_genre_dose|all] [--img-root PATH] [--budget 160] [--workers 2]
      -> <img-root>/_grid_viewer/{ranger,split_atlas,te_pilot}.html  (+ cache/ with previews and difference maps)

The cache is kept between runs; re-run until it prints "0 left". The pages are rewritten on every run
and show "non pronto" for cells not processed yet.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"
IMG_ROOT = Path(os.environ.get("TEXT2IMG", r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"))
OUT_NAME = "_grid_viewer"
PREVIEW_W = 512
GAIN_ABS = 4.0      # heat map: |delta| * 4 / 255, so a mean channel change of 64 is already white
GAIN_SIGNED = 4.0   # signed map: delta Y * 4 / 255


def rd(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def iid(rel):
    """Cache id of a render: its relative path without the folder separators and the suffix."""
    s = rel.replace("\\", "/").replace("/", "__")
    s = re.sub(r"_krea2_seed(\d+)_00001_\.png$", r"_s\1", s)
    return s


def cell(rel, base, sub="", badge="", note=""):
    if rel is None or not (IMG_ROOT / rel).exists():
        return None
    return {"src": rel.replace("\\", "/"), "base_src": base, "id": iid(rel), "sub": sub,
            "badge": badge, "note": note, "base": rel == base}


# ---------------------------------------------------------------- image work (runs in workers)
def _heat(t):
    t = np.clip(t, 0, 1)
    return (np.stack([np.clip(3 * t, 0, 1), np.clip(3 * t - 1, 0, 1), np.clip(3 * t - 2, 0, 1)], -1) * 255).astype(np.uint8)


def _signed(t):
    t = np.clip(t, -1, 1)
    pos, neg = np.clip(t, 0, 1)[..., None], np.clip(-t, 0, 1)[..., None]
    rgb = pos * np.array([1.0, 0.62, 0.18]) + neg * np.array([0.28, 0.58, 1.0])
    return (rgb * 255).astype(np.uint8)


def _hf(img):
    g = img.convert("L")
    a = np.asarray(g, np.float32) - np.asarray(g.filter(ImageFilter.GaussianBlur(1.5)), np.float32)
    return float(a.std())


def process(job):
    root, cache, rel, base = job
    root, cache = Path(root), Path(cache)
    key = iid(rel)
    outs = {k: cache / f"{k}_{key}.jpg" for k in ("p", "a", "s", "A")}
    meas = cache / f"m_{key}.json"
    is_base = rel == base
    need = [outs["p"]] if is_base else list(outs.values())
    if meas.exists() and all(o.exists() for o in need):
        return key, json.loads(meas.read_text())
    e = Image.open(root / rel).convert("RGB")
    w, h = e.size
    pw, ph = PREVIEW_W, round(h * PREVIEW_W / w)
    e.resize((pw, ph), Image.LANCZOS).save(outs["p"], quality=88)
    if is_base:
        m = {"w": w, "h": h, "mad": 0.0, "dy": 0.0, "hf": 1.0, "p95": 0.0}
    else:
        b = Image.open(root / base).convert("RGB")
        if b.size != e.size:
            b = b.resize(e.size, Image.BICUBIC)
        E, B = np.asarray(e, np.float32), np.asarray(b, np.float32)
        ad = np.abs(E - B).mean(2)
        wy = np.array([0.299, 0.587, 0.114], np.float32)
        dy = E @ wy - B @ wy
        heat = Image.fromarray(_heat(ad * GAIN_ABS / 255))
        heat.save(outs["A"], quality=85)
        heat.resize((pw, ph), Image.BOX).save(outs["a"], quality=88)
        Image.fromarray(_signed(dy * GAIN_SIGNED / 255)).resize((pw, ph), Image.BOX).save(outs["s"], quality=88)
        m = {"w": w, "h": h, "mad": round(float(ad.mean()), 2), "dy": round(float(dy.mean()), 2),
             "hf": round(_hf(e) / max(_hf(b), 1e-6), 3), "p95": round(float(np.percentile(ad, 95)), 1)}
    meas.write_text(json.dumps(m))
    return key, m


# ---------------------------------------------------------------- grids: the ranger (P3_archerforest)
ARCH = "P3_archerforest_{c}_krea2_seed{s}_00001_.png"


def _hood_labels():
    """C54 labels by file (hood_key + hood_tally) and C56 ladder labels by (block, sign, dose)."""
    key = {r["item"]: r["file"] for r in rd("hood_key.csv")}
    c54 = {}
    for r in rd("hood_tally_alessandro.csv"):
        f = key.get(r["item"])
        if f:
            c54[f] = (r["label"], (f"seconda volta: {r['second_label']}" if r.get("second_label") else "")
                      + (f" · vs base: {r['vs_baseline']}" if r.get("vs_baseline") else ""))
    c56 = {(r["block"], r["sign"], r["dose"]): r["label"] for r in rd("hood_threshold_tally.csv")}
    return c54, c56


def _v3_files(seed):
    d = IMG_ROOT / "benchmark_single_blocks_v3" / "renders"
    out = {}
    for f in os.listdir(d):
        m = re.match(rf"P3_archerforest_blk(\d\d)_(neg|pos)_d([\d.]+)_krea2_seed{seed}_00001_\.png$", f)
        if m:
            out.setdefault((int(m[1]), m[2]), []).append((float(m[3]), f"benchmark_single_blocks_v3/renders/{f}"))
    return {k: sorted(v) for k, v in out.items()}


def build_ranger():
    s = "3141592"
    base = f"benchmark_hood_threshold/{ARCH.format(c='baseline', s=s)}"
    c54, c56 = _hood_labels()
    v3 = _v3_files(s)
    lad = [0.01, 0.02, 0.04, 0.08, 0.16]
    grids = []

    def lab54(rel):
        return c54.get(rel, ("", ""))

    # A: dose ladders of the hood (C56) with the far dose of the v3 atlas at both ends
    cols = ["− forte (v3)"] + [f"−{d:.2f}" for d in reversed(lad)] + ["base"] + [f"+{d:.2f}" for d in lad] + ["+ forte (v3)"]
    rows = []
    for b in [0, 10, 20, 23]:
        cells = []
        far = v3.get((b, "neg"), [])
        if far:
            d, rel = far[-1]
            cells.append(cell(rel, base, f"−{d:.3f}", *lab54(rel)))
        else:
            cells.append(None)
        for d in reversed(lad):
            rel = f"benchmark_hood_threshold/{ARCH.format(c=f'blk{b:02d}_neg_d{d:.3f}', s=s)}"
            cells.append(cell(rel, base, f"−{d:.3f}", c56.get((f"blk{b:02d}", "-", f"{d:.3f}"), "")))
        cells.append(cell(base, base, "0", "a metà", "baseline: cappuccio a metà (C54)"))
        for d in lad:
            rel = f"benchmark_hood_threshold/{ARCH.format(c=f'blk{b:02d}_pos_d{d:.3f}', s=s)}"
            cells.append(cell(rel, base, f"+{d:.3f}", c56.get((f"blk{b:02d}", "+", f"{d:.3f}"), "")))
        far = v3.get((b, "pos"), [])
        if far:
            d, rel = far[-1]
            cells.append(cell(rel, base, f"+{d:.3f}", *lab54(rel)))
        else:
            cells.append(None)
        rows.append({"label": f"blocco {b}", "cells": cells})
    grids.append({"id": "hood_ladder", "title": "Ranger · cappuccio: scale di dose (C56) + dose forte (v3)",
                  "note": "Seed 3141592, blocco intero via vettore. Etichette: le tue del test cieco (C56 per la scala, "
                          "C54 per le dosi forti). Le colonne «forte» hanno dosi diverse per blocco: la dose è sotto la cella.",
                  "cols": cols, "rows": rows})

    # B: every block of the v3 atlas, both signs, all doses rendered for this seed
    cols = ["− forte", "− lieve", "base", "+ lieve", "+ forte"]
    rows = []
    for b in range(28):
        cells = []
        for sg in ("neg", "pos"):
            ds = v3.get((b, sg), [])
            strong = ds[-1] if ds else None
            mild = ds[0] if len(ds) > 1 else None
            mk = lambda x: cell(x[1], base, ("−" if sg == "neg" else "+") + f"{x[0]:.3f}", *lab54(x[1])) if x else None
            pair = [mk(strong), mk(mild)] if sg == "neg" else [mk(mild), mk(strong)]
            if sg == "pos":
                cells.append(cell(base, base, "0", "a metà"))
            cells.extend(pair)
        rows.append({"label": f"blocco {b}", "cells": cells})
    grids.append({"id": "all_blocks_v3", "title": "Ranger · tutti i 28 blocchi (atlante v3, dosi calibrate)",
                  "note": "Dosi diverse per blocco (calibrate in stage 1): leggi la dose sotto la cella prima di confrontare due righe. "
                          "«lieve» esiste solo dove il v3 ha due dosi per quel segno.", "cols": cols, "rows": rows})

    # C: block 23 split into attention, MLP and whole, two seeds
    for s2 in ["3141592", "4669201"]:
        b2 = f"benchmark_blk23_colorful/{ARCH.format(c='baseline', s=s2)}"
        cols = ["−1.00", "−0.45", "−0.30", "−0.15", "base", "+0.15", "+0.30", "+1.00"]
        sp = lambda c: f"benchmark_blk23_split/{ARCH.format(c=c, s=s2)}"
        co = lambda c: f"benchmark_blk23_colorful/{ARCH.format(c=c, s=s2)}"
        spec = {
            "attention": [sp("attn_m1.000"), sp("attn_m0.450"), None, None, b2, None, sp("attn_p0.300"), sp("attn_p1.000")],
            "MLP": [sp("mlp_m1.000"), sp("mlp_m0.450"), None, None, b2, None, sp("mlp_p0.300"), sp("mlp_p1.000")],
            "intero": [sp("whole_m1.000"), co("b23_m0.450"), co("b23_m0.300"), co("b23_m0.150"), b2,
                       co("b23_p0.150"), co("b23_p0.300"), sp("whole_p1.000")],
        }
        rows = [{"label": k, "cells": [cell(r, b2, cols[i] if r != b2 else "0", *lab54(r)) if r else None
                                       for i, r in enumerate(v)]} for k, v in spec.items()]
        grids.append({"id": f"blk23_split_{s2}", "title": f"Ranger · blocco 23 diviso, seed {s2}",
                      "note": "Attention e MLP via granular (benchmark_blk23_split), intero via vettore (blk23_colorful) "
                              "o granular a ±1.00. Etichette C54 dove esistono.", "cols": cols, "rows": rows})
    return {"title": "Ranger (P3_archerforest)", "grids": grids}


# ---------------------------------------------------------------- grids: split atlas (C59)
def build_split():
    SA, AT = "benchmark_split_atlas", "benchmark_single_blocks_atlas/renders"
    eye = {}
    for r in rd("split_atlas_eye_tally_alessandro.csv"):
        if r["repeated"] == "0":
            lab = "" if r["lab"].strip(" .*") == "" else r["lab"]
            eye[(int(r["block"]), r["part"], r["sign"])] = (lab, r["note"])
    cols = ["attn −", "MLP −", "intero −", "base", "intero +", "MLP +", "attn +"]
    order = [("attn", "neg"), ("mlp", "neg"), ("whole", "neg"), None, ("whole", "pos"), ("mlp", "pos"), ("attn", "pos")]
    grids = []
    for pid in ["P01_blacksmith", "F4_closeup", "S1_rally"]:
        for seed in ["2718281", "3141592", "4669201"]:
            fn = f"{pid}_baseline_krea2_seed{seed}_00001_.png"
            base = f"{SA}/{fn}" if (IMG_ROOT / SA / fn).exists() else f"{AT}/{fn}"
            rows = []
            for b in range(28):
                cells = []
                for o in order:
                    if o is None:
                        cells.append(cell(base, base, "0"))
                        continue
                    part, sg = o
                    rel = (f"{AT}/{pid}_blk{b:02d}_{sg}_d0.350_krea2_seed{seed}_00001_.png" if part == "whole"
                           else f"{SA}/{pid}_blk{b:02d}_{part}_{sg}_d0.350_krea2_seed{seed}_00001_.png")
                    lab, note = eye.get((b, part, sg), ("", ""))
                    cells.append(cell(rel, base, ("−" if sg == "neg" else "+") + "0.35", lab, note))
                rows.append({"label": f"blocco {b}", "cells": cells})
            grids.append({"id": f"{pid}_{seed}", "title": f"Atlante diviso · {pid} · seed {seed}",
                          "note": "Dose ±0.35. «intero» esiste solo al seed 2718281 (atlante a dose uguale). Etichette: il tuo "
                                  "test a occhio C59, date per foglio (blocco, parte, segno) su tutti i prompt e seed insieme, "
                                  "quindi uguali in ogni griglia.", "cols": cols, "rows": rows})
    return {"title": "Atlante diviso (C59)", "grids": grids}



# ---------------------------------------------------------------- grids: text-encoder pilot (C64)
def _te_labels():
    """Badge per render from the C64 eye labels, once they exist: text / arm / number of traits changed."""
    if (DATA / "te_pilot_phase1_joined.csv").exists():  # phase 1 (doses +-1.00): quick verdict per render
        out = {}
        for r in rd("te_pilot_phase1_joined.csv"):
            bits = [r["entita"]] + (["stile cambiato"] if r["stile"] == "cambiato" else []) + \
                   ([f"braccio: {r['braccio']}"] if r["braccio"] in ("altro", "ambiguo") else []) + \
                   ([f"sup: {r['dmg']}"] if r["dmg"] not in ("come", "") else [])
            out[r["cond"]] = (" · ".join(bits), (r["stilenote"] + " " + r["note"]).strip())
        return out
    lab = DATA / "te_pilot_eye_alessandro.csv"
    if not lab.exists():
        return {}
    key = {r["item"]: r for r in rd("te_pilot_eye_key.csv")}
    out = {}
    for r in rd("te_pilot_eye_alessandro.csv"):
        item = r["slot"].split("#")[0]
        if item not in key or item in out:  # first showing only
            continue
        traits = [k for k in r if k not in ("slot", "touched", "same", "text", "braccio", "stile", "stilenote", "dmg", "note")]
        changed = [k for k in traits if r[k] != "P"]
        bits = []
        if r.get("text") == "1":
            bits.append("TESTO")
        else:
            if changed:
                bits.append(f"{len(changed)} tratti")
            if r.get("braccio") in ("altro", "ambiguo"):
                bits.append("braccio: " + r["braccio"])
            if r.get("dmg") not in ("", "come", None):
                bits.append("sup: " + r["dmg"])
        note = ", ".join(f"{k}={r[k]}" for k in changed) + (f" · {r['note']}" if r.get("note") else "")
        out[key[item]["cond"]] = (" · ".join(bits), note)
    return out


ONSET = {"head": "da che dose cambia lo stile? (− a sinistra, + a destra)",
         "qs": [{"k": "onset_neg", "lab": "lato −", "o": ["0.10", "0.35", "1.00", "mai"]},
                {"k": "onset_pos", "lab": "lato +", "o": ["0.10", "0.35", "1.00", "mai"]}]}


def build_te_pilot():
    F = "benchmark_te_pilot"
    plan = rd("te_pilot_plan.csv")
    by = {(r["unit"], r["part"], r["dose"]): r for r in plan if r["phase"] == "main"}
    base = f"{F}/" + next(r["expected_filename"] for r in plan if r["cond"] == "CHK_repro_baseline")
    labs = _te_labels()
    doses = ["-1.0", "-0.35", "-0.1", "0", "0.1", "0.35", "1.0"]
    cols = ["−1.00", "−0.35", "−0.10", "base", "+0.10", "+0.35", "+1.00"]

    def mk(unit, part):
        cells = []
        for d, c in zip(doses, cols):
            if d == "0":
                cells.append(cell(base, base, "0"))
                continue
            r = by.get((unit, part, d))
            lab = labs.get(r["cond"], ("", "")) if r else ("", "")
            cells.append(cell(f"{F}/{r['expected_filename']}", base, c, *lab) if r else None)
        return cells

    layers = sorted({u for (u, p, _) in by if p == "attn"})
    note = ("Elfa P1, seed 1618033. Modifica dei pesi del text encoder Qwen3-VL x(1+d), via ArthemyKrea2CLIPTuner. "
            "Krea-2 legge l'ingresso dei layer 2, 5, ..., 35: una modifica al layer L arriva a tutte le letture dopo L. "
            "Etichette: il tuo test a occhio fase 1 (solo dosi ±1.00); passa il mouse sulla cella per la nota.")
    grids = [
        {"id": "te_attn", "title": "C64 · attention (q, k, v, o) per layer", "note": note,
         "cols": cols, "rows": [{"label": u, "cells": mk(u, "attn")} for u in layers], "notes": ONSET},
        {"id": "te_mlp", "title": "C64 · MLP (gate, up, down) per layer", "note": note,
         "cols": cols, "rows": [{"label": u, "cells": mk(u, "mlp")} for u in layers], "notes": ONSET},
        {"id": "te_both", "title": "C64 · attention e MLP alternate per layer", "note": note + " Righe alternate: attn, MLP.",
         "cols": cols, "rows": [x for u in layers for x in ({"label": f"{u} attn", "cells": mk(u, "attn")},
                                                              {"label": f"{u} MLP", "cells": mk(u, "mlp")})]},
        {"id": "te_slots", "title": "C64 · slot di testo del DiT (vettore)", "note": "Gli slot 28-33 del DiT che lavorano sul testo, per confronto.",
         "cols": cols, "rows": [{"label": u, "cells": mk(u, "slot")} for u in sorted({u for (u, p, _) in by if p == "slot"})], "notes": ONSET},
    ]
    chk = [r for r in plan if r["phase"] == "check" and r["cond"] != "CHK_repro_baseline"]
    grids.append({"id": "te_checks", "title": "C64 · controlli", "note": "Nulli attesi: L35 (mai letto) e torre visiva. "
                  "Attivo atteso: L02 MLP. q+k: previsione di nullità falsificata (circa 10/255).",
                  "cols": ["base"] + [r["cond"].replace("CHK_", "") for r in chk],
                  "rows": [{"label": "controlli", "cells": [cell(base, base, "0")] + [cell(f"{F}/{r['expected_filename']}", base, r["dose"]) for r in chk]}]})
    return {"title": "Text encoder (C64)", "grids": grids, "notes_file": "te_pilot_dose_grid_alessandro.csv"}


# ---------------------------------------------------------------- grids: C65 part B, word order (same words, five orders)
def build_te_order():
    plan = rd("te_characters_plan.csv")
    edits = []
    for r in plan:
        if r["phase"] == "order" and r["cond"] not in edits:
            edits.append(r["cond"])
    orders = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
    cols = ["1 · originale", "2 · soggetto prima", "3 · sfondo prima", "4 · azione prima", "5 · inverso"]
    eye = {}
    if (DATA / "te_characters_tests.csv").exists():
        for r in rd("te_order_tests.csv"):
            eye[r["cond"]] = f"cos ordini {r['cos_order']} · cos semi {r['cos_seed']}"
    grids = []
    for seed in ["3141592", "1234567"]:
        base = {v: f"benchmark_prompt_order/{v}_baseline_krea2_seed{seed}_00001_.png" for v in orders}
        rows = [{"label": "originali", "cells": [cell(base[v], base[v], "base") for v in orders]}]
        for k in edits:
            rows.append({"label": k, "cells": [cell(f"benchmark_te_characters/{v}_{k}_krea2_seed{seed}_00001_.png", base[v], k.split("_")[0],
                                                    "", eye.get(k, "")) for v in orders]})
        grids.append({"id": f"te_order_{seed}", "title": f"C65 · ordine delle parole · seed {seed}",
                      "note": "Elfa P1, stesse parole in cinque ordini (colonne). Prima riga: gli originali di ogni ordine; sotto, la stessa "
                              "modifica del text encoder (±1.00) su ciascun ordine. La differenza dalla base è calcolata contro l'originale "
                              "della stessa colonna. Nel tooltip: quanto la modifica concorda tra ordini e tra semi (23 statistiche).",
                      "cols": cols, "rows": rows,
                      "notes": {"head": "quanto cambia con l'ordine? (1 poco · 5 molto)",
                                "qs": [{"k": "score_1_5", "lab": "quanto cambia", "o": ["1", "2", "3", "4", "5"]}]}})
    return {"title": "Ordine delle parole (C65 B)", "grids": grids, "notes_file": "te_order_grid_notes_alessandro.csv"}


GENRES = ["fumetto", "anime", "cartoon", "realist", "pittura", "altro"]


def build_te_genre():
    """C70: the genre of every image of C65 B (word orders), one choice per image. No measurements shown on the page."""
    plan = rd("te_characters_plan.csv")
    edits = []
    for r in plan:
        if r["phase"] == "order" and r["cond"] not in edits:
            edits.append(r["cond"])
    orders = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
    cols = ["1 · originale", "2 · soggetto prima", "3 · sfondo prima", "4 · azione prima", "5 · inverso"]
    grids = []
    for seed in ["3141592", "1234567"]:
        base = {v: f"benchmark_prompt_order/{v}_baseline_krea2_seed{seed}_00001_.png" for v in orders}
        rows = [{"label": "originali", "cells": [cell(base[v], base[v], "base") for v in orders]}]
        for k in edits:
            rows.append({"label": k, "cells": [cell(f"benchmark_te_characters/{v}_{k}_krea2_seed{seed}_00001_.png", base[v], str(i + 1))
                                                for i, v in enumerate(orders)]})
        grids.append({"id": f"te_genre_{seed}", "title": f"C70 · genere di ogni immagine · seed {seed}",
                      "note": "Per ogni immagine (colonne 1-5) scegli il genere che vedi: fumetto occidentale, anime/manga, cartoon, "
                              "realistico o semi-realistico (foto, 3D), pittura (acquerello, olio, digital painting), altro. "
                              "Anche gli originali. Una scelta per immagine; il testo libero è facoltativo.",
                      "cols": cols, "rows": rows,
                      "notes": {"head": "genere per colonna (1-5)", "w": "430px", "cls": "gen",
                                "qs": [{"k": f"g{i}", "lab": str(i), "o": GENRES} for i in range(1, 6)]}})
    return {"title": "Genere delle immagini (C70)", "grids": grids, "notes_file": "te_genre_alessandro.csv"}


def build_te_genre_dose():
    """C70 amendment 2: how far each image moves from the style of the original of its column (0-3), seed 3141592."""
    plan = rd("te_characters_plan.csv")
    edits = []
    for r in plan:
        if r["phase"] == "order" and r["cond"] not in edits:
            edits.append(r["cond"])
    orders = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
    cols = ["1 · originale", "2 · soggetto prima", "3 · sfondo prima", "4 · azione prima", "5 · inverso"]
    seed = "3141592"
    gl = {r["row"]: [r[f"g{i}"] for i in range(1, 6)] for r in rd("te_genre_alessandro.csv") if r["grid"] == f"te_genre_{seed}"}
    base = {v: f"benchmark_prompt_order/{v}_baseline_krea2_seed{seed}_00001_.png" for v in orders}
    rows = [{"label": "originali", "cells": [cell(base[v], base[v], "base · " + gl.get("originali", [""] * 5)[i]) for i, v in enumerate(orders)]}]
    for k in edits:
        rows.append({"label": k, "cells": [cell(f"benchmark_te_characters/{v}_{k}_krea2_seed{seed}_00001_.png", base[v],
                                                f"{i + 1} · {gl.get(k, [''] * 5)[i]}") for i, v in enumerate(orders)]})
    grids = [{"id": f"te_dose_{seed}", "title": f"C70 · quanto si allontana dall'originale · seed {seed}",
              "note": "Per ogni immagine: quanto il suo stile si allontana dall'originale della stessa colonna. "
                      "0 = stesso stile · 1 = deriva leggera (qualche tratto diverso) · 2 = chiaramente un altro stile, con tracce "
                      "dell'originale · 3 = del tutto un altro genere. Sotto ogni immagine il genere che hai già scelto.",
              "cols": cols, "rows": rows,
              "notes": {"head": "intensità per colonna (0-3)", "w": "330px", "cls": "gen",
                        "qs": [{"k": f"d{i}", "lab": str(i), "o": ["0", "1", "2", "3"]} for i in range(1, 6)]}}]
    return {"title": "Intensità del cambio di stile (C70)", "grids": grids, "notes_file": "te_genre_dose_alessandro.csv"}


SETS = {"ranger": build_ranger, "split_atlas": build_split, "te_pilot": build_te_pilot, "te_order": build_te_order, "te_genre": build_te_genre, "te_genre_dose": build_te_genre_dose}


# ---------------------------------------------------------------- build
def build(names, budget, workers):
    out = IMG_ROOT / OUT_NAME
    cache = out / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    left_total = 0
    for name in names:
        board = SETS[name]()
        jobs, seen = [], set()
        for g in board["grids"]:
            for r in g["rows"]:
                for c in r["cells"]:
                    if c and c["id"] not in seen:
                        seen.add(c["id"])
                        jobs.append((str(IMG_ROOT), str(cache), c["src"], c["base_src"]))
        done = {}
        todo = []
        for j in jobs:
            m = cache / f"m_{iid(j[2])}.json"
            if m.exists():
                done[iid(j[2])] = json.loads(m.read_text())
            else:
                todo.append(j)
        with ProcessPoolExecutor(max_workers=workers) as ex:
            i = 0
            while i < len(todo) and time.time() - t0 < budget:
                chunk = todo[i:i + workers * 3]
                for k, m in ex.map(process, chunk):
                    done[k] = m
                i += len(chunk)
        left = len(todo) - i
        left_total += left
        for g in board["grids"]:
            for r in g["rows"]:
                for c in r["cells"]:
                    if c:
                        c["m"] = done.get(c["id"])
                        c.pop("base_src", None)
            ms = [c["m"] for r in g["rows"] for c in r["cells"] if c and c.get("m")]
            g["aspect"] = (ms[0]["w"] / ms[0]["h"]) if ms else 0.8
        html = PAGE.replace("__TITLE__", board["title"]).replace("__DATA__", json.dumps(board, ensure_ascii=False))
        (out / f"{name}.html").write_text(html, encoding="utf-8")
        print(f"{name}: {len(jobs)} renders, {len(jobs) - left} ready, {left} left -> {out / (name + '.html')}")
    print(f"{left_total} left" + (" (run again)" if left_total else ""))


PAGE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Griglia · __TITLE__</title>
<style>
:root{--bg:#151517;--panel:#232327;--fg:#eee;--mut:#9a9aa2;--acc:#6cf;--w:150px;--ar:0.8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:13px system-ui,sans-serif}
#bar{position:sticky;top:0;z-index:6;background:var(--panel);padding:6px 10px;display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;border-bottom:1px solid #333}
#bar .g{display:flex;gap:4px;align-items:center}#bar .lab{color:var(--mut)}
select,button,input{font:13px system-ui,sans-serif}select{background:#333;color:#eee;border:1px solid #555;border-radius:6px;padding:3px}
button{background:#333;color:#eee;border:1px solid #555;border-radius:6px;padding:3px 9px;cursor:pointer}button.on{background:#2c5880;border-color:var(--acc)}
#note{color:var(--mut);padding:6px 10px 0;max-width:1300px;line-height:1.4}#help{color:#777;padding:2px 10px 0;font-size:12px}
#grid{display:grid;gap:3px;padding:8px 10px 40px;grid-template-columns:150px repeat(var(--n),var(--w)) var(--nw,0px);width:max-content}
.nt{display:flex;flex-direction:column;gap:2px;padding:2px 0 2px 6px}.nt textarea{flex:1;width:100%;box-sizing:border-box;background:#222;color:#eee;border:1px solid #555;border-radius:6px;font:13px system-ui;resize:none;min-height:40px}
.nt textarea:focus{border-color:#fc6}.sc{display:flex;gap:3px;align-items:center}.sc button{padding:2px 8px}.sc .lab{margin-right:4px;min-width:14px}.sc.gen button{padding:1px 5px;font-size:12px}
.hd{position:sticky;top:var(--barh,40px);z-index:4;background:var(--bg);text-align:center;color:var(--mut);padding:3px 0;font-weight:600}
.rl{position:sticky;left:0;z-index:3;background:var(--bg);padding:2px 4px;display:flex;flex-direction:column;justify-content:center;gap:2px}
.rl b{font-size:13px}.rl svg{display:block}
.cell{position:relative;width:var(--w);aspect-ratio:var(--ar);overflow:hidden;background:#000;cursor:crosshair;touch-action:none}
.cell img{position:absolute;max-width:none;user-select:none;-webkit-user-drag:none;pointer-events:none}
.cell img.hi{display:none}.cell.zoomhi img.hi{display:block}
.cell.base{outline:1px solid #4a8ab8}.cell.sel{outline:2px solid #fc6;z-index:2}
.empty{width:var(--w);aspect-ratio:var(--ar);background:repeating-linear-gradient(45deg,#1c1c1f 0 6px,#19191b 6px 12px)}
.bd,.ms,.sb{position:absolute;background:#000c;border-radius:3px;pointer-events:none;padding:0 3px;font-size:11px;line-height:15px}
.bd{left:2px;top:2px;color:#fc6;max-width:calc(100% - 4px);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ms{right:2px;bottom:2px;color:#ddd}.sb{left:2px;bottom:2px;color:#9cf}
.np{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#666}
body.nobd .bd,body.nobd .sb{display:none}body.noms .ms{display:none}
#tip{position:fixed;z-index:20;pointer-events:none;background:#000e;border:1px solid #444;border-radius:6px;padding:6px 8px;max-width:360px;display:none;line-height:1.4}
#fx{position:fixed;inset:0;z-index:30;background:#0d0d0f;display:none;flex-direction:column}
#fx.open{display:flex}#fxtop{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;padding:6px 10px;background:var(--panel)}
#fxmain{flex:1;display:flex;gap:12px;padding:10px;min-height:0}
#fxv{width:auto;height:100%;flex:none}#fxside{flex:1;min-width:220px;overflow:auto;line-height:1.5}
#fxside .k{color:var(--mut)}#strip{display:flex;gap:2px;padding:4px 10px 8px;overflow-x:auto}
#strip .cell{width:64px;cursor:pointer}#rng{width:min(520px,60vw)}
</style></head><body>
<div id="bar">
 <div class="g"><span class="lab">griglia</span><select id="gs"></select></div>
 <div class="g"><span class="lab">vista</span><button data-m="p" class="on">render</button><button data-m="a">|Δ| dalla base</button><button data-m="s">ΔL firmato</button></div>
 <div class="g"><span class="lab">guadagno Δ</span><input id="gain" type="range" min="0.5" max="6" step="0.25" value="1"><span id="gainv">×1</span></div>
 <div class="g"><span class="lab">cella</span><input id="cw" type="range" min="70" max="420" step="10" value="150"></div>
 <div class="g"><span class="lab">numero</span><select id="num"><option value="mad">|Δ| medio</option><option value="dy">ΔL medio</option><option value="hf">HF ×base</option><option value="p95">|Δ| 95°</option><option value="">nessuno</option></select></div>
 <div class="g" id="ntbar" style="display:none"><button id="ntexp">scarica le note</button><span id="ntn" class="lab"></span></div>
 <div class="g"><button id="bdt" class="on">etichette</button><button id="z0">zoom 1:1</button><span id="zv" class="lab">×1.0</span></div>
</div>
<div id="note"></div>
<div id="help">Rotella su una cella = zoom (uguale ovunque) · trascina = sposta · clic = seleziona · doppio clic o F = vista scorrevole · D = cambia vista · 0 = azzera zoom.
 Nella vista scorrevole: ←→ dose, ↑↓ blocco, spazio = anima, tieni premuto B = mostra la base, Esc = chiudi.
 I numeri sono calcolati per questa pagina (non sono misure pubblicate).</div>
<div id="grid"></div>
<div id="tip"></div>
<div id="fx">
 <div id="fxtop">
  <b id="fxt"></b>
  <span class="g"><span class="lab">scorri lungo</span> <button id="axc" class="on">dose (riga)</button><button id="axr">blocchi (colonna)</button></span>
  <input id="rng" type="range" min="0" max="0" step="1" value="0">
  <button id="play">▶ anima</button><span class="lab">fps</span><input id="fps" type="range" min="1" max="12" value="3" style="width:90px">
  <button id="pp" class="on">avanti-indietro</button><button id="flk">alterna con base</button>
  <button id="fxclose">chiudi (Esc)</button>
 </div>
 <div id="fxmain"><div id="fxv" class="cell"><img class="lo"><img class="hi"><span class="bd"></span><span class="sb"></span><span class="ms"></span></div><div id="fxside"></div></div>
 <div id="strip"></div>
</div>
<script>
const D=__DATA__;
const NK='grid_notes_'+D.title;let NOTES={},SCORES={};try{NOTES=JSON.parse(localStorage.getItem(NK)||'{}');SCORES=JSON.parse(localStorage.getItem(NK+'_scores')||'{}')}catch(e){}
function saveNotes(){try{localStorage.setItem(NK,JSON.stringify(NOTES));localStorage.setItem(NK+'_scores',JSON.stringify(SCORES))}catch(e){}
  const el=document.querySelector('#ntn');if(el)el.textContent=Object.values(SCORES).filter(v=>v).length+' voti · '+Object.values(NOTES).filter(v=>v.trim()).length+' note'}
const $=s=>document.querySelector(s);
const S={g:0,mode:'p',z:1,cx:.5,cy:.5,gain:1,num:'mad',sel:null};
let G=null,CELLS=[];
const F={r:0,c:0,axis:'c',play:null,pp:true,dir:1,flk:null,showBase:false};
function fmt(m,k){if(!m)return'…';const v=m[k];if(v==null)return'';return k==='hf'?'×'+v.toFixed(2):k==='dy'?(v>0?'+':'')+v.toFixed(1):v.toFixed(1)}
function srcOf(c,hi){
  if(!c.m)return'';
  if(c.base||S.mode==='p')return hi?'../'+c.src:'cache/p_'+c.id+'.jpg';
  if(S.mode==='a')return hi?'cache/A_'+c.id+'.jpg':'cache/a_'+c.id+'.jpg';
  return'cache/s_'+c.id+'.jpg';}
function baseCell(){for(const r of G.rows)for(const c of r.cells)if(c&&c.base)return c;return null}
function needHi(el){return el.clientWidth*S.z*(window.devicePixelRatio||1)>PRE*1.15}
const PRE=512;
function place(el,c){
  const lo=el.querySelector('img.lo'),hi=el.querySelector('img.hi');
  const w=el.clientWidth,h=el.clientHeight,W=w*S.z,H=h*S.z;
  for(const im of[lo,hi]){im.style.width=W+'px';im.style.height=H+'px';im.style.left=(w/2-S.cx*W)+'px';im.style.top=(h/2-S.cy*H)+'px';
    im.style.filter=(!c.base&&S.mode!=='p')?`brightness(${S.gain})`:'none';}
  const sl=srcOf(c,false);if(lo.dataset.s!==sl){lo.dataset.s=sl;lo.src=sl}
  const big=needHi(el);el.classList.toggle('zoomhi',big);
  if(big){const sh=srcOf(c,true);if(hi.dataset.s!==sh){hi.dataset.s=sh;hi.src=sh}}
}
function mkCell(c,cls){
  const el=document.createElement('div');el.className='cell'+(c.base?' base':'')+(cls?' '+cls:'');
  el.innerHTML='<img class="lo" loading="lazy"><img class="hi" loading="lazy"><span class="bd"></span><span class="sb"></span><span class="ms"></span>'+(c.m?'':'<span class="np">non pronto</span>');
  fillTags(el,c);return el}
function fillTags(el,c){el.querySelector('.bd').textContent=c.badge||'';el.querySelector('.bd').style.display=c.badge?'':'none';
  el.querySelector('.sb').textContent=c.sub||'';el.querySelector('.ms').textContent=S.num&&!c.base?fmt(c.m,S.num):'';
  el.querySelector('.ms').style.display=S.num&&!c.base?'':'none'}
function spark(row){
  const k=S.num||'mad',W=140,H=30;
  const vals=row.cells.map(c=>c&&c.m?(k==='hf'?c.m.hf-1:c.m[k]):null);
  let mx=0;for(const r of G.rows)for(const c of r.cells)if(c&&c.m){const v=Math.abs(k==='hf'?c.m.hf-1:c.m[k]);if(v>mx)mx=v}
  mx=mx||1;const n=vals.length,signed=(k==='dy'||k==='hf');
  const y=v=>signed?H/2-(v/mx)*(H/2-2):H-2-(Math.abs(v)/mx)*(H-4);
  let p='',dots='';vals.forEach((v,i)=>{if(v==null)return;const x=4+i*(W-8)/Math.max(1,n-1);p+=(p?' L':'M')+x.toFixed(1)+' '+y(v).toFixed(1);dots+=`<circle cx="${x.toFixed(1)}" cy="${y(v).toFixed(1)}" r="1.8" fill="#fc6"/>`});
  const zero=signed?`<line x1="0" x2="${W}" y1="${H/2}" y2="${H/2}" stroke="#444"/>`:'';
  return `<svg width="${W}" height="${H}">${zero}<path d="${p}" fill="none" stroke="#e8743b" stroke-width="1.4"/>${dots}</svg>`}
function render(){
  G=D.grids[S.g];$('#note').textContent=G.title+' — '+(G.note||'');
  const g=$('#grid');g.style.setProperty('--n',G.cols.length);document.documentElement.style.setProperty('--ar',G.aspect||.8);
  g.innerHTML='';CELLS=[];
  const corner=document.createElement('div');corner.className='hd';corner.style.left='0';corner.style.zIndex=5;g.appendChild(corner);
  G.cols.forEach(c=>{const d=document.createElement('div');d.className='hd';d.textContent=c;g.appendChild(d)});
  g.style.setProperty('--nw',G.notes?(G.notes.w||'280px'):'0px');$('#ntbar').style.display=G.notes?'':'none';
  if(G.notes){const d=document.createElement('div');d.className='hd';d.textContent=G.notes.head||'';g.appendChild(d)}
  G.rows.forEach((row,ri)=>{
    const l=document.createElement('div');l.className='rl';l.innerHTML=`<b>${row.label}</b>`+spark(row);g.appendChild(l);
    row.cells.forEach((c,ci)=>{
      if(!c){const e=document.createElement('div');e.className='empty';g.appendChild(e);return}
      const el=mkCell(c);el.dataset.r=ri;el.dataset.c=ci;g.appendChild(el);CELLS.push([el,c]);hook(el)});
    if(G.notes){const d=document.createElement('div');d.className='nt';const key=G.id+'|'+row.label;
      (G.notes.qs||[]).forEach(qq=>{const kk=skey(key,qq.k);const sc=document.createElement('div');sc.className='sc'+(G.notes.cls?' '+G.notes.cls:'');
        sc.innerHTML=`<span class="lab">${qq.lab}</span>`+qq.o.map(v=>`<button data-v="${v}">${v}</button>`).join('');
        const paint=()=>sc.querySelectorAll('button').forEach(b=>b.classList.toggle('on',SCORES[kk]==b.dataset.v));
        sc.querySelectorAll('button').forEach(b=>b.onclick=()=>{SCORES[kk]=SCORES[kk]==b.dataset.v?undefined:b.dataset.v;saveNotes();paint()});paint();d.appendChild(sc)});
      const t=document.createElement('textarea');
      t.placeholder='dettagli importanti (facoltativo)';t.value=NOTES[G.id+'|'+row.label]||'';
      t.oninput=()=>{NOTES[G.id+'|'+row.label]=t.value;saveNotes()};d.appendChild(t);g.appendChild(d)}
  });
  document.documentElement.style.setProperty('--barh',$('#bar').offsetHeight+'px');
  draw();}
let raf=0;function draw(){if(raf)return;raf=requestAnimationFrame(()=>{raf=0;for(const[el,c]of CELLS)place(el,c);if(F.open)fxDraw();$('#zv').textContent='×'+S.z.toFixed(1)})}
function clamp(){S.z=Math.min(32,Math.max(1,S.z));const h=.5/S.z;S.cx=Math.min(1-h,Math.max(h,S.cx));S.cy=Math.min(1-h,Math.max(h,S.cy))}
function hook(el){
  el.addEventListener('wheel',e=>{e.preventDefault();const r=el.getBoundingClientRect();const mx=(e.clientX-r.left)/r.width-.5,my=(e.clientY-r.top)/r.height-.5;
    const u=S.cx+mx/S.z,v=S.cy+my/S.z;S.z*=Math.exp(-e.deltaY*0.0018);clamp();S.cx=u-mx/S.z;S.cy=v-my/S.z;clamp();draw()},{passive:false});
  el.addEventListener('pointerdown',e=>{el.setPointerCapture(e.pointerId);const r=el.getBoundingClientRect();let lx=e.clientX,ly=e.clientY,mv=0;
    const mm=ev=>{const dx=ev.clientX-lx,dy=ev.clientY-ly;mv+=Math.abs(dx)+Math.abs(dy);lx=ev.clientX;ly=ev.clientY;S.cx-=dx/(r.width*S.z);S.cy-=dy/(r.height*S.z);clamp();draw()};
    const up=()=>{el.removeEventListener('pointermove',mm);el.removeEventListener('pointerup',up);if(mv<4&&el.dataset.r!=null)select(+el.dataset.r,+el.dataset.c)};
    el.addEventListener('pointermove',mm);el.addEventListener('pointerup',up)});
  el.addEventListener('dblclick',()=>{if(el.dataset.r!=null){select(+el.dataset.r,+el.dataset.c);openFx()}});
  el.addEventListener('mousemove',e=>tip(e,el));el.addEventListener('mouseleave',()=>$('#tip').style.display='none');
}
function cellAt(r,c){const row=G.rows[r];return row?row.cells[c]:null}
function tip(e,el){if(el.dataset.r==null)return;const c=cellAt(+el.dataset.r,+el.dataset.c);const t=$('#tip');
  t.innerHTML=info(+el.dataset.r,+el.dataset.c);t.style.display='block';t.style.left=Math.min(innerWidth-370,e.clientX+14)+'px';t.style.top=Math.min(innerHeight-160,e.clientY+14)+'px'}
function info(r,c){const x=cellAt(r,c);if(!x)return'';const m=x.m;
  return `<b>${G.rows[r].label} · ${G.cols[c]}</b> <span class="k">(dose ${x.sub})</span><br>`+
   (x.badge?`<span style="color:#fc6">${x.badge}</span><br>`:'')+(x.note?`<i>${x.note}</i><br>`:'')+
   (m?`|Δ| medio ${m.mad} · |Δ| 95° ${m.p95} · ΔL medio ${m.dy} · HF ×${m.hf}`:'non pronto')+`<br><span class="k">${x.src}</span>`}
function select(r,c){S.sel=[r,c];for(const[el]of CELLS)el.classList.toggle('sel',+el.dataset.r===r&&+el.dataset.c===c);F.r=r;F.c=c;if(F.open)fxSync()}
// ---------- focus view
function line(){return F.axis==='c'?G.rows[F.r].cells.map((c,i)=>c?i:null).filter(i=>i!=null):G.rows.map((row,i)=>row.cells[F.c]?i:null).filter(i=>i!=null)}
function openFx(){if(!S.sel)select(0,G.cols.indexOf('base')>=0?G.cols.indexOf('base'):0);F.open=true;$('#fx').classList.add('open');fxSync()}
function closeFx(){F.open=false;$('#fx').classList.remove('open');stop();stopFlk()}
function colBase(c){const r=G.rows.find(r=>r.cells[c]&&r.cells[c].base);return r?r.cells[c]:baseCell()}
function fxCur(){return F.showBase?colBase(F.c):cellAt(F.r,F.c)}
function fxSize(){const v=$('#fxv'),m=$('#fxmain');const H=m.clientHeight-20,W=m.clientWidth-260;const ar=G.aspect||.8;let h=H,w=h*ar;if(w>W){w=W;h=w/ar}v.style.width=w+'px';v.style.height=h+'px'}
function fxDraw(){const c=fxCur();if(!c)return;const v=$('#fxv');fxSize();place(v,c);fillTags(v,c);
  $('#fxt').textContent=`${G.rows[F.r].label} · ${G.cols[F.c]}`+(F.showBase?'  [BASE]':'');$('#fxside').innerHTML=info(F.r,F.c)}
function fxSync(){const L=line(),i=L.indexOf(F.axis==='c'?F.c:F.r);const R=$('#rng');R.max=L.length-1;R.value=Math.max(0,i);
  const st=$('#strip');st.innerHTML='';L.forEach(k=>{const r=F.axis==='c'?F.r:k,c=F.axis==='c'?k:F.c,x=cellAt(r,c);
    const el=mkCell(x);if((F.axis==='c'?c:r)===(F.axis==='c'?F.c:F.r))el.classList.add('sel');el.onclick=()=>{F.r=r;F.c=c;fxSync()};st.appendChild(el);
    requestAnimationFrame(()=>{const z=S.z,cx=S.cx,cy=S.cy;place(el,x)})});
  preload(L);fxDraw()}
function preload(L){for(const k of L){const x=F.axis==='c'?cellAt(F.r,k):cellAt(k,F.c);if(x){const i=new Image();i.src=srcOf(x,needHi($('#fxv')))}}}
function step(d){const L=line();let i=L.indexOf(F.axis==='c'?F.c:F.r)+d;
  if(F.play&&F.pp){if(i>=L.length||i<0){F.dir=-F.dir;i+=2*F.dir;d=F.dir}}
  i=(i+L.length)%L.length;if(F.axis==='c')F.c=L[i];else F.r=L[i];fxSync()}
function stop(){if(F.play){clearInterval(F.play);F.play=null;$('#play').textContent='▶ anima'}}
function play(){if(F.play)return stop();F.dir=1;F.play=setInterval(()=>step(F.dir),1000/+$('#fps').value);$('#play').textContent='■ ferma'}
function stopFlk(){if(F.flk){clearInterval(F.flk);F.flk=null;F.showBase=false;$('#flk').classList.remove('on')}}
function flk(){if(F.flk){stopFlk();fxDraw();return}$('#flk').classList.add('on');F.flk=setInterval(()=>{F.showBase=!F.showBase;fxDraw()},1000/+$('#fps').value)}
$('#rng').oninput=e=>{const L=line(),k=L[+e.target.value];if(F.axis==='c')F.c=k;else F.r=k;fxSync()};
$('#play').onclick=play;$('#flk').onclick=flk;$('#fxclose').onclick=closeFx;
$('#pp').onclick=()=>{F.pp=!F.pp;$('#pp').classList.toggle('on',F.pp)};
$('#fps').oninput=()=>{if(F.play){stop();play()}if(F.flk){stopFlk();flk()}};
$('#axc').onclick=()=>{F.axis='c';$('#axc').classList.add('on');$('#axr').classList.remove('on');fxSync()};
$('#axr').onclick=()=>{F.axis='r';$('#axr').classList.add('on');$('#axc').classList.remove('on');fxSync()};
hook($('#fxv'));
// ---------- controls
D.grids.forEach((g,i)=>{const o=document.createElement('option');o.value=i;o.textContent=g.title;$('#gs').appendChild(o)});
$('#gs').onchange=e=>{S.g=+e.target.value;S.sel=null;closeFx();render()};
document.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>setMode(b.dataset.m));
function setMode(m){S.mode=m;document.querySelectorAll('[data-m]').forEach(x=>x.classList.toggle('on',x.dataset.m===m));draw()}
$('#gain').oninput=e=>{S.gain=+e.target.value;$('#gainv').textContent='×'+S.gain;draw()};
$('#cw').oninput=e=>{document.documentElement.style.setProperty('--w',e.target.value+'px');draw()};
$('#num').onchange=e=>{S.num=e.target.value;document.body.classList.toggle('noms',!S.num);render()};
$('#bdt').onclick=()=>{document.body.classList.toggle('nobd');$('#bdt').classList.toggle('on')};
$('#z0').onclick=()=>{S.z=1;S.cx=S.cy=.5;draw()};
function skey(key,k){return k==='score_1_5'?key:key+'|'+k}
$('#ntexp').onclick=()=>{const q=v=>'"'+String(v||'').replace(/"/g,'""').replace(/\n/g,' ')+'"';
  const QK=[];D.grids.filter(g=>g.notes).forEach(g=>(g.notes.qs||[]).forEach(x=>{if(!QK.includes(x.k))QK.push(x.k)}));
  let t='grid,row,'+QK.join(',')+(QK.length?',':'')+'note\n';
  D.grids.filter(g=>g.notes).forEach(g=>g.rows.forEach(r=>{const k=g.id+'|'+r.label;t+=[g.id,q(r.label),...QK.map(x=>SCORES[skey(k,x)]||''),q(NOTES[k])].join(',')+'\n'}));
  const u=URL.createObjectURL(new Blob([t],{type:'text/csv'}));const l=document.createElement('a');l.href=u;l.download=D.notes_file||'grid_notes_alessandro.csv';l.click()};
addEventListener('keydown',e=>{if(e.target.tagName==='SELECT'||e.target.tagName==='TEXTAREA'||e.target.tagName==='INPUT'&&e.target.type!=='range')return;
  const k=e.key.toLowerCase();
  if(k==='d'){setMode({p:'a',a:'s',s:'p'}[S.mode]);return}
  if(k==='0'){S.z=1;S.cx=S.cy=.5;draw();return}
  if(k==='f'){F.open?closeFx():openFx();return}
  if(!F.open)return;
  if(k==='escape')closeFx();
  else if(k==='b'&&!e.repeat){F.showBase=true;fxDraw()}
  else if(k===' '){e.preventDefault();play()}
  else if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();const L=G.rows[F.r].cells.map((c,i)=>c?i:null).filter(i=>i!=null);let i=L.indexOf(F.c)+(e.key==='ArrowRight'?1:-1);i=(i+L.length)%L.length;F.c=L[i];fxSync()}
  else if(e.key==='ArrowUp'||e.key==='ArrowDown'){e.preventDefault();const L=G.rows.map((r,i)=>r.cells[F.c]?i:null).filter(i=>i!=null);let i=L.indexOf(F.r)+(e.key==='ArrowDown'?1:-1);i=(i+L.length)%L.length;F.r=L[i];fxSync()}});
addEventListener('keyup',e=>{if(e.key.toLowerCase()==='b'&&F.open){F.showBase=false;fxDraw()}});
saveNotes();
addEventListener('resize',()=>{document.documentElement.style.setProperty('--barh',$('#bar').offsetHeight+'px');draw()});
render();
</script></body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--set", default="all", choices=["all", *SETS])
    ap.add_argument("--img-root")
    ap.add_argument("--budget", type=float, default=160)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if a.img_root:
        IMG_ROOT = Path(a.img_root)
    if not a.build:
        ap.print_help()
        sys.exit(0)
    build(list(SETS) if a.set == "all" else [a.set], a.budget, a.workers)
