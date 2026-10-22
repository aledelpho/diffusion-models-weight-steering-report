# C108 result — the gender word's pull toward anime does not generalise; a four-panel page keeps its genre under L06

2026-10-22. Pre-registration `docs/prereg_te_gender.md` (e4f51c8, before any render). Renders by Antigravity
(`docs/RENDERS_2026-10-21_te_gender.md`): 96, gates 2 of 2 pixel-identical. Keys and pages committed after the renders,
before any label (77a8ebd). Alessandro's labels committed as downloaded: single pictures (fbab295, 86), pages (9deb49a,
18). **The pairs were not labelled:** Alessandro judged the question unclear, not answerable with certainty; that
reported measure is missing. Rules: `experiments/te_gender.py --rules` → `data/te_gender_tests.csv`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| 0 — plain pictures Western comic | 4 of 4 for all 10 prompts; 32 of 32 plain panels | all kept |
| **A — other characters** (anime nb − original, L06) | pooled 0.33 − 0.00 = **+0.33**; positive in **1 of 3** (D1 +0.00, O4 +0.00, T7 +1.00) | **not shown on other characters** |
| **B — short prompts, species** | anime elf 0.12 − human 0.00 = +0.12 | not the species alone |
| **B — short prompts, gender** | anime nb 0.12 − female 0.00 = +0.12 | **not the gender word alone** |
| **C — inside one picture** | anime nb panels 0.00 − female panels 0.00 = **+0.00**; 16 of 16 pages with four panels | **no split inside one picture** |
| reported | L06 pages with one genre in all four panels: 8 of 8, all Western comic; test–retest 6 of 6 (single), 2 of 2 (pages) | — |

Tallies under L06: D1 realistic 4 / 4 with either word; O4 realistic 4 / 4 with either; T7 original cartoon 1,
comic 1, realistic 2, non-binary anime 4. Short prompts: SEN painting 3, anime 1; SEF painting 3, other 1; SHN and SHF
painting 4 each.

## What the pictures show (looked at, Claude, after the rules, conditions known; sheets `scratch/c108_{A,B,C}.jpg`, not committed)

* **A.** Under L06 "non-binary" does not change the genre of the dwarf or the half-orc (both photographs, as in C73);
  it changes **who** is drawn: the non-binary dwarf becomes a bearded man, the non-binary half-orc a young man, where
  the original words give women. The non-binary tiefling becomes a silver-haired young anime man in 4 of 4; the original
  tiefling an old man between anime and photograph.
* **B.** Under L06 the short prompts all become digital paintings of a generic young person; the elves keep their
  pointed ears, the humans become ordinary men and women.
* **C.** Under L06 the comic pages stay comic pages: four panels, ink and flat colour. The change is in the content,
  and it looks the same in all four panels: hoods and cloaks gone, a grey-blue background, a lighter-skinned young woman
  with long hair and the feather earring, pointed ears mostly gone. The four panels become much the same person.
  This is Claude's reading with the conditions known, not a blind answer.

## Reading

* C107's "the gender word decides" holds for the elf rogue's description (and, here, the tiefling's), not as a
  general rule: on the dwarf and the half-orc "non-binary" changes the drawn sex under L06, not the genre, and in short
  prompts L06 sends every variant to painting. The destination depends on the whole description, not on one word.
* A four-panel page is protected: the page-layout prompt holds the genre (0 of 32 edited panels changed genre), while
  the content change of L06 still happens, and it looks alike across panels. This fits page 31: one fixed edit, one
  recognisable change; here the change is visible without the genre switch that accompanies it in single portraits.
* L06's content change is again "toward a generic person": lighter skin, younger, fewer fantasy traits (C75, C107).

## Limits

One edit, four seeds, one observer who knew the hypothesis. The pairs measure is missing. Panel ↔ description by
position in the prompt; in the edited pages the descriptions are hard to tell apart, which may be why the pairs question
could not be answered. The anime label for the tiefling is one character.
