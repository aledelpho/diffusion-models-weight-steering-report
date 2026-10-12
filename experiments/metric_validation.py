"""C66 — which automatic measures reproduce Alessandro's eye on text-encoder edits? (docs/prereg_metric_validation.md)
Written 2026-10-12, before any measure is computed. No new renders: only images already judged by eye.

  python metric_validation.py --list        # data/metric_val_images.csv (every image the tests use)
  python metric_validation.py --smoke       # GPU PC: load the four models, embed 3 images, print shapes; nothing written
  python metric_validation.py --embed       # GPU PC: data/metric_val_emb.npz, metric_val_genre.csv, metric_val_vqa.csv
  python metric_validation.py --test        # the decision rules (Claude runs it)
  python metric_validation.py --selftest    # the rules on synthetic data

Models (fixed here): CSD-ViT-L (style; HF tomg-group-umd/CSD-ViT-L), DINOv2-large (content; facebook/dinov2-large),
CLIP ViT-L/14 zero-shot genre (openai/clip-vit-large-patch14), VQAScore with clip-flant5-xl (t2v_metrics).
"""
import argparse, csv, itertools, json, re, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47

DATA = HERE.parent / "data"
IMAGES = DATA / "metric_val_images.csv"
EMB = DATA / "metric_val_emb.npz"
GENRE = DATA / "metric_val_genre.csv"
VQA = DATA / "metric_val_vqa.csv"
RESULT = DATA / "metric_val_tests.csv"

GENRES = {  # class -> CLIP prompt
    "comic": "a western comic book illustration", "anime": "an anime illustration", "cartoon": "a cartoon",
    "oil": "an oil painting", "render3d": "a 3D render", "photo": "a photograph", "watercolor": "a watercolor painting"}
GENRE_RE = {  # Italian words in Alessandro's notes -> class
    "anime": r"anime|chibi", "cartoon": r"cartone|cartoon|animazione|saturday morning", "oil": r"\bolio\b",
    "render3d": r"\b3d\b|render", "photo": r"fotograf|fotorealis", "watercolor": r"acquerell", "comic": r"fumett"}
ELF_TRAITS = {  # trait -> (VQAScore text, Italian loss pattern in the notes)
    "antlers": ("a small pair of pale antlers", r"(pers[oae]|perde|manca|mancano|niente|no|senza)[^.]{0,25}\bcorn"),
    "eyepatch": ("an eyepatch over one eye", r"(pers[oae]|perde|manca|niente|no|senza)[^.]{0,20}\bbenda"),
    "fur": ("a fur collar", r"(pers[oae]|perde|manca|niente|no|senza)[^.]{0,25}pelliccia|pelliccia (è )?scompars"),
    "pauldron": ("a gold wood-textured pauldron", r"spall(accio|iera)[^.]{0,30}(sparit|diventa|manca)|(pers[oae]|perde|manca|niente|no)[^.]{0,20}spall"),
    "gauntlet": ("a heavy silver gauntlet", r"(?<!braccio )senza (il )?guanto metallico|(non ha più|manca|niente|no|perso|perde)[^.]{0,20}guanto"),
    "elf": ("pointed elf ears", r"non (è )?più un elf|non elfo|no elfo"),
    "tan": ("tan sun-kissed skin", r"pelle (pallida|chiara|non abbronzata|meno abbronzata)"),
}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


# ---------------------------------------------------------------- the images
def image_list():
    import te_pilot as TP, te_characters as TC
    rows = []
    add = lambda set_, item, cond, unit, seed, path: rows.append(
        {"set": set_, "item": item, "cond": cond, "unit": unit, "seed": seed, "path": str(path)})
    # S1: C64 phase 1 (elf, +-1.00) and its baseline
    plan = {r["cond"]: r for r in rd(DATA / "te_pilot_plan.csv")}
    add("elf", "base", "baseline", "", TP.SEED, TP.f("baseline", "benchmark_comic_form"))
    for r in rd(DATA / "te_pilot_phase1_joined.csv"):
        if r["phase"] == "main":
            add("elf", r["item"], r["cond"], r["unit"], TP.SEED, c47.IMG_ROOT / TP.FOLDER / plan[r["cond"]]["expected_filename"])
    # S2: C65 characters
    conds = TC.main_conds() if TC.PLAN.exists() else []
    for ch in TC.CHARS:
        for s in TC.SEEDS:
            add("chars", "", "baseline", ch, s, TC.path(ch, "baseline", s))
            for k in conds:
                add("chars", "", k, ch, s, TC.path(ch, k, s))
    # S3: C65 word order
    for v in TC.ORDERS:
        for s in TC.ORDER_SEEDS:
            add("order", "", "baseline", v, s, TC.order_path(v, "baseline", s))
            for k in conds:
                add("order", "", k, v, s, TC.order_path(v, k, s))
    return rows


