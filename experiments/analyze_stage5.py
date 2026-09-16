"""
experiments/analyze_stage5.py  --  tre condizioni a pari spostamento, sette prompt

LA DOMANDA, nella forma a cui siamo arrivati.

Lo Stage 4 confrontava due cose: il preset e RANDSIGN, che capovolge il segno di
ogni singolo tensore. Ha trovato il preset piu' coerente, ma poi abbiamo
misurato il preset e visto com'e' fatto davvero: costante a blocchi (dev
0.000000 su meta' dei blocchi del DiT e su tutti i layer di testo del CLIP;
B05..B09 portano addirittura lo stesso profilo interno replicato su cinque
blocchi). Quindi RANDSIGN non randomizzava un'assegnazione: distruggeva la
coerenza di blocco. Il confronto rispondeva a una domanda piu' debole di quella
che credevamo.

BLOCKSHUFFLE e' il controllo che mancava: stesso multiinsieme di profili, stessa
coerenza dentro ogni blocco, stesso spostamento di Frobenius, e cambia solo
QUALE blocco riceve QUALE profilo. Le tre condizioni si ordinano cosi':

    preset        coerente, assegnato come dice il preset
    blockshuffle  coerente, assegnato a caso
    randsign      incoerente

e le due differenze rispondono a due domande diverse:

    preset - randsign       conta la coerenza di blocco?
    preset - blockshuffle   conta QUESTA assegnazione, o basta essere coerenti?

Se la prima e' grande e la seconda e' zero, il risultato e' generale e
replicabile da chiunque, e non dipende da anni di selezione a mano. Se anche la
seconda e' grande, l'assegnazione porta informazione.

COME SI MISURA.
Per ogni coppia +/- a parita' di prompt e di seed si scompone lo spostamento
nell'embedding CLIP:
    S = (d+ + d-)/2   la parte che non dipende dal segno, cioe' dal contenuto
    A = (d+ - d-)/2   la parte direzionale, l'unica che puo' essere uno "stile"
e si misura quanto le A di prompt DIVERSI puntano nella stessa direzione
(coseno medio a coppie delle A mediate sui seed). Sette prompt: 21 coppie.

DUE PRECAUZIONI, entrambe imparate sbagliando.

  * COLORE. Block_6 aveva vinto tutto il benchmark facendo solo una dominante
    globale. Ogni misura gira due volte, grezza e con media/deviazione LAB
    riallineate alla baseline: la differenza fra le due dice quanta parte
    dell'effetto era soltanto colore.

  * IL NULL NON E' ZERO. Due misure diverse: il coseno fra baseline a seed
    diversi (che cosa fa il rumore) e una permutazione di segno sulle A per
    prompt (che cosa fa una coerenza per caso). Le differenze fra condizioni
    hanno un bootstrap APPAIATO sui prompt, perche' il prompt e' l'unita' su cui
    si generalizza, non il seed.

Gira uguale su 7 prompt (stage5 --light) e su 10 (stage5 completo): legge quello
che trova e stampa la copertura prima di ogni altra cosa.
"""

import os
import sys
import csv
import json
import glob
import collections
import itertools
import numpy as np
import cv2
import torch
import open_clip
from skimage import color

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stage5_config import ATTRS, SHARED_VOCAB

COMFY_OUT = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"
DIRS = [os.path.join(COMFY_OUT, d, "renders") for d in
        ("benchmark_stage5", "benchmark_stage4_preset", "benchmark_stage2_family")]
ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"

CSV_IN = [os.path.join(ROOT, "stage4_images.csv"),
          os.path.join(ROOT, "stage5_images.csv")]
CSV_BASE = [os.path.join(ROOT, "stage2_images.csv"),
            os.path.join(ROOT, "stage5_images.csv")]
EMB_NPZ = os.path.join(ROOT, "_stage5_emb.npz")
OUT_SA = os.path.join(ROOT, "stage5_sa.csv")
OUT_ATTR = os.path.join(ROOT, "stage5_attributes.csv")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
EXPECTED = (1280, 1024)
N_BOOT = 20000
N_PERM = 20000
RNG = np.random.default_rng(20260914)

