# -*- coding: utf-8 -*-
"""Costruisce data/prompts_anima_native.json dai 10 prompt in formato nativo Anima.

I testi sono incollati verbatim come forniti dall'utente. Ogni prompt riceve un
prompt_sha1 (primi 10 hex di sha1 del testo) con la stessa convenzione del corpus
Krea-2, cosi' che l'identita' dei prompt sia verificabile e nessuno possa
modificarli senza che l'hash smetta di tornare.
"""
import json, hashlib, re, os, sys

PROMPTS = [
("A01", "elf_brawler", """realistic comic style, gradients, hatched shadows, seen from below with a low angle, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective deformation.
Female elf brawler, short messy lime to teal green bob haircut, long side bangs, small antlers, pointed ears. Black eyepatch, green eye, cross scar, smug angry smile.
Black leather uniform, white fur collar, wooden shoulder pauldron. giant metal gauntlet, open hand, electricity crackling.
white background, simple background."""),

("A02", "tiefling_vanguard", """realistic comic style, gradients, hatched shadows,  extreme close-up detail shot from an angle, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective.
Female tiefling vanguard, short spiky obsidian to neon violet undercut, asymmetric side swept bangs, light purple to light blue gradient skin, ram horns, sharp fangs. blue eyes, jagged burn scar across the cheek, defiant feral snarl. Dark plate armor. short yellow cape, Mid-air leap, axe raised, body coiled to strike downward with maximum force.
white background, simple background."""),

("A03", "orc_wizard", """realistic comic style, gradients, hatched shadows, seen from above with a high angle close-up, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective.
male orc wizard, long white hair dreadlocks, very long white eyebrows, small reading glasses, light green to cold green skin gradient, two fangs from lower lips, old, long nails, white beard, wrinkles, yellow eyes. squared jaw, fat, annoyed expression. blue wizard robe, very long blue flame behind him, gold very long earrings. holding a wooden staff bored expression.
 white background, simple background."""),

("A04", "stag_wolf_bear", """realistic comic style, gradients, hatched shadows, seen from below with a low angle, dynamic pose, dramatic angle, strong perspective.
Stag + Wolf + Bear monster, shaggy coarse dark brown to pale tan gradient fur, massive moss-covered stag antlers, long wolf-like snout with exposed black gums, old, heavily weathered hide, thick dull claws. Golden torc ring pierced through the upper cartilage of the left ear, pale yellow eyes, blunt scarred muzzle, wild bared-teeth expression. Immense top-heavy bear build with a massive shoulder hump. Faded tattered plaid wool cloak pinned across its broad back with a heavy bronze penannular brooch. Rearing up on its hind legs, front paws clawing the air, chest exposed, body balanced in a towering dominant stance.
white background, simple background."""),

("A05", "alligator_prep", """western cartoon style, gradients, hatched shadows,  extreme close-up detail shot from an angle, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective.
Male alligator prep, short razor-cut preppy side-part, olive green to pale yellow underbelly scale gradient, heavy ridge scales along the spine, blunt dark talons. Gold rimless monocle over one eye, solid amber reptilian eyes, long heavy jaw, smug condescending smile. Tall broad-shouldered build. Navy blue cable-knit sweater vest worn over a crisp white collared shirt, tailored beige trousers. Adjusting a silk navy blue necktie with one hand, body turned in a rigid three-quarter stance.
 white background, simple background."""),

("A06", "orc_captain", """realistic comic style, gradients, hatched shadows,  extreme close-up detail shot from an angle, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective.
Male orc captain, bald polished head, elongated pointed ears, protruding lower tusks. Iron brow-ring, piercing yellow eyes, split lip scar, calm focused expression. Loose wrap vest with a deep amber to crimson gradient, flowing linen trousers. Low-centered martial arts stance, one hand extended in a open-palm guard, tensed, dust kicking up around his feet.
 white background, simple background."""),

("A07", "tiefling_noble", """realistic comic style, gradients, hatched shadows, seen from below with a low angle, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective.
Female tiefling noble, long straight stark white to dark gray hair, sharp center-parted bangs, light purple to light blue skin gradient, sleek swept-back ram horns. Solid black eyes, sharp pointed jaw, tall slender build, cold analytical expression. Fitted velvet waist-cincher featuring a deep red to black color gradient, long sheer fabric sashes draping from her upper arms. Rigid stationary pose, body turned three-quarters away, head turned back over her shoulder with a sharp profile view.
white background, simple background."""),

("A08", "elf_judge", """realistic comic style, gradients, hatched shadows, seen from above with a high angle close-up, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective.
attractive Female elf judge, long straight hair with a gradient from black ro red, striped pattern on robes, pale skin, wide nose. giant deco artstyle necklace, dark red eyes, round softened jaw, serene expression, laughing. sun themed decorations, belt made of thorns with large leaves. Leaning forward waving to the camera, relaxed and chill.
white background, simple background."""),

("A09", "goblin_mariner", """realistic comic style, gradients, hatched shadows, seen from above with a high angle close-up, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective.
Female goblin mariner, short spiky dark yellow to light yellow pixie cut, messy asymmetric bangs, dark green skin, wide bat-like ears, sharp needle teeth. Dark orange eyes, small round jaw, short lean build, manic cheerful smile. Wide leather utility belt with brass buckles, a frayed linen sash with a dark blue to light blue color gradient tied around her waist. Kinetic mid-stride stance, one foot planted high on an invisible ledge, torso twisted forward as if ready to spring off.
white background, simple background."""),

("A10", "firbolg_botanist", """realistic comic style, gradients, hatched shadows, seen from above with a high angle close-up, upper body portrait, dutch angle, dynamic pose, dramatic angle, strong perspective.
Female firbolg botanist, long fluffy chocolate brown to pastel pink hair tied in a loose messy bun, thick soft eyebrows, floppy cow-like ears, soft lilac to pale cream gradient skin, small pink nose, young, round gentle face. Round wire-rimmed reading glasses, wide warm hazel eyes, soft rounded jawline, shy endearing smile. Plump soft build, slouching posture. Oversized thick-knit cream sweater with a pattern of embroidered acorns. Holding a wooden teacup close to her face, body slightly turned inward in a comfortable sitting posture.
white background, simple background."""),
]

