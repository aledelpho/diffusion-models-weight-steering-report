"""
experiments/derive_blockshuffle.py  --  il controllo di assegnazione

PERCHE'.
Lo Stage 4 ha confrontato il preset con RANDSIGN: stessi |valori|, segno di ogni
singolo tensore sorteggiato, spostamento di Frobenius identico per costruzione.
Sembrava il controllo giusto. Non lo era del tutto.

Il preset non e' una lista di 1059 scelte indipendenti. E' costante a blocchi:
i 28 blocchi del DiT hanno 13 tensori ciascuno con gli stessi suffissi, i 31
layer di testo del CLIP ne hanno 11, e dentro un blocco il valore e' lo stesso
o quasi (dev 0.000000 su meta' dei blocchi e su tutti i layer del CLIP). Il
segno concorda al 96% fra tensori adiacenti dello stesso blocco contro l'88%
sull'intero file. B05..B09 non sono nemmeno piatti: portano un profilo interno
forte (da -0.045 a +0.110 sui 13 componenti) replicato identico su cinque
blocchi consecutivi.

Quindi capovolgere il segno di ogni singolo delta non randomizza
un'assegnazione: DISTRUGGE LA COERENZA DI BLOCCO. Lo Stage 4 ha misurato
"coerente batte incoerente a pari norma", che e' gia' qualcosa, ma non ancora
"questa assegnazione batte un'assegnazione qualunque".

COSA FA.
Permuta i profili fra blocchi, componente per componente. Ogni blocco del DiT
riceve il vettore di 13 valori di un altro blocco; ogni layer di testo del CLIP
riceve gli 11 valori di un altro layer. Derangement con seme fisso, col vincolo
che nessun blocco riceva un profilo NUMERICAMENTE uguale al proprio (B10, B12 e
B13 sono tutti -0.025: cambiare indice non basta).

NON tocca, e questo e' il punto corretto rispetto alla prima versione:
  - i 66 tensori del modello senza indice di blocco (txtfusion, first, last,
    tmlp, tproj, txtmlp): non sono blocchi, non c'e' niente da permutare;
  - i 288 tensori della torre visiva del CLIP: tutti esattamente -0.025, e
    comunque inerti in una generazione testo->immagine;
  - le 4 ricette di rotazione su Block_3.
Restano BIT PER BIT quelli del Base, cosi' BLOCKSHUFFLE differisce in una cosa
sola: quale blocco riceve quale profilo.

RISCALATURA -- e il bug che c'era qui.
Permutare non conserva lo spostamento: blocchi diversi hanno norme diverse.
Serve un fattore alpha, e ||dW|| e' esattamente lineare in alpha, quindi basta
una divisione. Ma la prima versione di questo script calcolava alpha su TUTTI i
tensori del preset e lo applicava a TUTTI, comprese le parti non permutate. Il
risultato: la torre visiva del CLIP finiva a -0.027307 invece di -0.025000, e
sui soli 341 layer di linguaggio -- gli unici che leggono il prompt -- il
controllo risultava il 3.94% piu' debole del preset. Un controllo piu' debole
del trattamento non e' un controllo.

La forma giusta e' ovvia una volta vista: alpha si misura e si applica SOLO al
sottoinsieme permutato. Quello che non e' stato permutato resta identico, e
allora
    ||dW||^2 = (parte permutata, riportata a quella del Base) + (resto, identico)
combacia sul sottoinsieme, sul resto e sul totale insieme. Tre gate invece di
uno, e nessuna parte del preset viene alterata senza motivo.

NOTA SUL GATE PRECEDENTE.
Il gate usato per Base/NEG/HALF/RANDSIGN cercava i tensori del CLIP col prefisso
model.language_model.* e contava 288 miss senza fermarsi: misurava 341 tensori
su 629. Per quei preset non cambiava nulla, perche' conservavano |valore| esatto
e quindi combaciavano su qualunque sottoinsieme. Qui invece avrebbe nascosto
proprio lo scarto del 3.94%. Il miss silenzioso va tolto dal gate.

Scrive Arthemy_Bench_BLOCKSHUFFLE.json e Arthemy_Bench_BLOCKSHUFFLE_NEG.json
(NEG = tutti i valori x -1, rotation_angle compreso).
"""

import os
import re
import sys
import json
import math
import random
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

BASE_NAME = "Arthemy_Bench_Base"
OUT_NAME = "Arthemy_Bench_BLOCKSHUFFLE"
NEG_NAME = "Arthemy_Bench_BLOCKSHUFFLE_NEG"

MODEL_FILE = "krea2_turbo_bf16.safetensors"
CLIP_FILE = "qwen3vl_4b_bf16.safetensors"

