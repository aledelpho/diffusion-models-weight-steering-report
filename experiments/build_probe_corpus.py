# -*- coding: utf-8 -*-
"""Costruisce data/prompts_probe_krea2.json — prompt sonda multi-contenuto per la mappa.

Scopo diverso da tutti gli altri corpus del progetto: qui non serve confrontare prompt fra
loro, serve **una sola immagine che contenga molti tipi di materia insieme**, perche' la
mappa di differenza per pixel possa dire su COSA agisce ogni blocco e non solo dove.

Registro: quello nativo di Krea-2 (frasi con relazioni, non grappoli di attributi), coerente
con i 40 prompt del corpus storico.

Vincolo di progetto: la composizione deve essere **molto specificata**. Una scena affollata
varia molto fra seed, il rumore di seed sale, la soglia del null sale con lui e la mappa
perde sensibilita'. Inquadratura, posizione del soggetto e disposizione degli elementi sono
quindi dichiarate nel testo.
"""
import json, hashlib, os, sys, re

PROMPTS = [
("P01", "forge_bench", """Western comics style, bold ink outlines, hatched shadows, medium wide shot, static centred composition, eye-level camera, subject centred and filling the middle third of the frame. A blacksmith woman stands behind a heavy oak workbench, facing the viewer, both hands resting flat on the wood. She has coarse dark curls tied back, weathered brown skin, a leather apron over a coarse linen shirt, and a polished steel gauntlet on her left forearm. On the bench lie a hammered copper bowl, a coil of frayed rope, and three rough granite offcuts. Behind her on the left a forge fire glows with a warm orange to deep red gradient, and thin smoke rises against a flat dark stone wall on the right. Cold blue window light falls from the upper left across the steel."""),

("P02", "greenhouse", """Western comics style, bold ink outlines, hatched shadows, medium wide shot, static centred composition, eye-level camera, subject centred and filling the middle third of the frame. A botanist man stands among potting benches, facing the viewer, one hand on a terracotta pot. He has straight pale hair, freckled fair skin, a knitted wool cardigan over a cotton shirt, and small round glasses. Broad waxy monstera leaves crowd the left of the frame and fine ferns the right. A glass carafe half full of water sits on the bench in front of him, beside damp dark soil and a brass watering can. Behind him the greenhouse panes show a pale cyan to warm cream sky gradient, with condensation beading on the glass."""),
]

OUT = sys.argv[1] if len(sys.argv) > 1 else "data/prompts_probe_krea2.json"
rows = [{"id": i, "tag": t, "sha1": hashlib.sha1(x.encode("utf-8")).hexdigest()[:10],
         "family": "probe_multicontent", "text": x} for i, t, x in PROMPTS]
assert len({r["sha1"] for r in rows}) == len(rows)

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
json.dump({"note": "Prompt sonda multi-contenuto per la mappa esplorativa dei blocchi. "
                   "NON fanno parte di nessun corpus di test: sono descrittivi e non entrano "
                   "in nessuna statistica. Registro nativo Krea-2. Composizione specificata "
                   "per tenere basso il rumore di seed.",
           "materials_present": {
               "P01": ["pelle", "capelli", "acciaio lucido", "rame martellato", "legno di quercia",
                       "cuoio", "lino grezzo", "corda", "granito", "fuoco e gradiente caldo",
                       "fumo", "pietra piatta di fondo"],
               "P02": ["pelle", "capelli", "lana lavorata a maglia", "cotone", "vetro trasparente",
                       "acqua", "terracotta", "ottone", "foglie larghe e cerose", "felci fini",
                       "terriccio scuro", "gradiente di cielo", "condensa"]},
           "prompts": rows},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

V = r"\b(stands|facing|resting|has|lie|rises|falls|glows|sits|show|crowd|beading|filling|tied|hammered|frayed|polished|knitted|centred)\b"
print(f"scritto {OUT}\n")
print(f"{'id':<5}{'sha1':<12}{'parole':>7}{'verbi':>6}{'v/parola':>9}  tag")
for r in rows:
    w = len(r["text"].split()); v = len(re.findall(V, r["text"], re.I))
    print(f"{r['id']:<5}{r['sha1']:<12}{w:>7}{v:>6}{v/w:>9.3f}  {r['tag']}")
print("\n(per confronto: corpus storico Krea-2 ~0.105 v/parola, corpus nativo Anima 0.028)")
