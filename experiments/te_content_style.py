"""C104 - content shared, style own? Re-blinding C103's renders with two questions, plus CSD (docs/prereg_te_content_style.md).
Written 2026-10-19 with the pre-registration, before the blind pass and any CSD vector.

  python te_content_style.py --selftest
  python te_content_style.py --page        # Text2Img/occhio_C104.html, data/te_content_style_key.csv (no GPU)
  python te_content_style.py --csd         # GPU: CSD vectors of C103's test renders -> data/te_content_style_csd.npz
  python te_content_style.py --rules       # numpy: data/te_content_style_tests.csv
"""
import argparse, csv, itertools, os, random, statistics, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_depth_control2 as T2
import te_depth_control as T

DATA = HERE.parent / "data"
KEY = DATA / "te_content_style_key.csv"
LABELS = DATA / "te_content_style_labels.csv"
CSD = DATA / "te_content_style_csd.npz"
TESTS = DATA / "te_content_style_tests.csv"
PROMPTS, SEEDS = T2.PROMPTS, T2.SEEDS
NOT_MATCHED = {"R09a"}
OPTS = T2.OPTS


def page():
    from eye_grid_page import thumb, build
    R = T.img_root(); root = str(R); rng = random.Random(10404)
    have = {(r["char"], r["seed"], r["cond"]) for r in T2.rd(T2.PLAN) if r["block"] == "main"}
    A, B = T2.units_spec(have); base = A + B; rng.shuffle(base)
    reps = rng.sample(base, 6); order = list(base)
    for r in reps:
        i = order.index(r); order.insert(rng.randint(min(i + 10, len(order)), len(order)), r)
    f = lambda p, c, s: thumb(str(R / T2.FOLDER / f"{p}_{c}_krea2_seed{s}_00001_.png"), root)
    key, units, seen = [], [], set()
    for n, u in enumerate(order, 1):
        kind, p, c, s0 = u; uid = f"W{n:02d}"
        key.append({"unit": uid, "kind": kind, "prompt": p, "cond": c, "seed": s0, "repeat": int(u in seen)}); seen.add(u)
        pairs = [(s, c) for s in SEEDS] if kind == "A" else [(s0, f"{c}{x}_t") for x in "abc"]
        rows = []
        for k, (s, cc) in enumerate(pairs, 1):
            a, b = f(p, "C0", s), f(p, cc, s)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=["unit", "kind", "prompt", "cond", "seed", "repeat"]); w.writeheader(); w.writerows(key)
    qs = [("content", "Il contenuto (soggetti, forme, oggetti, composizione) cambia nello stesso modo nelle tre coppie?", OPTS),
          ("style", "Lo stile (resa, tecnica, colori, tratto) cambia nello stesso modo nelle tre coppie?", OPTS)]
    build(os.path.join(root, "occhio_C104.html"), "C104 · contenuto e stile", units, qs, OPTS, "c104_labels_v1", "te_content_style_labels.csv")
    print("units", len(units), "->", os.path.join(root, "occhio_C104.html"))


def csd():
    from PIL import Image
    import metric_validation as MV
    R = T.img_root(); m = MV.Models(vqa=False); keys, vecs = [], []
    for r in T2.rd(T2.PLAN):
        keys.append(f"{r['char']}|{r['seed']}|{r['cond']}")
        vecs.append(np.asarray(m.csd_vec(Image.open(R / T2.FOLDER / r["expected_filename"]).convert("RGB")), dtype=np.float32))
    np.savez_compressed(CSD, keys=np.array(keys), vecs=np.stack(vecs)); print("wrote", CSD, len(keys))


def load(path):
    z = np.load(path)
    return {tuple(k.split("|")): v.astype(np.float64) for k, v in zip(z["keys"], z["vecs"])}


def stats(V, L):
    cos = T._cos
    dl = lambda p, s, c: V[(p, s, c)] - V[(p, s, "C0")]
    rnd = [f"R{L}{x}" for x in "abc" if f"R{L}{x}" not in NOT_MATCHED]
    K = [T.kappa_seeds(V, p, f"{n}_t", SEEDS) for p in PROMPTS for n in rnd]; K = [k for k in K if k is not None]
    rho = []
    for p in PROMPTS:
        for s in SEEDS:
            D = [dl(p, s, f"{n}_t") for n in rnd if (p, s, f"{n}_t") in V]
            if len(D) >= 2:
                rho.append(statistics.mean(cos(a, b) for a, b in itertools.combinations(D, 2)))
    e = f"L{L}_t"
    Ke = [T.kappa_seeds(V, p, e, SEEDS) for p in PROMPTS]; Ke = [k for k in Ke if k is not None]
    eps = [statistics.mean(cos(dl(p, s, e), dl(p, s, f"{n}_t")) for n in rnd) for p in PROMPTS for s in SEEDS
           if (p, s, e) in V and all((p, s, f"{n}_t") in V for n in rnd)]
    mk, mr = statistics.median(K), statistics.median(rho)
    return {"kappa": mk, "rho": mr, "r": mr / mk if mk > 0 else float("inf"), "kappa_edit": statistics.median(Ke), "eps": statistics.median(eps)}


