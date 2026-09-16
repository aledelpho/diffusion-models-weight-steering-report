# -*- coding: utf-8 -*-
"""
experiments/stage7_prompts.py -- Sei prompt per lo Stage 7 (Color Freedom Test)

SCOPO:
Verificare se, eliminando l'ancoraggio cromatico forzato ("monochromatic {hue}")
e lasciando il modello libero di scegliere la palette con "colored", i diversi
interventi sui pesi (Preset+, Preset-, Blockshuffle+, Blockshuffle-, Randsign+, Randsign-)
mostrano differenze cromatiche significative rispetto alla baseline.
"""

STAGE7_PROMPTS = [
    {
        "id": "S7_01",
        "tag": "sea_woman",
        "has_face": True,
        "text": (
            "Western comics style, bold ink outlines, hatched shadows, "
            "hard rim light glowing along the edges of her face, seductive simmering menace, "
            "seen from an extreme tilted low angle with her chin raised, extreme close-up on the head only, "
            "tight framing, sharp dutch angle. ageless female sea-touched woman, long dark hair fanning as if suspended in water, "
            "thin webbed fin-like ridges tracing along her temple, faintly scaled skin, sharply arched eyebrows, a narrow straight nose, "
            "wide eyes with slitted pupils half-lidded in cold allure, full lips curled in a knowing smirk, small barnacle-like clusters "
            "studding one earlobe, faint sheen along her jawline. white background, simple background, colored."
        ),
    },
    {
        "id": "S7_02",
        "tag": "goblin",
        "has_face": True,
        "text": (
            "Western comics style, bold ink outlines, hatched shadows, "
            "hard rim light glowing along the edges of his face, sly calculating grin, "
            "seen from an extreme low tilted angle looking sharply up his chin, extreme close-up on the head only, "
            "tight framing, steep dutch angle. middle-aged male goblin, mottled skin, greasy tufts of black hair slicked into a lopsided topknot, "
            "one eyebrow arched high in shrewd amusement, small beady eyes darting sideways, a long hooked nose with a slight downward curve, "
            "wide crooked grin showing several missing teeth, a small metal loop pierced through one nostril, thin wispy chin-whiskers "
            "braided into a point. white background, simple background, colored."
        ),
    },
    {
        "id": "S7_03",
        "tag": "dwarf_shout",
        "has_face": True,
        "text": (
            "Western comics style, bold ink outlines, hatched shadows, "
            "hard rim light glowing along the edges of her face, booming commanding shout, "
            "seen from an extreme low front angle looking sharply up beneath her jaw, extreme close-up on the head only, "
            "tight framing, sharp dutch angle. middle-aged female dwarf, weathered skin, thick hair braided tightly back from a high forehead, "
            "strong straight eyebrows drawn low, wide eyes blazing with authority, a broad sturdy nose, mouth open wide mid-shout showing "
            "strong square teeth, a small soot smudge dusting one cheekbone, thick leather strap crossing beneath her chin. "
            "white background, simple background, colored."
        ),
    },
    {
        "id": "S7_04",
        "tag": "hag",
        "has_face": True,
        "text": (
            "Western comics style, bold ink outlines, hatched shadows, "
            "hard rim light glowing along the edges of her face, wild-eyed manic determination, "
            "seen from an extreme low angle shot through an imagined gap between her chin and chest, extreme close-up on the head only, "
            "tight framing, sharply canted dutch angle. very old female hag, deeply weathered skin, wild frizzed grey hair sticking straight up "
            "as if charged with static, an exaggeratedly long hooked nose nearly touching her upturned chin, small sunken eyes blazing wide "
            "with fevered focus, sagging jowls trembling around a muttering open mouth, three long grey chin-hairs twisted into tiny braids, "
            "a single large hoop stretching one earlobe low. white background, simple background, colored."
        ),
    },
    {
        "id": "S7_05",
        "tag": "dwarf_sneeze",
        "has_face": True,
        "text": (
            "Western comics style, bold ink outlines, hatched shadows, "
            "hard rim light glowing along the edges of her face, explosive uncontrollable sneeze, "
            "seen from an extreme close angle shot from below her nostrils looking straight up, extreme close-up on the head only, "
            "tight framing, wildly canted dutch angle. middle-aged female dwarf, deeply sun-weathered skin, elaborate silver hair twisted "
            "into thick coiled loops atop her head, eyebrows scrunched violently together, a broad nose flared wide mid-sneeze, eyes squeezed "
            "shut with lashes fanned outward, mouth caught wide open in an explosive \"achoo\", a jeweled hairpin knocked askew, small crumbs "
            "of some pastry still clinging to her lower lip. white background, simple background, colored."
        ),
    },
    {
        "id": "S7_06",
        "tag": "tiefling_cold",
        "has_face": True,
        "text": (
            "Western comics style, bold ink outlines, hatched shadows, "
            "hard rim light glowing along the edges of his face, severe icy contempt, "
            "seen from an extreme side-profile angle canted at a sharp diagonal, extreme close-up on the head only, "
            "tight framing, steep dutch angle. older male tiefling, deep charcoal-grey skin, short curling horns swept flat against "
            "cropped silver hair, heavy-lidded eyes narrowed in judgment, a sharply hooked nose, deep-set lines bracketing a thin frowning mouth, "
            "one long fang resting over his lower lip, faint smoke curling from one nostril. white background, simple background, colored."
        ),
    },
]
