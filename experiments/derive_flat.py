"""
experiments/derive_flat.py  --  isolare il lavoro sui sub-blocchi

QUELLO CHE HAI DESCRITTO. "Se un blocco intero migliorava e peggiorava
contemporaneamente degli attributi ma mi piaceva la direzione generale, provavo a
usare i sub-blocchi per trattenere quel set di attributi positivi, evitando
quelli che mi davano problemi."

QUELLO CHE C'E' NEL FILE. Il preset e' quasi ovunque costante dentro il blocco --
dev 0.000000 su B10..B14 e su tutti i layer di testo del CLIP, 0.0003 su
B00..B04, B15..B19, B20..B23. Con UNA eccezione netta:

    B05..B09   media +0.038   dev 0.077   da -0.045 a +0.110 sui 13 componenti
               e lo STESSO profilo interno, identico, su tutti e cinque i blocchi

Quello e' il lavoro sui sub-blocchi, ed e' l'unico posto dell'intero preset dove
c'e' struttura per componente invece che un valore per blocco. Non e' una
congettura sul processo: e' leggibile nel file.

IL CONTROLLO. FLAT sostituisce a ogni blocco la MEDIA dei suoi tredici valori,
tenendo cosi' il profilo in profondita' -- quali blocchi spinti, in che verso, di
quanto -- e cancellando la struttura interna. Poi riscala perche' lo spostamento
di Frobenius torni esattamente quello del preset intero, che appiattire da solo
non conserva.

    preset   profilo di profondita' + struttura sub-blocco
    FLAT     profilo di profondita', struttura sub-blocco cancellata
    (BLOCKSHUFFLE: profilo di profondita' permutato, struttura portata con se')

preset - FLAT misura QUANTO VALGONO quei due o tre giorni sui sub-blocchi. Se e'
zero, la struttura interna non serviva e il profilo per blocco bastava -- che e'
un risultato utile, perche' semplifica enormemente la procedura. Se non e' zero,
e' la prova che il lavoro fine porta informazione.

100 immagini: 2 condizioni x 10 prompt x 5 seed, circa 47 minuti.
"""

import os
import re
import sys
import json
import math
import argparse
from collections import defaultdict

import torch
import safetensors

COMFY_ROOT = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
SUITE_DIR = os.path.join(COMFY_ROOT, "custom_nodes", "Arthemy_Krea2_Tuner")
PRESET_DIR = os.path.join(SUITE_DIR, "presets")
MODELS_ROOT = r"C:\StabilityMatrix-win-x64\Data\Models"
sys.path.insert(0, COMFY_ROOT)
sys.path.append(SUITE_DIR)
from Arthemy_Krea2_Tuner import Krea2TensorParser

BASE, OUT, NEG = "Arthemy_Bench_Base", "Arthemy_Bench_FLAT", "Arthemy_Bench_FLAT_NEG"


def find_model(fn):
    for root, _d, files in os.walk(MODELS_ROOT):
        if fn in files:
            return os.path.join(root, fn)
    raise FileNotFoundError(fn)


def split_indexed(patches, pattern):
    rx = re.compile(pattern)
    g, rest = defaultdict(dict), {}
    for k, v in patches.items():
        m = rx.match(k)
        if m:
            g[int(m.group(1))][m.group(2)] = v
        else:
            rest[k] = v
    return dict(g), rest


def norm_table(path, keys):
    want, norms = set(keys), {}
    with safetensors.safe_open(path, framework="pt", device="cpu") as f:
        for raw in f.keys():
            ck = Krea2TensorParser.clean_key(raw)
            if ck in want and ck not in norms:
                norms[ck] = float(torch.linalg.vector_norm(
                    f.get_tensor(raw).to(torch.float32)).item())
    if want - set(norms):
        raise KeyError("chiavi senza tensore")
    return norms


def dn(p, n):
    return math.sqrt(sum((v * n[k]) ** 2 for k, v in p.items()))


def flatten(patches, pattern, prefix, norms, label):
    g, rest = split_indexed(patches, pattern)
    sub = {f"{prefix}{i}.{s}": v for i, prof in g.items() for s, v in prof.items()}
    flat = {}
    devs = []
    for i, prof in g.items():
        m = sum(prof.values()) / len(prof)
        devs.append((i, (sum((v - m) ** 2 for v in prof.values()) / len(prof)) ** 0.5))
        for s in prof:
            flat[f"{prefix}{i}.{s}"] = m
    d0, d1 = dn(sub, norms), dn(flat, norms)
    alpha = d0 / d1
    flat = {k: v * alpha for k, v in flat.items()}
    res = dn(flat, norms) / d0 - 1.0
    if abs(res) > 1e-9:
        raise RuntimeError(f"{label}: riscalatura non convergente")
    devs.sort(key=lambda x: -x[1])
    print(f"   {label:8s} alpha {alpha:.6f}  residuo {res:+.1e}   "
          f"struttura interna piu' forte: " +
          ", ".join(f"{prefix[0].upper()}{i:02d} dev {d:.4f}" for i, d in devs[:5]))
    out = dict(rest)
    out.update(flat)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(PRESET_DIR, BASE + ".json"), encoding="utf-8") as f:
        base = json.load(f)
    print("[flat] norme di Frobenius dai pesi reali...")
    mn = norm_table(find_model("krea2_turbo_bf16.safetensors"), base["model_patches"].keys())
    cn = norm_table(find_model("qwen3vl_4b_bf16.safetensors"), base["clip_patches"].keys())

    o = json.loads(json.dumps(base))
    o["name"] = OUT
    o["model_patches"] = flatten(base["model_patches"], r"blocks\.(\d+)\.(.*)", "blocks.", mn, "modello")
    o["clip_patches"] = flatten(base["clip_patches"], r"layers\.(\d+)\.(.*)", "layers.", cn, "clip")
    o["notes"] = ("Ogni blocco ridotto alla MEDIA dei suoi valori: il profilo in "
                  "profondita' resta intatto, la struttura per sub-componente e' "
                  "cancellata. Riscalato perche' lo spostamento di Frobenius torni "
                  "esattamente quello del preset intero. I tensori fuori blocco, la "
                  "torre visiva e le 4 rotazioni su Block_3 non si toccano. "
                  "preset - FLAT misura quanto vale il lavoro sui sub-blocchi, che "
                  "nel file vive quasi tutto in B05..B09.")
    n = json.loads(json.dumps(o))
    n["name"] = NEG
    n["model_patches"] = {k: -v for k, v in o["model_patches"].items()}
    n["clip_patches"] = {k: -v for k, v in o["clip_patches"].items()}
    for r in n.get("rotation_recipes", []):
        r["rotation_angle"] = -r["rotation_angle"]
    n["notes"] = "NEG di " + OUT + ". " + o["notes"]

    for obj in (o, n):
        p = os.path.join(PRESET_DIR, obj["name"] + ".json")
        if os.path.exists(p) and not a.force:
            raise FileExistsError(f"{p} esiste gia'. --force solo su questi due.")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1)
        print(f"[flat] scritto {obj['name']}.json  "
              f"({len(obj['model_patches'])}/{len(obj['clip_patches'])})")


if __name__ == "__main__":
    main()