# seme fissato una volta e mai piu' toccato
PERM_SEED = 20260914


def find_model(filename):
    for root, _dirs, files in os.walk(MODELS_ROOT):
        if filename in files:
            return os.path.join(root, filename)
    raise FileNotFoundError(f"non trovo {filename} sotto {MODELS_ROOT}")


# ---------------------------------------------------------------- permutazione

def split_indexed(patches, pattern):
    """{indice: {suffisso: valore}} per cio' che e' indicizzato, resto a parte."""
    rx = re.compile(pattern)
    grouped, rest = defaultdict(dict), {}
    for k, v in patches.items():
        m = rx.match(k)
        if m:
            grouped[int(m.group(1))][m.group(2)] = v
        else:
            rest[k] = v
    return dict(grouped), rest


def derangement(indices, profiles, rng, max_tries=4000):
    def key(i):
        return tuple(round(profiles[i][s], 9) for s in sorted(profiles[i]))
    keys = {i: key(i) for i in indices}
    for _ in range(max_tries):
        shuffled = list(indices)
        rng.shuffle(shuffled)
        if all(keys[a] != keys[b] for a, b in zip(indices, shuffled)):
            return dict(zip(indices, shuffled))
    raise RuntimeError("nessun derangement trovato: troppi profili identici")


def flatten(grouped, perm, prefix):
    """Il solo sottoinsieme permutato, gia' ricomposto in chiavi piene."""
    out = {}
    for dst, src in perm.items():
        for suf, val in grouped[src].items():
            out[f"{prefix}{dst}.{suf}"] = val
    return out


def flatten_identity(grouped, prefix):
    out = {}
    for idx, prof in grouped.items():
        for suf, val in prof.items():
            out[f"{prefix}{idx}.{suf}"] = val
    return out


# ------------------------------------------------------------------ norme reali

def norm_table(path, patch_keys):
    wanted = set(patch_keys)
    norms = {}
    with safetensors.safe_open(path, framework="pt", device="cpu") as f:
        for raw in f.keys():
            ck = Krea2TensorParser.clean_key(raw)
            if ck in wanted and ck not in norms:
                t = f.get_tensor(raw).to(torch.float32)
                norms[ck] = float(torch.linalg.vector_norm(t).item())
    missing = wanted - set(norms)
    if missing:
        raise KeyError(f"{len(missing)} chiavi del preset non trovate nei pesi, "
                       f"es: {sorted(missing)[:3]}")
    return norms


def dnorm(patches, norms):
    """||dW||_F dello spostamento scalare su un insieme di tensori."""
    return math.sqrt(sum((v * norms[k]) ** 2 for k, v in patches.items()))


# ------------------------------------------------------------------------ main