def rules(VD, VC, labels=None, key=None):
    out, blind, reps = [], {}, []
    if labels and key:
        for r in labels:
            k = key[r["unit"]]; tag = (k["kind"], k["prompt"], k["cond"], k["seed"])
            ans = {q: (r.get(q) or "").strip() for q in ("content", "style")}
            if not any(ans.values()):
                continue
            if tag in blind:
                reps.append((blind[tag], ans)); continue
            blind[tag] = ans
    def share(kind, cond_test, q):
        vis = [a[q] for (kd, p, c, s), a in blind.items() if kd == kind and cond_test(c) and a[q] in ("stesso", "diversi")]
        return (sum(x == "stesso" for x in vis) / len(vis) if vis else None), len(vis)
    for L in ("09", "26"):
        d, c = stats(VD, L), stats(VC, L)
        out.append({"test": f"Layer {L} computed (reported)", "value": f"DINOv2 kappa {d['kappa']:.2f} rho {d['rho']:.2f} r {d['r']:.2f} | CSD kappa {c['kappa']:.2f} rho {c['rho']:.2f} r {c['r']:.2f} | edit: DINOv2 kappa {d['kappa_edit']:.2f} eps {d['eps']:.2f}; CSD kappa {c['kappa_edit']:.2f} eps {c['eps']:.2f}", "verdict": ""})
        if not blind:
            continue
        sc, nc = share("B", lambda x: x == f"R{L}", "content"); ss, ns = share("B", lambda x: x == f"R{L}", "style")
        b1 = None if nc < 4 else sc >= 0.60; c1 = d["r"] >= 0.50
        v1 = "not testable" if b1 is None else ("supported" if b1 and c1 else ("not supported" if not b1 and not c1 else "disagreement"))
        out.append({"test": f"Rule 1 layer {L}: content is the network's", "value": f"blind B content {sc if sc is None else round(sc, 2)} (n {nc}); DINOv2 r {d['r']:.2f}", "verdict": v1})
        b2 = None if ns < 4 else ss <= 0.30; c2 = c["r"] <= 0.25
        v2 = "not testable" if b2 is None else ("supported" if b2 and c2 else ("not supported" if not b2 and not c2 else "disagreement"))
        out.append({"test": f"Rule 2 layer {L}: style is the perturbation's own", "value": f"blind B style {ss if ss is None else round(ss, 2)} (n {ns}); CSD r {c['r']:.2f}", "verdict": v2})
        out.append({"test": f"Rule 3 layer {L}: content from the network, rendering from the perturbation", "value": "", "verdict": "supported" if v1 == v2 == "supported" else "not supported"})
        rnd = lambda x: x.startswith(f"R{L}") and x[:4] not in NOT_MATCHED
        ac, nac = share("A", rnd, "content"); ast, nas = share("A", rnd, "style")
        out.append({"test": f"Rule 4 layer {L}: A units of random pushes, same change across seeds (reported)", "value": f"content {ac if ac is None else round(ac, 2)} (n {nac}); style {ast if ast is None else round(ast, 2)} (n {nas})", "verdict": ""})
    if blind:
        ns = {}
        for (kd, p, c, s), a in blind.items():
            for q in ("content", "style"):
                ns[q] = ns.get(q, 0) + (a[q] == "nonsivede")
        out.append({"test": "Rule 4 'non si vede' (reported)", "value": f"content {ns['content']}, style {ns['style']}", "verdict": ""})
        if reps:
            out.append({"test": "Rule 4 test-retest (reported)", "value": f"content {sum(a['content'] == b['content'] for a, b in reps)}/{len(reps)}, style {sum(a['style'] == b['style'] for a, b in reps)}/{len(reps)}", "verdict": ""})
    return out


def selftest():
    rng = np.random.default_rng(0)
    def synth(shared):
        V = {}
        for p in PROMPTS:
            net = {L: rng.standard_normal(64) for L in ("09", "26")}; own = {c: rng.standard_normal(64) for c in T2.conds()}
            for s in SEEDS:
                b = rng.standard_normal(64); V[(p, s, "C0")] = b
                for c in T2.conds()[1:]:
                    V[(p, s, c)] = b + 1.5 * (net[c[1:3]] if shared else own[c]) + 0.4 * rng.standard_normal(64)
        return V
    VD, VC = synth(True), synth(False)
    have = set(VD); A, B = T2.units_spec(have)
    key, lab = {}, []
    for i, (kind, p, c, s) in enumerate(A + B):
        key[f"W{i}"] = {"kind": kind, "prompt": p, "cond": c, "seed": s}
        lab.append({"unit": f"W{i}", "content": "stesso", "style": "stesso" if kind == "A" else "diversi"})
    o = {x["test"].split(":")[0]: x["verdict"] for x in rules(VD, VC, lab, key)}
    assert o["Rule 1 layer 26"] == "supported" and o["Rule 2 layer 26"] == "supported" and o["Rule 3 layer 26"] == "supported", o
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "page", "csd", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.page: page()
    if a.csd: csd()
    if a.rules:
        lab = T2.rd(LABELS) if LABELS.exists() else None
        key = {r["unit"]: r for r in T2.rd(KEY)} if KEY.exists() else None
        out = rules(load(T2.VECS), load(CSD), lab, key)
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
