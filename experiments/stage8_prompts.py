import hashlib
import csv
import os
import sys

REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
sys.path.append(os.path.join(REPORT_ROOT, "experiments"))
from stage7_prompts import STAGE7_CANDIDATES

# -------------------------------------------------------------
# BRACCIO A: PROMPT VUOTO (1 prompt, 20 render)
# -------------------------------------------------------------
PROMPT_EMPTY = {
    "prompt_id": "P0_empty",
    "arm": "A",
    "subject_id": "empty",
    "color_variant": "none",
    "prompt_tag": "empty_string",
    "prompt_text": "",
}

# -------------------------------------------------------------
# BRACCIO B: 4 COPPIE APPAIATE FISSATO / LIBERO (8 prompt, 160 render)
# -------------------------------------------------------------
PAIRS_B = [
    # Coppia 1: Donna nana (Amber)
    {
        "subject_id": "B1_dwarf",
        "color_variant": "free",
        "prompt_id": "B1_free",
        "prompt_tag": "dwarf_amber_free",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A dwarf woman with twin braided ginger pigtails, freckled cheeks, brass goggles resting on her forehead, wearing heavy leather smithing aprons and riveted gauntlets, confident warm smile, direct eye contact. Simple background."
    },
    {
        "subject_id": "B1_dwarf",
        "color_variant": "fixed",
        "prompt_id": "B1_fixed",
        "prompt_tag": "dwarf_amber_fixed",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, hard amber-tinted rim light glowing along the edges of her face, upper body portrait. A dwarf woman with twin braided ginger pigtails, freckled cheeks, brass goggles resting on her forehead, wearing heavy leather smithing aprons and riveted gauntlets, confident warm smile, direct eye contact. Simple background, amber overall hue, monochromatic amber."
    },

    # Coppia 2: Erudito elfo scuro (Teal)
    {
        "subject_id": "B2_elf",
        "color_variant": "free",
        "prompt_id": "B2_free",
        "prompt_tag": "elf_teal_free",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A tall dark elf scholar with sleek white hair pulled back, arched eyebrows, narrow intense eyes, wearing a high-collared scholar robe embroidered with silver runes, holding an open leather-bound grimoire, sharp thoughtful expression. Simple background."
    },
    {
        "subject_id": "B2_elf",
        "color_variant": "fixed",
        "prompt_id": "B2_fixed",
        "prompt_tag": "elf_teal_fixed",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, hard teal-tinted rim light glowing along the edges of his face, upper body portrait. A tall dark elf scholar with sleek white hair pulled back, arched eyebrows, narrow intense eyes, wearing a high-collared scholar robe embroidered with silver runes, holding an open leather-bound grimoire, sharp thoughtful expression. Simple background, teal overall hue, monochromatic teal."
    },

    # Coppia 3: Cyborg guerriero (Crimson)
    {
        "subject_id": "B3_cyborg",
        "color_variant": "free",
        "prompt_id": "B3_free",
        "prompt_tag": "cyborg_crimson_free",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A cybernetic human warrior with short buzzcut hair, segmented chrome jawline, glowing optic sensor implant over one eye, clad in ballistic carbon armor with exposed hydraulics, stoic grim gaze. Simple background."
    },
    {
        "subject_id": "B3_cyborg",
        "color_variant": "fixed",
        "prompt_id": "B3_fixed",
        "prompt_tag": "cyborg_crimson_fixed",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, hard crimson-tinted rim light glowing along the edges of his face, upper body portrait. A cybernetic human warrior with short buzzcut hair, segmented chrome jawline, glowing optic sensor implant over one eye, clad in ballistic carbon armor with exposed hydraulics, stoic grim gaze. Simple background, crimson overall hue, monochromatic crimson."
    },

    # Coppia 4: Sacerdotessa genasi (Ultramarine)
    {
        "subject_id": "B4_genasi",
        "color_variant": "free",
        "prompt_id": "B4_free",
        "prompt_tag": "genasi_ultramarine_free",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A water genasi priestess with wavy translucent blue hair floating softly, smooth azure skin, droplet pearls dangling from her earlobes, draped in seafoam silk garments, serene contemplative expression. Simple background."
    },
    {
        "subject_id": "B4_genasi",
        "color_variant": "fixed",
        "prompt_id": "B4_fixed",
        "prompt_tag": "genasi_ultramarine_fixed",
        "prompt_text": "Western comics style, bold ink outlines, hatched shadows, hard ultramarine-tinted rim light glowing along the edges of her face, upper body portrait. A water genasi priestess with wavy translucent blue hair floating softly, smooth azure skin, droplet pearls dangling from her earlobes, draped in seafoam silk garments, serene contemplative expression. Simple background, ultramarine overall hue, monochromatic ultramarine."
    },
]

# -------------------------------------------------------------
# BRACCIO C: 4 PROMPT DA STAGE 7 (4 prompt, 120 render)
# -------------------------------------------------------------
PROMPTS_C_KEYS = ["I06", "I07", "I20", "I24"]
PROMPTS_C = []
for p in STAGE7_CANDIDATES:
    if p["id"] in PROMPTS_C_KEYS:
        PROMPTS_C.append({
            "prompt_id": p["id"],
            "arm": "C",
            "subject_id": p["id"],
            "color_variant": "stage7_baseline",
            "prompt_tag": p["tag"],
            "prompt_text": p["text"]
        })

def sha1(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]

def build_catalog():
    all_prompts = []
    
    # Arm A
    p_a = dict(PROMPT_EMPTY)
    p_a["prompt_sha1"] = sha1(p_a["prompt_text"])
    all_prompts.append(p_a)

    # Arm B
    for p in PAIRS_B:
        p_b = dict(p)
        p_b["arm"] = "B"
        p_b["prompt_sha1"] = sha1(p_b["prompt_text"])
        all_prompts.append(p_b)

    # Arm C
    for p in PROMPTS_C:
        p_c = dict(p)
        p_c["prompt_sha1"] = sha1(p_c["prompt_text"])
        all_prompts.append(p_c)

    # Save to CSV
    csv_path = os.path.join(REPORT_ROOT, "data", "stage8_prompts.csv")
    fieldnames = ["prompt_id", "arm", "subject_id", "color_variant", "prompt_tag", "prompt_sha1", "prompt_text"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_prompts)

    print(f"Catalogo Stage 8 generato con successo: {len(all_prompts)} prompt totali in {csv_path}")
    for p in all_prompts:
        print(f"  [{p['arm']}] {p['prompt_id']:10s} {p['prompt_sha1']} {p['prompt_tag']}")

if __name__ == "__main__":
    build_catalog()