def write_list():
    rows = image_list()
    with open(IMAGES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    miss = [r["path"] for r in rows if not Path(r["path"]).exists()]
    print(len(rows), "images,", len(miss), "missing", miss[:3])


def key(r):
    return f"{r['set']}|{r['cond']}|{r['unit']}|{r['seed']}"


# ---------------------------------------------------------------- models (GPU PC)
class Models:
    def __init__(self, vqa=True):
        import torch
        from transformers import AutoModel, AutoImageProcessor, CLIPModel, CLIPProcessor, pipeline
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch = torch
        self.csd = pipeline("image-feature-extraction", model="tomg-group-umd/CSD-ViT-L", trust_remote_code=True,
                            device=0 if self.dev == "cuda" else -1)
        self.dino_p = AutoImageProcessor.from_pretrained("facebook/dinov2-large")
        self.dino = AutoModel.from_pretrained("facebook/dinov2-large").to(self.dev).eval()
        self.clip_p = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        self.clip = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").to(self.dev).eval()
        self.vqa = None
        if vqa:
            import t2v_metrics
            self.vqa = t2v_metrics.VQAScore(model="clip-flant5-xl")

    def csd_vec(self, im):
        a = np.asarray(self.csd(im), dtype=np.float32).squeeze()
        return a[0] if a.ndim == 2 else a          # first token if the pipeline returns tokens

    def dino_vec(self, im):
        with self.torch.no_grad():
            o = self.dino(**self.dino_p(images=im, return_tensors="pt").to(self.dev))
        return o.pooler_output[0].float().cpu().numpy()

    def genre(self, im):
        with self.torch.no_grad():
            x = self.clip_p(text=list(GENRES.values()), images=im, return_tensors="pt", padding=True).to(self.dev)
            p = self.clip(**x).logits_per_image.softmax(-1)[0].float().cpu().numpy()
        return dict(zip(GENRES, p))

    def vqa_scores(self, path, texts):
        s = self.vqa(images=[str(path)], texts=texts)
        return [float(v) for v in np.asarray(s.detach().cpu() if hasattr(s, "detach") else s).ravel()]


def smoke():
    from PIL import Image
    m = Models()
    rows = rd(IMAGES)[:3]
    for r in rows:
        im = Image.open(r["path"]).convert("RGB")
        print(r["set"], r["cond"], "csd", m.csd_vec(im).shape, "dino", m.dino_vec(im).shape,
              "genre", {k: round(float(v), 3) for k, v in m.genre(im).items()},
              "vqa", m.vqa_scores(r["path"], [ELF_TRAITS["antlers"][0]]))


def embed():
    from PIL import Image
    m = Models()
    rows = rd(IMAGES)
    keys, csd, dino, gen, vq = [], [], [], [], []
    for i, r in enumerate(rows):
        im = Image.open(r["path"]).convert("RGB")
        keys.append(key(r)); csd.append(m.csd_vec(im)); dino.append(m.dino_vec(im))
        gen.append({"key": key(r), **{k: round(float(v), 5) for k, v in m.genre(im).items()}})
        if r["set"] == "elf":
            sc = m.vqa_scores(r["path"], [t for t, _ in ELF_TRAITS.values()])
            vq.append({"key": key(r), **{k: round(v, 5) for k, v in zip(ELF_TRAITS, sc)}})
        if i % 50 == 0:
            print(i, "/", len(rows))
    np.savez_compressed(EMB, keys=np.array(keys), csd=np.array(csd), dino=np.array(dino))
    for out, rr in ((GENRE, gen), (VQA, vq)):
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rr[0])); w.writeheader(); w.writerows(rr)
    print("embed ok:", len(keys), "images; csd", np.array(csd).shape, "dino", np.array(dino).shape, "; vqa", len(vq))


