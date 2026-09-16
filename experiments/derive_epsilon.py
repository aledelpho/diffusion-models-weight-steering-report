"""
experiments/derive_epsilon.py  --  la scala di ampiezza, per misurare l'esponente

PERCHE'. Lo Stage 5 misura cos(+,-) = +0.27 sul preset: il 64% dell'energia della
risposta e' cieca al segno. La domanda legittima e' se quella parte pari sia il
termine del second'ordine dello sviluppo -- cioe' una conseguenza inevitabile
della non linearita' della catena -- oppure un danno generico che non ha niente
a che fare con la direzione.

Le due ipotesi predicono cose diverse e lontane. Con

    Delta(eps) = eps * J v  +  eps^2 * Q(v,v) + O(eps^3)
                   dispari       pari

si ha ||A|| ~ eps e ||S|| ~ eps^2, quindi ||A||/||S|| ~ 1/eps: dimezzare
l'ampiezza raddoppia il rapporto e porta cos(+,-) da +0.27 a circa -0.39. Se
invece S e' danno generico proporzionale a ||dW||, il rapporto resta 0.75 e
cos(+,-) resta +0.27.

Tre punti (eps = 0.25, 0.5, 1) danno la pendenza in log-log di ||A|| e di ||S||
separatamente: si MISURA l'esponente invece di sceglierlo.

REGOLE, le stesse gia' usate per HALF e per i NEG, nessuna nuova:
  - scalare eps: ogni valore x eps; angolo di rotazione x eps, e measured_delta
    ricalcolato con sqrt(2-2cos t) = 2 sin(t/2), cioe' moltiplicato per
    sin(eps*t/2)/sin(t/2). Verificato contro l'HALF gia' esistente: 0.029459 ->
    0.014744, e nel file c'e' 0.0147.
  - NEG: ogni valore x -1, rotation_angle compreso, measured_delta invariato.

Scrive HALF_NEG, QUARTER, QUARTER_NEG. HALF esiste gia' e non si tocca.
"""

import os
import json
import math
import argparse

PRESET_DIR = (r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI"
              r"\custom_nodes\Arthemy_Krea2_Tuner\presets")
BASE = "Arthemy_Bench_Base"


def load(name):
    with open(os.path.join(PRESET_DIR, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def scaled(base, eps, name, note):
    out = json.loads(json.dumps(base))
    out["name"] = name
    out["model_patches"] = {k: v * eps for k, v in base["model_patches"].items()}
    out["clip_patches"] = {k: v * eps for k, v in base["clip_patches"].items()}
    for r in out.get("rotation_recipes", []):
        t = math.radians(r["rotation_angle"])
        r["rotation_angle"] = r["rotation_angle"] * eps
        if r.get("measured_delta") and abs(math.sin(t / 2)) > 1e-12:
            r["measured_delta"] = r["measured_delta"] * math.sin(eps * t / 2) / math.sin(t / 2)
    out["notes"] = note
    return out


def negated(src, name):
    out = json.loads(json.dumps(src))
    out["name"] = name
    out["model_patches"] = {k: -v for k, v in src["model_patches"].items()}
    out["clip_patches"] = {k: -v for k, v in src["clip_patches"].items()}
    for r in out.get("rotation_recipes", []):
        r["rotation_angle"] = -r["rotation_angle"]
    out["notes"] = "NEG di " + src["name"] + ". " + src.get("notes", "")
    return out


def write(obj, force):
    p = os.path.join(PRESET_DIR, obj["name"] + ".json")
    if os.path.exists(p) and not force:
        raise FileExistsError(f"{p} esiste gia'. --force solo su questi tre.")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
    print(f"[derive_eps] scritto {os.path.basename(p)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    base = load(BASE)

    # controllo della regola contro l'HALF che esiste gia'
    try:
        half = load("Arthemy_Bench_HALF")
        atteso = scaled(base, 0.5, "x", "x")
        da = [(a["measured_delta"], b["measured_delta"])
              for a, b in zip(half["rotation_recipes"], atteso["rotation_recipes"])]
        err = max(abs(a - b) for a, b in da)
        k = next(iter(half["model_patches"]))
        errv = abs(half["model_patches"][k] - base["model_patches"][k] * 0.5)
        print(f"[derive_eps] regola verificata contro HALF: scarto massimo su "
              f"measured_delta {err:.2e}, su un valore {errv:.2e}")
        if err > 1e-4 or errv > 1e-5:
            raise RuntimeError("la regola di scala non riproduce l'HALF esistente")
    except FileNotFoundError:
        print("[derive_eps] HALF assente, salto la verifica della regola")
        half = None

    note = ("Punto della scala di ampiezza. Serve a misurare l'esponente con cui "
            "crescono la parte pari e quella dispari della risposta: se S e' il "
            "termine del second'ordine, ||S|| ~ eps^2 e ||A|| ~ eps, quindi "
            "cos(+,-) deve scendere al calare di eps. Derivato dal Base per "
            "moltiplicazione, angoli di rotazione compresi.")

    objs = []
    if half is not None:
        objs.append(negated(half, "Arthemy_Bench_HALF_NEG"))
    q = scaled(base, 0.25, "Arthemy_Bench_QUARTER", note)
    objs += [q, negated(q, "Arthemy_Bench_QUARTER_NEG")]

    for o in objs:
        write(o, args.force)

    print("\n[derive_eps] verifica")
    for o in objs:
        mp, cp = o["model_patches"], o["clip_patches"]
        rot = [round(r["rotation_angle"], 4) for r in o.get("rotation_recipes", [])]
        print(f"   {o['name']:34s} model {len(mp)} clip {len(cp)}  "
              f"|v| max {max(abs(v) for v in mp.values()):.6f}  angoli {rot}")
    print("\n   atteso: 430 / 629 ovunque; |v| max del Base x eps; "
          "angoli +2.5 per QUARTER, -5.0 per HALF_NEG, -2.5 per QUARTER_NEG")


if __name__ == "__main__":
    main()
