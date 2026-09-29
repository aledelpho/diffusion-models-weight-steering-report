# -*- coding: utf-8 -*-
"""H1-H5 of docs/prereg_late_blocks_render_controls.md (ff06640 + amendment 108f731). No render."""
import itertools, math, statistics, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent; DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_single_blocks as S

LABEL = {22: ("vividezza", "colorfulness_hs"), 23: ("saturazione", "sat"), 24: ("contrasto", "contrast"),
         25: ("texture", "lbp_entropy"), 26: ("sharpness", "fft_high_freq_share"), 27: ("focus", "focus_cv")}
MEAS = [LABEL[b][1] for b in range(22, 28)]
plan = G.read_csv(S.PLAN)
m = {r["file"]: r for r in G.read_csv(S.CACHE)}
for r in G.read_csv(DATA / "late_blocks_atlas_extra.csv"): m[r["file"]].update(r)
base = {r["prompt_id"]: r["expected_filename"] for r in plan if r["arm"] == "baseline"}
cell = {(int(r["block_idx"]), r["sign"], r["prompt_id"]): r["expected_filename"] for r in plan if r["arm"] == "perturbation"}
v = lambda fn, k: float(m[fn][k])

# swings S[b][k] = mean over prompts of (m(+) - m(-)) / m(0)
S_ = {b: {k: statistics.fmean((v(cell[(b, "pos", p)], k) - v(cell[(b, "neg", p)], k)) / v(base[p], k)
                              for p in S.PROMPTS) for k in MEAS} for b in S.BLOCKS}
sdk = {k: statistics.pstdev([S_[b][k] for b in S.BLOCKS]) for k in MEAS}
Z = {b: {k: S_[b][k] / sdk[k] for k in MEAS} for b in S.BLOCKS}

def mw_greater(x, y):  # exact one-sided P(U >= u_obs), x expected larger
    allv = x + y; n = len(x); u = sum((a > c) + 0.5 * (a == c) for a in x for c in y)
    cnt = tot = 0
    for comb in itertools.combinations(range(len(allv)), n):
        xs = [allv[i] for i in comb]; ys = [allv[i] for i in range(len(allv)) if i not in comb]
        uu = sum((a > c) + 0.5 * (a == c) for a in xs for c in ys); tot += 1; cnt += uu >= u - 1e-12
    return u, cnt / tot

# H4 data
prof = G.read_csv(DATA / "late_blocks_profondita.csv")
pb = {r["prompt"]: r for r in prof if r["sign"] == "baseline"}
pc = {(int(r["block"]), r["sign"], r["prompt"]): r for r in prof if r["sign"] != "baseline"}

print("H1 — due poli sul proprio asse (segni opposti di + e − rispetto al baseline, su 3/3 prompt)")
res = {}
for b in range(22, 28):
    word, k = LABEL[b]
    dp = [v(cell[(b, "pos", p)], k) - v(base[p], k) for p in S.PROMPTS]
    dn = [v(cell[(b, "neg", p)], k) - v(base[p], k) for p in S.PROMPTS]
    h1 = sum(a * c < 0 for a, c in zip(dp, dn))
    # direction of + relative to baseline, and of the swing
    dirs = ["+" if a > 0 else "−" for a in dp]
    # H2a: own measure the largest |z| among the six?
    own = max(MEAS, key=lambda kk: abs(Z[b][kk])) == k
    top = max(MEAS, key=lambda kk: abs(Z[b][kk]))
    # H2b: rank of block b among 28 on its own measure (|z|)
    rank = 1 + sum(abs(Z[bb][k]) > abs(Z[b][k]) for bb in S.BLOCKS if bb != b)
    # H4: same direction arm by arm on profondita
    h4 = 0; h4d = []
    for p_at, p_pr in (("P01_blacksmith", "P01"),):
        pass
    for p in ("P01", "P02"):
        pa = "P01_blacksmith" if p == "P01" else None
        for sign in ("pos", "neg"):
            d_pr = float(pc[(b, sign, p)][k]) - float(pb[p][k])
            # reference direction from the atlas: its mean over the three prompts for that arm
            d_at = statistics.fmean(v(cell[(b, sign, pp)], k) - v(base[pp], k) for pp in S.PROMPTS)
            ok = d_pr * d_at > 0; h4 += ok; h4d.append(f"{p}{'+' if sign=='pos' else '−'}{'✓' if ok else '✗'}")
    res[b] = dict(word=word, k=k, h1=h1, own=own, top=top, rank=rank, h4=h4, h4d=h4d, dirs=dirs,
                  swing=S_[b][k], z=Z[b][k])
    print(f"  {b} {word:11} {k:20} H1 {h1}/3  (+ va {''.join(dirs)})  swing {S_[b][k]:+.3f} z {Z[b][k]:+.2f}")
