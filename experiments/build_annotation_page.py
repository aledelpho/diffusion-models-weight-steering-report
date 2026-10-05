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
         Path("C:/StabilityMatrix-win-x64/Data/Images/Text2Img"),
         Path("C:/StabilityMatrix-win-x64/Data/Packages/ComfyUI/output")]


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


# ----------------------------------------------------------------- wo_depth
WD_PAT = re.compile(r"^(P\d\d)_(slice_(b\d)|union)_(pos|neg|d[+-][\d.]+)_krea2_seed(\d+)_")
WD_BLOCKS = {"b1": "blocchi 0–4", "b2": "blocchi 5–9", "b3": "blocchi 10–14", "b4": "blocchi 15–19",
             "b5": "blocchi 20–23", "b6": "blocchi 24–27", "union": "tutti i 28 blocchi"}


def scan_wo_depth(B: Path) -> dict:
    idx: dict = {}
    for p in sorted((B / "renders").glob("*.png")):
        m = WD_PAT.match(p.name)
        if not m:
            continue
        P, _, g, t, seed = m.groups()
        g = g or "union"
        d = 0.1 if t == "pos" else -0.1 if t == "neg" else float(t[1:])
        idx.setdefault(P, {}).setdefault(seed, {}).setdefault(g, {})[f"{d:+.3f}"] = f"renders/{p.name}"
    # baselines are BORROWED from benchmark_centre_push (G_det: pixel-identical); served from the
    # sibling folder, so the page must stay next to it in Text2Img
    base: dict = {}
    for r in csv.DictReader(open(DATA / "centre_push_plan.csv", encoding="utf-8")):
        if r["arm"] == "baseline" and (B.parent / "benchmark_centre_push" / "renders" / r["expected_filename"]).is_file():
            base.setdefault(r["prompt_id"], {})[r["seed"]] = "../benchmark_centre_push/renders/" + r["expected_filename"]
    groups = {g: {"title": ("union — " if g == "union" else f"slice {g} — ") + WD_BLOCKS[g],
                  "meta": ("28 tensori · <code>blocks.0…27.attn.wo.weight</code>" if g == "union" else
                           f"{4 if g in ('b5','b6') else 5} tensori · <code>attn.wo.weight</code> di {WD_BLOCKS[g]}")}
              for g in WD_BLOCKS}
    return {"idx": idx, "base": base, "groups": groups,
            "order": ["b1", "b2", "b3", "b4", "b5", "b6", "union"], "stats": {},
            "unit": "la fetta",
            "title": "wo tagliato per profondità — dal più negativo al più positivo",
            "sub": "benchmark_wo_depth · sei fette di attn.wo più l'unione, sette dosi con il baseline allo zero",
            "note": "Il <b>baseline</b> è preso in prestito da <code>benchmark_centre_push</code>: stesso prompt, "
                    "stesso seme, e la guardia G_det ha verificato che ri-renderizzarlo dà gli stessi pixel. "
                    "<b>Solo ±0.100 è preregistrato</b>; ±0.200 e ±0.350 sono esplorativi. "
                    "<b>La domanda della preregistrazione (§8):</b> l'unione somiglia a una delle sei fette, a "
                    "tutte insieme, o a qualcosa che nessuna delle sei è?"}


# ----------------------------------------------------------------- single_blocks_atlas
SB_PAT = re.compile(r"^(P01_blacksmith|S1_rally|F4_closeup)_blk(\d\d)_(pos|neg)_d([\d.]+)_krea2_seed(\d+)_")
SB_BASE = re.compile(r"^(P01_blacksmith|S1_rally|F4_closeup)_baseline_krea2_seed(\d+)_")
SB_GROUP = {**{b: "Block_1" for b in range(0, 5)}, **{b: "Block_2" for b in range(5, 10)},
            **{b: "Block_3" for b in range(10, 15)}, **{b: "Block_4" for b in range(15, 20)},
            **{b: "Block_5" for b in range(20, 24)}, **{b: "Block_6" for b in range(24, 28)}}


def scan_single_blocks_atlas(B: Path) -> dict:
    idx: dict = {}; base: dict = {}
    for p in sorted((B / "renders").glob("*.png")):
        m = SB_PAT.match(p.name)
        if m:
            P, b, sign, dose, seed = m.groups()
            v = (-1 if sign == "neg" else 1) * float(dose)
            idx.setdefault(P, {}).setdefault(seed, {}).setdefault(f"blk{b}", {})[f"{v:+.3f}"] = f"renders/{p.name}"
            continue
        m = SB_BASE.match(p.name)
        if m:
            base.setdefault(m.group(1), {})[m.group(2)] = f"renders/{p.name}"
    groups = {f"blk{b:02d}": {"title": f"blk{b:02d}", "meta": f"blocco {b} · nel gruppo {SB_GROUP[b]}"} for b in range(28)}
    return {"idx": idx, "base": base, "groups": groups, "order": [f"blk{b:02d}" for b in range(28)],
            "stats": {}, "unit": "il blocco", "stack": True,
            "title": "Atlante per singolo blocco — −0.350, baseline, +0.350",
            "sub": "benchmark_single_blocks_atlas · 28 blocchi, tre prompt, un solo seme",
            "note": "<b>Un solo seme</b>: parte di quello che vedi in un blocco può essere la traiettoria di quel seme e "
                    "non il blocco. Il confronto utile è <b>fra prompt</b>: se un blocco fa la stessa cosa su "
                    "fabbro, auto e primo piano, è un controllo; se fa cose diverse, dipende dall'immagine."}


