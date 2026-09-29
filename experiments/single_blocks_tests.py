# -*- coding: utf-8 -*-
"""T1, T2, T3 of docs/prereg_single_blocks_identifiability.md. Writes data/single_blocks_T*.csv. No render."""
import csv, itertools, random, statistics, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent; DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_single_blocks as S

plan = G.read_csv(S.PLAN); meas = {r["file"]: r for r in G.read_csv(S.CACHE)}
cloud, feats, mu, sd = G.load_cloud(); G.resolve_cloud_sha(cloud)
Z = lambda row: np.array(G.z_of([float(row[c]) for c in feats], mu, sd))
base = {r["prompt_id"]: r["expected_filename"] for r in plan if r["arm"] == "baseline"}
D = {}
for r in plan:
    if r["arm"] == "perturbation":
        D[(int(r["block_idx"]), r["sign"], r["prompt_id"])] = Z(meas[r["expected_filename"]]) - Z(meas[base[r["prompt_id"]]])
cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
rng = random.Random(20260929)

def identif(M):
    n = len(M); diag = sum(1 for i in range(n) if int(np.argmax(M[i])) == i)
    top3 = sum(1 for i in range(n) if i in np.argsort(-M[i])[:3])
    nb = sum(1 for i in range(n) if abs(int(np.argmax(M[i])) - i) <= 1)
    return diag, top3, nb

def perm_null(A, B, reps=10000):
    """A[i], B[j]: per-block vectors (or lists of per-prompt-pair vectors). Shuffle B's labels."""
    out = []
    idx = list(range(len(B)))
    for _ in range(reps):
        rng.shuffle(idx)
        M = np.array([[cs(A[i], B[idx[j]]) for j in range(len(B))] for i in range(len(A))])
        out.append(identif(M)[0])
    return out

rows = []
print("T1 — la firma di un blocco, vista su un'altra immagine, somiglia a se stessa piu' che agli altri 27?")
for sign in ("pos", "neg"):
    pairs = list(itertools.combinations(S.PROMPTS, 2))
    def cs(i_vecs, j_vecs):  # mean over prompt pairs, both directions
        return statistics.fmean(cos(i_vecs[a], j_vecs[b]) for a, b in pairs for (a, b) in ((a, b), (b, a)))
    V = [{p: D[(b, sign, p)] for p in S.PROMPTS} for b in S.BLOCKS]
    M = np.array([[cs(V[i], V[j]) for j in S.BLOCKS] for i in S.BLOCKS])
    diag, top3, nb = identif(M)
    null = perm_null(V, V, reps=2000)
    p95 = sorted(null)[int(0.95 * len(null))]; pv = (1 + sum(x >= diag for x in null)) / (1 + len(null))
    print(f"  {sign}: identificabili {diag}/28 (caso ~1; perm 95° = {p95}; p = {pv:.4f}) | nella top-3 {top3}/28 | a meno di un vicino {nb}/28")
    print(f"       diagonale media {np.mean(np.diag(M)):+.3f}  fuori diagonale media {(M.sum()-np.trace(M))/(28*27):+.3f}")
    for b in S.BLOCKS:
        rows.append({"test": "T1", "sign": sign, "block": b, "self": M[b, b], "row_max_block": int(np.argmax(M[b])),
                     "row_max": float(M[b].max()), "identifiable": int(np.argmax(M[b])) == b})
    rows.append({"test": "T1_summary", "sign": sign, "block": "all", "self": diag, "row_max_block": p95,
                 "row_max": pv, "identifiable": diag > p95})
# per-block identifiability line
for sign in ("pos", "neg"):
    ok = [str(r["block"]) for r in rows if r["test"] == "T1" and r["sign"] == sign and r["identifiable"]]
    print(f"  blocchi identificabili ({sign}): {', '.join(ok) or 'nessuno'}")

# ---------------- T2: replication vs benchmark_profondita (P01, 0.200, seeds 42/777/1337)
print("\nT2 — replica: atlante (0.350, seme 2718281) contro profondita (0.200, semi 42/777/1337), stesso P01")
prof = {r["file"]: r for r in csv.DictReader(open(DATA / "style_features_profondita.csv", encoding="utf-8"))}
cb = {str(o["seed"]): np.array(o["z"]) for o in cloud if o["sha"] == "52e5b19ca6" and o["file"].startswith("P01_baseline")}
seeds = [s for s in ("42", "777", "1337") if s in cb]
print(f"  baseline P01 disponibili nella nuvola ai semi di profondita: {seeds}")
P = {}
for b in S.BLOCKS:
    for sign in ("pos", "neg"):
        vs = []
        for s in seeds:
            fn = f"P01_blk{b:02d}{sign}_0.200_krea2_seed{s}_00001_.png"
            if fn in prof:
                vs.append(Z(prof[fn]) - cb[s])
        if vs: P[(b, sign)] = sum(vs) / len(vs)
for sign in ("pos", "neg"):
    if not all((b, sign) in P for b in S.BLOCKS):
        print(f"  {sign}: profondita incompleta, saltato"); continue
    A = [D[(b, sign, "P01_blacksmith")] for b in S.BLOCKS]; B = [P[(b, sign)] for b in S.BLOCKS]
    M = np.array([[cos(A[i], B[j]) for j in S.BLOCKS] for i in S.BLOCKS])
    diag, top3, nb = identif(M)
    def cs(a, b): return cos(a, b)
    null = perm_null(A, B, reps=10000)
    p95 = sorted(null)[int(0.95 * len(null))]; pv = (1 + sum(x >= diag for x in null)) / (1 + len(null))
    ok = [b for b in S.BLOCKS if int(np.argmax(M[b])) == b]
    print(f"  {sign}: identificabili {diag}/28 (perm 95° = {p95}; p = {pv:.4f}) | top-3 {top3}/28 | a meno di un vicino {nb}/28 | blocchi: {ok}")
    print(f"       diagonale media {np.mean(np.diag(M)):+.3f}  fuori diagonale {(M.sum()-np.trace(M))/(28*27):+.3f}")
    for b in S.BLOCKS:
        rows.append({"test": "T2", "sign": sign, "block": b, "self": M[b, b], "row_max_block": int(np.argmax(M[b])),
                     "row_max": float(M[b].max()), "identifiable": b in ok})
    rows.append({"test": "T2_summary", "sign": sign, "block": "all", "self": diag, "row_max_block": p95, "row_max": pv, "identifiable": diag > p95})

# ---------------- T3
print("\nT3 — cos(Δ+, Δ−) per blocco, media sui 3 prompt (−1 = un solo asse a due poli)")
t3 = [statistics.fmean(cos(D[(b, 'pos', p)], D[(b, 'neg', p)]) for p in S.PROMPTS) for b in S.BLOCKS]
print("  " + "  ".join(f"{b:02d}:{v:+.2f}" for b, v in zip(S.BLOCKS, t3)))
for b, v in zip(S.BLOCKS, t3): rows.append({"test": "T3", "sign": "", "block": b, "self": v, "row_max_block": "", "row_max": "", "identifiable": ""})
G.write_csv(DATA / "single_blocks_tests.csv", rows)
