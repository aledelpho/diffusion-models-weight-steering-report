"""
experiments/vlm_gate.py  --  calibrare il giudice PRIMA di usarlo

Un VLM-come-giudice e' uno strumento di misura, e in questo progetto nessuno
strumento e' entrato nel report senza essere prima messo davanti a un segnale
noto. Questo script non misura i preset: misura IL GIUDICE.

TRE PROVE, tutte con verita' di base gia' sul disco.

  1. DISCRIMINAZIONE GROSSA. Coppie di immagini la cui differenza di larghezza
     mediana del tratto e' GIA' MISURATA in pixel (dalle feature di
     analyze_texture). Si prendono le coppie piu' distanti. Se il giudice non
     vede un divario che il calibro misura, e' inutilizzabile e lo sappiamo
     senza disturbare nessun illustratore.

  2. SOGLIA. Coppie a differenza piccola ma non nulla. Dice DOVE si ferma la sua
     risoluzione: serve a sapere su quali confronti ci si puo' appoggiare.

  3. CONTROLLO NEGATIVO. Coppie di due BASELINE a seed diversi, stesso prompt,
     nessun preset. Qui la risposta giusta e' "non saprei". Se il giudice
     dichiara differenze sistematiche di tratto dove non c'e' nessun intervento,
     sta confabulando, e le sue risposte altrove non valgono niente per quanto
     siano numeri. E' il pavimento dei seed applicato allo strumento.

TRE SCELTE DI DISEGNO CHE NON SONO DETTAGLI.

  * SCELTA FORZATA, NON SCALE 1-5. La varianza fra immagini e' dominata dal
    soggetto: una megera rugosa ha piu' tratteggio di un'elfa liscia qualunque
    cosa ci sia sopra. Un voto assoluto misura il soggetto. Una scelta a coppie
    a parita' di prompt e di seed misura l'intervento, ed entra nella stessa
    struttura appaiata di tutto il resto del benchmark.

  * ENTRAMBI GLI ORDINI. I VLM hanno un bias di posizione forte. Ogni coppia si
    chiede A-B e B-A: il disaccordo fra i due ordini e' insieme la misura del
    bias e l'affidabilita' del singolo item.

  * RITAGLIO A RISOLUZIONE NATIVA. Ridimensionare a 512 px rifarebbe l'errore di
    CLIP: lo spessore del tratto sparisce nel ricampionamento. Si manda un
    ritaglio 768x768 preso dove l'inchiostro e' piu' denso, pixel originali.

Se il giudice passa, si scala. Se non passa, il fallimento e' esso stesso un
risultato da riportare: le metriche automatiche non colgono cio' che conta per
un occhio esperto.
"""

import os
import io
import sys
import csv
import json
import glob
import base64
import argparse
import collections
import urllib.request
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_texture import COND, PAIRS, CSV_IN, CSV_BASE, DIRS, TEX_NPZ, NAMES, b

ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
OUT = os.path.join(ROOT, "vlm_gate.csv")
CROP = 768

DOMANDA = {
    "tratto": "which image has THICKER, HEAVIER contour lines?",
    "tratteggio": "which image has DENSER hatching or cross-hatching?",
    "ombre": "which image has HARDER, more abrupt shadow edges (as opposed to soft gradients)?",
}

SCHEMA = (
    "You are comparing two crops from comic-style illustrations, shown at their "
    "original pixel resolution.\n\n"
    "Question: {q}\n\n"
    "Answer with JSON only, no prose, exactly this shape:\n"
    '{{"choice": "A" | "B" | "same", "confidence": 1-5, "evidence": "<=15 words"}}\n\n'
    'Use "same" when you genuinely cannot tell them apart on this specific '
    "property. Do not guess to avoid saying same. Judge only the property asked "
    "about; ignore the subject, pose, expression and colour."
)


