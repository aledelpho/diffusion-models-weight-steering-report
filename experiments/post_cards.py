"""Picture cards for the Reddit / Civitai post (2026-10-14). Every number on a card comes from a file in data/ or a
published result page; every picture is an existing render. Output: <Text2Img>/_post_cards/NN_name.png

  python post_cards.py --img-root <Text2Img>
"""
import argparse, csv, os, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent; DATA = HERE.parent / "data"; ASSETS = HERE.parent / "assets"
IMG = Path(".")
BG, INK, DIM, ACC, OK = (20, 20, 20), (240, 240, 240), (160, 160, 160), (236, 120, 60), (90, 190, 130)
W = 1600; PAD = 48
FOOT = "Krea-2 · small samples, mostly one observer · details and all the data in the report linked in the post"
SPEC = (130, 190, 230)
GEN = {"fumetto": "Western comic", "anime": "anime", "cartoon": "cartoon", "realist": "realistic", "pittura": "painting", "altro": "other"}


def F(size, bold=False):
    for p in (r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def rd(name):
    return list(csv.DictReader(open(DATA / name, encoding="utf-8-sig")))


class Card:
    def __init__(self, title, sub):
        self.blocks = []; self.title = title; self.sub = sub

    def text(self, s, size=26, color=DIM, bold=False):
        self.blocks.append(("text", s, size, color, bold))

    def row(self, items, h=420, label_size=24):
        """items: [(path or Image, label, color)]"""
        self.blocks.append(("row", items, h, label_size))

    def stats(self, items):
        """items: [(big, small, color)]"""
        self.blocks.append(("stats", items))

    def spec(self, s):
        self.blocks.append(("text", "⚙ " + s, 22, SPEC, False))

    def image(self, im):
        self.blocks.append(("image", im))

    def render(self, out):
        parts = []
        def txt(s, size, color, bold):
            f = F(size, bold); lines = []
            meas = ImageDraw.Draw(Image.new("RGB", (1, 1)))
            for para in s.split("\n"):
                cur = ""
                for word in para.split(" "):
                    t = (cur + " " + word).strip()
                    if meas.textlength(t, font=f) <= W - 2 * PAD:
                        cur = t
                    else:
                        lines.append(cur); cur = word
                lines.append(cur)
            h = int(len(lines) * size * 1.3)
            im = Image.new("RGB", (W, h + 6), BG); d = ImageDraw.Draw(im)
            for i, l in enumerate(lines):
                d.text((PAD, i * size * 1.3), l, fill=color, font=f)
            return im
        # 2026-10-14: titles and explanations stay in the post (translatable); the card carries only content
        for b in self.blocks:
            if b[0] == "text":
                parts.append(txt(b[1], b[2], b[3], b[4]))
            elif b[0] == "row":
                items, h, ls = b[1], b[2], b[3]
                ims = [it[0] if isinstance(it[0], Image.Image) else Image.open(IMG / it[0]).convert("RGB") for it in items]
                ws = [int(im.width * h / im.height) for im in ims]
                gap = 10; total = sum(ws) + gap * (len(ws) - 1)
                if total > W - 2 * PAD:
                    k = (W - 2 * PAD) / total; h = int(h * k); ws = [int(w * k) for w in ws]; total = sum(ws) + gap * (len(ws) - 1)
                f = F(ls, True); meas = ImageDraw.Draw(Image.new("RGB", (1, 1)))
                def wrap(lab, w):
                    """Labels never overflow their picture: split on spaces (after ':' or '·' first), one or more lines."""
                    out, cur = [], ""
                    for word in lab.split(" "):
                        t = (cur + " " + word).strip()
                        if meas.textlength(t, font=f) <= w - 6 or not cur:
                            cur = t
                        else:
                            out.append(cur); cur = word
                    return out + [cur]
                labs = [sum((wrap(part, w) for part in it[1].split("\n")), []) for it, w in zip(items, ws)]
                nl = max(len(l) for l in labs); lh = int(ls * 1.25)
                row = Image.new("RGB", (W, h + nl * lh + 16), BG); d = ImageDraw.Draw(row); x = (W - total) // 2
                for im, w, it, ll in zip(ims, ws, items, labs):
                    row.paste(im.resize((w, h), Image.LANCZOS), (x, 0))
                    for j, line in enumerate(ll):
                        tw = d.textlength(line, font=f)
                        d.text((x + (w - tw) / 2, h + 6 + j * lh), line, fill=it[2], font=f)
                    x += w + gap
                parts.append(row)
            elif b[0] == "stats":
                n = len(b[1]); cw = (W - 2 * PAD) // n
                wraps = [textwrap.wrap(small, width=int(cw / 13.5)) for _, small, _ in b[1]]
                hh = 100 + 30 * max(len(w) for w in wraps)
                im = Image.new("RGB", (W, hh + 10), BG); d = ImageDraw.Draw(im)
                for i, (big, small, col) in enumerate(b[1]):
                    x = PAD + i * cw
                    d.rounded_rectangle((x + 6, 6, x + cw - 6, hh), 14, outline=(60, 60, 60), width=2)
                    d.text((x + 26, 18), big, fill=col, font=F(54, True))
                    for j, l in enumerate(wraps[i]):
                        d.text((x + 26, 92 + j * 30), l, fill=DIM, font=F(22))
                parts.append(im)
            elif b[0] == "image":
                im = b[1]; k = min(1.0 * (W - 2 * PAD) / im.width, 2.0)
                im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
                c = Image.new("RGB", (W, im.height), BG); c.paste(im, ((W - im.width) // 2, 0)); parts.append(c)
        parts.append(txt(FOOT, 20, (110, 110, 110), False))
        H = sum(p.height for p in parts) + PAD * 2 + 14 * len(parts)
        card = Image.new("RGB", (W, H), BG); y = PAD
        for p in parts:
            card.paste(p, (0, y)); y += p.height + 14
        out.parent.mkdir(parents=True, exist_ok=True); card.save(out); print("card", out.name, card.size)




def pc(ch, seed, cond="baseline"):
    return f"benchmark_portraits/phase_c/{ch}_{cond}_krea2_seed{seed}_00001_.png"


def chart(fig_fn, w=10.0, h=4.6):
    """A simple dark matplotlib chart rendered to a PIL image."""
    import io
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(w, h), dpi=150, facecolor="#141414")
    ax.set_facecolor("#141414")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#555555")
    ax.tick_params(colors="#bbbbbb", labelsize=11)
    fig_fn(ax)
    fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor="#141414"); plt.close(fig)
    buf.seek(0); return Image.open(buf).convert("RGB")


def build(out):
    HOW = "How to read: "

    # 01 text encoder: content, not quality
    c = Card("", "")
    c.spec("Text encoder: Qwen3-VL-4B, 36 layers · edit: the gate, up and down matrices of ONE layer's MLP × 2 each (d = +1), so the layer's output grows up to about × 8 (estimate) · seed 2645751")
    for ch in ("D1_dwarf_paladin", "T7_tiefling_bard"):
        c.row([(pc(ch, "2645751"), "original", DIM),
               (f"benchmark_te_characters/{ch}_L06_mlp_p1.00_krea2_seed2645751_00001_.png", "text-encoder layer 6 doubled", ACC),
               (f"benchmark_te_characters/{ch}_L12_mlp_p1.00_krea2_seed2645751_00001_.png", "text-encoder layer 12 doubled", ACC)], h=400)
    c.render(out / "01_text_encoder_vs_model.png")

    # 02 no single fallback
    fb = {(r["grid"], r["row"]): [r["g1"], r["g2"], r["g3"], r["g4"]] for r in rd("te_fallback_genre_alessandro.csv")}
    eg = {(r["grid"], r["row"]): [r.get(f"g{i}") for i in range(1, 6)] for r in rd("te_default_genre_alessandro.csv")}
    c = Card("", "")
    c.spec("No weight edited · same prompt with and without its style words ('realistic western comics style, bold ink outlines, hatched shadows' for the elf; 'Western comics style' for the portraits) · seeds 3141592, 1234567 (elf) and 2645751 (portraits)")
    def face(path):
        im = Image.open(IMG / path).convert("RGB"); w, h = im.size
        return im.crop((int(0.08 * w), 0, int(0.72 * w), int(0.5 * h)))   # the face, enlarged: ink and hatching vs flat cel shading
    row = []
    for sd_ in ("3141592", "1234567"):
        row += [(face(f"benchmark_prompt_order/V1_Original_baseline_krea2_seed{sd_}_00001_.png"), "elf, with style words", DIM),
                (face(f"benchmark_te_default/V1_Original_nostyle_krea2_seed{sd_}_00001_.png"), "without → " + GEN[eg[(f"c72_{sd_}", "senza_stile")][0]], ACC)]
    c.row(row, h=330, label_size=19)
    items = []
    for ch in ("R6_dragonborn_cleric", "O4_halforc_fighter", "T7_tiefling_bard"):
        items += [(pc(ch, "2645751"), "with style words", DIM),
                  (f"benchmark_te_fallback/{ch}_nostyle_krea2_seed2645751_00001_.png", "without → " + GEN[fb[('fb_without', ch)][0]], ACC)]
    c.row(items, h=300, label_size=18)
    c.render(out / "02_no_single_fallback.png")

    # 03 words alone
    c = Card("", "")
    c.spec('No weight edited · the phrase alone is the whole prompt · seeds 3141592, 1234567, 1618033, 2718281')
    for w, lab in (("W37", '"female dwarf"  → always a beard'), ("W41", '"uniform"  → always a schoolgirl'),
                   ("W00", '"realistic western comics style"  → always cowboys')):
        c.text(lab, 28, INK, True)
        c.row([(f"benchmark_te_default/{w}_word_krea2_seed{s}_00001_.png", "", DIM) for s in ("3141592", "1234567", "1618033", "2718281")], h=330)
    c.render(out / "03_words_alone.png")

    # 04 the character goes first
    ch, s = "O4_halforc_fighter", "2645751"
    A = {(r["edit"], r["dose"]): r for r in rd("te_traits_by_picture.csv") if r["char"] == "O4" and r["seed"] == s}
    # traits judged in the original (denominator) from the part A labels
    keyA = {r["item"]: r for r in rd("te_traits_key_A.csv")}
    labA = [r for r in rd("te_traits_alessandro.csv") if r["showing"] == "1"]
    def counts_A(edit, dose):
        it_o = next(k for k, v in keyA.items() if v["char"] == "O4" and v["seed"] == s and v["dose"] == "0.00")
        it = it_o if dose == "0.00" else next(k for k, v in keyA.items() if v["char"] == "O4" and v["seed"] == s and v["edit"] == edit and v["dose"] == dose)
        a = {r["question"]: r["answer"] for r in labA if r["item"] == it}
        o = {r["question"]: r["answer"] for r in labA if r["item"] == it_o}
        p0 = [q for q, v in o.items() if v == "sì" and q.startswith("o_")]
        return sum(a.get(q) == "no" for q in p0), len(p0)      # traits lost, out of the traits the original shows
    style_from = float(next(r["cambia_da"] for r in rd("te_dose_alessandro.csv") if r["grid"] == "dose_L06" and r["row"] == f"{ch} · {s}"))
    def dose_p(d):
        return pc(ch, s) if d == "0.00" else (f"benchmark_te_characters/{ch}_L06_mlp_p1.00_krea2_seed{s}_00001_.png" if d == "1.00"
                                              else f"benchmark_te_dose/{ch}_L06_mlp_p{d}_krea2_seed{s}_00001_.png")
    c = Card("", "")
    c.spec("Text encoder layer 6 MLP: gate, up, down each × (1 + d), the multiplier under each picture; the layer's output grows up to about (1 + d)³ (estimate) · random pushes: noise added to what the text encoder hands over, matched in size to the real edit, varying per word or with channels shuffled · 8 traits judged on the original · seed 2645751")
    row = []
    for d in ("0.00", "0.40", "0.60", "0.70", "0.80", "1.00"):
        k, n = counts_A("L06_mlp", d)
        style = "comic" if float(d) < style_from else "realistic"
        head = "original" if d == "0.00" else f"× {1 + float(d):.1f}"
        row.append((dose_p(d), f"{head}\n{'nothing lost' if k == 0 else f'{k} of {n} traits lost'}\n{style}", ACC if k else DIM))
    c.row(row, h=310, label_size=20)
    # second row: random pushes of the same size, second labeller
    K = {r["item"]: r for r in rd("te_traits_key_B2.csv")}
    lab2 = {}
    for r in rd("te_traits_B2_rater2.csv"):
        if r["showing"] == "1":
            k = K[r["item"]]
            if k["char"] == "O4" and k["seed"] == s and k["dose"] in ("0.00", "1.00") and k["edit"] in ("", "L06_mlp") and k["variant"] != "plain_B0":
                lab2.setdefault(k["variant"], {})[r["question"]] = r["answer"]
    def counts_B(v):
        o = lab2["original"]; a = lab2[v]
        p0 = [q for q, x in o.items() if x == "sì" and q.startswith("o_")]
        return sum(a.get(q) == "no" for q in p0), len(p0)
    c.text("The same size of push (× 2.0) in a random direction keeps most of the character", 26, INK, True)
    lb = []
    for v, head, col, path in (("real", "the real edit", ACC, dose_p("1.00")),
                               ("token", "random push", OK, f"benchmark_te_traits/{ch}_L06_mlp_p1.00_token_krea2_seed{s}_00001_.png"),
                               ("permuted", "another random push", OK, f"benchmark_te_traits/{ch}_L06_mlp_p1.00_permuted_krea2_seed{s}_00001_.png")):
        k, n = counts_B(v); lb.append((path, f"{head}\n{k} of {n} traits lost", col))
    c.row([(pc(ch, s), "original", DIM)] + lb, h=330, label_size=20)
    c.text("Traits counted by blind yes/no answers (first row: mine; second row: a second person who knew nothing of the study). "
           "Over all pictures at × 2.0, the real edit keeps about half the traits, random pushes about nine in ten.", 20, DIM)
    c.render(out / "04_character_goes_first.png")

    # 05 commas
    c = Card("", "")
    c.spec("Measured on 20 text-encoder edits × 12 readings of the conditioning (241 encodes, no images) · the similarity of two words' shifts halves after about 3 words")
    im = Image.new("RGB", (W - 2 * PAD, 260), BG); d = ImageDraw.Draw(im)
    groups = [["dark", "green", "hooded", "cowl"], ["brass", "buckles"], ["a", "single", "feather", "earring"]]
    cols = [(236, 120, 60), (90, 160, 230), (120, 200, 120)]
    x = 20; f = F(32, True)
    for gi, g in enumerate(groups):
        x0 = x
        for wd in g:
            tw = d.textlength(wd, font=f)
            d.rounded_rectangle((x, 60, x + tw + 24, 124), 10, fill=cols[gi]); d.text((x + 12, 70), wd, fill=(20, 20, 20), font=f)
            x += tw + 34
        d.line((x0, 146, x - 10, 146), fill=cols[gi], width=5); d.text((x0, 160), "move together", fill=cols[gi], font=F(24))
        if gi < len(groups) - 1:
            d.text((x - 4, 58), ",", fill=INK, font=F(56, True)); x += 26
    c.image(im)
    c.stats([("18 of 20", "edits where words inside one comma-phrase moved more alike than words across a comma", ACC)])
    c.render(out / "05_commas.png")

    # 06 blocks
    plan = {(int(r["block_idx"]), r["sign"]): f"{abs(float(r['dose'])):.3f}" for r in rd("single_blocks_v4_plan.csv") if r["block_idx"]}
    root = "benchmark_single_blocks_v4/renders"; P = "P5_comic_panels"; sd = "1234567"
    def top(path):
        im = Image.open(IMG / path).convert("RGB"); w, h = im.size
        return im.crop((w // 2, 0, w, h // 2))
    b = lambda k: top(f"{root}/{P}_blk{k:02d}_pos_d{plan[(k, 'pos')]}_krea2_seed{sd}_00001_.png")
    c = Card("", "")
    c.spec('Image model: 28 blocks · edit: every weight matrix of ONE block × (1 + d): block 9 × 1.55, block 23 × 1.30, block 26 × 1.15 · seed 1234567 · upper-right panel of a four-panel comic page')
    c.row([(top(f"{root}/{P}_baseline_krea2_seed{sd}_00001_.png"), "original", DIM),
           (b(9), "middle block 9:\ncontent changes", ACC), (b(23), "late block 23:\nless colour", OK), (b(26), "late block 26:\nsurface, contrast", OK)],
          h=440, label_size=22)
    c.render(out / "06_blocks.png")

    # 07 saturation
    c = Card("", "")
    c.spec("Image model block 23 only, all its weight matrices × (1 + d): × 0.55 (more colour), × 1.30 (less colour) · the words added: 'colorful, vivid highly saturated colors' · seed 2718281")
    bb = "benchmark_blk23_colorful"
    for p_, sd2 in (("E3_oil", "2718281"), ("E1_cartoon", "2718281"), ("C4_stilllife", "2718281")):
        c.row([(f"{bb}/{p_}_baseline_krea2_seed{sd2}_00001_.png", "original", DIM),
               (f"{bb}/{p_}_b23_m0.450_krea2_seed{sd2}_00001_.png", "block 23: more colour", OK),
               (f"{bb}/{p_}_b23_p0.300_krea2_seed{sd2}_00001_.png", "block 23: less colour", OK),
               (f"{bb}/{p_}_txtpos_krea2_seed{sd2}_00001_.png", 'prompt + "colorful"', ACC)], h=330, label_size=20)
    c.render(out / "07_saturation.png")

    # 08 preset
    c = Card("", "")
    c.spec("Preset: 10 of the tuner's 34 multipliers changed, from −0.35 to +0.15, frozen before the test · seed 3316624 · blind test: 28 pairs (7 characters × 4 seeds), each shown twice with sides swapped = 56 choices")
    chars = ("H3_halfling_druid", "R6_dragonborn_cleric", "T7_tiefling_bard")
    c.row([(pc(x, "3316624"), "original", DIM) for x in chars], h=420)
    c.row([(pc(x, "3316624", "preset"), "with the preset", ACC) for x in chars], h=420)
    c.render(out / "08_preset_unseen.png")

    # 09 shuffled
    gen = {r["row"]: [r[f"g{i}"] for i in range(1, 6)] for r in rd("te_genre_alessandro.csv") if r["grid"] == "te_genre_3141592"}
    orders = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
    c = Card("", "")
    c.spec("Elf brawler, seed 3141592 · edits: one text-encoder layer's MLP (gate, up, down) × 2 · genre labels: mine")
    c.row([(f"benchmark_prompt_order/{o}_baseline_krea2_seed3141592_00001_.png", GEN[gen["originali"][i]], DIM) for i, o in enumerate(orders)], h=250, label_size=18)
    c.text("text-encoder layer 5 doubled: every order → anime", 24, INK, True)
    c.row([(f"benchmark_te_characters/{o}_L05_mlp_p1.00_krea2_seed3141592_00001_.png", GEN[gen["L05_mlp_p1.00"][i]], ACC) for i, o in enumerate(orders)], h=250, label_size=18)
    c.text("text-encoder layer 6 doubled: the orders scatter", 24, INK, True)
    c.row([(f"benchmark_te_characters/{o}_L06_mlp_p1.00_krea2_seed3141592_00001_.png", GEN[gen["L06_mlp_p1.00"][i]], ACC) for i, o in enumerate(orders)], h=250, label_size=18)
    c.render(out / "09_shuffled_prompts.png")

    # 10 hatching (simple chart from the pairs file)
    import statistics
    pairs = rd("stage7_hatching_pairs.csv")
    def per_prompt(fam):
        g = {}
        for r in pairs:
            if r["family"] == fam:
                g.setdefault(r["prompt_sha1"], []).append(float(r["delta"]))
        return [statistics.mean(v) for v in g.values()]
    re_, rnd = per_prompt("blockshuffle"), per_prompt("randsign")
    def draw(ax):
        ax.axvline(0, color="#888888", ls="--", lw=1)
        ax.scatter(re_, [1] * len(re_), s=90, color="#ec783c", zorder=3)
        ax.scatter(rnd, [0] * len(rnd), s=90, color="#5abe82", zorder=3)
        ax.set_yticks([0, 1]); ax.set_yticklabels(["random edit,\nsame size", "block\nreordering"], color="#eeeeee", fontsize=13)
        ax.set_ylim(-0.6, 1.6); ax.set_xlim(-0.5, 0.6)
        ax.set_xlabel("← fewer crossing strokes      change in shadow hatching after the edit      more crossing strokes →", color="#bbbbbb", fontsize=12)
    c = Card("", "")
    c.spec('Edit: weights of whole blocks moved between positions in the checkpoint, + and − direction, relative weight change 5.4% · random edit: weights changed by the same 5.4% with random signs · 16 prompts × 5 seeds · measure: crosshatch entropy (variety of stroke directions)')
    c.image(chart(draw, 10, 3.6))
    c.render(out / "10_hatching.png")

    # 11 predict (simple chart)
    size = {r["cond"]: float(r["size"]) for r in rd("te_order_tests.csv")}
    inten = {r["row"]: statistics.mean(int(r[f"d{i}"]) for i in range(1, 6)) for r in rd("te_genre_dose_alessandro.csv")}
    pts = [(size[k], inten[k], k.endswith("_m1.00")) for k in size if k in inten]
    def draw2(ax):
        ax.scatter([x for x, y, z in pts if not z], [y for x, y, z in pts if not z], s=90, color="#ec783c", label="one layer doubled", zorder=3)
        ax.scatter([x for x, y, z in pts if z], [y for x, y, z in pts if z], s=90, color="#5aa0e6", label="one layer switched off", zorder=3)
        ax.set_xlabel("how far the edit moves what the text encoder hands over  →", color="#bbbbbb", fontsize=12)
        ax.set_ylabel("how much the picture changed\n(by eye, 0 = nothing, 3 = everything)", color="#bbbbbb", fontsize=12)
        ax.legend(frameon=False, labelcolor="#eeeeee", fontsize=12, loc="lower right")
    c = Card("", "")
    c.spec('Each dot: one text-encoder edit (one layer, attention or MLP, × 0 or × 2) on the elf prompt, seed 3141592 · x: mean relative change of the conditioning · y: mean intensity of change by eye (0-3) over 5 word orders · Spearman 0.80 (pre-registered)')
    c.image(chart(draw2, 10, 4.6))
    c.render(out / "11_predict_change.png")


def build_schema(out):
    """00 - what the edit is: the whole model, and the one crude multiplication applied to it."""
    import random
    rnd = random.Random(3)
    Wc, Hc = 1600, 1200
    im = Image.new("RGB", (Wc, Hc), BG); d = ImageDraw.Draw(im)
    TE_C, DIT_C, HI = (70, 110, 160), (80, 80, 80), ACC
    # pipeline row
    y0 = 40
    def box(x, y, w, h, txt, sub, col, fs=26):
        d.rounded_rectangle((x, y, x + w, y + h), 14, fill=col)
        d.text((x + 16, y + 12), txt, fill=INK, font=F(fs, True))
        if sub:
            d.text((x + 16, y + 12 + fs + 8), sub, fill=(220, 220, 220), font=F(20))
    def arrow(x1, y, x2):
        d.line((x1, y, x2 - 12, y), fill=DIM, width=4); d.polygon([(x2, y), (x2 - 16, y - 9), (x2 - 16, y + 9)], fill=DIM)
    box(PAD, y0, 200, 90, "prompt", "your words", (55, 55, 55))
    arrow(PAD + 205, y0 + 45, PAD + 265)
    box(PAD + 270, y0, 420, 90, "Text encoder", "Qwen3-VL-4B · 36 layers", TE_C)
    arrow(PAD + 695, y0 + 45, PAD + 755)
    box(PAD + 760, y0, 470, 90, "Image model (DiT)", "Krea-2 · 28 blocks", DIT_C)
    arrow(PAD + 1235, y0 + 45, PAD + 1295)
    thumb = Image.open(IMG / pc("R6_dragonborn_cleric", "3316624")).convert("RGB"); thumb.thumbnail((120, 150))
    im.paste(thumb, (PAD + 1300, y0 - 25))
    d.text((PAD, y0 + 108), "the text encoder turns the words into numbers (12 readings per word); that is all the image model ever sees of the prompt",
           fill=DIM, font=F(19))
    # text encoder layers
    y1 = 230
    d.text((PAD, y1), "Text encoder: 36 layers (each: attention + MLP)", fill=INK, font=F(26, True))
    cw = (Wc - 2 * PAD - 35 * 6) / 36
    for i in range(36):
        x = PAD + i * (cw + 6); hl = i == 6
        d.rounded_rectangle((x, y1 + 44, x + cw, y1 + 110), 6, fill=HI if hl else TE_C)
        if i % 5 == 0 or hl:
            d.text((x + 3, y1 + 116), str(i), fill=HI if hl else DIM, font=F(16, hl))
    d.text((PAD + 6 * (cw + 6) - 10, y1 + 140), "e.g. layer 6: its MLP matrices (gate, up, down) × 2", fill=HI, font=F(20, True))
    # image model blocks
    y2 = 430
    d.text((PAD, y2), "Image model: 28 blocks (each: attention + MLP, 8 weight matrices)", fill=INK, font=F(26, True))
    cw2 = (Wc - 2 * PAD - 27 * 8) / 28
    bx = {}
    for i in range(28):
        x = PAD + i * (cw2 + 8); hl = i == 23
        d.rounded_rectangle((x, y2 + 44, x + cw2, y2 + 130), 8, fill=HI if hl else DIT_C)
        d.text((x + 6, y2 + 136), str(i), fill=HI if hl else DIM, font=F(16, hl))
        bx[i] = x
    d.text((PAD, y2 + 166), "early blocks", fill=DIM, font=F(20)); d.text((bx[9], y2 + 166), "middle: content", fill=DIM, font=F(20))
    lt = "late: colour, grain, surface"; d.text((bx[23] - 14 - d.textlength(lt, font=F(20)), y2 + 166), lt, fill=DIM, font=F(20))
    # zoom on block 23
    y3 = 650
    zx0, zx1 = PAD + 40, Wc - PAD - 40
    yl = y2 + 198
    d.line((bx[23] + cw2 / 2, y2 + 160, bx[23] + cw2 / 2, yl), fill=HI, width=3)
    d.line((bx[23] + cw2 / 2, yl, zx0, y3), fill=HI, width=2); d.line((bx[23] + cw2 / 2, yl, zx1, y3), fill=HI, width=2)
    d.rounded_rectangle((zx0, y3, zx1, y3 + 470), 16, outline=HI, width=3)
    d.text((zx0 + 24, y3 + 16), "block 23, opened: its 8 weight matrices (illustration: each square stands for thousands of numbers)", fill=INK, font=F(22, True))
    # 8 matrices as noise squares
    ms = 120
    for k in range(8):
        x = zx0 + 30 + k * (ms + 50); y = y3 + 70
        tile = Image.new("L", (24, 24))
        tile.putdata([int(128 + rnd.gauss(0, 45)) for _ in range(24 * 24)])
        tile = tile.resize((ms, ms), Image.NEAREST).convert("RGB")
        im.paste(tile, (x, y))
        d.text((x, y + ms + 6), ["attn q", "attn k", "attn v", "attn out", "attn gate", "MLP up", "MLP gate", "MLP down"][k], fill=DIM, font=F(18))
    # the operation
    ya = y3 + 250
    d.text((zx0 + 30, ya), "The whole intervention:", fill=INK, font=F(30, True))
    d.text((zx0 + 30, ya + 50), "every number in those 8 matrices  ×  1.30", fill=HI, font=F(44, True))
    ex_in = [0.0121, -0.0307, 0.0043, -0.0189]; f = 1.30
    d.text((zx0 + 30, ya + 120), "for example   " + "   ".join(f"{v:+.4f}" for v in ex_in) + "   →   " + "   ".join(f"{v * f:+.4f}" for v in ex_in),
           fill=(200, 200, 200), font=F(22))
    d.text((zx0 + 30, ya + 165), "one number per block · nothing trained · nothing added · the other 27 blocks and the text encoder untouched",
           fill=DIM, font=F(22))
    # footer
    d.text((PAD, Hc - 60), "A preset is just a list of such multipliers (34 numbers in the tuner). Numbers in the example row are illustrative.",
           fill=(110, 110, 110), font=F(20))
    im.save(out / "00_what_the_edit_is.png"); print("card 00_what_the_edit_is.png", im.size)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--img-root", required=True)
    a = ap.parse_args(); IMG = Path(a.img_root)
    build(IMG / "_post_cards")
    build_schema(IMG / "_post_cards")
