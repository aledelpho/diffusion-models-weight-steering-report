"""C68 — how large are the regions of the prompt that a text-encoder edit pushes the same way?
(docs/prereg_te_regions.md). Written 2026-10-12, before any C68 encode. No images.

  python te_regions.py --plan            # data/te_regions_plan.csv (20 C65 edits x 5 word orders + 7 characters, full, last 3 taps)
  python te_regions.py --queue --first 2 # the gate pair (one edit encoded twice)
  python te_regions.py --queue           # everything else
  python te_regions.py --count
  python te_regions.py --gate            # determinism + agreement with the C67 diff files; must print GATE PASS
  python te_regions.py --analyze         # data/te_regions_*.csv and the tests (Claude)
  python te_regions.py --selftest

Change of an edit = edited conditioning (C68, last three taps: layers 29, 32, 35 — read by every edit of the set) minus
the C67 baseline of the same prompt (stored in full). Residual = change minus its mean over the prompt's positions
(the shared push C67 found). All units are built from the decoded tokens with fixed rules (`units()`).
"""
import argparse, csv, itertools, json, re, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_conditioning as T

DATA = HERE.parent / "data"
PLAN = DATA / "te_regions_plan.csv"
FOLDER = "benchmark_te_regions"
TAPS = [9, 10, 11]                         # tap indices (layers 29, 32, 35)
ORDERS = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter", "G5_gnome_wizard", "H3_halfling_druid",
         "R6_dragonborn_cleric", "T7_tiefling_bard"]
SHORT = ["D1", "E2", "O4", "G5", "H3", "R6", "T7"]
FLOOR = 2 ** -11
KMAX = 40


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def out_path(set_, pid, cond):
    return c47.IMG_ROOT / FOLDER / set_ / f"{pid}_{cond}.npz"


# ---------------------------------------------------------------- plan / queue
def make_plan():
    c67 = [r for r in T.rd(T.PLAN) if r["mode"] == "diff" and r["set"] in ("order", "chars") and r["prompt_id"] in ORDERS + CHARS]
    rows = []
    for r in c67:
        rows.append({"row": len(rows), "set": r["set"], "prompt_id": r["prompt_id"], "cond": r["cond"], "unit": r["unit"],
                     "te_granular_json": r["te_granular_json"], "prompt_text": r["prompt_text"],
                     "out": str(out_path(r["set"], r["prompt_id"], r["cond"]))})
    g = dict(rows[0]); g["row"] = len(rows); g["cond"] = rows[0]["cond"] + "_again"; g["out"] = str(out_path(g["set"], g["prompt_id"], g["cond"]))
    rows.insert(1, g)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("plan rows:", len(rows))


def workflow(r):
    wf = T.workflow({"prompt_text": r["prompt_text"], "te_granular_json": r["te_granular_json"], "out": r["out"],
                     "mode": "full", "baseline": ""})
    wf["90"]["inputs"]["taps"] = ",".join(map(str, TAPS))
    return wf