# nome della condizione a partire dal preset: l'unica chiave affidabile, perche'
# lo Stage 4 e lo Stage 5 nominano i file in modo diverso
COND = {
    "Arthemy_Bench_Base.json": "preset_pos",
    "Arthemy_Bench_NEG.json": "preset_neg",
    "Arthemy_Bench_HALF.json": "preset_half",
    "Arthemy_Bench_RANDSIGN.json": "rand_pos",
    "Arthemy_Bench_RANDSIGN_NEG.json": "rand_neg",
    "Arthemy_Bench_BLOCKSHUFFLE.json": "blockshuf_pos",
    "Arthemy_Bench_BLOCKSHUFFLE_NEG.json": "blockshuf_neg",
}
PAIRS = [("preset", "preset_pos", "preset_neg"),
         ("blockshuffle", "blockshuf_pos", "blockshuf_neg"),
         ("randsign", "rand_pos", "rand_neg")]
CONFRONTI = [("preset", "randsign", "conta la coerenza di blocco?"),
             ("preset", "blockshuffle", "conta QUESTA assegnazione?"),
             ("blockshuffle", "randsign", "coerente a caso batte incoerente?")]


# ----------------------------------------------------------------- immagini

def build_index():
    """basename -> percorso. Un basename duplicato fra le cartelle e' un errore
    che va visto subito, non risolto in silenzio scegliendo il primo."""
    idx = {}
    for d in DIRS:
        if not os.path.isdir(d):
            print(f"  [!] cartella assente, la salto: {d}")
            continue
        for p in glob.glob(os.path.join(d, "*.png")):
            b = os.path.basename(p)
            if b in idx:
                raise RuntimeError(f"basename duplicato fra due run: {b}")
            idx[b] = p
    return idx