print("\nH2 — specificita'")
k2 = 0
for b in range(22, 28):
    r = res[b]; k2 += r["own"]
    zs = "  ".join(f"{kk[:10]} {Z[b][kk]:+.2f}" for kk in MEAS)
    print(f"  {b} {r['word']:11} (a) proprio asse il massimo fra sei: {'SI' if r['own'] else 'no, e ' + r['top']:26} (b) rango {r['rank']:2}/28 | z: {zs}")
p2 = sum(math.comb(6, i) * (1/6)**i * (5/6)**(6-i) for i in range(k2, 7))
print(f"  H2(a): {k2}/6 (caso 1/6 ciascuno), binomiale esatta p = {p2:.4f}")
print("\nH3 — soggetto preservato: somiglianza d'impianto, blocchi 22-27 contro 0-21")
ls = {b: statistics.fmean(v(cell[(b, s, p)], "layout_sim") for s in ("pos", "neg") for p in S.PROMPTS) for b in S.BLOCKS}
late = [ls[b] for b in range(22, 28)]; early = [ls[b] for b in range(0, 22)]
u, p3 = mw_greater(late, early)
print("  " + " ".join(f"{b}:{ls[b]:.3f}" for b in S.BLOCKS))
print(f"  media 22-27 {statistics.fmean(late):.3f}  vs 0-21 {statistics.fmean(early):.3f}  | Mann-Whitney U={u:.0f}, p = {p3:.4f}")
print("\nH4 — replica su profondita' (±0.200, seme 42), stessa direzione del braccio nell'atlante")
for b in range(22, 28): print(f"  {b} {res[b]['word']:11} {res[b]['h4']}/4  {' '.join(res[b]['h4d'])}")
print("\nH5 — l'attributo vive nella regione? |z| medio 22-27 contro 0-21, per misura")
h5 = {}
for k in MEAS:
    a = [abs(Z[b][k]) for b in range(22, 28)]; c = [abs(Z[b][k]) for b in range(0, 22)]
    u, p = mw_greater(a, c); h5[k] = p
    print(f"  {k:20} 22-27 {statistics.fmean(a):.2f}  0-21 {statistics.fmean(c):.2f}  p = {p:.4f}")
print("\nVERDETTI")
rows = []
for b in range(22, 28):
    r = res[b]
    strong = r["h1"] == 3 and r["own"] and r["h4"] >= 3
    partly = r["h1"] == 3 and r["h4"] >= 3 and not r["own"]
    lever = r["h1"] == 3 and r["h4"] >= 3 and h5[r["k"]] <= 0.05
    sv = "SUPPORTATA" if strong else ("in parte" if partly else "non supportata")
    lv = "SUPPORTATA" if lever else "non supportata"
    print(f"  {b} {r['word']:11}  lettura forte: {sv:15} | lettura a leve: {lv}")
    rows.append({"block": b, "label": r["word"], "measure": r["k"], "H1": r["h1"], "H2a_own_max": r["own"],
                 "H2a_top": r["top"], "H2b_rank": r["rank"], "H4": r["h4"], "H5_p": h5[r["k"]],
                 "swing": r["swing"], "z": r["z"], "strong": sv, "lever": lv})
G.write_csv(DATA / "late_blocks_tests.csv", rows)
print(f"\n(H3 generale: p = {p3:.4f})")
