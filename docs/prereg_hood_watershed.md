# C54 — the archer's half-formed hood: which existing edits complete it, which break it

2026-10-06. Exploratory; criteria fixed before any image is labelled. No new render.

## Why

The archer prompt (`P3_archerforest`) asks for "a dark grey hood obscuring some of her hair" and
"brown hair". At seed 3141592 the baseline draws the hood only halfway: a grey fragment on one side,
hair on the other. Alessandro calls such cases *watersheds*: the model is pulled between two
requests and finishes neither shape, and edits that unbalance the model can tip it one way. In C53
he noticed that block 23 also repaired this hood. The question: across every render that already
exists, which edits complete the hood, which leave it, which remove it?

## Material

All distinct renders of `P3_archerforest` (duplicates identical to the pixel counted once):
* seed 3141592 — `benchmark_single_blocks_v3` (baseline + 65 single-block arms, every block, one
  or two doses per sign, from the v3 atlas) and the C47 arms not in it (blk23 −0.45 and −0.15,
  "colorful", "muted"): 70 images;
* seed 4669201 — C47: baseline, blk23 at five doses, "colorful", "muted": 8 images.
78 images. Seed 4669201 is the control: if its baseline hood is complete, it asks whether edits
break a hood that was fine.

## Labelling (eye first)

One image at a time, random order, no file name, no condition: the whole frame and an enlarged crop
of the upper half. Question: **"Il cappuccio è…"** — *completo* (one continuous hood over the top
of the head) / *a metà* (it starts and stops, or melts into the hair) / *assente* / *non riesco a
dirlo*. 12 images are shown a second time, at random places in the order, to measure
self-agreement. If fewer than 10 of the 12 repeats get the same label, the labels are reported as
unreliable and no table is built on them (pitfall 89).

Observer: Alessandro. He has seen some of these renders before; he does not see the condition.
After he has answered, Claude labels the same crops in a fresh shuffled order, without file names,
as an agreement check only.

## What is reported (descriptive)

* For each image: its label and its condition. At seed 3141592 an edit **completes** the hood if
  labelled *completo* where the baseline is *a metà*; **removes** it if *assente*. At seed 4669201
  an edit **breaks** it if labelled *a metà* or *assente* where the baseline is *completo*.
* Per block and sign: completed / unchanged / removed, on a 28-block strip.
* Expectation written now, to be checked, not tested: middle blocks (05–14), which rewrite content
  (page 21), change the hood's state more often than the end blocks (00–01, 21–27), which change
  surface properties.

Code: `experiments/hood_watershed.py` (`--page`, `--tally --answers <csv>`). Key: `data/hood_key.csv`.

## Amendment 1 — 2026-10-06, before any label

Alessandro, looking at the first images, noted that a hood can be whole but lowered: the girl's head
and hair are fully uncovered and the hood lies behind it. "Completo" would hide that case, which is
another way out of the watershed (the hair wins, the hood survives). The labels become: *completo
(in testa)* / *abbassato* / *a metà* / *assente* / *non riesco a dirlo*. In the tally, *abbassato*
is its own outcome: at seed 3141592 an edit **lowers** the hood; at seed 4669201 too. Everything else
is unchanged; the page is rebuilt with the same items and order, and any answers given to the first
version are discarded.
