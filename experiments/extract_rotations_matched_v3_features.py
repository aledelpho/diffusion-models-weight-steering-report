# -*- coding: utf-8 -*-
"""
experiments/extract_rotations_matched_v3_features.py
====================================================
Audit indipendente e estrazione delle feature per rotations_matched_v3 (324 PNG: 270 S01..S10 +
54 probe P01/P02). Ogni immagine e' risolta per nome file dal manifest, mai per posizione.

Per ogni PNG: dimensioni decodificate, sha256 contro il manifest e contro la copia in ComfyUI/output,
grafo nel tEXt contro nome file e contro gli angoli di data/matched_rotation_calibration_v3.json,
cancello di qualita' ricalcolato (grad_ratio, dL contro la baseline appaiata), feature style + palette.

Output: data/rotations_matched_v3_features.csv, data/rotations_matched_v3_audit.csv
"""
import os, sys, json, hashlib
import numpy as np, pandas as pd
from PIL import Image

REPORT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
PILOT = r"C:\Users\aless\Desktop\comfyui-pilot"
RENDERS = os.path.join(PILOT, "benchmark_rotations_matched_v3", "renders")
COMFY = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_rotations_matched_v3\renders"
DATA = os.path.join(REPORT, "data")
sys.path.insert(0, os.path.join(PILOT, "experiments"))
from style_features import extract_all_features
from analyze_palette import palette_features

man = pd.read_csv(os.path.join(DATA, "rotations_matched_v3_manifest.csv"))
cal = json.load(open(os.path.join(DATA, "matched_rotation_calibration_v3.json"), encoding="utf-8"))
on_disk = sorted(f for f in os.listdir(RENDERS) if f.endswith(".png"))
if sorted(man.file) != on_disk or man.file.duplicated().any():
    raise SystemExit(f"manifest ({len(man)}) e cartella ({len(on_disk)}) non coincidono")


def find_angles(obj, out):
    """raccoglie ogni valore 'angle_deg' del json di calibrazione alla dose 0.0071"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "angle_deg":
                out.append(float(v))
            find_angles(v, out)
    elif isinstance(obj, list):
        for v in obj:
            find_angles(v, out)


lvl = next((v for k, v in cal.get("levels", {}).items() if "0071" in k), None)
if lvl is None:
    raise SystemExit(f"livello d0071 assente dalla calibrazione: {list(cal.get('levels', {}))}")
cal_angles = []
find_angles(lvl, cal_angles)
TH1, TH6 = min(cal_angles), max(cal_angles)
print("angoli calibrati d0071:", sorted(set(cal_angles)), flush=True)

EXP = {"B1": ("ArthemyKrea2ModelRotator", "Block_1 (All 0-4)", TH1),
       "B6": ("ArthemyKrea2ModelRotator", "Block_6 (All 24-27)", TH6),
       "scrA": ("ArthemyKrea2ModelScrambleRotator", "scramble_A", TH1),
       "scrB": ("ArthemyKrea2ModelScrambleRotator", "scramble_B", TH6)}


def gray_stats(path):
    a = np.asarray(Image.open(path).convert("L"), float)
    gy, gx = np.gradient(a)
    return a.mean(), np.hypot(gx, gy).mean()


man = man.set_index("file")
audit, feats = [], []
for i, f in enumerate(on_disk):
    p = os.path.join(RENDERS, f)
    r = man.loc[f]
    raw = open(p, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    sha_c = hashlib.sha256(open(os.path.join(COMFY, f), "rb").read()).hexdigest() if os.path.exists(os.path.join(COMFY, f)) else None
    im = Image.open(p)
    shape = np.asarray(im.convert("RGB")).shape
    g = json.loads(im.text["prompt"])
    ks = next(v for v in g.values() if v["class_type"] == "KSampler")["inputs"]
    lat = next(v for v in g.values() if v["class_type"] == "EmptyLatentImage")["inputs"]
    txt = next(v for v in g.values() if v["class_type"] == "CLIPTextEncode")["inputs"]["text"]
    rot = [v for v in g.values() if "Rotator" in v["class_type"]]
    stem = f.rsplit("_", 2)[0]
    tag = "_".join(stem.split("_")[-2:]) if not stem.endswith("baseline") else "baseline"
    prompt_id = stem[: -(len(tag) + 1)].rsplit("_s", 1)[0]
    seed_f = int(stem[: -(len(tag) + 1)].rsplit("_s", 1)[1])
    problems = []
    if shape != (1280, 1024, 3): problems.append(f"shape {shape}")
    if sha != r.png_sha256: problems.append("sha != manifest")
    if sha_c is not None and sha_c != sha: problems.append("sha != comfy copy")
    if ks["seed"] != seed_f or ks["seed"] != r.seed: problems.append("seed")
    if (lat["width"], lat["height"]) != (1024, 1280): problems.append("latent")
    if (ks["steps"], ks["cfg"], ks["sampler_name"], ks["scheduler"], ks["denoise"]) != (9, 1.0, "euler_ancestral", "simple", 1.0):
        problems.append("sampler")
    if hashlib.sha1(txt.encode("utf-8")).hexdigest()[:10] != str(r.prompt_sha1): problems.append("prompt sha1")
    if tag != r.tag or prompt_id != r.prompt_id: problems.append("tag/prompt vs manifest")
    if tag == "baseline":
        if rot: problems.append("rotator in baseline")
    else:
        arm, sgn = tag.split("_")
        cls, tgt, th = EXP[arm]
        if len(rot) != 1: problems.append(f"{len(rot)} rotators")
        else:
            ri = rot[0]["inputs"]
            ang = float(ri.get("structural_rot_x", ri.get("angle")))
            if rot[0]["class_type"] != cls: problems.append("class")
            if ri.get("target_block", ri.get("control")) != tgt: problems.append("target")
            if abs(ang - (th if sgn == "pos" else -th)) > 1e-6: problems.append(f"angle {ang}")
            if any(abs(float(ri.get(k, 0))) > 0 for k in ("structural_rot_y", "tensor_rot_x", "tensor_rot_y")): problems.append("extra rot")
    L, G = gray_stats(p)
    audit.append(dict(file=f, prompt_id=prompt_id, seed=seed_f, tag=tag, L=L, grad=G, problems=";".join(problems)))
    sf = extract_all_features(p)
    pf = palette_features(p, RENDERS)
    row = {"file": f}
    row.update({k: v for k, v in sf.items() if k not in ("file", "seed")})
    row.update({k: v for k, v in pf.items() if k not in ("file", "seed", "prompt_sha1", "prompt_dir", "rel_path") and k not in row})
    feats.append(row)
    if (i + 1) % 20 == 0:
        print(i + 1, flush=True)

a = pd.DataFrame(audit)
b = a[a.tag == "baseline"].set_index(["prompt_id", "seed"])
a["grad_ratio"] = [r.grad / b.loc[(r.prompt_id, r.seed), "grad"] for r in a.itertuples()]
a["dL"] = [r.L - b.loc[(r.prompt_id, r.seed), "L"] for r in a.itertuples()]
a["passed"] = a.grad_ratio.between(0.67, 1.50) & (a.dL.abs() <= 20)
a.to_csv(os.path.join(DATA, "rotations_matched_v3_audit.csv"), index=False)
pd.DataFrame(feats).to_csv(os.path.join(DATA, "rotations_matched_v3_features.csv"), index=False)
print("problemi:", (a.problems.fillna("") != "").sum(), flush=True)
print("DONE", len(a), flush=True)
