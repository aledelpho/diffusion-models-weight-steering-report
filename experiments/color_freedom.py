# -*- coding: utf-8 -*-
"""
experiments/color_freedom.py -- I preset scelgono colori diversi, quando sono liberi?

LA DOMANDA, che nessuna misura fatta finora poteva vedere.
Lo Stage 7 toglie l'ancoraggio "monochromatic {hue}" e lascia solo "colored": il
modello sceglie la palette. Se interventi diversi sui pesi portassero a
colorazioni diverse, si vedrebbe li'.

Ma ogni misura di colore costruita finora RIALLINEA la dominante alla baseline,
perche' dopo Block_6 sapevamo che una metrica di universalita' premia un filtro di
colore per costruzione. Quella scelta era giusta per la domanda di allora e rende
questa domanda invisibile: abbiamo misurato QUANTI colori, mai QUALI. Quindi il
risultato attuale non e' "nullo", e' "non misurato".

COSA MISURA QUESTO. Spostamento cromatico medio in LAB, SENZA normalizzare la
dominante: per ogni immagine la media di (a, b) sul soggetto, la differenza dalla
baseline dello STESSO seed, e poi due cose.

  1. AMPIEZZA contro il pavimento. Il null non e' zero: con la palette libera due
     baseline a seed diversi gia' scelgono colori diversi. Quello e' il metro.
  2. COERENZA fra prompt. Se il preset spingesse verso una sua palette, gli
     spostamenti di prompt diversi punterebbero nella stessa direzione del piano
     (a, b). Coseno medio a coppie, con null a permutazione di segno.

Solo sui pixel del soggetto: lo sfondo e' bianco per costruzione in tutti i
prompt, e includerlo diluirebbe qualunque effetto verso zero.
"""
import os, csv, glob, itertools, collections
import numpy as np, cv2
# LAB via OpenCV: skimage non c'e' in questo ambiente, e cv2 su float32 in [0,1]
# restituisce L in [0,100] e a,b in [-127,127], che e' la stessa scala.

# Percorsi: lo script gira sia su Windows sia dentro la VM Linux del ponte, dove le
# stesse cartelle sono montate sotto $HOME/mnt. Si prova la forma Windows e si
# ripiega su quella montata, invece di avere due copie dello script.
def _first(*cand):
    for c in cand:
        if os.path.isdir(c):
            return c
    return cand[0]

_H = os.path.expanduser("~")
ROOT = _first(r"c:\Users\aless\Desktop\comfyui-pilot",
              os.path.join(_H, "mnt", "comfyui-pilot"))