def calibrate(patches, pattern, prefix, norms, label, rng):
    """Permuta il sottoinsieme indicizzato, riscala SOLO quello, lascia il resto
    bit per bit com'era. Restituisce (nuovo dizionario completo, alpha, perm)."""
    grouped, rest = split_indexed(patches, pattern)
    sizes = {len(v) for v in grouped.values()}
    if len(sizes) != 1:
        raise RuntimeError(f"{label}: gruppi di taglia disomogenea {sizes}")
    idx = sorted(grouped)
    perm = derangement(idx, grouped, rng)

    sub_base = flatten_identity(grouped, prefix)
    sub_perm = flatten(grouped, perm, prefix)

    d_sub_base = dnorm(sub_base, norms)
    d_sub_perm = dnorm(sub_perm, norms)
    d_rest = dnorm(rest, norms)
    alpha = d_sub_base / d_sub_perm

    sub_perm = {k: v * alpha for k, v in sub_perm.items()}
    out = dict(rest)
    out.update(sub_perm)

    print(f"[{label}] {len(idx)} gruppi x {sizes.pop()} tensori permutati, "
          f"{len(rest)} tensori lasciati intatti")
    print(f"[{label}] ||dW|| sottoinsieme  base {d_sub_base:12.8f}  "
          f"permutato {d_sub_perm:12.8f}  -> alpha {alpha:.8f}")
    print(f"[{label}] ||dW|| resto intatto {d_rest:12.8f}")
    print(f"[{label}] ||dW|| totale        base {math.hypot(d_sub_base, d_rest):12.8f}  "
          f"uscita {math.hypot(dnorm(sub_perm, norms), d_rest):12.8f}")

    res_sub = dnorm(sub_perm, norms) / d_sub_base - 1.0
    res_tot = math.hypot(dnorm(sub_perm, norms), d_rest) / math.hypot(d_sub_base, d_rest) - 1.0
    print(f"[{label}] residuo sottoinsieme {res_sub:+.3e}   totale {res_tot:+.3e}")
    if max(abs(res_sub), abs(res_tot)) > 1e-9:
        raise RuntimeError(f"{label}: riscalatura non convergente")

    for k, v in rest.items():
        if out[k] != v:
            raise RuntimeError(f"{label}: {k} alterato, non doveva esserlo")

    return out, alpha, perm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="sovrascrive i due preset BLOCKSHUFFLE se esistono gia'")
    args = ap.parse_args()

    with open(os.path.join(PRESET_DIR, BASE_NAME + ".json"), "r", encoding="utf-8") as f:
        base = json.load(f)
    mp, cp = base["model_patches"], base["clip_patches"]

    print("[derive] norme di Frobenius dai pesi reali...")
    m_norms = norm_table(find_model(MODEL_FILE), mp.keys())
    c_norms = norm_table(find_model(CLIP_FILE), cp.keys())
    print(f"[derive] norme lette: modello {len(m_norms)}/{len(mp)}  "
          f"clip {len(c_norms)}/{len(cp)}")

    rng = random.Random(PERM_SEED)
    mp_new, a_m, m_perm = calibrate(mp, r"blocks\.(\d+)\.(.*)", "blocks.",
                                    m_norms, "modello", rng)
    cp_new, a_c, c_perm = calibrate(cp, r"layers\.(\d+)\.(.*)", "layers.",
                                    c_norms, "clip   ", rng)

    print(f"\n[derive] permutazione modello (seme {PERM_SEED}):")
    print("   " + "  ".join(f"B{d:02d}<-B{s:02d}" for d, s in sorted(m_perm.items())))
    print("[derive] permutazione clip:")
    print("   " + "  ".join(f"L{d:02d}<-L{s:02d}" for d, s in sorted(c_perm.items())))

    assert set(mp_new) == set(mp) and set(cp_new) == set(cp), "chiavi cambiate"

    out = json.loads(json.dumps(base))
    out["name"] = OUT_NAME
    out["model_patches"] = mp_new
    out["clip_patches"] = cp_new
    out["notes"] = (
        "Controllo di assegnazione. Stesso multiinsieme di profili del Base, "
        "stessa coerenza interna di blocco, stesse 4 ricette di rotazione su "
        f"Block_3; cambia solo QUALE blocco riceve QUALE profilo (derangement, "
        f"seme {PERM_SEED}). La permutazione riguarda i 364 tensori dei 28 "
        "blocchi del DiT e i 341 tensori dei 31 layer di testo del CLIP; i 66 "
        "tensori fuori blocco del modello e i 288 della torre visiva restano bit "
        f"per bit quelli del Base. Riscalatura alpha_model={a_m:.8f}, "
        f"alpha_clip={a_c:.8f} applicata SOLO al sottoinsieme permutato, perche' "
        "blocchi diversi hanno norme diverse e la permutazione da sola non "
        "conserva lo spostamento: cosi' combaciano insieme il sottoinsieme, il "
        "resto e il totale. Serve a separare 'conta la coerenza di blocco' da "
        "'conta l'assegnazione specifica'."
    )

    neg = json.loads(json.dumps(out))
    neg["name"] = NEG_NAME
    neg["model_patches"] = {k: -v for k, v in mp_new.items()}
    neg["clip_patches"] = {k: -v for k, v in cp_new.items()}
    for r in neg.get("rotation_recipes", []):
        r["rotation_angle"] = -r["rotation_angle"]
    neg["notes"] = "NEG di " + OUT_NAME + ". " + out["notes"]

    for name, obj in ((OUT_NAME, out), (NEG_NAME, neg)):
        p = os.path.join(PRESET_DIR, name + ".json")
        if os.path.exists(p) and not args.force:
            raise FileExistsError(f"{p} esiste gia'. Rilancia con --force solo se "
                                  f"stai rigenerando questi due, mai altri preset.")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1)
        print(f"[derive] scritto {p}")

    print("\n[derive] verifica finale")
    print(f"   model_patches {len(out['model_patches'])}  (atteso {len(mp)})")
    print(f"   clip_patches  {len(out['clip_patches'])}   (atteso {len(cp)})")
    print(f"   rotation_recipes identiche al Base: "
          f"{out['rotation_recipes'] == base['rotation_recipes']}")
    print(f"   granulari {len(out['model_granular_patches'])}/"
          f"{len(out['clip_granular_patches'])}  (atteso 0/0)")
    vis = [v for k, v in out["clip_patches"].items() if k.startswith("visual.")]
    print(f"   torre visiva intatta: {len(vis)} tensori, "
          f"min {min(vis):+.6f} max {max(vis):+.6f}  (atteso -0.025000 ovunque)")


if __name__ == "__main__":
    main()
