# -*- coding: utf-8 -*-
"""
experiments/gate_rotations_matched_v4.py
========================================
Cancelli di rotations_matched_v4. Scritto da chi analizza, eseguito da chi rende.
Ogni sottocomando stampa una tabella e termina con codice 0 (PASSATO) o 1 (FALLITO).
Chi esegue incolla l'output **integralmente** nel log: nessun riassunto a parole.

  python gate_rotations_matched_v4.py identity           controllo di identita' a 0 gradi
  python gate_rotations_matched_v4.py pilot d0035        pilota a una dose (80 immagini attive)
  python gate_rotations_matched_v4.py full d0025         corpus completo (270) alla dose scelta
  python gate_rotations_matched_v4.py probes d0025       probe P01/P02 (54), esplorativi

La dose si passa come chiave di data/matched_rotation_calibration_v4.json (d0035, d0025, d0018).
"""
import os, sys, json, hashlib, itertools
import numpy as np, pandas as pd
from PIL import Image

OUT = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"
REPORT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
DATA = os.path.join(REPORT, "data")
CAL = json.load(open(os.path.join(DATA, "matched_rotation_calibration_v4.json"), encoding="utf-8"))

S_PROMPTS = {"S01_oil": "6de4189f5e", "S02_linocut": "e20e86ac75", "S03_cyberpunk": "6ab02b69aa",
             "S04_gouache": "6335032007", "S05_pencil": "9a68323a39", "S06_pastel": "61861c7677",
             "S07_comic": "69f4e68eba", "S08_papercraft": "17e466c859", "S09_fresco": "9e81add78f",
             "S10_synthwave": "25147e923b"}
P_PROMPTS = {"P01": "52e5b19ca6", "P02": "7919c95fcf"}
TAGS = ["baseline", "B1_pos", "B1_neg", "B6_pos", "B6_neg", "scrA_pos", "scrA_neg", "scrB_pos", "scrB_neg"]
ARM = {"B1": ("ArthemyKrea2ModelRotator", "Block_1 (All 0-4)", "theta_B1_deg"),
       "B6": ("ArthemyKrea2ModelRotator", "Block_6 (All 24-27)", "theta_B6_deg"),
       "scrA": ("ArthemyKrea2ModelScrambleRotator", "scramble_A", "theta_B1_deg"),
       "scrB": ("ArthemyKrea2ModelScrambleRotator", "scramble_B", "theta_B6_deg")}


def graph_of(path):
    im = Image.open(path)
    g = json.loads(im.text["prompt"])
    ks = next(v for v in g.values() if v["class_type"] == "KSampler")["inputs"]
    lat = next(v for v in g.values() if v["class_type"] == "EmptyLatentImage")["inputs"]
    txt = next(v for v in g.values() if v["class_type"] == "CLIPTextEncode")["inputs"]["text"]
    rot = [v for v in g.values() if "Rotator" in v["class_type"]]
    bad = [v["class_type"] for v in g.values() if any(s in v["class_type"].lower() for s in ("hud", "stitch", "visual", "drawtext", "overlay"))]
    return im, ks, lat, txt, rot, bad


def check_image(path, prompt_id, sha1, seed, tag, dose_key):
    problems = []
    im, ks, lat, txt, rot, bad = graph_of(path)
    if np.asarray(im.convert("RGB")).shape != (1280, 1024, 3): problems.append("dimensioni")
    if bad: problems.append(f"nodi vietati {bad}")
    if ks["seed"] != seed: problems.append("seed")
    if (lat["width"], lat["height"]) != (1024, 1280): problems.append("latente")
    if (ks["steps"], float(ks["cfg"]), ks["sampler_name"], ks["scheduler"], float(ks["denoise"])) != (9, 1.0, "euler_ancestral", "simple", 1.0):
        problems.append("sampler")
    if hashlib.sha1(txt.encode("utf-8")).hexdigest()[:10] != sha1: problems.append("sha1 prompt")
    if tag == "baseline":
        if rot: problems.append("rotatore nella baseline")
    else:
        arm, sgn = tag.split("_")
        cls, target, key = ARM[arm]
        want = CAL["levels"][dose_key][key] * (1 if sgn == "pos" else -1)
        if len(rot) != 1:
            problems.append(f"{len(rot)} rotatori")
        else:
            ri = rot[0]["inputs"]
            got = float(ri.get("structural_rot_x", ri.get("angle")))
            if rot[0]["class_type"] != cls: problems.append("classe nodo")
            if ri.get("target_block", ri.get("control")) != target: problems.append("bersaglio")
            if abs(got - want) > 1e-9: problems.append(f"angolo {got} invece di {want}")
            if any(abs(float(ri.get(k, 0))) > 0 for k in ("structural_rot_y", "tensor_rot_x", "tensor_rot_y")): problems.append("altre rotazioni")
            if ri.get("depth_reach", "Default") != "Default": problems.append("depth_reach")
            if cls.endswith("ModelRotator") and ri.get("sub_components") != "All Components": problems.append("sub_components")
    return problems


def gray(path):
    a = np.asarray(Image.open(path).convert("L"), float)
    gy, gx = np.gradient(a)
    return a.mean(), float(np.hypot(gx, gy).mean())


