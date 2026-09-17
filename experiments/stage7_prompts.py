# -*- coding: utf-8 -*-
"""
experiments/stage7_prompts.py
I 24 prompt candidati per lo Stage 7 (Tempo A), definiti in newpromptlist.txt.
"""
import hashlib

STAGE7_CANDIDATES = [
    {
        "id": "I01",
        "tag": "a_viking_woman_with_blonde_long_braided_hair",
        "sha1": "2adb8ea1cd",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A viking woman with blonde long braided hair. armor made of ice, She wears an iron crown and large metallic shoulder pads. She's holding a mace with both hands, casual pose, snob, playful. snow covered plains, simple background. blue reflections on the metal."
    },
    {
        "id": "I02",
        "tag": "an_elf_man_with_long_white_straight_hair",
        "sha1": "0aa12a28b0",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. An elf man with long white straight hair. armor made of obsidian, He wears a silver circlet and thin curved shoulder guards. He's holding a rapier upright in one hand, defensive pose, calm, focused. misty autumn forest, simple background. green reflection on the glass."
    },
    {
        "id": "I03",
        "tag": "an_orc_woman_with_dark_green_dreadlocks",
        "sha1": "c31d285321",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. An orc woman with dark green dreadlocks. armor made of bone, She wears a skull headpiece and thick hide shoulder wraps. She's holding a jagged broadsword with both hands, aggressive pose, furious, menacing. muddy battlefield trenches, simple background. orange reflection on the bone."
    },
    {
        "id": "I04",
        "tag": "a_goblin_man_with_huge_pointed_ears",
        "sha1": "bb8edafd35",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A goblin man with huge pointed ears. armor made of scrap iron, He wears cracked brass goggles and mismatched plate shoulder pads. He's holding a mechanical wrench in two hands, cowering pose, paranoid, nervous. dark cavern workshop, simple background. yellow reflection on the brass."
    },
    {
        "id": "I05",
        "tag": "a_tiefling_woman_with_curled_ram_horns_and_purple_hair",
        "sha1": "5b67e787c8",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A tiefling woman with curled ram horns and purple hair. armor made of chitin, She wears a gold diadem and spiked black shoulder pads. She's holding a curved dagger underhand, dynamic pose, smug, cunning. brimstone volcanic wasteland, simple background. violet reflection on the chitin."
    },
    {
        "id": "I06",
        "tag": "a_human_man_with_cropped_brown_hair_and_stubble",
        "sha1": "a324a148e4",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A human man with cropped brown hair and stubble. armor made of steel, He wears a chainmail coif and round polished shoulder guards. He's holding a tower shield across his chest, guarding pose, weary, resolute. ruined castle courtyard, simple background. white reflection on the metal."
    },
    {
        "id": "I07",
        "tag": "a_half_orc_man_with_a_shaved_head_and_facial_scars",
        "sha1": "402376662d",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A half-orc man with a shaved head and facial scars. armor made of granite, He wears an iron jaw visor and layered stone shoulder pads. He's holding a heavy greataxe pointed down, relaxed pose, solemn, tired. cracked dry earth, simple background. blue reflection on the stone."
    },
    {
        "id": "I08",
        "tag": "a_high_elf_woman_with_a_tight_red_ponytail",
        "sha1": "c00acc77d9",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A high elf woman with a tight red ponytail. armor made of mother-of-pearl, She wears a filigree tiara and winged gold shoulder guards. She's holding a longbow held horizontally, poised pose, arrogant, regal. pristine marble terrace, simple background. cyan reflection on the pearl."
    },
    {
        "id": "I09",
        "tag": "a_dwarf_woman_with_twin_braided_ginger_pigtails",
        "sha1": "0a1c94584d",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A dwarf woman with twin braided ginger pigtails. armor made of copper, She wears an iron miner cap and thick square shoulder pads. She's holding a heavy pickaxe leaning forward, cheerful pose, grinning, confident. underground crystal mine, simple background. yellow reflection on the copper."
    },
    {
        "id": "I10",
        "tag": "a_lizardfolk_man_with_spiked_crest_and_yellow_eyes",
        "sha1": "90ec9bbe8c",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A lizardfolk man with spiked crest and yellow eyes. armor made of hard scales, He wears a feather headdress and woven rope shoulder pads. He's holding a flint spear ready to strike, predatory pose, wild, alert. murky green swamp, simple background. green reflection on the scales."
    },
    {
        "id": "I11",
        "tag": "a_gnome_woman_with_wild_blue_curls",
        "sha1": "2b36c75165",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A gnome woman with wild blue curls. armor made of carved amber, She wears oversized brass monocles and round gear-shaped shoulder guards. She's holding an alchemical vial in both hands, frantic pose, manic, excited. stone alchemy laboratory, simple background. orange reflection on the glass."
    },
    {
        "id": "I12",
        "tag": "a_human_woman_with_short_raven_pixie_cut",
        "sha1": "8c3325ffd9",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A human woman with short raven pixie cut. armor made of polished silver, She wears a cloth hood and sleek aerodynamic shoulder guards. She's holding a shortsword crossed over chest, ready pose, cold, calculating. rain-soaked rooftop, simple background. blue reflection on the silver."
    },
    {
        "id": "I13",
        "tag": "a_minotaur_man_with_heavy_iron_nose_ring",
        "sha1": "fb96d83893",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A minotaur man with heavy iron nose ring. armor made of black basalt, He wears a spiked collar and enormous segmented iron shoulder pads. He's holding a giant iron club low, hulking pose, sullen, brooding. sandy colosseum arena, simple background. red reflection on the basalt."
    },
    {
        "id": "I14",
        "tag": "a_wood_elf_woman_with_messy_brown_braided_crown",
        "sha1": "c478c2b3f1",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A wood elf woman with messy brown braided crown. armor made of petrified bark, She wears a dried floral wreath and thorn-covered shoulder wraps. She's holding a wooden stave grounded, graceful pose, serene, distant. dense pine woods, simple background. amber reflection on the bark."
    },
    {
        "id": "I15",
        "tag": "a_dragonborn_man_with_dark_red_scaled_face",
        "sha1": "ef69aba3ba",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A dragonborn man with dark red scaled face. armor made of brass, He wears a crested war mask and draconic claw shoulder pads. He's holding a halberd upright, rigid military pose, arrogant, imposing. smoking fortress ramparts, simple background. yellow reflection on the brass."
    },
    {
        "id": "I16",
        "tag": "a_halfling_man_with_curly_blond_sideburns",
        "sha1": "5421ab290b",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A halfling man with curly blond sideburns. armor made of layered leather, He wears a wool beret and hardened boiled-leather shoulder pads. He's holding a small iron buckler and sling, nimble pose, cheekily defiant, smirking. rolling green hillside, simple background. white reflection on the leather."
    },
    {
        "id": "I17",
        "tag": "an_undead_human_woman_with_hollow_cheeks_and_ragged_dark_hair",
        "sha1": "0dee1ceb78",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. An undead human woman with hollow cheeks and ragged dark hair. armor made of rusted iron, She wears a bent copper coronet and cracked tattered shoulder guards. She's holding a broken straight sword hanging limp, motionless pose, hollow, mournful. foggy burial mound, simple background. violet reflection on the rust."
    },
    {
        "id": "I18",
        "tag": "a_celestial_woman_with_glowing_metallic_gold_skin",
        "sha1": "3d8a617173",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A celestial woman with glowing metallic gold skin. armor made of white marble, She wears a glowing ring halo and ornate wing-shaped shoulder pads. She's holding a two-handed radiant claymore pointed to sky, righteous pose, fierce, zealous. cloud-covered summit, simple background. yellow reflection on the marble."
    },
    {
        "id": "I19",
        "tag": "a_deep_gnome_man_with_chalky_gray_bald_head",
        "sha1": "f1f616b0ac",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A deep gnome man with chalky gray bald head. armor made of raw lead, He wears a tinted leather visor and blocky slate shoulder pads. He's holding a heavy iron chisel, cautious pose, suspicious, guarded. dark stalactite cavern, simple background. cyan reflection on the lead."
    },
    {
        "id": "I20",
        "tag": "a_drow_man_with_swept_back_silver_hair",
        "sha1": "952efcc3c6",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A drow man with swept-back silver hair. armor made of dark adamantine, He wears a spider-web cowl and sharp chitinous shoulder guards. He's holding dual twin daggers drawn, predatory pose, mocking, sinister. subterranean purple cavern, simple background. magenta reflection on the adamantine."
    },
    {
        "id": "I21",
        "tag": "an_elemental_woman_with_fiery_orange_glowing_hair",
        "sha1": "2f3689f658",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. An elemental woman with fiery orange glowing hair. armor made of cooled magma, She wears a burning cinder crown and charred basalt shoulder pads. She's holding a glowing iron staff in two hands, commanding pose, passionate, fierce. volcanic ash desert, simple background. red reflection on the obsidian."
    },
    {
        "id": "I22",
        "tag": "a_barbarian_man_with_messy_long_black_hair",
        "sha1": "c412444d34",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A barbarian man with messy long black hair. armor made of thick hide, He wears an antler headpiece and fur-lined leather shoulder pads. He's holding a heavy hunting bow strung taut, crouched pose, savage, intense. frozen tundra cliffs, simple background. blue reflection on the ice."
    },
    {
        "id": "I23",
        "tag": "a_satyr_woman_with_small_curled_horns_and_unruly_chestnut_curls",
        "sha1": "92b7d2e00d",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A satyr woman with small curled horns and unruly chestnut curls. armor made of polished wood, She wears a bronze ivy band and knotted root shoulder guards. She's holding a carved wooden flute in one hand, loose casual pose, teasing, joyful. open sunny glade, simple background. green reflection on the bronze."
    },
    {
        "id": "I24",
        "tag": "a_construct_man_with_blank_brass_faceplate",
        "sha1": "66faaa372d",
        "text": "Western comics style, bold ink outlines, hatched shadows, upper body portrait. A construct man with blank brass faceplate. armor made of solid gold, He wears a bolted iron halo and enormous heavy cube shoulder pads. He's holding a massive flat-headed maul rested on ground, static pose, unfeeling, neutral. tiled temple floor, simple background. orange reflection on the gold."
    }
]

for p in STAGE7_CANDIDATES:
    calc = hashlib.sha1(p["text"].encode("utf-8")).hexdigest()[:10]
    assert calc == p["sha1"], f"SHA mismatch on {p['id']}"