# ----------------------------------------------------------------- single_blocks_styles
SS_PAT = re.compile(r"^([A-Z]\d_[a-z_]+?)_blk(\d\d)_(pos|neg)_d([\d.]+)_krea2_seed(\d+)_")
SS_BASE = re.compile(r"^([A-Z]\d_[a-z_]+?)_baseline_krea2_seed(\d+)_")


def load_alessandro_notes() -> dict:
    notes_file = DATA / "single_blocks_styles_notes_alessandro.md"
    if not notes_file.is_file():
        return {}
    txt = notes_file.read_text(encoding="utf-8")
    res = {}
    current_blk = None
    for line in txt.splitlines():
        line_s = line.strip()
        if line_s.startswith("## blk"):
            current_blk = line_s.split()[1]
        elif current_blk:
            if line_s.startswith("**-") and "—" in line_s:
                parts = line_s.split("—", 1)
                d = parts[0].replace("*", "").strip()
                t = parts[1].strip()
                if t and t != "_(nessun appunto)_":
                    res[f"{current_blk}|neg"] = f"[{d}]: {t}"
            elif line_s.startswith("**+") and "—" in line_s:
                parts = line_s.split("—", 1)
                d = parts[0].replace("*", "").strip()
                t = parts[1].strip()
                if t and t != "_(nessun appunto)_":
                    res[f"{current_blk}|pos"] = f"[{d}]: {t}"
            elif "Il blocco nel suo insieme" in line_s and "—" in line_s:
                parts = line_s.split("—", 1)
                t = parts[1].strip()
                if t and t != "_(nessun appunto)_":
                    res[f"{current_blk}|__family__"] = t
    return res


def scan_single_blocks_unified(B: Path) -> dict:
    """Unified scan for single_blocks_v3 and single_blocks_styles with multi-series support."""
    idx: dict = {}; base: dict = {}
    
    # Identify sibling folders
    v3_dir = B.parent / "benchmark_single_blocks_v3"
    styles_dir = B.parent / "benchmark_single_blocks_styles"
    v4_dir = B.parent / "benchmark_single_blocks_v4"
    
    # Helper to scan a specific bench directory
    def scan_bench_dir(tgt_dir: Path, rel_base: str):
        if not (tgt_dir / "renders").is_dir(): return
        rel_prefix = f"../{rel_base}/renders/"
        for p in sorted((tgt_dir / "renders").glob("*.png")):
            m = SS_PAT.match(p.name)
            if m:
                P, b, sign, dose, seed = m.groups()
                v = (-1 if sign == "neg" else 1) * float(dose)
                idx.setdefault(P, {}).setdefault(seed, {}).setdefault(f"blk{b}", {})[f"{v:+.3f}"] = f"{rel_prefix}{p.name}"
                continue
            m = SS_BASE.match(p.name)
            if m:
                base.setdefault(m.group(1), {})[m.group(2)] = f"{rel_prefix}{p.name}"

    scan_bench_dir(v3_dir, "benchmark_single_blocks_v3")
    scan_bench_dir(styles_dir, "benchmark_single_blocks_styles")
    scan_bench_dir(v4_dir, "benchmark_single_blocks_v4")

    def get_zone_name(b: int) -> str:
        if 0 <= b <= 1: return "Base"
        if 2 <= b <= 18: return "Style"
        if 19 <= b <= 22: return "Details"
        if 23 <= b <= 27: return "Correction"
        return ""

    groups = {f"blk{b:02d}": {"title": f"blk{b:02d} · {get_zone_name(b)}", "meta": f"blocco {b} · nel gruppo {SB_GROUP[b]}"} for b in range(28)}

    raw_notes = load_alessandro_notes()
    default_notes = {}
    for blk_name in groups:
        for P in idx:
            for s in idx[P]:
                for d in idx[P][s].get(blk_name, {}):
                    if float(d) < 0 and f"{blk_name}|neg" in raw_notes:
                        default_notes[f"{blk_name}|{d}"] = raw_notes[f"{blk_name}|neg"]
                    elif float(d) > 0 and f"{blk_name}|pos" in raw_notes:
                        default_notes[f"{blk_name}|{d}"] = raw_notes[f"{blk_name}|pos"]
        if f"{blk_name}|__family__" in raw_notes:
            default_notes[f"{blk_name}|__family__"] = raw_notes[f"{blk_name}|__family__"]

    series = [
        {
            "id": "v4",
            "name": "Serie V4 (Camera e Materiali)",
            "shortName": "V4 (5 prompt)",
            "prompts": ["P1_crown_topdown", "P2_crown_bottomup", "P3_crown_rusted", "P4_crown_glass", "P5_comic_panels"],
            "bands": [["P1_crown_topdown", "P2_crown_bottomup"], ["P3_crown_rusted", "P4_crown_glass"], ["P5_comic_panels"]],
            "bandNames": ["Camera (Alto vs Basso)", "Materiali (Ferro vs Vetro)", "Layout Multiplo (Fumetto)"]
        },
        {
            "id": "v3",
            "name": "Serie V3 (6 soggetti complessi)",
            "shortName": "V3 (6 soggetti)",
            "prompts": ["P1_elfbrawler", "P2_lotuscanoe", "P3_archerforest", "P4_selfie", "P5_gingervampire", "P6_ghostgirl"],
            "bands": [["P1_elfbrawler", "P2_lotuscanoe", "P3_archerforest"],
                      ["P4_selfie", "P5_gingervampire", "P6_ghostgirl"]],
            "bandNames": ["Serie 1 · seed 3141592 (Comics, Canoa, Cacciatrice)",
                          "Serie 2 · seed 1618033 (Selfie, Vampira, Fantasma)"]
        },
        {
            "id": "styles_cartoon",
            "name": "Cartoon (6 soggetti diversi)",
            "shortName": "Cartoon (6 soggetti)",
            "prompts": ["E1_cartoon", "E8_cartoon_styleend", "C1_blacksmith", "C2_rally", "C3_fox", "C4_stilllife"],
            "bands": [["E1_cartoon", "E8_cartoon_styleend", "C1_blacksmith", "C2_rally", "C3_fox", "C4_stilllife"]],
            "bandNames": ["Stesso stile cartoon, 6 soggetti diversi · seed 2718281"]
        },
        {
            "id": "styles_art",
            "name": "Stili Elfa (7 stili artistici)",
            "shortName": "Stili (7 stili elfa)",
            "prompts": ["E1_cartoon", "E2_watercolor", "E3_oil", "E4_colorpencil", "E5_childrensbook", "E6_claymation", "E7_sepiaphoto"],
            "bands": [["E1_cartoon", "E2_watercolor", "E3_oil", "E4_colorpencil", "E5_childrensbook", "E6_claymation", "E7_sepiaphoto"]],
            "bandNames": ["Stesso soggetto (elfa urlante), 7 stili diversi · seed 2718281"]
        },
        {
            "id": "styles_all",
            "name": "Tutti gli stili (12 prompt)",
            "shortName": "Styles (12 prompt)",
            "prompts": ["E1_cartoon", "E8_cartoon_styleend", "C1_blacksmith", "C2_rally", "C3_fox", "C4_stilllife",
                        "E2_watercolor", "E3_oil", "E4_colorpencil", "E5_childrensbook", "E6_claymation", "E7_sepiaphoto"],
            "bands": [["E1_cartoon", "E8_cartoon_styleend", "C1_blacksmith", "C2_rally", "C3_fox", "C4_stilllife"],
                      ["E1_cartoon", "E2_watercolor", "E3_oil", "E4_colorpencil", "E5_childrensbook", "E6_claymation", "E7_sepiaphoto"]],
            "bandNames": ["Stesso stile (cartoon), soggetti diversi", "Stesso soggetto (elfa), stili diversi"]
        }
    ]

    return {"idx": idx, "base": base, "groups": groups, "order": [f"blk{b:02d}" for b in range(28)],
            "stats": {}, "unit": "il blocco", "stack": True, "focus": True,
            "series": series,
            "promptOrder": series[0]["prompts"],
            "bands": series[0]["bands"],
            "bandNames": series[0]["bandNames"],
            "defaultNotes": default_notes,
            "title": "Singoli blocchi — Soggetti e stili a confronto",
            "sub": "benchmark_single_blocks_v3 + styles + v4 · 28 blocchi, 23 prompt complessivi, serie intercambiabili con un clic",
            "note": "Usa il pulsante <b>Serie</b> nella toolbar (o premi il tasto <code>S</code>) per alternare istantaneamente fra le nuove variazioni v4, i soggetti complessi di v3, e gli stili."}


