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
FOOT = "Krea-2 turbo · euler_ancestral, 9 steps, CFG 1, 1024×1280 · small samples, mostly one observer · full report linked in the post"
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


def build(out):
    # 01 text encoder vs image model
    c = Card("1 · Text-encoder edits change WHAT is drawn, not the image quality",
             "Same seed, one layer of the text encoder doubled. The pictures stay clean, but genre and character change, "
             "and the same edit moves different characters in different directions.")
    c.spec("Text encoder: Qwen3-VL-4B, 36 layers · edit: the gate, up and down matrices of ONE layer's MLP × 2 each (d = +1), so the layer's output grows up to about × 8 (estimate) · seed 2645751")
    for ch in ("D1_dwarf_paladin", "T7_tiefling_bard"):
        c.row([(pc(ch, "2645751"), "original", DIM),
               (f"benchmark_te_characters/{ch}_L06_mlp_p1.00_krea2_seed2645751_00001_.png", "TE layer 6 MLP × 2", ACC),
               (f"benchmark_te_characters/{ch}_L12_mlp_p1.00_krea2_seed2645751_00001_.png", "TE layer 12 MLP × 2", ACC)], h=380)
    c.stats([("−1.52 vs +8.09", "image-quality change (BRISQUE, lower = better): text-encoder edits vs an image-model preset", OK),
             ("4 of 20", "text-encoder edits that moved different characters the same way", ACC)])
    c.render(out / "01_text_encoder_vs_model.png")

    # 02 no single fallback
    fb = {(r["grid"], r["row"]): [r["g1"], r["g2"], r["g3"], r["g4"]] for r in rd("te_fallback_genre_alessandro.csv")}
    eg = {(r["grid"], r["row"]): [r.get(f"g{i}") for i in range(1, 6)] for r in rd("te_default_genre_alessandro.csv")}
    c = Card("2 · Without a style in the prompt, there is no single default",
             "I removed the style words. This elf turns anime every time; other characters come back as paintings or "
             "photographs. Each description carries its own fallback.")
    c.spec("No weight edited · same prompt with and without its style words · seeds 3141592 (elf) and 2645751 (portraits)")
    c.row([("benchmark_prompt_order/V1_Original_baseline_krea2_seed3141592_00001_.png", "with style: " + GEN[eg[("c72_3141592", "originale")][0]], DIM),
           ("benchmark_te_default/V1_Original_nostyle_krea2_seed3141592_00001_.png", "no style: " + GEN[eg[("c72_3141592", "senza_stile")][0]], ACC)], h=460)
    items = []
    for ch, name in (("R6_dragonborn_cleric", "dragonborn"), ("O4_halforc_fighter", "half-orc"), ("T7_tiefling_bard", "tiefling")):
        items += [(pc(ch, "2645751"), f"{name}: with style", DIM),
                  (f"benchmark_te_fallback/{ch}_nostyle_krea2_seed2645751_00001_.png", f"no style: {GEN[fb[('fb_without', ch)][0]]}", ACC)]
    c.row(items, h=300, label_size=18)
    c.render(out / "02_no_single_fallback.png")

    # 03 words alone
    c = Card("3 · Single words carry their own baggage",
             "Each phrase rendered on its own (three of the four seeds shown). If something keeps showing up uninvited, try the suspicious words alone.")
    c.spec("No weight edited · the phrase alone is the whole prompt · labels: 4 seeds per phrase")
    for w, lab in (("W37", '"female dwarf"  → a beard, 4 of 4'), ("W41", '"uniform"  → anime schoolgirl, 4 of 4'),
                   ("W00", '"realistic western comics style"  → cowboys')):
        c.text(lab, 28, INK, True)
        c.row([(f"benchmark_te_default/{w}_word_krea2_seed{s}_00001_.png", f"seed {s}", DIM) for s in ("3141592", "1234567", "1618033")], h=340)
    c.render(out / "03_words_alone.png")

    # 04 the character goes first (rebuilt 2026-10-14: every picture says what it lost, from the blind labels)
    NAMES = {"o_orc": "orc features", "o_undercut": "undercut", "o_knot": "warrior knot", "o_scale": "scale collar",
             "o_young": "young", "o_jack": "quilted jacket", "o_female": "female", "o_greyeyes": "grey eyes",
             "o_tusks": "tusks", "o_snarl": "snarl", "o_dirt": "dirt", "c_frontal": "frontal", "c_whitebg": "white background"}
    ch, s = "O4_halforc_fighter", "2645751"
    A = {(r["edit"], r["dose"]): r for r in rd("te_traits_by_picture.csv") if r["char"] == "O4" and r["seed"] == s}
    style_from = next(r["cambia_da"] for r in rd("te_dose_alessandro.csv") if r["grid"] == "dose_L06" and r["row"] == f"{ch} · {s}")
    def dose_p(d):
        return pc(ch, s) if d == "0" else (f"benchmark_te_characters/{ch}_L06_mlp_p1.00_krea2_seed{s}_00001_.png" if d == "1.00"
                                           else f"benchmark_te_dose/{ch}_L06_mlp_p{d}_krea2_seed{s}_00001_.png")
    def lab_a(d):
        r = A[("", "0.00")] if d == "0" else A[("L06_mlp", d)]
        lost = [NAMES.get(t, t) for t in r["lost"].split(";") if t]
        style = "comic" if d == "0" or float(d) < float(style_from) else "realistic"
        head = "original" if d == "0" else f"× {1 + float(d):.1f}"
        return (f"{head}\ntraits kept {float(r['R']):.2f}\nlost: {', '.join(lost) if lost else 'nothing'}\nstyle: {style}",
                ACC if lost else DIM)
    c = Card("4", "")
    c.spec("Text encoder layer 6 MLP: gate, up, down each × (1 + d), shown as the multiplier under each picture · "
           "'traits kept' = share of the traits the prompt asks for (and the original shows) that are still there, blind yes/no labels · seed 2645751")
    c.text("Turning one text-encoder layer up: the half-orc loses her traits first, the drawing style changes later", 26, INK, True)
    c.row([(dose_p(d), *lab_a(d)) for d in ("0", "0.40", "0.60", "0.70", "0.80", "1.00")], h=300, label_size=17)
    # second row: the same size of push in a random direction, labelled by the second person
    K = {r["item"]: r for r in rd("te_traits_key_B2.csv")}
    lab2 = {}
    for r in rd("te_traits_B2_rater2.csv"):
        if r["showing"] == "1":
            k = K[r["item"]]
            if k["char"] == "O4" and k["seed"] == s and k["dose"] in ("0.00", "1.00") and k["edit"] in ("", "L06_mlp") and k["variant"] != "plain_B0":
                lab2[(k["variant"], r["question"])] = r["answer"]
    def lost2(v):
        return [NAMES.get(q, q) for (vv, q), a in lab2.items() if vv == v and q in NAMES and a == "no" and lab2.get(("original", q)) == "sì"]
    R = {(r["variant"]): r for r in rd("te_traits_B2_by_picture.csv") if r["char"] == "O4" and r["seed"] == s and r["dose"] in ("0.00", "1.00") and r["edit"] in ("", "L06_mlp") and r["variant"] != "plain_B0"}
    def lab_b(v, head):
        L = lost2(v)
        kept = "" if v == "original" else f"\ntraits kept {float(R[v]['R']):.2f}"
        return (f"{head}{kept}\nlost: {', '.join(sorted(L)) if L else 'nothing'}", ACC if v == "real" else (OK if v != "original" else DIM))
    c.text("Same size of push (× 2.0), but in a random direction: most traits stay (labels by a second, blind person)", 26, INK, True)
    c.row([(pc(ch, s), *lab_b("original", "original")),
           (dose_p("1.00"), *lab_b("real", "real edit")),
           (f"benchmark_te_traits/{ch}_L06_mlp_p1.00_token_krea2_seed{s}_00001_.png", *lab_b("token", "random push (per word)")),
           (f"benchmark_te_traits/{ch}_L06_mlp_p1.00_permuted_krea2_seed{s}_00001_.png", *lab_b("permuted", "random push (shuffled)"))],
          h=330, label_size=18)
    c.stats([("0.48 vs 0.88", "traits kept at × 2.0, layer 6, average of 6 pictures: real edit vs random pushes", ACC),
             ("0.63 vs 0.94", "the same for layer 14", ACC)])
    c.render(out / "04_character_goes_first.png")

    # 05 commas (schematic)
    c = Card("5 · Commas seem to act as borders (lead, not proof)",
             "When I edit the text encoder, the meaning of every word shifts a little. Part of the shift is shared by the whole "
             "prompt; part moves in small packets of 2-4 neighbouring words, and the packets tend to break at commas.")
    c.spec("Measured on 20 text-encoder edits × 12 readings of the conditioning (241 encodes, no images)")
    im = Image.new("RGB", (W - 2 * PAD, 330), BG); d = ImageDraw.Draw(im)
    groups = [["dark", "green", "hooded", "cowl"], ["brass", "buckles"], ["a", "single", "feather", "earring"]]
    cols = [(236, 120, 60), (90, 160, 230), (120, 200, 120)]
    x = 20; f = F(30, True)
    d.rounded_rectangle((10, 20, W - 2 * PAD - 10, 80), 12, fill=(60, 60, 60))
    d.text((30, 32), "shared shift: the whole prompt moves a little in one direction", fill=INK, font=F(26))
    for gi, g in enumerate(groups):
        x0 = x
        for wd in g:
            tw = d.textlength(wd, font=f)
            d.rounded_rectangle((x, 130, x + tw + 24, 190), 10, fill=cols[gi]); d.text((x + 12, 140), wd, fill=(20, 20, 20), font=f)
            x += tw + 34
        d.line((x0, 210, x - 10, 210), fill=cols[gi], width=5); d.text((x0, 222), "moves together", fill=cols[gi], font=F(22))
        if gi < len(groups) - 1:
            d.text((x - 4, 128), ",", fill=INK, font=F(52, True)); x += 26
    d.text((20, 280), "illustration of the pattern, not a measurement on this phrase", fill=DIM, font=F(20))
    c.image(im)
    c.stats([("18 of 20", "edits where words of the same comma-phrase moved more alike than words across a comma", ACC),
             ("~3 words", "distance at which the similarity of two words' shifts halves", ACC)])
    c.render(out / "05_commas.png")

    # 06 blocks
    plan = {(int(r["block_idx"]), r["sign"]): f"{abs(float(r['dose'])):.3f}" for r in rd("single_blocks_v4_plan.csv") if r["block_idx"]}
    root = "benchmark_single_blocks_v4/renders"; P = "P5_comic_panels"; sd = "1234567"
    b0 = lambda k, sg: f"{root}/{P}_blk{k:02d}_{sg}_d{plan[(k, sg)]}_krea2_seed{sd}_00001_.png"
    def top(path):
        im = Image.open(IMG / path).convert("RGB"); w, h = im.size
        return im.crop((w // 2, 0, w, h // 2))      # the upper-right panel of the comic page (the elf), larger
    b = lambda k, sg: top(b0(k, sg))
    c = Card("6 · Different blocks do different things",
             "One block of the image model pushed at a time, same seed. Middle blocks change the content; the last ones change "
             "colour, contrast and grain.")
    c.spec("Image model: 28 blocks · edit: every weight matrix of ONE block × (1 + d) · seed 1234567")
    c.row([(top(f"{root}/{P}_baseline_krea2_seed{sd}_00001_.png"), "original", DIM), (b(9, "pos"), f"block 9 × {1 + float(plan[(9, 'pos')]):.2f}: content", ACC),
           (b(23, "pos"), f"block 23 × {1 + float(plan[(23, 'pos')]):.2f}: colour", ACC), (b(26, "pos"), f"block 26 × {1 + float(plan[(26, 'pos')]):.2f}: surface", ACC)], h=420, label_size=22)
    c.text("(one panel of a four-panel comic page, enlarged; every picture is the same seed)", 20, DIM)
    c.stats([("19% vs 79%", "pictures with surface damage: edits to blocks 1-19 vs blocks 20-27 (comics and cartoons, labelled blind)", OK)])
    c.render(out / "06_blocks.png")

    # 07 saturation
    c = Card("7 · Block 23 works as a saturation knob",
             "Block 23 alone moves colour and keeps the picture. Writing \"colorful\" in the prompt changes far more: the elf "
             "turns blonde, a cut lemon appears in the still life.")
    c.spec("Image model block 23 only, all its weight matrices × (1 + d) · seed 2718281")
    for p, sd2 in (("E3_oil", "2718281"), ("E1_cartoon", "2718281"), ("C4_stilllife", "2718281")):
        bb = "benchmark_blk23_colorful"
        c.row([(f"{bb}/{p}_baseline_krea2_seed{sd2}_00001_.png", "original", DIM),
               (f"{bb}/{p}_b23_m0.450_krea2_seed{sd2}_00001_.png", "block 23 × 0.55: more colour", OK),
               (f"{bb}/{p}_b23_p0.300_krea2_seed{sd2}_00001_.png", "block 23 × 1.30: less colour", OK),
               (f"{bb}/{p}_txtpos_krea2_seed{sd2}_00001_.png", 'words: "colorful…"', ACC)], h=330, label_size=20)
    c.render(out / "07_saturation.png")

    # 08 preset on unseen characters
    c = Card("8 · A preset carries over to characters it has never seen",
             "Tuned by eye on four portraits, then applied to three new characters. A person who didn't know which was which "
             "picked the preset as closer to the look I described (a more American-comic look, flat colours, clean lines) "
             "56 times out of 56.")
    c.spec("Preset: 10 of the tuner's 34 multipliers changed, from −0.35 to +0.15, frozen before the test · seed 3316624")
    chars = ("H3_halfling_druid", "R6_dragonborn_cleric", "T7_tiefling_bard")
    c.row([(pc(ch, "3316624"), "original", DIM) for ch in chars], h=420)
    c.row([(pc(ch, "3316624", "preset"), "preset", ACC) for ch in chars], h=420)
    c.render(out / "08_preset_unseen.png")

    # 09 shuffled prompts
    gen = {r["row"]: [r[f"g{i}"] for i in range(1, 6)] for r in rd("te_genre_alessandro.csv") if r["grid"] == "te_genre_3141592"}
    orders = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
    c = Card("9 · Same words, five orders (lead, still under study)",
             "The same prompt with its phrases shuffled. Some text-encoder edits send every order to the same place, others "
             "scatter them into different genres. I don't know why yet.")
    c.spec("Elf brawler, seed 3141592 · edits: one text-encoder layer's MLP × 2")
    c.row([(f"benchmark_prompt_order/{o}_baseline_krea2_seed3141592_00001_.png", GEN[gen["originali"][i]], DIM) for i, o in enumerate(orders)], h=260, label_size=18)
    c.text("TE layer 5 MLP × 2: every order goes anime", 26, INK, True)
    c.row([(f"benchmark_te_characters/{o}_L05_mlp_p1.00_krea2_seed3141592_00001_.png", GEN[gen["L05_mlp_p1.00"][i]], ACC) for i, o in enumerate(orders)], h=260, label_size=18)
    c.text("TE layer 6 MLP × 2: the orders scatter", 26, INK, True)
    c.row([(f"benchmark_te_characters/{o}_L06_mlp_p1.00_krea2_seed3141592_00001_.png", GEN[gen["L06_mlp_p1.00"][i]], ACC) for i, o in enumerate(orders)], h=260, label_size=18)
    c.render(out / "09_shuffled_prompts.png")

    # 10 hatching: the measured result (crops were not convincing by eye, 2026-10-14)
    c = Card("10", "")
    c.spec("Edit: weights of whole blocks moved between positions in the checkpoint, + and − direction, relative weight change 5.4% "
           "· 16 new comic prompts × 5 seeds · measure: crosshatch entropy, how varied the stroke directions are (higher = more crossing)")
    c.image(Image.open(HERE.parent / "assets" / "06-the-hatching-axis" / "F06.1_hatching_axis_by_prompt.webp").convert("RGB"))
    c.text("Orange row: block reordering, 16 prompts of 16 on the predicted side. Blue: my hand-calibrated preset goes the other way. "
           "Green: a random edit of the same size does nothing consistent. By eye the effect is subtle; it shows up in the measure.", 22)
    c.render(out / "10_hatching.png")

    # 11 predict
    c = Card("11 · How much a picture will change can be predicted without rendering it",
             "Measure how far a text-encoder edit moves what it hands to the image model, and you know roughly how much the "
             "picture will change (correlation 0.71 and 0.80, pre-registered). It works mostly to tell kinds of edit apart.")
    c.spec("Each dot: one text-encoder edit (one layer, attention or MLP, × 0 or × 2) · x = how far it moves the text encoder's output · y = how much the picture changed by eye")
    c.image(Image.open(ASSETS / "30-the-text-encoder" / "F30.3_te_size_vs_intensity.webp").convert("RGB"))
    c.render(out / "11_predict_change.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--img-root", required=True)
    a = ap.parse_args(); IMG = Path(a.img_root)
    build(IMG / "_post_cards")
