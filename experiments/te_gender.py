"""C108 - does the gender word decide where L06 sends the style beyond the elf rogue, in short prompts, and inside one
four-panel picture? (docs/prereg_te_gender.md). Written 2026-10-21 with the pre-registration, before any C108 render.
Renders authorised by Alessandro on 2026-10-21 ("Sono curioso di fare quell'esperimento ... con meno parole, e
mettendo tutte e quattro le descrizioni nella stessa immagine").

  python te_gender.py --selftest
  python te_gender.py --plan             # data/te_gender_plan.csv (committed: do not re-run)
  python te_gender.py --queue --first 2  # the two gate renders
  python te_gender.py --gate             # both equal to existing renders pixel for pixel
  python te_gender.py --queue
  python te_gender.py --count            # expected 96 missing 0 []
  python te_gender.py --rules            # once the keys and labels exist

Block A - other characters: D1 dwarf, O4 half-orc (female), T7 tiefling (male), each with its gender word and with
"non-binary" in its place. Block B - short prompts: "Western comics style, portrait of a {non-binary|female}
{elf|human}." Block C - one comic page, four panels, the four C107 long descriptions (EN, EF, HN, HF), in two orders.
Every prompt plain and with L06 MLP doubled (ArthemyKrea2CLIPTuner, Real Value, x(1+d)), at the C52 phase-C seeds.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_gender_plan.csv"
KEY_S, LAB_S = DATA / "te_gender_key_single.csv", DATA / "te_gender_labels_single.csv"
KEY_P, LAB_P = DATA / "te_gender_key_panels.csv", DATA / "te_gender_labels_panels.csv"
KEY_Q, LAB_Q = DATA / "te_gender_key_pairs.csv", DATA / "te_gender_labels_pairs.csv"
TESTS = DATA / "te_gender_tests.csv"
FOLDER = "benchmark_te_gender"
SEEDS = ["2645751", "3316624", "3605551", "4123105"]
L06 = json.dumps({"layers.6.mlp.gate_proj.weight": 1.0, "layers.6.mlp.up_proj.weight": 1.0,
                  "layers.6.mlp.down_proj.weight": 1.0})
CONDS = {"plain": "", "L06": L06}
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
       "width": "1024", "height": "1280"}
A_CHARS = {"D1": ("D1_dwarf_paladin", "female paladin mountain dwarf", "non-binary paladin mountain dwarf"),
           "O4": ("O4_halforc_fighter", "female fighter half-orc", "non-binary fighter half-orc"),
           "T7": ("T7_tiefling_bard", "male bard tiefling", "non-binary bard tiefling")}
B_VARIANTS = {"SEN": "non-binary elf", "SEF": "female elf", "SHN": "non-binary human", "SHF": "female human"}
E2_SUBJECT = "non-binary rogue wood elf"
C_DESC = {"EN": "non-binary rogue wood elf", "EF": "female rogue wood elf", "HN": "non-binary rogue human",
          "HF": "female rogue human"}
C_ORDERS = {"O1": ["EN", "EF", "HN", "HF"], "O2": ["HF", "HN", "EF", "EN"]}
PANEL_POS = ["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
SPECIES = {"SEN": "elf", "SEF": "elf", "SHN": "human", "SHF": "human", "EN": "elf", "EF": "elf", "HN": "human", "HF": "human"}
GENDER = {"SEN": "nb", "SEF": "female", "SHN": "nb", "SHF": "female", "EN": "nb", "EF": "female", "HN": "nb", "HF": "female"}
GATES = {("D1", "plain", "2645751"): ("benchmark_portraits/phase_c", "D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png"),
         ("D1", "L06", "2645751"): ("benchmark_te_characters", "D1_dwarf_paladin_L06_mlp_p1.00_krea2_seed2645751_00001_.png")}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def char_texts():
    t = {}
    for r in rd(DATA / "te_characters_plan.csv"):
        t.setdefault(r["char"], r["prompt_text"])
    return t


def text_A(c, word):
    ch, orig, nb = A_CHARS[c]
    t = char_texts()[ch]; assert t.count(orig) == 1, (c, orig)
    return t if word == "orig" else t.replace(orig, nb)


def text_B(v):
    return f"Western comics style, portrait of a {B_VARIANTS[v]}."


def e2_desc(v):
    t = char_texts()["E2_elf_rogue"].split("\n", 1)[1]
    t = t.replace(" white background, simple background.", "").rstrip(".")
    assert t.count(E2_SUBJECT) == 1
    return t.replace(E2_SUBJECT, C_DESC[v])


def text_C(order):
    panels = " ".join(f"Panel {i + 1} ({PANEL_POS[i]}): {e2_desc(v)}." for i, v in enumerate(C_ORDERS[order]))
    return ("Western comics style. Comic book page layout, single image divided into four equal rectangular panels by "
            "thick bold black borders, a close-up portrait in each panel. " + panels +
            " High quality, ultra-detailed comic illustration.")


def make_plan():
    rows = []
    def add(block, item, word, cond, seed, text):
        prefix = f"{block}_{item}_{word}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "block": block, "item": item, "word": word, "cond": cond, "seed": seed,
                     "te_granular_json": CONDS[cond], "vectors_override": "", "prompt_text": text,
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    for (c, cond, s) in GATES:
        add("A", c, "orig", cond, s, text_A(c, "orig"))
    for s in SEEDS:
        for cond in CONDS:
            for c in A_CHARS:
                for w in ("orig", "nb"):
                    if not (w == "orig" and (c, cond, s) in GATES):
                        add("A", c, w, cond, s, text_A(c, w))
            for v in B_VARIANTS:
                add("B", v, "-", cond, s, text_B(v))
            for o in C_ORDERS:
                add("C", o, "-", cond, s, text_C(o))
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = TP.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(first):
    n = 0
    for r in rd(PLAN)[: first or None]:
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def _im(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def gate():
    ok = True
    for r in rd(PLAN)[:2]:
        folder, name = GATES[(r["item"], r["cond"], r["seed"])]
        d = int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(c47.IMG_ROOT / folder / name)).max())
        print(f"{r['expected_filename']} vs {folder}/{name}: max abs diff {d}")
        ok = ok and d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


# ---------------------------------------------------------------- rules (fixed with the pre-registration)

def anime(rows):
    return sum(r["genre"] == "anime" for r in rows) / len(rows) if rows else float("nan")


def first_showings(key, lab):
    L = {r["id"]: r for r in lab}
    return [{**k, **{x: L[k["id"]][x] for x in L[k["id"]] if x != "id"}} for k in key
            if str(k["repeat"]) == "0" and k["id"] in L]


def retest(key, lab, fields):
    L = {r["id"]: r for r in lab}; g = {}
    for k in key:
        if k["id"] in L:
            g.setdefault(k["file"], []).append(tuple(L[k["id"]][f] for f in fields))
    same = [len(set(v)) == 1 for v in g.values() if len(v) == 2]
    return f"{sum(same)}/{len(same)} identical"


def rules(ks, ls, kp, lp, kq, lq):
    out = []
    pics = first_showings(ks, ls)
    # rule 0: plain pictures Western comic in >= 3 of 4 per prompt
    ok = {}
    for blk, items in (("A", [(c, w) for c in A_CHARS for w in ("orig", "nb")]), ("B", [(v, "-") for v in B_VARIANTS])):
        for it, w in items:
            pl = [p for p in pics if p["block"] == blk and p["item"] == it and p["word"] == w and p["cond"] == "plain"]
            n = sum(p["genre"] == "fumetto" for p in pl); ok[(it, w)] = n >= 3
            out.append({"rule": f"0_plain_{it}_{w}", "value": f"{n}/{len(pl)} fumetto", "verdict": "kept" if ok[(it, w)] else "excluded"})
    # rule A
    ed = [p for p in pics if p["block"] == "A" and p["cond"] == "L06"]
    per, nbs, ors = [], [], []
    for c in A_CHARS:
        if not (ok[(c, "orig")] and ok[(c, "nb")]):
            continue
        nb = [p for p in ed if p["item"] == c and p["word"] == "nb"]; o = [p for p in ed if p["item"] == c and p["word"] == "orig"]
        nbs += nb; ors += o; per.append(anime(nb) - anime(o))
        out.append({"rule": f"A_{c} (reported)", "value": f"anime non-binary {anime(nb):.2f} - original {anime(o):.2f} = {anime(nb) - anime(o):+.2f}", "verdict": "-"})
    if len(per) < 2:
        out.append({"rule": "A_other_characters", "value": "not testable", "verdict": "not testable"})
    else:
        diff = anime(nbs) - anime(ors); pos = sum(d > 0 for d in per)
        out.append({"rule": "A_other_characters", "value": f"pooled {anime(nbs):.2f} - {anime(ors):.2f} = {diff:+.2f}; positive in {pos} of {len(per)}",
                    "verdict": "non-binary pulls toward anime on other characters" if diff >= 0.40 and pos >= 2 else "not shown on other characters"})
    # rule B
    eb = [p for p in pics if p["block"] == "B" and p["cond"] == "L06" and ok[(p["item"], "-")]]
    for name, key, a, b, lab in (("B_species", SPECIES, "elf", "human", "the species decides"),
                                 ("B_gender", GENDER, "nb", "female", "the gender word decides")):
        x = [p for p in eb if key[p["item"]] == a]; y = [p for p in eb if key[p["item"]] == b]
        if not (x and y):
            out.append({"rule": name, "value": "not testable", "verdict": "not testable"}); continue
        d = anime(x) - anime(y)
        out.append({"rule": name, "value": f"anime {a} {anime(x):.2f} (n {len(x)}) - {b} {anime(y):.2f} (n {len(y)}) = {d:+.2f}",
                    "verdict": lab if d >= 0.50 else "not " + lab.replace("decides", "alone")})
    for v in B_VARIANTS:
        t = {}
        for p in pics:
            if p["block"] == "B" and p["item"] == v and p["cond"] == "L06":
                t[p["genre"]] = t.get(p["genre"], 0) + 1
        out.append({"rule": f"B_L06_{v} (reported)", "value": json.dumps(t, sort_keys=True), "verdict": "-"})
    # rule C: panels
    pages = first_showings(kp, lp)
    good = [p for p in pages if p["four"] == "si"]
    out.append({"rule": "C0_four_panels", "value": f"{len(good)} of {len(pages)} pages with four panels", "verdict": "-"})
    panels = []
    for p in good:
        for i, v in enumerate(C_ORDERS[p["item"]]):
            panels.append({"cond": p["cond"], "desc": v, "genre": p[f"g{i + 1}"]})
    plain_ok = [q for q in panels if q["cond"] == "plain"]
    out.append({"rule": "C0_plain_panels", "value": f"{sum(q['genre'] == 'fumetto' for q in plain_ok)}/{len(plain_ok)} fumetto", "verdict": "-"})
    ep = [q for q in panels if q["cond"] == "L06"]
    nb = [q for q in ep if GENDER[q["desc"]] == "nb"]; fe = [q for q in ep if GENDER[q["desc"]] == "female"]
    if not (nb and fe):
        out.append({"rule": "C_gender_in_one_picture", "value": "not testable", "verdict": "not testable"})
    else:
        d = anime(nb) - anime(fe)
        out.append({"rule": "C_gender_in_one_picture", "value": f"anime non-binary panels {anime(nb):.2f} (n {len(nb)}) - female {anime(fe):.2f} (n {len(fe)}) = {d:+.2f}",
                    "verdict": "the same split inside one picture" if d >= 0.50 else "no split inside one picture"})
        el = [q for q in ep if SPECIES[q["desc"]] == "elf"]; hu = [q for q in ep if SPECIES[q["desc"]] == "human"]
        out.append({"rule": "C_species (reported)", "value": f"anime elf {anime(el):.2f} - human {anime(hu):.2f} = {anime(el) - anime(hu):+.2f}", "verdict": "-"})
        same_page = [len({p[f"g{i}"] for i in range(1, 5)}) == 1 for p in good if p["cond"] == "L06"]
        out.append({"rule": "C_one_genre_per_page (reported)", "value": f"{sum(same_page)}/{len(same_page)} L06 pages with one genre in all panels", "verdict": "-"})
    # pairs (reported)
    pr = first_showings(kq, lq)
    sc = {"stesso": 1.0, "simile": 0.5, "diversi": 0.0}
    vals = [sc[p["answer"]] for p in pr if p["answer"] in sc]
    out.append({"rule": "C_pairs_same_change (reported)", "value": f"mean {sum(vals) / len(vals):.2f} (n {len(vals)}; same 1, similar 0.5, different 0)" if vals else "no answers",
                "verdict": "-"})
    out.append({"rule": "retest_single (reported)", "value": retest(ks, ls, ["genre"]), "verdict": "-"})
    out.append({"rule": "retest_panels (reported)", "value": retest(kp, lp, ["g1", "g2", "g3", "g4"]), "verdict": "-"})
    return out


def selftest():
    for c in A_CHARS:
        assert "non-binary" in text_A(c, "nb") and text_A(c, "orig").startswith("Western comics style")
    for o in C_ORDERS:
        t = text_C(o); assert t.count("Panel ") == 4 and "white background" not in t, t
    print(text_B("SHF")); print(text_C("O1")[:240], "...", len(text_C("O1").split()), "words")
    # synthetic labels: non-binary -> anime, female -> pittura, everything plain fumetto
    ks, ls, kp, lp = [], [], [], []
    i = 0
    for s in SEEDS:
        for cond in CONDS:
            for c in A_CHARS:
                for w in ("orig", "nb"):
                    i += 1; ks.append({"id": f"S{i:03d}", "block": "A", "item": c, "word": w, "cond": cond, "seed": s, "repeat": "0", "file": f"a{i}"})
                    ls.append({"id": f"S{i:03d}", "genre": "fumetto" if cond == "plain" else ("anime" if w == "nb" else "pittura")})
            for v in B_VARIANTS:
                i += 1; ks.append({"id": f"S{i:03d}", "block": "B", "item": v, "word": "-", "cond": cond, "seed": s, "repeat": "0", "file": f"b{i}"})
                ls.append({"id": f"S{i:03d}", "genre": "fumetto" if cond == "plain" else ("anime" if GENDER[v] == "nb" else "pittura")})
            for o in C_ORDERS:
                i += 1; kp.append({"id": f"Q{i:03d}", "block": "C", "item": o, "word": "-", "cond": cond, "seed": s, "repeat": "0", "file": f"c{i}"})
                g = {f"g{j + 1}": ("fumetto" if cond == "plain" else ("anime" if GENDER[v] == "nb" else "pittura")) for j, v in enumerate(C_ORDERS[o])}
                lp.append({"id": f"Q{i:03d}", "four": "si", **g})
    res = {r["rule"]: r for r in rules(ks, ls, kp, lp, [], [])}
    assert res["A_other_characters"]["verdict"].startswith("non-binary pulls"), res["A_other_characters"]
    assert res["B_gender"]["verdict"] == "the gender word decides" and res["B_species"]["verdict"].startswith("not")
    assert res["C_gender_in_one_picture"]["verdict"] == "the same split inside one picture"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "gate", "count", "selftest", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.gate: gate()
    if a.count: count()
    if a.selftest: selftest()
    if a.rules:
        res = rules(rd(KEY_S), rd(LAB_S), rd(KEY_P), rd(LAB_P), rd(KEY_Q) if KEY_Q.exists() else [], rd(LAB_Q) if LAB_Q.exists() else [])
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["rule", "value", "verdict"]); w.writeheader(); w.writerows(res)
        for r in res:
            print(f"{r['rule']:34s} {r['value']:80s} {r['verdict']}")