scan_single_blocks_styles = scan_single_blocks_unified
scan_single_blocks_v3 = scan_single_blocks_unified
scan_single_blocks_v4 = scan_single_blocks_unified


BENCHES = {"parameter_families": scan_parameter_families, "centre_push": scan_centre_push,
           "wo_depth": scan_wo_depth, "single_blocks_atlas": scan_single_blocks_atlas,
           "single_blocks_styles": scan_single_blocks_styles,
           "single_blocks_v3": scan_single_blocks_v3,
           "single_blocks_v4": scan_single_blocks_v4}


def thumbs(B: Path, files: set[str]) -> None:
    from PIL import Image
    n = 0
    for rel in sorted(files):
        if not rel.startswith("../"):
            continue
        parts = rel.split("/")
        bench_dir_name = parts[1]
        native_dir = B.parent / bench_dir_name
        out = native_dir / "_thumbs"
        out.mkdir(exist_ok=True)
        
        clean = "renders/" + parts[-1]
        dst = out / (clean.replace("/", "__").rsplit(".", 1)[0] + ".jpg")
        if dst.exists():
            continue
        src = native_dir / "renders" / parts[-1]
        if not src.is_file():
            continue
        im = Image.open(src).convert("RGB")
        im.thumbnail((360, 360 * im.height // im.width), Image.LANCZOS)
        im.save(dst, quality=86)
        n += 1
    print(f"  {n} nuove miniature ({len(files)} in totale)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bench", choices=sorted(BENCHES))
    a = ap.parse_args()
    B = bench_dir("benchmark_" + a.bench)
    cfg = BENCHES[a.bench](B)
    cfg["bench"] = a.bench
    cfg.setdefault("stack", False)

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

    if a.bench in ("single_blocks_v3", "single_blocks_styles", "single_blocks_v4"):
        for other_name in ("benchmark_single_blocks_v3", "benchmark_single_blocks_styles", "benchmark_single_blocks_v4"):
            if other_name == "benchmark_" + a.bench:
                continue
            try:
                other_dir = bench_dir(other_name)
                (other_dir / "presets.html").write_text(html, encoding="utf-8")
                print(f"  presets.html (mirror) -> {other_dir}")
            except Exception as e:
                pass

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
  #seriesbtn{background:#233240;border-color:#356088;color:#d0e6ff;font-weight:600;display:inline-flex;align-items:center;gap:6px}
  #seriesbtn:hover{background:#2b3f54;border-color:#4884bb}
  #seriesbtn b{color:#64b5f6}
  .series-tag{display:inline-block;padding:2px 8px;border-radius:12px;font-size:12px;background:#2d3748;color:#a0aec0;margin-left:6px;font-weight:normal}
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
  .nav.u,.nav.dn{left:96px;right:96px;width:auto;height:58px;flex-direction:row;gap:12px}
  .nav.u{top:0;bottom:auto;background:linear-gradient(180deg,#000a,#0000)}
  .nav.dn{top:auto;bottom:90px;background:linear-gradient(0deg,#000a,#0000)}
  .nav.u:hover{background:linear-gradient(180deg,#000c,#0004)}
  .nav.dn:hover{background:linear-gradient(0deg,#000c,#0004)}
  .nav.u .ar,.nav.dn .ar{font-size:30px}
  #ov:not(.grid2) .nav.u,#ov:not(.grid2) .nav.dn{display:none}
  .sgrid{display:grid;gap:8px;align-items:start;overflow-x:auto;padding:2px 0 6px}
  .sgrid .plab{font:600 12px ui-monospace,monospace;color:var(--dim);writing-mode:vertical-rl;
               transform:rotate(180deg);align-self:center;justify-self:center;letter-spacing:.04em}
  .sgrid .dlab{font:600 13px ui-monospace,monospace;padding:0 2px}
  .sgrid .cellimg{width:100%;display:block;cursor:zoom-in;border-radius:6px;background:var(--surround)}
  .sgrid .cellimg.isb{outline:2px solid #3d6b56;outline-offset:-2px}
  .sgrid textarea{border:1px solid var(--line);border-radius:7px;min-height:74px}
  .sgrid .nonote{font-size:12px;color:var(--dim);padding:8px 4px}
  body.stacked .wrap{max-width:1900px}
  .fnav{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:0 0 14px}
  .fnav select{min-width:120px}
  .fnav .hint{margin-left:6px}
  .band{margin:0 0 18px}
  .band h3{font-size:14px;margin:0 0 8px;color:var(--dim);font-weight:600}
  .fgrid{display:grid;gap:6px;align-items:start}
  .fgrid .plabel{font:600 11px ui-monospace,monospace;color:var(--dim);text-align:center;overflow:hidden;
                 text-overflow:ellipsis;white-space:nowrap;padding:0 2px}
  .fgrid .rlab{font:600 12px ui-monospace,monospace;writing-mode:vertical-rl;transform:rotate(180deg);
               align-self:center;justify-self:center}
  .fgrid img{width:100%;display:block;cursor:zoom-in;border-radius:5px;background:var(--surround)}
  .fgrid img.isb{outline:2px solid #3d6b56;outline-offset:-2px}
  .fnotes{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:6px 0 0}
  .fnotes textarea{border:1px solid var(--line);border-radius:8px;min-height:90px}
  .fnotes .full{grid-column:1 / -1}
  #fams.stackwrap{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,calc(3*var(--rw,200px) + 80px)),1fr));gap:0 16px;align-items:start}
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
    <button id="focusbtn">Un blocco alla volta</button>
    <button id="stack">Prompt impilati</button>
    <button id="seriesbtn" title="Passa alla serie successiva di prompt (scorciatoia da tastiera: tasto S)">Serie: <b id="seriesname">V3 (6 soggetti)</b> ⟳</button>
    <label id="serieslab">serie <select id="series"></select></label>
    <label id="promptlab">prompt <select id="prompt"></select></label>
    <label>seme <select id="seed"></select></label>
    <button id="tstats">Mostra i numeri misurati</button>
    <label>miniature <select id="size"><option value="200">piccole</option><option value="260" selected>medie</option><option value="340">grandi</option></select></label>
    <button id="onerow">Una riga sola</button>
    <span class="grow"></span>
    <span class="hint" id="count"></span>
    <button id="exp">Esporta gli appunti</button>
  </div>

  <div class="fnav" id="fnav" style="display:none">
    <button id="fprev">&larr; blocco precedente</button>
    <select id="fsel"></select>
    <button id="fnext">blocco successivo &rarr;</button>
    <button id="fcompact">Tutto in una schermata ✓</button>
    <span class="hint"><kbd>&larr;</kbd> <kbd>&rarr;</kbd> cambiano blocco (fuori dall'ingrandimento e dalle caselle di testo)</span>
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
  <button class="nav u" id="ovup"><span class="ar">&#8963;</span><span class="to"></span></button>
  <button class="nav dn" id="ovdown"><span class="ar">&#8964;</span><span class="to"></span></button>
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
// One storage key per bench. Until 2026-09-29 every page shared "param_families_notes_v1"; notes
// already written there for THIS bench's groups are copied over once, never deleted.
const store = "annot_notes_single_blocks_v3";
let notes = {};
try { notes = JSON.parse(localStorage.getItem(store) || "{}"); } catch (e) { notes = {}; }
try {
  const oldStyles = JSON.parse(localStorage.getItem("annot_notes_single_blocks_styles") || "{}");
  for (const [k, v] of Object.entries(oldStyles)) {
    if (!notes[k] && v) notes[k] = v;
  }
} catch (e) {}
if (M.defaultNotes) {
  for (const [k, v] of Object.entries(M.defaultNotes)) {
    if (!notes[k]) notes[k] = v;
  }
}
try {
  const old = JSON.parse(localStorage.getItem("param_families_notes_v1") || "{}");
  let moved = 0;
  for (const [k, v] of Object.entries(old)) {
    if (M.order.includes(k.split("|")[0]) && !(k in notes)) { notes[k] = v; moved++; }
  }
  if (moved) localStorage.setItem(store, JSON.stringify(notes));
} catch (e) {}
const save = () => {
  try {
    localStorage.setItem(store, JSON.stringify(notes));
    localStorage.setItem("annot_notes_single_blocks_styles", JSON.stringify(notes));
  } catch (e) {}
};

const $ = s => document.querySelector(s);
function resolveRel(rel) {
  return rel || "";
}

const thumb = rel => {
  if (!rel) return "";
  return rel.replace("/renders/", "/_thumbs/renders__").replace(/\.png$/, ".jpg");
};

const nkey = (fam, dose) => fam + "|" + dose;              // the note belongs to the PRESET
const fkey = fam => fam + "|__family__";
let showStats = false, fit = false;
let stacked = !!M.stack;
let grid = [], ovr = 0, ovc = 0, ovfam = "";   // overlay: rows = prompts, columns = rungs
let focus = !!M.focus, fi = 0, compactF = true;

let curSeriesIdx = 0;
const hasSeries = !!(M.series && M.series.length);
let curSeries = hasSeries ? M.series[0] : null;
let PROMPTS = curSeries ? curSeries.prompts.filter(p => M.idx[p]) : ((M.promptOrder || Object.keys(M.idx).sort()).filter(p => M.idx[p]));
let P = PROMPTS[0] || "P1_elfbrawler", S = "3141592";

function ladderItems(p, s, fam) {
  const pSeeds = Object.keys(M.idx[p] || {});
  const actualSeed = (s && pSeeds.includes(s)) ? s : pSeeds[0];
  const rungs = ((M.idx[p] || {})[actualSeed] || {})[fam]; if (!rungs) return null;
  const bRel = (M.base[p] || {})[actualSeed] || null;
  const doses = Object.keys(rungs).sort((a, b) => parseFloat(a) - parseFloat(b));
  const items = []; let ins = false;
  for (const d of doses) {
    if (!ins && bRel && parseFloat(d) > 0) { items.push({d: "BASE", rel: bRel}); ins = true; }
    items.push({d, rel: rungs[d]});
  }
  if (!ins && bRel) items.push({d: "BASE", rel: bRel});
  return {label: p, base: bRel, items, seed: actualSeed};
}

function updatePromptOpts() {
  $("#prompt").innerHTML = "";
  for (const p of PROMPTS) $("#prompt").add(new Option(p, p));
  if (!PROMPTS.includes(P)) P = PROMPTS[0];
  $("#prompt").value = P;
}

function seedOpts() {
  $("#seed").innerHTML = "";
  const sList = Object.keys(M.idx[P] || {}).sort((a, b) => a - b);
  for (const s of sList) $("#seed").add(new Option("seed " + s, s));
  if (!(M.idx[P] || {})[S]) S = sList[0] || S;
  $("#seed").value = S;
}

function setSeries(idx) {
  if (!hasSeries) return;
  curSeriesIdx = (idx + M.series.length) % M.series.length;
  curSeries = M.series[curSeriesIdx];
  PROMPTS = curSeries.prompts.filter(p => M.idx[p]);
  M.bands = curSeries.bands;
  M.bandNames = curSeries.bandNames;
  $("#seriesname").textContent = curSeries.shortName || curSeries.name;
  $("#series").value = curSeriesIdx;
  updatePromptOpts();
  seedOpts();
  draw();
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
      im.onclick = () => { const row = ladderItems(P, S, fam);
        row.items = row.items.filter(x => hasBase || x.d !== "BASE");
        openOv([row], 0, row.items.findIndex(x => x.d === d), fam); };
      if (!isB) {
        const ta = document.createElement("textarea");
        ta.placeholder = "cosa sta succedendo qui…";
        const armKey = fam + "|" + (parseFloat(d) < 0 ? "neg" : "pos");
        const val = notes[nkey(fam, d)] || notes[armKey] || "";
        ta.value = val;
        if (val.trim()) ta.classList.add("filled");
        ta.oninput = () => {
          notes[nkey(fam, d)] = ta.value;
          notes[armKey] = ta.value;
          save();
          ta.classList.toggle("filled", !!ta.value.trim()); tally();
        };
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

function renderStacked() {
  const host = $("#fams"); host.innerHTML = "";
  for (const fam of M.order) {
    const rows = PROMPTS.map(p => ladderItems(p, S, fam)).filter(Boolean);
    if (!rows.length) continue;
    const info = M.groups[fam];
    const cols = rows[0].items.map(x => x.d);
    const card = document.createElement("div"); card.className = "card";
    const seriesDesc = curSeries ? ` · <span class="series-tag">${curSeries.name}</span>` : "";
    card.innerHTML = `<div class="famhead"><div><h2>${info.title}${seriesDesc}</h2>
        <p class="sub">${rows.length} prompt uno sotto l'altro · ${cols.length} colonne</p></div>
        <div class="meta">${info.meta}</div></div>`;
    const g = document.createElement("div"); g.className = "sgrid";
    g.style.gridTemplateColumns = `26px repeat(${cols.length}, var(--rw,200px))`;
    g.appendChild(document.createElement("div"));
    for (const d of cols) {
      const h = document.createElement("div"); h.className = "dlab " + (d === "BASE" ? "bas" : parseFloat(d) < 0 ? "neg" : "pos");
      h.textContent = d === "BASE" ? "BASELINE" : d; g.appendChild(h);
    }
    rows.forEach((row, r) => {
      const pl = document.createElement("div"); pl.className = "plab"; pl.textContent = row.label; g.appendChild(pl);
      row.items.forEach((it, c) => {
        const im = document.createElement("img"); im.loading = "lazy"; im.src = thumb(it.rel);
        im.className = "cellimg" + (it.d === "BASE" ? " isb" : ""); im.title = row.label + " · " + it.d;
        im.onclick = () => openOv(rows, r, c, fam);
        g.appendChild(im);
      });
    });
    g.appendChild(document.createElement("div"));
    for (const d of cols) {
      if (d === "BASE") { const n = document.createElement("div"); n.className = "nonote"; n.textContent = "il baseline non si annota"; g.appendChild(n); continue; }
      const ta = document.createElement("textarea"); ta.placeholder = d + ": cosa fa su tutti i prompt?";
      const armKey = fam + "|" + (parseFloat(d) < 0 ? "neg" : "pos");
      const val = notes[nkey(fam, d)] || notes[armKey] || "";
      ta.value = val; if (val.trim()) ta.classList.add("filled");
      ta.oninput = () => {
        notes[nkey(fam, d)] = ta.value;
        notes[armKey] = ta.value;
        save(); ta.classList.toggle("filled", !!ta.value.trim()); tally();
      };
      g.appendChild(ta);
    }
    card.appendChild(g);
    const fta = document.createElement("textarea");
    fta.placeholder = M.unit + " nel suo insieme: fa la stessa cosa sui prompt? che cosa compra, e a che prezzo…";
    fta.style.marginTop = "10px"; fta.style.border = "1px solid var(--line)"; fta.style.borderRadius = "8px";
    fta.value = notes[fkey(fam)] || "";
    fta.oninput = () => { notes[fkey(fam)] = fta.value; save(); };
    card.appendChild(fta);
    host.appendChild(card);
  }
  tally();
}
function renderFocus() {
  const host = $("#fams"); host.innerHTML = "";
  const fam = M.order[fi]; const info = M.groups[fam];
  $("#fsel").value = fam;
  const card = document.createElement("div"); card.className = "card";
  const seriesDesc = curSeries ? ` · <span class="series-tag">${curSeries.name}</span>` : "";
  card.innerHTML = `<div class="famhead"><div><h2>${info.title}${seriesDesc}</h2>
      <p class="sub">${PROMPTS.length} prompt · ogni colonna: −dose in alto, baseline, +dose in basso</p></div>
      <div class="meta">${info.meta}</div></div>`;
  const bands = compactF ? [PROMPTS] : (M.bands || [PROMPTS]);
  const W = Math.max(600, document.querySelector(".wrap").clientWidth - 60);
  // where the second group starts, to leave a visible gap between the two groups in the single band
  const sepAt = (compactF && M.bands && M.bands[1]) ? M.bands[1].find(p => !M.bands[0].includes(p)) : null;
  let first = null;
  bands.forEach((bp, bi) => {
    const rows = bp.map(p => ladderItems(p, S, fam)).filter(Boolean);
    if (!rows.length) return;
    if (!first) first = rows[0];
    const band = document.createElement("div"); band.className = "band";
    if (!compactF && M.bandNames && M.bandNames[bi]) { const h = document.createElement("h3"); h.textContent = M.bandNames[bi]; band.appendChild(h); }
    if (compactF && M.bandNames) {
      const h = document.createElement("h3");
      h.textContent = M.bandNames.length > 1 ? (M.bandNames[0] + "   |   " + (M.bandNames[1] || "")) : M.bandNames[0];
      band.appendChild(h);
    }
    const perRow = compactF ? rows.length : Math.max(1, Math.min(rows.length, Math.floor(W / 150)));
    for (let start = 0; start < rows.length; start += perRow) {
      const chunk = rows.slice(start, start + perRow);
      const g = document.createElement("div"); g.className = "fgrid";
      let cw = Math.floor((W - 30 - (sepAt ? 14 : 0)) / perRow) - 6;
      // all three rows (−, baseline, +) must fit in one screen: images are 4:5
      if (compactF) cw = Math.max(90, Math.min(cw, Math.floor((innerHeight - 190) / 3 / 1.25)));
      const k = sepAt ? chunk.findIndex(r => r.label === sepAt) : -1;
      g.style.gridTemplateColumns = k > 0
        ? `22px repeat(${k}, ${cw}px) 14px repeat(${chunk.length - k}, ${cw}px)`
        : `22px repeat(${chunk.length}, ${cw}px)`;
      const spacer = (lab) => { if (k > 0 && lab === sepAt) g.appendChild(document.createElement("div")); };
      g.appendChild(document.createElement("div"));
      chunk.forEach(r => { spacer(r.label); const l = document.createElement("div"); l.className = "plabel"; l.textContent = r.label; l.title = r.label; g.appendChild(l); });
      const cols = chunk[0].items.map(x => x.d);
      cols.forEach((d, ci) => {
        const rl = document.createElement("div"); rl.className = "rlab " + (d === "BASE" ? "bas" : parseFloat(d) < 0 ? "neg" : "pos");
        rl.textContent = d === "BASE" ? "BASE" : d; g.appendChild(rl);
        chunk.forEach(r => {
          const it = r.items.find(x => x.d === d); const im = document.createElement("img"); im.loading = "lazy";
          spacer(r.label);
          if (it) { im.src = thumb(it.rel); if (it.d === "BASE") im.classList.add("isb"); im.title = r.label + " · " + d;
                    const all = PROMPTS.map(p => ladderItems(p, S, fam)).filter(Boolean);
                    im.onclick = () => openOv(all, all.findIndex(x => x.label === r.label), all[all.findIndex(x => x.label === r.label)].items.findIndex(x => x.d === d), fam); }
          g.appendChild(im);
        });
      });
      band.appendChild(g);
    }
    card.appendChild(band);
  });
  const nt = document.createElement("div"); nt.className = "fnotes";
  if (first) first.items.filter(x => x.d !== "BASE").forEach(x => {
    const ta = document.createElement("textarea");
    ta.placeholder = x.d + ": cosa fa, su tutti i prompt?";
    const armKey = fam + "|" + (parseFloat(x.d) < 0 ? "neg" : "pos");
    const val = notes[nkey(fam, x.d)] || notes[armKey] || "";
    ta.value = val; if (val.trim()) ta.classList.add("filled");
    ta.oninput = () => {
      notes[nkey(fam, x.d)] = ta.value;
      notes[armKey] = ta.value;
      save(); ta.classList.toggle("filled", !!ta.value.trim()); tally();
    };
    nt.appendChild(ta);
  });
  const fta = document.createElement("textarea"); fta.className = "full";
  fta.placeholder = "il blocco nel suo insieme: cambia con il soggetto? cambia con lo stile? che nome gli daresti?";
  fta.value = notes[fkey(fam)] || ""; fta.oninput = () => { notes[fkey(fam)] = fta.value; save(); };
  nt.appendChild(fta); card.appendChild(nt);
  host.appendChild(card);
  tally();
}
function goBlock(n) { fi = (fi + n + M.order.length) % M.order.length; renderFocus(); window.scrollTo(0, document.getElementById("fnav").offsetTop - 10); }

function draw() {
  $("#focusbtn").classList.toggle("on", focus);
  $("#focusbtn").textContent = focus ? "Un blocco alla volta ✓" : "Un blocco alla volta";
  $("#fnav").style.display = focus ? "" : "none";
  if (focus) {
    $("#stack").style.display = "none"; $("#promptlab").style.display = "none"; $("#onerow").style.display = "none";
    $("#fams").classList.remove("stackwrap"); document.body.classList.add("stacked");
    renderFocus(); return;
  }
  $("#stack").style.display = "";
  $("#stack").classList.toggle("on", stacked);
  $("#stack").textContent = stacked ? "Prompt impilati ✓" : "Prompt impilati";
  $("#promptlab").style.display = stacked ? "none" : "";
  $("#onerow").style.display = stacked ? "none" : "";
  $("#fams").classList.toggle("stackwrap", stacked);
  document.body.classList.toggle("stacked", stacked);
  (stacked ? renderStacked : render)();
}

function tally() { const [n, t] = nTotal(); $("#count").textContent = n + " preset annotati su " + t; }

// ---------------------------------------------------------------- 1:1 overlay
let pos = null;                 // pan offset, KEPT across steps: the same region must stay
                                // under the eye, otherwise flicking between two doses compares
                                // nothing and the small differences are exactly what is lost.
function openOv(rows, r, c, fam) {
  grid = rows; ovr = r; ovc = c; ovfam = fam; fit = false; pos = null;
  $("#ov").classList.toggle("grid2", rows.length > 1);
  $("#ov").classList.add("show"); drawOv();
}
const cur = () => { const row = grid[ovr]; const it = row && row.items[ovc]; return it ? {...it, fam: ovfam} : null; };
function step(n) { const j = ovc + n; if (j < 0 || j >= grid[ovr].items.length) return; ovc = j; drawOv(); }
function vstep(n) {                          // another prompt, SAME dose, SAME pan position
  const r = ovr + n; if (r < 0 || r >= grid.length) return;
  const d = grid[ovr].items[ovc].d; const c = grid[r].items.findIndex(x => x.d === d);
  if (c < 0) return; ovr = r; ovc = c; drawOv();
}
function arrows() {
  const items = grid[ovr].items;
  const lab = k => { const it = items[k]; return it ? (it.d === "BASE" ? "BASELINE" : it.d) : ""; };
  $("#ovprev").disabled = ovc <= 0;
  $("#ovnext").disabled = ovc >= items.length - 1;
  $("#ovprev").querySelector(".to").textContent = lab(ovc - 1);
  $("#ovnext").querySelector(".to").textContent = lab(ovc + 1);
  $("#ovup").disabled = ovr <= 0;
  $("#ovdown").disabled = ovr >= grid.length - 1;
  $("#ovup").querySelector(".to").textContent = ovr > 0 ? grid[ovr - 1].label : "";
  $("#ovdown").querySelector(".to").textContent = ovr < grid.length - 1 ? grid[ovr + 1].label : "";
}
function drawOv() {
  const it = cur(); if (!it) return;
  const im = $("#ovimg");
  im.src = resolveRel(it.rel);
  im.onload = () => place();
  im.onerror = () => { $("#ovlab").textContent += "  — immagine non trovata"; };
  $("#ovlab").textContent = (grid.length > 1 ? grid[ovr].label + " · " : "") +
                            (it.d === "BASE" ? "BASELINE" : it.fam + "  " + it.d);
  const dis = it.d === "BASE";
  $("#ovnote").disabled = dis;
  const armKey = it.fam + "|" + (parseFloat(it.d) < 0 ? "neg" : "pos");
  $("#ovnote").value = dis ? "" : (notes[nkey(it.fam, it.d)] || notes[armKey] || "");
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
$("#ovup").onclick = () => vstep(-1);
$("#ovdown").onclick = () => vstep(1);
$("#ovclose").onclick = () => $("#ov").classList.remove("show");
$("#ovnote").oninput = () => {
  const it = cur();
  if (it && it.d !== "BASE") {
    notes[nkey(it.fam, it.d)] = $("#ovnote").value;
    notes[it.fam + "|" + (parseFloat(it.d) < 0 ? "neg" : "pos")] = $("#ovnote").value;
    save();
  }
};
let baseHeld = null;
const baseRel = () => (grid[ovr] && grid[ovr].base) || null;     // the baseline OF THIS ROW'S prompt
$("#ovbase").onmousedown = () => { const b = baseRel(); if (!b) return;
  baseHeld = $("#ovimg").src; $("#ovimg").src = resolveRel(b); };
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
  else if (e.key === "ArrowUp") { e.preventDefault(); vstep(-1); }
  else if (e.key === "ArrowDown") { e.preventDefault(); vstep(1); }
  else if (e.key.toLowerCase() === "b" && !e.repeat) {
    const b = baseRel(); if (!b) return;
    baseHeld = $("#ovimg").src; $("#ovimg").src = resolveRel(b); }
});
addEventListener("keyup", e => { if (e.key.toLowerCase() === "b" && baseHeld) {
  $("#ovimg").src = baseHeld; baseHeld = null; } });

// ---------------------------------------------------------------- controls
$("#prompt").onchange = () => { P = $("#prompt").value; seedOpts(); draw(); };
$("#seed").onchange = () => { S = $("#seed").value; draw(); };
$("#stack").onclick = () => { stacked = !stacked; draw(); };
$("#focusbtn").onclick = () => { focus = !focus; draw(); };
for (const f of M.order) $("#fsel").add(new Option(M.groups[f].title, f));
$("#fsel").onchange = () => { fi = M.order.indexOf($("#fsel").value); renderFocus(); };
$("#fprev").onclick = () => goBlock(-1);
$("#fcompact").onclick = () => { compactF = !compactF;
  $("#fcompact").textContent = compactF ? "Tutto in una schermata ✓" : "Tutto in una schermata";
  renderFocus(); };
addEventListener("resize", () => { if (focus) renderFocus(); });
$("#fnext").onclick = () => goBlock(1);
addEventListener("keydown", e => {
  const a = document.activeElement; if (a && (a.tagName === "TEXTAREA" || a.tagName === "SELECT" || a.tagName === "INPUT")) return;
  if (!$("#ov").classList.contains("show")) {
    if (e.key.toLowerCase() === "s") {
      e.preventDefault();
      setSeries(curSeriesIdx + 1);
      return;
    }
  }
  if (!focus || $("#ov").classList.contains("show")) return;
  if (e.key === "ArrowLeft") { e.preventDefault(); goBlock(-1); }
  else if (e.key === "ArrowRight") { e.preventDefault(); goBlock(1); }
});
$("#size").onchange = () => document.documentElement.style.setProperty("--rw", $("#size").value + "px");
$("#onerow").onclick = () => { const on = !document.querySelector(".ladder").classList.contains("onerow");
  document.querySelectorAll(".ladder").forEach(l => l.classList.toggle("onerow", on));
  $("#onerow").classList.toggle("on", on); };
$("#tstats").onclick = () => { showStats = !showStats;
  $("#tstats").classList.toggle("on", showStats);
  $("#tstats").textContent = showStats ? "Nascondi i numeri misurati" : "Mostra i numeri misurati";
  draw(); };

$("#exp").onclick = () => {
  let out = "# Appunti sui preset — " + M.sub + "\n\n";
  for (const fam of M.order) {
    const info = M.groups[fam];
    out += `## ${info.title}\n\n- ${info.meta.replace(/<br>/g, " · ").replace(/<\/?code>/g, "`")}\n\n`;
    const seen = new Set();
    for (const p of Object.keys(M.idx)) for (const s of Object.keys(M.idx[p]))
      for (const d of Object.keys((M.idx[p][s] || {})[fam] || {})) seen.add(d);
    for (const d of [...seen].sort((a, b) => parseFloat(a) - parseFloat(b))) {
      const armKey = fam + "|" + (parseFloat(d) < 0 ? "neg" : "pos");
      const t = (notes[nkey(fam, d)] || notes[armKey] || "").trim();
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
  a.download = "appunti_" + M.bench + ".md"; a.click(); };

if (hasSeries) {
  $("#seriesbtn").onclick = () => setSeries(curSeriesIdx + 1);
  M.series.forEach((s, i) => $("#series").add(new Option(s.name, i)));
  $("#series").onchange = () => setSeries(parseInt($("#series").value, 10));
  $("#seriesname").textContent = curSeries.shortName || curSeries.name;
} else {
  $("#seriesbtn").style.display = "none";
  $("#serieslab").style.display = "none";
}
updatePromptOpts();
seedOpts();
if (stacked) { document.documentElement.style.setProperty("--rw", "200px"); $("#size").value = "200"; }
draw();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
