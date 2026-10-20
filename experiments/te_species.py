"""C107 - is it the subject that decides where L06 sends the style? Species against gender on the elf rogue
(docs/prereg_te_species.md). Written 2026-10-20 with the pre-registration, before any C107 render. Renders
authorised by Alessandro on 2026-10-20 ("Dammi la direttiva per antigravity per lanciare quei render").

  python te_species.py --selftest
  python te_species.py --plan             # data/te_species_plan.csv (already committed: do not re-run)
  python te_species.py --queue --first 2  # the two gate renders
  python te_species.py --gate             # both must equal the existing renders pixel for pixel
  python te_species.py --queue
  python te_species.py --count            # expected 40 missing 0 []
  python te_species.py --rules            # once data/te_species_key.csv and data/te_species_labels.csv exist

The E2 elf rogue of C52/C65 ("Western comics style, close-up portrait, frontal view." frame), with only the subject
phrase "non-binary rogue wood elf" changed: species elf / human x gender non-binary / female, plus Alessandro's
female human ranger. Plain encoder, and L06 MLP doubled (ArthemyKrea2CLIPTuner, Real Value, granular_json x(1+d)),
at the four C52 phase-C seeds.
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_species_plan.csv"
KEY = DATA / "te_species_key.csv"
LABELS = DATA / "te_species_labels.csv"
TESTS = DATA / "te_species_tests.csv"
FOLDER = "benchmark_te_species"
CHAR = "E2_elf_rogue"
SUBJECT = "non-binary rogue wood elf"
VARIANTS = {"EN": "non-binary rogue wood elf", "EF": "female rogue wood elf", "HN": "non-binary rogue human",
            "HF": "female rogue human", "RF": "female ranger human"}
SPECIES = {"EN": "elf", "EF": "elf", "HN": "human", "HF": "human"}
GENDER = {"EN": "nb", "EF": "female", "HN": "nb", "HF": "female"}
SEEDS = ["2645751", "3316624", "3605551", "4123105"]
L06 = json.dumps({"layers.6.mlp.gate_proj.weight": 1.0, "layers.6.mlp.up_proj.weight": 1.0,
                  "layers.6.mlp.down_proj.weight": 1.0})
CONDS = {"plain": "", "L06": L06}
SET = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
       "width": "1024", "height": "1280"}
GATES = {("EN", "plain", "2645751"): ("benchmark_portraits/phase_c", "E2_elf_rogue_baseline_krea2_seed2645751_00001_.png"),
         ("EN", "L06", "2645751"): ("benchmark_te_characters", "E2_elf_rogue_L06_mlp_p1.00_krea2_seed2645751_00001_.png")}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def base_text():
    for r in rd(DATA / "te_characters_plan.csv"):
        if r["char"] == CHAR:
            return r["prompt_text"]
    raise SystemExit("E2 text not found")


def variant_text(v):
    t = base_text()
    assert t.count(SUBJECT) == 1, "subject phrase must occur once"
    return t.replace(SUBJECT, VARIANTS[v])


def make_plan():
    rows = []
    def add(block, v, cond, seed):
        prefix = f"{v}_{cond}_krea2_seed{seed}"
        rows.append({"row": len(rows), "block": block, "variant": v, "cond": cond, "seed": seed,
                     "te_granular_json": CONDS[cond], "vectors_override": "", "prompt_text": variant_text(v),
                     "output_prefix": prefix, "expected_filename": f"{prefix}_00001_.png", **SET})
    for (v, c, s) in GATES:
        add("gate", v, c, s)
    for s in SEEDS:
        for v in VARIANTS:
            for c in CONDS:
                if (v, c, s) not in GATES:
                    add("main", v, c, s)
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
        folder, name = GATES[(r["variant"], r["cond"], r["seed"])]
        d = int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(c47.IMG_ROOT / folder / name)).max())
        print(f"{r['expected_filename']} vs {folder}/{name}: max abs diff {d}")
        ok = ok and d == 0
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


# ---------------------------------------------------------------- rules (fixed with the pre-registration)

def share(rows, genre):
    return sum(r["genre"] == genre for r in rows) / len(rows) if rows else float("nan")


def rules(key, labels):
    """key: id, variant, cond, seed, repeat. labels: id, genre, ears (si/no). First showings only."""
    lab = {r["id"]: r for r in labels}
    pics = []
    for k in key:
        if str(k["repeat"]) == "1" or k["id"] not in lab or not lab[k["id"]]["genre"]:
            continue
        pics.append({**k, "genre": lab[k["id"]]["genre"], "ears": lab[k["id"]].get("ears", "")})
    out = []
    plain_ok = {}
    for v in VARIANTS:
        pl = [p for p in pics if p["variant"] == v and p["cond"] == "plain"]
        plain_ok[v] = sum(p["genre"] == "fumetto" for p in pl) >= 3
        out.append({"rule": f"0_plain_{v}", "value": f"{sum(p['genre'] == 'fumetto' for p in pl)}/{len(pl)} fumetto",
                    "verdict": "kept" if plain_ok[v] else "excluded (plain not Western comic)"})
    ed = [p for p in pics if p["cond"] == "L06" and p["variant"] in SPECIES and plain_ok[p["variant"]]]
    elf = [p for p in ed if SPECIES[p["variant"]] == "elf"]; hum = [p for p in ed if SPECIES[p["variant"]] == "human"]
    nb = [p for p in ed if GENDER[p["variant"]] == "nb"]; fe = [p for p in ed if GENDER[p["variant"]] == "female"]
    if not (elf and hum):
        r1 = None; out.append({"rule": "1_species", "value": "not testable", "verdict": "not testable"})
    else:
        r1 = share(elf, "anime") - share(hum, "anime")
        out.append({"rule": "1_species", "value": f"anime elf {share(elf, 'anime'):.2f} (n {len(elf)}) - human {share(hum, 'anime'):.2f} (n {len(hum)}) = {r1:+.2f}",
                    "verdict": "the species decides" if r1 >= 0.50 else "not the species alone"})
    if not (nb and fe):
        r2 = None; out.append({"rule": "2_gender", "value": "not testable", "verdict": "not testable"})
    else:
        r2 = share(nb, "anime") - share(fe, "anime")
        out.append({"rule": "2_gender", "value": f"anime non-binary {share(nb, 'anime'):.2f} (n {len(nb)}) - female {share(fe, 'anime'):.2f} (n {len(fe)}) = {r2:+.2f}",
                    "verdict": "the gender word decides" if r2 >= 0.50 else "not the gender word alone"})
    if elf and hum:
        rr = share(hum, "realist") - share(elf, "realist")
        out.append({"rule": "3_realism_species (reported)", "value": f"realistic human {share(hum, 'realist'):.2f} - elf {share(elf, 'realist'):.2f} = {rr:+.2f}", "verdict": "-"})
    for v in VARIANTS:
        pl = [p for p in pics if p["variant"] == v and p["cond"] == "L06"]
        tally = {}
        for p in pl:
            tally[p["genre"]] = tally.get(p["genre"], 0) + 1
        out.append({"rule": f"4_L06_{v} (reported)", "value": json.dumps(tally, sort_keys=True), "verdict": "-"})
    rf = [p for p in pics if p["variant"] == "RF" and p["cond"] == "L06"]
    out.append({"rule": "5_ranger_prediction (reported)", "value": f"realistic {sum(p['genre'] == 'realist' for p in rf)}/{len(rf)}",
                "verdict": "Claude's prediction (>= 3 of 4 realistic) " + ("met" if sum(p["genre"] == "realist" for p in rf) >= 3 else "not met")})
    for sp in ("elf", "human"):
        grp = [p for p in ed if SPECIES[p["variant"]] == sp]
        for e in ("si", "no"):
            g = [p for p in grp if p["ears"] == e]
            out.append({"rule": f"6_ears_{sp}_{e} (reported)", "value": f"anime {sum(p['genre'] == 'anime' for p in g)}/{len(g)}, realistic {sum(p['genre'] == 'realist' for p in g)}/{len(g)}", "verdict": "-"})
    rep = {}
    for k in key:
        if k["id"] in lab and lab[k["id"]]["genre"]:
            rep.setdefault((k["variant"], k["cond"], k["seed"]), []).append(lab[k["id"]]["genre"])
    same = [len(set(g)) == 1 for g in rep.values() if len(g) == 2]
    out.append({"rule": "7_retest (reported)", "value": f"{sum(same)}/{len(same)} identical", "verdict": "-"})
    return out


def selftest():
    for v in VARIANTS:
        t = variant_text(v)
        assert t.startswith("Western comics style, close-up portrait, frontal view.\n") and VARIANTS[v] in t
        assert len(t) - len(base_text()) == len(VARIANTS[v]) - len(SUBJECT)
    print(variant_text("HF").split("\n")[1][:80])
    key, lab = [], []
    i = 0
    for v in VARIANTS:
        for c in CONDS:
            for s in SEEDS:
                i += 1; key.append({"id": f"P{i:02d}", "variant": v, "cond": c, "seed": s, "repeat": "0"})
                g = "fumetto" if c == "plain" else ("anime" if SPECIES.get(v) == "elf" else "realist")
                lab.append({"id": f"P{i:02d}", "genre": g, "ears": "si" if SPECIES.get(v) == "elf" else "no"})
    res = {r["rule"]: r for r in rules(key, lab)}
    assert res["1_species"]["verdict"] == "the species decides", res["1_species"]
    assert res["2_gender"]["verdict"] == "not the gender word alone", res["2_gender"]
    assert res["5_ranger_prediction (reported)"]["verdict"].endswith("met")
    lab2 = [{**l, "genre": "anime" if l["genre"] != "fumetto" else "fumetto"} for l in lab]
    res2 = {r["rule"]: r for r in rules(key, lab2)}
    assert res2["1_species"]["verdict"] == "not the species alone"
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
        res = rules(rd(KEY), rd(LABELS))
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["rule", "value", "verdict"]); w.writeheader(); w.writerows(res)
        for r in res:
            print(f"{r['rule']:32s} {r['value']:70s} {r['verdict']}")