# ---------------------------------------------------------------- rules
def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def auc(pos, neg):
    """P(score of a positive > score of a negative), ties 1/2."""
    if not pos or not neg:
        return float("nan")
    s = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return s / (len(pos) * len(neg))


def spearman(x, y):
    from scipy.stats import spearmanr
    r = spearmanr(x, y)
    return float(r.statistic), float(r.pvalue)


def verdict(ok, value):
    return "validated" if ok else "not validated"


def t_style_coherence(E, labels):
    """T1. CSD direction coherence across the 7 characters (sheet) vs 'same direction' (yes 2 / partly 1 / no 0)."""
    import te_characters as TC
    out = {}
    for x in labels:
        k, s = x["cond"], x["seed"]
        d = {c: E[f"chars|{k}|{c}|{s}"] - E[f"chars|baseline|{c}|{s}"] for c in TC.CHARS}
        out[(k, s)] = float(np.median([cos(d[a], d[b]) for a, b in itertools.combinations(TC.CHARS, 2)]))
    lab = {"si": 2, "parte": 1, "no": 0}
    xs = [(out[(x["cond"], x["seed"])], lab[x["stessa"]]) for x in labels if x["stessa"] in lab]
    rho, p = spearman([a for a, _ in xs], [b for _, b in xs])
    a = auc([v for v, l in xs if l == 2], [v for v, l in xs if l == 0])
    return {"test": "T1 style coherence (CSD) vs 'same direction'", "n": len(xs), "rho": round(rho, 3), "p": round(p, 4),
            "auc_yes_vs_no": round(a, 3), "rule": "rho >= 0.40 and AUC >= 0.75",
            "verdict": verdict(rho >= 0.40 and a >= 0.75, None)}


def t_exceptions(E, labels):
    """T2. A character marked 'another way' has a CSD change less aligned with the other six."""
    import te_characters as TC
    pos, neg = [], []
    for x in labels:
        if x["stessa"] not in ("si", "parte", "no"):
            continue
        k, s = x["cond"], x["seed"]
        d = {c: E[f"chars|{k}|{c}|{s}"] - E[f"chars|baseline|{c}|{s}"] for c in TC.CHARS}
        for j, c in enumerate(TC.CHARS):
            m = np.mean([d[o] for o in TC.CHARS if o != c], axis=0)
            v = cos(d[c], m)
            lab = x[f"c_{['D1','E2','O4','G5','H3','R6','T7'][j]}"]
            (pos if lab == "segue" else neg if lab == "diverso" else []).append(v)
    a = auc(pos, neg)
    return {"test": "T2 exceptions (CSD) vs follows / another way", "n": f"{len(pos)}+{len(neg)}", "auc": round(a, 3),
            "rule": "AUC >= 0.70", "verdict": verdict(a >= 0.70, None)}


def t_order(E, scores, space):
    """T3. Dispersion across the five word orders (mean pairwise distance of the edited images minus that of the
    five originals) vs Alessandro's 1-5 scores, seed 3141592."""
    import te_characters as TC
    s = "3141592"
    disp = lambda k: np.mean([1 - cos(E[f"order|{k}|{a}|{s}"], E[f"order|{k}|{b}|{s}"]) for a, b in itertools.combinations(TC.ORDERS, 2)])
    b0 = disp("baseline")
    ks = [k for k in scores if k != "originali"]
    rho, p = spearman([disp(k) - b0 for k in ks], [scores[k] for k in ks])
    return {"test": f"T3 order dispersion ({space}) vs 1-5 scores", "n": len(ks), "rho": round(rho, 3), "p": round(p, 4),
            "rule": "rho >= 0.60 (CSD only; DINOv2 reported)",
            "verdict": verdict(rho >= 0.60, None) if space == "CSD" else "reported"}