OUT = os.path.join(ROOT, "color_freedom.csv")
# Le render stanno sotto Data\Images\Text2Img, non sotto Packages\ComfyUI\output.
COMFY = _first(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img",
               os.path.join(_H, "mnt", "StabilityMatrix-win-x64", "Data", "Images", "Text2Img"),
               r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
DIRS = [os.path.join(COMFY, d, "renders") for d in
        ("benchmark_stage7", "benchmark_stage6", "benchmark_stage5",
         "benchmark_stage4_preset", "benchmark_stage2_family")]
COND = {"Arthemy_Bench_Base.json": "preset+", "Arthemy_Bench_NEG.json": "preset-",
        "Arthemy_Bench_BLOCKSHUFFLE.json": "block+", "Arthemy_Bench_BLOCKSHUFFLE_NEG.json": "block-",
        "Arthemy_Bench_RANDSIGN.json": "rand+", "Arthemy_Bench_RANDSIGN_NEG.json": "rand-"}
RNG = np.random.default_rng(20260915)
b = os.path.basename


def chroma(path):
    """media di (a, b) sui soli pixel del soggetto."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        return None
    lab = cv2.cvtColor(img.astype(np.float32) / 255.0, cv2.COLOR_BGR2LAB)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    soggetto = ~((L > 88) & (np.hypot(A, B) < 8))      # esclude il bianco di sfondo
    if soggetto.mean() < 0.05:
        soggetto = np.ones_like(soggetto, bool)
    return np.array([A[soggetto].mean(), B[soggetto].mean()])


def main():
    idx = {}
    for d in DIRS:
        if os.path.isdir(d):
            for p in glob.glob(os.path.join(d, "*.png")):
                idx.setdefault(b(p), p)
    rows = []
    for f in glob.glob(os.path.join(ROOT, "stage*_images.csv")):
        rows += list(csv.DictReader(open(f, encoding="utf-8-sig")))
    base, cond = {}, collections.defaultdict(dict)
    for r in rows:
        pid, s = r.get("prompt_id", ""), r.get("seed", "")
        if r.get("operation") == "baseline":
            base.setdefault((pid, s), b(r["image_path"]))
        g = COND.get(r.get("preset_file", ""))
        if g:
            cond[g][(pid, s)] = b(r["image_path"])
            base.setdefault((pid, s), b(r["baseline_path"]))

    fam = {"colore LIBERO (solo 'colored')": lambda p: p.startswith("S7_"),
           "colore SPECIFICATO per elemento": lambda p: not p.startswith("S7_")}
    cache = {}
    def cr(n):
        if n not in cache:
            cache[n] = chroma(idx[n]) if n in idx else None
        return cache[n]

    out = []
    for lab_f, sel in fam.items():
        prompts = sorted({p for g in cond for p, _ in cond[g] if sel(p)})
        prompts = [p for p in prompts
                   if all(sum(1 for pp, _s in cond[g] if pp == p) >= 5 for g in COND.values())]
        if len(prompts) < 3:
            continue
        seeds = sorted({s for p, s in cond["preset+"] if p in prompts}, key=int)

        # pavimento: quanto cambia la palette fra due baseline a seed diversi
        floor = []
        for p in prompts:
            v = [cr(base[(p, s)]) for s in seeds if (p, s) in base and cr(base[(p, s)]) is not None]
            floor += [np.linalg.norm(x - y) for x, y in itertools.combinations(v, 2)]
        floor = float(np.median(floor)) if floor else float("nan")

        print("\n" + "=" * 86)
        print(f"  {lab_f}   {len(prompts)} prompt: {', '.join(prompts)}")
        print(f"  pavimento (mediana dello spostamento di palette fra due seed) = {floor:.2f} unita' LAB")
        print("=" * 86)
        print(f"  {'condition':12s}{'displacement':>13s}{'/ floor':>13s}"
              f"{'cross-prompt coherence':>24s}{'null p95':>10s}{'p':>8s}")
        for g in ("preset+", "preset-", "block+", "block-", "rand+", "rand-"):
            D = {}
            for p in prompts:
                v = [cr(cond[g][(p, s)]) - cr(base[(p, s)])
                     for s in seeds
                     if (p, s) in cond[g] and (p, s) in base
                     and cr(cond[g][(p, s)]) is not None and cr(base[(p, s)]) is not None]
                if v:
                    D[p] = np.mean(v, 0)
            if len(D) < 3:
                continue
            M = np.stack([D[p] for p in sorted(D)])
            amp = float(np.mean(np.linalg.norm(M, axis=1)))
            N = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
            G = N @ N.T
            iu = np.triu_indices(len(N), 1)
            coh = float(G[iu].mean())
            sg = RNG.choice([-1.0, 1.0], size=(20000, len(N)))
            nul = np.array([float(np.mean((np.outer(v, v) * G)[iu])) for v in sg])
            pv = float((np.sum(nul >= coh) + 1) / 20001)
            print(f"  {g:12s}{amp:>13.2f}{amp/floor:>12.2f}x{coh:>+21.3f}"
                  f"{np.percentile(nul,95):>+10.3f}{pv:>8.4f}")
            out.append(dict(family=lab_f, condition=g, n_prompts=len(D),
                            displacement=round(amp, 3), floor=round(floor, 3),
                            ratio=round(amp / floor, 3), coherence=round(coh, 4),
                            null_p95=round(float(np.percentile(nul, 95)), 4), p=round(pv, 5)))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(f"\n-> {OUT}")
    print("\n  Come si legge: 'spostamento / pavimento' sotto 1 significa che l'intervento")
    print("  cambia la palette MENO di quanto la cambi un seed diverso. La coerenza dice se")
    print("  i pochi spostamenti che ci sono puntano tutti nella stessa direzione del piano (a,b).")


if __name__ == "__main__":
    main()