OUT = sys.argv[1] if len(sys.argv) > 1 else "data/prompts_anima_native.json"

rows = []
for pid, tag, text in PROMPTS:
    rows.append({"id": pid, "tag": tag,
                 "sha1": hashlib.sha1(text.encode("utf-8")).hexdigest()[:10],
                 "family": "anima_native", "text": text})

assert len({r["sha1"] for r in rows}) == len(rows), "collisione di hash o prompt duplicato"

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
json.dump({"note": "Corpus in formato nativo Anima (grappoli di attributi, bassa densita' "
                   "relazionale). prompt_sha1 = primi 10 hex di sha1(text), stessa convenzione "
                   "di data/prompts.json. I prompt non vanno mai modificati.",
           "prompts": rows},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- proprietà del corpus, da dichiarare prima di misurare
VERBS = r"\b(is|are|holding|wearing|wears|adjusting|raised|turned|clawing|balanced|kicking|coiled|draping|pinned|worn|pierced|crackling|extended|rearing|leaning|waving|planted|twisted|slouching|tied|embroidered|swung|trailing|propped)\b"
print(f"scritto {OUT} — {len(rows)} prompt\n")
print(f"{'id':<5}{'sha1':<12}{'parole':>7}{'virgole':>8}{'verbi':>6}{'v/parola':>9}  tag")
tot = []
for r in rows:
    w = len(r["text"].split()); v = len(re.findall(VERBS, r["text"], re.I))
    tot.append((w, v))
    print(f"{r['id']:<5}{r['sha1']:<12}{w:>7}{r['text'].count(','):>8}{v:>6}{v/w:>9.3f}  {r['tag']}")
W = sum(x[0] for x in tot); V = sum(x[1] for x in tot)
print(f"\ndensita' relazionale del corpus: {V/W:.3f} verbi/parola")
print(f"(Krea-2 I07, per confronto: 6 verbi / 57 parole = 0.105)\n")

for phrase in ["hatched shadows", "gradients", "white background", "simple background",
               "realistic comic style", "western cartoon style", "upper body portrait",
               "seen from below", "seen from above", "extreme close-up"]:
    n = sum(1 for r in rows if phrase in r["text"].lower())
    print(f"  {phrase:<24}{n}/10")