def load(idx, rel):
    p = idx.get(os.path.basename(rel))
    if p is None:
        raise FileNotFoundError(rel)
    img = cv2.imread(p, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(p)
    if img.shape[:2] != EXPECTED:
        raise ValueError(f"{p} e' {img.shape[:2]}, atteso {EXPECTED}")
    return img[:, :, ::-1].astype(np.float32) / 255.0


def color_match(src, ref):
    a, b = color.rgb2lab(src), color.rgb2lab(ref)
    out = (a - a.reshape(-1, 3).mean(0)) / (a.reshape(-1, 3).std(0) + 1e-6)
    out = out * b.reshape(-1, 3).std(0) + b.reshape(-1, 3).mean(0)
    out[..., 0] = np.clip(out[..., 0], 0, 100)
    out[..., 1:] = np.clip(out[..., 1:], -128, 127)
    return np.clip(color.lab2rgb(out), 0, 1).astype(np.float32)


class Clip:
    def __init__(self):
        self.m, _, _ = open_clip.create_model_and_transforms(
            "ViT-L-14", pretrained="openai", device=DEVICE)
        self.m.eval()
        self.tok = open_clip.get_tokenizer("ViT-L-14")
        self.mean = torch.tensor([0.48145466, 0.4578275, 0.40821073]).view(1, 3, 1, 1).to(DEVICE)
        self.std = torch.tensor([0.26862954, 0.26130258, 0.27577711]).view(1, 3, 1, 1).to(DEVICE)
        self._t = {}

    def txt(self, s):
        if s not in self._t:
            with torch.no_grad():
                e = self.m.encode_text(self.tok([s]).to(DEVICE))
            self._t[s] = torch.nn.functional.normalize(e, dim=-1).squeeze(0).cpu().numpy()
        return self._t[s]

    def img(self, rgb01):
        # niente CenterCrop: taglierebbe via meta' di un'inquadratura 1024x1280
        t = torch.from_numpy(np.ascontiguousarray(rgb01)).permute(2, 0, 1)[None]
        t = torch.nn.functional.interpolate(t, size=(224, 224), mode="bicubic",
                                            align_corners=False).to(DEVICE)
        with torch.no_grad():
            e = self.m.encode_image((t - self.mean) / self.std)
        return torch.nn.functional.normalize(e, dim=-1).squeeze(0).cpu().numpy()


# ------------------------------------------------------------------ statistica

def pair_cos(vs):
    n = np.stack(vs)
    n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
    return np.array([float(n[i] @ n[j]) for i, j in itertools.combinations(range(len(n)), 2)])


def gram(A_by_prompt, prompts):
    """matrice dei coseni fra le direzioni A dei prompt, gia' normalizzate."""
    M = np.stack([A_by_prompt[p] for p in prompts])
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    return M @ M.T


def coherence_from_gram(G, take):
    """coseno medio a coppie sui prompt indicati da 'take' (indici, con
    ripetizioni ammesse dal bootstrap). Le coppie di un prompt CON SE STESSO
    valgono 1 per costruzione e gonfierebbero la coerenza in proporzione a
    quante volte il ricampionamento lo ha pescato: si escludono."""
    k = len(take)
    if k < 2:
        return np.nan
    sub = G[np.ix_(take, take)]
    iu = np.triu_indices(k, 1)
    same = take[:, None] == take[None, :]
    vals = sub[iu][~same[iu]]
    return float(vals.mean()) if vals.size else np.nan


def main():
    idx = build_index()
    print(f"[analyze] {len(idx)} immagini indicizzate su {DEVICE}")

    rows = []
    for p in CSV_IN:
        if os.path.exists(p):
            rows += list(csv.DictReader(open(p, encoding="utf-8-sig")))
    rows = [r for r in rows if r.get("preset_file") in COND]
    print(f"[analyze] {len(rows)} righe trattate")

    bases = {}
    for p in CSV_BASE:
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            if r.get("operation") == "baseline":
                bases.setdefault((r["prompt_id"], r["seed"]), r["image_path"])
    for r in rows:
        bases.setdefault((r["prompt_id"], r["seed"]), r["baseline_path"])

    byc = collections.defaultdict(dict)
    for r in rows:
        byc[COND[r["preset_file"]]][(r["prompt_id"], r["seed"])] = r["image_path"]

    prompts = sorted({r["prompt_id"] for r in rows})
    conds = [c for _, a, b in PAIRS for c in (a, b) if c in byc]

    # --- copertura, prima di tutto -------------------------------------------
    print("\n" + "=" * 78)
    print("  COPERTURA  --  seed per (prompt, condizione)")
    print("=" * 78)
    print(f"  {'prompt':8s}" + "".join(f"{c.replace('_',''):>15s}" for c in conds) + f"{'base':>7s}")
    full = []
    for p in prompts:
        line = f"  {p:8s}"
        ok = True
        for c in conds:
            n = sum(1 for (pp, _s) in byc[c] if pp == p)
            line += f"{n:>15d}"
            if n < 5:
                ok = False
        nb = sum(1 for (pp, _s) in bases if pp == p)
        print(line + f"{nb:>7d}")
        if ok:
            full.append(p)
    print(f"\n  prompt completi su tutte e {len(conds)} le condizioni: "
          f"{len(full)}  ({', '.join(full)})")
    if len(full) < 3:
        raise RuntimeError("meno di 3 prompt completi: non c'e' niente da confrontare")
    prompts = full

    # --- embedding ------------------------------------------------------------
    need = sorted({v for d in byc.values() for v in d.values()} |
                  {v for v in bases.values()})
    key = lambda rel: os.path.basename(rel)
    raw, cn = {}, {}
    if os.path.exists(EMB_NPZ):
        z = np.load(EMB_NPZ, allow_pickle=True)
        raw = {k[4:]: z[k] for k in z.files if k.startswith("raw|")}
        cn = {k[3:]: z[k] for k in z.files if k.startswith("cn|")}
        print(f"\n[analyze] cache: {len(raw)} embedding")
    todo = [r for r in need if key(r) not in raw or key(r) not in cn]
    if todo:
        print(f"[analyze] da calcolare: {len(todo)}")
        clip = Clip()
        bcache = {}

        def base_img(p, s):
            if (p, s) not in bcache:
                bcache[(p, s)] = load(idx, bases[(p, s)])
            return bcache[(p, s)]

        owner = {}
        for c, d in byc.items():
            for (p, s), rel in d.items():
                owner[key(rel)] = (p, s)
        for (p, s), rel in bases.items():
            owner[key(rel)] = (p, s)
        for n, rel in enumerate(todo, 1):
            p, s = owner[key(rel)]
            img = load(idx, rel)
            raw[key(rel)] = clip.img(img)
            cn[key(rel)] = clip.img(color_match(img, base_img(p, s)))
            if n % 25 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)}")
        np.savez_compressed(EMB_NPZ,
                            **{"raw|" + k: v for k, v in raw.items()},
                            **{"cn|" + k: v for k, v in cn.items()})
        print(f"[analyze] cache scritta -> {EMB_NPZ}")
    else:
        clip = None

    seeds_all = sorted({s for _, s in bases}, key=int)
    out_rows = []

    for space, E in (("RAW", raw), ("COLOUR-NORMALISED", cn)):
        print("\n" + "=" * 78)
        print(f"  {space}")
        print("=" * 78)

        def emb(rel):
            return E[key(rel)]

        # null 1: che cosa fa il solo cambio di seed
        null_seed = []
        for s1, s2 in itertools.combinations(seeds_all, 2):
            if all((p, s1) in bases and (p, s2) in bases for p in prompts):
                null_seed.append(np.mean(pair_cos(
                    [emb(bases[(p, s1)]) - emb(bases[(p, s2)]) for p in prompts])))
        null_seed = np.array(null_seed)
        print(f"\n  null del cambio di seed: mediana {np.median(null_seed):+.3f}  "
              f"p95 {np.percentile(null_seed, 95):+.3f}   n={len(null_seed)}")

        # S / A
        print(f"\n  {'pair':14s}{'|S|':>8s}{'|A|':>8s}{'|A|/|S|':>9s}"
              f"{'cos(+,-)':>10s}{'A coherence':>13s}{'null p95':>10s}{'p':>9s}")
        A_by = {}
        grams = {}
        stats = {}
        for name, cp, cn_ in PAIRS:
            if cp not in byc or cn_ not in byc:
                continue
            keys = [k for k in byc[cp] if k in byc[cn_] and k[0] in prompts]
            if not keys:
                continue
            dp = np.stack([emb(byc[cp][k]) - emb(bases[k]) for k in keys])
            dn = np.stack([emb(byc[cn_][k]) - emb(bases[k]) for k in keys])
            S, A = (dp + dn) / 2, (dp - dn) / 2
            cospm = float(np.mean(np.sum(dp * dn, 1) /
                                  (np.linalg.norm(dp, axis=1) * np.linalg.norm(dn, axis=1) + 1e-12)))
            g = collections.defaultdict(list)
            for v, (p, _s) in zip(A, keys):
                g[p].append(v)
            Ap = {p: np.mean(g[p], axis=0) for p in g}
            A_by[name] = Ap
            G = gram(Ap, prompts)
            grams[name] = G
            iu = np.triu_indices(len(prompts), 1)
            coh = float(G[iu].mean())

            # null 2: permutazione di segno sulle direzioni per prompt
            sg = RNG.choice([-1.0, 1.0], size=(N_PERM, len(prompts)))
            nullperm = np.array([float(np.mean((np.outer(v, v) * G)[iu])) for v in sg])
            p95 = float(np.percentile(nullperm, 95))
            pval = float((np.sum(nullperm >= coh) + 1) / (N_PERM + 1))

            ns = float(np.mean(np.linalg.norm(S, axis=1)))
            na = float(np.mean(np.linalg.norm(A, axis=1)))
            print(f"  {name:14s}{ns:>8.3f}{na:>8.3f}{na/ns:>9.3f}{cospm:>+10.3f}"
                  f"{coh:>+12.3f}{p95:>+10.3f}{pval:>9.4f}")
            stats[name] = dict(S=ns, A=na, ratio=na / ns, cos_pm=cospm,
                               coh=coh, null_p95=p95, p=pval, n_cells=len(keys))
            out_rows.append(dict(space=space, pair=name, n_prompts=len(prompts),
                                 **{k: round(v, 6) if isinstance(v, float) else v
                                    for k, v in stats[name].items()}))

        # differenze, bootstrap APPAIATO sui prompt
        print(f"\n  differenze di coerenza A   (bootstrap appaiato sui {len(prompts)} prompt, "
              f"{N_BOOT} campioni)")
        for a, b, domanda in CONFRONTI:
            if a not in A_by or b not in A_by:
                continue
            obs = stats[a]["coh"] - stats[b]["coh"]
            n = len(prompts)
            draws = np.empty(N_BOOT)
            for i in range(N_BOOT):
                take = RNG.integers(0, n, n)
                draws[i] = (coherence_from_gram(grams[a], take) -
                            coherence_from_gram(grams[b], take))
            draws = draws[~np.isnan(draws)]
            lo, hi = np.percentile(draws, [2.5, 97.5])
            pz = float(np.mean(draws <= 0))
            verdetto = "SI'" if lo > 0 else ("no" if hi < 0 else "non deciso")
            print(f"    {a:12s} - {b:12s} {obs:>+7.3f}   IC95 [{lo:+.3f}, {hi:+.3f}]"
                  f"   P(<=0) {pz:.4f}   {verdetto:11s}  {domanda}")
            out_rows.append(dict(space=space, pair=f"{a}-{b}", n_prompts=len(prompts),
                                 coh=round(obs, 6), ic_lo=round(float(lo), 6),
                                 ic_hi=round(float(hi), 6), p=round(pz, 6)))

    # --- che cosa e' cambiato, non quanto ------------------------------------
    print("\n" + "=" * 78)
    print("  ADERENZA PER ATTRIBUTO   (colore normalizzato)")
    print("  z contro la deviazione fra baseline a seed diversi")
    print("=" * 78)
    shared = [s.strip() for s in SHARED_VOCAB.split(",")]
    attr_rows = []
    if clip is None:
        clip = Clip()
    for cname in conds:
        d = byc[cname]
        own_z, sh_z = [], []
        for p in prompts:
            for a in ATTRS.get(p, []) + shared:
                e = clip.txt(a)
                bv = [float(cn[key(bases[(p, s)])] @ e) for s in seeds_all if (p, s) in bases]
                sd = float(np.std(bv, ddof=1)) if len(bv) > 1 else 1.0
                dv = [float(cn[key(rel)] @ e) - float(cn[key(bases[(p, s)])] @ e)
                      for (pp, s), rel in d.items() if pp == p]
                if not dv:
                    continue
                z = float(np.mean(dv) / max(sd, 1e-6))
                (sh_z if a in shared else own_z).append(z)
                attr_rows.append(dict(condition=cname, prompt=p, attribute=a,
                                      type="shared" if a in shared else "character",
                                      z=round(z, 4)))
        if own_z:
            print(f"  {cname:16s} |z| personaggio {np.mean(np.abs(own_z)):5.2f}   "
                  f"vocabolario condiviso {np.mean(np.abs(sh_z)):5.2f}   "
                  f"z medio con segno {np.mean(own_z):+5.2f}")

    with open(OUT_SA, "w", newline="", encoding="utf-8") as f:
        ks = sorted({k for r in out_rows for k in r})
        w = csv.DictWriter(f, fieldnames=ks); w.writeheader(); w.writerows(out_rows)
    with open(OUT_ATTR, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["condition", "prompt", "attribute", "type", "z"])
        w.writeheader(); w.writerows(attr_rows)
    print(f"\n-> {OUT_SA}\n-> {OUT_ATTR}\n-> {EMB_NPZ}")


if __name__ == "__main__":
    main()
