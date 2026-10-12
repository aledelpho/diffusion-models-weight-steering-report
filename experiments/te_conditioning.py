"""C67 — what does a text-encoder edit do to the conditioning Krea-2 reads, token by token? (docs/prereg_te_conditioning.md)
Written 2026-10-12, before any conditioning is computed. No images: ComfyUI runs only the text encoder and the
Krea2ConditioningProbe node (tools/comfyui_krea2_probe), which writes .npz files instead of renders.

  python te_conditioning.py --plan          # data/te_conditioning_plan.csv
  python te_conditioning.py --queue --first 2   # the two baselines of the elf, encoded twice (determinism gate)
  python te_conditioning.py --gate          # determinism and nulls; must print GATE PASS
  python te_conditioning.py --queue         # everything else (baselines first: "diff" rows need them)
  python te_conditioning.py --count
  python te_conditioning.py --logitlens     # GPU PC: top tokens per position for the "full" files (reads the TE weights)
  python te_conditioning.py --reduce        # data/te_conditioning_tokens.csv, te_conditioning_edits.csv (VM or PC)
  python te_conditioning.py --test          # the decision rules (Claude)
  python te_conditioning.py --selftest
"""
import argparse, csv, itertools, json, re, sys, urllib.request
from pathlib import Path, PureWindowsPath
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_conditioning_plan.csv"
TOKENS = DATA / "te_conditioning_tokens.csv"
EDITS = DATA / "te_conditioning_edits.csv"
LENS = DATA / "te_conditioning_logitlens.csv"
RESULT = DATA / "te_conditioning_tests.csv"
FOLDER = "benchmark_te_conditioning"
TAPS = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
VOCAB = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\comfy\text_encoders\qwen25_tokenizer")  # overridable
TE_WEIGHTS = Path(r"C:\StabilityMatrix-win-x64\Data\Models\TextEncoders\qwen3vl_4b_bf16.safetensors")   # overridable


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def out_path(set_, prompt_id, cond):
    return c47.IMG_ROOT / FOLDER / set_ / f"{prompt_id}_{cond}.npz"


# ---------------------------------------------------------------- plan
def make_plan():
    import te_characters as TC, portraits as P
    elf_text = next(r["prompt_text"] for r in rd(DATA / "te_pilot_plan.csv"))
    c65 = TC.select_edits()                                    # the 20 edits of C65: (L, part, d, cond)
    rows = []
    def add(set_, pid, text, cond, gj, mode, unit="", part="", dose=0.0, base_cond="baseline"):
        rows.append({"row": len(rows), "set": set_, "prompt_id": pid, "cond": cond, "unit": unit, "part": part, "dose": dose,
                     "mode": mode, "te_granular_json": gj, "prompt_text": text,
                     "out": str(out_path(set_, pid, cond)), "baseline": str(out_path(set_, pid, base_cond)) if mode == "diff" else ""})
    # gate: the elf baseline twice
    add("elf", "P1_elfbrawler", elf_text, "baseline", "", "full")
    add("elf", "P1_elfbrawler", elf_text, "baseline_again", "", "full")
    # other baselines
    OP = TC.order_prompts()
    for v in TC.ORDERS:
        add("order", v, OP[v], "baseline", "", "full")
    texts = {c: P.text({**P.CALIBRATION, **P.HELD_OUT}[c]) for c in TC.CHARS}
    texts[TC.WC] = f"{TC.WC_HEAD}\n{P.CALIBRATION[TC.WC_OF]} {P.TAIL}"
    for c, t in texts.items():
        add("chars", c, t, "baseline", "", "full")
    # elf: every C64 text-encoder edit (checks and main), as differences
    for r in rd(DATA / "te_pilot_plan.csv"):
        if r["te_granular_json"]:
            add("elf", "P1_elfbrawler", elf_text, r["cond"], r["te_granular_json"], "diff", r["unit"], r["part"], float(r["dose"]))
    # elf: the 20 C65 edits again, full (for the logit lens)
    for L, part, d, cond in c65:
        add("elf_full", "P1_elfbrawler", elf_text, cond, TP.gj_te(L, TC.PARTS[part], d), "full", f"L{L:02d}", part, d)
    # word order and characters: the 20 C65 edits
    for L, part, d, cond in c65:
        gj = TP.gj_te(L, TC.PARTS[part], d)
        for v in TC.ORDERS:
            add("order", v, OP[v], cond, gj, "diff", f"L{L:02d}", part, d)
        for c, t in texts.items():
            add("chars", c, t, cond, gj, "diff", f"L{L:02d}", part, d)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("plan rows:", len(rows), dict(Counter((r["set"], r["mode"]) for r in rows)))


