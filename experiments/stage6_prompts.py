# -*- coding: utf-8 -*-
"""
experiments/stage6_prompts.py  --  venti prompt nuovi per la fase successiva

PERCHE' VENTI.
Lo Stage 5 light ha stabilito che uno spostamento coerente a blocchi batte uno
incoerente a pari norma (preset - randsign = +0.165, IC95 [+0.024, +0.311]).
Non ha stabilito la scomposizione: preset - blockshuffle e' rimasto a +0.078 con
l'intervallo che copre lo zero. La semiampiezza dell'IC a 7 prompt e' circa 0.15
e la differenza da staccare e' 0.078; siccome l'ampiezza scala come 1/sqrt(P),
servono all'incirca 7 * (0.15/0.078)^2 ~ 26 prompt. Dieci non bastano, venticinque
si'. Questi venti portano la famiglia a trenta, con un margine che serve: la
proiezione e' fatta su una stima puntuale che a sua volta ha un errore.

REGOLE COSTRUTTIVE, tutte ereditate dai dieci esistenti e nessuna decorativa.

  * STESSA STRUTTURA, PAROLA PER PAROLA. Stile, inquadratura, sfondo e tag
    monocromatico sono identici in tutti e trenta. Alessandro l'aveva chiesto
    dopo lo Stage 1: "e' a parita' di stile e struttura del prompt stesso che si
    vedono effettivamente dei cambiamenti". Variano solo personaggio, tinta ed
    espressione, perche' la coerenza si misura FRA prompt e un prompt costruito
    diversamente introduce una differenza che non c'entra con i pesi.

  * TINTE TUTTE DIVERSE. Venti tinte che nei primi dieci non compaiono. Se due
    prompt condividono la dominante, il loro coseno sale per una ragione che non
    e' lo stile del modello -- e' esattamente la trappola di Block_6.

  * GENERI BILANCIATI. Dieci maschili e dieci femminili. Il vocabolario condiviso
    e' gia' neutro ("the face", non "her face") proprio per questo.

  * CINQUE ATTRIBUTI DICHIARATI CIASCUNO, presenti alla lettera nel testo. Sono
    la sola metrica che dice CHE COSA e' cambiato invece di quanto: una dominante
    di colore non puo' muovere "a single sharp lower tusk", un cambio di
    contenuto si'.

  * has_face: True ovunque, e qui e' vero. Nello Stage 1 avevo marcato il troll
    di P3 come has_face e l'asse identita' era sparito in silenzio. Tutti e venti
    hanno una faccia leggibile da ArcFace; dove ne dubitassi, il campo va messo a
    False PRIMA di lanciare, non dopo aver visto i numeri.

I PROMPT NON SI TOCCANO. Ne' per accorciarli, ne' per "migliorarli", ne' per
uniformare una virgola: prompt_sha1 esiste per accorgersene.
"""

_STYLE = ("Western comics style, bold ink outlines, hatched shadows, "
          "hard {hue}-tinted rim light glowing along the edges of {poss} face, "
          "{expr}, seen from {angle}, extreme close-up on the head only, "
          "tight framing, {dutch}. {subject}. white background, simple background, "
          "{hue} overall hue, monochromatic {hue}.")


def _p(pid, tag, hue, poss, expr, angle, dutch, subject, attrs):
    return {"id": pid, "tag": tag, "hue": hue, "has_face": True,
            "text": _STYLE.format(hue=hue, poss=poss, expr=expr, angle=angle,
                                  dutch=dutch, subject=subject),
            "attrs": attrs}