def t_style_vs_content(Ec, Ed, elf):
    """T4. On the elf (+-1.00): CSD distance to the baseline separates 'style changed' from 'unchanged' (AUC >= 0.70)
    and better than DINOv2 does (discriminant validity). T5. DINOv2 distance tracks 'how much it changed' (rho >= 0.50)."""
    dist = lambda E, r: 1 - cos(E[f"elf|{r['cond']}||1618033"], E["elf|baseline||1618033"])
    ch = [r for r in elf if r["stile"] == "cambiato"]; un = [r for r in elf if r["stile"] == "inalterato"]
    ac = auc([dist(Ec, r) for r in ch], [dist(Ec, r) for r in un]); ad = auc([dist(Ed, r) for r in ch], [dist(Ed, r) for r in un])
    order = {"nessuna": 0, "lieve": 1, "media": 2, "forte": 3}
    xs = [r for r in elf if r["entita"] in order]
    rho, p = spearman([dist(Ed, r) for r in xs], [order[r["entita"]] for r in xs])
    rc, _ = spearman([dist(Ec, r) for r in xs], [order[r["entita"]] for r in xs])
    return [{"test": "T4 style changed (CSD) vs unchanged", "n": f"{len(ch)}+{len(un)}", "auc_csd": round(ac, 3), "auc_dino": round(ad, 3),
             "rule": "AUC(CSD) >= 0.70 and > AUC(DINOv2)", "verdict": verdict(ac >= 0.70 and ac > ad, None)},
            {"test": "T5 how much it changed (DINOv2)", "n": len(xs), "rho": round(rho, 3), "p": round(p, 4), "rho_csd": round(rc, 3),
             "rule": "rho >= 0.50", "verdict": verdict(rho >= 0.50, None)}]


def genre_labels():
    """Notes that name exactly one genre class: C65 per-character texts and C64 phase-1 style notes."""
    out = []
    import te_characters as TC
    for x in rd(DATA / "te_characters_eye_joined.csv"):
        if x["first"] != "1":
            continue
        for c, ch in zip(["D1", "E2", "O4", "G5", "H3", "R6", "T7"], TC.CHARS):
            t = x[f"t_{c}"].lower()
            hit = [g for g, rx in GENRE_RE.items() if re.search(rx, t)]
            if len(hit) == 1:
                out.append((f"chars|{x['cond']}|{ch}|{x['seed']}", hit[0]))
    for r in rd(DATA / "te_pilot_phase1_joined.csv"):
        t = (r["stilenote"] + " " + r["note"]).lower()
        hit = [g for g, rx in GENRE_RE.items() if re.search(rx, t)]
        if r["phase"] == "main" and len(hit) == 1:
            out.append((f"elf|{r['cond']}||1618033", hit[0]))
    return out


def t_genre(G, labs):
    """T6. Zero-shot CLIP genre = the genre named in the note."""
    from collections import Counter
    xs = [(G[k], g) for k, g in labs if k in G]
    acc = np.mean([max(p, key=p.get) == g for p, g in xs]) if xs else float("nan")
    maj = Counter(g for _, g in xs).most_common(1)[0][1] / len(xs) if xs else float("nan")
    return {"test": "T6 genre (CLIP zero-shot) vs the genre named in the notes", "n": len(xs), "accuracy": round(float(acc), 3),
            "majority": round(float(maj), 3), "rule": "accuracy >= 0.60 and >= majority + 0.15",
            "verdict": verdict(acc >= 0.60 and acc >= maj + 0.15, None)}


def elf_trait_labels():
    """Per trait: renders whose notes say the trait was lost (positives) vs the baseline and renders judged
    'none'/'slight' change whose notes do not mention the trait (negatives)."""
    pos, neg = {t: [] for t in ELF_TRAITS}, {t: [] for t in ELF_TRAITS}
    for r in rd(DATA / "te_pilot_phase1_joined.csv"):
        if r["phase"] != "main":
            continue
        t = (r["stilenote"] + " " + r["note"]).lower()
        for tr, (_, rx) in ELF_TRAITS.items():
            if r["entita"] == "testo":
                continue
            if re.search(rx, t):
                pos[tr].append(f"elf|{r['cond']}||1618033")
            elif r["entita"] in ("nessuna", "lieve"):
                neg[tr].append(f"elf|{r['cond']}||1618033")
    for tr in ELF_TRAITS:
        neg[tr].append("elf|baseline||1618033")
    return pos, neg


