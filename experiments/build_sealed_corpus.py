# -*- coding: utf-8 -*-
"""Genera un corpus di prompt SIGILLATO per i test confermativi futuri.

PROBLEMA CHE RISOLVE
  Chi scrive i prompt di un test di conferma li sceglie, consapevolmente o no, fra quelli su
  cui si aspetta che l'effetto si veda. Vale per l'utente (che ha anni di intuizioni su cosa
  funziona) e vale per il modello che assiste (che ha visto tutti i dati dell'esplorazione).

SOLUZIONE
  Nessuno dei due sceglie le combinazioni. Il vocabolario e' dichiarato per intero qui sotto,
  in chiaro; le combinazioni sono estratte da un generatore con seme fissato e scritto nel
  file. Chiunque puo' rieseguire e ottenere gli stessi prompt.

LIMITE CHE RESTA, E VA DICHIARATO
  Il vocabolario l'ha scritto il modello. La randomizzazione rimuove la selezione degli
  stimoli a favore dell'ipotesi; non rimuove il fatto che le liste potrebbero essere sbilanciate
  in partenza. Mitigazione: ogni slot copre lo spettro in modo deliberatamente simmetrico
  (sorgenti di luce calde e fredde, materiali lucidi e opachi, ambienti chiusi e aperti), e le
  liste sono ispezionabili.

VINCOLO DI PROGETTO
  Ogni prompt dichiara una sorgente di luce e una struttura tonale, perche' le grandezze sotto
  test (alte luci, ombre, contrasto, saturazione) sono indefinite su una scena piatta. Questa
  e' una scelta di disegno, non un'ottimizzazione: serve che la misura esista, non che esca in
  un certo verso. Meta' delle sorgenti sono calde e meta' fredde.

  Registro: nativo Krea-2 (frasi con relazioni). Composizione dichiarata, per tenere basso il
  rumore di seed.
"""
import json, hashlib, random, sys, os, re

RNG_SEED = 20260919          # fissato prima di generare, scritto qui, mai cambiato

SOGGETTO = [
 "a stonemason woman", "an elderly clockmaker", "a young falconer", "a harbour pilot",
 "a travelling bookbinder", "a mountain surveyor", "a glassblower man", "a night fisherman",
]
TRATTI = [
 "with cropped grey hair and deep-set eyes", "with a long dark braid and a scarred cheek",
 "with close shorn hair and a broad flat nose", "with loose red curls and pale freckled skin",
 "with a heavy beard and weathered brown skin", "with thin blond hair and sharp cheekbones",
]
VESTE = [
 "a waxed canvas coat over a ribbed sweater", "a quilted jacket and a linen scarf",
 "a leather jerkin over a rough wool shirt", "an oilskin cape and knitted fingerless gloves",
 "a felted overcoat with horn buttons", "a padded gambeson and a cotton undershirt",
]
LUOGO = [
 "in a low vaulted cellar", "on a windswept stone pier", "inside a timber-framed attic",
 "at the mouth of a slate quarry", "in a narrow tiled workshop", "on a railed iron walkway",
]
LUCE_CALDA = [
 "A brazier burns low on the left, throwing a deep amber to dull red gradient across the scene",
 "An oil lamp on the near table casts a narrow warm pool that falls off sharply into darkness",
 "Late sun enters from a single high window in a hard orange shaft, leaving the corners black",
]
LUCE_FREDDA = [
 "Flat blue daylight comes from an opening on the right, with no direct sun and soft shadows",
 "A gas lantern overhead gives a pale green-white light that flattens every surface evenly",
 "Overcast light from above renders the whole scene in close, low-contrast greys",
]
OGGETTI = [
 "A chipped enamel basin, a bundle of waxed twine and two iron wedges sit on the bench before them",
 "A brass caliper, a stack of pressed paper and a cracked ceramic jar lie within reach",
 "A coiled leather strap, a tin cup and three split river stones rest on the surface in front",
 "A folded tarpaulin, a bone-handled knife and a glass float are arranged across the foreground",
]

PREFISSO = ("Western comics style, bold ink outlines, hatched shadows, medium wide shot, "
            "static centred composition, eye-level camera, subject centred and filling the "
            "middle third of the frame.")

def build(n=12):
    rng = random.Random(RNG_SEED)
    out, visti = [], set()
    luci = [(l, "calda") for l in LUCE_CALDA] + [(l, "fredda") for l in LUCE_FREDDA]
    while len(out) < n:
        s, t, v = rng.choice(SOGGETTO), rng.choice(TRATTI), rng.choice(VESTE)
        lg = rng.choice(LUOGO)
        luce, temp = luci[len(out) % len(luci)]          # alternanza calda/fredda imposta
        og = rng.choice(OGGETTI)
        testo = (f"{PREFISSO} {s.capitalize()} {t} stands {lg}, facing the viewer, wearing "
                 f"{v}. {og}. {luce}.")
        h = hashlib.sha1(testo.encode("utf-8")).hexdigest()[:10]
        if h in visti: continue
        visti.add(h)
        out.append({"id": f"S{len(out)+1:02d}", "sha1": h, "temperatura": temp,
                    "family": "sealed_confirmatory", "text": testo})
    return out

if __name__ == "__main__":
    OUT = sys.argv[1] if len(sys.argv) > 1 else "data/prompts_sealed_krea2.json"
    rows = build()
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    payload = {"note": "CORPUS SIGILLATO. Generato meccanicamente il 2026-09-19 con seme "
                       f"{RNG_SEED}. Riservato ai test CONFERMATIVI: non va usato in nessuna "
                       "analisi esplorativa, e nessuna statistica va calcolata su queste scene "
                       "prima che l'ipotesi da testare sia scritta e datata.",
               "rng_seed": RNG_SEED, "prompts": rows}
    json.dump(payload, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    blob = "".join(r["sha1"] for r in rows)
    print(f"scritto {OUT}   {len(rows)} prompt")
    print(f"IMPRONTA DEL CORPUS (sha256 degli sha1 in ordine): {hashlib.sha256(blob.encode()).hexdigest()}")
    V = (r"\b(stands|facing|wearing|sit|lie|rest|are|burns|casts|enters|comes|gives|falls|"
         r"throwing|leaving|renders|arranged|filling|centred|pressed|split|coiled|folded)\b")
    for r in rows:
        w = len(r["text"].split()); v = len(re.findall(V, r["text"], re.I))
        print(f"  {r['id']}  {r['sha1']}  {w:>3} parole  {v/w:.3f} v/parola  luce {r['temperatura']}")