def queue(first):
    n = 0
    for r in rd(PLAN)[: first or None]:
        if Path(r["out"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def count():
    rows = rd(PLAN)
    miss = [r["out"] for r in rows if not out_path(r["set"], r["prompt_id"], r["cond"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


# ---------------------------------------------------------------- data
def base(set_, pid):
    z = np.load(T.out_path(set_, pid, "baseline"))
    return z["cond"].astype(np.float32)[:, TAPS], z["ids"]


def change(set_, pid, cond):
    E = np.load(out_path(set_, pid, cond))["cond"].astype(np.float32)
    B, ids = base(set_, pid)
    return E - B, ids


def gate():
    r0, r1 = rd(PLAN)[0], rd(PLAN)[1]
    a = np.load(out_path(r0["set"], r0["prompt_id"], r0["cond"])); b = np.load(out_path(r1["set"], r1["prompt_id"], r1["cond"]))
    same = np.array_equal(a["cond"], b["cond"])
    print("determinism:", "identical" if same else "DIFFERENT")
    worst = 0.0
    for r in rd(PLAN)[2:12]:
        D, _ = change(r["set"], r["prompt_id"], r["cond"])
        Bv, _ = base(r["set"], r["prompt_id"])
        rel = np.linalg.norm(D, axis=-1) / (np.linalg.norm(Bv, axis=-1) + 1e-6)
        ref = np.load(T.out_path(r["set"], r["prompt_id"], r["cond"]))["rel"][:, TAPS]
        worst = max(worst, float(np.abs(rel - ref).max()))
    print(f"agreement with the C67 diff files (10 edits, last 3 taps): max |rel - rel_C67| = {worst:.6f} (limit {2 * FLOOR:.6f})")
    ok = same and worst <= 2 * FLOOR
    print("GATE", "PASS" if ok else "FAIL - stop")
    return ok


# ---------------------------------------------------------------- units
def norm_text(s):
    return re.sub(r"[^a-z0-9\-]+", " ", s.lower()).strip()


def units(ids, inv, kind):
    """Groups of positions. kind: 'clause' (runs ending at , . : or newline), 'sentence' (runs ending at . or :),
    'word' (T.words). Template tokens (<|...|> and what follows <|im_end|>) are dropped."""
    pieces = [inv.get(int(i), "") for i in ids]
    end = next((p for p, s in enumerate(pieces) if s.startswith("<|im_end")), len(pieces))
    if kind == "word":
        ws = [w for w in T.words(ids[:end], inv) if norm_text(w["word"])]
        return [{"text": norm_text(w["word"]), "pos": w["pos"]} for w in ws]
    stop = r"[,.:\n]" if kind == "clause" else r"[.:\n]"
    out, cur = [], []
    for p in range(end):
        cur.append(p)
        if re.search(stop, pieces[p]):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    res = []
    for u in out:
        t = norm_text("".join(pieces[p] for p in u))
        if t:
            res.append({"text": t, "pos": u})
    return res


def residual(D, ids, inv):
    end = next((p for p in range(len(ids)) if inv.get(int(ids[p]), "").startswith("<|im_end")), len(ids))
    X = D[:end].reshape(end, -1)
    return X - X.mean(0, keepdims=True)


def cosm(X):
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    Y = X / n
    return Y @ Y.T


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


# ---------------------------------------------------------------- analysis
def size_curve(R, cl_of):
    """Mean cosine of residuals at token distance k (1..KMAX); and, for k <= 8, the same split into pairs inside one
    clause and pairs across clauses."""
    C = cosm(R); n = len(R)
    curve, same, diff = [], [], []
    for k in range(1, KMAX + 1):
        i = np.arange(n - k); v = C[i, i + k]
        curve.append(float(v.mean()) if len(v) else float("nan"))
        if k <= 8:
            s = cl_of[i] == cl_of[i + k]
            same.append(float(v[s].mean()) if s.any() else np.nan); diff.append(float(v[~s].mean()) if (~s).any() else np.nan)
    c1 = curve[0]
    half = next((k for k, v in enumerate(curve, 1) if v <= c1 / 2), KMAX + 1)
    w = [(a - b) for a, b in zip(same, diff) if not (np.isnan(a) or np.isnan(b))]
    return curve, half, float(np.mean(w)) if w else float("nan")


def analyze():
    inv = T.vocab()
    edits = []
    for r in rd(PLAN):
        if not r["cond"].endswith("_again") and r["cond"] not in edits:
            edits.append(r["cond"])
    size_rows, curves = [], []
    order_dis, frame_vec = {}, {}
    for k in edits:
        halves, bnd = [], []
        # word orders
        U = {}
        for v in ORDERS:
            D, ids = change("order", v, k); R = residual(D, ids, inv)
            cl = units(ids, inv, "clause"); cl_of = np.full(len(R), -1)
            for j, u in enumerate(cl):
                cl_of[[p for p in u["pos"] if p < len(R)]] = j
            curve, half, b = size_curve(R, cl_of); halves.append(half); bnd.append(b); curves.append({"cond": k, "prompt": v, **{f"k{i+1}": round(c, 4) for i, c in enumerate(curve)}})
            for kind in ("sentence", "clause", "word"):
                seen = {}
                for u in units(ids, inv, kind):
                    key = (u["text"], seen.get(u["text"], 0)); seen[u["text"]] = key[1] + 1
                    U.setdefault(kind, {}).setdefault(key, {})[v] = R[[p for p in u["pos"] if p < len(R)]].mean(0)
        dis = {}
        for kind, by in U.items():
            vals = [np.mean([cos(m[a], m[b]) for a, b in itertools.combinations(ORDERS, 2)]) for m in by.values() if len(m) == 5]
            dis[kind] = (1 - float(np.mean(vals)), len(vals))
        order_dis[k] = dis
        # characters: the frame shared by all seven prompts
        F = {}
        for ch in CHARS:
            D, ids = change("chars", ch, k); R = residual(D, ids, inv)
            cl = units(ids, inv, "clause"); cl_of = np.full(len(R), -1)
            for j, u in enumerate(cl):
                cl_of[[p for p in u["pos"] if p < len(R)]] = j
            curve, half, b = size_curve(R, cl_of); halves.append(half); bnd.append(b); curves.append({"cond": k, "prompt": ch, **{f"k{i+1}": round(c, 4) for i, c in enumerate(curve)}})
            F[ch] = {u["text"]: R[[p for p in u["pos"] if p < len(R)]].mean(0) for u in cl}
        shared = sorted(set.intersection(*[set(f) for f in F.values()]))
        frame_vec[k] = {ch: np.concatenate([F[ch][t] for t in shared]) for ch in CHARS}
        size_rows.append({"cond": k, "half_life_tokens_median": float(np.median(halves)), "same_minus_cross_clause": round(float(np.nanmean(bnd)), 4),
                          "order_disagreement_sentence": round(dis["sentence"][0], 4), "order_disagreement_clause": round(dis["clause"][0], 4),
                          "order_disagreement_word": round(dis["word"][0], 4), "n_clauses_matched": dis["clause"][1], "frame_units": len(shared),
                          "frame_agreement_chars": round(float(np.mean([cos(frame_vec[k][a], frame_vec[k][b]) for a, b in itertools.combinations(CHARS, 2)])), 4)})
    for name, rows in (("te_regions_size.csv", size_rows), ("te_regions_curves.csv", curves)):
        with open(DATA / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    S = {r["cond"]: r for r in size_rows}
    res = []
    # H1: residual regions exist (replication of the elf observation on 12 new prompts)
    agree_prompt = {}
    for k in edits:
        vals = []
        for v in ORDERS:
            D, ids = change("order", v, k)
            cl = units(ids, inv, "clause")
            X = np.stack([D[[p for p in u["pos"]]].reshape(len(u["pos"]), -1).mean(0) for u in cl])
            C = cosm(X); vals.append(float(C[np.triu_indices(len(X), 1)].mean()))
        agree_prompt[k] = float(np.mean(vals))
    c67 = {r["cond"]: float(r["agree_orders"]) for r in rd(DATA / "te_conditioning_direction.csv")}
    nlow = sum(agree_prompt[k] < c67[k] for k in edits)
    res.append({"test": "H1 clauses of one prompt are pushed less alike than the whole prompt across orders", "n": len(edits),
                "value": f"{nlow}/{len(edits)} edits; median clause agreement {np.median(list(agree_prompt.values())):.3f}",
                "rule": ">= 16 of 20", "verdict": "supported" if nlow >= 16 else "not supported"})
    # H2: region boundaries follow the punctuation
    from scipy.stats import binomtest
    pos = sum(S[k]["same_minus_cross_clause"] > 0 for k in edits)
    p = binomtest(pos, len(edits), 0.5, alternative="greater").pvalue
    res.append({"test": "H2 at equal distance, tokens of the same clause are pushed more alike than across clauses", "n": len(edits),
                "value": f"{pos}/{len(edits)} edits, sign test p = {p:.4f}", "rule": ">= 15 of 20 and p < 0.05",
                "verdict": "supported" if pos >= 15 and p < 0.05 else "not supported"})
    # H3: word-order dependence lives in the clause residuals
    sc = {r["row"]: int(r["score_1_5"]) for r in rd(DATA / "te_order_grid_notes_alessandro.csv") if r["grid"] == "te_order_3141592" and r["score_1_5"]}
    ks = [k for k in edits if k in sc]
    for kind in ("clause", "sentence", "word"):
        rho, pv = T.spearman([S[k][f"order_disagreement_{kind}"] for k in ks], [sc[k] for k in ks])
        res.append({"test": f"H3 order disagreement of the {kind} residuals vs the 1-5 scores", "n": len(ks), "value": f"rho {rho:.3f}, p {pv:.4f}",
                    "rule": "rho >= 0.50 (clause decides; sentence and word reported)",
                    "verdict": ("supported" if rho >= 0.50 else "not supported") if kind == "clause" else "reported"})
    # H4: characters — the shared frame's residual
    eye = [x for x in rd(DATA / "te_characters_eye_joined.csv") if x["first"] == "1" and x["stessa"]]
    m = {"si": 2, "parte": 1, "no": 0}
    xs = [(S[x["cond"]]["frame_agreement_chars"], m[x["stessa"]]) for x in eye if x["cond"] in S]
    rho4, p4 = T.spearman([a for a, _ in xs], [b for _, b in xs])
    res.append({"test": "H4a frame residual agreement across characters vs 'same direction'", "n": len(xs), "value": f"rho {rho4:.3f}, p {p4:.4f}",
                "rule": "rho >= 0.40", "verdict": "supported" if rho4 >= 0.40 else "not supported"})
    pos_, neg_ = [], []
    for x in eye:
        fv = frame_vec.get(x["cond"])
        if fv is None:
            continue
        for ch, s in zip(CHARS, SHORT):
            v = cos(fv[ch], np.mean([fv[o] for o in CHARS if o != ch], axis=0))
            (neg_ if x[f"c_{s}"] == "diverso" else pos_ if x[f"c_{s}"] == "segue" else []).append(v)
    a = T.auc(pos_, neg_)
    res.append({"test": "H4b exceptions: a character's frame residual vs the other six, follows vs another way", "n": f"{len(pos_)}+{len(neg_)}",
                "value": f"AUC {a:.3f}", "rule": "AUC >= 0.70", "verdict": "supported" if a >= 0.70 else "not supported"})
    res.append({"test": "SIZE half-life of the residual similarity, tokens (median over edits; per edit = median over the 12 prompts)",
                "n": len(edits), "value": f"{np.median([S[k]['half_life_tokens_median'] for k in edits]):.1f} tokens "
                f"(range {min(S[k]['half_life_tokens_median'] for k in edits):.0f}-{max(S[k]['half_life_tokens_median'] for k in edits):.0f})",
                "rule": "reported (the answer to 'how large')", "verdict": "reported"})
    with open(DATA / "te_regions_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "n", "value", "rule", "verdict"]); w.writeheader(); w.writerows(res)
    for r in res:
        print(r)


def selftest():
    rng = np.random.default_rng(0)
    # residuals made of blocks of 6 tokens sharing a direction: half-life near the block size, boundary effect positive
    blocks = [rng.normal(size=32) for _ in range(10)]
    R = np.stack([blocks[i // 6] + rng.normal(size=32) * 0.3 for i in range(60)])
    R = R - R.mean(0)
    cl_of = np.array([i // 6 for i in range(60)])
    curve, half, b = size_curve(R, cl_of)
    assert 3 <= half <= 8 and b > 0.5, (half, b)
    inv = {1: "red", 2: " cat", 3: ",", 4: " blue", 5: " dog", 6: ".", 7: "<|im_end|>"}
    u = units(np.array([1, 2, 3, 4, 5, 6, 7]), inv, "clause")
    assert [x["text"] for x in u] == ["red cat", "blue dog"] and u[1]["pos"] == [3, 4, 5], u
    print("selftest ok, half-life", half, "boundary", round(b, 3))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "count", "gate", "analyze", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root"); ap.add_argument("--vocab")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.vocab: T.VOCAB = Path(a.vocab)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.count: count()
    if a.gate: gate()
    if a.analyze: analyze()
    if a.selftest: selftest()