def ink_crop(path, size=CROP):
    """Ritaglio dove l'inchiostro e' piu' denso: mandare sfondo bianco al giudice
    sarebbe chiedergli di giudicare il nulla."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ink = (g < 90).astype(np.float32)
    h, w = g.shape
    s = min(size, h, w)
    integ = cv2.integral(ink)
    best, by, bx = -1.0, (h - s) // 2, (w - s) // 2
    for y in range(0, h - s + 1, 64):
        for x in range(0, w - s + 1, 64):
            v = (integ[y + s, x + s] - integ[y, x + s] - integ[y + s, x] + integ[y, x])
            if v > best:
                best, by, bx = v, y, x
    return img[by:by + s, bx:bx + s]


def b64(img):
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise RuntimeError("encode fallito")
    return base64.b64encode(buf.tobytes()).decode("ascii")


def ask_ollama(url, model, prompt, imgs):
    body = json.dumps({"model": model, "prompt": prompt, "images": imgs,
                       "stream": False, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())["response"]


def ask_openai(url, model, prompt, imgs):
    content = [{"type": "text", "text": prompt}]
    for i in imgs:
        content.append({"type": "image_url",
                        "image_url": {"url": "data:image/png;base64," + i}})
    body = json.dumps({"model": model, "temperature": 0, "max_tokens": 200,
                       "messages": [{"role": "user", "content": content}]}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/v1/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer local"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())["choices"][0]["message"]["content"]


def parse(txt):
    s = txt.strip()
    i, j = s.find("{"), s.rfind("}")
    if i < 0 or j < 0:
        return None
    try:
        d = json.loads(s[i:j + 1])
    except Exception:
        return None
    c = str(d.get("choice", "")).strip().upper()
    if c not in ("A", "B", "SAME"):
        return None
    return dict(choice=c, confidence=d.get("confidence", 0),
                evidence=str(d.get("evidence", ""))[:80])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    ap.add_argument("--url", default="http://127.0.0.1:11434")
    ap.add_argument("--model", required=True, help="es. qwen2.5vl:7b, llava:13b")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--n-per-gruppo", type=int, default=15)
    args = ap.parse_args()
    ask = ask_ollama if args.backend == "ollama" else ask_openai

    idx = {}
    for d in DIRS:
        if os.path.isdir(d):
            for p in glob.glob(os.path.join(d, "*.png")):
                idx.setdefault(b(p), p)

    z = np.load(TEX_NPZ, allow_pickle=True)
    T = {k: z[k] for k in z.files if k != "__names__"}
    WID = NAMES.index("inchiostro_largh_mediana")
    larg = {k: float(v[WID]) for k, v in T.items()}

    rows = []
    for p in CSV_IN:
        if os.path.exists(p):
            rows += [r for r in csv.DictReader(open(p, encoding="utf-8-sig"))
                     if r.get("preset_file") in COND]
    bases = {}
    for p in CSV_BASE:
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8-sig")):
                if r.get("operation") == "baseline":
                    bases.setdefault((r["prompt_id"], r["seed"]), r["image_path"])
    byc = collections.defaultdict(dict)
    for r in rows:
        byc[COND[r["preset_file"]]][(r["prompt_id"], r["seed"])] = r["image_path"]
    conds = [c for _n, x, y in PAIRS for c in (x, y) if c in byc]

    # --- coppie appaiate: stesso prompt, stesso seed, due condizioni ----------
    cand = []
    for i in range(len(conds)):
        for j in range(i + 1, len(conds)):
            a, bb = conds[i], conds[j]
            for k in byc[a]:
                if k in byc[bb]:
                    ia, ib = byc[a][k], byc[bb][k]
                    if b(ia) in larg and b(ib) in larg:
                        cand.append((abs(larg[b(ia)] - larg[b(ib)]), ia, ib, k, f"{a}|{bb}"))
    cand.sort(key=lambda x: -x[0])
    n = args.n_per_gruppo
    gruppi = [("grossa", cand[:n]), ("soglia", cand[len(cand) // 2:len(cand) // 2 + n])]

    # --- controllo negativo: due baseline a seed diversi ---------------------
    neg = []
    byp = collections.defaultdict(list)
    for (p, s), rel in bases.items():
        byp[p].append((s, rel))
    for p, lst in byp.items():
        lst.sort()
        for i in range(0, min(len(lst) - 1, 4), 2):
            ia, ib = lst[i][1], lst[i + 1][1]
            if b(ia) in larg and b(ib) in larg:
                neg.append((abs(larg[b(ia)] - larg[b(ib)]), ia, ib, (p, "base"), "baseline|baseline"))
    gruppi.append(("controllo negativo", neg[:n]))

    print(f"[vlm] {args.model} via {args.backend} @ {args.url}")
    for g, lst in gruppi:
        if lst:
            d = [x[0] for x in lst]
            print(f"  {g:20s} {len(lst):3d} coppie   "
                  f"divario di larghezza misurato {min(d):.1f}-{max(d):.1f} px")
    tot = sum(len(l) for _g, l in gruppi) * 2 * args.repeats
    print(f"  {tot} chiamate (2 ordini x {args.repeats} ripetizioni)\n")

    crops = {}
    def crop(rel):
        if rel not in crops:
            crops[rel] = b64(ink_crop(idx[b(rel)]))
        return crops[rel]

    out, done = [], 0
    for gname, lst in gruppi:
        for dw, ia, ib, k, coppia in lst:
            for ordine, (x, y) in (("AB", (ia, ib)), ("BA", (ib, ia))):
                for rep in range(args.repeats):
                    prompt = SCHEMA.format(q=DOMANDA["tratto"])
                    try:
                        r = parse(ask(args.url, args.model, prompt, [crop(x), crop(y)]))
                    except Exception as e:
                        r = None
                        print(f"  [errore] {e}")
                    done += 1
                    if done % 20 == 0:
                        print(f"  {done}/{tot}")
                    if r is None:
                        out.append(dict(gruppo=gname, coppia=coppia, prompt_id=k[0],
                                        seed=k[1], ordine=ordine, ripetizione=rep,
                                        delta_px=round(dw, 3), scelta="ILLEGGIBILE",
                                        vince_il_piu_spesso="", confidenza="", motivo=""))
                        continue
                    # chi ha il tratto piu' spesso, secondo il calibro
                    spesso = ia if larg[b(ia)] >= larg[b(ib)] else ib
                    scelto = x if r["choice"] == "A" else (y if r["choice"] == "B" else None)
                    out.append(dict(gruppo=gname, coppia=coppia, prompt_id=k[0], seed=k[1],
                                    ordine=ordine, ripetizione=rep, delta_px=round(dw, 3),
                                    scelta=r["choice"],
                                    vince_il_piu_spesso=("" if scelto is None
                                                         else int(scelto == spesso)),
                                    confidenza=r["confidence"], motivo=r["evidence"]))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)

    # --- verdetto -------------------------------------------------------------
    print("\n" + "=" * 78)
    print("  IL GIUDICE E' UTILIZZABILE?")
    print("=" * 78)
    hs = "same"
    print(f"\n  {'gruppo':22s}{'accordo col calibro':>21s}{hs:>9s}"
          f"{'coerenza ordini':>17s}{'illeggibili':>13s}")
    verdetto = {}
    for gname, _l in gruppi:
        g = [r for r in out if r["gruppo"] == gname]
        if not g:
            continue
        dec = [r for r in g if r["vince_il_piu_spesso"] != ""]
        acc = np.mean([r["vince_il_piu_spesso"] for r in dec]) if dec else float("nan")
        same = np.mean([r["scelta"] == "SAME" for r in g])
        ill = np.mean([r["scelta"] == "ILLEGGIBILE" for r in g])
        byitem = collections.defaultdict(list)
        for r in g:
            byitem[(r["prompt_id"], r["seed"], r["coppia"])].append(r["scelta"])
        coer = np.mean([max(collections.Counter(v).values()) / len(v)
                        for v in byitem.values()])
        verdetto[gname] = (acc, same, coer, ill)
        print(f"  {gname:22s}{acc:>20.1%}{same:>9.1%}{coer:>17.1%}{ill:>13.1%}")

    print("\n  Come si legge:")
    print("   - 'grossa': deve stare ben sopra il 50%. Se e' vicino al caso su divari")
    print("     che il calibro misura come i piu' grandi del benchmark, il giudice non")
    print("     vede lo spessore del tratto e non si usa.")
    print("   - 'controllo negativo': li' NON c'e' nessun intervento, solo due seed")
    print("     diversi. La percentuale di 'same' deve essere ALTA. Se e' bassa, il")
    print("     giudice inventa differenze dove non ce ne sono, e allora nemmeno le")
    print("     sue risposte giuste altrove significano qualcosa.")
    print("   - coerenza fra i due ordini: sotto il 70% c'e' bias di posizione")
    print("     dominante e ogni media successiva e' rumore ordinato.")
    g = verdetto.get("grossa", (0, 0, 0, 0))
    ncg = verdetto.get("controllo negativo", (0, 0, 0, 0))
    ok = g[0] > 0.70 and g[2] > 0.70 and ncg[1] > 0.40
    esito = "PASSA: si puo' scalare" if ok else "NON PASSA: non usarlo come misura"
    print(f"\n  -> {esito}")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