def run_set(folder, prompts, seeds, dose_key, out_csv):
    if not os.path.isdir(folder):
        print(f"cartella assente: {folder}"); return 1
    files = sorted(f for f in os.listdir(folder))
    expected = {f"{p}_s{s}_{t}_00001_.png": (p, s, t) for p, s, t in itertools.product(prompts, seeds, TAGS)}
    extra, missing = sorted(set(files) - set(expected)), sorted(set(expected) - set(files))
    print(f"file attesi {len(expected)}, trovati {len(files)}, mancanti {len(missing)}, estranei {len(extra)}")
    for f in (missing + extra)[:10]: print("   ", f)
    rows, fail_struct, shas = [], 0, {}
    for f, (p, s, t) in expected.items():
        if f not in files: continue
        path = os.path.join(folder, f)
        pr = check_image(path, p, prompts[p], s, t, dose_key)
        sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if sha in shas: pr.append(f"duplicato di {shas[sha]}")
        shas[sha] = f
        L, G = gray(path)
        rows.append(dict(prompt_id=p, seed=s, tag=t, file=f, sha256=sha, L=L, grad=G, problems=";".join(pr)))
        fail_struct += bool(pr)
    df = pd.DataFrame(rows)
    b = df[df.tag == "baseline"].set_index(["prompt_id", "seed"])
    act = df[df.tag != "baseline"].copy()
    act["baseline_file"] = [b.loc[(r.prompt_id, r.seed), "file"] for r in act.itertuples()]
    act["grad_ratio"] = [r.grad / b.loc[(r.prompt_id, r.seed), "grad"] for r in act.itertuples()]
    act["dL"] = [r.L - b.loc[(r.prompt_id, r.seed), "L"] for r in act.itertuples()]
    act["passed"] = act.grad_ratio.between(0.67, 1.50) & (act.dL.abs() <= 20)
    act[["prompt_id", "seed", "tag", "file", "baseline_file", "grad_ratio", "dL", "passed", "sha256", "problems"]].to_csv(out_csv, index=False)
    pd.set_option("display.width", 200)
    print(f"\nproblemi strutturali (grafo, dimensioni, duplicati): {fail_struct}")
    for r in df[df.problems != ""].itertuples(): print("   ", r.file, r.problems)
    summ = act.groupby("tag").agg(n=("passed", "size"), falliti=("passed", lambda x: int((~x).sum())),
                                  dL_min=("dL", "min"), dL_max=("dL", "max"),
                                  grad_min=("grad_ratio", "min"), grad_max=("grad_ratio", "max")).round(3)
    print("\ncancello di qualita' (grad_ratio in [0.67, 1.50], |dL| <= 20) per condizione:")
    print(summ.to_string())
    print(f"\nscritto: {out_csv}")
    return act, fail_struct, bool(missing or extra)


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "identity":
        folder = os.path.join(OUT, "benchmark_rotations_matched_v4_pilot", "identity")
        base = os.path.join(folder, "S01_oil_s90210_baseline_00001_.png")
        ref = np.asarray(Image.open(base).convert("RGB"))
        ok = True
        for t in ("B1_zero", "B6_zero", "scrA_zero", "scrB_zero"):
            p = os.path.join(folder, f"S01_oil_s90210_{t}_00001_.png")
            im, ks, lat, txt, rot, bad = graph_of(p)
            ang = float(rot[0]["inputs"].get("structural_rot_x", rot[0]["inputs"].get("angle"))) if len(rot) == 1 else None
            d = int(np.abs(np.asarray(im.convert("RGB")).astype(int) - ref.astype(int)).max())
            passed = len(rot) == 1 and ang == 0.0 and d == 0
            ok &= passed
            print(f"{t:10s} rotatori {len(rot)} angolo {ang}  differenza massima di canale {d}  {'OK' if passed else 'FALLITO'}")
        print("IDENTITA':", "PASSATA" if ok else "FALLITA")
        sys.exit(0 if ok else 1)
    dose = sys.argv[2]
    if dose not in CAL["levels"]:
        print(f"dose sconosciuta {dose}; disponibili {list(CAL['levels'])}"); sys.exit(2)
    if not CAL["levels"][dose]["dose_gate_passed"]:
        print(f"{dose} NON ha passato il cancello bf16 della calibrazione: non va resa"); sys.exit(1)
    if cmd == "pilot":
        act, fs, cov = run_set(os.path.join(OUT, "benchmark_rotations_matched_v4_pilot", dose), S_PROMPTS, [90210], dose,
                               os.path.join(DATA, f"rotations_matched_v4_pilot_gate_{dose}.csv"))
        ok = not fs and not cov and bool(act.passed.all())
        print(f"\nPILOTA {dose}: {int(act.passed.sum())}/{len(act)} immagini attive passano ->",
              "PASSATO: questa e' la dose" if ok else "FALLITO: prova la dose successiva della scala, o fermati se era l'ultima")
        sys.exit(0 if ok else 1)
    if cmd in ("full", "probes"):
        if cmd == "full":
            folder, prompts, seeds = os.path.join(OUT, "benchmark_rotations_matched_v4", "renders"), S_PROMPTS, [42, 1337, 4242145]
            out = os.path.join(DATA, "rotations_matched_v4_quality_gate.csv")
        else:
            folder, prompts, seeds = os.path.join(OUT, "benchmark_rotations_matched_v4_probes", "renders"), P_PROMPTS, [2718281, 3141592, 1618033]
            out = os.path.join(DATA, "rotations_matched_v4_probes_quality_gate.csv")
        act, fs, cov = run_set(folder, prompts, seeds, dose, out)
        ok = not fs and not cov
        deg = act.groupby("tag").passed.apply(lambda x: int((~x).sum()))
        print("\ncondizioni in regime degradato (piu' del 10% fallite):", [t for t, n in deg.items() if n > 0.1 * len(seeds) * len(prompts)] or "nessuna")
        print(f"\nSTRUTTURA {cmd.upper()}:", "PASSATA" if ok else "FALLITA — fermati")
        sys.exit(0 if ok else 1)
    print(__doc__); sys.exit(2)


if __name__ == "__main__":
    main()