NEXT_PROMPTS = [

    _p("H01", "orc_magenta", "magenta", "his",
       "defiant curling snarl",
       "an extreme low angle looking sharply up past his jaw",
       "steep dutch angle",
       "young male orc, mottled grey-green skin, a single sharp upper tusk pushing "
       "through his lip, a shaved scalp crossed by four pale scars, small deep-set "
       "amber eyes narrowed hard, a flattened broken nose, a heavy brow ridge "
       "casting the eyes into shadow",
       ["a single sharp upper tusk pushing through his lip",
        "a shaved scalp crossed by four pale scars",
        "small deep-set amber eyes narrowed hard",
        "a flattened broken nose",
        "a heavy brow ridge casting the eyes into shadow"]),

    _p("H02", "elf_amber", "amber", "her",
       "serene unbothered contempt",
       "a slightly high three-quarter angle tilted off vertical",
       "sharp dutch angle",
       "very old female elf, translucent pale skin stretched thin over high "
       "cheekbones, long silver hair parted in a severe centre line, sharply "
       "pointed ears pierced with three thin rings each, heavy-lidded grey eyes "
       "that do not blink, a mouth set in a flat unimpressed line",
       ["translucent pale skin stretched thin over high cheekbones",
        "long silver hair parted in a severe centre line",
        "sharply pointed ears pierced with three thin rings each",
        "heavy-lidded grey eyes that do not blink",
        "a mouth set in a flat unimpressed line"]),

    _p("H03", "dwarf_vermilion", "vermilion", "his",
       "a roaring open-mouthed laugh",
       "an extreme low angle from below his beard looking straight up",
       "wildly canted dutch angle",
       "middle-aged male dwarf, broad ruddy face flushed dark, an enormous forked "
       "black beard bound with two iron clasps, bushy eyebrows shot up high, eyes "
       "squeezed almost shut with laughter, a bulbous nose veined red, a chipped "
       "front tooth showing in the open mouth",
       ["an enormous forked black beard bound with two iron clasps",
        "bushy eyebrows shot up high",
        "eyes squeezed almost shut with laughter",
        "a bulbous nose veined red",
        "a chipped front tooth showing in the open mouth"]),

    _p("H04", "tiefling_mint", "mint", "her",
       "a startled indrawn gasp",
       "an extreme low front angle beneath her chin",
       "sharp dutch angle",
       "young female tiefling, smooth lilac-grey skin, two slender horns swept "
       "straight back from the hairline, a thick black braid falling across one "
       "eye, wide solid-white eyes with no visible pupils, a small round mouth "
       "caught open mid-gasp, a thin gold chain looping from ear to nostril",
       ["two slender horns swept straight back from the hairline",
        "a thick black braid falling across one eye",
        "wide solid-white eyes with no visible pupils",
        "a small round mouth caught open mid-gasp",
        "a thin gold chain looping from ear to nostril"]),

    _p("H05", "dryad_olive", "olive", "his",
       "a slow settled sorrow",
       "a low angle tilted hard to one side",
       "steep dutch angle",
       "ancient male dryad, bark-textured brown skin split by deep vertical "
       "furrows, thin green shoots sprouting from his temples, moss gathered in "
       "the hollows beneath his eyes, small black eyes like knots in wood, a "
       "mouth that is barely a seam in the bark",
       ["bark-textured brown skin split by deep vertical furrows",
        "thin green shoots sprouting from his temples",
        "moss gathered in the hollows beneath his eyes",
        "small black eyes like knots in wood",
        "a mouth that is barely a seam in the bark"]),

    _p("H06", "orc_rose", "rose", "her",
       "weary immovable resolve",
       "an extreme low angle looking up beneath her jaw",
       "sharply canted dutch angle",
       "middle-aged female orc, deep olive skin scarred across one cheek, two "
       "blunt lower tusks worn down flat, black hair shaved at the sides and "
       "knotted high, tired heavy-lidded orange eyes, a broad flat nose with a "
       "bone ring through the septum",
       ["deep olive skin scarred across one cheek",
        "two blunt lower tusks worn down flat",
        "black hair shaved at the sides and knotted high",
        "tired heavy-lidded orange eyes",
        "a broad flat nose with a bone ring through the septum"]),

    _p("H07", "gnome_turquoise", "turquoise", "his",
       "gleeful conspiratorial mischief",
       "an extreme close low angle from just below his nose",
       "steep dutch angle",
       "young male gnome, ruddy freckled skin, an explosion of ginger curls "
       "pushed back by cracked goggles, enormous round eyes bright with delight, "
       "a small upturned nose smudged with soot, a wide grin showing a gap "
       "between the front teeth",
       ["an explosion of ginger curls pushed back by cracked goggles",
        "enormous round eyes bright with delight",
        "a small upturned nose smudged with soot",
        "a wide grin showing a gap between the front teeth",
        "ruddy freckled skin"]),

    _p("H08", "dwarf_gold", "gold", "her",
       "stern narrow-eyed disapproval",
       "a low front angle canted off vertical",
       "sharp dutch angle",
       "old female dwarf, weathered tan skin creased deep around the mouth, "
       "iron-grey hair coiled into a tight crown braid, thick eyebrows drawn "
       "into a single hard line, pale blue eyes narrowed to slits, a heavy "
       "square jaw set forward",
       ["weathered tan skin creased deep around the mouth",
        "iron-grey hair coiled into a tight crown braid",
        "thick eyebrows drawn into a single hard line",
        "pale blue eyes narrowed to slits",
        "a heavy square jaw set forward"]),

    _p("H09", "lizardfolk_lime", "lime", "his",
       "cold unhurried appraisal",
       "an extreme side-profile angle canted at a sharp diagonal",
       "steep dutch angle",
       "middle-aged male lizardfolk, fine emerald scales tightening across the "
       "snout, a low crest of stiff spines running back over the skull, a "
       "vertical slit pupil in a flat yellow eye, a forked tongue just visible "
       "between the teeth, one scale missing above the brow leaving pale skin",
       ["fine emerald scales tightening across the snout",
        "a low crest of stiff spines running back over the skull",
        "a vertical slit pupil in a flat yellow eye",
        "a forked tongue just visible between the teeth",
        "one scale missing above the brow leaving pale skin"]),

    _p("H10", "halfling_coral", "coral", "her",
       "wide-eyed unguarded wonder",
       "an extreme low angle looking up past her chin",
       "sharply canted dutch angle",
       "young female halfling, round sun-browned cheeks, thick chestnut curls "
       "escaping a knotted headscarf, enormous hazel eyes caught wide open, a "
       "scattering of freckles across the bridge of the nose, lips parted in a "
       "small silent oh",
       ["thick chestnut curls escaping a knotted headscarf",
        "enormous hazel eyes caught wide open",
        "a scattering of freckles across the bridge of the nose",
        "lips parted in a small silent oh",
        "round sun-browned cheeks"]),

    _p("H11", "vampire_sapphire", "sapphire", "her",
       "patient predatory hunger",
       "a slightly high angle tilted hard off vertical",
       "sharp dutch angle",
       "ancient female vampire, bloodless white skin with blue veins showing at "
       "the temple, black hair pulled back so tightly it strains the brow, two "
       "long slender fangs resting over the lower lip, pale irises ringed with a "
       "dark line, a high lace collar rising against the jaw",
       ["bloodless white skin with blue veins showing at the temple",
        "black hair pulled back so tightly it strains the brow",
        "two long slender fangs resting over the lower lip",
        "pale irises ringed with a dark line",
        "a high lace collar rising against the jaw"]),

    _p("H12", "minotaur_rust", "rust", "his",
       "a furious open-throated bellow",
       "an extreme low angle from directly beneath his muzzle",
       "wildly canted dutch angle",
       "middle-aged male minotaur, shaggy dark brown hide, two thick curved horns "
       "one of them snapped short, a heavy brass ring through the broad nose, "
       "small furious black eyes set wide apart, blunt square teeth bared in the "
       "open mouth",
       ["two thick curved horns one of them snapped short",
        "a heavy brass ring through the broad nose",
        "small furious black eyes set wide apart",
        "blunt square teeth bared in the open mouth",
        "shaggy dark brown hide"]),

    _p("H13", "satyr_plum", "plum", "his",
       "loose delighted drunkenness",
       "an extreme low tilted angle looking up his chin",
       "steep dutch angle",
       "young male satyr, warm tan skin flushed across the cheeks, two short "
       "ribbed horns curling back through tousled black curls, long pointed ears "
       "pushed out sideways, unfocused half-closed eyes, a crooked grin with wine "
       "still on the lower lip",
       ["two short ribbed horns curling back through tousled black curls",
        "long pointed ears pushed out sideways",
        "unfocused half-closed eyes",
        "a crooked grin with wine still on the lower lip",
        "warm tan skin flushed across the cheeks"]),

    _p("H14", "wizard_sepia", "sepia", "his",
       "exhausted narrow concentration",
       "a low three-quarter angle canted off vertical",
       "sharp dutch angle",
       "old male human wizard, deep brown skin lined heavily across the forehead, "
       "a long thin white beard twisted into a single point, wire spectacles "
       "slipped down to the end of the nose, dark eyes fixed on something too "
       "close to see, ink stains dried along the side of one finger at his temple",
       ["deep brown skin lined heavily across the forehead",
        "a long thin white beard twisted into a single point",
        "wire spectacles slipped down to the end of the nose",
        "dark eyes fixed on something too close to see",
        "ink stains dried along the side of one finger at his temple"]),

    _p("H15", "drow_scarlet", "scarlet", "her",
       "silent contained fury",
       "an extreme low front angle beneath her jaw",
       "steep dutch angle",
       "middle-aged female drow, deep charcoal-violet skin, straight white hair "
       "cut blunt at the jawline, sharply tapered ears held flat back, red irises "
       "burning against the dark skin, a thin white scar running from lip to chin",
       ["deep charcoal-violet skin",
        "straight white hair cut blunt at the jawline",
        "sharply tapered ears held flat back",
        "red irises burning against the dark skin",
        "a thin white scar running from lip to chin"]),

    _p("H16", "construct_azure", "azure", "her",
       "blank unblinking curiosity",
       "an extreme low angle tilted hard to one side",
       "sharply canted dutch angle",
       "young female clockwork construct, polished brass faceplate seamed down the "
       "centre, a hinged jaw hanging very slightly open, two glass lenses turning "
       "in place of eyes, fine copper wire braided where hair would be, a small "
       "keyhole set beneath one ear",
       ["polished brass faceplate seamed down the centre",
        "a hinged jaw hanging very slightly open",
        "two glass lenses turning in place of eyes",
        "fine copper wire braided where hair would be",
        "a small keyhole set beneath one ear"]),

    _p("H17", "fishman_ochre", "ochre", "his",
       "a wheezing toothless laugh",
       "an extreme low angle from below his gills looking up",
       "wildly canted dutch angle",
       "old male fishman, slick grey-green skin beaded with water, three ragged "
       "gill slits opening along the side of the neck, huge lidless round eyes set "
       "far apart, a wide lipless mouth stretched in a wheezing laugh, thin "
       "trailing barbels hanging from the chin",
       ["slick grey-green skin beaded with water",
        "three ragged gill slits opening along the side of the neck",
        "huge lidless round eyes set far apart",
        "a wide lipless mouth stretched in a wheezing laugh",
        "thin trailing barbels hanging from the chin"]),

    _p("H18", "harpy_emerald", "emerald", "her",
       "a shrieking open-beaked alarm",
       "an extreme low angle looking sharply up past her throat",
       "steep dutch angle",
       "middle-aged female harpy, a crown of dark ruffled feathers standing up "
       "from the skull, a hooked horn-coloured beak opened wide mid-shriek, round "
       "orange eyes ringed with bare grey skin, fine down covering the cheeks, a "
       "single long white feather out of place above one eye",
       ["a crown of dark ruffled feathers standing up from the skull",
        "a hooked horn-coloured beak opened wide mid-shriek",
        "round orange eyes ringed with bare grey skin",
        "fine down covering the cheeks",
        "a single long white feather out of place above one eye"]),

    _p("H19", "ghoul_violet", "violet", "his",
       "a vacant hollow stare",
       "an extreme low front angle beneath his chin",
       "sharp dutch angle",
       "young male ghoul, waxy grey skin drawn tight over the skull, patchy black "
       "hair coming away in clumps, sunken eyes clouded over pale, a nose worn "
       "back to two open slits, dark lips pulled away from long yellowed teeth",
       ["waxy grey skin drawn tight over the skull",
        "patchy black hair coming away in clumps",
        "sunken eyes clouded over pale",
        "a nose worn back to two open slits",
        "dark lips pulled away from long yellowed teeth"]),

    _p("H20", "centaur_copper", "copper", "her",
       "a proud level challenge",
       "a low front angle canted at a sharp diagonal",
       "steep dutch angle",
       "middle-aged female centaur, sun-darkened skin over a strong straight nose, "
       "thick auburn hair bound back with a leather cord, two small ears set high "
       "and turned forward, steady hazel eyes holding the viewer, a painted ochre "
       "stripe running down one cheekbone",
       ["sun-darkened skin over a strong straight nose",
        "thick auburn hair bound back with a leather cord",
        "two small ears set high and turned forward",
        "steady hazel eyes holding the viewer",
        "a painted ochre stripe running down one cheekbone"]),
]

ATTRS_NEXT = {p["id"]: p["attrs"] for p in NEXT_PROMPTS}
PROMPT_TEXT_BY_ID_NEXT = {p["id"]: p["text"] for p in NEXT_PROMPTS}