def t_traits(V, pos, neg):
    """T7. VQAScore 'is the trait there' is lower where the notes say it was lost. Pooled AUC over traits with >= 3 positives."""
    P, N, per = [], [], {}
    for tr in ELF_TRAITS:
        if len(pos[tr]) < 3:
            continue
        p = [1 - V[k][tr] for k in pos[tr] if k in V]; n = [1 - V[k][tr] for k in neg[tr] if k in V]
        per[tr] = (len(p), round(auc(p, n), 3)); P += [(tr, v) for v in p]; N += [(tr, v) for v in n]
    # pooled within trait: compare only pairs of the same trait
    num = den = 0
    for tr in per:
        p = [v for t, v in P if t == tr]; n = [v for t, v in N if t == tr]
        num += auc(p, n) * len(p) * len(n); den += len(p) * len(n)
    a = num / den if den else float("nan")
    return {"test": "T7 trait lost (VQAScore) vs the notes", "n": sum(v[0] for v in per.values()), "auc_pooled": round(a, 3),
            "per_trait": json.dumps(per), "rule": "pooled AUC >= 0.80", "verdict": verdict(a >= 0.80, None)}


def gap_diagnostic(E, labs):
    """Reported (arXiv 2605.09030): for the genre-labelled images, mean CSD cosine within the same named genre minus
    across genres. A negative gap means raw CSD cosine cannot be read as style similarity on this corpus."""
    xs = [(E[k], g) for k, g in labs if k in E]
    w = [cos(a, b) for (a, g), (b, h) in itertools.combinations(xs, 2) if g == h]
    x = [cos(a, b) for (a, g), (b, h) in itertools.combinations(xs, 2) if g != h]
    return {"test": "D discrimination gap (CSD, genre-labelled images)", "n": len(xs),
            "gap": round(float(np.mean(w) - np.mean(x)), 4) if w and x else None, "rule": "reported", "verdict": "reported"}


def test():
    z = np.load(EMB, allow_pickle=False)
    keys = list(z["keys"]); Ec = dict(zip(keys, z["csd"])); Ed = dict(zip(keys, z["dino"]))
    G = {r["key"]: {g: float(r[g]) for g in GENRES} for r in rd(GENRE)}
    V = {r["key"]: {t: float(r[t]) for t in ELF_TRAITS} for r in rd(VQA)}
    chars = [x for x in rd(DATA / "te_characters_eye_joined.csv") if x["first"] == "1"]
    scores = {r["row"]: int(r["score_1_5"]) for r in rd(DATA / "te_order_grid_notes_alessandro.csv")
              if r["grid"] == "te_order_3141592" and r["score_1_5"]}
    elf = [r for r in rd(DATA / "te_pilot_phase1_joined.csv") if r["phase"] == "main"]
    labs = genre_labels(); pos, neg = elf_trait_labels()
    res = [t_style_coherence(Ec, chars), t_exceptions(Ec, chars), t_order(Ec, scores, "CSD"), t_order(Ed, scores, "DINOv2"),
           *t_style_vs_content(Ec, Ed, elf), t_genre(G, labs), t_traits(V, pos, neg), gap_diagnostic(Ec, labs)]
    cols = sorted({k for r in res for k in r}, key=lambda k: ["test", "n", "verdict", "rule"].index(k) if k in ("test", "n", "verdict", "rule") else 9)
    with open(RESULT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(res)
    for r in res:
        print(r)


def selftest():
    rng = np.random.default_rng(1)
    # a measure equal to the label plus noise passes, pure noise fails
    lab = rng.integers(0, 3, 60)
    good = lab + rng.normal(0, .3, 60); bad = rng.normal(0, 1, 60)
    assert spearman(good, lab)[0] > 0.8 and abs(spearman(bad, lab)[0]) < 0.4
    assert auc([3, 4, 5], [0, 1, 2]) == 1.0 and auc([1], [1]) == 0.5
    assert re.search(ELF_TRAITS["antlers"][1], "ha perso le corna, semplificato")
    assert re.search(ELF_TRAITS["eyepatch"][1], "manca la benda") and not re.search(ELF_TRAITS["eyepatch"][1], "la benda è passata all'altro occhio")
    assert not re.search(ELF_TRAITS["gauntlet"][1], "ha abbassato il braccio senza guanto metallico.")
    assert re.search(ELF_TRAITS["gauntlet"][1], "non ha più il guanto metallico")
    assert [g for g, rx in GENRE_RE.items() if re.search(rx, "dipinto ad olio")] == ["oil"]
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("list", "smoke", "embed", "test", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.list: write_list()
    if a.smoke: smoke()
    if a.embed: embed()
    if a.test: test()
    if a.selftest: selftest()
