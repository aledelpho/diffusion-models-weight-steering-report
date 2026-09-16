"""
experiments/derive_subset.py  --  la curva del numero di blocchi, a spostamento fisso

LA TESI DA TESTARE, che e' di Alessandro e non mia:
"ogni blocco da solo spinge molto meno della combinazione di essi, quindi era
fondamentale bilanciarli alla fine".

E' un'affermazione di SUPERADDITIVITA', ed e' gia' parzialmente misurata senza
volerlo. Lo Stage 2 ha messo un blocco singolo a D = 0.05 e non ha trovato nulla
sopra il rumore del seed. Il preset intero sta a D = 0.0538 -- lo STESSO gradino,
lo stesso spostamento relativo globale -- e produce l'unica direzione coerente
sulla morfologia del tratto di tutto il benchmark. Stessa ampiezza, esito
opposto: cambia solo se lo spostamento sta in un blocco o e' distribuito su
ventotto.

Quello che manca e' il mezzo. Questa e' la curva: si tengono k blocchi del preset
vero, si azzerano gli altri, e si riscala il sottoinsieme tenuto perche' lo
spostamento di Frobenius TOTALE torni esattamente quello del preset intero. Cosi'
l'unica variabile e' su quanti blocchi lo spostamento e' distribuito.

    k = 4        \\
    k = 10        >  nuovi, da generare
    k = 18       /
    k = 28   = il preset intero, gia' generato

Se la coerenza cresce con k a spostamento fisso, il bilanciamento e' il
meccanismo e la tesi e' misurata. Se e' piatta, conta solo quali blocchi, non
quanti.

PERCHE' NON BASTA UN SOTTOINSIEME SOLO PER k. Un singolo sorteggio potrebbe
pescare per caso i blocchi che contano. Di default i blocchi si scelgono
stratificati sulla profondita' (uno ogni 28/k, con sfasamento dal seme), cosi'
nessun k e' concentrato nella stessa parte della rete. Con --mode top si tengono
invece i k blocchi con |valore| medio piu' alto: e' la domanda diversa "bastano i
blocchi che hai spinto di piu'?", e vale la pena farla dopo, non insieme.

Riscalatura: come in derive_blockshuffle, alpha si misura e si applica SOLO al
sottoinsieme tenuto. Qui pero' il resto e' AZZERATO, non lasciato intatto, quindi
alpha deve compensare anche l'energia persa: si riporta il totale a quello del
preset intero, compresi i 66 tensori fuori blocco e le rotazioni, che NON si
toccano mai.
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

BASE = "Arthemy_Bench_Base"
MODEL_FILE = "krea2_turbo_bf16.safetensors"
CLIP_FILE = "qwen3vl_4b_bf16.safetensors"
KS = [4, 10, 18]
SEED = 20260915


def find_model(fn):
    for root, _d, files in os.walk(MODELS_ROOT):
        if fn in files:
            return os.path.join(root, fn)
    raise FileNotFoundError(fn)


def split_indexed(patches, pattern):
    rx = re.compile(pattern)
    grouped, rest = defaultdict(dict), {}
    for k, v in patches.items():
        m = rx.match(k)
        if m:
            grouped[int(m.group(1))][m.group(2)] = v
        else:
            rest[k] = v
    return dict(grouped), rest


def norm_table(path, keys):
    want, norms = set(keys), {}
    with safetensors.safe_open(path, framework="pt", device="cpu") as f:
        for raw in f.keys():
            ck = Krea2TensorParser.clean_key(raw)
            if ck in want and ck not in norms:
                norms[ck] = float(torch.linalg.vector_norm(
                    f.get_tensor(raw).to(torch.float32)).item())
    if want - set(norms):
        raise KeyError(f"{len(want - set(norms))} chiavi senza tensore")
    return norms


def dn(patches, norms):
    return math.sqrt(sum((v * norms[k]) ** 2 for k, v in patches.items()))


def choose(indices, k, mode, grouped, seed):
    if mode == "top":
        forza = {i: sum(abs(v) for v in grouped[i].values()) / len(grouped[i]) for i in indices}
        return sorted(sorted(indices, key=lambda i: -forza[i])[:k])
    # stratificato sulla profondita': nessun k concentrato in una zona sola
    n = len(indices)
    off = (seed + k) % max(1, n // k)
    pos = [int(round(off + i * (n - 1 - off) / max(k - 1, 1))) for i in range(k)]
    return sorted({indices[min(p, n - 1)] for p in pos})


def build(base, k, mode, m_norms, c_norms, force):
    mp, cp = base["model_patches"], base["clip_patches"]
    out_p = {}
    info = {}
    for dom, patches, pat, pref, norms in (
            ("modello", mp, r"blocks\.(\d+)\.(.*)", "blocks.", m_norms),
            ("clip", cp, r"layers\.(\d+)\.(.*)", "layers.", c_norms)):
        grouped, rest = split_indexed(patches, pat)
        idx = sorted(grouped)
        kk = max(2, min(k, len(idx))) if dom == "modello" else \
            max(2, min(int(round(k * len(idx) / 28)), len(idx)))
        keep = choose(idx, kk, mode, grouped, SEED)

        sub_full = {f"{pref}{i}.{s}": v for i in idx for s, v in grouped[i].items()}
        sub_keep = {f"{pref}{i}.{s}": v for i in keep for s, v in grouped[i].items()}
        d_rest = dn(rest, norms)
        d_tot = math.hypot(dn(sub_full, norms), d_rest)
        d_keep = dn(sub_keep, norms)
        # alpha riporta il TOTALE a quello del preset intero, compensando anche
        # i blocchi azzerati
        target = d_tot ** 2 - d_rest ** 2
        if target <= 0:
            raise RuntimeError(f"{dom}: il resto da solo supera il totale")
        alpha = math.sqrt(target) / d_keep
        new = dict(rest)
        new.update({kx: v * alpha for kx, v in sub_keep.items()})
        for i in idx:
            if i not in keep:
                for s in grouped[i]:
                    new[f"{pref}{i}.{s}"] = 0.0
        res = math.hypot(dn({kx: v for kx, v in new.items() if kx not in rest}, norms),
                         d_rest) / d_tot - 1.0
        if abs(res) > 1e-9:
            raise RuntimeError(f"{dom}: riscalatura non convergente ({res:.2e})")
        print(f"   {dom:8s} tenuti {len(keep):2d}/{len(idx)}  alpha {alpha:6.3f}  "
              f"residuo {res:+.1e}   {keep if dom=='modello' else ''}")
        out_p[dom] = new
        info[dom] = dict(keep=keep, alpha=round(alpha, 6), n=len(idx))

    name = f"Arthemy_Bench_K{k:02d}"
    o = json.loads(json.dumps(base))
    o["name"] = name
    o["model_patches"] = out_p["modello"]
    o["clip_patches"] = out_p["clip"]
    o["notes"] = (
        f"Sottoinsieme di {k} blocchi del preset intero, gli altri azzerati, il "
        f"tenuto riscalato perche' lo spostamento di Frobenius TOTALE torni "
        f"esattamente quello del preset intero (modello alpha "
        f"{info['modello']['alpha']}, clip alpha {info['clip']['alpha']}). I 66 "
        f"tensori fuori blocco, i 288 della torre visiva e le 4 rotazioni su "
        f"Block_3 restano identici al Base. Blocchi tenuti (modo {mode}, "
        f"seme {SEED}): {info['modello']['keep']}. Serve a misurare se la "
        f"coerenza cresce col NUMERO di blocchi su cui lo spostamento e' "
        f"distribuito, a spostamento fisso.")
    neg = json.loads(json.dumps(o))
    neg["name"] = name + "_NEG"
    neg["model_patches"] = {kx: -v for kx, v in o["model_patches"].items()}
    neg["clip_patches"] = {kx: -v for kx, v in o["clip_patches"].items()}
    for r in neg.get("rotation_recipes", []):
        r["rotation_angle"] = -r["rotation_angle"]
    neg["notes"] = "NEG di " + name + ". " + o["notes"]

    for obj in (o, neg):
        p = os.path.join(PRESET_DIR, obj["name"] + ".json")
        if os.path.exists(p) and not force:
            raise FileExistsError(f"{p} esiste gia'. --force solo su questi.")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1)
        print(f"   scritto {obj['name']}.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["random", "top"], default="random")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    with open(os.path.join(PRESET_DIR, BASE + ".json"), encoding="utf-8") as f:
        base = json.load(f)
    print("[subset] norme di Frobenius dai pesi reali...")
    m_norms = norm_table(find_model(MODEL_FILE), base["model_patches"].keys())
    c_norms = norm_table(find_model(CLIP_FILE), base["clip_patches"].keys())

    for k in KS:
        print(f"\n[subset] k = {k}   (modo {args.mode})")
        build(base, k, args.mode, m_norms, c_norms, args.force)

    print("\n[subset] la curva sara':  k=4  k=10  k=18  k=28(gia' generato)")


if __name__ == "__main__":
    main()