def plan():
    return rd(PLAN)


def workflow(r):
    base = {"prompt_text": r["prompt_text"], "te_granular_json": r["te_granular_json"], "vectors_override": "",
            "seed": "1", "output_prefix": "unused", **{k: v for k, v in TP_SETTINGS.items()}}
    wf = TP.workflow(base)
    clip = wf["40"]["inputs"]["clip"]
    for k in ("40", "43", "42", "46", "61", "45", "48"):
        wf.pop(k, None)
    wf["90"] = {"class_type": "Krea2ConditioningProbe", "inputs": {"clip": clip, "text": r["prompt_text"], "out_path": r["out"],
                                                                    "mode": r["mode"], "baseline_path": r["baseline"]}}
    return wf


TP_SETTINGS = {"sampler": "euler_ancestral", "scheduler": "simple", "steps": "9", "cfg": "1.0", "denoise": "1.0",
               "width": "1024", "height": "1280"}


def queue(first):
    rows = plan()
    # baselines ("full" with cond baseline) before any "diff"
    rows = sorted(rows, key=lambda r: (r["mode"] != "full" or not r["cond"].startswith("baseline"), int(r["row"])))
    n = 0
    for r in rows[: first or None]:
        if Path(r["out"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def count():
    rows = plan()
    miss = [r["out"] for r in rows if not out_path(r["set"], r["prompt_id"], r["cond"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


FP16_FLOOR = 2 ** -11   # baselines are stored in float16: |b - fp16(b)| / |b| <= 2^-11 per position (amendment 1)


def gate():
    """Amendment 1 (2026-10-12): the baselines are stored in float16 and the diffs compare a float32 encode with them,
    so an unchanged encode reads as a relative change up to 2^-11, not 0. Gate: the two encodes of the baseline are
    identical; the two null edits (layer 35, visual tower) give bit-identical diff files (so the encoder output is the
    same in both) whose maximum is <= 2^-11; the active check (L02 MLP +1.00) is above 10 x 2^-11 everywhere it can
    reach (taps after layer 2)."""
    a = np.load(out_path("elf", "P1_elfbrawler", "baseline")); b = np.load(out_path("elf", "P1_elfbrawler", "baseline_again"))
    same = np.array_equal(a["cond"], b["cond"]) and np.array_equal(a["ids"], b["ids"])
    print("determinism:", "identical" if same else f"DIFFERENT max {np.abs(a['cond'].astype(np.float32) - b['cond'].astype(np.float32)).max()}")
    z = {c: np.load(out_path("elf", "P1_elfbrawler", c)) for c in ("CHK_null_L35_both_p1.00", "CHK_null_visual4_p1.00", "CHK_active_L02_mlp_p1.00")}
    n1, n2, act = z["CHK_null_L35_both_p1.00"], z["CHK_null_visual4_p1.00"], z["CHK_active_L02_mlp_p1.00"]
    nulls_equal = all(np.array_equal(n1[k], n2[k]) for k in ("rel", "cos", "dmean"))
    null_max = float(max(n1["rel"].max(), n2["rel"].max()))
    act_min = float(act["rel"][:, first_tap("L02"):].min())
    print(f"nulls bit-identical: {nulls_equal}; null max {null_max:.6f} (floor {FP16_FLOOR:.6f}); active min over reached taps {act_min:.4f}")
    ok = same and nulls_equal and null_max <= FP16_FLOOR and act_min > 10 * FP16_FLOOR
    print("GATE", "PASS" if ok else "FAIL - stop")
    return ok


# ---------------------------------------------------------------- tokens
def vocab():
    """id -> readable string, from the Qwen tokenizer files ComfyUI ships (byte-level BPE)."""
    v = json.load(open(VOCAB / "vocab.json", encoding="utf-8"))
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]; n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b); cs.append(256 + n); n += 1
    dec = {chr(c): b for b, c in zip(bs, cs)}
    inv = {}
    for s, i in v.items():
        try:
            inv[i] = bytes(dec[ch] for ch in s).decode("utf-8", errors="replace")
        except KeyError:
            inv[i] = s
    try:
        for i, t in json.load(open(VOCAB / "tokenizer_config.json", encoding="utf-8")).get("added_tokens_decoder", {}).items():
            inv[int(i)] = t["content"]
    except Exception:
        pass
    return inv


def words(ids, inv):
    """Group token positions into words (a token starting with a space or punctuation starts a new word)."""
    out, cur = [], None
    for p, i in enumerate(ids):
        s = inv.get(int(i), f"<{int(i)}>")
        new = cur is None or s.startswith(" ") or s.startswith("\n") or not s[:1].isalnum() or s.startswith("<|")
        if new:
            cur = {"word": s.strip(), "pos": [p]}; out.append(cur)
        else:
            cur["word"] += s; cur["pos"].append(p)
    return out


def first_tap(unit):
    """Index of the first tap that reads past an edit to layer L (tap k is the input of layer k)."""
    L = int(unit[1:]) if unit and unit[0] == "L" else 0
    return next((j for j, t in enumerate(TAPS) if t > L), len(TAPS))


def reduce():
    inv = vocab()
    tok_rows, edit_rows = [], []
    for r in plan():
        op = out_path(r["set"], r["prompt_id"], r["cond"])
        if r["mode"] != "diff" or not op.exists():
            continue
        z = np.load(op); rel = np.where(z["rel"] <= FP16_FLOOR, 0.0, z["rel"]); ids = z["ids"]   # amendment 1
        j0 = first_tap(r["unit"])
        reach = rel[:, j0:] if j0 < rel.shape[1] else rel[:, :0]
        per_pos = reach.mean(1) if reach.shape[1] else np.zeros(len(ids))
        ws = words(ids, inv)
        for w_ in ws:
            tok_rows.append({"set": r["set"], "prompt_id": r["prompt_id"], "cond": r["cond"], "word": w_["word"],
                             "first_pos": w_["pos"][0], "rel": round(float(per_pos[w_["pos"]].mean()), 5)})
        edit_rows.append({"set": r["set"], "prompt_id": r["prompt_id"], "cond": r["cond"], "unit": r["unit"], "part": r["part"],
                          "dose": r["dose"], "taps_reached": rel.shape[1] - j0, "mean_rel": round(float(per_pos.mean()), 5),
                          "max_rel": round(float(per_pos.max()), 5) if len(per_pos) else 0,
                          "top_words": " | ".join(f"{w_['word']}:{per_pos[w_['pos']].mean():.3f}"
                                                  for w_ in sorted(ws, key=lambda w_: -per_pos[w_["pos"]].mean())[:8])})
    for p, rows in ((TOKENS, tok_rows), (EDITS, edit_rows)):
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("reduce ok:", len(edit_rows), "edits,", len(tok_rows), "word rows")


# ---------------------------------------------------------------- logit lens (GPU PC)
def logitlens():
    """Project every tap of the 'full' files through the text encoder's own token embedding (Qwen3-4B ties input and
    output embeddings; the taps already carry the final norm) and keep the top-3 tokens per position and tap."""
    import torch
    from safetensors import safe_open
    with safe_open(str(TE_WEIGHTS), framework="pt") as f:
        name = next(k for k in f.keys() if k.endswith("embed_tokens.weight") and "visual" not in k)
        E = f.get_tensor(name).float().cuda()
    inv = vocab()
    rows = []
    for r in plan():
        if r["mode"] != "full" or r["set"] not in ("elf", "elf_full") or r["cond"] == "baseline_again":
            continue
        z = np.load(out_path(r["set"], r["prompt_id"], r["cond"])); c = torch.from_numpy(z["cond"].astype(np.float32)).cuda()
        top = (c @ E.T).topk(3, dim=-1).indices.cpu().numpy()      # (seq, 12, 3)
        for p in range(top.shape[0]):
            for j, t in enumerate(TAPS):
                rows.append({"cond": r["cond"], "pos": p, "tap": t, "token": inv.get(int(z["ids"][p]), ""),
                             "top3": " | ".join(inv.get(int(i), "") for i in top[p, j])})
    with open(LENS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("logit lens ok:", len(rows), "rows, embedding", name, tuple(E.shape))


# ---------------------------------------------------------------- rules
def spearman(x, y):
    from scipy.stats import spearmanr
    r = spearmanr(x, y); return float(r.statistic), float(r.pvalue)


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


STYLE_WORDS_CHARS = {"western", "comics", "style", "close-up", "portrait", "frontal", "view", "white", "background", "simple"}


def test():
    ed = rd(EDITS); tk = rd(TOKENS)
    res = []
    # E1: elf, total change vs 'how much it changed' (C64 phase 1, +-1.00)
    lab = {r["cond"]: r for r in rd(DATA / "te_pilot_phase1_joined.csv") if r["phase"] == "main"}
    order = {"nessuna": 0, "lieve": 1, "media": 2, "forte": 3, "testo": 4}
    xs = [(float(e["mean_rel"]), order[lab[e["cond"]]["entita"]], lab[e["cond"]]["stile"]) for e in ed
          if e["set"] == "elf" and e["cond"] in lab and lab[e["cond"]]["entita"] in order]
    rho, p = spearman([a for a, _, _ in xs], [b for _, b, _ in xs])
    a = auc([v for v, _, s in xs if s == "cambiato"], [v for v, _, s in xs if s == "inalterato"])
    res.append({"test": "E1 elf: conditioning change vs how much the picture changed", "n": len(xs), "rho": round(rho, 3), "p": round(p, 4),
                "auc_style_changed": round(a, 3), "rule": "rho >= 0.50", "verdict": "supported" if rho >= 0.50 else "not supported"})
    # E2: word order — does the same edit move the same words in every order?
    sc = {r["row"]: int(r["score_1_5"]) for r in rd(DATA / "te_order_grid_notes_alessandro.csv") if r["grid"] == "te_order_3141592" and r["score_1_5"]}
    prof = {}
    for t in tk:
        if t["set"] == "order":
            prof.setdefault(t["cond"], {}).setdefault(t["prompt_id"], {})
            prof[t["cond"]][t["prompt_id"]].setdefault(t["word"].lower(), []).append(float(t["rel"]))
    dis = {}
    for k, by in prof.items():
        common = set.intersection(*[set(v) for v in by.values()]) if len(by) == 5 else set()
        common = sorted(w for w in common if w)
        if len(common) < 10:
            continue
        vecs = {v: np.array([np.mean(by[v][w]) for w in common]) for v in by}
        cs = [spearman(vecs[a], vecs[b])[0] for a, b in itertools.combinations(sorted(vecs), 2)]
        dis[k] = 1 - float(np.mean(cs))
    ks = [k for k in sc if k in dis]
    rho2, p2 = spearman([dis[k] for k in ks], [sc[k] for k in ks]) if len(ks) > 4 else (float("nan"), float("nan"))
    res.append({"test": "E2 order: word-profile disagreement across orders vs 1-5 scores", "n": len(ks), "rho": round(rho2, 3), "p": round(p2, 4),
                "rule": "rho >= 0.50", "verdict": "supported" if rho2 >= 0.50 else "not supported"})
    # E3: characters — share of the change on the shared style words vs 'same direction'
    share = {}
    for t in tk:
        if t["set"] == "chars" and t["prompt_id"] != "D1W_dwarf_paladin_watercolor":
            s = share.setdefault(t["cond"], [0.0, 0.0])
            w = re.sub(r"[^a-z\-]", "", t["word"].lower())
            s[0 if w in STYLE_WORDS_CHARS else 1] += float(t["rel"])
    eye = [x for x in rd(DATA / "te_characters_eye_joined.csv") if x["first"] == "1" and x["stessa"]]
    m = {"si": 2, "parte": 1, "no": 0}
    xs3 = [(share[x["cond"]][0] / max(sum(share[x["cond"]]), 1e-9), m[x["stessa"]]) for x in eye if x["cond"] in share]
    rho3, p3 = spearman([a for a, _ in xs3], [b for _, b in xs3])
    res.append({"test": "E3 characters: share of change on shared style words vs 'same direction'", "n": len(xs3), "rho": round(rho3, 3),
                "p": round(p3, 4), "rule": "rho >= 0.40", "verdict": "supported" if rho3 >= 0.40 else "not supported"})
    with open(RESULT, "w", newline="", encoding="utf-8") as f:
        cols = sorted({k for r in res for k in r}, key=lambda k: ["test", "n", "verdict", "rule"].index(k) if k in ("test", "n", "verdict", "rule") else 9)
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(res)
    for r in res:
        print(r)


def selftest():
    inv = {1: "Western", 2: " comics", 3: " style", 4: ",", 5: " eye", 6: "patch", 7: "<|im_end|>"}
    ws = words([1, 2, 3, 4, 5, 6, 7], inv)
    assert [w["word"] for w in ws] == ["Western", "comics", "style", ",", "eyepatch", "<|im_end|>"], ws
    assert first_tap("L00") == 0 and first_tap("L02") == 1 and first_tap("L34") == 11 and first_tap("L35") == 12
    assert auc([2, 3], [0, 1]) == 1.0
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "gate", "count", "logitlens", "reduce", "test", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root"); ap.add_argument("--vocab"); ap.add_argument("--te-weights")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.vocab: VOCAB = Path(a.vocab)
    if a.te_weights: TE_WEIGHTS = Path(a.te_weights)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.gate: gate()
    if a.count: count()
    if a.logitlens: logitlens()
    if a.reduce: reduce()
    if a.test: test()
    if a.selftest: selftest()
